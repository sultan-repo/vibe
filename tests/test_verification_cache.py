"""Exercise the optional verification template against real, isolated Git repositories."""
from pathlib import Path
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "hooks/verification-cache.py"
TEMPLATE = ROOT / "hooks/pre-push.template"
CONTEXT = "runtime-1/fixture-1"
GATE = '''from pathlib import Path
import os, subprocess, sys, time
count = Path(".gate-count")
count.write_text((count.read_text() if count.exists() else "") + sys.argv[-1] + "\\n")
action = os.environ.get("GATE_ACTION", "")
if action == "fail":
    sys.exit(9)
if action == "context":
    Path(".context-value").write_text("changed fixture")
if action in ("dirty", "commit"):
    Path("source.txt").write_text("changed during verification\\n")
    if action == "commit":
        subprocess.run(["git", "add", "source.txt"], check=True)
        subprocess.run(["git", "commit", "-qm", "Concurrent change"], check=True)
if action == "wait":
    Path(".gate-ready").touch()
    deadline = time.monotonic() + 8
    while not Path(".gate-release").exists():
        if time.monotonic() > deadline:
            sys.exit(8)
        time.sleep(0.02)
'''


class VerificationCacheTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="vibe-verification-test-")
        self.addCleanup(self.temporary.cleanup)
        self.area = Path(self.temporary.name)
        self.repo = self.area / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Verification test")
        self.git("config", "user.email", "verification@example.invalid")
        (self.repo / ".gitignore").write_text(".gate-*\n.context-*\n.guard-seen\n")
        (self.repo / "source.txt").write_text("initial\n")
        (self.repo / "gate.py").write_text(GATE)
        self.git("add", ".")
        self.git("commit", "-qm", "Initial fixture")
        self.command = [sys.executable, "gate.py"]

    def git(self, *args, cwd=None, check=True, **kwargs):
        return subprocess.run(["git", *args], cwd=cwd or self.repo, text=True,
                              capture_output=True, check=check, **kwargs)

    def oid(self, ref="HEAD", cwd=None):
        return self.git("rev-parse", ref, cwd=cwd).stdout.strip()

    def arguments(self, action="run", mode="full", context=CONTEXT, includes=True,
                  fresh=False, helper=HELPER, context_command=None):
        args = [sys.executable, str(helper), action, "--mode", mode]
        args.extend(["--context-command", context_command] if context_command else ["--context", context])
        if includes:
            args.append("--full-includes-quick")
        if fresh:
            args.append("--fresh")
        return [*args, "--", *self.command]

    def run_gate(self, *, cwd=None, updates=None, env=None, **options):
        if updates is not None:
            options["action"] = "pre-push"
        return subprocess.run(self.arguments(**options), cwd=cwd or self.repo,
                              input=updates, text=True, capture_output=True,
                              env={**os.environ, **(env or {})}, timeout=15)

    def count(self, cwd=None):
        path = (cwd or self.repo) / ".gate-count"
        return path.read_text().splitlines() if path.exists() else []

    def cache(self, cwd=None):
        path = self.git("rev-parse", "--path-format=absolute", "--git-path",
                        "vibe-verification", cwd=cwd).stdout.strip()
        return Path(path)

    def update(self, local="HEAD", remote="refs/heads/main"):
        return f"{local} {self.oid(local)} {remote} {'0' * len(self.oid())}\n"

    def assert_pass(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reuses_same_tree_after_a_real_merge_commit(self):
        self.assert_pass(self.run_gate())
        before = self.oid()
        self.git("checkout", "-qb", "side")
        self.git("commit", "--allow-empty", "-qm", "Same source")
        self.git("checkout", "-q", "main")
        self.git("merge", "--no-ff", "-qm", "Merge same source", "side")
        self.assertNotEqual(self.oid(), before)
        self.assertEqual(self.oid("HEAD^{tree}"), self.oid(before + "^{tree}"))
        result = self.run_gate()
        self.assert_pass(result)
        self.assertIn("reusing full", result.stdout)
        self.assertEqual(self.count(), ["full"])

    def test_mode_coverage_preserves_the_stronger_pass(self):
        self.assert_pass(self.run_gate(mode="quick"))
        self.assert_pass(self.run_gate(mode="full"))
        self.assertEqual(self.count(), ["quick", "full"])
        self.assert_pass(self.run_gate(mode="quick", fresh=True))
        self.assert_pass(self.run_gate(mode="full"))
        self.assertEqual(self.count(), ["quick", "full", "quick"])

    def test_full_covers_quick_only_with_explicit_contract(self):
        for includes in (False, True):
            with self.subTest(includes=includes):
                self.assert_pass(self.run_gate(includes=includes))
                before = len(self.count())
                self.assert_pass(self.run_gate(mode="quick", includes=includes))
                self.assertEqual(len(self.count()), before + (0 if includes else 1))

    def test_changed_tree_context_command_or_helper_requires_a_new_pass(self):
        self.assert_pass(self.run_gate())
        (self.repo / "source.txt").write_text("new source\n")
        self.git("commit", "-qam", "Change source")
        self.assert_pass(self.run_gate())
        self.assert_pass(self.run_gate(context="runtime-2/fixture-1"))
        self.command = [sys.executable, "./gate.py"]
        self.assert_pass(self.run_gate(context="runtime-2/fixture-1"))
        alternate = self.area / "new-helper.py"
        alternate.write_text(HELPER.read_text() + "\n")
        self.assert_pass(self.run_gate(context="runtime-2/fixture-1", helper=alternate))
        self.assertEqual(self.count(), ["full"] * 5)

    def test_failed_fresh_run_cannot_reuse_an_older_pass(self):
        self.assert_pass(self.run_gate())
        self.assert_pass(self.run_gate(mode="quick", fresh=True))
        failed = self.run_gate(fresh=True, env={"GATE_ACTION": "fail"})
        self.assertEqual(failed.returncode, 9)
        self.assertEqual(list(self.cache().glob("*.json")), [])
        self.assert_pass(self.run_gate(mode="quick"))
        self.assert_pass(self.run_gate())
        self.assertEqual(self.count(), ["full", "quick", "full", "quick", "full"])

    def context_provider(self):
        path = self.repo / "context.py"
        path.write_text(f"#!{sys.executable}\n" +
                        "from pathlib import Path\nimport os\n" +
                        "reads = Path('.context-reads')\n" +
                        "count = int(reads.read_text()) if reads.exists() else 0\n" +
                        "reads.write_text(str(count + 1))\n" +
                        "if os.environ.get('CONTEXT_CHANGE') and count == 1:\n" +
                        "    Path('.context-value').write_text('changed fixture')\n" +
                        "print(Path('.context-value').read_text())\n")
        path.chmod(0o755)
        self.git("add", "context.py")
        self.git("commit", "-qm", "Declare context")
        (self.repo / ".context-value").write_text(CONTEXT)
        return "./context.py"

    def test_context_change_during_gate_invalidates_previous_evidence(self):
        provider = self.context_provider()
        self.assert_pass(self.run_gate(context_command=provider))
        result = self.run_gate(context_command=provider, fresh=True, env={"GATE_ACTION": "context"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("context changed", result.stderr)
        self.assertEqual(list(self.cache().glob("*.json")), [])
        (self.repo / ".context-value").write_text(CONTEXT)
        self.assert_pass(self.run_gate(context_command=provider))
        self.assertEqual(self.count(), ["full", "full", "full"])

    def test_context_is_rechecked_even_when_reusing_a_pass(self):
        provider = self.context_provider()
        self.assert_pass(self.run_gate(context_command=provider))
        (self.repo / ".context-reads").write_text("0")
        result = self.run_gate(context_command=provider, env={"CONTEXT_CHANGE": "yes"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("context changed", result.stderr)
        self.assertEqual(list(self.cache().glob("*.json")), [])
        self.assertEqual(self.count(), ["full"])

    def test_dirty_staged_and_untracked_inputs_block_even_a_cache_hit(self):
        self.assert_pass(self.run_gate())
        for kind in ("tracked", "staged", "untracked"):
            with self.subTest(kind=kind):
                path = self.repo / ("extra.py" if kind == "untracked" else "source.txt")
                path.write_text("not committed\n")
                if kind == "staged":
                    self.git("add", "source.txt")
                result = self.run_gate(updates=self.update())
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("dirty", result.stderr)
                if kind == "untracked":
                    path.unlink()
                else:
                    self.git("restore", "--staged", "--worktree", "source.txt")
        self.assertEqual(self.count(), ["full"])

    def test_mid_run_mutation_or_commit_never_records_a_pass(self):
        for action in ("dirty", "commit"):
            with self.subTest(action=action):
                result = self.run_gate(env={"GATE_ACTION": action})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(self.cache().glob("*.json")), [])
                self.git("restore", "source.txt")

    def test_corrupt_records_rerun_and_do_not_store_raw_context(self):
        self.assert_pass(self.run_gate())
        marker = next(self.cache().glob("*.json"))
        self.assertNotIn(CONTEXT, marker.read_text())
        self.assertNotIn("gate.py", marker.read_text())
        for malformed in ("{", "[]", '{"schema": 9}', json.dumps({
                **json.loads(marker.read_text()), "passes": {"full": "not a timestamp"}})):
            with self.subTest(malformed=malformed):
                marker.write_text(malformed)
                self.assert_pass(self.run_gate())
        self.assertEqual(self.count(), ["full"] * 5)

    def test_real_push_rejects_unverified_non_head_even_when_head_passed(self):
        self.git("checkout", "-qb", "other")
        (self.repo / "source.txt").write_text("other branch\n")
        self.git("commit", "-qam", "Other source")
        self.git("checkout", "-q", "main")
        self.assert_pass(self.run_gate())
        remote = self.area / "remote.git"
        self.git("init", "--bare", "-q", str(remote))
        self.git("remote", "add", "origin", str(remote))
        hook = self.repo / ".git/hooks/pre-push"
        hook.write_text("#!/bin/sh\nexec " + shlex.join(self.arguments(action="pre-push")) + "\n")
        hook.chmod(0o755)
        pushed = self.git("push", "origin", "other", check=False)
        self.assertNotEqual(pushed.returncode, 0)
        self.assertIn("not checked out", pushed.stderr)
        self.assertNotEqual(self.git("show-ref", "--verify", "refs/heads/other", cwd=remote,
                                     check=False).returncode, 0)
        self.assert_pass(self.git("push", "origin", "main", check=False))
        self.assertEqual(self.count(), ["full"])

    def test_multiple_pushed_refs_and_annotated_tag_use_their_own_evidence(self):
        self.assert_pass(self.run_gate())
        main = self.oid()
        self.git("checkout", "-qb", "other")
        (self.repo / "source.txt").write_text("other branch\n")
        self.git("commit", "-qam", "Other source")
        self.assert_pass(self.run_gate())
        self.git("tag", "-am", "Release", "v-test")
        other = self.oid()
        tag = self.oid("v-test")
        self.git("checkout", "-q", "main")
        updates = "".join(f"{ref} {oid} {ref} {'0' * 40}\n" for ref, oid in (
            ("refs/heads/main", main), ("refs/heads/other", other), ("refs/tags/v-test", tag)))
        result = self.run_gate(updates=updates)
        self.assert_pass(result)
        self.assertEqual(result.stdout.count("reusing full"), 2)
        self.assertEqual(self.count(), ["full", "full"])

    def test_empty_and_deletion_only_pushes_do_not_run_source_checks(self):
        (self.repo / "source.txt").write_text("unrelated dirty checkout\n")
        self.assert_pass(self.run_gate(updates=""))
        self.assert_pass(self.run_gate(updates=f"(delete) {'0' * 40} refs/heads/old {self.oid()}\n",
                                       context_command="./missing-context-program"))
        self.assertEqual(self.count(), [])

    def test_malformed_updates_and_non_commit_objects_fail_closed(self):
        blob = self.git("hash-object", "-w", "--stdin", input="tagged content").stdout.strip()
        for updates in ("bad update\n", "\n", f"HEAD not-an-oid refs/heads/main {'0' * 40}\n",
                        f"HEAD {'0' * 40} refs/heads/main {self.oid()}\n",
                        f"refs/tags/blob {blob} refs/tags/blob {'0' * 40}\n"):
            with self.subTest(updates=updates):
                self.assertNotEqual(self.run_gate(updates=updates).returncode, 0)
        self.assertEqual(self.count(), [])

    def test_linked_worktree_uses_private_git_metadata(self):
        self.assert_pass(self.run_gate())
        worker = self.area / "worker"
        self.git("worktree", "add", "--detach", "-q", str(worker), "HEAD")
        self.assertTrue((worker / ".git").is_file())
        self.assert_pass(self.run_gate(cwd=worker))
        self.assert_pass(self.run_gate(cwd=worker, mode="quick"))
        self.assertNotEqual(self.cache(), self.cache(cwd=worker))
        self.assertEqual(self.count(), ["full"])
        self.assertEqual(self.count(cwd=worker), ["full"])

    def test_concurrent_runs_do_not_execute_a_second_gate(self):
        process = subprocess.Popen(self.arguments(), cwd=self.repo, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env={**os.environ, "GATE_ACTION": "wait"})
        try:
            deadline = time.monotonic() + 5
            while not (self.repo / ".gate-ready").exists() and process.poll() is None:
                self.assertLess(time.monotonic(), deadline, "gate did not start")
                time.sleep(0.02)
            result = self.run_gate()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("verification is active", result.stderr)
        finally:
            (self.repo / ".gate-release").touch()
            stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 0, stdout + stderr)
        self.assertEqual(self.count(), ["full"])
        self.assertFalse((self.cache() / "active.lock").exists())

    def install_template(self):
        hooks = self.repo / ".githooks"
        scripts = self.repo / "scripts"
        hooks.mkdir()
        scripts.mkdir()
        shutil.copyfile(HELPER, hooks / "verification-cache.py")
        shutil.copyfile(TEMPLATE, hooks / "pre-push")
        (hooks / "pre-push").chmod(0o755)
        guard = hooks / "pre-push.project"
        guard.write_text(f"#!{sys.executable}\n" +
                         "from pathlib import Path\nimport json, os, sys\n" +
                         "Path('.guard-seen').write_text(json.dumps([sys.argv[1:], sys.stdin.read()]))\n" +
                         "sys.exit(int(os.environ.get('GUARD_FAIL', '0')))\n")
        guard.chmod(0o755)
        adapter = scripts / "verify.sh"
        adapter.write_text("#!/bin/sh\nexec " + shlex.join(self.command) + ' "$@"\n')
        adapter.chmod(0o755)
        context = scripts / "verification-context"
        context.write_text(f"#!/bin/sh\nprintf '%s\\n' {shlex.quote(CONTEXT)}\n")
        context.chmod(0o755)
        self.git("add", ".githooks", "scripts")
        self.git("commit", "-qm", "Adopt project gate")
        self.command = ["scripts/verify.sh"]
        return hooks

    def test_template_preserves_guards_stdin_and_full_release_mode(self):
        hooks = self.install_template()
        updates = self.update(remote="refs/heads/release")
        result = subprocess.run([str(hooks / "pre-push"), "origin", "example.invalid:repo"],
                                cwd=self.repo, input=updates, text=True, capture_output=True, timeout=15)
        self.assert_pass(result)
        self.assertEqual(json.loads((self.repo / ".guard-seen").read_text()),
                         [["origin", "example.invalid:repo"], updates])
        self.assert_pass(self.run_gate(mode="quick", helper=hooks / "verification-cache.py",
                                       context_command="scripts/verification-context"))
        self.assertEqual(self.count(), ["full"])
        blocked = subprocess.run([str(hooks / "pre-push"), "origin", "example.invalid:repo"],
                                 cwd=self.repo, input=updates, text=True, capture_output=True,
                                 env={**os.environ, "GUARD_FAIL": "7"}, timeout=15)
        self.assertEqual(blocked.returncode, 7)
        self.assertEqual(self.count(), ["full"])
        self.assertEqual(list((self.repo / ".git").glob("vibe-pre-push.*")), [])

    def test_template_mixed_stack_push_keeps_lower_refs_quick(self):
        hooks = self.install_template()
        context = {"context_command": "scripts/verification-context", "helper": hooks / "verification-cache.py"}
        self.assert_pass(self.run_gate(mode="quick", **context))
        lower = self.update("main", "refs/heads/main")
        self.git("checkout", "-qb", "candidate")
        (self.repo / "source.txt").write_text("integrated candidate\n")
        self.git("commit", "-qam", "Integrate milestone")
        self.assert_pass(self.run_gate(**context))
        updates = lower + self.update("candidate", "refs/heads/release")
        result = subprocess.run([str(hooks / "pre-push"), "origin", "example.invalid:repo"],
                                cwd=self.repo, input=updates, text=True, capture_output=True, timeout=15)
        self.assert_pass(result)
        self.assertEqual(self.count(), ["quick", "full"])
        self.assertIn("reusing quick", result.stdout)
        self.assertIn("reusing full", result.stdout)
        self.assertEqual(json.loads((self.repo / ".guard-seen").read_text())[1], updates)

    def test_template_deletion_does_not_execute_context_command(self):
        hooks = self.install_template()
        (self.repo / "scripts/verification-context").unlink()
        updates = f"(delete) {'0' * 40} refs/heads/release {self.oid()}\n"
        result = subprocess.run([str(hooks / "pre-push"), "origin", "example.invalid:repo"],
                                cwd=self.repo, input=updates, text=True, capture_output=True, timeout=15)
        self.assert_pass(result)
        self.assertEqual(self.count(), [])


if __name__ == "__main__":
    unittest.main()
