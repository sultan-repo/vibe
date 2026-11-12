"""Check actual startup payload against the pinned Codex per-handler byte budget.

This tests transport and content, not live model compliance or hook trust.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CoreTransportTest(unittest.TestCase):
    def test_complete_core_and_maximum_unicode_summary_fit_codex_allowance(self):
        hook = json.loads((ROOT / "hooks/codex.json").read_text())["hooks"]["SessionStart"][0]["hooks"][0]
        limit = hook.get("additionalContextLimit", 2500)
        self.assertLessEqual(limit, 16384, "Keep a bounded allowance, not unbounded context")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "docs").mkdir()
            fields = ["Updated", "Position", "In progress", "Next task", "Waiting on owner"]
            lines = [(key + ": ").ljust(500, "\U0001f9ea") for key in fields]
            lines += ["\U0001f9ea" * 500] * 5
            (root / "docs/STATUS.md").write_text("## Now\n" + "\n".join(lines) + "\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text("Run full verification before each push.\n")
            result = subprocess.run([sys.executable, str(ROOT / "hooks/session-start.py"),
                                     "--core", str(ROOT / "core/CLAUDE.md")],
                                    input=json.dumps({"cwd": str(root)}), text=True,
                                    capture_output=True, timeout=6,
                                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(result.returncode, 0, result.stderr)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        # Codex 0.162.1 estimates ceil(UTF-8 bytes / 4) before spilling hook output.
        self.assertLessEqual((len(context.encode("utf-8")) + 3) // 4, limit)
        self.assertIn((ROOT / "core/CLAUDE.md").read_text(), context)
        for rule in ("## Verification cadence", "- **Affected:**", "- **Expanded:**", "- **Release:**",
                     "- **Feature completion:**", "## Git and permissions", "## Reuse before rebuilding"):
            self.assertIn(rule, context)
        self.assertIn("Project continuity", context)
        self.assertIn("Vibe gate advisory:", context)

    def test_core_treats_a_truncated_preview_as_incomplete(self):
        core = (ROOT / "core/CLAUDE.md").read_text()
        self.assertIn("truncated startup preview", core)
        self.assertIn("complete installed core", core)


if __name__ == "__main__":
    unittest.main()
