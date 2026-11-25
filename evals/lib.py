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
FILE_NAME = re.compile(r"(?<![\w/])(?:src|test|tests|bin|lib|data)/[\w./-]+|\b[\w-]+\.(?:js|cjs|mjs|ts|json|py|sh|yml)\b")
TEST_COUNT = re.compile(
    r"\b(?:all\s+)?\d+\s*(?:/\s*\d+\s*)?(?:of\s+\d+\s+)?(?:unit |new |existing )?(?:tests?|checks?|specs?|assertions?)\b"
    r"|\b\d+\s+(?:passing|passed|pass)\b", re.I)


def args():
    """-> (project dir, [transcript paths], arm)"""
    return os.path.abspath(sys.argv[1]), sys.argv[2:-1], sys.argv[-1]


def emit(notes="", **measures):
    print(json.dumps(dict({k: bool(v) for k, v in measures.items()}, notes=str(notes)[:300])))


def load(path):
    """Read one stream-json transcript of the main session (subagent events are skipped)."""
    t = {"texts": [], "tools": [], "opening": "", "final": "", "cost": 0.0, "turns": 0, "plugins": [], "ended": None, "api_error": False}
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        kind = e.get("type")
        if kind == "system" and e.get("subtype") == "init":
            t["plugins"] = [p.get("source", "") for p in e.get("plugins", [])]
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
            t["ended"] = e.get("subtype")
            t["api_error"] = bool(e.get("api_error_status"))
            t["final"] = e.get("result") or ""
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


def review_count(t):
    """How many independent reviews the session asked for: review skills, or else review agents."""
    skills = [i for name, i in t["tools"] if name == "Skill" and "review" in str(i.get("skill", "")).lower()]
    agents = [i for name, i in t["tools"] if name in ("Agent", "Task") and re.search(
        r"(?i)\breview", " ".join(str(i.get(k, "")) for k in ("subagent_type", "description", "prompt")))]
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
