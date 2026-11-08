#!/bin/bash
# Installs Vibe (delivery standard) v4 into ~/.claude for all projects.
# Safe to re-run after editing the bundle: copies are refreshed, your own ~/.claude/CLAUDE.md is kept.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CL="${VIBE_CLAUDE_HOME:-$HOME/.claude}"
mkdir -p "$CL/skills" "$CL/agents" "$CL/hooks"

# 1. Core rules: installed as their own file and imported, so personal notes in CLAUDE.md survive re-installs.
cp "$HERE/core/CLAUDE.md" "$CL/vibe.md"
touch "$CL/CLAUDE.md"
if ! grep -q '@~/.claude/vibe.md' "$CL/CLAUDE.md"; then
  printf '\n@~/.claude/vibe.md\n' >> "$CL/CLAUDE.md"
fi

# 2. Workflow/effort skills and scoped subagents.
for skill in discover build reassess effort-low effort-medium effort-high; do
  rm -rf "$CL/skills/$skill"
  cp -R "$HERE/skills/$skill" "$CL/skills/"
done
cp "$HERE/agents/reviewer.md" "$HERE/agents/worker.md" "$CL/agents/"
# Remove legacy external reviewer artifacts from earlier installations, leaving other files alone.
rm -f "$CL/vibe-tools/codex-review.py" "$CL/vibe-tools/review-result.schema.json"
rmdir "$CL/vibe-tools" 2>/dev/null || true

# Optional project verification templates; never register a global verification gate.
mkdir -p "$CL/vibe-tools"
cp "$HERE/hooks/verification-cache.py" "$HERE/hooks/pre-push.template" "$HERE/hooks/verification-cache.md" "$CL/vibe-tools/"

# 3. Force-push protection and startup continuity, preserving unrelated settings.
cp "$HERE/hooks/block-force-push.sh" "$HERE/hooks/check-force-push.py" \
   "$HERE/hooks/session-start.sh" "$HERE/hooks/session-start.py" "$CL/hooks/"
chmod +x "$CL/hooks/block-force-push.sh" "$CL/hooks/session-start.sh"
python3 - "$CL/settings.json" "$CL/hooks/block-force-push.sh" "$CL/hooks/session-start.sh" <<'PY'
import json, os, shlex, sys
path, cmd, startup_path = sys.argv[1:]
data = {}
if os.path.exists(path) and os.path.getsize(path) > 0:
    with open(path) as f:
        data = json.load(f)
pre = data.setdefault("hooks", {}).setdefault("PreToolUse", [])
present = any(h.get("command") == cmd for e in pre for h in e.get("hooks", []))
if not present:
    pre.append({"matcher": "Bash", "hooks": [{"type": "command", "command": cmd}]})
# The core is already imported by CLAUDE.md, so this hook adds only project status.
startup_cmd = shlex.quote(startup_path) + " --status-only"
starts = data["hooks"].setdefault("SessionStart", [])
present = any(h.get("command") == startup_cmd for e in starts for h in e.get("hooks", []))
if not present:
    starts.append({"hooks": [{"type": "command", "command": startup_cmd}]})
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY

echo "Installed into $CL:"
echo "  vibe.md   (imported by $CL/CLAUDE.md)"
echo "  skills/discover, skills/build, skills/reassess"
echo "  skills/effort-low, skills/effort-medium, skills/effort-high (internal controls)"
echo "  agents/reviewer.md, agents/worker.md"
echo "  vibe-tools/ (optional project verification reuse; not enabled globally)"
echo "  hooks/block-force-push.sh + check-force-push.py (PreToolUse hook in settings.json)"
echo "  hooks/session-start.sh + session-start.py (project status at session start)"
echo "Open a new Claude Code session to pick it up."
