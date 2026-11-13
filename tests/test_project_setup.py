"""Project policy adoption and bounded advisory checks, without model calls."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("project_setup", ROOT / "hooks/project_setup.py")
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class LocalGit:
    def __init__(self, cwd):
        self.cwd = cwd

    def text(self, *args):
        result = subprocess.run(["git", "-C", str(self.cwd), *args],
                                text=True, capture_output=True, timeout=2)
        return result.stdout.strip() if result.returncode == 0 else None


class ProjectSetupTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.git = LocalGit(self.root)

    def write(self, name, text, executable=False):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        if executable:
            path.chmod(0o755)
        return path

    def hook(self, text, directory=".git/hooks", name="pre-push"):
        return self.write(directory + "/" + name, text, True)

    def inspect(self):
        before = self.git.text("status", "--porcelain")
        result = setup.inspect_project(self.git)
        self.assertEqual(self.git.text("status", "--porcelain"), before)
        self.assertLessEqual(len(result), 1200)
        return result

    def test_adopts_empty_project_once(self):
        path, changed = setup.adopt(self.root, codex_fallbacks=[])
        self.assertTrue(changed)
        self.assertEqual(path, self.root / "AGENTS.md")
        self.assertIn("@AGENTS.md", (self.root / "CLAUDE.md").read_text())
        original = path.read_bytes()
        self.assertFalse(setup.adopt(self.root, codex_fallbacks=[])[1])
        self.assertEqual(path.read_bytes(), original)
        self.assertIn("not completed hook/CI migration", path.read_text())
        self.assertEqual(path.read_text().count(setup.START), 1)

    def test_managed_policy_migrates_from_v413_without_overwriting_owner_rules(self):
        self.assertIn("routine work or feature deployment", setup.POLICY)
        self.assertIn("formal production release/promotion", setup.POLICY)
        self.assertIn("explicit owner E2E request", setup.POLICY)
        legacy = setup.POLICY.replace("managed; v4.14.0", "managed; v4.13.0")
        legacy = legacy.replace(
            "Use feature-scoped unit/integration/component and UI/API acceptance for routine work or feature deployment, including auto-deploying merges; do not automatically run whole-journey E2E. Expand for shared, high-risk or uncertain impact, and preserve relevant smoke/rollback checks. Require full relevant checks and E2E for formal production release/promotion or an explicit owner E2E request. Existing project gates still apply; reuse only matching, sufficient evidence.",
            "Use affected checks and targeted browser acceptance during development, expand for shared or uncertain impact, and require full integrated evidence before production delivery. Reuse only matching, sufficient evidence.")
        owner = "Owner constraint: require review before sensitive data changes.\\n"
        shared = self.write("AGENTS.md", setup.managed_rules(owner, setup.START, setup.END, legacy))
        setup.adopt(self.root, codex_fallbacks=[])
        self.assertIn(owner, shared.read_text())
        self.assertIn("managed; v4.14.0", shared.read_text())
        self.assertNotIn("full integrated evidence before production delivery", shared.read_text())
        self.assertFalse(setup.adopt(self.root, codex_fallbacks=[])[1])

    def test_preserves_existing_rules_and_permissions(self):
        path = self.write("CLAUDE.md", "# Owner policy\nNever weaken production checks.\n")
        path.chmod(0o600)
        before = path.read_bytes()
        setup.adopt(self.root, codex_fallbacks=[])
        self.assertTrue(path.read_bytes().endswith(before))
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_updates_only_managed_block_and_preserves_crlf(self):
        path = self.root / "CLAUDE.md"
        before = ("owner prefix\r\n" + setup.START + "\r\nold policy\r\n" +
                  setup.END + "\r\nowner suffix\r\n").encode()
        path.write_bytes(before)
        setup.adopt(self.root, codex_fallbacks=[])
        after = path.read_bytes()
        self.assertTrue(after.startswith(b"owner prefix\r\n"))
        self.assertTrue(after.endswith(b"\r\nowner suffix\r\n"))
        self.assertNotIn(b"\n", after.replace(b"\r\n", b""))

    def test_uses_existing_nested_rules_without_creating_duplicate(self):
        nested = self.write(".claude/CLAUDE.md", "nested owner rules\n")
        self.assertEqual(setup.adopt(self.root, codex_fallbacks=[])[0], self.root / "AGENTS.md")
        self.assertIn("@../AGENTS.md", nested.read_text())
        self.assertFalse((self.root / "CLAUDE.md").exists())

    def test_refuses_duplicate_missing_or_reversed_markers(self):
        for content in (setup.START, setup.END, (setup.START + setup.END) * 2,
                        setup.END + "\n" + setup.START):
            with self.subTest(content=content):
                path = self.write("CLAUDE.md", content)
                with self.assertRaises(setup.SetupError):
                    setup.adopt(self.root, codex_fallbacks=[])
                self.assertEqual(path.read_text(), content)
                self.assertFalse((self.root / "AGENTS.md").exists())

    def test_migrates_legacy_claude_block_and_reuses_existing_shared_rules(self):
        shared = self.write("AGENTS.md", "Owner's shared rules\n")
        claude = self.write("CLAUDE.md", f"Claude rules\n{setup.START}\nold policy\n{setup.END}\nEnd\n")
        setup.adopt(self.root, codex_fallbacks=[])
        self.assertTrue(shared.read_text().startswith("Owner's shared rules\n"))
        self.assertIn(setup.POLICY, shared.read_text())
        self.assertEqual(claude.read_text(), f"Claude rules\n{setup.START}\n@AGENTS.md\n{setup.END}\nEnd\n")
        self.assertFalse(setup.adopt(self.root, codex_fallbacks=[])[1])

    def test_populated_override_receives_policy_without_sharing_owner_rules(self):
        override = self.root / "AGENTS.override.md"
        owner = b"Private Codex rules\r\n"
        override.write_bytes(owner)
        shared, changed = setup.adopt(self.root, codex_fallbacks=[])
        self.assertTrue(changed)
        self.assertTrue(override.read_bytes().startswith(owner))
        self.assertIn(setup.POLICY, override.read_text())
        self.assertNotIn("Private Codex rules", shared.read_text())
        self.assertNotIn("Private Codex rules", (self.root / "CLAUDE.md").read_text())
        self.assertEqual(override.read_text().count(setup.START), 1)
        self.assertFalse(setup.adopt(self.root, codex_fallbacks=[])[1])

    def test_configured_fallback_keeps_owner_rules_natively_loaded(self):
        claude = self.write("CLAUDE.md", "Owner's existing project constraints\n")
        target, _ = setup.adopt(self.root, codex_fallbacks=["CLAUDE.md"])
        self.assertEqual(target, claude)
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertTrue(claude.read_text().startswith("Owner's existing project constraints"))
        with claude.open("a", encoding="utf-8") as rules:
            rules.write("Additional owner rules\n")
        self.assertFalse(setup.adopt(self.root, codex_fallbacks=["CLAUDE.md"])[1])
        self.assertIn("Additional owner rules", claude.read_text())

    def test_existing_shared_owner_rules_keep_their_precedence(self):
        shared = self.write("AGENTS.md", "Use these project rules\n")
        self.write("CLAUDE.md", "Claude-only rule\n")
        setup.adopt(self.root, codex_fallbacks=[])
        self.assertNotIn("project_doc_fallback_filenames", shared.read_text())

    def test_preserves_existing_import(self):
        claude = self.write("CLAUDE.md", "@./AGENTS.md\nPersonal instructions\n")
        before = claude.read_bytes()
        setup.adopt(self.root, codex_fallbacks=[])
        self.assertEqual(claude.read_bytes(), before)

    def test_import_in_a_code_example_is_not_an_active_import(self):
        claude = self.write("CLAUDE.md", "~~~text\n@AGENTS.md\n~~~\n")
        setup.adopt(self.root, codex_fallbacks=[])
        self.assertIn(f"{setup.START}\n@AGENTS.md", claude.read_text())

    def test_refuses_symlink_rules_or_parent(self):
        outside = self.root.parent / "owner.md"
        outside.write_text("untouched")
        (self.root / "CLAUDE.md").symlink_to(outside)
        with self.assertRaises(setup.SetupError):
            setup.adopt(self.root, codex_fallbacks=[])
        self.assertEqual(outside.read_text(), "untouched")
        (self.root / "CLAUDE.md").unlink()
        (self.root / ".claude").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(setup.SetupError):
            setup.adopt(self.root, codex_fallbacks=[])

    def test_unreadable_encoding_and_oversized_policy_are_preserved(self):
        for content in (b"\xff", b"x" * 131073):
            with self.subTest(size=len(content)):
                path = self.root / "CLAUDE.md"
                path.write_bytes(content)
                with self.assertRaises(setup.SetupError):
                    setup.adopt(self.root, codex_fallbacks=[])
                self.assertEqual(path.read_bytes(), content)

    def test_empty_project_is_silent_and_does_not_adopt_at_startup(self):
        self.assertEqual(self.inspect(), "")
        self.assertFalse((self.root / "CLAUDE.md").exists())

    def test_active_hook_package_chain_is_advisory_and_never_executed(self):
        sentinel = self.root / "DO_NOT_CREATE"
        self.hook("#!/bin/sh\nnpm run verify\ntouch DO_NOT_CREATE\n")
        self.write("package.json", json.dumps({"scripts": {"verify": "bash scripts/verify.sh"}}))
        self.write("scripts/verify.sh", "#!/bin/sh\nnpx playwright test\n")
        notice = self.inspect()
        self.assertIn("pre-push", notice)
        self.assertIn("may run broad verification", notice)
        self.assertIn("before calling this a conflict", notice)
        self.assertFalse(sentinel.exists())
        self.assertEqual(self.inspect(), "")
        self.write("scripts/verify.sh", "#!/bin/sh\nnpx playwright test --workers=1\n")
        self.assertIn("pre-push", self.inspect())

    def test_effective_relative_and_external_hook_paths(self):
        for directory in ("custom-hooks", str(self.root.parent / "external-hooks")):
            with self.subTest(directory=directory):
                self.git.text("config", "core.hooksPath", directory)
                self.hook("#!/bin/sh\nnpx playwright test\n", directory=directory)
                self.assertIn("pre-push", self.inspect())

    def test_inactive_hook_does_not_warn(self):
        self.write(".git/hooks/pre-push", "#!/bin/sh\nnpx playwright test\n")
        self.assertEqual(self.inspect(), "")

    def test_targeted_browser_and_cheap_checks_are_not_automatic_conflicts(self):
        self.hook("#!/bin/sh\nnpx playwright test tests/login.spec.ts\nnpm run lint\n")
        self.write("package.json", json.dumps({"scripts": {"lint": "eslint ."}}))
        self.assertEqual(self.inspect(), "")

    def test_evidence_only_hook_does_not_follow_gate_as_an_executed_command(self):
        self.hook("#!/bin/sh\npython3 .githooks/verification-cache.py pre-push --require-evidence "
                  "--mode full --context x -- scripts/verify.sh\n")
        self.write("scripts/verify.sh", "npx playwright test\n")
        self.assertEqual(self.inspect(), "")

    def test_evidence_only_call_cannot_hide_a_second_full_gate(self):
        self.hook("#!/bin/sh\npython3 .githooks/verification-cache.py check --mode full "
                  "--context x -- scripts/verify.sh; npx playwright test\n")
        self.write("scripts/verify.sh", "npx playwright test\n")
        self.assertIn("may run broad", self.inspect())

    def test_project_rule_and_workflow_paths_are_reported_without_content(self):
        self.write("CLAUDE.md", "Run full verification before each push. PRIVATE_SECRET\n")
        self.write(".github/workflows/test.yml", "steps:\n  - run: npx playwright test\n")
        notice = self.inspect()
        self.assertIn("CLAUDE.md", notice)
        self.assertIn("test.yml", notice)
        self.assertNotIn("PRIVATE_SECRET", notice)
        cache = (self.root / ".git/vibe-project-gates.json").read_text()
        self.assertNotIn("PRIVATE_SECRET", cache)

    def test_negated_policy_is_not_a_conflict(self):
        self.write("CLAUDE.md", "Never run the full suite on every push.\n")
        self.assertEqual(self.inspect(), "")

    def test_large_and_special_inputs_fail_as_advice_not_startup_failure(self):
        self.write("package.json", "x" * (setup.MAX_FILE + 1))
        self.assertIn("incomplete", self.inspect())
        (self.root / "package.json").unlink()
        os.mkfifo(self.root / "package.json")
        self.assertIn("incomplete", self.inspect())

    def test_symlinked_sources_are_not_read_or_followed(self):
        outside = self.root.parent / "secret"
        outside.write_text("Run full verification before push.\n")
        (self.root / "CLAUDE.md").symlink_to(outside)
        self.assertIn("incomplete", self.inspect())

    def test_workflow_count_limit_and_corrupt_cache(self):
        for index in range(setup.MAX_WORKFLOWS + 2):
            self.write(f".github/workflows/check-{index}.yml", "steps: []\n")
        self.assertIn("incomplete", self.inspect())
        (self.root / ".git/vibe-project-gates.json").write_text("{broken")
        self.assertIn("incomplete", self.inspect())

    def test_elapsed_budget_returns_bounded_incomplete_advice(self):
        with patch.object(setup, "MAX_SECONDS", -1):
            self.assertIn("incomplete", self.inspect())


if __name__ == "__main__":
    unittest.main()
