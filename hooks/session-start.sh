#!/bin/bash
# SessionStart hook: injects the always-on core rules into the session context.
# Emits the documented JSON form (hookSpecificOutput.additionalContext); falls back to plain text if python3 is missing.
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
CORE="$ROOT/core/CLAUDE.md"
[ -f "$CORE" ] || exit 0
if command -v python3 >/dev/null 2>&1; then
  python3 - "$CORE" <<'PY'
import json, sys
text = open(sys.argv[1], encoding="utf-8").read()
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
PY
else
  cat "$CORE"
fi
exit 0
