#!/usr/bin/env python3
"""Deterministic mock Codex CLI tests. Run: python3 -m unittest discover -s tests -v"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / "scripts" / "codex-review.py"
MOCK = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
if args[:2] == ['login', 'status']:
    sys.exit(1 if os.environ.get('FAKE_MODE') == 'login' else 0)
assert args[:3] == ['--ask-for-approval', 'never', 'exec'] and args[-1] == '-'
assert args[args.index('--sandbox') + 1] == 'read-only'
assert args[args.index('--ask-for-approval') + 1] == 'never'
assert args[args.index('-c') + 1] == 'model_reasoning_effort=' + os.environ['EXPECT_EFFORT']
assert Path(args[args.index('--output-schema') + 1]).is_file()
assert 'Head SHA:' in sys.stdin.read()
mode = os.environ.get('FAKE_MODE')
if mode == 'execution': sys.exit(7)
if mode == 'invalid':
    Path(args[args.index('--output-last-message') + 1]).write_text('bad json')
    sys.exit(0)
report = {'head_sha': os.environ['EXPECT_HEAD'], 'verdict': 'APPROVE',
          'findings': [], 'previous_findings': [], 'unverified_requirements': []}
if mode == 'reject': report['verdict'] = 'REJECT'
if mode == 'stale': report['head_sha'] = '0' * 40
if mode == 'unverified': report['unverified_requirements'] = ['R-01']
if mode == 'spec': report['findings'] = [{'kind': 'spec_question', 'severity': 'minor'}]
if mode == 'previous': report['previous_findings'] = [{'id': 'F-1', 'status': 'open', 'evidence': 'still broken'}]
if mode == 'incomplete': report['findings'] = [{}]
Path(args[args.index('--output-last-message') + 1]).write_text(json.dumps(report))
'''


class TestCodexReview(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.sandbox = Path(self.tmp.name)
        self.root = self.sandbox / "repo"
        self.root.mkdir()
        (self.sandbox / "bin").mkdir()
        mock = self.sandbox / "bin" / "codex"
        mock.write_text(MOCK)
        mock.chmod(0o755)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.org",
                        "commit", "--allow-empty", "-qm", "initial"], cwd=self.root, check=True)
        self.sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.brief = self.root.parent / f"vibe-brief-{self.root.name}.txt"
        self.brief.write_text("Head SHA: " + self.sha)
        self.addCleanup(lambda: self.brief.unlink(missing_ok=True))
        self.output = self.root.parent / f"vibe-report-{self.root.name}.json"
        self.addCleanup(lambda: self.output.unlink(missing_ok=True))

    def run_review(self, mode="ok", effort="medium", head=None):
        env = dict(os.environ, PATH=str(self.sandbox / "bin") + os.pathsep + os.environ["PATH"],
                   FAKE_MODE=mode, EXPECT_HEAD=self.sha, EXPECT_EFFORT=effort)
        return subprocess.run([sys.executable, str(RUNNER), "--brief", str(self.brief),
                               "--head", head or self.sha, "--effort", effort,
                               "--output", str(self.output)], cwd=self.root,
                              env=env, text=True, capture_output=True)

    def test_approved_for_each_effort(self):
        for effort in ("medium", "high", "xhigh"):
            with self.subTest(effort=effort):
                self.assertEqual(self.run_review(effort=effort).returncode, 0)

    def test_fail_closed(self):
        for mode in ("login", "execution", "invalid", "reject", "stale", "unverified", "spec", "previous", "incomplete"):
            with self.subTest(mode=mode):
                self.assertNotEqual(self.run_review(mode=mode).returncode, 0)

    def test_wrong_head_rejected(self):
        self.assertNotEqual(self.run_review(head="0" * 40).returncode, 0)

    def test_dirty_worktree_rejected(self):
        (self.root / "untracked.txt").write_text("dirty")
        self.assertNotEqual(self.run_review().returncode, 0)

    def test_old_approval_cannot_survive_failure(self):
        self.assertEqual(self.run_review().returncode, 0)
        self.assertTrue(self.output.exists())
        self.assertNotEqual(self.run_review(mode="execution").returncode, 0)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
