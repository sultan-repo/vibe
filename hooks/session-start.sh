#!/bin/bash
# SessionStart only: core rules and a bounded, local continuity snapshot.
# The manual installer uses --status-only because it already imports the core.
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$HERE/.." && pwd)}"
CORE="$ROOT/core/CLAUDE.md"
if command -v python3 >/dev/null 2>&1; then
  python3 "$HERE/session-start.py" --core "$CORE" "$@"
elif [ "${1:-}" != "--status-only" ] && [ -f "$CORE" ]; then
  cat "$CORE"
fi
exit 0
