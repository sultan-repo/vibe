"""The README's numbers come from the measured result, and its links lead somewhere. No model calls."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "evals"))
import table  # noqa: E402

README = (ROOT / "README.md").read_text(encoding="utf-8")


class Readme(unittest.TestCase):
    def test_measured_tables_are_the_ones_built_from_the_result_file(self):
        version = json.loads((ROOT / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        result = ROOT / "evals" / "results" / (version + ".json")
        if not result.exists():
            self.skipTest("no result file for %s yet; test_evals reports that" % version)
        for name, block in table.blocks(json.loads(result.read_text(encoding="utf-8"))).items():
            self.assertEqual(table.in_readme(README, name), block,
                             "README.md is out of date with %s: run python3 evals/table.py --write" % result.name)

    def test_every_row_of_the_tables_names_a_measure_that_exists(self):
        for label, case, measure in table.COMPARED + table.FORMAT:
            gates = json.loads((ROOT / "evals/cases" / case / "case.json").read_text(encoding="utf-8"))["gates"]
            self.assertIn(measure, gates, label)

    def test_relative_links_lead_to_files_that_exist(self):
        for name in ("README.md", "CHANGES.md", "evals/README.md", "assessment/evidence/README.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for target in re.findall(r"\]\((?!https?:|#|mailto:)([^)#\s]+)", text):
                self.assertTrue((ROOT / name).parent.joinpath(target).exists(), "%s links to %s" % (name, target))

    def test_links_to_headings_match_a_heading(self):
        def anchors(text):
            return {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in re.findall(r"(?m)^#+ (.+)$", text)}
        for name in ("README.md", "CHANGES.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for target, anchor in re.findall(r"\]\(([^)#\s]*)#([^)\s]+)\)", text):
                if target.startswith("http"):
                    continue
                where = (ROOT / name).parent.joinpath(target) if target else ROOT / name
                self.assertIn(anchor, anchors(where.read_text(encoding="utf-8")), "%s links to %s#%s" % (name, target, anchor))


if __name__ == "__main__":
    unittest.main()
