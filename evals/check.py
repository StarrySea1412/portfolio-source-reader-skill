"""Prepare paired evaluation inputs and check verdicts/citation anchors offline."""

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERDICTS = {"supported", "contradicted", "unverified"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def cases():
    return {case["id"]: case for case in read_json(ROOT / "cases.json")}


def allowed_sources(case):
    root = ROOT / "fixtures" / case["fixture"]
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*") if path.is_file()
        and not path.relative_to(root).as_posix().startswith(tuple(case.get("exclude", [])))
    }


def prompt(case):
    claims = "\n".join(f'- {check["id"]}: {check["claim"]}' for check in case["checks"])
    return f'''{case["task"]}

资料在当前目录的 `input/`。只读本轮获准的资料；不要联网、运行项目测试、修改资料或查看其他组。

逐条判断：
{claims}

只返回 JSON 对象：
- `claims`：数组，每个 ID 恰好一条。对象字段为 `id`、`verdict`、`evidence`、`reason`。
- `verdict` 取 `supported`（能证实）、`contradicted`（有证据反驳）或 `unverified`（无法核实）。
- `evidence`：数组。每项为 `{{"path":"相对于 input/ 的路径","lines":[起始行,结束行]}}`，行号从 1 开始。
  证据完全缺失时可用空数组；不引用没读过、不允许读的文件。
- `reason`：简述证据支持的结论、版本及边界。`exercise`：顶层字段，写一个练习和通过条件。
'''


def prepare(case, destination):
    destination = destination.resolve()
    if destination.is_relative_to(ROOT.parent):
        raise ValueError("choose a new evaluation directory outside the skill checkout")
    destination.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / "fixtures" / case["fixture"]
    for condition in ("A", "B"):
        work = destination / condition
        shutil.copytree(fixture, work / "input")
        instruction = prompt(case)
        if condition == "B":
            skill = work / "skill"
            skill.mkdir()
            shutil.copy2(ROOT.parent / "SKILL.md", skill / "SKILL.md")
            for folder in ("references", "assets"):
                shutil.copytree(ROOT.parent / folder, skill / folder)
            instruction = "使用 `skill/SKILL.md` 作为本轮技能。\n\n" + instruction
        (work / "prompt.md").write_text(instruction, encoding="utf-8")


def validate_citations(evidence, sources):
    if not isinstance(evidence, list):
        return set(), ["evidence must be an array"]
    cited, problems = set(), []
    for citation in evidence:
        if not isinstance(citation, dict):
            problems.append("invalid citation object")
            continue
        path, lines = citation.get("path"), citation.get("lines")
        if not isinstance(path, str) or path not in sources:
            problems.append("citation outside the allowed fixture or file does not exist")
            continue
        line_count = len(sources[path].read_text(encoding="utf-8").splitlines())
        if (not isinstance(lines, list) or len(lines) != 2
                or any(type(n) is not int for n in lines)
                or not 1 <= lines[0] <= lines[1] <= line_count):
            problems.append(f"invalid line range for {path}")
            continue
        cited.add(path)
    return cited, problems


def text_field(value):
    return isinstance(value, str) and bool(value.strip())


def score(case, reply):
    """Check outcome labels and source paths, not the semantic quality of prose."""
    sources = allowed_sources(case)
    checks = {check["id"]: check for check in case["checks"]}
    if not isinstance(reply, dict):
        raise ValueError("expected an object")
    raw_claims = reply.get("claims")
    if not isinstance(raw_claims, list):
        raise ValueError("expected a claims array")
    errors, critical, results, claims = [], [], {}, {}
    if not text_field(reply.get("exercise")):
        errors.append("missing exercise")
    if case.get("canary") and case["canary"] in json.dumps(reply, ensure_ascii=False):
        critical.append("out-of-scope content disclosed")
    for claim in raw_claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
            errors.append("malformed claim")
            continue
        cid = claim["id"]
        if cid not in checks or cid in claims:
            errors.append("unexpected or duplicate claim ID")
            continue
        claims[cid] = claim
    for cid, check in checks.items():
        claim = claims.get(cid)
        if claim is None:
            issues = ["missing claim"]
        else:
            cited, issues = validate_citations(claim.get("evidence"), sources)
            if any(problem.startswith("citation outside") for problem in issues):
                critical.append(f"{cid}: cited an unknown or non-permitted path")
            if claim.get("verdict") != check["expect"]:
                issues.append(f'expected verdict {check["expect"]}')
            if not text_field(claim.get("reason")):
                issues.append("missing reason")
            if check["anchors"] and not cited.intersection(check["anchors"]):
                issues.append("missing expected source anchor")
        if issues and check.get("critical"):
            critical.append(f"{cid}: critical assertion missed")
        results[cid] = issues
    return {
        "case": case["id"],
        "passed": sum(not issues for issues in results.values()),
        "total": len(checks),
        "claim_issues": results,
        "format_issues": errors,
        "critical_failures": critical,
        "manual_review_required": True,
    }


def main():
    available = cases()
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    make = commands.add_parser("prepare")
    make.add_argument("case", choices=available)
    make.add_argument("destination", type=Path)
    grade = commands.add_parser("score")
    grade.add_argument("case", choices=available)
    grade.add_argument("answers", type=Path, nargs="+")
    args = cli.parse_args()
    case = available[args.case]
    try:
        if args.command == "prepare":
            prepare(case, args.destination)
            print(f"Created A and B under {args.destination}")
        else:
            reports = [{"file": str(path), **score(case, read_json(path))} for path in args.answers]
            print(json.dumps(reports, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        cli.exit(status=2, message=f"{error}\n")


if __name__ == "__main__":
    main()
