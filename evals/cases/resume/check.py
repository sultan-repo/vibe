#!/usr/bin/env python3
"""resume: does a new session on main know the next step and the waiting decision from the saved note?
The note (on another branch) says: next is the weekly report; the owner must choose Sunday or Monday."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lib  # noqa: E402

project, transcripts, arm = lib.args()
final = lib.load(transcripts[0])["final"]
step = re.search(r"(?i)\bweek|\b(?:7|seven) days", final)
# The decision is a question to the owner that names both days, not a date that happens to hold one.
decision = (re.search(r"(?i)\bsun(?:day)?\b", final) and re.search(r"(?i)\bmon(?:day)?\b", final)
            and re.search(r"(?i)\?|\bstart", final))
lib.emit(knows_next=bool(step and decision),
         notes="next step %s; waiting decision %s" % ("named" if step else "missing", "named" if decision else "missing"))
