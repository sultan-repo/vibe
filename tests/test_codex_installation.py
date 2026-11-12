"""Exercise real Codex instruction loading in disposable projects, without model calls."""
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
            names = ["CLAUDE.md", "TEAM.md"]

            def prompt(project, fallbacks):
                return subprocess.check_output(
                    [CODEX, "debug", "prompt-input", "-c",
                     "project_doc_fallback_filenames=" + json.dumps(fallbacks),
                     "What are the project rules?"], cwd=project, env=env, stderr=subprocess.PIPE,
                    encoding="utf-8", timeout=60)

            cases = (("empty", b"", names), ("blank", b" \r\n", names),
                     ("populated", b"OVERRIDE_OWNER", names), ("claude-fallback", None, names),
                     ("team-fallback", None, names), ("team-first", None, list(reversed(names))),
                     ("empty-fallback", None, names))
            for name, override, fallbacks in cases:
                with self.subTest(name=name):
                    project = base / name
                    project.mkdir()
                    subprocess.run(["git", "init", "-q", str(project)], check=True)
                    (project / "TEAM.md").write_text("TEAM_OWNER", encoding="utf-8")
                    if name != "team-fallback":
                        (project / "CLAUDE.md").write_text(
                            "" if name == "empty-fallback" else "CLAUDE_OWNER", encoding="utf-8")
                    if override is not None:
                        (project / "AGENTS.override.md").write_bytes(override)
                    before = prompt(project, fallbacks)
                    adopt = [sys.executable, str(ROOT / "hooks/project_setup.py"), "adopt",
                             "--project-dir", str(project), "--codex-fallbacks-json", json.dumps(fallbacks)]
                    subprocess.run(adopt, env=env, capture_output=True, check=True)
                    after = prompt(project, fallbacks)
                    self.assertIn("Vibe project workflow (managed;", after)
                    if override is not None:
                        self.assertTrue((project / "AGENTS.override.md").read_bytes().startswith(override))
                        self.assertNotIn("CLAUDE_OWNER", before)
                        self.assertNotIn("CLAUDE_OWNER", after)
                        self.assertNotIn("TEAM_OWNER", after)
                        self.assertNotIn("OVERRIDE_OWNER", (project / "AGENTS.md").read_text())
                        if name == "populated":
                            self.assertIn("OVERRIDE_OWNER", after)
                    else:
                        # Preserve native selection, not just a reminder to rediscover owner text.
                        for owner in ("TEAM_OWNER", "CLAUDE_OWNER"):
                            self.assertEqual(owner in before, owner in after)
                        self.assertFalse((project / "AGENTS.md").exists())
                        self.assertFalse((project / "AGENTS.override.md").exists())
                        active = project / ("TEAM.md" if name in ("team-fallback", "team-first") else "CLAUDE.md")
                        with active.open("a", encoding="utf-8") as stream:
                            stream.write("\nOWNER_RULE_ADDED_LATER\n")
                        self.assertIn("OWNER_RULE_ADDED_LATER", prompt(project, fallbacks))
                        if name == "team-fallback":
                            self.assertFalse((project / "CLAUDE.md").exists())
                    repeat = subprocess.check_output(adopt, env=env, encoding="utf-8")
                    self.assertIn("already current", repeat)

    def test_legacy_repair_restores_native_owner_loading_and_keeps_new_owner_edits(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            profile = base / "profile"
            profile.mkdir()
            env = dict(os.environ, CODEX_HOME=str(profile), PYTHONDONTWRITEBYTECODE="1")
            fallbacks = ["CLAUDE.md", "TEAM.md"]
            for new_owner in (False, True):
                with self.subTest(owner_added_to_old_bridge=new_owner):
                    project = base / str(new_owner)
                    project.mkdir()
                    subprocess.run(["git", "init", "-q", str(project)], check=True)
                    (project / "TEAM.md").write_text("ORIGINAL_TEAM_OWNER\n")
                    (project / "AGENTS.md").write_text(
                        "<!-- vibe:project:start -->\n## Vibe project workflow (managed; v4.12)\n"
                        "In Codex, retain the owner instructions from your configured project fallback. "
                        "Ignore the root CLAUDE.md bridge created by this adoption when locating the previous fallback.\n"
                        "<!-- vibe:project:end -->\n")
                    (project / "CLAUDE.md").write_text(
                        "<!-- vibe:project:start -->\n@AGENTS.md\n<!-- vibe:project:end -->\n" +
                        ("NEW_CLAUDE_OWNER\n" if new_owner else ""))
                    subprocess.run([sys.executable, str(ROOT / "hooks/project_setup.py"), "adopt",
                                    "--project-dir", str(project), "--codex-fallbacks-json", json.dumps(fallbacks)],
                                   env=env, capture_output=True, check=True)
                    after = subprocess.check_output(
                        [CODEX, "debug", "prompt-input", "-c",
                         "project_doc_fallback_filenames=" + json.dumps(fallbacks), "What are the rules?"],
                        cwd=project, env=env, stderr=subprocess.PIPE, encoding="utf-8", timeout=60)
                    self.assertIn("NEW_CLAUDE_OWNER" if new_owner else "ORIGINAL_TEAM_OWNER", after)
                    self.assertNotIn("Ignore the root CLAUDE.md bridge", after)
                    self.assertIn("Vibe project workflow (managed;", after)
                    self.assertFalse((project / "AGENTS.md").exists())

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

            # Preserve a native installation's lifecycle and unrelated profile rules.
            run(CODEX, "plugin", "marketplace", "add", str(ROOT))
            run(CODEX, "plugin", "add", "vibe@vibe")
            run(*installer)
            self.assertFalse((profile / "vibe-local").exists())
            self.assertIn("apply Vibe to ordinary software requests", run(CODEX, "debug", "prompt-input", "Help me plan"))
            run(*installer, "--uninstall")
            self.assertEqual(rule.read_bytes(), original)
            native = json.loads(run(CODEX, "plugin", "list", "--marketplace", "vibe", "--json"))
            self.assertTrue(native["installed"][0]["enabled"])
