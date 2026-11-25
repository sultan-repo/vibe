#!/usr/bin/env python3
"""Vibe status note reader (SessionStart hook).

Shows Claude the "## Now" block of docs/STATUS.md and shows the owner a one-line
"where things stand" banner. Looks for the note in the folder the session was started
in, then at the top of the Git repository. Only when neither has one does it take the
newest note saved on another branch, and then it says so. Whatever it shortens, it marks.
Read-only: never writes and never follows a link out of the project. Its Git commands
only read saved history and settings, share six seconds, and never fetch (in a partial
clone it does not look on other branches) or run a program the repository's settings name.
Prints nothing when there is nothing to say, and always exits 0.
"""
import json
import os
import re
import subprocess
import sys
import time

NOTE = "docs/STATUS.md"
MAX_LINES, MAX_COLS, MAX_BANNER, MAX_BYTES = 30, 200, 600, 200000
CUT = " [cut: read the file]"
DEADLINE = time.monotonic() + 6  # for all git calls together
BOX = r"\s*(?:[-*]|\d+[.)])\s*\[%s\]"
LABEL = r"\s*[-*]?\s*\**(?:%s)\**\s*:"
GOAL, STEPS, NEXT, WAITING = "Goal", "Steps", r"Next(?: task| step)?", r"Waiting on (?:the )?(?:owner|you)"
QUIET = re.compile(r"(?!.*\?)(?:(?:nothing|none|n/a)\b.*|no|-)?\W*$", re.I)  # nothing to do; a question never is
UNSAFE = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f\u202a-\u202e\u2066-\u2069]")  # control and text-direction characters


def git(*args):
    """Run one git command that only reads. None when it fails or runs out of time (2 seconds, and 6 for all calls together)."""
    left = max(0.05, min(2, DEADLINE - time.monotonic()))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    safe = ("git", "-c", "core.fsmonitor=", "-c", "core.hooksPath=/dev/null", "-c", "log.showSignature=false")
    try:
        r = subprocess.run(safe + args, capture_output=True, encoding="utf-8", errors="replace", timeout=left, env=env)
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


def cut(text, limit, mark):
    """The text, or its first `limit` characters followed by a mark that says it was cut."""
    return text if len(text) <= limit else text[:limit] + mark


def where_saved(here):
    """Whether this folder's note is committed, how long ago, and how many commits were made after it."""
    head = git("show", "HEAD:./" + NOTE)
    if head is None or here.strip() != head.lstrip("\ufeff").strip():  # read() drops a byte-order mark too
        return "this folder, not committed yet", []
    sha, _, age = (git("log", "-1", "--format=%H%x09%cr", "HEAD", "--", NOTE) or "").partition("\t")
    if not sha:
        return "this folder", []
    later = git("rev-list", "--count", sha + "..HEAD") or "0"
    after = "%s commit%s made after this note was saved." % (later, " was" if later == "1" else "s were")
    return "saved " + age, [after] if later != "0" else []


def note_on_another_branch():
    """(text, branch, age) of the newest recent note saved outside this folder's history, or None."""
    partial = git("config", "--get-regexp", r"^(extensions\.partialclone|remote\..*\.(promisor|partialclonefilter))$") or ""
    if any(line.split()[-1].lower() not in ("false", "no", "off", "0") for line in partial.splitlines()):
        return None  # a partial clone would download the note, and Git older than 2.44 ignores GIT_NO_LAZY_FETCH
    newest = git("log", "--branches", "--remotes", "--source", "--since=6.months", "-1",
                 "--format=%H%x09%ct%x09%cr%x09%S", "--", NOTE)
    sha, when, age, ref = ((newest or "").split("\t") + ["", "", ""])[:4]
    if not when.isdigit() or git("merge-base", "--is-ancestor", sha, "HEAD") is not None:
        return None  # none found, or it is in this folder's own history and the note was removed here since
    ours = git("log", "-1", "--format=%ct", "HEAD") or "0"
    if not int(ours) <= int(when) <= time.time() + 300:
        return None  # an older note on an abandoned branch is not news, and a date in the future is not trusted
    branch = UNSAFE.sub("", re.sub(r"^refs/(heads|remotes)/", "", ref))
    return git("show", "%s:./%s" % (sha, NOTE)), cut(branch, MAX_COLS, "..."), age


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
        if re.match(r"#{1,2}(?!#)", line):  # a smaller heading such as "### Goal" belongs to the block
            break
        if line.strip():
            body.append(cut(UNSAFE.sub("", line.rstrip()), MAX_COLS, CUT))
    return body


def field(lines, label):
    """Value after "Label:", or the plain list item on the next line when the label stands alone."""
    for i, line in enumerate(lines):
        m = re.match(LABEL % label + r"\**\s*(.*)", line, re.I)
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
    os.chdir(event.get("cwd") or ".")  # a folder that is gone ends the run quietly, as any error does
    start = os.getcwd()
    top = git("rev-parse", "--show-toplevel")
    here = read(NOTE)
    if here is None and top:
        os.chdir(top)
        here = read(NOTE)
    text, where, branch, facts = here, "this folder", "", []
    if top and here is not None:
        where, facts = where_saved(here)
    elif top:
        found = note_on_another_branch()  # a fresh clone, or the work is on another branch
        if found:
            text, branch, age = found
            where = "branch %s, saved %s; this folder is on another branch and has no note" % (branch, age)
    lines = now_block(text)
    places = [(start, "")] + ([(top, " at the top of the repository")] if top and not os.path.samefile(top, start) else [])
    for folder, place in places:
        for name in ("AGENTS.md", "CLAUDE.md"):
            if "<!-- vibe:project:start -->" in (read(os.path.join(folder, name)) or ""):
                facts.append("%s%s still holds a Vibe 4 managed block (between the vibe:project markers), "
                             "which Vibe no longer uses." % (name, place))
    if not lines:
        facts = [f for f in facts if "Vibe 4" in f]
        if not facts:
            return
    indent = lambda line: len(line) - len(line.lstrip())
    boxes = sorted((l for l in lines if re.match(BOX % "[ xX]", l)), key=indent)
    steps = [l for l in boxes if indent(l) == indent(boxes[0])]  # sub-steps under a step are not counted
    done, total = sum(1 for l in steps if re.match(BOX % "[xX]", l)), len(steps)
    goal, nxt, waiting = field(lines, GOAL), field(lines, NEXT), field(lines, WAITING)
    open_work = bool(lines) and (total > done or not QUIET.match(nxt) or not QUIET.match(waiting))
    shown = lines[:MAX_LINES]
    if len(lines) > MAX_LINES:
        shown.append("[%d more lines: read the file]" % (len(lines) - MAX_LINES))
    if total:
        facts.insert(0, "Counted from the note: done %d of %d steps." % (done, total))
        known = LABEL % "|".join((GOAL, STEPS, NEXT, WAITING))
        # One quiet line, but only when the block holds nothing else that Claude would lose (a question, say).
        if not open_work and all(re.match(BOX % "[xX]", l) or re.match(known, l, re.I) for l in lines):
            shown = ["The last plan in the note is finished: %s" % (goal or "all steps done")]
    title = ["Status note for this project (%s; %s). It records where the work stood; the code is the truth if they differ:" % (NOTE, where)] if lines else []
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(title + shown + facts)}}
    if open_work and event.get("source", "startup") != "compact":
        parts = ["Saved on branch %s, not the one open here" % branch if branch else "", goal,
                 "Done %d of %d" % (done, total) if total else "",
                 "" if QUIET.match(nxt) else "Next: " + nxt,
                 "" if QUIET.match(waiting) else "Waiting on you: " + waiting]
        banner = "Where things stand: " + " | ".join(p.strip().rstrip(".").replace(CUT, "...") for p in parts if p)
        out["systemMessage"] = cut(banner, MAX_BANNER, "...")
    sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
