"""Behavioral tests use isolated fixtures; never inspect the user's projects."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "discover_sources.py"
SPEC = importlib.util.spec_from_file_location("discover_sources", SCRIPT)
discovery = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(discovery)
GIT = shutil.which("git")


class SourceDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="reader-discovery-test-")
        self.root = Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temporary.cleanup)

    def git(self, root: Path, *arguments: str) -> str:
        result = subprocess.run(
            [GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "-C", str(root), *arguments],
            capture_output=True, text=True, encoding="utf-8", check=False,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def repository(self, name: str = "repo", commit: bool = True) -> Path:
        root = self.root / name
        root.mkdir(parents=True)
        self.git(root, "init", "-b", "main")
        if commit:
            (root / "README.md").write_text("Fixture documentation\n", encoding="utf-8")
            self.git(root, "add", "README.md")
            self.git(root, "commit", "-m", "fixture")
        return root

    def snapshot(self, root: Path) -> tuple[str, bytes, dict[str, bytes]]:
        head = self.git(root, "rev-parse", "HEAD")
        index = Path(self.git(root, "rev-parse", "--git-path", "index"))
        if not index.is_absolute():
            index = root / index
        files = {
            str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob("*") if path.is_file() and ".git" not in path.parts
        }
        return head, hashlib.sha256(index.read_bytes()).digest(), files

    def test_remote_credentials_are_removed_and_visibility_stays_unknown(self) -> None:
        remote = discovery.sanitize_remote(
            "https://account:secret@github.com/person/repo.git?token=private#credential"
        )
        self.assertEqual(remote["url"], "https://github.com/person/repo")
        self.assertEqual(remote["visibility"], "unconfirmed")
        serialized = json.dumps(remote)
        for value in ("account", "secret", "private", "credential"):
            self.assertNotIn(value, serialized)
        self.assertEqual(
            discovery.sanitize_remote("git@gitee.com:person/repo.git")["url"],
            "https://gitee.com/person/repo",
        )

    def test_internal_or_local_remotes_never_emit_the_address(self) -> None:
        for value in ("ssh://user@internal.example/customer/repo", "git@10.1.2.3:repo",
                      "file:///private/customer/repo", "https://github.com.evil.example/a/b"):
            with self.subTest(remote=value):
                result = discovery.sanitize_remote(value)
                self.assertIsNone(result["url"])
                self.assertEqual(result["state"], "needs_safe_reference")
                self.assertNotIn(value, json.dumps(result))

    @unittest.skipUnless(GIT, "git not installed")
    def test_non_origin_remote_is_found_without_losing_origin_priority(self) -> None:
        repo = self.repository()
        self.git(repo, "remote", "add", "gitee",
                 "https://account:secret@gitee.com/person/repo.git?token=hidden")
        before = self.snapshot(repo)
        source = discovery.discover_sources(repo)["sources"][0]
        remote = source["git"]["remote"]
        self.assertEqual(remote["name"], "gitee")
        self.assertEqual(remote["url"], "https://gitee.com/person/repo")
        self.assertEqual(remote["visibility"], "unconfirmed")
        self.assertNotIn("secret", json.dumps(source))
        self.assertNotIn("hidden", json.dumps(source))
        self.assertEqual(before, self.snapshot(repo))
        self.git(repo, "remote", "add", "origin", "git@github.com:person/repo.git")
        remote = discovery.discover_sources(repo)["sources"][0]["git"]["remote"]
        self.assertEqual(remote["name"], "origin")
        self.assertEqual(remote["url"], "https://github.com/person/repo")

    def test_reparse_points_are_skipped_without_modern_path_methods(self) -> None:
        junction = self.root / "junction"
        junction.mkdir()
        (junction / "README.md").write_text("must not inspect", encoding="utf-8")
        original_lstat = Path.lstat

        def legacy_lstat(path: Path, *args, **kwargs):
            if path == junction:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return original_lstat(path, *args, **kwargs)

        # Older Python has no Path.is_junction; lstat attributes still identify it.
        with patch.object(Path, "is_junction", None, create=True), \
                patch.object(Path, "lstat", legacy_lstat):
            source = discovery.discover_sources(junction)["sources"][0]
            report = discovery.discover_sources(self.root, scan_children=True)
        self.assertEqual(source["kind"], "skipped_link")
        self.assertEqual(source["documents"], [])
        self.assertNotIn("junction", [entry["name"] for entry in report["sources"]])

    def test_inaccessible_directory_does_not_discard_healthy_siblings(self) -> None:
        denied = self.root / "denied"
        denied.mkdir()
        healthy = self.root / "healthy"
        healthy.mkdir()
        (healthy / "README.md").write_text("fixture", encoding="utf-8")
        original_lstat = Path.lstat

        def failing_lstat(path: Path, *args, **kwargs):
            if path == denied:
                raise PermissionError("internal.example must not appear in diagnostics")
            return original_lstat(path, *args, **kwargs)

        with patch.object(Path, "lstat", failing_lstat):
            report = discovery.discover_sources(self.root, scan_children=True)
        sources = {entry["name"]: entry for entry in report["sources"]}
        self.assertEqual(sources["denied"]["git"]["state"],
                         "filesystem_metadata_unavailable")
        self.assertEqual(sources["healthy"]["documents"],
                         [{"path": "README.md", "kind": "readme"}])
        self.assertNotIn("internal.example", json.dumps(report))

    @unittest.skipUnless(GIT, "git not installed")
    def test_failed_document_metadata_still_allows_git_and_other_documents(self) -> None:
        repo = self.repository()
        (repo / "SOURCES.md").write_text("fixture map", encoding="utf-8")
        original_lstat = Path.lstat

        def failing_lstat(path: Path, *args, **kwargs):
            if path == repo / "README.md":
                raise PermissionError("not readable")
            return original_lstat(path, *args, **kwargs)

        with patch.object(Path, "lstat", failing_lstat):
            source = discovery.discover_sources(repo)["sources"][0]
        self.assertEqual(source["git"]["state"], "available")
        self.assertEqual(source["git"]["head"], self.git(repo, "rev-parse", "HEAD"))
        self.assertIn("document_metadata_unavailable", source["notes"])
        self.assertIn("SOURCES.md", [entry["path"] for entry in source["documents"]])

    def test_failed_root_enumeration_returns_the_root_instead_of_crashing(self) -> None:
        with patch.object(Path, "iterdir", side_effect=PermissionError("not readable")):
            report = discovery.discover_sources(self.root, scan_children=True)
        self.assertEqual(len(report["sources"]), 1)
        self.assertEqual(report["sources"][0]["path"], str(self.root))
        self.assertIn("child_directory_listing_unavailable", report["notes"])

    def test_archive_can_be_discovered_without_git(self) -> None:
        archive = self.root / "archive"
        (archive / "projects").mkdir(parents=True)
        (archive / "SOURCES.md").write_text("map", encoding="utf-8")
        (archive / "projects" / "index.md").write_text("index", encoding="utf-8")
        with patch.object(discovery.shutil, "which", return_value=None):
            source = discovery.discover_sources(archive)["sources"][0]
        self.assertEqual(source["kind"], "archive_or_documents")
        self.assertEqual(source["git"]["state"], "git_unavailable")
        self.assertEqual({item["path"] for item in source["documents"]},
                         {"SOURCES.md", "projects/index.md"})

    def test_scope_is_explicit_bounded_and_never_recursive(self) -> None:
        for name in ("a", "b", "c", "node_modules", "build", ".venv"):
            (self.root / name).mkdir()
        (self.root / "a" / "deep").mkdir()
        self.assertEqual(len(discovery.discover_sources(self.root)["sources"]), 1)
        report = discovery.discover_sources(self.root, scan_children=True, max_repos=3)
        self.assertEqual([item["name"] for item in report["sources"]][1:], ["a", "b"])
        self.assertTrue(report["truncated"])
        complete = discovery.discover_sources(self.root, scan_children=True)
        self.assertEqual([item["name"] for item in complete["sources"]][1:], ["a", "b", "c"])

    def test_links_are_not_followed_for_sources_or_documents(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "index.md").write_text("outside", encoding="utf-8")
        inspected = self.root / "inspected"
        inspected.mkdir()
        try:
            (inspected / "projects").symlink_to(outside, target_is_directory=True)
            (inspected / "linked").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Directory symlinks are unavailable")
        report = discovery.discover_sources(inspected, scan_children=True)
        self.assertEqual(len(report["sources"]), 1)
        self.assertEqual(report["sources"][0]["documents"], [])

    @unittest.skipUnless(GIT, "git not installed")
    def test_dirty_repository_is_reported_without_mutating_index_or_files(self) -> None:
        repo = self.repository()
        self.git(repo, "remote", "add", "origin",
                 "https://account:secret@github.com/person/repo.git?token=hidden")
        (repo / "README.md").write_text("modified", encoding="utf-8")
        (repo / ".env").write_text("SECRET=do-not-read", encoding="utf-8")
        before = self.snapshot(repo)
        report = discovery.discover_sources(repo)
        source = report["sources"][0]
        self.assertTrue(source["git"]["dirty"])
        self.assertFalse(source["git"]["shallow"])
        self.assertFalse(source["git"]["linked_worktree"])
        self.assertEqual(source["git"]["head"], before[0])
        self.assertEqual(before, self.snapshot(repo))
        serialized = json.dumps(report)
        for value in ("do-not-read", "secret", "hidden", "account"):
            self.assertNotIn(value, serialized)

    @unittest.skipUnless(GIT, "git not installed")
    def test_empty_repository_has_an_unborn_state(self) -> None:
        repo = self.repository(commit=False)
        source = discovery.discover_sources(repo)["sources"][0]
        self.assertEqual(source["git"]["state"], "unborn")
        self.assertIsNone(source["git"]["head"])
        self.assertEqual(source["git"]["branch"], "main")
        self.assertFalse(source["git"]["dirty"])

    @unittest.skipUnless(GIT, "git not installed")
    def test_archive_inside_a_repository_is_not_counted_as_another_repo(self) -> None:
        repo = self.repository()
        archive = repo / "archive"
        archive.mkdir()
        (archive / "case-study.md").write_text("archive", encoding="utf-8")
        source = discovery.discover_sources(archive)["sources"][0]
        self.assertEqual(source["git"]["state"], "not_repository")
        self.assertEqual(source["kind"], "archive_or_documents")

    @unittest.skipUnless(GIT, "git not installed")
    def test_linked_worktree_keeps_its_own_head_and_is_not_changed(self) -> None:
        repo = self.repository()
        worktree = self.root / "worktree"
        self.git(repo, "worktree", "add", "--detach", str(worktree), "HEAD")
        before = self.snapshot(worktree)
        source = discovery.discover_sources(worktree)["sources"][0]
        self.assertTrue(source["git"]["linked_worktree"])
        self.assertIsNone(source["git"]["branch"])
        self.assertEqual(source["git"]["head"], before[0])
        self.assertEqual(before, self.snapshot(worktree))

    @unittest.skipUnless(GIT, "git not installed")
    def test_local_shallow_clone_is_not_presented_as_complete_history(self) -> None:
        repo = self.repository()
        (repo / "README.md").write_text("second", encoding="utf-8")
        self.git(repo, "add", "README.md")
        self.git(repo, "commit", "-m", "second")
        shallow = self.root / "shallow"
        self.git(self.root, "clone", "--depth", "1", repo.as_uri(), str(shallow))
        source = discovery.discover_sources(shallow)["sources"][0]
        self.assertTrue(source["git"]["shallow"])
        self.assertEqual(source["git"]["head"], self.git(repo, "rev-parse", "HEAD"))

    def test_missing_and_malformed_locations_do_not_crash_the_batch(self) -> None:
        missing = discovery.discover_sources(self.root / "missing")["sources"][0]
        self.assertEqual(missing["kind"], "missing")
        broken = self.root / "broken"
        broken.mkdir()
        (broken / ".git").write_text("invalid marker", encoding="utf-8")
        source = discovery.discover_sources(broken)["sources"][0]
        self.assertIn(source["git"]["state"], {"unreadable_repository", "git_unavailable"})

    def test_cli_outputs_parseable_json_and_redacted_markdown(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(self.root)],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        report = json.loads(completed.stdout)
        self.assertTrue(report["metadata_only"])
        source = report["sources"][0]
        source["git"]["remote"] = discovery.sanitize_remote("git@internal.example:private")
        markdown = discovery.render_markdown(report)
        self.assertNotIn("internal.example", markdown)
        self.assertIn(str(self.root), markdown)


if __name__ == "__main__":
    unittest.main()
