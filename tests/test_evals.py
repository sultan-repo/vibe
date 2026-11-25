"""The eval suite is complete and runnable, and this plugin text has a measured result.

No model calls. The last test is the release gate: evals/results/<version>.json must carry
the hashes of the plugin files as they are now, and its counts must meet every gate.
Set VIBE_ALLOW_UNMEASURED=1 to skip it while a change is still being worked on.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVALS = os.path.join(REPO, "evals")
sys.dont_write_bytecode = True
sys.path.insert(0, EVALS)
import run  # noqa: E402  (evals/run.py)

CASE_DIRS = sorted(d for d in os.listdir(os.path.join(EVALS, "cases")) if os.path.isdir(os.path.join(EVALS, "cases", d)))
CASES = run.load_cases()
BIG = {"gates": {"m": {"min_with": 0.8, "min_delta": 0.4}}, "id": "c"}
GUARD = {"gates": {"m": {"guard": True}, "extra": {}}, "id": "c"}


def counts(with_pass, with_n, without_pass, without_n):
    return {"measures": {"m": {"with": {"pass": with_pass, "n": with_n}, "without": {"pass": without_pass, "n": without_n}}}}


class EvalSuite(unittest.TestCase):
    def test_every_case_folder_is_complete(self):
        self.assertEqual([c["id"] for c in CASES], CASE_DIRS, "a case folder has no case.json")
        self.assertGreaterEqual(len(CASES), 10)
        for case in CASES:
            with self.subTest(case=case["id"]):
                for name in ("setup.sh", "check.py"):
                    self.assertTrue(os.path.isfile(os.path.join(case["dir"], name)), name + " is missing")
                self.assertTrue(case["prompt"].strip() and case["description"].strip())
                self.assertIsInstance(case["max_turns"], int)
                self.assertTrue(any(case["gates"].values()), "no measure is gated")
                for gate in case["gates"].values():
                    self.assertLessEqual(set(gate), {"min_with", "min_delta", "guard", "arms"})

    def test_setup_builds_a_repository_and_the_checker_reports_every_gated_measure(self):
        have_node = shutil.which("node") is not None
        for case in CASES:
            with self.subTest(case=case["id"]), tempfile.TemporaryDirectory() as tmp:
                project, transcript = os.path.join(tmp, "project"), os.path.join(tmp, "empty.jsonl")
                made = subprocess.run(["sh", os.path.join(case["dir"], "setup.sh"), project], capture_output=True, text=True)
                self.assertEqual(made.returncode, 0, made.stderr)
                git = subprocess.run(["git", "-C", project, "status", "--porcelain"], capture_output=True, text=True)
                self.assertEqual((git.returncode, git.stdout), (0, ""), "setup.sh must leave a clean git repository")
                if not have_node:
                    continue  # most checkers run the toy project, which needs Node
                open(transcript, "w").close()
                check = subprocess.run([sys.executable, "-B", os.path.join(case["dir"], "check.py"), project, transcript, "with"],
                                       capture_output=True, text=True)
                self.assertEqual(check.returncode, 0, check.stderr)
                measures = json.loads(check.stdout)
                self.assertIsInstance(measures.pop("notes"), str)
                self.assertEqual(set(measures), set(case["gates"]), "check.py and the gates in case.json name different measures")
                self.assertTrue(all(isinstance(v, bool) for v in measures.values()))

    def test_gate_arithmetic(self):
        self.assertEqual(run.gate_failures(BIG, counts(4, 5, 2, 5)), [])
        self.assertEqual(run.gate_failures({"gates": {"m": {"min_with": 0.6, "min_delta": 0.4}}, "id": "c"}, counts(3, 5, 1, 5)), [])
        self.assertEqual(len(run.gate_failures(BIG, counts(3, 5, 0, 5))), 1)  # rate too low
        self.assertEqual(len(run.gate_failures(BIG, counts(5, 5, 4, 5))), 1)  # no real difference
        self.assertEqual(run.gate_failures(GUARD, counts(5, 5, 5, 5)), [])
        self.assertEqual(len(run.gate_failures(GUARD, counts(5, 5, 4, 5))), 1)
        self.assertEqual(len(run.gate_failures(GUARD, None)), 1)  # not measured at all
        only_with = {"gates": {"m": {"guard": True, "arms": ["with"]}}, "id": "c"}
        self.assertEqual(run.gate_failures(only_with, counts(5, 5, 0, 5)), [])

    def test_this_plugin_text_has_a_measured_result_that_meets_every_gate(self):
        path = os.path.join(EVALS, "results", run.version() + ".json")
        if not os.path.exists(path):
            if os.environ.get("VIBE_ALLOW_UNMEASURED") == "1":
                self.skipTest("no measured result for this version (allowed by VIBE_ALLOW_UNMEASURED=1)")
            self.fail("no measured result for this version")
        with open(path, encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual(result["files"], run.plugin_files(),
                         "plugin text changed since the last measured result: re-run python3 evals/run.py and commit the new result file")
        entries = {c["id"]: c for c in result["cases"]}
        missed = [m for case in CASES for m in run.gate_failures(case, entries.get(case["id"]))]
        self.assertEqual(missed, [], "the measured result does not meet its gates:\n  " + "\n  ".join(missed))


if __name__ == "__main__":
    unittest.main()
