#!/usr/bin/env python3
"""Run an independent, read-only Codex review for one clean commit.

Run from the project repository, not the Vibe repository. Requires a locally
installed and authenticated Codex CLI. Exits 0 only for a valid APPROVE result.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

SCHEMA = Path(__file__).with_name("review-result.schema.json")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()


def fail(message):
    print(f"Vibe review blocked: {message}", file=sys.stderr)
    return 2


def valid_report(report):
    if not isinstance(report, dict) or set(report) != {
        "head_sha", "verdict", "findings", "previous_findings", "unverified_requirements",
        "reviewer_limitations"
    }:
        return False
    if not isinstance(report["head_sha"], str) or report["verdict"] not in {
        "APPROVE", "APPROVE_WITH_REQUIRED_FIXES", "REJECT"
    }:
        return False
    if not all(isinstance(report[k], list) for k in (
        "findings", "previous_findings", "unverified_requirements", "reviewer_limitations"
    )):
        return False
    if not all(isinstance(x, str) and x for x in report["reviewer_limitations"]):
        return False
    if not all(isinstance(x, str) and x for x in report["unverified_requirements"]):
        return False
    for item in report["findings"]:
        keys = {"id", "kind", "severity", "requirement", "evidence", "impact", "suggested_resolution"}
        if not isinstance(item, dict) or set(item) != keys:
            return False
        if not all(isinstance(item[k], str) and item[k].strip() for k in keys):
            return False
        if item["kind"] not in {"bug", "spec_question", "out_of_scope"} or item["severity"] not in {
            "blocker", "required", "minor"
        }:
            return False
    for item in report["previous_findings"]:
        if not isinstance(item, dict) or set(item) != {"id", "status", "evidence"}:
            return False
        if not all(isinstance(item[k], str) and item[k].strip() for k in item):
            return False
        if item["status"] not in {"fixed", "open", "disputed"}:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, type=Path, help="Reviewer brief text file")
    parser.add_argument("--head", required=True, help="Full SHA of the commit to review")
    parser.add_argument("--effort", required=True, choices=("medium", "high", "xhigh"))
    parser.add_argument("--output", required=True, type=Path, help="JSON report destination")
    args = parser.parse_args()

    if not args.brief.is_file() or not args.brief.read_text(encoding="utf-8").strip():
        return fail("reviewer brief is missing or empty")
    if args.head not in args.brief.read_text(encoding="utf-8"):
        return fail("reviewer brief does not identify the requested commit")
    if not shutil.which("codex"):
        return fail("Codex CLI is not installed; no reviewer substitution was made")
    try:
        root = Path(git("rev-parse", "--show-toplevel"))
        head = git("rev-parse", "HEAD")
        dirty = git("status", "--porcelain")
    except (subprocess.CalledProcessError, OSError):
        return fail("must run inside a Git worktree")
    if head != args.head or len(args.head) != 40:
        return fail("HEAD does not match the requested review SHA")
    if dirty:
        return fail("worktree is not clean; commit changes before reviewing")
    login = subprocess.run(["codex", "login", "status"], cwd=root, capture_output=True, text=True)
    if login.returncode != 0:
        return fail("local Codex sign-in is unavailable; authenticate on this machine")

    destination = args.output.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.unlink(missing_ok=True)  # Never treat an old approval as a new result.
    command = [
        "codex", "--ask-for-approval", "never", "exec", "--sandbox", "read-only",
        "-c", f"model_reasoning_effort={args.effort}",
        "--output-schema", str(SCHEMA), "--output-last-message", str(destination), "-",
    ]
    run = subprocess.run(command, input=args.brief.read_text(encoding="utf-8"),
                         cwd=root, text=True, capture_output=True)
    if run.returncode != 0:
        return fail("Codex execution failed (check CLI model/effort support and authentication). "
                    + (run.stderr.strip()[-1200:] if run.stderr else f"Exit code: {run.returncode}"))
    try:
        report = json.loads(destination.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fail("Codex did not return a valid JSON review")
    if not valid_report(report):
        return fail("review report does not match the expected schema")
    if report.get("head_sha") != args.head:
        return fail("review result targets another commit")
    if git("rev-parse", "HEAD") != args.head or git("status", "--porcelain"):
        return fail("the reviewed worktree changed during the review")
    findings = report.get("findings")
    previous = report.get("previous_findings")
    unverified = report.get("unverified_requirements")
    if not isinstance(findings, list) or not isinstance(previous, list) or not isinstance(unverified, list):
        return fail("review result is missing required collections")
    if report.get("verdict") != "APPROVE":
        return fail(f"review verdict is {report.get('verdict', 'missing')}")
    if unverified:
        return fail("unverified acceptance evidence: " + " | ".join(unverified)[:1500])
    blocking = [item.get("id", "unknown") for item in findings
                if item.get("severity") in ("blocker", "required") or item.get("kind") == "spec_question"]
    if blocking:
        return fail("unresolved required findings: " + ", ".join(blocking))
    if any(item.get("status") != "fixed" for item in previous):
        return fail("previous review findings have not all been resolved")
    limitations = report["reviewer_limitations"]
    if limitations:
        print(f"Review limitations (not missing acceptance evidence): {len(limitations)}")
        for item in limitations:
            print(f"  - {item}")
    print(f"Vibe review APPROVED at {args.head[:12]} (effort: {args.effort}); {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
