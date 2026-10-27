#!/usr/bin/env python3
"""Policy regression checks for opt-in learning, resume anchors and scoped security."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class SelectivePracticesTests(unittest.TestCase):
    def test_learning_is_optional_and_evidence_based(self):
        guidance = read("skills/build/references/lessons-and-handoff.md")
        self.assertIn("optional", guidance.lower())
        self.assertIn("two independently observed instances", guidance)
        self.assertIn("explicitly asks", guidance)
        self.assertIn("never auto-promote", guidance.lower())
        self.assertIn("Do not run learning analysis", guidance)

    def test_resume_reuses_existing_status(self):
        guidance = read("skills/build/references/lessons-and-handoff.md")
        template = read("skills/discover/references/register-template.md")
        for text in ("HEAD", "verified command", "failed approach", "next approved"):
            self.assertIn(text.lower(), (guidance + template).lower())
        self.assertEqual(template.count("```"), 6, "Expected 3 closed Markdown template blocks")
        self.assertIn("docs/LESSONS.md (optional", template)

    def test_security_preflight_only_for_affected_gate(self):
        guide = read("skills/reassess/references/security-preflight.md")
        reassess = read("skills/reassess/SKILL.md")
        self.assertIn("only for affected surfaces", guide.lower())
        self.assertIn("not applicable", guide.lower())
        self.assertIn("not", guide.lower())
        self.assertIn("security-preflight.md", reassess)
        self.assertIn("high-risk or release gate", reassess)

    def test_no_new_runtime_or_mandatory_review(self):
        core = read("core/CLAUDE.md")
        build = read("skills/build/SKILL.md")
        lessons = read("skills/build/references/lessons-and-handoff.md")
        self.assertIn("Optional project lessons", core)
        self.assertIn("do not automatically run it for small fixes", build)
        self.assertIn("no", lessons.lower())
        self.assertNotIn("PreToolUse", lessons)
        self.assertNotIn("PostToolUse", lessons)
        self.assertNotIn("SessionStart", lessons)


if __name__ == "__main__":
    unittest.main()
