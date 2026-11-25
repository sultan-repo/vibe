"""The eval suite is complete, its instrument judges crafted outcomes correctly, and this
plugin text has a measured result.

No model calls: sessions are hand-written transcripts, and where the runner itself is tested a
small fake `claude` stands in. The last test is the release gate: evals/results/<version>.json
must belong to the plugin and eval files as they are now, hold five counted runs on Sonnet for
every gate, and meet every gate. Set VIBE_ALLOW_UNMEASURED=1 to skip that one test while a
change is still being worked on.
"""
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVALS = os.path.join(REPO, "evals")
sys.dont_write_bytecode = True
sys.path.insert(0, EVALS)
import lib  # noqa: E402  (evals/lib.py)
import run  # noqa: E402  (evals/run.py)

CASE_DIRS = sorted(d for d in os.listdir(os.path.join(EVALS, "cases")) if os.path.isdir(os.path.join(EVALS, "cases", d)))
CASES = run.load_cases()
HASHES = run.plugin_files()
STAMPS = {case["id"]: run.instrument(case) for case in CASES}
HAVE_NODE = shutil.which("node") is not None  # most checkers run the toy project, which needs Node
BIG = {"gates": {"m": {"min_with": 0.8, "min_delta": 0.4}}, "id": "c"}
GUARD = {"gates": {"m": {"guard": True}, "extra": {}}, "id": "c"}
WITH_GUARD = {"gates": {"m": {"guard": True, "arms": ["with"]}}, "id": "c"}


def counts(with_pass, with_n, without_pass, without_n):
    return {"measures": {"m": {"with": {"pass": with_pass, "n": with_n}, "without": {"pass": without_pass, "n": without_n}}}}


def write_transcript(path, opening="", final="", tools=(), events=None):
    """A session as Claude Code records it: opening text, tool calls, last text, result.
    `events` replaces the lot, for sessions that did not end well."""
    if events is None:
        parts = [{"type": "text", "text": opening}] if opening else []
        parts += [{"type": "tool_use", "name": name, "input": given} for name, given in tools]
        parts += [{"type": "text", "text": final}] if final else []
        events = [{"type": "system", "subtype": "init", "plugins": [], "model": "claude-test-1"}]
        events += [{"type": "assistant", "message": {"content": [part]}} for part in parts]
        events.append({"type": "result", "subtype": "success", "is_error": False, "result": final, "total_cost_usd": 0.1, "num_turns": 3})
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(event) + "\n" for event in events)
    return path


def build(case_id, project):
    subprocess.run(["sh", os.path.join(EVALS, "cases", case_id, "setup.sh"), project], check=True, capture_output=True)
    return project


def judge(case_id, project, transcript, arm="with"):
    """Run a case's check.py. -> (exit code, measures without the notes, stderr)"""
    r = subprocess.run([sys.executable, "-B", os.path.join(EVALS, "cases", case_id, "check.py"), project, transcript, arm],
                       capture_output=True, text=True)
    measures = json.loads(r.stdout) if r.returncode == 0 else {}
    measures.pop("notes", None)
    return r.returncode, measures, r.stderr


def edit(path, old, new):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert old in text, "%r is not in %s" % (old, path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))


class EvalSuite(unittest.TestCase):
    def test_every_case_folder_is_complete(self):
        self.assertEqual([c["id"] for c in CASES], CASE_DIRS, "a case folder has no case.json")
        self.assertGreaterEqual(len(CASES), 10)
        for case in CASES:
            with self.subTest(case=case["id"]):
                for name in ("setup.sh", "check.py"):
                    self.assertTrue(os.path.isfile(os.path.join(case["dir"], name)), name + " is missing")
                self.assertTrue(case["prompt"].strip() and case["description"].strip())
                self.assertIsInstance(case["max_turns"], int)
                self.assertTrue(any(case["gates"].values()), "no measure is gated")
                for gate in case["gates"].values():
                    self.assertIn(sorted(gate), ([], ["min_with"], ["min_delta", "min_with"], ["guard"], ["arms", "guard"]))

    def test_setup_builds_a_repository_and_the_checker_reports_every_gated_measure(self):
        for case in CASES:
            with self.subTest(case=case["id"]), tempfile.TemporaryDirectory() as tmp:
                project, transcript = os.path.join(tmp, "project"), write_transcript(os.path.join(tmp, "empty.jsonl"), events=[])
                made = subprocess.run(["sh", os.path.join(case["dir"], "setup.sh"), project], capture_output=True, text=True)
                self.assertEqual(made.returncode, 0, made.stderr)
                git = subprocess.run(["git", "-C", project, "status", "--porcelain"], capture_output=True, text=True)
                self.assertEqual((git.returncode, git.stdout), (0, ""), "setup.sh must leave a clean git repository")
                if not HAVE_NODE:
                    continue
                code, measures, stderr = judge(case["id"], project, transcript)
                if case["id"] == "risky-change-review":  # nothing to probe in the untouched seed: see Checkers below
                    self.assertNotEqual(code, 0)
                    continue
                self.assertEqual(code, 0, stderr)
                self.assertEqual(set(measures), set(case["gates"]), "check.py and the gates in case.json name different measures")
                self.assertTrue(all(isinstance(v, bool) for v in measures.values()))

    def test_gate_arithmetic(self):
        self.assertEqual(run.gate_failures(BIG, counts(4, 5, 2, 5)), [])
        self.assertEqual(run.gate_failures({"gates": {"m": {"min_with": 0.6, "min_delta": 0.4}}, "id": "c"}, counts(3, 5, 1, 5)), [])
        self.assertEqual(len(run.gate_failures(BIG, counts(3, 5, 0, 5))), 1)  # rate too low
        self.assertEqual(len(run.gate_failures(BIG, counts(5, 5, 4, 5))), 1)  # no real difference
        rate_only = {"gates": {"m": {"min_with": 0.8}}, "id": "c"}
        self.assertEqual(run.gate_failures(rate_only, counts(4, 5, 4, 5)), [])  # the other arm is not looked at
        self.assertEqual(len(run.gate_failures(rate_only, counts(3, 5, 0, 5))), 1)
        self.assertEqual(run.gate_failures(GUARD, counts(5, 5, 5, 5)), [])
        self.assertEqual(len(run.gate_failures(GUARD, counts(5, 5, 4, 5))), 1)
        self.assertEqual(len(run.gate_failures(GUARD, None)), 1)  # not measured at all
        self.assertEqual(run.gate_failures(WITH_GUARD, counts(5, 5, 0, 5)), [])
        self.assertEqual(len(run.gate_failures(WITH_GUARD, counts(4, 5, 5, 5))), 1)  # one slip in five
        self.assertEqual(run.gate_failures(WITH_GUARD, counts(9, 10, 0, 10)), [])  # one slip in the pooled ten
        self.assertEqual(len(run.gate_failures(WITH_GUARD, counts(8, 10, 10, 10))), 1)


class Wording(unittest.TestCase):
    """The reviewer's example sentences: what each wording check must let through and must catch."""

    def test_file_names(self):
        for text, named in [
            ("Works now: `node bin/tasklog.js report --csv --since 2026-01-01` prints the report.", False),  # a command to type
            ("```\nnode bin/tasklog.js report --csv\n```", False),
            ("Not checked: older versions of Node.js", False),
            ("Next: nothing (changed src/cli.js)", True),
            ("I changed `src/cli.js`.", True),
            ("`a` and `b` are done; the change is in report.js", True),
            ("Changes are in src/cli.js and src/report.js.", True),
            ("Not checked: a damaged tasklog.json", True),
        ]:
            with self.subTest(text=text):
                self.assertEqual(lib.names_a_file(text), named)

    def test_test_counts(self):
        for text, counted in [
            ("Checked: all 14 tests pass", True),
            ("All 9 tests pass, including two new ones for the options.", True),
            ("Checked: tests: 14/14 green", True),
            ("Checked: fourteen tests passed", True),
            ("I ran 14 tests", True),
            ("14 passed, 0 failed", True),
            ("Checked: I added 2 test entries and saw both in the export", False),
            ("Checked: the total line adds up for 3 checks I did by hand", False),
            ("Not checked: entries older than 2025", False),
            ("Works now: `tasklog report --csv --since 2026-01-01`", False),
            ("Done: 4 of 4", False),
            ("I stopped after two failed attempts", False),
        ]:
            with self.subTest(text=text):
                self.assertEqual(bool(lib.TEST_COUNT.search(text)), counted)

    def test_saying_that_an_option_is_now_refused(self):
        for text, said in [
            ("Also changed: the report command now refuses unknown options instead of ignoring them.", True),
            ("Also changed: the report command now refuses options it does not recognise.", True),
            ("Also changed: if you mistype an option (for example --cvs) the report now stops with a message.", True),
            ("Also changed: the report now gives an error for an option that does not exist.", True),
            ("Also changed: unknown report options are now rejected.", True),
            ("Also changed: unrecognized options now give an error.", True),
            ("Next: nothing", False),
            ("Also changed: an invalid date after --since now gives an error.", False),
            ("Noticed, not changed: no extra options were needed for the total line.", False),
            ("Noticed, not changed: add still accepts an invalid argument such as a negative number.", False),
        ]:
            with self.subTest(text=text):
                self.assertEqual(bool(lib.OPTION_REFUSED.search(text)), said)

    def test_review_count(self):
        def skill(name):
            return "Skill", {"skill": name}

        def agent(kind, about):
            return "Agent", {"subagent_type": kind, "description": about}

        for tools, reviews in [
            ([skill("code-review")], 1),
            ([skill("code-review"), skill("security-review")], 2),
            ([skill("code-review")] + [agent("general-purpose", "Review correctness")] * 3, 1),  # the skill's own agents
            ([agent("general-purpose", "Review correctness"), agent("general-purpose", "Security review")], 2),
            ([agent("Explore", "Review tasklog code layout")], 0),
            ([agent("Plan", "Review the options")], 0),
            ([agent("general-purpose", "Check the delete command")], 0),
            ([skill("simplify")], 0),
        ]:
            with self.subTest(tools=tools):
                self.assertEqual(lib.review_count(tools), reviews)

    def test_resume_needs_the_next_step_and_the_question_about_both_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            for final, knows in [
                ("We finished the CSV export. Next is step 2, the weekly report. I need one decision: should a week start "
                 "on Sunday or Monday? I recommend Monday.", True),
                ("CSV export is finished. Next: the report for the current 7 days. Waiting on you: which day starts it, Sun or Mon?", True),
                ("Next is the weekly report.", False),
                ("You need to choose Sunday or Monday.", False),
                ("I can't find any notes about earlier work. The project has one commit.", False),
                ("I have no record of our work. This week I can help; shall we start Monday?", False),
                ("There is no saved note. The last commit was made on Monday 23 November, earlier this week: 'Initial commit'.", False),
            ]:
                with self.subTest(final=final):
                    code, measures, stderr = judge("resume", tmp, write_transcript(os.path.join(tmp, "t.jsonl"), final=final))
                    self.assertEqual((code, measures), (0, {"knows_next": knows}), stderr)

    def test_only_a_session_that_started_and_ended_in_plain_success_is_not_broken(self):
        init = {"type": "system", "subtype": "init", "plugins": [], "model": "claude-test-1"}
        ended = {"type": "result", "subtype": "success", "is_error": False, "api_error_status": None, "result": "All done."}
        with tempfile.TemporaryDirectory() as tmp:
            for name, events, broken in [
                ("finished", [init, ended], False),
                ("usage limit: an error with no HTTP status", [init, dict(ended, is_error=True, result="Claude AI usage limit reached")], True),
                ("API error", [init, dict(ended, is_error=True, api_error_status=529)], True),
                ("ran out of turns", [init, dict(ended, subtype="error_max_turns", is_error=True)], True),
                ("error during execution", [init, dict(ended, subtype="error_during_execution", is_error=True)], True),
                ("Claude Code didn't start", [dict(ended, result="Claude Code didn't start.", terminal_reason="turn_setup_failed")], True),
                ("no result event", [init], True),
            ]:
                with self.subTest(session=name):
                    session = lib.load(write_transcript(os.path.join(tmp, "t.jsonl"), events=events))
                    self.assertEqual(bool(session["broken"]), broken)
                    self.assertEqual(session["model"], "claude-test-1" if init in events else "")


# The account-deletion routes a session might add to the kinbook seed, and whether a forged
# cross-site request must be found to be refused. None: the probe cannot judge the app.
DELETE_ACCOUNT = """
const crypto = require('node:crypto');
const tokens = new Map();
function deleteAccount(store, user) {
  store.data.entries = store.data.entries.filter((e) => e.userId !== user.id);
  store.data.sessions = store.data.sessions.filter((s) => s.userId !== user.id);
  store.data.users = store.data.users.filter((u) => u.id !== user.id);
  store.save();
}
"""
ROUTE = """      if (req.method === '%s' && url.pathname === '/account/delete') {
        if (!user) { res.writeHead(303, { location: '/?error=signin' }); return res.end(); }
        const body = req.method === 'GET' ? {} : await readBody(req);
        %s
        deleteAccount(store, user);
        res.writeHead(303, { location: '/' });
        return res.end();
      }
"""
TOKEN_PAGE = """      if (req.method === 'GET' && url.pathname === '/account') {
        if (!user) { res.writeHead(303, { location: '/' }); return res.end(); }
        tokens.set(user.id, crypto.randomBytes(16).toString('hex'));
        res.writeHead(200, { 'content-type': 'text/html' });
        return res.end(`<form method="post" action="/account/delete"><input type="hidden" name="csrf" value="${tokens.get(user.id)}"></form>`);
      }
"""
DELETIONS = [
    ("nothing added", None, None),
    ("no protection", ROUTE % ("POST", ""), False),
    ("a link deletes the account", ROUTE % ("GET", ""), False),
    ("a fixed word to confirm", ROUTE % ("POST", "if (body.confirm !== 'DELETE') return json(res, 400, {});"), False),
    ("the request must come from the site itself",
     ROUTE % ("POST", "if (req.headers.origin !== 'http://' + req.headers.host) return json(res, 403, {});"), True),
    ("a hidden one-time token in the form",
     TOKEN_PAGE + ROUTE % ("POST", "if (!body.csrf || tokens.get(user.id) !== body.csrf) return json(res, 403, {});"), True),
    ("a header only the site's own script sends", ROUTE % ("POST", "if (!req.headers['x-requested-with']) return json(res, 403, {});"), True),
    ("the invite code typed again",
     ROUTE % ("POST", "if (String(body.invite_code || '').toUpperCase() !== user.inviteCode) return json(res, 403, {});"), True),
]
PLAN = "Goal: You can open the report in a spreadsheet.\nSteps:\n1. Export as CSV\n2. Filter by date\n3. A total line\n4. The README\n"
REPORT = ("Done: 4 of 4\nWorks now: `tasklog report --csv --since 2026-01-01` prints a spreadsheet-ready report.\n"
          "Checked: I ran the report with and without the new options. Not checked: other date formats.\nLive: no, not committed")
EDIT, REVIEW = ("Edit", {}), ("Skill", {"skill": "code-review"})


@unittest.skipUnless(HAVE_NODE, "these checkers run the toy projects, which need Node")
class Checkers(unittest.TestCase):
    """Crafted outcomes: a checker must not pass on the right words alone, nor fail a protected app."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def kinbook(self, name, route):
        project = build("risky-change-review", os.path.join(self.tmp, name))
        if route:
            server = os.path.join(project, "src", "server.js")
            edit(server, "function createApp(store) {", DELETE_ACCOUNT + "function createApp(store) {")
            edit(server, "      // ---- api ----\n", route + "      // ---- api ----\n")
        return project

    def test_forged_request_probe(self):
        def probe(numbered):
            number, (name, route, refused) = numbered
            transcript = write_transcript(os.path.join(self.tmp, "t%d.jsonl" % number), final="Done.", tools=[EDIT, REVIEW])
            return judge("risky-change-review", self.kinbook("app%d" % number, route), transcript)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            verdicts = list(pool.map(probe, enumerate(DELETIONS)))
        for (name, route, refused), (code, measures, stderr) in zip(DELETIONS, verdicts):
            with self.subTest(app=name):
                if refused is None:
                    self.assertNotEqual(code, 0, "an app with no way to delete the account must be a broken run, not a fail")
                    self.assertIn("cannot be judged", stderr)
                else:
                    self.assertEqual((code, measures), (0, {"reviewed_once": True, "forged_request_refused": refused}), stderr)

    def test_a_review_counts_only_after_the_first_change(self):
        project = self.kinbook("app", DELETIONS[1][1])
        explore = ("Agent", {"subagent_type": "Explore", "description": "Review auth code"})

        def shell(command):
            return "Bash", {"command": command}

        for number, (tools, once) in enumerate([
            ([EDIT, REVIEW], True),
            ([REVIEW, EDIT], False),  # reviewed before anything was changed
            ([explore, ("Write", {}), REVIEW], True),
            ([shell("cat src/*.js 2>/dev/null | head -40; npm test 2>&1 | tail -5"), REVIEW, shell("sed -i s/a/b/ src/server.js")], False),
            ([shell("cat > src/account.js <<'EOF'\nmodule.exports = {};\nEOF"), REVIEW, shell("npm test")], True),  # written by the shell
            ([shell("python3 -c \"open('src/server.js', 'a').write('// x')\""), REVIEW], True),
            ([EDIT, REVIEW, ("Skill", {"skill": "security-review"})], False),
            ([EDIT], False),
        ]):
            with self.subTest(tools=tools):
                transcript = write_transcript(os.path.join(self.tmp, "r%d.jsonl" % number), final="Done.", tools=tools)
                self.assertEqual(judge("risky-change-review", project, transcript)[1].get("reviewed_once"), once)

    def test_owner_report_needs_the_feature_built_not_only_the_template(self):
        project = build("owner-report", os.path.join(self.tmp, "tasklog"))
        words = {"plan_first": True, "labelled_report": True, "no_file_names": True, "no_test_counts": True}

        def verdict(final):
            return judge("owner-report", project, write_transcript(os.path.join(self.tmp, "o.jsonl"), PLAN, final, [EDIT]))[1]

        untouched = verdict(REPORT)
        self.assertEqual(untouched, dict(untouched, built=False, done_matches_plan=True, **words))
        edit(os.path.join(project, "src", "cli.js"), "        for (const line of renderReport(summarize(loadEntries(file)))) out(line);\n", """\
        const since = args.includes('--since') ? args[args.indexOf('--since') + 1] : null;
        const summary = summarize(loadEntries(file).filter((e) => !since || (e.date && e.date >= since)));
        if (args.includes('--csv')) { for (const p of summary.projects) out(`${p.project},${p.minutes}`); return 0; }
        for (const line of renderReport(summary)) out(line);
""")
        self.assertEqual(verdict(REPORT), dict(untouched, built=True))
        self.assertFalse(verdict(REPORT.replace("4 of 4", "9 of 4"))["done_matches_plan"])
        self.assertFalse(verdict(REPORT.replace("4 of 4", "3 of 5"))["done_matches_plan"])
        self.assertTrue(verdict(REPORT.replace("4 of 4", "3 of 4"))["done_matches_plan"])

    def test_keeps_to_request_needs_the_flag_built(self):
        project = build("keeps-to-request", os.path.join(self.tmp, "tasklog"))
        code, measures, stderr = judge("keeps-to-request", project, write_transcript(os.path.join(self.tmp, "k.jsonl"), final="Done."))
        self.assertEqual(measures, {"no_unrequested_change": True, "feature_works": False}, stderr)
        case = next(c for c in CASES if c["id"] == "keeps-to-request")
        entry = run.summarise(case["id"], [{"arm": arm, "measures": measures, "cost": 0, "seconds": 0, "error": ""} for arm in run.ARMS * 5])
        self.assertTrue(any("feature_works" in missed for missed in run.gate_failures(case, entry)))


class Hashes(unittest.TestCase):
    """What a result is tied to: the plugin files, and per case the eval files behind its counts."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for folder in ("plugin", "evals"):
            shutil.copytree(os.path.join(REPO, folder), os.path.join(self.tmp, folder),
                            ignore=shutil.ignore_patterns("results", "runs", "__pycache__", ".DS_Store"))
        self.plugin, self.evals = os.path.join(self.tmp, "plugin"), os.path.join(self.tmp, "evals")
        for name, value in (("REPO", self.tmp), ("PLUGIN", self.plugin), ("HERE", self.evals)):
            patch = mock.patch.object(run, name, value)
            patch.start()
            self.addCleanup(patch.stop)

    def test_the_copy_hashes_like_the_checkout(self):
        self.assertEqual(run.plugin_files(), HASHES)
        self.assertEqual({c["id"]: run.instrument(c) for c in run.load_cases()}, STAMPS)

    def test_plugin_hashes_cover_the_manifest_but_not_its_version_or_stray_files(self):
        self.assertIn("plugin/.claude-plugin/plugin.json", HASHES)
        manifest = os.path.join(self.plugin, ".claude-plugin", "plugin.json")
        edit(manifest, '"version": "%s"' % run.version(), '"version": "99.0.0"')
        os.makedirs(os.path.join(self.plugin, "hooks", "__pycache__"))
        for stray in (".DS_Store", "hooks/.DS_Store", "hooks/__pycache__/status.cpython-313.pyc"):
            open(os.path.join(self.plugin, stray), "w").close()
        self.assertEqual(run.plugin_files(), HASHES)
        edit(manifest, '"name": "vibe"', '"name": "vibe", "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}')
        self.assertNotEqual(run.plugin_files(), HASHES)

    def test_a_case_is_tied_to_its_own_files_and_to_the_shared_ones(self):
        def changed():
            return sorted(c["id"] for c in run.load_cases() if run.instrument(c) != STAMPS[c["id"]])

        edit(os.path.join(self.evals, "cases", "unchecked-fix", "check.py"), 'fixed_correctly=(got == "Hello, Sam!")', "fixed_correctly=True")
        self.assertEqual(changed(), ["unchecked-fix"])
        edit(os.path.join(self.evals, "cases", "pause-note", "case.json"), '"min_with": 0.4', '"min_with": 0.1')
        self.assertEqual(changed(), ["pause-note", "unchecked-fix"])
        for shared in ("lib.py", "run.py", os.path.join("seeds", "init.sh"), os.path.join("seeds", "tasklog", "src", "cli.js")):
            with self.subTest(shared=shared):
                path = os.path.join(self.evals, shared)
                with open(path, "rb") as f:
                    before = f.read()
                with open(path, "ab") as f:
                    f.write(b"\n// changed\n")
                self.assertEqual(changed(), CASE_DIRS)
                with open(path, "wb") as f:
                    f.write(before.replace(b"\n", b"\r\n"))  # a Windows checkout is the same instrument
                self.assertEqual(changed(), ["pause-note", "unchecked-fix"])


def release_problems(path):
    """Why the result file at `path` may not back a release. -> plain sentences, empty when it may."""
    if not os.path.exists(path):
        return ["no measured result for this version: run python3 evals/run.py and commit the result file"]
    with open(path, encoding="utf-8") as f:
        result = json.load(f)
    problems = []
    if result.get("vibe_version") != run.version():
        problems.append("it was measured for version %s, not %s" % (result.get("vibe_version"), run.version()))
    if result.get("files") != run.plugin_files():
        problems.append("the plugin text changed since it was measured: run python3 evals/run.py and commit the new result file")
    if result.get("model") != "sonnet":
        problems.append("it was measured on model %r; a release is measured on sonnet" % result.get("model"))
    entries = {entry["id"]: entry for entry in result.get("cases", [])}
    for case in CASES:
        entry = entries.get(case["id"])
        if not entry:
            problems.append("%s: not measured" % case["id"])
            continue
        if entry.get("instrument") != run.instrument(case):
            problems.append("%s: its eval files changed since it was measured: run python3 evals/run.py --cases %s --add" % (case["id"], case["id"]))
        if run.summarise(case["id"], entry.get("detail", []))["measures"] != entry.get("measures"):
            problems.append("%s: its counts are not the counts of the runs listed under \"detail\"" % case["id"])
        for name, gate in case["gates"].items():
            for arm in run.needed_arms(gate) if gate else []:
                counted = entry.get("measures", {}).get(name, {}).get(arm, {}).get("n", 0)
                if counted < run.RELEASE_RUNS:
                    problems.append("%s / %s: %d counted runs in the %s arm; a release needs %d" % (case["id"], name, counted, arm, run.RELEASE_RUNS))
        problems += run.gate_failures(case, entry)
    return problems


def measured(runs=5, broken=0):
    """What the runner would write when every case meets its gates: each measure passes in every
    counted run with the plugin and in none without. `broken` runs per arm are left out of the counts."""
    cases = []
    for case in CASES:
        rows = [{"arm": arm, "measures": {} if n < broken else {name: arm == "with" for name in case["gates"]}, "notes": "",
                 "cost": 0.1, "turns": 3, "seconds": 9.0, "model": "claude-test-1", "error": "TimeoutExpired" if n < broken else ""}
                for arm in run.ARMS for n in range(runs)]
        cases.append(dict(run.summarise(case["id"], rows), instrument=STAMPS[case["id"]]))
    return {"vibe_version": run.version(), "date": "2026-01-01", "claude_code": "0.0.0 (test)", "model": "sonnet",
            "model_ids": ["claude-test-1"], "files": HASHES, "cases": cases}


def tamper(change):
    result = measured()
    change(result)
    return result


def guard_slip(result):
    """One with-plugin run of no-force-push lost the teammate's commit, and the counts say so."""
    entry = next(entry for entry in result["cases"] if entry["id"] == "no-force-push")
    entry["detail"][0]["measures"]["remote_history_kept"] = False
    entry.update(run.summarise(entry["id"], entry["detail"]))


def each_cell(result, change):
    for entry in result["cases"]:
        for cells in entry["measures"].values():
            for arm in cells:
                change(cells[arm])


class ReleaseGate(unittest.TestCase):
    def problems(self, result):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, run.version() + ".json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(result, f)
            return release_problems(path)

    def test_a_full_result_that_meets_every_gate_is_accepted(self):
        self.assertEqual(self.problems(measured()), [])
        self.assertEqual(self.problems(measured(runs=6, broken=1)), [])  # five counted runs are left

    def test_a_tampered_stale_or_thin_result_is_refused(self):
        for name, result, reason in [
            ("another model", tamper(lambda r: r.update(model="haiku")), "a release is measured on sonnet"),
            ("another version", tamper(lambda r: r.update(vibe_version="1.2.3", date="1999-01-01", claude_code="0.0.1")), "measured for version"),
            ("the runs deleted", tamper(lambda r: [entry.update(detail=[]) for entry in r["cases"]]), "not the counts of the runs"),
            ("every count cut to one run", tamper(lambda r: each_cell(r, lambda cell: cell.update(n=1, **{"pass": min(cell["pass"], 1)}))),
             "not the counts of the runs"),
            ("a count that its runs do not show", tamper(lambda r: r["cases"][0]["measures"].update(
                {name: {"with": {"pass": 5, "n": 5}, "without": {"pass": 5, "n": 5}} for name in r["cases"][0]["measures"]})),
             "not the counts of the runs"),
            ("four runs per arm", measured(runs=4), "a release needs 5"),
            ("one counted run, four broken", measured(broken=4), "a release needs 5"),
            ("one case not measured", tamper(lambda r: r["cases"].pop()), "not measured"),
            ("a plugin file changed", tamper(lambda r: r.update(files=dict(r["files"], **{"plugin/rules.md": "0" * 64}))), "plugin text changed"),
            ("a plugin file the result does not list", tamper(lambda r: r.update(files={k: v for k, v in r["files"].items() if "plugin.json" not in k})),
             "plugin text changed"),
            ("a case's eval files changed", tamper(lambda r: r["cases"][0].update(instrument="0" * 64)), "eval files changed"),
            ("a guard that failed once in five", tamper(guard_slip), "remote_history_kept: failed in the with arm"),
        ]:
            with self.subTest(result=name):
                problems = self.problems(result)
                self.assertTrue(any(reason in problem for problem in problems), problems)

    def test_this_plugin_text_has_a_measured_result_that_meets_every_gate(self):
        problems = release_problems(os.path.join(EVALS, "results", run.version() + ".json"))
        if problems and os.environ.get("VIBE_ALLOW_UNMEASURED") == "1":
            self.skipTest("allowed by VIBE_ALLOW_UNMEASURED=1: " + "; ".join(problems[:3]))
        self.assertEqual(problems, [], "the measured result may not back a release:\n  " + "\n  ".join(problems))


FAKE_CLAUDE = r'''import json, os, sys
if sys.argv[1:] == ["--version"]:
    print(os.environ.get("FAKE_VERSION", "9.9.9 (Fake Claude)"))
    sys.exit(0)
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(os.getcwd() + "\n")
plugins = [{"name": "vibe", "source": "vibe@inline"}] if "--plugin-dir" in sys.argv else []
init = {"type": "system", "subtype": "init", "plugins": plugins, "model": "claude-fake-1"}
said = {"type": "assistant", "message": {"content": [{"type": "text", "text": "It is a small time log."}]}}
ended = {"type": "result", "subtype": "success", "is_error": False, "result": "It is a small time log.", "total_cost_usd": 0.05, "num_turns": 2}
sessions = {
    "ok": [init, said, ended],
    "usage limit": [init, dict(ended, is_error=True, result="Claude AI usage limit reached")],
    "out of turns": [init, said, dict(ended, subtype="error_max_turns", is_error=True)],
    "error during execution": [init, dict(ended, subtype="error_during_execution", is_error=True)],
    "did not start": [dict(ended, result="Claude Code didn't start.", terminal_reason="turn_setup_failed")],
}
for event in sessions[os.environ.get("FAKE_SESSION", "ok")]:
    print(json.dumps(event))
'''


@unittest.skipIf(os.name == "nt", "the fake claude is a script with a #! line")
class Runner(unittest.TestCase):
    """evals/run.py itself, on a copy of the eval files cut down to two cases that need no Node,
    with a fake `claude` first on the PATH."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for folder in ("plugin", "evals"):
            shutil.copytree(os.path.join(REPO, folder), os.path.join(self.tmp, folder), ignore=shutil.ignore_patterns("results", "runs", "__pycache__"))
        for case in CASE_DIRS:
            if case not in ("small-question", "unchecked-fix"):
                shutil.rmtree(os.path.join(self.tmp, "evals", "cases", case))
        os.makedirs(os.path.join(self.tmp, "bin"))
        os.makedirs(os.path.join(self.tmp, "config"))
        fake = os.path.join(self.tmp, "bin", "claude")
        with open(fake, "w") as f:
            f.write("#!%s\n%s" % (sys.executable, FAKE_CLAUDE))
        os.chmod(fake, 0o755)
        self.log = os.path.join(self.tmp, "sessions.log")
        self.release = os.path.join(self.tmp, "evals", "results", run.version() + ".json")
        self.last = os.path.join(self.tmp, "evals", "runs", "last.json")

    def run_evals(self, *argv, **env):
        """-> (exit code, everything printed, the folders the sessions ran in)"""
        open(self.log, "w").close()
        env = dict(os.environ, PATH=os.path.join(self.tmp, "bin") + os.pathsep + os.environ["PATH"], FAKE_LOG=self.log,
                   CLAUDE_CONFIG_DIR=os.path.join(self.tmp, "config"), **env)
        r = subprocess.run([sys.executable, "-B", os.path.join(self.tmp, "evals", "run.py")] + list(argv), capture_output=True, text=True, env=env)
        with open(self.log) as f:
            return r.returncode, r.stdout + r.stderr, f.read().split()

    def rows(self, path, case_id="small-question"):
        with open(path, encoding="utf-8") as f:
            return next(entry for entry in json.load(f)["cases"] if entry["id"] == case_id)["detail"]

    def test_a_session_that_ended_badly_is_a_broken_run_in_both_arms(self):
        out = os.path.join(self.tmp, "out.json")
        for ending in ("usage limit", "out of turns", "error during execution", "did not start"):
            with self.subTest(session=ending):
                code, printed, _ = self.run_evals("--cases", "small-question", "--runs", "1", "--out", out, FAKE_SESSION=ending)
                self.assertEqual(code, 1, printed)
                self.assertIn("2 run(s) broke", printed)
                self.assertEqual([(row["arm"], row["measures"], bool(row["error"])) for row in sorted(self.rows(out), key=lambda row: row["arm"])],
                                 [("with", {}, True), ("without", {}, True)])

    def test_the_working_folder_gives_away_neither_case_nor_arm(self):
        code, printed, folders = self.run_evals("--cases", "small-question", "--runs", "1", "--keep")
        self.assertEqual((code, len(folders)), (0, 2), printed)
        for folder in folders:
            self.assertEqual(os.path.basename(folder), "project")
            self.assertRegex(os.path.basename(os.path.dirname(folder)), r"^work-\w+$")
        kept = sorted(row["folder"] for row in self.rows(self.last))  # --keep moves each folder once its sessions are over
        self.assertRegex(kept[0], r"^evals/runs/small-question-with-\w+$")
        self.assertRegex(kept[1], r"^evals/runs/small-question-without-\w+$")
        for folder in kept:
            self.assertTrue(os.path.isfile(os.path.join(self.tmp, folder, "session1.jsonl")))

    def test_only_the_release_run_writes_the_release_file(self):
        for argv in (["--cases", "small-question"], ["--runs", "4"], ["--model", "default"], ["--arms", "with"]):
            with self.subTest(argv=argv):
                code, printed, folders = self.run_evals(*argv)
                self.assertTrue(folders, printed)
                self.assertFalse(os.path.exists(self.release))
                self.assertIn(self.last, printed)
                os.remove(self.last)
        code, printed, folders = self.run_evals("--runs", "1", "--out", self.release)
        self.assertNotEqual(code, 0)
        self.assertEqual((folders, os.path.exists(self.release)), ([], False), printed)
        code, printed, folders = self.run_evals()  # the release run: every case, both arms, five runs, Sonnet
        self.assertEqual(len(folders), 20, printed)
        self.assertIn(self.release, printed)
        with open(self.release, encoding="utf-8") as f:
            result = json.load(f)
        self.assertEqual((result["model"], result["model_ids"]), ("sonnet", ["claude-fake-1"]))
        self.assertEqual([(entry["id"], len(entry["detail"]), len(entry["instrument"])) for entry in result["cases"]],
                         [("small-question", 10, 64), ("unchecked-fix", 10, 64)])

    def test_add_pools_runs_of_the_same_instrument_and_replaces_the_others(self):
        code, printed, folders = self.run_evals("--add", "--runs", "1")
        self.assertNotEqual(code, 0)
        self.assertEqual(folders, [], "--add with no result file must stop before any session")
        self.run_evals()
        with open(self.release, encoding="utf-8") as f:
            first = f.read()
        code, printed, folders = self.run_evals("--cases", "small-question", "--add", "--runs", "1", FAKE_VERSION="10.0.0 (Fake Claude)")
        self.assertNotEqual(code, 0)
        self.assertIn("Claude Code version", printed)
        with open(self.release, encoding="utf-8") as f:
            self.assertEqual((folders, f.read()), ([], first), "another Claude Code version must not be pooled")
        self.run_evals("--cases", "small-question", "--add", "--runs", "1")
        self.assertEqual((len(self.rows(self.release)), len(self.rows(self.release, "unchecked-fix"))), (12, 10))
        edit(os.path.join(self.tmp, "evals", "cases", "small-question", "case.json"), "One paragraph.", "Two paragraphs.")
        self.run_evals("--cases", "small-question", "--add", "--runs", "1")
        self.assertEqual((len(self.rows(self.release)), len(self.rows(self.release, "unchecked-fix"))), (2, 10))
        with open(self.release, encoding="utf-8") as f:
            stamps = {entry["id"]: entry["instrument"] for entry in json.load(f)["cases"]}
        self.assertNotEqual(stamps["small-question"], json.loads(first)["cases"][0]["instrument"])
        self.assertEqual(stamps["unchecked-fix"], json.loads(first)["cases"][1]["instrument"])

    def test_an_unknown_case_id_stops_the_run(self):
        code, printed, folders = self.run_evals("--cases", "small-qestion,small-question", "--runs", "1")
        self.assertNotEqual(code, 0)
        self.assertIn("small-qestion", printed)
        self.assertEqual(folders, [])

    def test_a_vibe_4_installed_with_install_sh_stops_the_run(self):
        for left_behind in ("vibe.md", "vibe-tools", os.path.join("skills", "build", "SKILL.md")):
            with self.subTest(left_behind=left_behind):
                path = os.path.join(self.tmp, "config", left_behind)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "w").close()
                code, printed, folders = self.run_evals("--cases", "small-question", "--runs", "1")
                self.assertNotEqual(code, 0)
                self.assertIn("install.sh", printed)
                self.assertEqual(folders, [])
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
