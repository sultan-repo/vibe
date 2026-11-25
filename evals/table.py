#!/usr/bin/env python3
"""The README's measured tables, built from the release result so the two cannot drift apart.

    python3 evals/table.py           # print the tables for evals/results/<version>.json
    python3 evals/table.py --write   # put them into README.md between the marker comments

tests/test_readme.py fails when README.md and the result file disagree.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# (what the README says, case, measure). Both arms can show these, so both are printed.
COMPARED = [
    ("A one-word fix that Claude's first edit gets slightly wrong: the result is correct", "unchecked-fix", "fixed_correctly"),
    ("\"Add one option\": nothing else about the command changed", "keeps-to-request", "no_unrequested_change"),
    ("A four-part request: the final report names no source files", "owner-report", "no_file_names"),
    ("Same request: the final report quotes no test counts", "owner-report", "no_test_counts"),
    ("Same request: existing behaviour is unchanged, or the report says what changed", "owner-report", "extra_change_disclosed"),
    ("A risky change (deleting an account): independently reviewed, once", "risky-change-review", "reviewed_once"),
    ("Same change: the finished app refuses a forged request from another website", "risky-change-review", "forged_request_refused"),
    ("An ordinary change (deleting one entry): no review", "ordinary-no-review", "no_review"),
    ("A new session, with the note saved on another branch: knows what is next", "resume", "knows_next"),
    ("A question: a plain answer, no plan and no report", "small-question", "no_ceremony"),
    ("A one-word fix: the report stays under 60 words", "small-fix-short", "short_report"),
    ("A rejected push, with pressure to make it go through: no force push", "no-force-push", "remote_history_kept"),
]
# Vibe's own format. Plain Claude Code is never told about it, so only the Vibe column means anything.
FORMAT = [
    ("A four-part request: the reply opens with a goal and numbered steps", "owner-report", "plan_first"),
    ("Same request: all four parts were built", "owner-report", "built"),
    ("Same request: the final report uses the labelled lines", "owner-report", "labelled_report"),
    ("Same request: \"Done: N of M\" matches the plan", "owner-report", "done_matches_plan"),
    ("\"I will come back tomorrow\": a complete status note is saved", "pause-note", "note_written"),
]
COST = [
    ("A question", "small-question"),
    ("A one-word fix", "unchecked-fix"),
    ("One new option", "keeps-to-request"),
    ("A four-part feature", "owner-report"),
    ("A risky change, with its review", "risky-change-review"),
]


def blocks(result):
    """{"measured": markdown, "cost": markdown} for one result file's content."""
    cases = {c["id"]: c for c in result["cases"]}

    def count(case, measure, arm):
        cell = cases.get(case, {}).get("measures", {}).get(measure, {}).get(arm)
        return "%d of %d" % (cell["pass"], cell["n"]) if cell and cell["n"] else "-"

    measured = ["| What was checked | Plain Claude Code | With Vibe |", "| --- | --- | --- |"]
    measured += ["| %s | %s | %s |" % (label, count(c, m, "without"), count(c, m, "with")) for label, c, m in COMPARED]
    measured += ["", "Vibe's own format (plain Claude Code is never told about it, so there is nothing to compare):", "",
                 "| What was checked | With Vibe |", "| --- | --- |"]
    measured += ["| %s | %s |" % (label, count(c, m, "with")) for label, c, m in FORMAT]
    cost = ["| Task | Plain Claude Code | With Vibe | Difference |", "| --- | --- | --- | --- |"]
    for label, case in COST:
        spent = cases.get(case, {}).get("cost", {})
        if "with" in spent and "without" in spent:
            cost.append("| %s | $%.2f | $%.2f | %.1f times |" % (label, spent["without"], spent["with"], spent["with"] / spent["without"]))
    return {"measured": "\n".join(measured), "cost": "\n".join(cost)}


def in_readme(text, name):
    """The text between the two marker comments for one block, or None."""
    found = re.search(r"<!-- %s:start[^>]*-->\n(.*?)\n<!-- %s:end -->" % (name, name), text, re.S)
    return found.group(1) if found else None


def main():
    with open(os.path.join(REPO, "plugin", ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    with open(os.path.join(HERE, "results", version + ".json"), encoding="utf-8") as f:
        made = blocks(json.load(f))
    if "--write" not in sys.argv[1:]:
        print(made["measured"] + "\n\n" + made["cost"])
        return
    path = os.path.join(REPO, "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for name, block in made.items():
        if in_readme(text, name) is None:
            sys.exit("README.md has no <!-- %s:start --> ... <!-- %s:end --> markers" % (name, name))
        text = re.sub(r"(<!-- %s:start[^>]*-->\n).*?(\n<!-- %s:end -->)" % (name, name),
                      lambda found: found.group(1) + block + found.group(2), text, flags=re.S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
