#!/usr/bin/env python3
"""Regression checks for low-overhead delivery, plain-language output and safety gates."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8").lower()


class LeanWorkflowTest(unittest.TestCase):
    def test_routing_and_communication(self):
        core = read("core/CLAUDE.md")
        for term in ("**fast**", "**standard**", "**critical**", "2–5 short lines",
                     "internal ids", "high-risk pre-merge", "reassess"):
            with self.subTest(term=term):
                self.assertIn(term, core)
        self.assertNotIn("about 15 lines", core)

    def test_build_does_not_stop_per_increment_or_require_docs(self):
        build = read("skills/build/SKILL.md")
        self.assertIn("continuous delivery is the default", build)
        self.assertIn("without stopping after each increment", build)
        self.assertIn("missing continuity files do **not** force discover", build)
        self.assertIn("do not automatically", build)
        self.assertNotIn("stop there. if the user asked", build)
        self.assertNotIn("about 15 lines", build)

    def test_discover_is_conditional(self):
        discovery = read("skills/discover/SKILL.md")
        self.assertIn("ordinary build requests", discovery)
        self.assertIn("skip this skill", discovery)
        self.assertIn("material decisions remain", discovery)
        self.assertIn("owner", discovery)

    def test_reassess_stays_risk_aware_but_concise(self):
        reassess = read("skills/reassess/SKILL.md")
        self.assertIn("one full review", reassess)
        self.assertIn("one targeted follow-up", reassess)
        self.assertIn("high-risk change", reassess)
        self.assertIn("2–5 concise", reassess)
        self.assertNotIn("about 20 lines", reassess)

    def test_readme_describes_new_defaults(self):
        readme = read("README.md")
        for term in ("fast", "standard", "critical", "continuously by default",
                     "2–5 plain-language lines"):
            with self.subTest(term=term):
                self.assertIn(term, readme)


if __name__ == "__main__":
    unittest.main()
