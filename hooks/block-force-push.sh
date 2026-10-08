#!/bin/bash
# PreToolUse hook for Bash: denies force-pushes and remote history rewrites.
# Claude Code passes the tool call as JSON on stdin; exit 2 blocks the call and shows stderr to Claude.
# Heredoc bodies and quoted strings are ignored, so a command that merely mentions a force-push is allowed.
TOOL_INPUT="$(cat)"
command -v python3 >/dev/null 2>&1 || exit 0
export TOOL_INPUT
python3 - <<'PY'
import json, os, re, sys
try:
    cmd = json.loads(os.environ.get("TOOL_INPUT", "")).get("tool_input", {}).get("command", "") or ""
except Exception:
    sys.exit(0)
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
PY
rc=$?
if [ "$rc" -eq 2 ]; then
  echo "Blocked by vibe: force-push rewrites shared history. Ask the user to run it themselves if it is truly needed." >&2
  exit 2
fi
exit 0
