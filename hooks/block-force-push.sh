#!/bin/bash
# PreToolUse hook for Bash: denies force-pushes and history rewrites on shared branches.
# Claude Code passes the tool call as JSON on stdin; exit 2 blocks the call and shows stderr to Claude.
input=$(cat)
cmd=$(printf '%s' "$input" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)".*/\1/p' | head -1)
if printf '%s' "$cmd" | grep -Eq 'git[[:space:]]+push[^|;&]*(--force|-f([[:space:]]|$)|\+[A-Za-z])'; then
  echo "Blocked by delivery standard: force-push is not allowed. Ask the user to run it if truly needed." >&2
  exit 2
fi
exit 0
