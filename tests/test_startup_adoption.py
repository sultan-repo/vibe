"""Startup keeps core/continuity independent of optional gate advisory failures."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StartupAdoptionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name)
        self.project = self.area / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.core = self.area / "core.md"
        self.core.write_text("# Core remains loaded\n")
        self.hooks = self.area / "hooks"
        self.hooks.mkdir()
        for name in ("session-start.py", "project_setup.py"):
            shutil.copyfile(ROOT / "hooks" / name, self.hooks / name)

    def start(self, status_only=False):
        result = subprocess.run([sys.executable, str(self.hooks / "session-start.py"),
                                 "--core", str(self.core), *(["--status-only"] if status_only else [])],
                                input=json.dumps({"cwd": str(self.project)}), text=True,
                                capture_output=True, timeout=6, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        if not result.stdout.strip():
            return ""
        return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_startup_loads_core_without_writing_project_policy(self):
        self.assertEqual(self.start(), self.core.read_text())
        self.assertFalse((self.project / "CLAUDE.md").exists())
        self.assertEqual(self.start(status_only=True), "")

    def test_notice_is_once_per_configuration_with_core_preserved(self):
        hook = self.project / ".git/hooks/pre-push"
        hook.write_text("#!/bin/sh\nnpx playwright test\ntouch DO_NOT_CREATE\n")
        hook.chmod(0o755)
        first = self.start()
        self.assertIn(self.core.read_text(), first)
        self.assertIn("may run broad verification", first)
        self.assertFalse((self.project / "DO_NOT_CREATE").exists())
        self.assertNotIn("Vibe gate advisory:", self.start())
        hook.write_text("#!/bin/sh\nnpx playwright test --workers=1\n")
        self.assertIn("may run broad verification", self.start())

    def test_missing_optional_helper_cannot_suppress_core_or_continuity(self):
        (self.hooks / "project_setup.py").unlink()
        (self.project / "docs").mkdir()
        (self.project / "docs/STATUS.md").write_text(
            "## Now\nUpdated: today\nPosition: Work saved\nIn progress: Example\n"
            "Next task: Continue the saved work\nWaiting on owner: none\n")
        context = self.start()
        self.assertIn(self.core.read_text(), context)
        self.assertIn("Continue the saved work", context)
        self.assertIn("inspection unavailable", context)

    def test_advisory_runtime_failure_cannot_suppress_core(self):
        (self.hooks / "project_setup.py").write_text(
            "def inspect_project(git):\n    raise RuntimeError('private diagnostic')\n")
        context = self.start()
        self.assertIn(self.core.read_text(), context)
        self.assertIn("inspection unavailable", context)
        self.assertNotIn("private diagnostic", context)

    def test_board_removed_and_native_tracking_remains(self):
        data = json.loads((ROOT / "hooks/hooks.json").read_text())
        self.assertNotIn("modules", data)
        for path in ("hooks/board.mjs", "hooks/board.test.ts", "tests/mod-board.test.mjs"):
            self.assertFalse((ROOT / path).exists())
        core = (ROOT / "core/CLAUDE.md").read_text()
        build = (ROOT / "skills/build/SKILL.md").read_text()
        self.assertIn("native task tracking", build.lower())
        self.assertNotIn("mcp__vibe__progress", build)
        self.assertIn("Automatic project adoption", core)
        self.assertIn("user-invocable: false", build)


if __name__ == "__main__":
    unittest.main()
