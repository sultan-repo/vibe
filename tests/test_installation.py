"""Manual installs preserve personal settings and load project continuity once."""
import copy
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InstallationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        # Exercise shell quoting without ever executing text from this pathname.
        self.home = self.base / "owner's Claude $notes"
        self.home.mkdir()
        self.env = os.environ.copy()
        self.env["VIBE_CLAUDE_HOME"] = str(self.home)
        self.env.pop("CLAUDE_PLUGIN_ROOT", None)
        self.env.pop("CLAUDE_PROJECT_DIR", None)
        self.personal = "# Personal rules\nKeep my preferences.\n"
        (self.home / "CLAUDE.md").write_text(self.personal, encoding="utf-8")
        (self.home / "hooks").mkdir()
        (self.home / "hooks" / "personal.sh").write_text("personal hook\n", encoding="utf-8")
        self.settings = {
            "permissions": {"allow": ["Read"]},
            "hooks": {
                "SessionStart": [{"matcher": "startup", "hooks": [
                    {"type": "command", "command": "printf personal-start"}]}],
                "PreToolUse": [{"matcher": "Bash", "hooks": [
                    {"type": "command", "command": "printf personal-pre"}]}],
                "Stop": [{"hooks": [
                    {"type": "command", "command": "printf personal-stop"}]}],
            },
        }
        self.write_settings(self.settings)

    def write_settings(self, settings):
        (self.home / "settings.json").write_text(json.dumps(settings), encoding="utf-8")

    def read_settings(self):
        return json.loads((self.home / "settings.json").read_text(encoding="utf-8"))

    def run_script(self, filename):
        return subprocess.run(["bash", str(ROOT / filename)], cwd=self.base,
                              env=self.env, check=True, capture_output=True, text=True)

    def startup_command(self):
        expected = [str(self.home / "vibe-tools" / "session-start.sh"), "--status-only"]
        commands = [hook["command"]
                    for entry in self.read_settings()["hooks"]["SessionStart"]
                    for hook in entry["hooks"]
                    if shlex.split(hook.get("command", "")) == expected]
        self.assertEqual(len(commands), 1)
        return commands[0]

    def test_reinstall_preserves_personal_settings_without_duplicate_hooks(self):
        self.run_script("install.sh")
        first = self.read_settings()
        self.run_script("install.sh")
        self.assertEqual(self.read_settings(), first)
        self.assertEqual(first["permissions"], self.settings["permissions"])
        self.assertEqual(set(first["hooks"]), set(self.settings["hooks"]))
        for event, entries in self.settings["hooks"].items():
            self.assertEqual(first["hooks"][event][0], entries[0])
        self.assertEqual(len(first["hooks"]["SessionStart"]), 2)
        self.assertEqual(len(first["hooks"]["PreToolUse"]), 2)
        self.assertEqual(shlex.split(self.startup_command()),
                         [str(self.home / "vibe-tools" / "session-start.sh"), "--status-only"])
        personal = (self.home / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertTrue(personal.startswith(self.personal))
        self.assertEqual(personal.count("@~/.claude/vibe.md"), 1)
        self.assertTrue(os.access(self.home / "vibe-tools" / "session-start.sh", os.X_OK))
        self.assertTrue((self.home / "vibe-tools" / "session-start.py").is_file())
        self.assertTrue((self.home / "vibe-tools" / "project_setup.py").is_file())
        self.assertTrue((self.home / "vibe-tools" / "project-adoption.md").is_file())
        self.assertTrue((self.home / "vibe-tools" / "governance.py").is_file())
        self.assertTrue((self.home / "vibe-tools" / "governance.md").is_file())

    def test_uninstall_removes_only_owned_hooks_and_files(self):
        self.run_script("install.sh")
        settings = self.read_settings()
        extra = {"type": "command", "command": "printf another-start"}
        # Sharing an entry with Vibe must not make another hook owned by Vibe.
        settings["hooks"]["SessionStart"][-1]["hooks"].append(extra)
        settings["hooks"]["SessionStart"][-1]["matcher"] = "resume"
        self.write_settings(settings)
        expected = copy.deepcopy(self.settings)
        expected["hooks"]["SessionStart"].append({"hooks": [extra], "matcher": "resume"})
        self.run_script("uninstall.sh")
        self.assertEqual(self.read_settings(), expected)
        self.run_script("uninstall.sh")
        self.assertEqual(self.read_settings(), expected)
        for filename in ("block-force-push.sh", "check-force-push.py"):
            self.assertFalse((self.home / "hooks" / filename).exists())
        for filename in ("session-start.sh", "session-start.py", "project_setup.py", "project-adoption.md", "governance.py", "governance.md"):
            self.assertFalse((self.home / "vibe-tools" / filename).exists())
        self.assertEqual((self.home / "hooks" / "personal.sh").read_text(encoding="utf-8"),
                         "personal hook\n")
        personal = (self.home / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn(self.personal, personal)
        self.assertNotIn("@~/.claude/vibe.md", personal)

    def test_generic_startup_scripts_and_registrations_survive_install_and_removal(self):
        personal_files = {
            self.home / "hooks" / "session-start.sh": "#!/bin/sh\necho personal startup\n",
            self.home / "hooks" / "session-start.py": "print('personal startup helper')\n",
        }
        for path, contents in personal_files.items():
            path.write_text(contents, encoding="utf-8")
        personal_start = shlex.quote(str(self.home / "hooks" / "session-start.sh"))
        personal_helper = shlex.quote(str(self.home / "hooks" / "session-start.py"))
        self.settings["hooks"]["SessionStart"].append({"hooks": [
            {"type": "command", "command": personal_start + " --status-only"},
            {"type": "command", "command": "python3 " + personal_helper},
        ]})
        self.write_settings(self.settings)
        for action in ("install.sh", "install.sh", "uninstall.sh"):
            self.run_script(action)
            for path, contents in personal_files.items():
                self.assertEqual(path.read_text(encoding="utf-8"), contents)
            if action == "install.sh":
                self.assertEqual(self.read_settings()["hooks"]["SessionStart"][:2],
                                 self.settings["hooks"]["SessionStart"])
                self.startup_command()
        self.assertEqual(self.read_settings(), self.settings)

    def test_registered_startup_reads_project_without_duplicating_core(self):
        self.run_script("install.sh")
        project = self.base / "project"
        project.mkdir()

        def git(*args):
            return subprocess.run(["git", "-C", str(project), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()

        git("init", "-b", "main")
        git("-c", "user.name=Vibe Test", "-c", "user.email=test@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "Initial project")
        baseline = git("rev-parse", "HEAD")
        git("update-ref", "refs/remotes/origin/main", baseline)
        git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        command = self.startup_command()
        hook_input = json.dumps({"cwd": str(project), "hook_event_name": "SessionStart"})

        def run_hook():
            return subprocess.run(["bash", "-c", command], cwd=self.base, input=hook_input,
                                  env=self.env, check=True, capture_output=True, text=True)

        self.assertEqual(run_hook().stdout.strip(), "")
        (project / "docs").mkdir()
        (project / "docs" / "STATUS.md").write_text(
            "# Status\n\n## Now\n"
            f"Updated: 2026-11-09 00:00 UTC | {baseline}\n"
            "Position: Delivery ready\n"
            "In progress: none\n"
            "Next task: Continue the approved invitation work\n"
            "Waiting on owner: none\n\n"
            "## History\nOld information must stay out of startup context.\n", encoding="utf-8")
        result = run_hook()
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Continue the approved invitation work", context)
        self.assertNotIn("Old information", context)
        self.assertNotIn("Vibe Delivery Standard", context)
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
