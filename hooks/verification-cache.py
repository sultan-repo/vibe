#!/usr/bin/env python3
"""Optional reuse of a project's full/quick verification; no checks are chosen here."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


class VerificationError(Exception):
    pass


def git(*args):
    result = subprocess.run(["git", *args], text=True, capture_output=True)
    if result.returncode:
        raise VerificationError(result.stderr.strip() or "Git inspection failed")
    return result.stdout.strip()


def snapshot():
    if git("status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
        raise VerificationError("checkout is dirty; verify the intended commit in a clean checkout")
    return git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def context_signature(args):
    if args.context_command:
        result = subprocess.run([args.context_command], text=True, capture_output=True)
        if result.returncode:
            raise VerificationError(f"verification-context command failed (exit {result.returncode})")
        value = result.stdout.strip()
    else:
        value = args.context
    if not value.strip():
        raise VerificationError("verification context is empty")
    return value


@contextmanager
def exclusive(directory):
    lock = directory / "active.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise VerificationError(
            f"verification is active or was interrupted; confirm it has stopped before removing {lock}"
        ) from None
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        lock.unlink(missing_ok=True)


class Evidence:
    def __init__(self, directory, identity, includes_quick):
        self.directory = directory
        self.identity = identity
        self.includes_quick = includes_quick

    def path(self, tree):
        return self.directory / (digest(f"{tree}:{self.identity}".encode()) + ".json")

    def read(self, tree):
        try:
            record = json.loads(self.path(tree).read_text())
            if record["schema"] != 1 or record["tree"] != tree or record["identity"] != self.identity:
                return {}
            passes = record["passes"]
            if not isinstance(passes, dict) or set(passes) - {"quick", "full"}:
                return {}
            for when in passes.values():
                if not isinstance(when, str) or datetime.fromisoformat(when).tzinfo is None:
                    return {}
            return passes
        except (OSError, ValueError, KeyError, TypeError):
            return {}

    def matching(self, tree, mode):
        passes = self.read(tree)
        if mode in passes:
            return mode, passes[mode]
        if mode == "quick" and self.includes_quick and "full" in passes:
            return "full", passes["full"]
        return None

    def forget(self, tree):
        self.path(tree).unlink(missing_ok=True)

    def save(self, tree, passes):
        record = {"schema": 1, "tree": tree, "identity": self.identity, "passes": passes}
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", dir=self.directory, delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(record, stream)
                stream.write("\n")
            os.replace(temporary, self.path(tree))
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)


def pushed_trees():
    trees = set()
    for line in sys.stdin:
        fields = line.split()
        if len(fields) != 4:
            raise VerificationError("malformed pre-push ref update")
        local_ref, local_oid, _, remote_oid = fields
        if not all(re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", oid) for oid in (local_oid, remote_oid)):
            raise VerificationError("malformed pre-push object ID")
        if set(local_oid) == {"0"}:
            if local_ref != "(delete)":
                raise VerificationError("malformed pre-push deletion")
            continue
        # Annotated tags to commits work; blobs/trees require their own project policy.
        commit = git("rev-parse", "--verify", local_oid + "^{commit}")
        trees.add(git("rev-parse", commit + "^{tree}"))
    return sorted(trees)


def verify(args):
    os.chdir(git("rev-parse", "--show-toplevel"))
    trees = pushed_trees() if args.action == "pre-push" else None
    check_only = args.action == "check" or args.require_evidence
    if trees == []:
        return 0  # No source is sent for a deletion-only or empty push.
    directory = Path(git("rev-parse", "--path-format=absolute", "--git-path", "vibe-verification"))
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive(directory):
        context = context_signature(args)
        start = snapshot()
        identity = digest(json.dumps({
            "context": context,
            "context_source": args.context_command,
            "command": args.command,
            "helper": digest(Path(__file__).read_bytes()),
            "full_includes_quick": args.full_includes_quick,
        }, sort_keys=True).encode())
        evidence = Evidence(directory, identity, args.full_includes_quick)
        trees = trees if trees is not None else [start[1]]
        hits = {tree: None if args.fresh else evidence.matching(tree, args.mode) for tree in trees}
        missing = [tree for tree in trees if hits[tree] is None]
        if missing and check_only:
            raise VerificationError(
                "required passing evidence is missing, stale or insufficient; "
                "run verification separately for the intended candidate before retrying"
            )
        if any(tree != start[1] for tree in missing):
            raise VerificationError(
                "a pushed tree has no matching evidence and is not checked out; "
                "the coordinator must verify that ref in a clean checkout first"
            )
        pending = None
        if missing:
            tree = start[1]
            previous = evidence.read(tree)
            # A failed/interrupted fresh attempt must not fall back to an older pass.
            evidence.forget(tree)
            print(f"Vibe verification: running {args.mode} checks for tree {tree[:12]}.", flush=True)
            status = subprocess.run([*args.command, args.mode]).returncode
            if status:
                return status if status > 0 else 1
            previous[args.mode] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            pending = tree, previous
        try:
            if context_signature(args) != context or snapshot() != start:
                raise VerificationError("checkout or verification context changed; no passing evidence retained")
        except (VerificationError, OSError):
            for tree in trees:
                evidence.forget(tree)
            raise
        if pending:
            evidence.save(*pending)
        for tree, hit in hits.items():
            if hit:
                print(f"Vibe verification: reusing {hit[0]} pass for tree {tree[:12]} ({hit[1]}).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "check", "pre-push"))
    parser.add_argument("--mode", required=True, choices=("quick", "full"))
    context = parser.add_mutually_exclusive_group(required=True)
    context.add_argument("--context", help="explicitly immutable nonsecret verification context")
    context.add_argument("--context-command", help="executable returning the input signature, checked before and after")
    parser.add_argument("--full-includes-quick", action="store_true")
    parser.add_argument("--require-evidence", action="store_true",
                        help="pre-push only: reject missing evidence without running the gate")
    parser.add_argument("--fresh", action="store_true", help="invalidate reusable evidence and run again")
    # Split the command explicitly so option parsing does not swallow helper flags.
    argv = sys.argv[1:]
    if "--" not in argv:
        parser.error("provide the project gate adapter after -- (it receives quick/full as its final argument)")
    separator = argv.index("--")
    args = parser.parse_args(argv[:separator])
    if args.require_evidence and args.action != "pre-push":
        parser.error("--require-evidence applies to pre-push; use check for the current candidate")
    if args.fresh and (args.action == "check" or args.require_evidence):
        parser.error("evidence-only checks cannot use --fresh")
    args.command = argv[separator + 1:]
    if not args.command:
        parser.error("a project gate adapter is required")
    try:
        return verify(args)
    except (VerificationError, OSError) as error:
        print(f"Vibe verification stopped: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Vibe verification interrupted; no new pass recorded.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
