#!/usr/bin/env python3
"""Vibe eval runner: the same small tasks, with and without the plugin.

    python3 evals/run.py              the release run: every case, both arms, 5 runs, Sonnet
    python3 evals/run.py [--runs 5] [--model sonnet] [--cases a,b] [--arms with,without]
                         [--jobs 4] [--out FILE] [--add] [--keep]

For every case, arm and run: build a fresh toy project in the system temp folder with the
case's setup.sh, run `claude -p` on the case's prompt (and a second, new session in the
same folder when the case has a "then" prompt), then run the case's check.py. The result
file records pass counts per measure and arm, mean cost, the sha256 of every plugin file
and, per case, one sha256 of the eval files behind its counts, so a result always belongs
to one exact plugin text and one exact instrument. Only the release run, or --add to its
file, writes evals/results/<version>.json; any other run writes evals/runs/last.json.
Standard library only.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PLUGIN = os.path.join(REPO, "plugin")
sys.dont_write_bytecode = True  # leave no __pycache__ in the repository
sys.path.insert(0, HERE)
import lib  # noqa: E402

ARMS = ("with", "without")
# Both arms switch off any installed copy of Vibe; the "with" arm then loads this checkout.
OFF = '{"enabledPlugins":{"vibe@vibe":false,"vibe@synced":false}}'
TOOLS = "Read,Edit,Write,Glob,Grep,Bash,Skill,Agent,Task,TodoWrite,TaskCreate,TaskUpdate,TaskList,TaskGet"
TIMEOUT = 1200  # seconds for one session
RELEASE_RUNS = 5  # runs per case and arm that a release result needs


def version():
    with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def files_under(folder, dot_files=False):
    """Every file under a folder, sorted, leaving out Python bytecode, .DS_Store and (unless asked for) other dot-files."""
    found = []
    for where, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        found += [os.path.join(where, n) for n in names if not n.endswith(".pyc")
                  and (n != ".DS_Store" if dot_files else not n.startswith("."))]
    return sorted(found)


def plugin_files():
    """{path relative to the repo: sha256} for every shipped file. plugin.json is hashed without
    its version number, which a release may raise without changing what was measured."""
    found = {}
    for path in files_under(PLUGIN):
        with open(path, "rb") as f:
            data = f.read()
        if os.path.basename(path) == "plugin.json":
            manifest = json.loads(data)
            manifest.pop("version", None)
            data = json.dumps(manifest, sort_keys=True).encode()
        found[os.path.relpath(path, REPO).replace(os.sep, "/")] = hashlib.sha256(data).hexdigest()
    return found


def instrument(case):
    """One sha256 over the eval files that decide a case's counts: this runner, lib.py, the
    case's own folder and the seed projects. Line ends are ignored."""
    digest = hashlib.sha256()
    shared = [os.path.join(HERE, "run.py"), os.path.join(HERE, "lib.py")]
    for path in shared + files_under(case["dir"], True) + files_under(os.path.join(HERE, "seeds"), True):  # a seed's .gitignore shapes the project too
        with open(path, "rb") as f:
            name = os.path.relpath(path, HERE).replace(os.sep, "/").encode()
            digest.update(name + b"\0" + f.read().replace(b"\r\n", b"\n") + b"\0")
    return digest.hexdigest()


def load_cases():
    cases = []
    for name in sorted(os.listdir(os.path.join(HERE, "cases"))):
        folder = os.path.join(HERE, "cases", name)
        if os.path.isfile(os.path.join(folder, "case.json")):
            with open(os.path.join(folder, "case.json"), encoding="utf-8") as f:
                cases.append(dict(json.load(f), id=name, dir=folder))
    return cases


def session(case, arm, model, prompt, project, transcript):
    cmd = ["claude", "-p", prompt, "--max-turns", str(case.get("max_turns", 40)),
           "--permission-mode", case.get("permission_mode", "acceptEdits"), "--allowedTools", TOOLS,
           "--output-format", "stream-json", "--verbose", "--include-hook-events", "--settings", OFF]
    if model != "default":
        cmd += ["--model", model]
    if arm == "with":
        cmd += ["--plugin-dir", PLUGIN]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_INCLUDE_PARTIAL_MESSAGES"}
    with open(transcript, "w") as out, open(transcript + ".stderr", "w") as err:
        subprocess.run(cmd, cwd=project, stdin=subprocess.DEVNULL, stdout=out, stderr=err, env=env, timeout=TIMEOUT)


def one_run(case, arm, model, keep):
    """One fresh project, one or two sessions, one check. -> a row for the result file."""
    row = {"arm": arm, "measures": {}, "notes": "", "cost": 0.0, "turns": 0, "seconds": 0.0, "model": "", "error": ""}
    # The session can read the path of its folder, so the name gives away neither the case nor the arm.
    root = tempfile.mkdtemp(prefix="work-")
    project, transcripts, start = os.path.join(root, "project"), [], time.time()
    try:
        subprocess.run(["sh", os.path.join(case["dir"], "setup.sh"), project], check=True, capture_output=True, timeout=120)
        for prompt in filter(None, [case["prompt"], case.get("then")]):
            transcripts.append(os.path.join(root, "session%d.jsonl" % (len(transcripts) + 1)))
            session(case, arm, model, prompt, project, transcripts[-1])
            t = lib.load(transcripts[-1])
            row["cost"] += t["cost"]
            row["turns"] += t["turns"]
            row["model"] = t["model"]
            if t["broken"]:
                with open(transcripts[-1] + ".stderr", errors="replace") as f:
                    raise RuntimeError("session broke (%s): %s" % (t["broken"], f.read().strip()[-200:] or t["final"][:200] or "no output"))
            vibes = sorted(p for p in t["plugins"] if p.startswith("vibe@"))
            if vibes != (["vibe@inline"] if arm == "with" else []):
                raise RuntimeError("wrong Vibe plugins loaded for the '%s' arm: %s" % (arm, vibes or "none"))
        row["seconds"], row["cost"] = round(time.time() - start, 1), round(row["cost"], 4)
        check = subprocess.run([sys.executable, "-B", os.path.join(case["dir"], "check.py"), project] + transcripts + [arm],
                               capture_output=True, text=True, timeout=300)
        if check.returncode:
            raise RuntimeError("the checker could not judge this run: " + check.stderr.strip()[-200:])
        row["measures"] = json.loads(check.stdout)
        row["notes"] = row["measures"].pop("notes", "")
    except Exception as err:  # a broken run is recorded and left out of the counts
        row["error"] = "%s: %s" % (type(err).__name__, str(err)[:300])
    finally:
        if keep:
            kept = os.path.join(HERE, "runs", "%s-%s-%s" % (case["id"], arm, os.path.basename(root)[len("work-"):]))
            os.makedirs(os.path.dirname(kept), exist_ok=True)
            row["folder"] = os.path.relpath(shutil.move(root, kept), REPO)
        else:
            shutil.rmtree(root, ignore_errors=True)
    return row


def summarise(case_id, rows):
    """Per-run rows of one case -> its entry in the result file."""
    entry = {"id": case_id, "measures": {}, "cost": {}, "seconds": {}, "errors": {}, "detail": rows}
    for arm in ARMS:
        good = [r for r in rows if r["arm"] == arm and not r["error"]]
        entry["errors"][arm] = sum(1 for r in rows if r["arm"] == arm and r["error"])
        if good:
            entry["cost"][arm] = round(sum(r["cost"] for r in good) / len(good), 4)
            entry["seconds"][arm] = round(sum(r["seconds"] for r in good) / len(good), 1)
        for r in good:
            for name, passed in r["measures"].items():
                cell = entry["measures"].setdefault(name, {}).setdefault(arm, {"pass": 0, "n": 0})
                cell["pass"] += bool(passed)
                cell["n"] += 1
    return entry


def needed_arms(gate):
    """The arms a gate is judged on: both for a difference, the with arm for a rate alone, and
    for a guard the arms it lists (both when it lists none)."""
    return gate.get("arms", ARMS) if gate.get("guard") or "min_delta" in gate else ["with"]


def gate_failures(case, entry):
    """One case's counts against the gates in its case.json. -> list of plain sentences, empty when all are met.
    {"min_with": 0.8, "min_delta": 0.4}: the with-plugin pass rate, and its lead over the without arm.
    {"min_with": 0.8}: the with-plugin pass rate alone.
    {"guard": true, "arms": ["with"]}: every run must pass in the arms listed (both when "arms" is left
    out); from ten counted runs on, one failure is allowed.
    {}: recorded, not gated.
    """
    missed = []
    for name, gate in case["gates"].items():
        if not gate:
            continue
        cells = (entry or {}).get("measures", {}).get(name, {})
        rate = {arm: cells[arm]["pass"] / cells[arm]["n"] for arm in ARMS if cells.get(arm, {}).get("n")}
        needed = needed_arms(gate)
        label = "%s / %s" % (case["id"], name)
        if any(arm not in rate for arm in needed):
            missed.append("%s: not measured in the %s arm" % (label, " and ".join(a for a in needed if a not in rate)))
        elif gate.get("guard"):
            missed += ["%s: failed in the %s arm (%d of %d passed; a guard needs every run, or all but one of ten or more)" % (
                label, a, cells[a]["pass"], cells[a]["n"]) for a in needed
                if cells[a]["n"] - cells[a]["pass"] > (1 if cells[a]["n"] >= 10 else 0)]
        else:
            if rate["with"] < gate.get("min_with", 0) - 1e-9:
                missed.append("%s: %.2f with the plugin, needs %.2f" % (label, rate["with"], gate["min_with"]))
            if "min_delta" in gate and rate["with"] - rate["without"] < gate["min_delta"] - 1e-9:
                missed.append("%s: %.2f with against %.2f without, needs a difference of %+.2f" % (
                    label, rate["with"], rate["without"], gate["min_delta"]))
    return missed


def table(cases, entries):
    lines, missed = [], []
    for case in cases:
        entry = entries.get(case["id"])
        if not entry:
            continue
        bad = gate_failures(case, entry)
        missed += bad
        lines.append(case["id"])
        for name in list(case["gates"]) + [m for m in entry["measures"] if m not in case["gates"]]:
            cells = entry["measures"].get(name, {})
            count = ["%d/%d" % (cells[a]["pass"], cells[a]["n"]) if a in cells else "-" for a in ARMS]
            start = "%s / %s:" % (case["id"], name)
            verdict = "not gated" if not case["gates"].get(name) else ("MISSED" if any(b.startswith(start) for b in bad) else "met")
            lines.append("  %-24s with %-5s without %-5s %s" % (name, count[0], count[1], verdict))
        cost = ["$%.3f" % entry["cost"][a] if a in entry["cost"] else "-" for a in ARMS]
        lines.append("  %-24s with %-5s without %-5s errors %d" % ("mean cost per run", cost[0], cost[1], sum(entry["errors"].values())))
    return "\n".join(lines), missed


def main():
    p = argparse.ArgumentParser(description="Run the Vibe eval cases with and without the plugin.")
    p.add_argument("--runs", type=int, default=RELEASE_RUNS, help="runs per case and arm (default %d, what a release needs)" % RELEASE_RUNS)
    p.add_argument("--model", default="sonnet", help='model alias or id; "default" uses your configured model')
    p.add_argument("--cases", default="", help="comma-separated case ids (default: all)")
    p.add_argument("--arms", default="with,without")
    p.add_argument("--jobs", type=int, default=4, help="sessions run at the same time")
    p.add_argument("--out", default="", help="result file (default: evals/results/<version>.json for the release run "
                   "and for --add, evals/runs/last.json for any other run)")
    p.add_argument("--add", action="store_true", help="add these runs to the existing result file for the same plugin text, "
                   "model and Claude Code version")
    p.add_argument("--keep", action="store_true", help="keep each run's project and transcripts under evals/runs/")
    a = p.parse_args()
    every, wanted, asked_arms = load_cases(), [c for c in a.cases.split(",") if c], a.arms.split(",")
    unknown = sorted(set(wanted) - {c["id"] for c in every}) + sorted(set(asked_arms) - set(ARMS))
    if unknown:
        sys.exit("no such case or arm: %s (cases: %s; arms: %s)" % (", ".join(unknown), ", ".join(c["id"] for c in every), ", ".join(ARMS)))
    cases, arms = [c for c in every if not wanted or c["id"] in wanted], [arm for arm in ARMS if arm in asked_arms]
    if a.runs < 1:
        sys.exit("nothing to run: --runs must be 1 or more")
    release = os.path.join(HERE, "results", version() + ".json")
    full = len(cases) == len(every) and len(arms) == len(ARMS) and a.model == "sonnet" and a.runs >= RELEASE_RUNS
    out = os.path.abspath(a.out or (release if full or a.add else os.path.join(HERE, "runs", "last.json")))
    if out == release and not (full or a.add):
        sys.exit("%s is the release result: only a run of every case, both arms, model sonnet and %d or more runs, "
                 "or --add, may write it" % (os.path.relpath(release, REPO), RELEASE_RUNS))
    config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    if any(os.path.exists(os.path.join(config, name)) for name in ("vibe.md", "vibe-tools", "skills/build/SKILL.md")):
        sys.exit("a Vibe 4 installed with install.sh is active in %s; remove it before measuring (CHANGES.md, Upgrading from Vibe 4)" % config)
    claude_code = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    files, stamps, rows = plugin_files(), {c["id"]: instrument(c) for c in cases}, {}
    if a.add:
        if not os.path.exists(out):
            sys.exit("--add needs an existing result file: " + out)
        with open(out, encoding="utf-8") as f:
            old = json.load(f)
        if (old["files"], old["model"], old["claude_code"]) != (files, a.model, claude_code):
            sys.exit("--add needs a result file made with this exact plugin text, model and Claude Code version: " + out)
        for c in old["cases"]:
            stamps.setdefault(c["id"], c["instrument"])  # a case that is not run now keeps its rows as they are
            if stamps[c["id"]] == c["instrument"]:  # rows measured with other eval files are replaced, not pooled
                rows[c["id"]] = c["detail"]
    jobs = [(case, arm) for _ in range(a.runs) for case in cases for arm in arms]
    print("%d sessions to run (%d cases, %d runs, arms: %s), %d at a time" % (
        sum(2 if c.get("then") else 1 for c, _ in jobs), len(cases), a.runs, ", ".join(arms), a.jobs), file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as pool:
        futures = {pool.submit(one_run, case, arm, a.model, a.keep): case for case, arm in jobs}
        for done, future in enumerate(concurrent.futures.as_completed(futures), 1):
            case, row = futures[future], future.result()
            rows.setdefault(case["id"], []).append(row)
            shown = row["error"] or " ".join("%s=%s" % (k, "yes" if v else "no") for k, v in row["measures"].items())
            print("[%d/%d] %s, %s: %s ($%.3f, %.0f s)" % (
                done, len(jobs), case["id"], row["arm"], shown, row["cost"], row["seconds"]), file=sys.stderr)
    if plugin_files() != files or any(instrument(c) != stamps[c["id"]] for c in cases):
        sys.exit("the plugin or the eval files changed while the suite was running: nothing written, run it again")
    result = {"vibe_version": version(), "date": datetime.date.today().isoformat(), "claude_code": claude_code, "model": a.model,
              "model_ids": sorted({r["model"] for case_rows in rows.values() for r in case_rows if r.get("model")}),
              "files": files, "cases": [dict(summarise(k, rows[k]), instrument=stamps[k]) for k in sorted(rows)]}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=1) + "\n")
    text, missed = table(every, {c["id"]: c for c in result["cases"]})
    total = sum(r["cost"] for case_rows in rows.values() for r in case_rows)
    print("\nVibe %s, %s, model %s (pass counts: runs that passed / runs counted)\n%s" % (result["vibe_version"], claude_code, a.model, text))
    print("\nTotal cost of all runs in this file: $%.2f. Result written to %s%s" % (
        total, out, "" if out == release else " (a try-out file, not the release result)"))
    print("Gates missed:\n  " + "\n  ".join(missed) if missed else "All gates met for the cases in this file.")
    broken = sum(sum(c["errors"].values()) for c in result["cases"])
    if broken:
        print("%d run(s) broke and were left out of the counts; see \"error\" in the result file." % broken)
    sys.exit(1 if missed or broken else 0)


if __name__ == "__main__":
    main()
