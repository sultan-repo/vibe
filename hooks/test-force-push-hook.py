#!/usr/bin/env python3
"""Tests for hooks/block-force-push.sh. Run: python3 hooks/test-force-push-hook.py"""
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "block-force-push.sh")

MUST_BLOCK = [
    "git push --force origin main",
    "git push -f",
    "git push --force-with-lease",
    "git push --force-with-lease=main origin main",
    "cd ~/x && git push -f origin HEAD",
    "git push origin +main",
    "git -C repo push -f",
    "sudo git push --force",
    "git push origin main -f",
    "git fetch; git push --force",
    "echo hi | git push -f",
    "git push -uf origin main",
]

MUST_ALLOW = [
    "git push origin main",
    "git push --follow-tags",
    "git push -u origin main",
    'echo "git push --force"',
    "echo 'git push -f'",
    "cat <<'EOF' > README.md\nA hook that denies git push --force\nEOF",
    'grep -rn "git push -f" .',
    "git log -f -- file",
    "git push --set-upstream origin feature",
    "ls -f",
    "git pushx -f",
    "cp hooks/block-force-push.sh ~/.claude/hooks/",
]


def run(cmd):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
    return subprocess.run([HOOK], input=payload, capture_output=True, text=True).returncode


def main():
    failures = 0
    for cases, expected, label in ((MUST_BLOCK, 2, "block"), (MUST_ALLOW, 0, "allow")):
        for cmd in cases:
            rc = run(cmd)
            ok = rc == expected
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'} {label:5} rc={rc} {cmd!r}")
    print(f"failures: {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
