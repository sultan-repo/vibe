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


if __name__ == "__main__":
    unittest.main()
