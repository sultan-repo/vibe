#!/bin/bash
# Installs Vibe (delivery standard) v4 into ~/.claude for all projects.
# Safe to re-run after editing the bundle: copies are refreshed, your own ~/.claude/CLAUDE.md is kept.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CL="$HOME/.claude"
mkdir -p "$CL/skills" "$CL/agents" "$CL/hooks"

# 1. Core rules: installed as their own file and imported, so personal notes in CLAUDE.md survive re-installs.
cp "$HERE/core/CLAUDE.md" "$CL/vibe.md"
touch "$CL/CLAUDE.md"
if ! grep -q '@~/.claude/vibe.md' "$CL/CLAUDE.md"; then
  printf '\n@~/.claude/vibe.md\n' >> "$CL/CLAUDE.md"
fi

# 2. Skills and the reviewer subagent.
rm -rf "$CL/skills/discover" "$CL/skills/reassess"
cp -R "$HERE/skills/discover" "$HERE/skills/reassess" "$CL/skills/"
cp "$HERE/agents/reviewer.md" "$CL/agents/reviewer.md"

# 3. Hook that denies force-pushes, registered in settings.json without touching other settings.
cp "$HERE/hooks/block-force-push.sh" "$CL/hooks/block-force-push.sh"
chmod +x "$CL/hooks/block-force-push.sh"
python3 - "$CL/settings.json" "$CL/hooks/block-force-push.sh" <<'PY'
import json, os, sys
path, cmd = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path) and os.path.getsize(path) > 0:
    with open(path) as f:
        data = json.load(f)
pre = data.setdefault("hooks", {}).setdefault("PreToolUse", [])
present = any(h.get("command") == cmd for e in pre for h in e.get("hooks", []))
if not present:
    pre.append({"matcher": "Bash", "hooks": [{"type": "command", "command": cmd}]})
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY

echo "Installed into $CL:"
echo "  vibe.md   (imported by $CL/CLAUDE.md)"
echo "  skills/discover, skills/reassess"
echo "  agents/reviewer.md"
echo "  hooks/block-force-push.sh  (PreToolUse hook in settings.json)"
echo "Open a new Claude Code session to pick it up."
