#!/usr/bin/env python3
"""Release configuration regressions; not runtime or application QA evidence."""
import json
from pathlib import Path
import subprocess
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ".github/workflows/vibe-checks.yml"
PUBLISH = ".github/workflows/publish-v4.5.yml"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def workflow(path):
    # BaseLoader preserves GitHub's `on` key instead of YAML 1.1's boolean.
    return yaml.load(read(path), Loader=yaml.BaseLoader)


class ReleaseCandidateTest(unittest.TestCase):
    def test_version_metadata_and_release_documents_agree(self):
        version = json.loads(read(".claude-plugin/plugin.json"))["version"]
        self.assertEqual(version, "4.12.0")
        self.assertEqual(json.loads(read(".codex-plugin/plugin.json"))["version"], version)
        series = ".".join(version.split(".")[:2])
        marketplace = json.loads(read(".claude-plugin/marketplace.json"))
        self.assertIn(f"v{series}:", marketplace["plugins"][0]["description"])
        self.assertIn(f"v{series}", read("core/CLAUDE.md").splitlines()[0])
        self.assertIn(f'== "{version}"', read(CHECKS))
        for path in (f"docs/RELEASE-{series}.md", f"docs/RELEASE_NOTES_{series}.md"):
            self.assertIn(f"v{version}", read(path))
        self.assertIn(f"v{version} (release candidate)", read("CHANGES.md"))

    def test_native_validation_runs_before_merge_without_branch_exceptions(self):
        checks = workflow(CHECKS)
        self.assertEqual(checks["on"]["push"]["branches"], ["main"])
        self.assertIn("pull_request", checks["on"])
        self.assertFalse(checks["on"]["pull_request"])
        native = checks["jobs"]["native-mod-render"]
        self.assertNotIn("if", native)
        self.assertNotIn("continue-on-error", native)
        for step in native["steps"]:
            self.assertNotIn("if", step)
            self.assertNotIn("continue-on-error", step)
        runs = [step.get("run") for step in native["steps"]]
        self.assertIn("npm install --global @anthropic-ai/claude-code@2.1.314", runs)
        self.assertIn("claude plugin validate --strict .", runs)
        self.assertNotIn("claude plugin test .", runs)  # No native Mod remains.

    def test_pr_checks_keep_read_only_permissions_and_no_publisher(self):
        checks = workflow(CHECKS)
        self.assertEqual(checks["permissions"], {"contents": "read"})
        self.assertEqual(set(checks["on"]), {"push", "pull_request"})
        self.assertEqual(set(checks["jobs"]), {"validate", "native-mod-render"})
        self.assertNotIn("secrets.", read(CHECKS))
        for job in checks["jobs"].values():
            self.assertNotIn("permissions", job)
            for step in job["steps"]:
                self.assertNotIn("gh release", step.get("run", ""))

    def test_existing_full_repository_checks_remain(self):
        validate = workflow(CHECKS)["jobs"]["validate"]
        self.assertNotIn("if", validate)
        self.assertNotIn("continue-on-error", validate)
        runs = "\n".join(step.get("run", "") for step in validate["steps"])
        for command in (
            "node --test tests/benchmark-runner.test.mjs",
            "python3 hooks/test-force-push-hook.py",
            "python3 -m unittest discover -s tests -v",
            "bash ./install.sh", "bash ./uninstall.sh",
        ):
            self.assertIn(command, runs)
        for step in validate["steps"]:
            self.assertNotIn("if", step)
            self.assertNotIn("continue-on-error", step)

    def test_publisher_accepts_only_successful_trusted_main_push(self):
        publish = workflow(PUBLISH)
        self.assertEqual(set(publish["on"]), {"workflow_run"})
        self.assertEqual(publish["on"]["workflow_run"], {
            "workflows": ["Vibe checks"], "types": ["completed"], "branches": ["main"],
        })
        condition = " ".join(publish["jobs"]["publish"]["if"].split())
        expected = " && ".join((
            "github.event.workflow_run.conclusion == 'success'",
            "github.event.workflow_run.event == 'push'",
            "github.event.workflow_run.head_branch == 'main'",
            "github.event.workflow_run.head_repository.full_name == github.repository",
        ))
        self.assertEqual(condition, expected)
        checkout = publish["jobs"]["publish"]["steps"][0]
        self.assertEqual(checkout["with"]["ref"], "${{ github.event.workflow_run.head_sha }}")
        self.assertEqual(checkout["with"]["persist-credentials"], "false")

    def test_publisher_uses_matching_version_notes_and_tested_sha(self):
        version = json.loads(read(".claude-plugin/plugin.json"))["version"]
        series = ".".join(version.split(".")[:2])
        text = read(PUBLISH)
        for term in (
            f'name: Publish Vibe {version}', f'"$version" != "{version}"',
            f"docs/RELEASE_NOTES_{series}.md", f"docs/RELEASE-{series}.md",
            f"refs/tags/v{version}", f"gh release create v{version}",
            'test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"',
            'if [ "$main_sha" != "$TESTED_SHA" ]',
            'if [ -n "$tag_sha" ] && [ "$tag_sha" != "$TESTED_SHA" ]',
            '--verify-tag', '--target "$TESTED_SHA"',
        ):
            self.assertIn(term, text)
        self.assertNotIn("4.8", text)

    def test_core_requires_acceptance_evidence_for_uncovered_requirements(self):
        expanded = next(line for line in read("core/CLAUDE.md").splitlines()
                        if line.startswith("- **Expanded:**"))
        self.assertIn("Add acceptance evidence for uncovered requirements", expanded)
        self.assertIn("a broader green suite alone cannot establish them", expanded)
        self.assertIn("Never defer critical checks", expanded)

    def test_release_boundary_and_skipped_checks_are_not_misrepresented(self):
        for path in ("docs/TESTING-VALIDATION.md", "docs/RELEASE-4.12.md"):
            text = read(path)
            self.assertIn("Merging to `main` is a production delivery", text)
            self.assertIn("before merge", text)
            self.assertIn("skipped", text.lower())
            self.assertTrue("not a pass" in text.lower() or "skipped checks as pending" in text.lower())
            self.assertNotIn("no release is implied", text)
        plan = read("docs/RELEASE-4.12.md")
        self.assertIn("independent", plan)
        self.assertIn("exact final", plan)
        self.assertIn("targeted recheck", plan)
        self.assertIn("cannot certify", plan)
        notes = read("docs/RELEASE_NOTES_4.12.md")
        self.assertIn("Executable hooks follow Codex's trust settings", notes)

    def test_adoption_still_requires_a_bounded_project_comparison(self):
        text = read("docs/TESTING-VALIDATION.md")
        for term in ("Keep old gates active", "bounded shadow comparison",
                     "known-regression replay", "Do not repeat this dual-run",
                     "No automatic project migration or measured speedup is claimed"):
            self.assertIn(term, text)

    def test_all_workflow_run_blocks_have_valid_shell_syntax(self):
        for path in (CHECKS, PUBLISH):
            for job in workflow(path)["jobs"].values():
                for step in job["steps"]:
                    if "run" not in step:
                        continue
                    with self.subTest(path=path, step=step.get("name")):
                        result = subprocess.run(["bash", "-n"], input=step["run"],
                                                text=True, capture_output=True, check=False)
                        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
