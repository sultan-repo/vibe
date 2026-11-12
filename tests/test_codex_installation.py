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
    def test_project_override_and_fallback_order_in_the_native_prompt(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            profile = base / "profile"
            profile.mkdir()
            env = dict(os.environ, CODEX_HOME=str(profile), PYTHONDONTWRITEBYTECODE="1")

            def prompt(project):
                return subprocess.check_output(
                    [CODEX, "debug", "prompt-input", "-c", 'project_doc_fallback_filenames=["CLAUDE.md","TEAM.md"]',
                     "What are the project rules?"], cwd=project, env=env, stderr=subprocess.PIPE,
                    encoding="utf-8", timeout=60)

            for name, override in (("empty", b""), ("blank", b" \r\n"), ("populated", b"OVERRIDE_OWNER"),
                                   ("claude-fallback", None), ("team-fallback", None)):
                with self.subTest(name=name):
                    project = base / name
                    project.mkdir()
                    subprocess.run(["git", "init", "-q", str(project)], check=True)
                    (project / "TEAM.md").write_text("TEAM_OWNER", encoding="utf-8")
                    if name != "team-fallback":
                        (project / "CLAUDE.md").write_text("CLAUDE_OWNER", encoding="utf-8")
                    if override is not None:
                        (project / "AGENTS.override.md").write_bytes(override)
                    before = prompt(project)
                    adopt = [sys.executable, str(ROOT / "hooks/project_setup.py"), "adopt", "--project-dir", str(project)]
                    subprocess.run(adopt, env=env, capture_output=True, check=True)
                    after = prompt(project)
                    self.assertIn("Vibe project workflow (managed;", after)
                    if override is not None:
                        self.assertTrue((project / "AGENTS.override.md").read_bytes().startswith(override))
                        self.assertNotIn("CLAUDE_OWNER", before)
                        self.assertNotIn("OVERRIDE_OWNER", (project / "AGENTS.md").read_text())
                        if name == "populated":
                            self.assertIn("OVERRIDE_OWNER", after)
                    else:
                        owner = "TEAM_OWNER" if name == "team-fallback" else "CLAUDE_OWNER"
                        self.assertIn(owner, before)
                        self.assertIn("project_doc_fallback_filenames", after)
                        self.assertEqual("bridge created by this adoption" in after, name == "team-fallback")
                        self.assertFalse((project / "AGENTS.override.md").exists())
                    repeat = subprocess.check_output(adopt, env=env, encoding="utf-8")
                    self.assertIn("already current", repeat)

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
