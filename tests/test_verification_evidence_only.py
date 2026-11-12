"""Evidence-only verification uses real Git candidates and never launches a gate."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "hooks/verification-cache.py"


class EvidenceOnlyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.repo / ".gitignore").write_text(".runs\n")
        (self.repo / "source").write_text("initial")
        (self.repo / "gate.py").write_text(
            "from pathlib import Path\nimport os, sys\n"
            "p=Path('.runs'); p.write_text((p.read_text() if p.exists() else '')+sys.argv[-1]+'\\n')\n"
            "sys.exit(int(os.environ.get('GATE_EXIT','0')))\n")
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, text=True,
                              capture_output=True, check=True).stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture")

    def call(self, action="check", mode="full", flags=(), updates=None, context="stable", env=None):
        return subprocess.run([sys.executable, str(HELPER), action, "--mode", mode,
                               "--context", context, *flags, "--", sys.executable, "gate.py"],
                              cwd=self.repo, input=updates, text=True, capture_output=True,
                              env={**os.environ, **(env or {})}, timeout=10)

    def count(self):
        p = self.repo / ".runs"
        return p.read_text().splitlines() if p.exists() else []

    def update(self, ref="HEAD", remote="refs/heads/release"):
        return f"{ref} {self.git('rev-parse', ref)} {remote} {'0' * 40}\n"

    def test_missing_evidence_fails_without_running(self):
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("run verification separately", result.stderr)
        self.assertEqual(self.count(), [])

    def test_same_inputs_pass_without_running_again(self):
        self.assertEqual(self.call("run").returncode, 0)
        self.assertEqual(self.call().returncode, 0)
        self.assertEqual(self.count(), ["full"])

    def test_quick_does_not_satisfy_full(self):
        self.assertEqual(self.call("run", mode="quick").returncode, 0)
        self.assertNotEqual(self.call().returncode, 0)
        self.assertEqual(self.count(), ["quick"])

    def test_full_covers_quick_only_with_explicit_contract(self):
        self.assertEqual(self.call("run").returncode, 0)
        self.assertNotEqual(self.call(mode="quick").returncode, 0)
        self.assertEqual(self.call("run", flags=("--full-includes-quick",)).returncode, 0)
        self.assertEqual(self.call(mode="quick", flags=("--full-includes-quick",)).returncode, 0)
        self.assertEqual(self.count(), ["full", "full"])

    def test_changed_candidate_or_context_cannot_reuse(self):
        self.assertEqual(self.call("run").returncode, 0)
        self.assertNotEqual(self.call(context="changed").returncode, 0)
        (self.repo / "source").write_text("changed")
        self.commit()
        self.assertNotEqual(self.call().returncode, 0)
        self.assertEqual(self.count(), ["full"])

    def test_dirty_checkout_cannot_reuse(self):
        self.assertEqual(self.call("run").returncode, 0)
        (self.repo / "untracked").write_text("dirty")
        self.assertNotEqual(self.call().returncode, 0)
        self.assertEqual(self.count(), ["full"])

    def test_failed_or_interrupted_rerun_invalidates_old_pass(self):
        for code in (9, 130):
            with self.subTest(code=code):
                self.assertEqual(self.call("run").returncode, 0)
                self.assertEqual(self.call("run", flags=("--fresh",), env={"GATE_EXIT": str(code)}).returncode, code)
                before = self.count()
                self.assertNotEqual(self.call().returncode, 0)
                self.assertEqual(self.count(), before)

    def test_malformed_record_and_pending_lock_fail_closed(self):
        self.assertEqual(self.call("run").returncode, 0)
        directory = self.repo / ".git/vibe-verification"
        lock = directory / "active.lock"
        lock.write_text("pending")
        self.assertNotEqual(self.call().returncode, 0)
        lock.unlink()
        next(directory.glob("*.json")).write_text("{bad")
        self.assertNotEqual(self.call().returncode, 0)
        self.assertEqual(self.count(), ["full"])

    def test_require_evidence_pre_push_checks_actual_refs_without_running(self):
        self.assertEqual(self.call("run").returncode, 0)
        main = self.update("main", "refs/heads/main")
        self.git("checkout", "-qb", "other")
        (self.repo / "source").write_text("other")
        self.commit()
        other = self.update("other")
        self.git("checkout", "-q", "main")
        flags = ("--require-evidence",)
        self.assertEqual(self.call("pre-push", flags=flags, updates=main).returncode, 0)
        self.assertNotEqual(self.call("pre-push", flags=flags, updates=main + other).returncode, 0)
        self.assertEqual(self.count(), ["full"])

    def test_annotated_commit_tag_uses_matching_evidence(self):
        self.assertEqual(self.call("run").returncode, 0)
        self.git("tag", "-am", "Candidate", "v-test")
        result = self.call("pre-push", flags=("--require-evidence",),
                           updates=self.update("v-test", "refs/tags/v-test"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.count(), ["full"])

    def test_malformed_updates_fail_and_deletion_skips_source_checks(self):
        for update in ("bad\n", "HEAD invalid refs/heads/main " + "0" * 40 + "\n"):
            self.assertNotEqual(self.call("pre-push", flags=("--require-evidence",), updates=update).returncode, 0)
        (self.repo / "source").write_text("dirty")
        deleted = f"(delete) {'0' * 40} refs/heads/old {self.git('rev-parse', 'HEAD')}\n"
        self.assertEqual(self.call("pre-push", flags=("--require-evidence",), updates=deleted).returncode, 0)
        self.assertEqual(self.count(), [])

    def test_incompatible_flags_are_usage_errors(self):
        for action, flags in (("check", ("--fresh",)), ("run", ("--require-evidence",)),
                              ("pre-push", ("--fresh", "--require-evidence"))):
            self.assertEqual(self.call(action, flags=flags).returncode, 2)
        self.assertEqual(self.count(), [])

    def test_check_does_not_borrow_another_worktrees_evidence(self):
        self.assertEqual(self.call("run").returncode, 0)
        worker = self.repo / ".git/worker"
        self.git("worktree", "add", "--detach", "-q", str(worker), "HEAD")
        original = self.repo
        self.repo = worker
        try:
            self.assertNotEqual(self.call().returncode, 0)
            self.assertEqual(self.count(), [])
        finally:
            self.repo = original


if __name__ == "__main__":
    unittest.main()
