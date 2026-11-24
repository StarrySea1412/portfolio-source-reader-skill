#!/usr/bin/env python3
"""Discover local source locations without reading project content or changing Git."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
from typing import Any
from urllib.parse import urlsplit


EXCLUDED_DIRECTORIES = {
    "node_modules", "vendor", "dist", "build", "out", "target", "coverage",
    "venv", "env", "__pycache__",
}
DOCUMENT_CANDIDATES = (
    ("README.md", "readme"),
    ("README.rst", "readme"),
    ("README.txt", "readme"),
    ("README", "readme"),
    ("readme.md", "readme"),
    ("AGENTS.md", "instructions"),
    ("SOURCES.md", "source_map"),
    ("case-study.md", "archive"),
    ("projects/index.md", "project_index"),
    ("docs/README.md", "docs_index"),
    ("docs", "docs_directory"),
)
GIT_TIMEOUT_SECONDS = 4


def is_link(path: Path) -> bool:
    """Skip symlinks and Windows reparse points, including on Python 3.10/3.11."""
    try:
        metadata = path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def sanitize_remote(value: str) -> dict[str, Any]:
    """Keep only a canonical GitHub/Gitee repo location; never infer visibility."""
    result: dict[str, Any] = {
        "url": None,
        "state": "needs_safe_reference",
        "visibility": "unconfirmed",
    }
    value = value.strip()
    if not value or any(ord(char) < 32 for char in value):
        return result
    try:
        if "://" in value:
            parsed = urlsplit(value)
            if parsed.scheme.lower() not in {"http", "https", "ssh", "git"}:
                return result
            host, path = parsed.hostname, parsed.path
        else:
            match = re.fullmatch(r"(?:[^@\s]+@)?([^:\s/]+):(.+)", value)
            if not match:
                return result
            host, path = match.groups()
        host = (host or "").lower()
        if host not in {"github.com", "gitee.com"}:
            return result
        parts = path.strip("/").removesuffix(".git").split("/")
        if len(parts) != 2 or any(
            not re.fullmatch(r"[A-Za-z0-9_.-]+", part) or part in {".", ".."}
            for part in parts
        ):
            return result
        result.update(url=f"https://{host}/{'/'.join(parts)}", state="location_only")
    except ValueError:
        pass
    return result


def run_git(executable: str, root: Path, *arguments: str) -> tuple[int | None, str]:
    environment = os.environ.copy()
    environment.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    command = [
        executable, "--no-optional-locks", "-c", "core.fsmonitor=false",
        "-c", "core.untrackedCache=false", "-C", str(root), *arguments,
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=GIT_TIMEOUT_SECONDS, env=environment,
            check=False,
        )
        # Git's diagnostics can contain credentials or internal remote addresses.
        return completed.returncode, completed.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None, ""


def find_documents(root: Path, notes: list[str] | None = None) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    seen: set[str] = set()
    for relative, kind in DOCUMENT_CANDIDATES:
        candidate = root / relative
        components = [root.joinpath(*Path(relative).parts[:index])
                      for index in range(1, len(Path(relative).parts) + 1)]
        try:
            if any(is_link(component) for component in components):
                continue
            normalized = os.path.normcase(str(candidate))
            if normalized not in seen and candidate.exists():
                if candidate.is_file() or (kind == "docs_directory" and candidate.is_dir()):
                    documents.append({"path": relative, "kind": kind})
                    seen.add(normalized)
        except OSError:
            if notes is not None and "document_metadata_unavailable" not in notes:
                notes.append("document_metadata_unavailable")
    return documents


def find_remote(root: Path, git_executable: str) -> dict[str, Any] | None:
    """Prefer origin, otherwise use the first readable recorded remote."""
    code, value = run_git(git_executable, root, "remote", "get-url", "--", "origin")
    if code == 0:
        return {**sanitize_remote(value), "name": "origin"}
    code, names = run_git(git_executable, root, "remote")
    if code == 0:
        for name in names.splitlines():
            if name == "origin":
                continue
            code, value = run_git(git_executable, root, "remote", "get-url", "--", name)
            if code == 0:
                return {**sanitize_remote(value), "name": name}
    return None


def inspect_location(root: Path, git_executable: str | None) -> dict[str, Any]:
    source: dict[str, Any] = {
        "name": root.name or str(root), "path": str(root), "kind": "directory",
        "documents": [], "notes": [],
        "git": {
            "state": "not_repository", "head": None, "branch": None, "dirty": None,
            "shallow": None, "linked_worktree": None, "remote": None,
        },
    }
    try:
        return inspect_readable_location(root, git_executable, source)
    except OSError:
        source["kind"] = "unreadable_location"
        source["git"]["state"] = "filesystem_metadata_unavailable"
        source["notes"].append("filesystem_metadata_unavailable")
        return source


def inspect_readable_location(root: Path, git_executable: str | None,
                              source: dict[str, Any]) -> dict[str, Any]:
    if is_link(root):
        source.update(kind="skipped_link")
        source["git"]["state"] = "not_checked"
        return source
    if not root.exists() or not root.is_dir():
        source.update(kind="missing" if not root.exists() else "not_directory")
        source["git"]["state"] = "not_checked"
        return source
    source["documents"] = find_documents(root, source["notes"])
    if source["documents"]:
        source["kind"] = "archive_or_documents"
    marker = root / ".git"
    if not marker.exists():
        # Do not mistake a subdirectory of some other repository for a new project.
        if not git_executable:
            source["git"]["state"] = "git_unavailable"
        return source
    source["kind"] = "git_repository"
    if is_link(marker):
        source["git"]["state"] = "not_checked"
        source["notes"].append("git_marker_is_link")
        return source
    if not git_executable:
        source["git"]["state"] = "git_unavailable"
        return source

    metadata = source["git"]
    code, inside = run_git(git_executable, root, "rev-parse", "--is-inside-work-tree")
    if code != 0 or inside != "true":
        metadata["state"] = "unreadable_repository"
        return source
    code, head = run_git(git_executable, root, "rev-parse", "--verify", "HEAD")
    branch_code, branch = run_git(
        git_executable, root, "symbolic-ref", "--quiet", "--short", "HEAD",
    )
    metadata["branch"] = branch if branch_code == 0 else None
    if code == 0 and re.fullmatch(r"[0-9a-fA-F]{40,64}", head):
        metadata.update(state="available", head=head)
    else:
        metadata["state"] = "unborn" if branch_code == 0 else "head_unavailable"
    code, status = run_git(
        git_executable, root, "status", "--porcelain=v1", "--untracked-files=normal",
    )
    if code == 0:
        metadata["dirty"] = bool(status)
    else:
        source["notes"].append("worktree_status_unavailable")
    code, shallow = run_git(git_executable, root, "rev-parse", "--is-shallow-repository")
    if code == 0 and shallow in {"true", "false"}:
        metadata["shallow"] = shallow == "true"
    metadata["linked_worktree"] = False
    if marker.is_file():
        dir_code, git_directory = run_git(
            git_executable, root, "rev-parse", "--absolute-git-dir",
        )
        common_code, common_directory = run_git(
            git_executable, root, "rev-parse", "--path-format=absolute", "--git-common-dir",
        )
        metadata["linked_worktree"] = (
            os.path.normcase(git_directory) != os.path.normcase(common_directory)
            if dir_code == common_code == 0 else None
        )
    metadata["remote"] = find_remote(root, git_executable)
    return source


def discover_sources(root: Path, scan_children: bool = False,
                     max_repos: int = 40) -> dict[str, Any]:
    if max_repos < 1:
        raise ValueError("max_repos must be at least 1")
    root = Path(os.path.abspath(root.expanduser()))
    candidates = [root]
    notes: list[str] = []
    if scan_children:
        children: list[Path] = []
        try:
            if not is_link(root) and root.is_dir():
                for child in root.iterdir():
                    if (child.name.startswith(".")
                            or child.name.lower() in EXCLUDED_DIRECTORIES):
                        continue
                    try:
                        if not is_link(child) and child.is_dir():
                            children.append(child)
                    except OSError:
                        # Keep an unknown entry visible and continue with other locations.
                        children.append(child)
        except OSError:
            notes.append("child_directory_listing_unavailable")
        candidates.extend(sorted(children, key=lambda child: child.name.casefold()))
    git_executable = shutil.which("git")
    selected = candidates[:max_repos]
    with ThreadPoolExecutor(max_workers=min(4, len(selected))) as executor:
        sources = list(executor.map(
            lambda candidate: inspect_location(candidate, git_executable), selected,
        ))
    return {
        "schema_version": 1, "metadata_only": True, "root": str(root),
        "scope": "root_and_direct_children" if scan_children else "root_only",
        "max_repos": max_repos, "truncated": len(candidates) > max_repos,
        "git_available": bool(git_executable), "sources": sources, "notes": notes,
    }


def inline_code(value: Any) -> str:
    value = str(value).replace("\r", " ").replace("\n", " ")
    longest = max((len(match.group()) for match in re.finditer(r"`+", value)), default=0)
    delimiter = "`" * (longest + 1)
    return f"{delimiter} {value} {delimiter}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SOURCES.md 草稿", "",
        "> 本次只读取目录和 Git 元数据。本人贡献、测试结果、业务效果与披露权限均待核实。",
        "> 远端链接表示仓库位置，公开性未确认；未读取项目内容或运行产品测试。", "",
    ]
    for source in report["sources"]:
        metadata = source["git"]
        remote = metadata["remote"]
        remote_text = (inline_code(remote["url"]) + "（公开性未确认）"
                       if remote and remote["url"]
                       else "待补安全引用" if remote else "未发现远端 / 未检查")
        if remote and remote.get("name"):
            remote_text = inline_code(remote["name"]) + " → " + remote_text
        dirty = {True: "有未提交修改", False: "干净", None: "未确认"}[metadata["dirty"]]
        lines.extend([
            f"### {inline_code(source['name'])}",
            f"- 本地路径：{inline_code(source['path'])}",
            f"- 发现状态：{source['kind']} / {metadata['state']}",
            f"- 源码快照：{inline_code(metadata['head']) if metadata['head'] else '未确认 / 无提交'}",
            f"- 工作树：{dirty}；shallow={metadata['shallow']}；linked_worktree={metadata['linked_worktree']}",
            f"- 远端位置：{remote_text}",
            "- 文档入口：" + ("、".join(inline_code(doc["path"]) for doc in source["documents"])
                             or "待补"),
            "- 本人贡献：待本人确认", "- 验证记录：待补日期、版本、环境与结果",
            "- 脱敏与披露权限：待确认", "",
        ])
    if report["truncated"]:
        lines.append("> 已达到目录检查上限；其余目录未检查。")
    return "\n".join(lines).rstrip() + "\n"


def positive_integer(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--scan-children", action="store_true",
                        help="Inspect root and direct child directories only.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--max-repos", type=positive_integer, default=40,
                        help="Maximum inspected locations, including root.")
    arguments = parser.parse_args()
    report = discover_sources(arguments.root, arguments.scan_children, arguments.max_repos)
    print(json.dumps(report, ensure_ascii=False, indent=2) if arguments.format == "json"
          else render_markdown(report), end="\n" if arguments.format == "json" else "")


if __name__ == "__main__":
    main()
