#!/usr/bin/env python3
"""Vibe status note reader (SessionStart hook).

Shows Claude the "## Now" block of docs/STATUS.md and shows the owner a one-line
"where things stand" banner. Reads the copy in this folder when it has unsaved
edits, otherwise the newest committed copy on any branch. Read-only: never
writes, never fetches, exits 0 and prints nothing when there is nothing to say.
"""
import json
import os
import re
import subprocess
import sys

NOTE = "docs/STATUS.md"
MAX_LINES, MAX_COLS = 30, 200


def git(*args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    try:
        r = subprocess.run(("git",) + args, capture_output=True, text=True, timeout=2, env=env)
    except Exception:
        return None
    return r.stdout.rstrip("\n") if r.returncode == 0 else None


def now_block(text, cap=True):
    text = text or ""
    m = re.search(r"(?ms)^## Now[^\n]*\n(.*?)(?=^## |\Z)", text)
    if m:
        body = m.group(1)
    elif re.search(r"(?mi)^\s*(?:[-*]\s*)?(?:goal\s*:|\[[ xX]\])", text):
        body = "\n".join(l for l in text.splitlines() if not l.startswith("#"))  # no "## Now" heading
    else:
        return []
    lines = [l.rstrip()[:MAX_COLS] for l in body.splitlines() if l.strip()]
    return lines[:MAX_LINES] if cap else lines


def field(lines, pattern):
    for line in lines:
        m = re.match(r"\s*[-*]?\s*\**(?:%s)\**\s*:\**\s*(.*)" % pattern, line, re.I)
        if m:
            return m.group(1).strip()
    return ""


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}
    try:
        os.chdir(event.get("cwd") or ".")
    except OSError:
        return
    top = git("rev-parse", "--show-toplevel")
    if top:
        os.chdir(top)
    here = None
    if os.path.isfile(NOTE):
        with open(NOTE, encoding="utf-8", errors="replace") as f:
            here = f.read()
    text, where, facts, n_dirty = here, "this folder", [], 0
    if top:
        head = git("show", "HEAD:" + NOTE)
        newest = git("log", "--branches", "--remotes", "--source", "-1", "--format=%H%x09%cr%x09%S", "--", NOTE)
        if here is not None and (head is None or here.strip() != head.strip()):
            where = "this folder, not committed yet"
        elif newest:
            sha, age, ref = (newest.split("\t") + ["", ""])[:3]
            branch = re.sub(r"^refs/(heads|remotes)/", "", ref)
            if git("merge-base", "--is-ancestor", sha, "HEAD") is None:
                when = lambda rev: int(git("log", "-1", "--format=%ct", rev) or 0)
                other = git("show", sha + ":" + NOTE) if when(sha) >= when("HEAD") else None
                if other:
                    text, where = other, "branch %s, saved %s; this folder is on another branch" % (branch, age)
            else:
                where = "saved " + age
                later = git("rev-list", "--count", sha + "..HEAD")
                if later and later != "0":
                    facts.append("%s commits were made after this note was saved." % later)
        dirty = git("status", "--porcelain", "--untracked-files=no")
        n_dirty = len(dirty.splitlines()) if dirty else 0
    for name in ("AGENTS.md", "CLAUDE.md"):
        try:
            with open(name, encoding="utf-8", errors="replace") as f:
                if "<!-- vibe:project:start -->" in f.read():
                    facts.append("%s still holds a Vibe 4 managed block (between the vibe:project markers), which Vibe no longer uses." % name)
        except OSError:
            pass
    lines, full = now_block(text), now_block(text, cap=False)
    if lines and top and n_dirty:
        facts.append("%d file%s uncommitted changes." % (n_dirty, " has" if n_dirty == 1 else "s have"))
    if not lines and not facts:
        return
    done = sum(1 for l in full if re.match(r"\s*(?:[-*]|\d+[.)])\s*\[[xX]\]", l))
    total = done + sum(1 for l in full if re.match(r"\s*(?:[-*]|\d+[.)])\s*\[ \]", l))
    if total:
        facts.insert(0, "Counted from the note: done %d of %d steps." % (done, total))
    goal = field(lines, "Goal")
    nxt = field(lines, r"Next(?: task)?")
    waiting = field(lines, r"Waiting on (?:owner|you)")
    quiet = lambda value: not value or bool(re.match(r"(nothing|none|no\b|n/a|-)", value, re.I))
    open_work = bool(lines) and (total > done or not quiet(nxt) or not quiet(waiting))
    if lines and total and not open_work:
        lines = ["The last plan in the note is finished: %s" % (goal or "all steps done")]
    head = ["Status note for this project (%s; %s). It records where the work stood; the code is the truth if they differ:" % (NOTE, where)] if lines else []
    context = "\n".join(head + lines + facts)
    if "--plain" in sys.argv:
        print(context)
        return
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}
    if open_work and event.get("source", "startup") != "compact":
        parts = [goal] if goal else []
        if total:
            parts.append("Done %d of %d" % (done, total))
        if not quiet(nxt):
            parts.append("Next: %s" % nxt)
        if not quiet(waiting):
            parts.append("Waiting on you: %s" % waiting)
        if parts:
            line = " | ".join(part.strip().rstrip(".") for part in parts)
            out["systemMessage"] = ("Where things stand: " + line)[:600]
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
