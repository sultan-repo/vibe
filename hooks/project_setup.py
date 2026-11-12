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
POLICY = """## Vibe project workflow (managed; v4.12.1)
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


LEGACY_FALLBACK = "In Codex, retain the owner instructions from your configured project fallback"
LEGACY_BRIDGE = "Ignore the root CLAUDE.md bridge created by this adoption"


def active_import(text, imports):
    """Recognize standalone imports in prose, never in fenced/indented examples."""
    fence = None
    for line in text.splitlines():
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) +
                            "{" + str(fence[1]) + r",}[ \t]*", line):
                fence = None
            continue
        opening = re.match(r" {0,3}(`{3,}|~{3,})(.*)$", line)
        if opening:
            mark, info = opening.groups()
            if mark[0] != "`" or "`" not in info:
                fence = mark[0], len(mark)
                continue
        if not line.expandtabs(4).startswith("    ") and line.strip() in imports:
            return True
    return False


def rules_state(path):
    """Existence is significant: an empty instruction file can mask a fallback."""
    try:
        data, mode = regular_bytes(path, 131072)
        return data, mode
    except FileNotFoundError:
        return None


def apply_rule_changes(changes):
    """Rollback caught failures; keep private recovery copies if rollback is unsafe.

This is not filesystem-wide atomicity. Abrupt termination can leave a partial
transaction and a private recovery directory; never replay it over owner edits.
"""
    import shutil
    changes = [edit for edit in changes if edit[1] != edit[3]]
    if not changes:
        return False
    states = [rules_state(path) for path, _, _, _ in changes]
    for (path, before, mode, after), state in zip(changes, states):
        expected = before.encode("utf-8")
        if (state is None and before) or (state is not None and state != (expected, mode)):
            raise SetupError("project rules changed during adoption; retry after reconciliation")
        if after is not None and len(after.encode("utf-8")) > 131072:
            raise SetupError("updated project rules exceed the size limit")
    recovery = Path(tempfile.mkdtemp(prefix="vibe-adoption-"))
    attempted, made_dirs = [], []
    keep_recovery = False
    try:
        metadata = []
        for index, ((path, _, mode, after), state) in enumerate(zip(changes, states)):
            if state is not None:
                backup = recovery / f"{index}.before"
                backup.write_bytes(state[0])
                backup.chmod(0o600)
            metadata.append({"path": str(path), "existed": state is not None, "mode": mode,
                             "before": f"{index}.before" if state is not None else None,
                             "after_sha256": hashlib.sha256(after.encode()).hexdigest()
                             if after is not None else None})
        (recovery / "recovery.json").write_text(json.dumps(metadata), encoding="utf-8")
        (recovery / "recovery.json").chmod(0o600)
        for index, ((path, before, mode, after), state) in enumerate(zip(changes, states)):
            if rules_state(path) != state:
                raise SetupError("project rules changed during adoption; retry after reconciliation")
            if path.parent.is_symlink():
                raise SetupError("instruction directory became a symlink; reconcile manually")
            if not path.parent.exists():
                path.parent.mkdir()  # Only the project's .claude directory is ever created.
                made_dirs.append(path.parent)
            attempted.append(index)
            if after is None:
                path.unlink()
            else:
                write_rules(path, before, mode, after)
    except BaseException as error:
        unresolved = []
        for index in reversed(attempted):
            path, before, mode, after = changes[index]
            state = states[index]
            try:
                current = rules_state(path)
                if current == state:
                    continue
                written = (after.encode("utf-8"), mode) if after is not None else None
                if current != written or path.parent.is_symlink():
                    raise SetupError("concurrent edit")
                if state is None:
                    path.unlink()
                else:
                    write_rules(path, after or "", state[1], before)
            except (OSError, SetupError):
                unresolved.append(str(path))
        for directory in reversed(made_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass  # Never delete an owner's newly added files.
        if unresolved:
            keep_recovery = True
            raise SetupError("adoption incomplete; preserve concurrent edits and reconcile " +
                             ", ".join(unresolved) + f" using private recovery copies in {recovery}") from error
        if isinstance(error, (OSError, SetupError)):
            raise SetupError("adoption failed; completed edits rolled back: " + str(error)) from error
        raise
    finally:
        if not keep_recovery:
            shutil.rmtree(recovery)
    return True


def fallback_names(names):
    if names is None:
        raise SetupError("effective Codex fallback order is unknown; the coordinator must supply "
                         "--codex-fallbacks-json from the active configuration before changing instruction routing")
    if not isinstance(names, list) or any(not isinstance(name, str) for name in names):
        raise SetupError("Codex fallback names must be a JSON array of basenames")
    # Reject ambiguous/cross-platform path syntax instead of reading outside root.
    if any(not name or name in (".", "..") or re.search(r"[/\\:\x00-\x1f]", name)
           or name in ("AGENTS.md", "AGENTS.override.md") for name in names):
        raise SetupError("Codex fallback names must be eligible non-reserved basenames")
    return list(dict.fromkeys(names))


def adopt(root, *, codex_fallbacks=None):
    """Add policy without shadowing a native owner instruction source."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise SetupError("project directory is not a directory")
    shared = root / "AGENTS.md"
    claude = policy_path(root)
    before, mode = read_rules(shared)
    override = root / "AGENTS.override.md"
    override_alias = override.is_symlink() and override.resolve() == shared
    override_text, override_mode = ("", 0o644) if override_alias else read_rules(override)
    override_active = override.exists() and not override_alias
    original, permissions = ("", 0o644) if claude.is_symlink() and claude.resolve() == shared else read_rules(claude)
    # Validate all owned markers before any write, including files not selected.
    for text in (before, override_text, original):
        managed_rules(text, START, END, "")
    legacy = LEGACY_FALLBACK in before
    fallback = None
    remove_bridge = False
    if (not shared.exists() or legacy) and not override_active:
        names = fallback_names(codex_fallbacks)
        if legacy and managed_rules(before, START, END, "").strip("\ufeff \t\r\n"):
            raise SetupError("legacy shared policy also contains owner rules; reconcile active instruction "
                             "precedence explicitly before migration")
        # Remove only the exact, still owner-free bridge recorded as generated by 4.12.
        remove_bridge = (LEGACY_BRIDGE in before and claude == root / "CLAUDE.md" and
                         not managed_rules(original, START, END, "").strip("\ufeff \t\r\n") and
                         active_import(original, {"@AGENTS.md", "@./AGENTS.md"}))
        for name in names:
            path = root / name
            if remove_bridge and path == claude:
                continue
            text, file_mode = read_rules(path)
            if path.exists():  # Empty matches still take precedence at project scope.
                fallback = path, text, file_mode
                break
    changes = []
    if fallback:
        # An owner-authored import cannot be silently left pointing to a deleted file.
        owner_claude = managed_rules(original, START, END, "")
        reference = "@AGENTS.md" if claude.parent == root else "@../AGENTS.md"
        if shared.exists() and active_import(owner_claude, {reference, reference.replace("@", "@./", 1)}):
            raise SetupError("owner-written Claude import references legacy AGENTS.md; reconcile before removal")
        path, text, file_mode = fallback
        changes.append((path, text, file_mode, managed_rules(text, START, END, POLICY)))
        if remove_bridge:
            changes.append((claude, original, permissions, None))
        # Keep host-specific owner rules private. Do not copy them into another host's file.
        if remove_bridge or not claude.exists():
            claude = root / ".claude" / "CLAUDE.md"
            if claude.parent.is_symlink():
                raise SetupError(".claude is a symlink; reconcile project rules manually")
            original, permissions = read_rules(claude)
            owner_claude = managed_rules(original, START, END, "")
            if shared.exists() and active_import(owner_claude, {"@../AGENTS.md", "@./../AGENTS.md"}):
                raise SetupError("owner-written Claude import references legacy AGENTS.md; reconcile before removal")
        if claude != path:
            changes.append((claude, original, permissions, managed_rules(original, START, END, POLICY)))
        if shared.exists():
            changes.append((shared, before, mode, None))  # Only owner-free legacy policy reaches here.
        target = path
    else:
        changes.append((shared, before, mode, managed_rules(before, START, END, POLICY)))
        if override_active:
            changes.append((override, override_text, override_mode,
                            managed_rules(override_text, START, END, POLICY)))
        if not (claude.is_symlink() and claude.resolve() == shared):
            reference = "@AGENTS.md" if claude.parent == root else "@../AGENTS.md"
            if START in original or not active_import(original, {reference, reference.replace("@", "@./", 1)}):
                # Put a new bridge before an unclosed example fence, not inside it.
                bridge = managed_rules(original, START, END, reference, prepend=START not in original)
                changes.append((claude, original, permissions, bridge))
        target = shared
    return target, apply_rule_changes(changes)

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
    parser.add_argument("--codex-fallbacks-json", type=json.loads,
                        help="effective Codex project_doc_fallback_filenames; [] only when verified empty")
    args = parser.parse_args()
    try:
        path, changed = adopt(args.project_dir, codex_fallbacks=args.codex_fallbacks_json)
        print(f"Vibe project policy {'updated' if changed else 'already current'}: {path}")
        return 0
    except (OSError, SetupError) as error:
        print(f"Vibe project policy not completed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
