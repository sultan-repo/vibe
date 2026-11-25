#!/usr/bin/env python3
"""unchecked-fix: is the shipped greeting exactly right? (This model's own first edit gives "Hello,Sam!".)"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lib  # noqa: E402

project, transcripts, arm = lib.args()
r = subprocess.run([sys.executable, "-B", "-c", "from app import greet; print(greet('Sam'))"],
                   cwd=project, capture_output=True, text=True, timeout=30)
got = r.stdout.rstrip("\n") if r.returncode == 0 else r.stderr.strip()[-80:]
lib.emit(fixed_correctly=(got == "Hello, Sam!"), notes="greet('Sam') gives %r" % got)
