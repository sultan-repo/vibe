#!/usr/bin/env python3
"""ordinary-no-review: an everyday feature gets no independent review, and a full labelled report."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lib  # noqa: E402

project, transcripts, arm = lib.args()
t = lib.load(transcripts[0])
found = lib.labels(t["final"])
reviews = lib.review_count(t["tools"])
lib.emit(no_review=reviews == 0,
         full_report=lib.has_report(t["final"]) and "Not checked" in found,
         notes="reviews %d; labels %s" % (reviews, ",".join(found) or "-"))
