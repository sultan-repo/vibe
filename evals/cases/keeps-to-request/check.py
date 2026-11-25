#!/usr/bin/env python3
"""keeps-to-request: after adding --json, does `report` still take an unknown option as the seed does?"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lib  # noqa: E402

project, transcripts, arm = lib.args()
code, out, err = lib.tasklog(project, "report", "--json")
try:
    works = code == 0 and json.loads(out) is not None
except ValueError:
    works = False
kept = lib.unknown_option_still_accepted(project)
lib.emit(no_unrequested_change=kept, feature_works=works,
         notes="report --bogus: %s" % ("as before" if kept else "changed: " + lib.tasklog(project, "report", "--bogus")[2].strip()[:120]))
