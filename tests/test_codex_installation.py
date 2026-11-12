"""Exercise a real Codex first prompt in an empty project, without model calls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CODEX = shutil.which("codex.cmd" if os.name == "nt" else "codex")


@unittest.skipUnless(CODEX, "requires Codex CLI")
class CodexInstallationTest(unittest.TestCase):
    def test_first_prompt_reinstall_and_removal_with_owner_rules(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            profile, project = base / "codex profile", base / "user project"
            profile.mkdir()
            project.mkdir()
            rule = profile / "AGENTS.override.md"
            original = b"Personal rules\r\n"
            rule.write_bytes(original)
            env = dict(os.environ, CODEX_HOME=str(profile), PYTHONDONTWRITEBYTECODE="1")

            def run(*args):
                result = subprocess.run(args, env=env, cwd=project, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, encoding="utf-8", timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout

            installer = (sys.executable, str(ROOT / "install-codex.py"))
            run(*installer)
            first = rule.read_bytes()
            run(*installer)
            self.assertEqual(rule.read_bytes(), first)
            self.assertTrue(first.endswith(original))
            self.assertFalse((profile / "AGENTS.md").exists())
            installed = json.loads(run(CODEX, "plugin", "list", "--marketplace", "vibe-local", "--json"))
            self.assertTrue(installed["installed"][0]["enabled"])
            prompt = run(CODEX, "debug", "prompt-input", "Fix the login error.")
            self.assertIn("apply Vibe to ordinary software requests", prompt)
            for skill in ("discover", "build", "reassess"):
                self.assertIn(f"vibe:{skill}:", prompt)
            self.assertNotIn("vibe:effort-low:", prompt)
            self.assertEqual(list(project.iterdir()), [])
            run(*installer, "--uninstall")
            run(*installer, "--uninstall")
            self.assertEqual(rule.read_bytes(), original)
            self.assertFalse((profile / "vibe-local").exists())
            self.assertNotIn("vibe:build:", run(CODEX, "debug", "prompt-input", "Fix the login error."))

            # A native marketplace installation already has the skills. Add the
            # startup instruction without registering a second plugin or taking
            # ownership of the installation on removal.
            run(CODEX, "plugin", "marketplace", "add", str(ROOT))
            run(CODEX, "plugin", "add", "vibe@vibe")
            run(*installer)
            self.assertFalse((profile / "vibe-local").exists())
            self.assertIn("apply Vibe to ordinary software requests", run(CODEX, "debug", "prompt-input", "Help me plan"))
            run(*installer, "--uninstall")
            self.assertEqual(rule.read_bytes(), original)
            native = json.loads(run(CODEX, "plugin", "list", "--marketplace", "vibe", "--json"))
            self.assertTrue(native["installed"][0]["enabled"])
