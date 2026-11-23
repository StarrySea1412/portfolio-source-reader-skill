"""Offline end-to-end probe using a real MCP client and stdio child process."""
from contextlib import asynccontextmanager
from pathlib import Path
import argparse
import asyncio
import errno
import json
import shutil
import subprocess
import sys
import tempfile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent
TOOLS = frozenset({"list_evidence", "read_evidence"})


@asynccontextmanager
async def connect_evidence(root=ROOT):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-I", "-B", str(root / "evidence_mcp.py")],
    )
    async with stdio_client(params) as (rx, tx):
        async with ClientSession(rx, tx) as session:
            hello = await session.initialize()
            if hello.serverInfo.name != "portfolio-evidence":
                raise RuntimeError("Unexpected MCP server")
            yield session, hello


async def call_object(session, tool_name, arguments=None):
    result = await session.call_tool(tool_name, arguments or {})
    if result.isError or not isinstance(result.structuredContent, dict):
        raise RuntimeError("MCP denied the request or did not return approved structured content")
    return result.structuredContent


async def expect_denied(session, evidence_id):
    reply = await session.call_tool("read_evidence", {"evidence_id": evidence_id})
    assert reply.isError and reply.structuredContent is None, evidence_id


async def verify_boundary():
    # Mutate only generated copies, never the checked-in bundle.
    parent = Path(tempfile.gettempdir()).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="portfolio-evidence-", dir=parent) as temp:
        root = Path(temp)
        if root.resolve(strict=True) != root or root.parent != parent:
            raise RuntimeError("Unexpected self-check directory")
        for name in ("evidence_mcp.py", "bundle/manifest.json", "bundle/app/storage.txt"):
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)

        storage = root / "bundle/app/storage.txt"
        original = storage.read_bytes()
        manifest = root / "bundle/manifest.json"
        async with connect_evidence(root) as (session, _):
            arguments = {"evidence_id": "storage"}
            baseline = await call_object(session, "read_evidence", arguments)
            storage.write_bytes(original + b"\nchanged after tool discovery\n")
            await expect_denied(session, "storage")
            storage.write_bytes(original)
            assert await call_object(session, "read_evidence", arguments) == baseline
            print("PASS integrity: changed evidence denied; restoring approved bytes restores access")

            # Give the external file the correct hash so this checks the path boundary,
            # not just rejection of modified bytes. No real external data is used.
            outside = root / "outside.txt"
            outside.write_bytes(original)
            storage.unlink()
            try:
                storage.symlink_to(outside)
            except OSError as exc:
                if (getattr(exc, "winerror", None) != 1314
                        and exc.errno not in (errno.EACCES, errno.EPERM, errno.ENOTSUP)):
                    raise
                print("SKIP path boundary: this environment cannot create a file symlink")
            else:
                try:
                    await expect_denied(session, "storage")
                finally:
                    storage.unlink()
                print("PASS path boundary: out-of-bundle symlink denied even with approved bytes")

        # Whitespace keeps the manifest valid JSON while changing its approved digest.
        with manifest.open("ab") as handle:
            handle.write(b"\n")
        process = subprocess.run(
            [sys.executable, "-I", "-B", str(root / "evidence_mcp.py")],
            input=b"", capture_output=True, timeout=15, check=False,
        )
        assert process.returncode != 0 and not process.stdout
        assert b"digest does not match" in process.stderr
        print("PASS startup: changed manifest fails closed before serving tools")


async def verify(show):
    async with connect_evidence() as (session, hello):
        print(f"PASS initialize: {hello.serverInfo.name}, protocol {hello.protocolVersion}")
        tools = (await session.list_tools()).tools
        assert len(tools) == len(TOOLS) and {tool.name for tool in tools} == TOOLS
        assert all(tool.annotations and tool.annotations.readOnlyHint for tool in tools)
        print("PASS tools/list: exactly two read-only tools")
        catalog = await call_object(session, "list_evidence")
        rows = catalog["items"]
        ids = {item["evidence_id"] for item in rows}
        assert len(ids) == len(rows) == 9 and "storage" in ids
        assert all(set(row) == {"evidence_id", "source_type", "path"} for row in rows)
        print("PASS catalog: 9 approved IDs; no document body in list")
        for row in rows:
            item = await call_object(session, "read_evidence", {"evidence_id": row["evidence_id"]})
            assert all(item[k] == v for k, v in row.items())
            assert set(item) == {*row, "numbered_text"}
            for index, line in enumerate(item["numbered_text"].split("\n"), 1):
                assert line.startswith(f"{index}: ")
        print("PASS read: all 9 approved items return structured line-numbered content")
        for bad in ("not-approved", "../outside.txt", r"C:\outside\file.txt"):
            await expect_denied(session, bad)
        print("PASS deny: unknown ID, traversal, absolute path")
        for key in show:
            row = await call_object(session, "read_evidence", {"evidence_id": key})
            print(json.dumps(row, ensure_ascii=False, indent=2))
    await verify_boundary()


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run the self-check without Python optimization")
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", nargs="*", default=[])
    args = parser.parse_args()
    asyncio.run(verify(args.evidence))
