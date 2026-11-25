#!/usr/bin/env python3
"""small-question: a plain question gets a plain answer, with no plan and no labelled report."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lib  # noqa: E402

project, transcripts, arm = lib.args()
t = lib.load(transcripts[0])
plan = lib.plan_steps(t["opening"]) or re.search(r"(?m)^[\s>*-]*Goal\**:", "\n".join(t["texts"]))
found = lib.labels(t["final"])
lib.emit(no_ceremony=not plan and not found,
         notes="plan %s; labels %s; words %d" % ("yes" if plan else "no", ",".join(found) or "-", len(t["final"].split())))
