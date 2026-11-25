#!/usr/bin/env python3
"""Vibe status note reader (SessionStart hook).

Shows Claude the "## Now" block of docs/STATUS.md and shows the owner a one-line
"where things stand" banner. Reads the note in this folder. Only when this folder
has none does it look for the newest note on another branch, and then it says so.
Read-only: never writes, never fetches, never follows a link out of the project.
Prints nothing when there is nothing to say, and always exits 0.
"""
import json
import os
import re
import subprocess
import sys
import time

NOTE = "docs/STATUS.md"
MAX_LINES, MAX_COLS, MAX_BYTES = 30, 200, 200000
BOX = r"\s*(?:[-*]|\d+[.)])\s*\[%s\]"
QUIET = re.compile(r"(nothing|none|no|n/a|-)?\W*$", re.I)
UNSAFE = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f‪-‮⁦-⁩]")


def git(*args):
    """Run one read-only git command; None on any failure. Never fetches or runs repo-configured programs."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    safe = ("git", "-c", "core.fsmonitor=", "-c", "core.hooksPath=/dev/null", "-c", "log.showSignature=false")
    try:
        r = subprocess.run(safe + args, capture_output=True, encoding="utf-8", errors="replace", timeout=2, env=env)
    except Exception:
        return None
    return r.stdout.rstrip("\n") if r.returncode == 0 else None


def read(path):
    """Text of a regular file inside the project, or None. Links are not followed."""
    if os.path.islink(path) or os.path.islink(os.path.dirname(path) or ".") or not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            return f.read(MAX_BYTES)
    except OSError:
        return None


def now_block(text):
    """The non-empty lines under "## Now" (or, with no such heading, from the Goal or first checkbox on)."""
    lines = (text or "").lstrip("\ufeff").splitlines()
    start = next((i + 1 for i, l in enumerate(lines) if re.match(r"## Now\b", l)), None)
    if start is None:
        start = next((i for i, l in enumerate(lines)
                      if re.match(r"[ \t]*(?:(?:[-*]|\d+[.)])[ \t]*)?\**(?:goal\**[ \t]*:|\[[ xX]\])", l, re.I)), None)
    if start is None:
        return []
    body = []
    for line in lines[start:]:
        if line.startswith("#"):
            break
        if line.strip():
            body.append(UNSAFE.sub("", line.rstrip())[:MAX_COLS])
    return body


def field(lines, pattern):
    """Value after "Label:", or the plain list item on the next line when the label stands alone."""
    for i, line in enumerate(lines):
        m = re.match(r"\s*[-*]?\s*\**(?:%s)\**\s*:\**\s*(.*)" % pattern, line, re.I)
        if m:
            value = m.group(1).strip()
            following = lines[i + 1] if i + 1 < len(lines) else ""
            if not value and re.match(r"\s*[-*]\s+\S", following) and not re.match(BOX % "[ xX]", following):
                value = re.sub(r"^\s*[-*]\s*", "", following).strip()
            return value
    return ""


def main():
    try:
        event = json.load(sys.stdin.buffer)
    except Exception:
        event = {}
    try:
        os.chdir(event.get("cwd") or ".")
    except OSError:
        return
    top = git("rev-parse", "--show-toplevel")
    if top:
        os.chdir(top)
    here = read(NOTE)
    text, where, branch, facts = here, "this folder", "", []
    if top and here is not None:
        head = git("show", "HEAD:" + NOTE)
        last = git("log", "-1", "--format=%H%x09%cr", "HEAD", "--", NOTE)
        if head is None or here.strip() != head.strip():
            where = "this folder, not committed yet"
        elif last:
            sha, age = (last.split("\t") + [""])[:2]
            where = "saved " + age
            later = git("rev-list", "--count", sha + "..HEAD")
            if later and later != "0":
                facts.append("%s commit%s made after this note was saved." % (later, " was" if later == "1" else "s were"))
        dirty = git("status", "--porcelain", "--untracked-files=no")
        if dirty:
            n = len(dirty.splitlines())
            facts.append("%d file%s uncommitted changes." % (n, " has" if n == 1 else "s have"))
    elif top:
        # No note in this folder (a fresh clone, or the work is on another branch): newest recent one elsewhere.
        newest = git("log", "--branches", "--remotes", "--source", "--since=6.months", "-1",
                     "--format=%H%x09%ct%x09%cr%x09%S", "--", NOTE)
        sha, when, age, ref = ((newest or "").split("\t") + ["", "", ""])[:4]
        ours = git("log", "-1", "--format=%ct", "HEAD") or "0"  # an older note on an abandoned branch is not news
        if sha and when.isdigit() and int(ours or 0) <= int(when) <= time.time() + 300:
            text = git("show", sha + ":" + NOTE)
            branch = re.sub(r"^refs/(heads|remotes)/", "", ref)
            where = "branch %s, saved %s; this folder is on another branch and has no note" % (UNSAFE.sub("", branch), age)
    lines = now_block(text)
    for name in ("AGENTS.md", "CLAUDE.md"):
        if "<!-- vibe:project:start -->" in (read(name) or ""):
            facts.append("%s still holds a Vibe 4 managed block (between the vibe:project markers), which Vibe no longer uses." % name)
    if not lines:
        facts = [f for f in facts if "Vibe 4" in f]
        if not facts:
            return
    done = sum(1 for l in lines if re.match(BOX % "[xX]", l))
    total = done + sum(1 for l in lines if re.match(BOX % " ", l))
    goal = field(lines, "Goal")
    nxt = field(lines, r"Next(?: task| step)?")
    waiting = field(lines, r"Waiting on (?:the )?(?:owner|you)")
    open_work = bool(lines) and (total > done or not QUIET.match(nxt) or not QUIET.match(waiting))
    shown = lines[:MAX_LINES]
    if total:
        facts.insert(0, "Counted from the note: done %d of %d steps." % (done, total))
        if not open_work:
            shown = ["The last plan in the note is finished: %s" % (goal or "all steps done")]
    head = ["Status note for this project (%s; %s). It records where the work stood; the code is the truth if they differ:" % (NOTE, where)] if lines else []
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(head + shown + facts)}}
    if open_work and event.get("source", "startup") != "compact":
        parts = ["On branch %s" % branch] if branch else []
        parts += [goal] if goal else []
        if total:
            parts.append("Done %d of %d" % (done, total))
        if not QUIET.match(nxt):
            parts.append("Next: %s" % nxt)
        if not QUIET.match(waiting):
            parts.append("Waiting on you: %s" % waiting)
        if parts:
            out["systemMessage"] = ("Where things stand: " + " | ".join(p.strip().rstrip(".") for p in parts))[:600]
    sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
