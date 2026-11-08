#!/usr/bin/env python3
"""Validate YAML frontmatter for all Vibe skills."""
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class SkillMetadataTest(unittest.TestCase):
    def test_skill_frontmatter_is_valid_yaml(self):
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(skills, "No skill metadata files found")
        for path in skills:
            with self.subTest(skill=path.parent.name):
                content = path.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("---\n"), f"{path} lacks YAML frontmatter")
                parts = content.split("---\n", 2)
                self.assertEqual(len(parts), 3, f"{path} has no closing YAML delimiter")
                metadata = yaml.safe_load(parts[1])
                self.assertIsInstance(metadata, dict)
                self.assertEqual(metadata.get("name"), path.parent.name)
                self.assertIsInstance(metadata.get("description"), str)
                self.assertTrue(metadata["description"].strip())

    def test_effort_controls_use_native_inline_metadata(self):
        # Reading instructions alone cannot change effort. These controls must
        # be invocable by the model, inline, without granting extra tools.
        for level in ("low", "medium", "high"):
            with self.subTest(level=level):
                path = ROOT / "skills" / f"effort-{level}" / "SKILL.md"
                metadata = yaml.safe_load(path.read_text().split("---\n", 2)[1])
                self.assertEqual(metadata["effort"], level)
                self.assertIs(metadata["user-invocable"], False)
                self.assertIsNot(metadata.get("disable-model-invocation"), True)
                self.assertNotEqual(metadata.get("context"), "fork")
                self.assertNotIn("allowed-tools", metadata)
                self.assertNotIn("model", metadata)

    def test_workflow_and_agent_effort_defaults(self):
        expected = {
            "skills/build/SKILL.md": "medium",
            "skills/discover/SKILL.md": "medium",
            "skills/reassess/SKILL.md": "medium",
            "agents/worker.md": "medium",
            "agents/reviewer.md": "high",
        }
        for relative, effort in expected.items():
            with self.subTest(path=relative):
                metadata = yaml.safe_load((ROOT / relative).read_text().split("---\n", 2)[1])
                self.assertEqual(metadata["effort"], effort)
                if relative.startswith("agents/"):
                    self.assertEqual(metadata["model"], "inherit")


if __name__ == "__main__":
    unittest.main()
