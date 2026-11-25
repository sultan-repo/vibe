#!/usr/bin/env python3
"""small-fix-short: a one-word fix is right, and its report is short (at most 60 words)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lib  # noqa: E402

project, transcripts, arm = lib.args()
words = len(lib.load(transcripts[0])["final"].split())
code, out, err = lib.tasklog(project, "add", "api", "lots")
lib.emit(short_report=0 < words <= 60,
         fixed_correctly=err.strip() == "add needs a project and a positive whole number of minutes",
         notes="%d words; message now %r" % (words, err.strip()[:90]))
