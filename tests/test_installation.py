"""Exercise installation only inside temporary directories with explicit targets."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ITEMS = ("SKILL.md", "LICENSE", "references", "assets", "scripts")


def find_bash() -> str | None:
    if os.name != "nt":
        return shutil.which("bash")
    git = shutil.which("git")
    if git:
        git_path = Path(git).resolve()
        for git_root in (git_path.parent.parent, git_path.parent.parent.parent):
            for relative in ("bin/bash.exe", "usr/bin/bash.exe"):
                candidate = git_root / relative
                if candidate.is_file():
                    return str(candidate)
    # Never fall back to Windows' bash.exe launcher for WSL.
    return None


BASH = find_bash()


@unittest.skipUnless(BASH, "Linux bash or Git for Windows bash not available")
class InstallationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="reader-installation-test-")
        self.root = Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temporary.cleanup)
        self.package = self.root / "Package With Spaces"
        self.package.mkdir()
        for relative in (*RUNTIME_ITEMS, "install.sh"):
            source = PACKAGE_ROOT / relative
            target = self.package / relative
            if source.is_dir():
                shutil.copytree(source, target,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(source, target)
        self.skills = self.root / "Skills With Spaces"
        self.target = self.skills / "portfolio-source-reader"
        self.unrelated = self.root / "Unrelated Current Directory"
        self.unrelated.mkdir()
        (self.unrelated / "SKILL.md").write_text("wrong package", encoding="utf-8")

    def install(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [BASH, "--noprofile", "--norc", (self.package / "install.sh").as_posix(),
             self.skills.as_posix(), *extra],
            cwd=self.unrelated, capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False, timeout=15,
        )

    def snapshot(self, root: Path) -> dict[str, tuple[str, bytes | str]]:
        result: dict[str, tuple[str, bytes | str]] = {}
        for path in root.rglob("*"):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[relative] = ("link", os.readlink(path))
            elif path.is_dir():
                result[relative] = ("directory", b"")
            elif path.is_file():
                result[relative] = ("file", path.read_bytes())
        return result

    def test_installation_uses_its_package_from_an_unrelated_cwd_with_spaces(self) -> None:
        completed = self.install()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual((self.target / "SKILL.md").read_bytes(),
                         (self.package / "SKILL.md").read_bytes())
        self.assertEqual((self.target / "LICENSE").read_bytes(),
                         (self.package / "LICENSE").read_bytes())
        self.assertTrue((self.target / "scripts" / "discover_sources.py").is_file())
        self.assertEqual(self.snapshot(self.target), {
            key: value for key, value in self.snapshot(self.package).items()
            if key != "install.sh"
        })
        self.assertEqual([path.name for path in self.skills.iterdir()],
                         ["portfolio-source-reader"])
        # Every local Markdown link reachable from the installed entry point exists.
        entrypoint = (self.target / "SKILL.md").read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", entrypoint):
            parsed = urlsplit(link)
            if not parsed.scheme and parsed.path:
                referenced = (self.target / unquote(parsed.path)).resolve()
                self.assertTrue(referenced.is_relative_to(self.target))
                self.assertTrue(referenced.exists(), link)

    def test_existing_installation_is_not_moved_overwritten_or_extended(self) -> None:
        self.target.mkdir(parents=True)
        (self.target / "user-edits.md").write_text("keep this", encoding="utf-8")
        (self.target / "custom").mkdir()
        (self.target / "custom" / "settings.json").write_text("{}", encoding="utf-8")
        before = self.snapshot(self.skills)
        completed = self.install()
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(before, self.snapshot(self.skills))

    def test_dangling_target_link_is_not_replaced(self) -> None:
        self.skills.mkdir()
        try:
            self.target.symlink_to(self.root / "missing target", target_is_directory=True)
        except OSError:
            self.skipTest("Directory symlinks are unavailable")
        link = os.readlink(self.target)
        completed = self.install()
        self.assertNotEqual(completed.returncode, 0)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(os.readlink(self.target), link)

    def test_missing_discovery_script_fails_before_creating_a_target(self) -> None:
        (self.package / "scripts" / "discover_sources.py").unlink()
        completed = self.install()
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(self.skills.exists())

    def test_missing_required_reference_fails_before_creating_a_target(self) -> None:
        (self.package / "references" / "evidence-rules.md").unlink()
        completed = self.install()
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(self.skills.exists())

    def test_copy_failure_removes_the_stage_and_never_publishes_a_partial_target(self) -> None:
        fake_bin = self.root / "Fake Commands"
        fake_bin.mkdir()
        fake_cp = fake_bin / "cp"
        fake_cp.write_text("#!/usr/bin/env bash\nprintf 'fixture copy failure\\n' >&2\nexit 7\n",
                           encoding="utf-8")
        fake_cp.chmod(0o755)
        wrapper = (
            'fixture_bin="$(cd -- "$1" && pwd -P)"; '
            'PATH="$fixture_bin:$PATH"; export PATH; '
            'exec "$BASH" --noprofile --norc "$2" "$3"'
        )
        completed = subprocess.run(
            [BASH, "--noprofile", "--norc", "-c", wrapper, "fixture",
             fake_bin.as_posix(), (self.package / "install.sh").as_posix(),
             self.skills.as_posix()],
            cwd=self.unrelated, capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False, timeout=15,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("fixture copy failure", completed.stderr)
        self.assertFalse(self.target.exists())
        self.assertEqual(list(self.skills.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
