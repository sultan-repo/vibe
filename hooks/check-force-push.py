#!/usr/bin/env python3
"""Parse Claude Code Bash tool input and deny force pushes; fail closed on errors.

Exit 0: verified safe command. Exit 2: force push or invalid/unreadable input.
"""
import json, re, sys

try:
    payload = json.load(sys.stdin)
    cmd = payload["tool_input"]["command"]
    if not isinstance(cmd, str):
        raise ValueError("tool_input.command is not a string")
except (TypeError, ValueError, KeyError):
    print("Vibe: malformed or incomplete tool payload; blocking", file=sys.stderr)
    sys.exit(2)
# Remove heredoc bodies, then quoted strings: that is text, not a command.
cmd = re.sub(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?^\1\s*$", " ", cmd, flags=re.S | re.M)
cmd = re.sub(r"'[^']*'", " ", cmd)
cmd = re.sub(r'"(?:[^"\\]|\\.)*"', " ", cmd)
# A git push at command position, with its arguments up to the next separator.
push = re.compile(r"(?:^|[;&|(`\n]|\$\()\s*(?:sudo\s+)?(?:command\s+)?git\s+(?:-C\s+\S+\s+)?push\b([^\n;&|`)]*)", re.M)
force = re.compile(r"(?:^|\s)(?:--force(?:-with-lease|-if-includes)?(?:=\S*)?|-f|-[a-zA-Z]*f[a-zA-Z]*)(?=\s|$)|(?:^|\s)\+\S")
for m in push.finditer(cmd):
    if force.search(m.group(1)):
        sys.exit(2)
sys.exit(0)