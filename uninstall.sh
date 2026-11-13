#!/bin/bash
# Removes everything install.sh put into ~/.claude. Leaves your own CLAUDE.md content and other settings untouched.
set -euo pipefail
CL="${VIBE_CLAUDE_HOME:-$HOME/.claude}"

# 1. Core: drop the import line and the installed file.
if [ -f "$CL/CLAUDE.md" ]; then
  grep -v '@~/.claude/vibe.md' "$CL/CLAUDE.md" > "$CL/CLAUDE.md.tmp" || true
  mv "$CL/CLAUDE.md.tmp" "$CL/CLAUDE.md"
fi
rm -f "$CL/vibe.md"

# 2. Workflow/effort skills and agents.
for skill in discover build reassess effort-low effort-medium effort-high; do
  rm -rf "$CL/skills/$skill"
done
rm -f "$CL/agents/reviewer.md" "$CL/agents/worker.md"
rm -f "$CL/vibe-tools/codex-review.py" "$CL/vibe-tools/review-result.schema.json" # legacy upgrade cleanup
rm -f "$CL/vibe-tools/verification-cache.py" "$CL/vibe-tools/pre-push.template" "$CL/vibe-tools/verification-cache.md"

# 3. Owned hook scripts and settings entries; preserve other hooks in the same entry.
HOOK="$CL/hooks/block-force-push.sh"
STARTUP="$CL/vibe-tools/session-start.sh"
rm -f "$HOOK" "$CL/hooks/check-force-push.py" "$STARTUP" "$CL/vibe-tools/session-start.py" "$CL/vibe-tools/project_setup.py" "$CL/vibe-tools/project-adoption.md" "$CL/vibe-tools/governance.py" "$CL/vibe-tools/governance.md"
rmdir "$CL/vibe-tools" 2>/dev/null || true
if [ -f "$CL/settings.json" ]; then
python3 - "$CL/settings.json" "$HOOK" "$STARTUP" <<'PY'
import json, shlex, sys
path, cmd, startup_path = sys.argv[1:]
with open(path) as f:
    data = json.load(f)
if "hooks" in data:
    owned = {"PreToolUse": cmd,
             "SessionStart": shlex.quote(startup_path) + " --status-only"}
    for event, owned_cmd in owned.items():
        kept = []
        for entry in data["hooks"].get(event, []):
            original = entry.get("hooks", [])
            remaining = [h for h in original if h.get("command") != owned_cmd]
            if remaining == original:
                kept.append(entry)
            elif remaining:
                entry["hooks"] = remaining
                kept.append(entry)
        if kept:
            data["hooks"][event] = kept
        else:
            data["hooks"].pop(event, None)
    if not data["hooks"]:
        data.pop("hooks")
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
fi
echo "Vibe removed from $CL. Open a new Claude Code session to apply."
