#!/usr/bin/env python3
"""pause-note: a usable docs/STATUS.md is left behind, and nothing was committed just for the note."""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lib  # noqa: E402

project, transcripts, arm = lib.args()


def git(*argv):
    return subprocess.run(("git",) + argv, cwd=project, capture_output=True, text=True, timeout=30).stdout


path = os.path.join(project, "docs", "STATUS.md")
if os.path.isfile(path):
    note = open(path, encoding="utf-8", errors="replace").read()
else:  # perhaps committed on another branch
    sha = git("log", "--all", "-1", "--format=%H", "--", "docs/STATUS.md").strip()
    note = git("show", sha + ":docs/STATUS.md") if sha else ""
has = {"goal": re.search(r"(?mi)^\W*Goal\b", note), "ticked": re.search(r"\[[xX]\]", note),
       "unticked": re.search(r"\[ \]", note), "next": re.search(r"(?mi)^\W*Next\b", note)}
commits = git("log", "--all", "--format=%H").split()
alone = [c for c in commits if git("show", "--name-only", "--format=", c).split() == ["docs/STATUS.md"]]
lib.emit(note_written=all(has.values()), no_status_only_commit=not alone,
         notes="note %s; missing %s; commits %d; note-only commits %d" % (
             "found" if note else "absent", ",".join(k for k, v in has.items() if not v) or "nothing", len(commits), len(alone)))
