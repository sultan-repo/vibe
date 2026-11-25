"""Guards for the two GitHub Actions workflows, read as plain text. No network, no YAML library.
Checks protects what runs on every pull request. Publisher protects who may publish, and what.
Run:  python3 -B -m unittest discover -s tests -p 'test_workflows.py' -v
"""
import json
import re
import shutil
import subprocess
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = {path.name: path.read_text(encoding="utf-8") for path in (ROOT / ".github" / "workflows").iterdir()}
CHECKS, RELEASE = FILES["vibe-checks.yml"], FILES["release.yml"]
GUARDS = ("github.event.workflow_run.conclusion == 'success'", "github.event.workflow_run.event == 'push'",
          "github.event.workflow_run.head_branch == 'main'",
          "github.event.workflow_run.head_repository.full_name == github.repository")
PIN = re.compile(r"@anthropic-ai/claude-code@\d+\.\d+\.\d+")  # the only three-part version a workflow may hold
SAMPLE = ("# Changes\n\n## Rules\nintro\n\n## 9.9.10 - 2030-02-01\nten\n\n"
          "## 9.9.1 - 2030-01-01\n\none\n### Removed\ngone\n\n## 9.9.0\nzero\n")


def notes(version, changelog):
    """What the publisher would use as release notes: its own awk program, run on this text."""
    program = re.search(r"awk -v v=\"\$version\" '(.+)' CHANGES\.md", RELEASE).group(1)
    return subprocess.run(["awk", "-v", "v=" + version, program], input=changelog, capture_output=True, text=True).stdout


class Checks(unittest.TestCase):
    def test_runs_on_pull_requests_and_main_with_read_only_access(self):
        self.assertTrue(CHECKS.startswith("name: Vibe checks\n"))  # the publisher finds it by this name
        self.assertIn("\non:\n  push:\n    branches: [main]\n  pull_request:\n", CHECKS)
        self.assertIn("\npermissions:\n  contents: read\n", CHECKS)
        for forbidden in ("secrets.", "continue-on-error", "gh release", "workflow_run"):
            self.assertNotIn(forbidden, CHECKS)

    def test_reports_the_two_checks_that_branch_protection_requires(self):
        jobs = CHECKS.split("\njobs:\n")[1]
        self.assertEqual(re.findall(r"(?m)^  ([\w-]+):$", jobs), ["validate", "native-mod-render"])
        # A job-level name or matrix renames a required check; a job-level "if" can skip it.
        self.assertEqual(re.findall(r"(?m)^    (?:name|if|strategy|permissions):", jobs), [])
        for command in ("python3 -B -m unittest discover -s tests -v\n", "claude plugin validate --strict .\n",
                        "claude plugin validate --strict plugin\n"):
            self.assertIn(command, jobs)


class Publisher(unittest.TestCase):
    def test_only_the_publisher_can_write(self):
        for name, text in FILES.items():
            self.assertEqual("contents: write" in text, name == "release.yml", name)
            self.assertNotIn("pull_request_target", text, name)

    def test_starts_only_after_the_checks_passed_on_a_push_to_main_here(self):
        trigger = '\non:\n  workflow_run:\n    workflows: ["Vibe checks"]\n    types: [completed]\n    branches: [main]\n\n'
        self.assertIn(trigger, RELEASE)
        self.assertIn("if: >- " + " && ".join(GUARDS) + " runs-on:", " ".join(RELEASE.split()))

    def test_publishes_exactly_the_tested_commit(self):
        for term in ("ref: ${{ github.event.workflow_run.head_sha }}\n          persist-credentials: false\n",
                     'test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"', 'if [ "$main_sha" != "$TESTED_SHA" ]',
                     'if [ -n "$tag_sha" ] && [ "$tag_sha" != "$TESTED_SHA" ]', "--verify-tag", '--target "$TESTED_SHA"'):
            self.assertIn(term, RELEASE)

    def test_no_version_is_written_into_a_workflow(self):
        # Action versions (@v4) and tool versions ("3.11", "22") have fewer than three parts.
        self.assertEqual(len(PIN.findall(CHECKS)), 1)
        for name, text in FILES.items():
            self.assertEqual(re.findall(r"v?\d+\.\d+\.\d+", PIN.sub("", text)), [], name)

    @unittest.skipUnless(shutil.which("awk"), "needs awk")
    def test_release_notes_are_one_version_section_of_the_changelog(self):
        self.assertEqual(notes("9.9.1", SAMPLE), "\none\n### Removed\ngone\n\n")
        self.assertEqual(notes("9.9.0", SAMPLE), "zero\n")
        self.assertEqual(notes("9.9", SAMPLE) + notes("9.9.2", SAMPLE), "")
        version = json.loads((ROOT / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        found = notes(version, (ROOT / "CHANGES.md").read_text(encoding="utf-8"))
        self.assertTrue(found.strip(), "CHANGES.md needs a '## %s' section before this version can be released" % version)

    @unittest.skipUnless(shutil.which("bash"), "needs bash")
    def test_every_script_step_is_valid_shell(self):
        for name, text in FILES.items():
            for script in re.findall(r"(?m)^ +run: \|\n((?:(?: {10}.*)?\n)+)", text):
                done = subprocess.run(["bash", "-n"], input=textwrap.dedent(script), capture_output=True, text=True)
                self.assertEqual(done.returncode, 0, "%s: %s\n%s" % (name, done.stderr, script))


if __name__ == "__main__":
    unittest.main()
