#!/usr/bin/env python3
"""Guard the Claude-only review policy and removal of external reviewer dependencies."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DOCS = [
    "README.md", "core/CLAUDE.md", "core/PROJECT-CLAUDE.template.md",
    "skills/discover/SKILL.md", "skills/discover/references/project-claude-template.md",
    "skills/build/SKILL.md", "skills/build/references/review-loop.md",
    "skills/build/references/reviewer-brief.md", "skills/reassess/SKILL.md",
    "agents/reviewer.md", ".claude-plugin/plugin.json",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ReviewPolicyTest(unittest.TestCase):
    def test_no_external_reviewer_in_active_instructions(self):
        for path in ACTIVE_DOCS:
            with self.subTest(path=path):
                self.assertNotIn("codex", read(path).lower())

    def test_external_cli_artifacts_are_removed(self):
        for path in ("scripts/codex-review.py", "scripts/review-result.schema.json",
                     "tests/test_codex_review.py"):
            with self.subTest(path=path):
                self.assertFalse((ROOT / path).exists())
        self.assertNotIn('cp "$HERE/scripts/', read("install.sh"))

    def test_final_gate_and_bounded_review(self):
        reassess = read("skills/reassess/SKILL.md")
        guidance = read("skills/build/references/review-loop.md")
        self.assertIn("high-risk", reassess.lower())
        self.assertIn("release", reassess.lower())
        self.assertIn("explicit", reassess.lower())
        self.assertIn("ordinary milestone", reassess.lower())
        self.assertIn("one full review", guidance.lower())
        self.assertIn("one targeted recheck", guidance.lower())
        self.assertIn("fresh-context", guidance.lower())

    def test_small_build_does_not_trigger_mandatory_review(self):
        build = read("skills/build/SKILL.md")
        self.assertIn("do not automatically", build.lower())
        self.assertIn("small fixes", build.lower())
        self.assertIn("reassess", build.lower())


if __name__ == "__main__":
    unittest.main()
