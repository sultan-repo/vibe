#!/bin/bash
# Removes everything install.sh put into ~/.claude. Leaves your own CLAUDE.md content and other settings untouched.
set -euo pipefail
CL="$HOME/.claude"

# 1. Core: drop the import line and the installed file.
if [ -f "$CL/CLAUDE.md" ]; then
  grep -v '@~/.claude/vibe.md' "$CL/CLAUDE.md" > "$CL/CLAUDE.md.tmp" || true
  mv "$CL/CLAUDE.md.tmp" "$CL/CLAUDE.md"
fi
rm -f "$CL/vibe.md"

# 2. Skills and agent.
rm -rf "$CL/skills/discover" "$CL/skills/build" "$CL/skills/reassess"
rm -f "$CL/agents/reviewer.md"

# 3. Hook script and its settings entry.
HOOK="$CL/hooks/block-force-push.sh"
rm -f "$HOOK"
if [ -f "$CL/settings.json" ]; then
python3 - "$CL/settings.json" "$HOOK" <<'PY'
import json, sys
path, cmd = sys.argv[1], sys.argv[2]
with open(path) as f:
    data = json.load(f)
pre = data.get("hooks", {}).get("PreToolUse", [])
kept = []
for entry in pre:
    entry["hooks"] = [h for h in entry.get("hooks", []) if h.get("command") != cmd]
    if entry["hooks"]:
        kept.append(entry)
if "hooks" in data:
    if kept:
        data["hooks"]["PreToolUse"] = kept
    else:
        data["hooks"].pop("PreToolUse", None)
    if not data["hooks"]:
        data.pop("hooks")
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
fi
echo "Vibe removed from $CL. Open a new Claude Code session to apply."
