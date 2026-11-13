"""Deterministic Vibe governance tests; no model calls or external changes."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('vibe_governance', ROOT / 'hooks/governance.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)

class GovernanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def item(self):
        return g.report(self.root)['conflicts'][0]

    def test_recognizes_both_host_rules(self):
        self.put('CLAUDE.md', 'Run the full test suite before every commit.\n')
        self.put('AGENTS.md', 'Every change must use an independent review.\n')
        ids = {x['id'] for x in g.report(self.root)['conflicts']}
        self.assertEqual(ids, {'testing.full-on-commit','review.every-change'})
        self.assertFalse((self.root / 'docs').exists())

    def test_ignores_fenced_and_managed_examples(self):
        self.put('CLAUDE.md', '~~~\nRun the full test suite before every commit.\n~~~~\n'
                 '<!-- vibe:project:start -->\nRun the full suite before every push.\n<!-- vibe:project:end -->\n'
                 'Avoid full suite before every commit.\n')
        self.assertEqual(g.report(self.root)['conflicts'], [])

    def test_security_and_product_rules_are_not_conflicts(self):
        self.put('AGENTS.md', 'Arabic RTL UI. Require review for authentication and privacy changes.\n')
        self.assertEqual(g.report(self.root)['conflicts'], [])

    def test_decisions_need_approval_and_preserve_existing_text(self):
        self.put('CLAUDE.md', 'Run the full test suite before every commit.\n')
        p = self.put('docs/DECISIONS.md', '# Decisions\nKeep this owner choice.\n')
        item = self.item()
        with self.assertRaises(g.GovernanceError):
            g.decide(self.root,item['id'],item['fingerprint'],'keep-project',False)
        self.assertTrue(g.decide(self.root,item['id'],item['fingerprint'],'keep-project',True))
        self.assertFalse(g.decide(self.root,item['id'],item['fingerprint'],'keep-project',True))
        self.assertEqual(self.item()['state'], 'accepted-exception')
        self.assertTrue(p.read_text().startswith('# Decisions\nKeep this owner choice.\n'))

    def test_align_is_pending_and_gates_not_changed(self):
        path = self.put('CLAUDE.md','Run the full test suite before every commit.\n')
        item = self.item()
        g.decide(self.root,item['id'],item['fingerprint'],'align-vibe',True)
        self.assertEqual(self.item()['state'],'alignment-pending')
        self.assertEqual(path.read_text(),'Run the full test suite before every commit.\n')

    def test_conflict_change_invalidates_old_decision(self):
        path = self.put('CLAUDE.md','Run the full test suite before every commit.\n')
        item = self.item()
        g.decide(self.root,item['id'],item['fingerprint'],'defer',True)
        path.write_text('Must run the entire test suite before each commit.\n')
        self.assertEqual(self.item()['state'],'unresolved')
        with self.assertRaises(g.GovernanceError):
            g.decide(self.root,item['id'],item['fingerprint'],'keep-project',True)

    def test_malformed_record_fails_closed(self):
        self.put('AGENTS.md','Run the full test suite before every commit.\n')
        item = self.item()
        p = self.put('docs/DECISIONS.md',g.START+'\n- broken record\n'+g.END)
        with self.assertRaises(g.GovernanceError):
            g.decide(self.root,item['id'],item['fingerprint'],'keep-project',True)
        self.assertIn('broken record',p.read_text())

    def test_no_symlink_following(self):
        outside = self.root.parent / (self.root.name + '-owner')
        outside.write_text('Run the full test suite before every commit.\n')
        (self.root/'AGENTS.md').symlink_to(outside)
        r = g.report(self.root)
        self.assertTrue(r['warnings'])
        self.assertFalse(r['conflicts'])
        self.assertIn('Run the full',outside.read_text())

    def test_active_hook_is_not_executed(self):
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        p = self.put('.git/hooks/pre-push', '#!/bin/sh\nnpx playwright test\ntouch SHOULD_NOT_EXIST\n')
        p.chmod(0o755)
        self.assertEqual(self.item()['id'],'testing.full-on-push')
        self.assertFalse((self.root/'SHOULD_NOT_EXIST').exists())
        p.chmod(0o644)
        self.assertEqual(g.report(self.root)['conflicts'],[])

    def test_slash_and_continuity(self):
        self.put('AGENTS.md','You must use /vibe:build for every task.\nNever update status files.\n')
        ids = {x['id'] for x in g.report(self.root)['conflicts']}
        self.assertIn('workflow.slash-required',ids)
        self.assertIn('continuity.no-checkpoint',ids)

if __name__ == '__main__':
    unittest.main()
