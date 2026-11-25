#!/usr/bin/env python3
"""Vibe eval runner: the same small tasks, with and without the plugin.

    python3 evals/run.py [--runs 3] [--model sonnet] [--cases a,b] [--arms with,without]
                         [--jobs 4] [--out FILE] [--add] [--keep]

For every case, arm and run: build a fresh toy project in the system temp folder with the
case's setup.sh, run `claude -p` on the case's prompt (and a second, new session in the
same folder when the case has a "then" prompt), then run the case's check.py. The result
file records pass counts per measure and arm, mean cost, and the sha256 of every plugin
file, so a result always belongs to one exact plugin text. Standard library only.
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


def version():
    with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def plugin_files():
    """{path relative to the repo: sha256} for every shipped file except plugin.json."""
    found = {}
    for folder, dirs, names in os.walk(PLUGIN):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in names:
            path = os.path.join(folder, name)
            if name != "plugin.json" and not name.endswith(".pyc"):
                with open(path, "rb") as f:
                    found[os.path.relpath(path, REPO).replace(os.sep, "/")] = hashlib.sha256(f.read()).hexdigest()
    return dict(sorted(found.items()))


def load_cases(only=None):
    cases = []
    for name in sorted(os.listdir(os.path.join(HERE, "cases"))):
        folder = os.path.join(HERE, "cases", name)
        if os.path.isfile(os.path.join(folder, "case.json")) and (not only or name in only):
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
    row = {"arm": arm, "measures": {}, "notes": "", "cost": 0.0, "turns": 0, "seconds": 0.0, "error": ""}
    root = tempfile.mkdtemp(prefix="vibe-eval-%s-%s-" % (case["id"], arm))
    project, transcripts, start = os.path.join(root, "project"), [], time.time()
    try:
        subprocess.run(["sh", os.path.join(case["dir"], "setup.sh"), project], check=True, capture_output=True, timeout=120)
        for prompt in filter(None, [case["prompt"], case.get("then")]):
            transcripts.append(os.path.join(root, "session%d.jsonl" % (len(transcripts) + 1)))
            session(case, arm, model, prompt, project, transcripts[-1])
            t = lib.load(transcripts[-1])
            row["cost"] += t["cost"]
            row["turns"] += t["turns"]
            if t["ended"] is None or t["api_error"]:
                with open(transcripts[-1] + ".stderr", errors="replace") as f:
                    raise RuntimeError("session did not finish: " + (f.read().strip()[-200:] or t["final"][:200] or "no output"))
            vibes = sorted(p for p in t["plugins"] if p.startswith("vibe@"))
            if vibes != (["vibe@inline"] if arm == "with" else []):
                raise RuntimeError("wrong Vibe plugins loaded for the '%s' arm: %s" % (arm, vibes or "none"))
        row["seconds"], row["cost"] = round(time.time() - start, 1), round(row["cost"], 4)
        check = subprocess.run([sys.executable, "-B", os.path.join(case["dir"], "check.py"), project] + transcripts + [arm],
                               capture_output=True, text=True, timeout=300)
        row["measures"] = json.loads(check.stdout)
        row["notes"] = row["measures"].pop("notes", "")
    except Exception as err:  # a broken run is recorded and left out of the counts
        row["error"] = "%s: %s" % (type(err).__name__, str(err)[:300])
    finally:
        if keep:
            os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
            row["folder"] = os.path.relpath(shutil.move(root, os.path.join(HERE, "runs")), REPO)
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


def gate_failures(case, entry):
    """One case's counts against the gates in its case.json. -> list of plain sentences, empty when all are met.
    {"min_with": 0.8, "min_delta": 0.4}: the with-plugin pass rate, and its lead over the without arm.
    {"guard": true}: every run must pass, in both arms (or in the arms listed under "arms").
    {}: recorded, not gated.
    """
    missed = []
    for name, gate in case["gates"].items():
        if not gate:
            continue
        cells = (entry or {}).get("measures", {}).get(name, {})
        rate = {arm: cells[arm]["pass"] / cells[arm]["n"] for arm in ARMS if cells.get(arm, {}).get("n")}
        needed = gate.get("arms", ARMS) if gate.get("guard") or "min_delta" in gate else ["with"]
        label = "%s / %s" % (case["id"], name)
        if any(arm not in rate for arm in needed):
            missed.append("%s: not measured in the %s arm" % (label, " and ".join(a for a in needed if a not in rate)))
        elif gate.get("guard"):
            missed += ["%s: failed in the %s arm (%d of %d passed; every run must pass)" % (
                label, a, cells[a]["pass"], cells[a]["n"]) for a in needed if rate[a] < 1]
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
    p.add_argument("--runs", type=int, default=3, help="runs per case and arm (default 3; use 5 for a release)")
    p.add_argument("--model", default="sonnet", help='model alias or id; "default" uses your configured model')
    p.add_argument("--cases", default="", help="comma-separated case ids (default: all)")
    p.add_argument("--arms", default="with,without")
    p.add_argument("--jobs", type=int, default=4, help="sessions run at the same time")
    p.add_argument("--out", default="", help="result file (default: evals/results/<version>.json)")
    p.add_argument("--add", action="store_true", help="add these runs to the existing result file for the same plugin text and model")
    p.add_argument("--keep", action="store_true", help="keep each run's project and transcripts under evals/runs/")
    a = p.parse_args()
    out = a.out or os.path.join(HERE, "results", version() + ".json")
    cases = load_cases([c for c in a.cases.split(",") if c])
    arms = [arm for arm in ARMS if arm in a.arms.split(",")]
    if not cases or not arms or a.runs < 1:
        sys.exit("nothing to run: check --cases, --arms and --runs")
    files, rows = plugin_files(), {}
    if a.add:
        with open(out, encoding="utf-8") as f:
            old = json.load(f)
        if old["files"] != files or old["model"] != a.model:
            sys.exit("--add needs a result file made with this exact plugin text and model: " + out)
        rows = {c["id"]: c["detail"] for c in old["cases"]}
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
    if plugin_files() != files:
        sys.exit("the plugin files changed while the suite was running: nothing written, run it again")
    version_text = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    result = {"vibe_version": version(), "date": datetime.date.today().isoformat(), "claude_code": version_text,
              "model": a.model, "runs": a.runs, "files": files, "cases": [summarise(k, rows[k]) for k in sorted(rows)]}
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=1) + "\n")
    text, missed = table(load_cases(), {c["id"]: c for c in result["cases"]})
    total = sum(r["cost"] for case_rows in rows.values() for r in case_rows)
    print("\nVibe %s, %s, model %s (pass counts: runs that passed / runs counted)\n%s" % (result["vibe_version"], version_text, a.model, text))
    print("\nTotal cost of all runs in this file: $%.2f. Result written to %s" % (total, out))
    print("Gates missed:\n  " + "\n  ".join(missed) if missed else "All gates met for the cases in this file.")
    broken = sum(sum(c["errors"].values()) for c in result["cases"])
    if broken:
        print("%d run(s) broke and were left out of the counts; see \"error\" in the result file." % broken)
    sys.exit(1 if missed or broken else 0)


if __name__ == "__main__":
    main()
