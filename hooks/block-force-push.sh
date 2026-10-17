#!/bin/bash
# PreToolUse for Bash: reject force-pushes and fail closed if validation cannot run.
# Claude Code treats exit 2 as a blocked tool call.
HOOK_DIR="$(cd -- "${BASH_SOURCE[0]%/*}" && pwd)" || exit 2
if ! command -v python3 >/dev/null 2>&1; then
  echo "Blocked by Vibe: python3 required for force-push check is unavailable." >&2
  exit 2
fi
python3 "$HOOK_DIR/check-force-push.py"
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "Blocked by Vibe: force-push detected or safety check failed." >&2
  exit 2
fi
exit 0
