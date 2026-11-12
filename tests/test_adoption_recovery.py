"""Regression fixtures for instruction selection and recoverable adoption."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("adoption_patch", ROOT / "hooks/project_setup.py")
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


def selected(root, fallbacks):
    # Native Codex prompt tests independently verify this documented precedence.
    return next((root / name for name in ("AGENTS.override.md", "AGENTS.md", *fallbacks)
                 if (root / name).is_file()), None)


class AdoptionRecoveryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def snapshot(self):
        return {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mode & 0o777)
                for p in self.root.rglob("*") if p.is_file()}

    def legacy(self, *, owner_addition="", shared_owner=""):
        policy = setup.POLICY.replace("v4.12.1", "v4.12") + "\n" + setup.LEGACY_FALLBACK
        policy += ". " + setup.LEGACY_BRIDGE + " when locating the previous fallback."
        self.put("AGENTS.md", setup.managed_rules(shared_owner, setup.START, setup.END, policy))
        self.put("CLAUDE.md", setup.managed_rules("", setup.START, setup.END, "@AGENTS.md") + owner_addition)
        self.put("TEAM.md", "TEAM_OWNER_NO_PUBLIC_DATA\n")

    def test_unknown_fallback_order_refuses_without_any_changes(self):
        self.put("TEAM.md", "OWNER\n")
        before = self.snapshot()
        with self.assertRaisesRegex(setup.SetupError, "fallback order is unknown"):
            setup.adopt(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_claude_fallback_remains_the_loaded_file(self):
        p = self.put("CLAUDE.md", "OWNER_NO_DEPLOY\n")
        path, _ = setup.adopt(self.root, codex_fallbacks=["CLAUDE.md"])
        self.assertEqual(path, p)
        self.assertEqual(selected(self.root, ["CLAUDE.md"]), p)
        self.assertIn("OWNER_NO_DEPLOY", p.read_text())
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_absent_higher_fallback_is_not_created_as_bridge(self):
        p = self.put("TEAM.md", "TEAM_OWNER\n")
        names = ["CLAUDE.md", "TEAM.md"]
        setup.adopt(self.root, codex_fallbacks=names)
        self.assertEqual(selected(self.root, names), p)
        self.assertFalse((self.root / "CLAUDE.md").exists())
        self.assertTrue((self.root / ".claude/CLAUDE.md").exists())
        self.assertNotIn("TEAM_OWNER", (self.root / ".claude/CLAUDE.md").read_text())
        self.assertFalse(setup.adopt(self.root, codex_fallbacks=names)[1])

    def test_custom_fallback_order_and_host_private_rules(self):
        team = self.put("TEAM.md", "CODEX_OWNER_ONLY\n")
        claude = self.put("CLAUDE.md", "CLAUDE_OWNER_ONLY\n")
        names = ["TEAM.md", "CLAUDE.md"]
        setup.adopt(self.root, codex_fallbacks=names)
        self.assertEqual(selected(self.root, names), team)
        self.assertNotIn("CLAUDE_OWNER_ONLY", team.read_text())
        self.assertNotIn("CODEX_OWNER_ONLY", claude.read_text())

    def test_empty_selected_fallback_keeps_precedence(self):
        team = self.put("TEAM.md", "")
        self.put("CLAUDE.md", "SHOULD_NOT_BE_CODEX_POLICY")
        setup.adopt(self.root, codex_fallbacks=["TEAM.md", "CLAUDE.md"])
        self.assertEqual(selected(self.root, ["TEAM.md", "CLAUDE.md"]), team)
        self.assertNotIn("SHOULD_NOT", team.read_text())

    def test_owner_edits_remain_live_not_copied_snapshots(self):
        team = self.put("TEAM.md", "OWNER_ONE\n")
        names = ["CLAUDE.md", "TEAM.md"]
        setup.adopt(self.root, codex_fallbacks=names)
        team.write_text(team.read_text() + "OWNER_TWO\n")
        self.assertIn("OWNER_TWO", selected(self.root, names).read_text())
        self.assertFalse(setup.adopt(self.root, codex_fallbacks=names)[1])

    def test_unconfigured_claude_rules_stay_claude_only(self):
        claude = self.put("CLAUDE.md", "CLAUDE_ONLY\n")
        setup.adopt(self.root, codex_fallbacks=[])
        self.assertEqual(selected(self.root, []).name, "AGENTS.md")
        self.assertNotIn("CLAUDE_ONLY", selected(self.root, []).read_text())
        self.assertIn("CLAUDE_ONLY", claude.read_text())

    def test_legacy_policy_repairs_fallback_without_shadowing(self):
        self.legacy()
        names = ["CLAUDE.md", "TEAM.md"]
        setup.adopt(self.root, codex_fallbacks=names)
        self.assertEqual(selected(self.root, names).name, "TEAM.md")
        self.assertIn("TEAM_OWNER_NO_PUBLIC_DATA", selected(self.root, names).read_text())
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertFalse((self.root / "CLAUDE.md").exists())
        self.assertFalse(setup.adopt(self.root, codex_fallbacks=names)[1])

    def test_legacy_bridge_with_new_owner_rules_is_never_ignored(self):
        self.legacy(owner_addition="NEW_OWNER_REQUIRE_APPROVAL\n")
        names = ["CLAUDE.md", "TEAM.md"]
        setup.adopt(self.root, codex_fallbacks=names)
        self.assertEqual(selected(self.root, names).name, "CLAUDE.md")
        self.assertIn("NEW_OWNER_REQUIRE_APPROVAL", selected(self.root, names).read_text())
        self.assertNotIn("Ignore the root", selected(self.root, names).read_text())

    def test_ambiguous_legacy_shared_owner_content_is_preserved(self):
        self.legacy(shared_owner="NEW_SHARED_OWNER\n")
        before = self.snapshot()
        with self.assertRaisesRegex(setup.SetupError, "also contains owner rules"):
            setup.adopt(self.root, codex_fallbacks=["TEAM.md"])
        self.assertEqual(self.snapshot(), before)

    def test_owner_authored_import_is_not_left_dangling_during_repair(self):
        self.legacy(owner_addition="@AGENTS.md\n")
        before = self.snapshot()
        with self.assertRaisesRegex(setup.SetupError, "owner-written Claude import"):
            setup.adopt(self.root, codex_fallbacks=["CLAUDE.md", "TEAM.md"])
        self.assertEqual(self.snapshot(), before)

    def test_nested_owner_import_blocks_legacy_shared_file_deletion(self):
        self.legacy()
        for reference in ("@../AGENTS.md", "@./../AGENTS.md"):
            with self.subTest(reference=reference):
                self.put(".claude/CLAUDE.md", reference + "\nNESTED_OWNER\n")
                before = self.snapshot()
                with self.assertRaisesRegex(setup.SetupError, "owner-written Claude import"):
                    setup.adopt(self.root, codex_fallbacks=["CLAUDE.md", "TEAM.md"])
                self.assertEqual(self.snapshot(), before)

    def test_unknown_legacy_fallback_order_is_not_guessed(self):
        self.legacy()
        before = self.snapshot()
        with self.assertRaises(setup.SetupError):
            setup.adopt(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_existing_shared_or_override_does_not_need_fallback_configuration(self):
        for name, text in (("AGENTS.md", "SHARED_OWNER\n"), ("AGENTS.override.md", "OVERRIDE_OWNER\n")):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / name).write_text(text)
                setup.adopt(root)
                self.assertTrue((root / name).read_text().startswith(text))
                self.assertFalse(setup.adopt(root)[1])

    def test_invalid_fallback_input_is_rejected_before_writes(self):
        for names in (["../outside"], ["dir/file"], ["dir\\file"], ["C:drive"], ["AGENTS.md"],
                      [""], [None], "CLAUDE.md", {"name": "TEAM.md"}):
            with self.subTest(names=names):
                with self.assertRaises(setup.SetupError):
                    setup.adopt(self.root, codex_fallbacks=names)
                self.assertEqual(self.snapshot(), {})

    def test_fenced_examples_with_longer_closings_receive_a_real_import(self):
        for opening, closing in (("```text", "````"), ("~~~md", "~~~~~"), ("  ```", "   ````")):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                original = f"{opening}\n@AGENTS.md\n{closing}\nOwner rule\n"
                (root / "CLAUDE.md").write_text(original)
                setup.adopt(root, codex_fallbacks=[])
                after = (root / "CLAUDE.md").read_text()
                self.assertTrue(after.endswith(original))
                self.assertIn(setup.START + "\n@AGENTS.md", after)
                self.assertTrue(setup.active_import(after, {"@AGENTS.md"}))
                self.assertFalse(setup.adopt(root, codex_fallbacks=[])[1])

    def test_unclosed_or_indented_example_does_not_hide_the_new_import(self):
        for original in ("```text\n@AGENTS.md\n", "Example:\n\n    @AGENTS.md\n", "Example:\n\n  \t@AGENTS.md\n", "~~~\n@AGENTS.md\n````\n"):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "CLAUDE.md").write_text(original)
                setup.adopt(root, codex_fallbacks=[])
                after = (root / "CLAUDE.md").read_text()
                self.assertTrue(after.endswith(original))
                self.assertIn(setup.START + "\n@AGENTS.md", after)
                self.assertTrue(setup.active_import(after, {"@AGENTS.md"}))

    def test_second_write_failure_restores_exact_existing_bytes_and_mode(self):
        p = self.put("CLAUDE.md", "OWNER\n")
        p.chmod(0o600)
        before = self.snapshot()
        writer = setup.write_rules
        def fail(path, *args):
            if path.name == "CLAUDE.md":
                raise PermissionError("injected write failure")
            return writer(path, *args)
        with patch.object(setup, "write_rules", fail):
            with self.assertRaisesRegex(setup.SetupError, "rolled back"):
                setup.adopt(self.root, codex_fallbacks=[])
        self.assertEqual(self.snapshot(), before)

    def test_failure_after_replace_still_rolls_back_attempted_file(self):
        before = self.snapshot()
        writer = setup.write_rules
        def fail(path, *args):
            result = writer(path, *args)
            if path.name == "CLAUDE.md":
                raise PermissionError("after replace")
            return result
        with patch.object(setup, "write_rules", fail):
            with self.assertRaisesRegex(setup.SetupError, "rolled back"):
                setup.adopt(self.root, codex_fallbacks=[])
        self.assertEqual(self.snapshot(), before)

    def test_failure_rolls_back_override_and_preserves_empty_file_existence(self):
        self.put("AGENTS.override.md", "")
        before = self.snapshot()
        writer = setup.write_rules
        def fail(path, *args):
            if path.name == "CLAUDE.md":
                raise PermissionError("third write")
            return writer(path, *args)
        with patch.object(setup, "write_rules", fail):
            with self.assertRaises(setup.SetupError):
                setup.adopt(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_repair_failure_restores_deleted_bridge_and_created_directory(self):
        self.legacy()
        before = self.snapshot()
        writer = setup.write_rules
        def fail(path, *args):
            if path.parent.name == ".claude":
                raise PermissionError("nested bridge write")
            return writer(path, *args)
        with patch.object(setup, "write_rules", fail):
            with self.assertRaises(setup.SetupError):
                setup.adopt(self.root, codex_fallbacks=["CLAUDE.md", "TEAM.md"])
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / ".claude").exists())

    def test_concurrent_edit_is_not_overwritten_and_private_recovery_is_retained(self):
        shared = self.put("AGENTS.md", "ORIGINAL_OWNER\n")
        self.put("CLAUDE.md", "CLAUDE_OWNER\n")
        writer = setup.write_rules
        recovery = self.root / "private-recovery"
        def make_recovery(**kwargs):
            recovery.mkdir(mode=0o700)
            return str(recovery)
        def fail(path, *args):
            if path.name == "CLAUDE.md":
                shared.write_text("CONCURRENT_OWNER_EDIT\n")
                raise PermissionError("injected")
            return writer(path, *args)
        with patch.object(setup.tempfile, "mkdtemp", make_recovery), patch.object(setup, "write_rules", fail):
            with self.assertRaisesRegex(setup.SetupError, "adoption incomplete"):
                setup.adopt(self.root)
        self.assertEqual(shared.read_text(), "CONCURRENT_OWNER_EDIT\n")
        manifest = json.loads((recovery / "recovery.json").read_text())
        original = next(m for m in manifest if m["path"] == str(shared))
        self.assertEqual((recovery / original["before"]).read_text(), "ORIGINAL_OWNER\n")
        self.assertEqual((recovery / original["before"]).stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
