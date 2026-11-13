"""Deterministic Vibe governance tests; no model calls or external changes."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

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

    def test_fenced_and_inline_marker_examples_preserve_owner_prose(self):
        self.put('AGENTS.md', '~~~html\n<!-- vibe:project:start -->\n~~~~\n'
                 'Use the marker <!-- vibe:governance:start --> in documentation.\n'
                 '> <!-- vibe:project:start -->\nRun all tests before every commit.\n'
                 'Before each push run all tests.\n')
        result = g.report(self.root)
        self.assertEqual(result['warnings'], [])
        self.assertEqual({i['id'] for i in result['conflicts']},
                         {'testing.full-on-commit', 'testing.full-on-push'})

    def test_ambiguous_blocks_require_manual_inspection(self):
        for marker in ('<!-- vibe:project:start -->', g.END, g.START + '\n' + g.START,
                       g.START + '\n<!-- vibe:project:end -->'):
            with self.subTest(marker=marker):
                self.put('AGENTS.md', marker + '\nRun all tests before every push.')
                self.assertTrue(g.report(self.root)['warnings'])

    def test_scoped_rules_follow_the_work_directory_and_keep_separate_decisions(self):
        self.put('CLAUDE.md', 'Root rules.')
        for directory in ('src', 'other'):
            self.put(directory + '/AGENTS.md', 'Run all tests before every commit.')
            self.put(directory + '/ui/.claude/CLAUDE.md', 'Run all tests before every push.')
        for directory in ('src', 'other'):
            scope = Path(directory, 'ui')
            report = g.report(self.root, scope)
            self.assertFalse(report['warnings'])
            commit, push = report['conflicts']
            self.assertEqual(commit['sources'], [directory + '/AGENTS.md:1'])
            self.assertEqual(push['sources'], [directory + '/ui/.claude/CLAUDE.md:1'])
            self.assertIsNone(commit['decision'])
            g.decide(self.root, commit['id'], commit['fingerprint'], 'keep-project', True, scope)
        self.assertEqual(g.report(self.root, Path('src/ui'))['conflicts'][0]['decision'], 'keep-project')
        self.assertFalse(g.report(self.root)['conflicts'])
        for invalid in ('..', 'missing-directory', 'deep/' * 17):
            with self.assertRaises(g.GovernanceError):
                g.report(self.root, Path(invalid))

    def test_context_change_invalidates_the_owner_choice(self):
        path = self.put('AGENTS.md', 'For release branches only:\nRun all tests before every push.')
        item = self.item()
        g.decide(self.root, item['id'], item['fingerprint'], 'defer', True)
        path.write_text('For all branches including routine development:\nRun all tests before every push.')
        self.assertEqual(self.item()['state'], 'unresolved')
        with self.assertRaises(g.GovernanceError):
            g.decide(self.root, item['id'], item['fingerprint'], 'keep-project', True)

    def test_publication_and_cleanup_use_the_open_decision_directory(self):
        self.put('AGENTS.md', 'Run all tests before every push.')
        self.put(g.DECISIONS, '# Owner decisions\n')
        item = self.item()
        with mock.patch.object(g.os, 'replace', wraps=g.os.replace) as replace, \
                mock.patch.object(g.os, 'unlink', wraps=g.os.unlink) as unlink:
            g.decide(self.root, item['id'], item['fingerprint'], 'keep-project', True)
        (temporary, destination), handles = replace.call_args
        self.assertEqual(destination, 'DECISIONS.md')
        self.assertEqual(Path(temporary).name, temporary)
        self.assertIsInstance(handles['src_dir_fd'], int)
        self.assertEqual(handles['dst_dir_fd'], handles['src_dir_fd'])
        unlink.assert_called_once_with(temporary, dir_fd=handles['src_dir_fd'])

    def test_substituted_directory_identity_is_rejected(self):
        self.put('AGENTS.md', 'Run all tests before every push.')
        path = self.put(g.DECISIONS, '# Owner decisions\n')
        item = self.item()
        archived = self.root / 'previous-docs'
        snapshot = g.snapshot
        calls = 0

        def refresh_directory(docs):
            nonlocal calls
            calls += 1
            if calls == 2:
                path.parent.rename(archived)
                path.parent.mkdir()
                path.write_text('# Replacement directory\n')
            return snapshot(docs)

        with mock.patch.object(g, 'snapshot', side_effect=refresh_directory):
            with self.assertRaisesRegex(g.GovernanceError, 'directory changed'):
                g.decide(self.root, item['id'], item['fingerprint'], 'defer', True)
        self.assertEqual(path.read_text(), '# Replacement directory\n')
        self.assertEqual([p.name for p in archived.iterdir()], ['DECISIONS.md'])
        self.assertEqual((archived / 'DECISIONS.md').read_text(), '# Owner decisions\n')

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
