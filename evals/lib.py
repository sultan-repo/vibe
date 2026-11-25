"""Shared helpers for the eval checkers and the runner. Standard library only.

A checker is run as:  check.py <project dir> <transcript> [<second transcript>] <arm>
and prints one JSON object: named true/false measures plus a short "notes" string.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

# The labels of the last-message template in plugin/rules.md. Checkers look at the shape
# of a message (which labelled lines it has), never at the wording of the rules.
REPORT = ("Done", "Works now", "Checked", "Live")
FILE_NAME = re.compile(r"(?<![\w/])(?:src|test|tests|bin|lib|data)/[\w./-]+"
                       r"|\b(?!(?i:node)\.js\b)[\w-]+\.(?:js|cjs|mjs|ts|json|py|sh|yml)\b")
NUMBER = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"
          r"|(?:thir|four|fif|six|seven|eigh|nine)teen|twenty|thirty|forty|fifty)")
TESTS = r"(?:\w+\s+)?(?:tests?|checks?|specs?|assertions?)"
# A count of tests with its result: "all 14 tests pass", "ran 14 tests", "14 passed", "14/14".
# "2 test entries" and "3 checks I did by hand" are not test counts.
TEST_COUNT = re.compile(
    r"\b{n}\s+(?:of\s+{n}\s+)?{t}[\s,:]+(?:(?:are|were|all|now|still)\s+)*(?:pass|ran|run|green|succeed|fail)"
    r"|\b(?:ran|run|passed|passing)\s+(?:all\s+)?{n}\s+{t}\b"
    r"|\b\d+\s+(?:of\s+\d+\s+)?(?:passing|passed)\b"
    r"|(?<![\d/-])\d+/\d+(?![\d/-])".format(n=NUMBER, t=TESTS), re.I)
# Saying that an option is now turned away: "refuses unknown options", "an error for an option that does not exist".
OPTION, REFUSED = r"\b(?:option|flag|argument)s?\b", r"(?:refus|reject|error|recogni|not exist|mistyp|ignor)"
OPTION_REFUSED = re.compile(r"{o}.{{0,60}}{r}|{r}.{{0,60}}{o}".format(o=OPTION, r=REFUSED), re.I)


def args():
    """-> (project dir, [transcript paths], arm)"""
    return os.path.abspath(sys.argv[1]), sys.argv[2:-1], sys.argv[-1]


def emit(notes="", **measures):
    print(json.dumps(dict({k: bool(v) for k, v in measures.items()}, notes=str(notes)[:300])))


def load(path):
    """Read one stream-json transcript of the main session (subagent events are skipped).
    "broken" is empty only when the session started and its result event reports plain success."""
    t = {"texts": [], "tools": [], "opening": "", "final": "", "cost": 0.0, "turns": 0, "plugins": [], "model": "",
         "broken": "no result event"}
    started = False
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        kind = e.get("type")
        if kind == "system" and e.get("subtype") == "init":
            started = True
            t["plugins"] = [p.get("source", "") for p in e.get("plugins", [])]
            t["model"] = e.get("model", "")
        elif kind == "assistant" and not e.get("parent_tool_use_id"):
            for part in e.get("message", {}).get("content", []):
                if part.get("type") == "text" and part.get("text", "").strip():
                    t["texts"].append(part["text"])
                    if not t["tools"]:
                        t["opening"] += part["text"] + "\n"
                elif part.get("type") == "tool_use":
                    t["tools"].append((part.get("name", ""), part.get("input") or {}))
        elif kind == "result":
            t["cost"] = e.get("total_cost_usd") or 0.0
            t["turns"] = e.get("num_turns") or 0
            t["final"] = e.get("result") or ""
            if not started:
                t["broken"] = "Claude Code did not start"
            elif e.get("subtype") != "success":
                t["broken"] = str(e.get("subtype"))
            else:
                t["broken"] = "ended with an error" if e.get("is_error") or e.get("api_error_status") else ""
    t["final"] = t["final"] or (t["texts"][-1] if t["texts"] else "")
    return t


def commands(t):
    return [i.get("command", "") for name, i in t["tools"] if name == "Bash"]


def labels(text):
    """Which report labels start a line of the message (bold markers and list dashes allowed)."""
    found = [l for l in REPORT + ("Also changed", "Noticed, not changed", "Next")
             if re.search(r"(?m)^[\s>*-]*%s\**:" % re.escape(l), text)]
    return found + (["Not checked"] if "Not checked:" in text.replace("*", "") else [])


def has_report(text):
    return all(l in labels(text) for l in REPORT)


def plan_steps(opening):
    """Numbered steps under a 'Steps' line of the opening message; [] when there is no Goal + Steps plan."""
    if not re.search(r"(?m)^[\s>*-]*Goal\**:", opening):
        return []
    m = re.search(r"(?ms)^[\s>*]*Steps\**:?\**\s*\n(.*)", opening)
    return re.findall(r"(?m)^\s*\d+[.)]\s+\S.*", m.group(1)) if m else []


def names_a_file(text):
    """True when a message names a source file. A command the owner would type (a backtick span
    with a space in it) may hold one; a bare file name in backticks still counts."""
    return bool(FILE_NAME.search(re.sub(r"`([^`]*)`", lambda m: "" if " " in m.group(1) else m.group(0), text)))


def review_count(tools):
    """How many independent reviews these tool calls asked for: review skills, or else review
    agents. An agent that only explores or plans is not a review, whatever it is called."""
    skills = [i for name, i in tools if name == "Skill" and "review" in str(i.get("skill", "")).lower()]
    agents = [i for name, i in tools if name in ("Agent", "Task") and i.get("subagent_type") not in ("Explore", "Plan")
              and re.search(r"(?i)\breview", " ".join(str(i.get(k, "")) for k in ("subagent_type", "description")))]
    return len(skills) or len(agents)


def tasklog(project, *argv):
    """Run the project's tasklog command against a scratch log holding two entries. -> (exit code, stdout, stderr)"""
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "log.json")
        with open(log, "w") as f:
            json.dump([{"project": "api", "minutes": 90, "note": "auth work"}, {"project": "site", "minutes": 30, "note": ""}], f)
        try:
            r = subprocess.run(["node", os.path.join(project, "bin", "tasklog.js")] + list(argv), capture_output=True,
                               text=True, timeout=30, cwd=tmp, env=dict(os.environ, TASKLOG_FILE=log))
            return r.returncode, r.stdout, r.stderr
        except (OSError, subprocess.SubprocessError) as err:
            return 99, "", str(err)


def unknown_option_still_accepted(project):
    """The seed prints the normal report for `report --bogus` and exits 0. True when that still holds."""
    plain, bogus = tasklog(project, "report"), tasklog(project, "report", "--bogus")
    return plain[0] == 0 and bogus[0] == 0 and bogus[1] == plain[1]
