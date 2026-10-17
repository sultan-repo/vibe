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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, type=Path, help="Reviewer brief text file")
    parser.add_argument("--head", required=True, help="Full SHA of the commit to review")
    parser.add_argument("--effort", required=True, choices=("medium", "high", "xhigh"))
    parser.add_argument("--output", required=True, type=Path, help="JSON report destination")
    args = parser.parse_args()

    if not args.brief.is_file() or not args.brief.read_text(encoding="utf-8").strip():
        return fail("reviewer brief is missing or empty")
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
        "codex", "exec", "--sandbox", "read-only", "--ask-for-approval", "never",
        "-c", f"model_reasoning_effort={args.effort}",
        "--output-schema", str(SCHEMA), "--output-last-message", str(destination), "-",
    ]
    run = subprocess.run(command, input=args.brief.read_text(encoding="utf-8"),
                         cwd=root, text=True, capture_output=True)
    if run.returncode != 0:
        return fail("Codex execution failed (check CLI model/effort support and authentication)")
    try:
        report = json.loads(destination.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fail("Codex did not return a valid JSON review")
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
    if unverified or any(item.get("severity") in ("blocker", "required") or
                         item.get("kind") == "spec_question" for item in findings):
        return fail("approval conflicts with unresolved findings or acceptance criteria")
    if any(item.get("status") != "fixed" for item in previous):
        return fail("previous review findings have not all been resolved")
    print(f"Vibe review APPROVED at {args.head[:12]} (effort: {args.effort}); {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
