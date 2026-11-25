"""Tests for the shipped plugin (the folder plugin/). No model calls; runs in about 15 seconds,
most of it in the two tests that give the status reader a slow or stuck git.
Run:  python3 -B -m unittest discover -s tests -p 'test_plugin.py' -v
BudgetsAndLayout checks sizes, files and version. StatusReader runs the status hook the way
Claude Code does (the registered command, hook JSON on stdin) inside throwaway projects.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
RULES = PLUGIN / "rules.md"
NOTE = "docs/STATUS.md"
SH = shutil.which("sh") or "/bin/sh"
GIT = shutil.which("git")
CAP = 10000  # Claude Code replaces a longer hook string with a 2,000-character preview
FILES = {".claude-plugin/plugin.json", "rules.md", "hooks/hooks.json", "hooks/status.py", "hooks/run.sh", "hooks/keep.txt"}
MARKED = "# Rules\n<!-- vibe:project:start -->\nold text\n<!-- vibe:project:end -->\n"
OLD_NOTE = ("# Project status\n\n## Now\n- **Updated:** 2026-05-01\n- **Position:** Login page built\n"
            "- **In progress:** Password reset\n- **Next task:** %s\n- **Waiting on owner:** nothing\n")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def commands(event):
    registered = load(PLUGIN / "hooks" / "hooks.json")["hooks"]
    return [hook["command"] for entry in registered[event] for hook in entry["hooks"]]


def hook_timeout():
    """Seconds Claude Code gives the status reader before it cancels it."""
    entries = load(PLUGIN / "hooks" / "hooks.json")["hooks"]["SessionStart"]
    return [hook["timeout"] for entry in entries for hook in entry["hooks"] if "status.py" in hook["command"]][0]


def note(done=1, goal="Customers can book a table", nxt="Add the booking form"):
    """A status note as rules.md asks for it, plus an older section that must not be counted."""
    steps = ["Booking page", "Booking form", "Email confirmation"]
    boxes = ["- [%s] %s" % ("x" if i < done else " ", step) for i, step in enumerate(steps)]
    return ("# Status\n\n## Now\nGoal: %s\nSteps:\n%s\nNext: %s\nWaiting on owner: nothing\n"
            "\n## Earlier\n- [x] An older plan\n" % (goal, "\n".join(boxes), nxt))


class Project(unittest.TestCase):
    """A throwaway project folder (self.dir) with helpers to use git and run the hooks in it."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vibe-test-")).resolve()
        self.addCleanup(shutil.rmtree, str(self.tmp), True)
        self.dir = self.tmp / "project"
        self.dir.mkdir()
        self.clock = int(time.time()) - 86400
        self.env = {  # empty HOME: no personal git settings; ceiling: no git repository above
            "PATH": os.environ.get("PATH", os.defpath), "HOME": str(self.tmp), "CLAUDE_PLUGIN_ROOT": str(PLUGIN),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CEILING_DIRECTORIES": str(self.tmp), "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}

    def git(self, *args):
        self.clock += 60  # each commit is a minute newer than the one before
        stamp = "%d +0000" % self.clock
        env = dict(self.env, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        r = subprocess.run(("git",) + args, cwd=str(self.dir), env=env, capture_output=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def write(self, name, text):
        (self.dir / name).parent.mkdir(parents=True, exist_ok=True)
        (self.dir / name).write_bytes(text.encode("utf-8"))

    def commit(self, name, text):
        self.write(name, text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "save " + name)

    def repo(self, status_note=None):
        """Make the project a git repository on branch main, optionally with a committed note."""
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/main")
        self.commit("app.txt", "one\n")
        if status_note is not None:
            self.commit(NOTE, status_note)

    def branch_with_note(self, name, status_note):
        self.git("checkout", "-q", "-b", name)
        self.commit(NOTE, status_note)
        self.git("checkout", "-q", "main")

    def fake(self, program, script):
        """Put a shell script with a program's name first on PATH. Returns that PATH."""
        folder = Path(tempfile.mkdtemp(dir=str(self.tmp)))
        (folder / program).write_text("#!/bin/sh\n" + script)
        (folder / program).chmod(0o755)
        return str(folder) + os.pathsep + self.env["PATH"]

    def run_hook(self, command=None, source="startup", cwd=None, path=None, run_from=None, stdin=None):
        """Run a hook command (default: the status reader). Returns (exit code, stdout, stderr).
        cwd is the folder named in the hook input; the command itself runs in run_from (default: the same)."""
        command = command or commands("SessionStart")[-1]
        cwd = str(cwd or self.dir)
        if stdin is None:
            stdin = json.dumps({"hook_event_name": "SessionStart", "source": source, "cwd": cwd})
        env = dict(self.env, PATH=path or self.env["PATH"])
        r = subprocess.run([SH, "-c", command], input=stdin, cwd=str(run_from or cwd), env=env,
                           capture_output=True, encoding="utf-8", timeout=30)
        return r.returncode, r.stdout, r.stderr

    def status(self, **how):
        """Run the status reader. Returns (context for Claude, banner for the owner or None)."""
        code, out, err = self.run_hook(**how)
        self.assertEqual((code, err), (0, ""))
        data = json.loads(out) if out.strip() else {}
        return data.get("hookSpecificOutput", {}).get("additionalContext", ""), data.get("systemMessage")


class BudgetsAndLayout(Project):
    def test_rules_fit_their_budget(self):
        size = len(RULES.read_text(encoding="utf-8"))
        self.assertLessEqual(size, 3800, "rules.md is over its budget: an addition needs a deletion")

    def test_session_start_output_fits_the_cap_in_a_worst_case_project(self):
        nasty = 20 * ('"quoted" \'single\' back\\slash\ttab \x01\x1b control '
                      '\u0645\u0631\u062d\u0628\u0627 \u65e5\u672c\u8a9e caf\u00e9 ')
        lines = ["## Now"] + ["%s: %s" % (k, nasty) for k in ("Goal", "Next", "Waiting on owner")]
        lines += ["- [ ] step %d %s" % (i, nasty) for i in range(200)]
        self.repo("\n".join(line[:500] for line in lines) + "\n")
        for name in ("CLAUDE.md", "AGENTS.md", "app.txt"):
            self.write(name, MARKED)
        for command in commands("SessionStart"):
            code, out, err = self.run_hook(command)
            self.assertTrue(code == 0 and out.strip() and not err, "failed or printed nothing: " + command)
            strings = [out]  # plain output is measured whole, JSON output one field at a time
            if "status.py" in command:
                data = json.loads(out)
                strings = [data["hookSpecificOutput"]["additionalContext"], data["systemMessage"]]
                self.assertIn("of 200", strings[0])  # steps are counted before the note is cut
            for text in strings:
                self.assertLessEqual(len(text), CAP, "longer than Claude Code delivers: " + command)

    def test_keep_list_is_one_short_line(self):
        text = (PLUGIN / "hooks" / "keep.txt").read_text(encoding="utf-8")
        self.assertEqual(len(text.strip().splitlines()), 1)
        self.assertLessEqual(len(text), 400)

    def test_plugin_folder_holds_exactly_the_expected_files(self):
        found = {p.relative_to(PLUGIN).as_posix() for p in PLUGIN.rglob("*") if p.is_file()}
        self.assertEqual(found - {".DS_Store"}, FILES, "a new component needs an eval case first")
        for folder in ("skills", "agents", "output-styles"):
            self.assertFalse((PLUGIN / folder).exists(), "a new component needs an eval case first")

    def test_hooks_file_registers_only_what_ships(self):
        registered = load(PLUGIN / "hooks" / "hooks.json")["hooks"]
        self.assertEqual(set(registered), {"SessionStart", "PreCompact"})
        for entry in registered["SessionStart"]:  # no "resume": nothing is added again on resume
            self.assertEqual(entry.get("matcher"), "startup|clear|compact")
        self.assertEqual(hook_timeout(), 10)  # the reader's own limit for git (6 seconds) must stay well below it
        self.assertNotIn("matcher", registered["PreCompact"][0])  # compaction asked for by hand or automatically
        for command in commands("SessionStart") + commands("PreCompact"):
            names = re.findall(r"[\w./-]+\.(?:py|sh|md|txt)\b", command)  # /hooks/run.sh, status.py, ...
            self.assertTrue(names, "no plugin file in: " + command)
            for name in names:  # a bare name is a script that sits beside run.sh
                path = PLUGIN / name[1:] if name.startswith("/") else PLUGIN / "hooks" / name
                self.assertTrue(path.is_file(), "%s is missing, used by: %s" % (path, command))

    def test_precompact_command_prints_the_keep_list(self):
        keep = (PLUGIN / "hooks" / "keep.txt").read_text(encoding="utf-8")
        self.assertEqual([self.run_hook(c)[1] for c in commands("PreCompact")], [keep])

    def test_hooks_work_from_a_plugin_path_with_a_space(self):
        copy = self.tmp / "my plugins" / "vibe"
        shutil.copytree(str(PLUGIN), str(copy))
        self.env["CLAUDE_PLUGIN_ROOT"] = str(copy)
        self.write(NOTE, note())
        rules, status = [self.run_hook(c) for c in commands("SessionStart")]
        self.assertEqual(rules, (0, RULES.read_text(encoding="utf-8"), ""))
        self.assertIn("Customers can book a table", status[1])

    def test_plugin_and_marketplace_use_the_same_name(self):
        entries = load(ROOT / ".claude-plugin" / "marketplace.json")["plugins"]
        self.assertEqual([e["name"] for e in entries], [load(PLUGIN / ".claude-plugin" / "plugin.json")["name"]])
        self.assertEqual(entries[0]["name"], "vibe")  # "claude plugin update vibe@vibe" depends on it

    def test_rules_do_not_point_at_plugin_files(self):
        text = RULES.read_text(encoding="utf-8")  # Claude may not read files in the plugin folder
        for name in sorted({Path(f).name for f in FILES} | {"CLAUDE_PLUGIN_ROOT", "hooks/"}):
            self.assertNotIn(name, text)

    def test_version_lives_in_plugin_json_only(self):
        version = load(PLUGIN / ".claude-plugin" / "plugin.json")["version"]
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")  # the publisher accepts nothing else
        market = ROOT / ".claude-plugin" / "marketplace.json"
        self.assertEqual([p["source"] for p in load(market)["plugins"]], ["./plugin"])
        self.assertNotIn('"version"', market.read_text(encoding="utf-8"))

    def test_newest_heading_in_changes_matches_the_version(self):
        changes = ROOT / "CHANGES.md"
        text = changes.read_text(encoding="utf-8") if changes.is_file() else ""
        headings = re.findall(r"(?m)^#+[^\n]*?(\d+\.\d+\.\d+)", text)
        if not headings:
            self.skipTest("CHANGES.md has no version heading yet")
        self.assertEqual(headings[0], load(PLUGIN / ".claude-plugin" / "plugin.json")["version"])


class StatusReader(Project):
    def test_no_note_prints_nothing(self):
        self.repo()
        self.assertEqual(self.run_hook(), (0, "", ""))
        self.write("app.txt", "changed, not committed\n")
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_removed_note_prints_nothing(self):
        self.repo(note())
        self.git("rm", "-q", NOTE)
        self.git("commit", "-q", "-m", "remove the note")
        self.commit("app.txt", "two\n")
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_committed_note_with_open_steps(self):
        self.repo(note())
        context, banner = self.status()
        for line in ("Goal: Customers can book a table", "- [x] Booking page", "- [ ] Booking form",
                     "Next: Add the booking form", "done 1 of 3"):
            self.assertIn(line, context)
        self.assertNotIn("commits", context)
        self.assertRegex(context.splitlines()[0], r"saved .+ ago")
        self.assertNotIn("read the file", context)  # nothing was cut
        self.assertEqual(banner, "Where things stand: Customers can book a table | Done 1 of 3 | Next: Add the booking form")

    def test_commits_after_the_note_are_mentioned(self):
        self.repo(note())
        self.commit("app.txt", "two\n")
        self.assertIn("1 commit was made after", self.status()[0])
        self.commit("app.txt", "three\n")
        self.assertIn("2 commits were made after", self.status()[0])

    def test_note_on_another_newer_branch_is_shown_with_its_branch(self):
        self.repo()
        self.branch_with_note("booking", note())
        clone = self.tmp / "clone"  # a fresh clone has that branch only as origin/booking
        self.git("clone", "-q", str(self.dir), str(clone))
        for folder, branch in ((self.dir, "booking"), (clone, "origin/booking")):
            with self.subTest(branch=branch):
                context, banner = self.status(cwd=folder)
                self.assertIn("Goal: Customers can book a table", context)
                self.assertIn("branch %s, saved" % branch, context)
                self.assertIn("this folder is on another branch and has no note", context)

    def test_this_folders_note_wins_over_a_newer_note_on_another_branch(self):
        self.repo(note(goal="Customers can book a table"))
        self.branch_with_note("experiment", note(done=2, goal="Abandoned experiment"))
        context, banner = self.status()
        self.assertIn("Customers can book a table", context)
        self.assertNotIn("Abandoned experiment", context + (banner or ""))

    def test_banner_names_the_branch_when_the_note_comes_from_elsewhere(self):
        self.repo()
        self.branch_with_note("feature/booking", note())
        self.assertIn("Saved on branch feature/booking, not the one open here | Customers", self.status()[1])

    def test_branch_name_is_cleaned_and_cut_wherever_it_is_printed(self):
        self.repo()
        self.branch_with_note("feat/with\u202e\u200fevil/" + "b" * 250, note())  # text-direction characters, and far too long
        context, banner = self.status()
        self.assertNotIn("\u202e", context + banner)
        self.assertNotIn("\u200f", context + banner)
        for text in (context, banner):
            self.assertIn("ranch feat/withevil/%s..." % ("b" * 186), text)
            self.assertNotIn("b" * 187, text)

    def test_future_dated_note_on_another_branch_is_ignored(self):
        self.repo()
        self.clock += 10 * 86400  # a commit dated ten days from now
        self.branch_with_note("odd", note())
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_linked_note_is_not_followed_out_of_the_project(self):
        self.repo()
        outside = self.tmp / "elsewhere" / "STATUS.md"
        outside.parent.mkdir()
        outside.write_text(note(goal="Another project's secret plan"), encoding="utf-8")
        (self.dir / "docs").mkdir()
        os.symlink(str(outside), str(self.dir / NOTE))  # the note itself is a link
        self.assertEqual(self.run_hook(), (0, "", ""))
        shutil.rmtree(str(self.dir / "docs"))
        os.symlink(str(outside.parent), str(self.dir / "docs"))  # the docs folder is a link
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_programs_named_in_the_repository_config_are_not_run(self):
        self.repo(note())
        marker, script = self.tmp / "ran", self.tmp / "program.sh"
        script.write_text("#!/bin/sh\ntouch '%s'\n" % marker)
        script.chmod(0o755)
        self.git("config", "core.fsmonitor", str(script))  # git runs it whenever it looks at the files
        self.git("config", "filter.evil.clean", str(script))  # git runs it to compare a changed file
        (self.dir / ".git" / "info").mkdir(exist_ok=True)
        (self.dir / ".git" / "info" / "attributes").write_text("* filter=evil\n")
        self.write("app.txt", "changed, not committed\n")
        self.write(NOTE, note(done=2))
        self.assertIn("Customers can book a table", self.status()[0])
        self.assertFalse(marker.exists(), "the status reader ran a program from .git/config")
        self.git("status")
        self.assertTrue(marker.exists(), "this test is no test: an ordinary git status did not run the program either")

    def test_partial_clone_is_never_fetched_from(self):
        self.repo()
        self.branch_with_note("feature", note())
        self.git("config", "uploadpack.allowFilter", "true")
        clone = self.tmp / "clone"
        r = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "file://%s" % self.dir, str(clone)],
                           env=self.env, capture_output=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        packs = lambda: sorted(p.name for p in (clone / ".git" / "objects" / "pack").iterdir())
        before = packs()
        unset = self.tmp / "git asked to fetch"
        old_git = self.fake("git", '[ "$GIT_NO_LAZY_FETCH" = 1 ] || touch "%s"\nunset GIT_NO_LAZY_FETCH\nexec "%s" "$@"\n'
                            % (unset, GIT))  # Git before 2.44 does not know the variable that forbids fetching
        setting = lambda *args: subprocess.run((GIT, "-C", str(clone), "config") + args, env=self.env, check=True)
        signs = {"extensions.partialclone": "origin", "remote.origin.promisor": "true",
                 "remote.origin.partialclonefilter": "blob:none"}  # any one of them makes git fetch what is missing
        for kept in [set(signs)] + [{key} for key in signs]:
            with self.subTest(kept=sorted(kept)):
                for key, value in signs.items():
                    setting(key, value)
                for key in set(signs) - kept:
                    setting("--unset", key)
                for path in (None, old_git):  # the note's content is not local: stay silent, fetch nothing
                    self.assertEqual(self.run_hook(cwd=clone, path=path), (0, "", ""))
                    self.assertEqual(packs(), before)
        self.assertFalse(unset.exists(), "a git command was run without GIT_NO_LAZY_FETCH=1")

    def test_committed_note_in_a_treeless_clone_fetches_nothing(self):
        self.repo(note())
        self.commit("app.txt", "later work\n")
        self.git("config", "uploadpack.allowFilter", "true")
        clone = self.tmp / "clone"
        r = subprocess.run(["git", "clone", "-q", "--filter=tree:0", "file://%s" % self.dir, str(clone)],
                           env=self.env, capture_output=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        packs = lambda: sorted(p.name for p in (clone / ".git" / "objects" / "pack").iterdir())
        before = packs()
        old_git = self.fake("git", 'unset GIT_NO_LAZY_FETCH\nexec "%s" "$@"\n' % GIT)  # Git before 2.44
        context, _ = self.status(cwd=clone, path=old_git)
        self.assertIn("Customers can book a table", context)  # the note in the folder is still shown
        self.assertEqual(packs(), before)

    def test_open_question_keeps_a_finished_plan_in_view(self):
        ask = "## Now\nGoal: Email the weekly report\n- [x] Build it\n- [x] Send it\nNext: nothing\n%s"
        for waiting in ("Waiting on owner: No answer yet: Monday or Friday?\n",
                        "Waiting on owner: nothing urgent, but Monday or Friday?\n",
                        "Waiting on owner:\n- Monday or Friday?\n- Which address?\n"):
            self.write(NOTE, ask % waiting)
            context, banner = self.status()
            self.assertIn("Monday or Friday?", context)
            self.assertIn("Waiting on you", banner or "")

    def test_question_written_under_a_label_is_never_hidden(self):
        ask = "## Now\nGoal: Email the weekly report\n- [x] Build it\n- [x] Send it\nNext: nothing\n%s"
        for waiting in ("Waiting on owner:\nMonday or Friday?\n", "Waiting on owner:\n1. Monday or Friday?\n",
                        "Waiting on owner\nMonday or Friday?\n", "  - [ ] Ask: Monday or Friday?\n"):
            with self.subTest(waiting=waiting):
                self.write(NOTE, ask % waiting)
                context, banner = self.status()
                self.assertIn("Monday or Friday?", context)
                self.assertNotIn("finished", context)
                if waiting.startswith("Waiting on owner:"):
                    self.assertIn("Waiting on you: Monday or Friday?", banner or "")

    def test_started_from_a_subfolder(self):
        self.repo(note())
        (self.dir / "src" / "deep").mkdir(parents=True)
        self.assertIn("Done 1 of 3", self.status(cwd=self.dir / "src" / "deep")[1])

    def test_note_in_the_subfolder_the_session_started_in_comes_first(self):
        self.repo(note(goal="Goal at the top"))
        self.commit("shop/" + NOTE, note(done=2, goal="Goal of the shop"))
        self.commit("app.txt", "two\n")
        context, banner = self.status(cwd=self.dir / "shop")
        self.assertIn("Goal of the shop | Done 2 of 3", banner)
        self.assertNotIn("Goal at the top", context)
        self.assertRegex(context.splitlines()[0], r"saved .+ ago")  # compared with its own committed copy
        self.assertIn("1 commit was made after", context)
        self.write("shop/" + NOTE, note(done=3, goal="Goal of the shop"))
        self.assertIn("this folder, not committed yet", self.status(cwd=self.dir / "shop")[0])

    def test_note_is_read_from_the_folder_named_in_the_hook_input(self):
        self.write(NOTE, note())
        self.assertIn("Done 1 of 3", self.status(run_from=self.tmp)[1])

    def test_note_deleted_here_but_not_committed_stays_silent(self):
        self.repo(note())  # the newest saved note is in this folder's own history: not "another branch"
        (self.dir / NOTE).unlink()
        self.assertEqual(self.run_hook(), (0, "", ""))
        self.git("rm", "-q", NOTE)
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_bad_input_is_harmless(self):
        self.repo()
        (self.dir / "docs").mkdir()
        (self.dir / NOTE).write_bytes(b"## Now\nGoal: caf\xe9 \xff\xfe menu\n- [ ] step\x1b[2J one\n")
        context, banner = self.status()
        self.assertIn("Goal: caf", context)
        self.assertNotIn("\x1b", context + banner)  # control characters never reach the terminal
        self.assertIn("Goal: caf", self.status(stdin="")[0])  # no hook input at all: the note is still shown
        reader = [sys.executable, "-B", str(PLUGIN / "hooks" / "status.py")]  # without run.sh, which hides errors
        for stdin in ("", "not JSON", "[1, 2]", '{"cwd": 5}', '{"cwd": "/no/such/folder"}'):
            with self.subTest(stdin=stdin):
                r = subprocess.run(reader, input=stdin, cwd=str(self.dir), env=self.env,
                                   capture_output=True, encoding="utf-8", timeout=30)
                self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_stuck_git_cannot_hang_the_session(self):
        self.repo(note())
        path = self.fake("git", 'case " $* " in *" rev-parse "*) exec "%s" "$@";; esac\nsleep 30\n' % GIT)
        started = time.time()
        context, _ = self.status(path=path)
        elapsed = time.time() - started
        self.assertIn("Customers can book a table", context)
        self.assertLess(elapsed, hook_timeout())
        self.assertLess(elapsed, 5)  # one stuck call is given up after 2 seconds, not after the time meant for all

    def test_two_stuck_git_calls_are_each_given_up_after_two_seconds(self):
        self.repo()
        self.branch_with_note("booking", note())  # rev-parse answers; the next two calls hang
        path = self.fake("git", 'case " $* " in *" rev-parse "*) exec "%s" "$@";; esac\nsleep 30\n' % GIT)
        started = time.time()
        self.assertEqual(self.run_hook(path=path), (0, "", ""))
        self.assertLess(time.time() - started, 5.5)

    def test_a_git_call_that_runs_out_of_time_is_not_an_answer(self):
        hang = 'case " $* " in *" %s "*) sleep 30;; esac\nexec "%s" "$@"\n'
        self.repo(note())  # the last commit saved the note
        (self.dir / NOTE).unlink()  # removed here, not yet committed: there is nothing to show
        self.assertEqual(self.run_hook(path=self.fake("git", hang % ("merge-base", GIT))), (0, "", ""))
        self.git("checkout", "-q", "--", NOTE)
        context, _ = self.status(path=self.fake("git", hang % ("show", GIT)))
        self.assertNotIn("not committed", context)  # no answer about the saved copy is not a difference from it

    def test_label_variants_reach_the_owner(self):
        self.write(NOTE, "## Now\nGoal: g\n- [ ] a\nNext step: a\nWaiting on you: choose a colour\n")
        self.assertIn("Next: a | Waiting on you: choose a colour", self.status()[1])

    def test_slow_git_is_given_up_with_time_to_spare(self):
        self.repo()
        self.branch_with_note("booking", note())  # the case with the most git calls, each just inside its own limit
        path = self.fake("git", 'case " $* " in *" rev-parse "*) ;; *) sleep 1.9;; esac\nexec "%s" "$@"\n' % GIT)
        started = time.time()
        self.assertEqual(self.run_hook(path=path), (0, "", ""))
        self.assertLess(time.time() - started, hook_timeout() - 2)  # two seconds left for a slow computer to start

    def test_note_on_an_older_abandoned_branch_is_not_shown(self):
        self.repo()
        self.branch_with_note("abandoned", note())
        self.commit("app.txt", "newer work on main\n")
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_uncommitted_note_here_wins_over_a_committed_note_elsewhere(self):
        self.repo()
        self.branch_with_note("other", note(goal="Goal from the other branch"))
        self.write(NOTE, note(goal="Goal from this folder"))
        context, banner = self.status()
        self.assertIn("this folder, not committed yet", context)
        self.assertIn("Goal from this folder", context)
        self.assertNotIn("Goal from the other branch", context + banner)

    def test_stash_touching_the_note_is_not_a_branch(self):
        self.repo()
        self.write(NOTE, note())
        self.git("add", "-A")
        self.git("stash", "-q")
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_folder_that_is_not_a_git_repository(self):
        self.write(NOTE, note())
        context, banner = self.status()
        self.assertIn("Goal: Customers can book a table", context)
        self.assertIn("done 1 of 3", context)
        self.assertIn("Done 1 of 3", banner)

    def test_old_4x_note_is_shown_as_written_and_never_called_finished(self):
        for next_task in ("Add the email check", "none"):
            with self.subTest(next_task=next_task):
                self.write(NOTE, OLD_NOTE % next_task)
                context, banner = self.status()
                for line in (OLD_NOTE % next_task).splitlines()[3:]:
                    self.assertIn(line, context)
                self.assertNotIn("finished", (context + (banner or "")).lower())

    def test_numbered_checkboxes_are_counted(self):
        self.write(NOTE, "## Now\nGoal: Ship the shop\n1. [x] Cart\n2. [ ] Checkout\n3. [ ] Receipts\n")
        self.assertIn("done 1 of 3", self.status()[0])

    def test_note_without_a_now_heading_is_still_read(self):
        self.write(NOTE, "# Status\n\nGoal: Ship the shop\n- [x] Cart\n- [ ] Checkout\n")
        context, banner = self.status()
        self.assertIn("Goal: Ship the shop", context)
        self.assertIn("done 1 of 2", context)

    def test_finished_plan_is_one_quiet_line(self):
        for nxt in ("nothing", "Nothing, ready to use", "nothing; all steps done, not yet committed", "None.", "N/A"):
            with self.subTest(nxt=nxt):
                self.write(NOTE, note(done=3, nxt=nxt))
                context, banner = self.status()
                self.assertIsNone(banner)
                self.assertEqual(context.splitlines()[1:], [
                    "The last plan in the note is finished: Customers can book a table",
                    "Counted from the note: done 3 of 3 steps."])

    def test_whatever_is_cut_is_marked(self):
        long = "word " * 60
        steps = "".join("- [ ] step %d\n" % i for i in range(36))
        self.write(NOTE, "## Now\nGoal: %s\n%sNext: %s\nWaiting on owner: %s\n" % (long, steps, long, long))
        context, banner = self.status()
        lines = context.splitlines()
        self.assertEqual(lines[1], ("Goal: " + long)[:200] + " [cut: read the file]")
        self.assertEqual(lines[30:32], ["- [ ] step 28", "[9 more lines: read the file]"])
        self.assertIn(("Next: " + long)[:200] + "... | Waiting on you: ", banner)
        self.assertEqual((len(banner), banner[600:]), (603, "..."))

    def test_sub_headings_belong_to_the_block_and_larger_headings_end_it(self):
        block = "## Now\n### Goal\nShip the shop\n### Steps\n- [x] Cart\n- [ ] Checkout\n"
        for after in ("## Earlier\n- [x] An older plan\n", "# Another title\n- [x] An older plan\n"):
            with self.subTest(after=after):
                self.write(NOTE, block + after)
                context, banner = self.status()
                self.assertIn("Ship the shop", context)
                self.assertIn("done 1 of 2", context)
                self.assertNotIn("An older plan", context)

    def test_sub_steps_under_a_step_are_not_counted(self):
        for steps in ("- [x] one\n  - [x] sub a\n  - [ ] sub b\n- [ ] two\n    - [ ] sub c\n",
                      "- **Steps:**\n  - [x] one\n  - [ ] two\n"):
            with self.subTest(steps=steps):
                self.write(NOTE, "## Now\nGoal: Ship the shop\n%sNext: two\n" % steps)
                context, banner = self.status()
                self.assertIn("done 1 of 2", context)
                self.assertIn("Done 1 of 2", banner)

    def test_note_saved_with_a_byte_order_mark_is_not_called_uncommitted(self):
        self.repo("\ufeff" + note())  # written by some Windows editors
        context, banner = self.status()
        self.assertRegex(context.splitlines()[0], r"saved .+ ago")
        self.assertIn("Done 1 of 3", banner)

    def test_after_compaction_there_is_no_banner(self):
        self.repo(note())
        context, banner = self.status(source="compact")
        self.assertIn("Goal: Customers can book a table", context)
        self.assertIsNone(banner)

    def test_leftover_vibe_4_block_is_mentioned_once(self):
        self.repo()
        for name in ("CLAUDE.md", "AGENTS.md"):
            with self.subTest(file=name):
                self.write(name, MARKED)
                context, banner = self.status()
                self.assertEqual(sum(name in line for line in context.splitlines()), 1, context)
                self.assertIsNone(banner)
                (self.dir / name).unlink()

    def test_leftover_vibe_4_block_is_found_in_the_start_folder_and_at_the_top(self):
        self.repo()
        self.write("CLAUDE.md", MARKED)
        self.write("shop/AGENTS.md", MARKED)
        context, banner = self.status(cwd=self.dir / "shop")
        self.assertEqual(len(context.splitlines()), 2, context)
        self.assertIn("AGENTS.md still holds a Vibe 4", context)
        self.assertIn("CLAUDE.md at the top of the repository still holds a Vibe 4", context)

    def test_reader_changes_nothing_in_the_project(self):
        self.repo(note())
        self.branch_with_note("other", note(done=2))
        self.write("app.txt", "changed, not committed\n")
        inside = lambda: {str(p): p.read_bytes() for p in (self.dir / ".git").rglob("*") if p.is_file()}
        porcelain = self.git("status", "--porcelain")
        os.utime(str(self.dir / NOTE), (1, 1))  # looks touched: an ordinary "git status" would now rewrite .git/index
        before = inside()
        self.assertTrue(self.status()[0])
        after = inside()
        self.assertEqual(sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)), [])
        self.assertEqual(self.git("status", "--porcelain"), porcelain)

    def test_reader_needs_no_lock_on_the_git_index(self):
        self.repo(note())
        (self.dir / ".git" / "index.lock").write_text("")
        started = time.time()
        self.assertIn("Goal: Customers can book a table", self.status()[0])
        self.assertLess(time.time() - started, 5)

    def test_without_python3_the_hook_is_silent(self):
        self.repo(note())
        tools = self.tmp / "bin"  # a PATH with everything the hook command uses except python3
        tools.mkdir()
        for tool in ("sh", "uname", "dirname", "git"):
            if shutil.which(tool):
                os.symlink(shutil.which(tool), str(tools / tool))
        self.assertEqual(self.run_hook(path=str(tools)), (0, "", ""))

    def test_with_a_broken_python3_the_hook_is_silent(self):
        self.repo(note())
        broken = self.fake("python3", "echo 'python3 is broken' >&2\nexit 1\n")
        self.assertEqual(self.run_hook(path=broken), (0, "", ""))
