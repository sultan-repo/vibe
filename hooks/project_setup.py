#!/usr/bin/env python3
"""Bounded startup advice and explicit, idempotent project policy adoption.

Inspection never executes project scripts or edits tracked files. Adoption is a
separate coordinator action, only after project edits have been authorized.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time

START = "<!-- vibe:project:start -->"
END = "<!-- vibe:project:end -->"
POLICY = """## Vibe project workflow (managed; v4.12)
Apply installed Vibe principles automatically to authorized work in this project.
Select Discover for material exploration, Build for implementation, and Reassess for assessment or delivery readiness; the user describes outcomes, not workflow commands.
Keep small, understood work on the Fast path. Read detailed skills and references only when needed; do not copy the framework into this repository.
Preserve existing project-specific safeguards, review requirements and permissions. Report contradictory gates; reconcile them only within authorized scope and after validating their replacement.
Use affected checks and targeted browser acceptance during development, expand for shared or uncertain impact, and require full integrated evidence before production delivery. Reuse only matching, sufficient evidence.
Keep native task tracking and the existing canonical project status current at work boundaries. Give concise, outcome-based updates.
This block records policy adoption, not completed hook/CI migration or permission to merge, publish or deploy."""
MAX_FILE = 65536
MAX_TOTAL = 262144
MAX_FILES = 24
MAX_WORKFLOWS = 8
MAX_DEPTH = 3
MAX_SECONDS = 0.5
# Only bounded, repository-relative script references are followed; no shell is evaluated.
SCRIPT = re.compile(r"(?<![\w/.-])(?:\./)?((?:scripts|\.githooks)/[\w./-]+)")
PACKAGE = re.compile(r"\b(?:npm|pnpm|yarn)\s+(?:run\s+)?([\w:.-]+)")


class SetupError(Exception):
    pass


def regular_bytes(path, limit):
    """Do not follow a final symlink, block on a FIFO, or read unlimited input."""
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    if path.is_symlink():
        raise SetupError("symlink requires manual inspection")
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise SetupError("not a regular file")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise SetupError("file exceeds inspection limit")
        return data, stat.S_IMODE(info.st_mode)
    finally:
        os.close(fd)


def policy_path(root):
    direct = root / "CLAUDE.md"
    nested = root / ".claude" / "CLAUDE.md"
    if direct.exists() or direct.is_symlink():
        return direct
    if (root / ".claude").is_symlink():
        raise SetupError(".claude is a symlink; reconcile project rules manually")
    return nested if nested.exists() or nested.is_symlink() else direct


def read_rules(path):
    try:
        before, mode = regular_bytes(path, 131072)
    except FileNotFoundError:
        before, mode = b"", 0o644
    try:
        text = before.decode("utf-8")
    except UnicodeDecodeError as error:
        raise SetupError("project rules are not UTF-8; preserve and reconcile manually") from error
    return text, mode


def managed_rules(text, start_marker, end_marker, block, *, prepend=False):
    """Replace only Vibe-owned text. An empty block removes an existing entry."""
    if text.count(start_marker) != text.count(end_marker) or text.count(start_marker) > 1:
        raise SetupError("ambiguous Vibe markers; preserve and reconcile manually")
    # Keep the managed block's own line endings even when an editor appends
    # owner text with a different newline style later.
    offset = text.index(start_marker) + len(start_marker) if start_marker in text else 0
    first_line = text[offset:].partition("\n")[0]
    newline = "\r\n" if first_line.endswith("\r") else "\n"
    if block:
        block = newline.join((start_marker, block.replace("\n", newline), end_marker))
    if start_marker in text:
        start, end = text.index(start_marker), text.index(end_marker)
        if end < start:
            raise SetupError("reversed Vibe markers; preserve and reconcile manually")
        tail = text[end + len(end_marker):]
        if prepend and not block:
            tail = tail.removeprefix(newline)
        return text[:start] + block + tail
    if not block:
        return text
    if prepend:
        bom = "\ufeff" if text.startswith("\ufeff") else ""
        return bom + block + newline + text[len(bom):]
    separator = "" if not text else (newline if text.endswith(newline) else newline * 2)
    return text + separator + block + newline


def write_rules(path, before, mode, after):
    if before == after:
        return False
    data = after.encode("utf-8")
    if len(data) > 131072:
        raise SetupError("updated rules exceed the size limit")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.chmod(temporary, mode)
        # Never overwrite a concurrently edited or substituted policy file.
        try:
            current, _ = regular_bytes(path, 131072)
        except FileNotFoundError:
            current = b""
        if current != before.encode("utf-8") or path.is_symlink():
            raise SetupError("project rules changed during adoption; retry after reconciliation")
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)
    return True


def adopt(root):
    """Both agents receive the same managed policy. Validate all edits before writing."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise SetupError("project directory is not a directory")
    shared = root / "AGENTS.md"
    claude = policy_path(root)
    before, mode = read_rules(shared)
    # A newly selected AGENTS.md can replace a configured Codex fallback.
    # Record the handoff only for a new shared file, and keep it on later refreshes.
    fallback_prefix = "In Codex, retain the owner instructions from your configured project fallback"
    policy = POLICY
    if not shared.exists() or fallback_prefix in before:
        policy += (f"\n{fallback_prefix}. In project_doc_fallback_filenames order, select the "
                   "first existing regular file with an eligible basename in this directory "
                   "(for example, `CLAUDE.md` when configured). An empty first match still "
                   "takes precedence. Apply its owner-written rules and skip managed imports back to AGENTS.md.")
        new_bridge = "Ignore the root CLAUDE.md bridge created by this adoption when locating the previous fallback."
        if new_bridge in before or (claude == root / "CLAUDE.md" and not claude.exists()):
            policy += " " + new_bridge
    changes = [(shared, before, mode, managed_rules(before, START, END, policy))]
    # At project scope Codex selects an existing override even when empty.
    # At user scope it skips empty files. Mirror just the Vibe
    # block there; owner-authored override rules stay private to that host.
    override = root / "AGENTS.override.md"
    if not (override.is_symlink() and override.resolve() == shared):
        override_text, override_mode = read_rules(override)
        if override.exists():
            changes.append((override, override_text, override_mode,
                            managed_rules(override_text, START, END, POLICY)))
    if not (claude.is_symlink() and claude.resolve() == shared):
        original, permissions = read_rules(claude)
        reference = "@AGENTS.md" if claude.parent == root else "@../AGENTS.md"
        # Keep a user's existing standalone import. Migrate an older managed block in place.
        imports = {reference, reference.replace("@", "@./", 1)}
        # Imports inside Markdown code fences are examples, not Claude instructions.
        prose = re.sub(r"(?ms)^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1[ \t]*\r?$", "", original)
        has_import = any(line.strip() in imports for line in prose.splitlines())
        if START in original or END in original or not has_import:
            bridge = managed_rules(original, START, END, reference)
            changes.append((claude, original, permissions, bridge))
    if any(len(replacement.encode("utf-8")) > 131072 for _, _, _, replacement in changes):
        raise SetupError("updated project rules exceed the size limit")
    changed = False
    for path, previous, permissions, replacement in changes:
        if write_rules(path, previous, permissions, replacement):
            changed = True
    return shared, changed


class Inspection:
    def __init__(self, root):
        self.root = root.resolve()
        self.deadline = time.monotonic() + MAX_SECONDS
        self.sources = {}
        self.fingerprints = {}
        self.total = 0
        self.incomplete = False

    def label(self, path):
        try:
            value = str(path.relative_to(self.root))
        except ValueError:
            value = str(path)
        return value

    def read(self, path, external=False):
        label = self.label(path)
        if label in self.fingerprints:
            return self.sources.get(label, "")
        if len(self.fingerprints) >= MAX_FILES or time.monotonic() > self.deadline:
            self.incomplete = True
            return ""
        try:
            # Effective hook paths may legitimately be outside the repository.
            if not external and not path.resolve().is_relative_to(self.root):
                raise SetupError("path escapes project")
            data, mode = regular_bytes(path, min(MAX_FILE, MAX_TOTAL - self.total))
            self.total += len(data)
            self.fingerprints[label] = [hashlib.sha256(data).hexdigest(), mode]
            text = data.decode("utf-8", errors="replace")
            self.sources[label] = text
            return text
        except FileNotFoundError:
            self.fingerprints[label] = "absent"
        except (OSError, SetupError, ValueError):
            try:
                info = path.lstat()
                detail = [info.st_mode, info.st_size, info.st_mtime_ns]
            except OSError:
                detail = None
            self.fingerprints[label] = ["unreadable-or-limited", detail]
            self.incomplete = True
        return ""

    def script_path(self, name):
        path = self.root / name
        if ".." in Path(name).parts or not path.resolve().is_relative_to(self.root):
            self.incomplete = True
            return None
        return path

    def collect(self):
        # Follow only literal script paths, bounded by depth, bytes, time and count.
        frontier = list(self.sources.values())
        for _ in range(MAX_DEPTH):
            next_frontier = []
            for text in frontier:
                for name in SCRIPT.findall(text):
                    path = self.script_path(name)
                    if path and self.label(path) not in self.fingerprints:
                        source = self.read(path)
                        if source:
                            next_frontier.append(source)
            frontier = next_frontier
            if not frontier:
                break
        if frontier and any(SCRIPT.search(text) for text in frontier):
            self.incomplete = True

    def expand(self, text, scripts, seen=None, depth=0):
        if depth > MAX_DEPTH:
            self.incomplete = True
            return ""
        seen = set() if seen is None else seen
        # Preserve other statements: an evidence-only command cannot hide a second gate.
        lines = text.replace("\\\n", " ").splitlines()
        parts = []
        for line in lines:
            if line.lstrip().startswith("#"):
                continue
            for statement in re.split(r";|&&|\|\|", line):
                if re.search(r"verification-cache\.py\s+(?:check\b|pre-push\b[^;]*--require-evidence\b)", statement):
                    continue
                parts.append(statement)
        text = "\n".join(parts)
        if re.search(r"\b(?:eval|source)\b|\b(?:sh|bash)\s+-c\b|\b(?:make|just|task)\s|^\s*\$", text, re.M):
            self.incomplete = True
        for name in PACKAGE.findall(text):
            key = "package:" + name
            if name in scripts and key not in seen:
                seen.add(key)
                parts.append(self.expand(scripts[name], scripts, seen, depth + 1))
        for name in SCRIPT.findall(text):
            if name not in seen:
                seen.add(name)
                path = self.script_path(name)
                source = self.sources.get(self.label(path), "") if path else ""
                if source:
                    parts.append(self.expand(source, scripts, seen, depth + 1))
                elif path:
                    self.incomplete = True
        return "\n".join(parts)


def display_path(value):
    return re.sub(r"[\x00-\x1f\x7f]", "?", value)[:160]


def broad_check(text):
    for line in text.splitlines():
        if re.search(r"\bplaywright\s+test\b|\bcypress\s+run\b", line):
            # A targeted journey or smoke check is not automatically a conflict.
            if not re.search(r"--(?:grep|project|only-changed|test-list|spec)\b|\.(?:spec|test)\.", line):
                return True
        if re.search(r"--mode(?:=|\s+)full\b|\b(?:verify|test)[\w./-]*\s+--?full\b|:-full\b", line):
            return True
    return False


def inspect_project(git):
    """Return one short advisory on a new/changed bounded configuration snapshot."""
    root = Path(git.cwd)
    inspection = Inspection(root)
    hooks = git.text("rev-parse", "--path-format=absolute", "--git-path", "hooks")
    cache_path = git.text("rev-parse", "--path-format=absolute", "--git-path", "vibe-project-gates.json")
    if not hooks or not cache_path:
        return ""  # No Git repo or exhausted read-only Git budget; no startup dependency.
    policies = ("AGENTS.md", "AGENTS.override.md", "CLAUDE.md", ".claude/CLAUDE.md")
    for name in (*policies, ".claude/settings.json", "package.json"):
        inspection.read(root / name)
    active = []
    for name in ("pre-commit", "pre-push"):
        path = Path(hooks) / name
        text = inspection.read(path, external=True)
        if text and os.access(path, os.X_OK):
            active.append((inspection.label(path), text))
    workflows = []
    directory = root / ".github" / "workflows"
    try:
        if directory.is_symlink() or not directory.resolve().is_relative_to(root.resolve()):
            raise SetupError("workflow directory escapes project")
        # Stop directory traversal even if most entries are not workflows.
        with os.scandir(directory) as entries:
            for index, entry in enumerate(entries):
                if index >= MAX_WORKFLOWS:
                    inspection.incomplete = True
                    break
                if entry.name.endswith((".yml", ".yaml")):
                    path = Path(entry.path)
                    workflows.append((inspection.label(path), inspection.read(path)))
    except FileNotFoundError:
        pass
    except (OSError, SetupError):
        inspection.incomplete = True
    inspection.collect()
    try:
        package = json.loads(inspection.sources.get("package.json", "{}"))
        scripts = package.get("scripts", {})
        if not isinstance(scripts, dict):
            raise ValueError("invalid scripts")
        scripts = {key: value for key, value in scripts.items() if isinstance(value, str)}
    except (ValueError, AttributeError):
        scripts = {}
        inspection.incomplete = True
    notices = []
    for label, text in active:
        if broad_check(inspection.expand(text, scripts)):
            notices.append(display_path(label) + " may run broad verification during commit/push")
    for label in policies:
        for line in inspection.sources.get(label, "").splitlines():
            if (re.search(r"\bfull\b", line, re.I) and re.search(r"\b(?:push|commit)\b", line, re.I)
                    and re.search(r"suite|verif|browser|E2E|tests", line, re.I)
                    and not re.search(r"\b(?:not|never|avoid)\b", line, re.I)):
                notices.append(display_path(label) + " mentions full verification at commit/push")
                break
    for label, text in workflows:
        if broad_check(inspection.expand(text, scripts)):
            notices.append(display_path(label) + " contains broad verification; confirm its triggers")
    if inspection.incomplete:
        notices.append("inspection incomplete (dynamic, unreadable or bounded inputs); inspect relevant configuration during project work")
    fingerprint = hashlib.sha256(json.dumps({
        "inspector": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "hooks": hooks, "sources": inspection.fingerprints, "incomplete": inspection.incomplete,
    }, sort_keys=True).encode()).hexdigest()
    cache = Path(cache_path)
    try:
        data, _ = regular_bytes(cache, 4096)
        if json.loads(data) == {"schema": 1, "fingerprint": fingerprint}:
            return ""
    except (OSError, SetupError, ValueError, TypeError):
        pass
    # Only Git-private bookkeeping changes. Never replace a suspicious cache symlink.
    if not cache.is_symlink():
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=cache.parent, mode="w", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump({"schema": 1, "fingerprint": fingerprint}, stream)
            os.replace(temporary, cache)
        except OSError:
            pass
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)
    if not notices:
        return ""
    return ("Vibe gate advisory: " + "; ".join(notices[:3]) +
            ". Confirm actual scope/deployment before calling this a conflict. "
            "Preserve existing gates until an authorized replacement is validated. "
            "Use Build's testing-policy reference during relevant project work.")[:1200]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("adopt",))
    parser.add_argument("--project-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        path, changed = adopt(args.project_dir)
        print(f"Vibe project policy {'updated' if changed else 'already current'}: {path}")
        return 0
    except (OSError, SetupError) as error:
        print(f"Vibe project policy unchanged: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
