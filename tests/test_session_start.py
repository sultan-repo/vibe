"""Exercise startup continuity against real local repositories and fresh clones."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/session-start.sh"
CORE = ROOT / "core/CLAUDE.md"


class SessionStartTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="vibe-session-test-")
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name)
        self.repo = self.area / "project"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Continuity test")
        self.git("config", "user.email", "continuity@example.invalid")
        (self.repo / "source.txt").write_text("working baseline\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Initial source")
        self.baseline = self.oid()
        self.sync_default()

    def git(self, *args, cwd=None, check=True):
        return subprocess.run(["git", *args], cwd=cwd or self.repo, text=True,
                              capture_output=True, check=check)

    def oid(self, ref="HEAD"):
        return self.git("rev-parse", ref).stdout.strip()

    def sync_default(self):
        self.git("update-ref", "refs/remotes/origin/main", self.oid("main"))
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")

    def status(self, *, baseline=None, progress="none", extra="", history="Old private detail"):
        path = self.repo / "docs/STATUS.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text("# Status\n\n## Now\n"
                        f"Updated: 2026-11-09 00:00 UTC | {baseline or self.baseline}\n"
                        "Position: Family import in progress\n"
                        f"In progress: {progress}\n"
                        "Next task: Finish validating duplicate relatives before importing.\n"
                        "Waiting on owner: none\n" + extra + "\n## History\n" + history + "\n")
        return path

    def commit(self, message="Save checkpoint"):
        self.git("add", ".")
        self.git("commit", "-qm", message)
        self.sync_default()

    def run_hook(self, *, cwd=None, payload=None, status_only=False, env=None):
        cwd = cwd or self.repo
        result = subprocess.run(["bash", str(HOOK), *(["--status-only"] if status_only else [])],
                                cwd=self.area, input=json.dumps(payload if payload is not None else {"cwd": str(cwd)}),
                                text=True, capture_output=True, timeout=6,
                                env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(ROOT), **(env or {})})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        if not result.stdout.strip():
            return ""
        data = json.loads(result.stdout)
        self.assertEqual(data["hookSpecificOutput"]["hookEventName"], "SessionStart")
        context = data["hookSpecificOutput"]["additionalContext"]
        self.assertLessEqual(context.count("Vibe continuity warning:"), 1)
        return context

    def feature(self, name):
        self.git("checkout", "-qb", name, self.baseline)
        (self.repo / "partial.txt").write_text("preserved partial implementation\n")
        self.git("add", "partial.txt")
        self.git("commit", "-qm", "Save partial work")
        self.git("update-ref", "refs/remotes/origin/" + name, self.oid())
        self.git("checkout", "-q", "main")

    def test_missing_file_preserves_exact_core_and_status_only_is_silent(self):
        self.assertEqual(self.run_hook(), CORE.read_text())
        self.assertEqual(self.run_hook(status_only=True), "")

    def test_current_summary_is_injected_without_history(self):
        self.status()
        context = self.run_hook()
        self.assertTrue(context.startswith(CORE.read_text() + "\n\n"))
        self.assertIn("## Now\nUpdated:", context)
        self.assertIn("Next task: Finish validating", context)
        self.assertNotIn("Old private detail", context)
        self.assertNotIn("Vibe continuity warning:", context)

    def test_status_only_commits_do_not_immediately_mark_summary_stale(self):
        self.status()
        self.commit()
        self.assertNotEqual(self.oid(), self.baseline)
        self.assertNotIn("Vibe continuity warning:", self.run_hook())
        self.status(progress="Import verification on feature/import")
        self.commit("Update active work")
        self.assertNotIn("Vibe continuity warning:", self.run_hook())

    def test_changed_source_is_stale(self):
        self.status()
        self.commit()
        (self.repo / "source.txt").write_text("changed behavior\n")
        self.commit("Change source")
        self.assertIn("behind the last known default branch", self.run_hook())

    def test_other_document_changes_are_not_exempted(self):
        self.status()
        self.commit()
        (self.repo / "docs/DECISIONS.md").write_text("A changed project decision\n")
        self.commit("Change a decision")
        self.assertIn("behind the last known default branch", self.run_hook())

    def test_unmentioned_unmerged_branch_warns_but_exact_mention_clears_it(self):
        self.feature("feature/import")
        self.status(progress="Review feature/import-other")
        context = self.run_hook()
        self.assertIn("locally known unmerged branches not in Now", context)
        self.assertIn("feature/import", context)
        self.status(progress="Import: `origin/feature/import`")
        self.assertNotIn("Vibe continuity warning:", self.run_hook())

    def test_history_mention_does_not_hide_unrecorded_active_branch(self):
        self.feature("feature/import")
        self.status(history="Earlier feature/import was discussed")
        self.assertIn("locally known unmerged branches not in Now", self.run_hook())

    def test_merged_remote_branch_does_not_warn(self):
        self.feature("feature/import")
        self.git("merge", "--no-ff", "-qm", "Integrate import", "feature/import")
        self.sync_default()
        self.status(baseline=self.oid())
        self.assertNotIn("Vibe continuity warning:", self.run_hook())

    def test_unknown_default_and_missing_baseline_are_advisory(self):
        self.status()
        self.git("symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
        self.assertIn("default branch is unknown locally", self.run_hook())
        self.sync_default()
        self.status(baseline="0" * 40)
        self.assertIn("baseline is unavailable locally", self.run_hook())

    def test_unique_non_origin_default_is_supported(self):
        self.status()
        self.git("symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
        self.git("update-ref", "refs/remotes/team/trunk", self.baseline)
        self.git("symbolic-ref", "refs/remotes/team/HEAD", "refs/remotes/team/trunk")
        self.assertNotIn("Vibe continuity warning:", self.run_hook())

    def test_worktree_and_nested_directory_use_project_root(self):
        self.status()
        self.commit()
        worker = self.area / "worker"
        self.git("worktree", "add", "--detach", "-q", str(worker), "HEAD")
        nested = worker / "src/nested"
        nested.mkdir(parents=True)
        context = self.run_hook(cwd=nested)
        self.assertIn("Position: Family import in progress", context)
        self.assertNotIn("Vibe continuity warning:", context)

    def test_environment_fallback_and_non_git_project(self):
        outside = self.area / "outside"
        (outside / "docs").mkdir(parents=True)
        shutil.copyfile(self.status(), outside / "docs/STATUS.md")
        context = self.run_hook(payload={}, env={"CLAUDE_PROJECT_DIR": str(outside)})
        self.assertIn("Next task: Finish validating", context)
        self.assertIn("default branch is unknown locally", context)

    def test_malformed_legacy_status_does_not_dump_the_file(self):
        path = self.status()
        path.write_text("# Status\nIn progress: none\nLegacy private detail\n")
        context = self.run_hook()
        self.assertIn("status has no Now summary", context)
        self.assertNotIn("Legacy private detail", context)

    def test_missing_fields_and_oversized_summary_are_bounded(self):
        self.status(extra="\n".join("detail " + "x" * 600 for _ in range(20)))
        context = self.run_hook(status_only=True)
        self.assertIn("size limit", context)
        self.assertLess(len(context), 5500)
        self.assertNotIn("## History", context)
        self.assertLessEqual(len(context.split("## Now\n", 1)[1].split("Vibe continuity warning:")[0].splitlines()), 10)
        self.status().write_text("## Now\nPosition: unfinished\n")
        self.assertIn("Now summary is incomplete", self.run_hook())

    def test_git_calls_are_read_only_and_disable_network_fetch(self):
        self.feature("feature/import")
        self.status()
        self.commit()
        before = self.git("status", "--porcelain").stdout
        shim = self.area / "bin"
        shim.mkdir()
        log = self.area / "git-calls.jsonl"
        program = shim / "git"
        program.write_text(f"#!{sys.executable}\n"
                           "import json, os, sys\n"
                           "args=sys.argv[1:]\n"
                           "command=args[args.index('-C')+2]\n"
                           "assert command in {'rev-parse','for-each-ref','merge-base','log'}, command\n"
                           "assert os.environ['GIT_NO_LAZY_FETCH']=='1'\n"
                           "assert os.environ['GIT_ALLOW_PROTOCOL']==''\n"
                           "assert os.environ['GIT_OPTIONAL_LOCKS']=='0'\n"
                           f"with open({str(log)!r},'a') as out: out.write(json.dumps(args)+'\\n')\n"
                           f"os.execv({shutil.which('git')!r}, ['git',*args])\n")
        program.chmod(0o755)
        self.assertIn("locally known unmerged", self.run_hook(env={"PATH": str(shim) + os.pathsep + os.environ["PATH"]}))
        self.assertTrue(log.read_text().strip())
        self.assertEqual(self.git("status", "--porcelain").stdout, before)

    def cold_resume_checkout(self):
        """A new clone has only remote source and durable handoff, no old session."""
        self.feature("feature/import")
        self.status(progress="Duplicate handling on feature/import")
        self.commit()
        remote = self.area / "remote.git"
        self.git("init", "--bare", "-q", "-b", "main", str(remote))
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-q", "--all", "origin")
        fresh = self.area / "fresh-session"
        self.git("clone", "-q", str(remote), str(fresh))
        return fresh

    def test_fresh_checkout_can_find_active_work_and_next_task(self):
        fresh = self.cold_resume_checkout()
        context = self.run_hook(cwd=fresh, status_only=True)
        self.assertIn("In progress: Duplicate handling on feature/import", context)
        self.assertIn("Next task: Finish validating duplicate relatives before importing.", context)
        self.assertIn("Waiting on owner: none", context)
        self.assertNotIn("Vibe continuity warning:", context)
        self.assertEqual(self.git("show", "origin/feature/import:partial.txt", cwd=fresh).stdout,
                         "preserved partial implementation\n")


if __name__ == "__main__":
    unittest.main()
