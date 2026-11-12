#!/usr/bin/env python3
"""Load a small continuity snapshot using only bounded, read-only local Git calls."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

try:
    from project_setup import inspect_project
except (ImportError, SyntaxError):
    inspect_project = None  # Advisory failure must not suppress core or continuity.


STATUS = "docs/STATUS.md"
FIELDS = ("Updated", "Position", "In progress", "Next task", "Waiting on owner")
MAX_LINES = 10
MAX_LINE_LENGTH = 500
MAX_READ = 16384


class LocalGit:
    def __init__(self, cwd):
        self.cwd = cwd
        self.deadline = time.monotonic() + 2

    def run(self, *args):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            return None
        # A partial clone must not lazily fetch a missing object while inspecting it.
        env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1",
               "GIT_ALLOW_PROTOCOL": "", "GIT_TERMINAL_PROMPT": "0", "GIT_PAGER": "cat"}
        try:
            return subprocess.run(
                ["git", "--no-pager", "-c", "core.fsmonitor=false", "-c", "log.showSignature=false",
                 "-C", str(self.cwd), *args],
                text=True, encoding="utf-8", errors="replace", capture_output=True,
                timeout=remaining, env=env, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None

    def text(self, *args):
        result = self.run(*args)
        return result.stdout.strip() if result is not None and result.returncode == 0 else None


def project_directory():
    try:
        payload = json.loads(sys.stdin.read(MAX_READ)) if not sys.stdin.isatty() else {}
    except (OSError, ValueError):
        payload = {}
    candidate = payload.get("cwd") if isinstance(payload, dict) else None
    for value in (candidate, os.environ.get("CLAUDE_PROJECT_DIR"), os.getcwd()):
        if isinstance(value, str) and Path(value).is_dir():
            return Path(value).resolve()
    return Path.cwd()


def now_block(text):
    """Return only the top summary, never history or an arbitrary legacy record."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == "## Now"), None)
    if start is None:
        return [], {}, ["status has no Now summary"]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    body = lines[start + 1:end]
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    warnings = []
    if len(body) > MAX_LINES or any(len(line) > MAX_LINE_LENGTH for line in body):
        warnings.append("Now summary exceeds its size limit; reconcile the record")
    body = [line[:MAX_LINE_LENGTH] for line in body[:MAX_LINES]]
    fields = {}
    for line in body:
        for key in FIELDS:
            if line.startswith(key + ":"):
                if key in fields:
                    warnings.append("Now summary has duplicate fields")
                fields[key] = line[len(key) + 1:].strip()
    if any(not fields.get(key) for key in FIELDS):
        warnings.append("Now summary is incomplete")
    return ["## Now", *body], fields, warnings


def default_branch(git):
    refs = git.text("for-each-ref", "--format=%(refname)%09%(symref)", "refs/remotes/")
    if refs is None:
        return None
    heads = {}
    for line in refs.splitlines():
        ref, _, target = line.partition("\t")
        if ref.endswith("/HEAD") and target.startswith("refs/remotes/"):
            heads[ref] = target
    return heads.get("refs/remotes/origin/HEAD") or (next(iter(heads.values())) if len(heads) == 1 else None)


def freshness_warnings(git, fields, summary):
    warnings = []
    default = default_branch(git)
    if not default:
        return ["default branch is unknown locally; freshness not checked"]
    tip = git.text("rev-parse", "--verify", default + "^{commit}")
    updated = fields.get("Updated", "")
    match = re.search(r"\|\s*([0-9a-fA-F]{40}|[0-9a-fA-F]{64})\s*$", updated)
    baseline = match.group(1).lower() if match else None
    if not tip or not baseline:
        warnings.append("status baseline is missing or unavailable; freshness not checked")
    elif baseline != tip:
        ancestor = git.run("merge-base", "--is-ancestor", baseline, tip)
        if ancestor is None or ancestor.returncode not in (0, 1):
            warnings.append("status baseline is unavailable locally; freshness not checked")
        elif ancestor.returncode == 1:
            warnings.append("status differs from the last known default branch")
        else:
            # Do not self-invalidate a status-only commit or exempt other documents.
            changed = git.text("log", "--format=%H", "-1", baseline + ".." + tip,
                               "--", ".", ":(exclude)" + STATUS)
            if changed is None:
                warnings.append("status freshness could not be checked locally")
            elif changed:
                warnings.append("status is behind the last known default branch")
    if tip:
        remote = default[len("refs/remotes/"):].split("/", 1)[0]
        refs = git.text("for-each-ref", "--format=%(refname)", "--no-merged=" + tip,
                        "refs/remotes/" + remote + "/")
        if refs is None:
            warnings.append("unmerged branches could not be checked locally")
        else:
            unmentioned = []
            for ref in refs.splitlines():
                if ref == default or ref.endswith("/HEAD"):
                    continue
                branch = ref[len("refs/remotes/" + remote + "/"):]
                pattern = r"(?<![\w./-])(?:" + re.escape(remote) + r"/)?" + re.escape(branch) + r"(?![\w./-])"
                if not re.search(pattern, summary):
                    unmentioned.append(branch)
            if unmentioned:
                names = ", ".join(name[:80] for name in unmentioned[:3])
                more = f" (+{len(unmentioned) - 3} more)" if len(unmentioned) > 3 else ""
                warnings.append("locally known unmerged branches not in Now (check relevance): " + names + more)
    return warnings


def continuity_context(git=None):
    git = git or LocalGit(project_directory())
    root = git.text("rev-parse", "--show-toplevel")
    if root:
        git.cwd = Path(root)
    status = git.cwd / STATUS
    try:
        with status.open(encoding="utf-8", errors="replace") as source:
            text = source.read(MAX_READ)
    except FileNotFoundError:
        return ""
    except OSError:
        return "Vibe continuity warning: docs/STATUS.md could not be read."
    lines, fields, warnings = now_block(text)
    if lines:
        warnings.extend(freshness_warnings(git, fields, "\n".join(lines)))
    output = ["Project continuity: " + STATUS, *lines]
    if warnings:
        output.append("Vibe continuity warning: " + "; ".join(dict.fromkeys(warnings)) + ".")
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", type=Path)
    parser.add_argument("--status-only", action="store_true")
    args = parser.parse_args()
    core = ""
    if args.core and not args.status_only:
        try:
            core = args.core.read_text(encoding="utf-8")
        except OSError:
            pass
    git = LocalGit(project_directory())
    status = continuity_context(git)
    try:
        advisory = inspect_project(git) if inspect_project else (
            "Vibe gate advisory: inspection unavailable; inspect relevant configuration during project work.")
    except Exception:
        # This optional static inspection is never a dependency of session recovery.
        advisory = "Vibe gate advisory: inspection unavailable; preserve existing project protections."
    context = "\n\n".join(part for part in (core, status, advisory) if part)
    if context:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                                 "additionalContext": context}}))


if __name__ == "__main__":
    main()
