#!/usr/bin/env python3
"""Install Vibe from this checkout and make its workflow available at session start."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "hooks"))
from project_setup import SetupError, managed_rules, read_rules, write_rules

START = "<!-- vibe:codex:start -->"
END = "<!-- vibe:codex:end -->"
ROUTING = """When the vibe:build skill is installed and enabled, apply Vibe to ordinary software requests.
Unless Vibe's delivery standard is already in the session, read ../../core/CLAUDE.md relative to the installed vibe:build SKILL.md directory before starting work. Resolve Vibe resources from that same plugin, not from the user's project.
Handle small fixes directly, use Discover for exploration, Build for implementation and Reassess for readiness. Select the workflow yourself. On resume, read the project's existing status if the startup hook did not supply it. Respect project instructions, permissions and hook trust."""


def local_package(profile, codex, uninstall):
    # Register a stable, private marketplace containing only distributable files.
    # Installing the checkout root also copies .git and untracked user files into
    # the cache. Read-only Git pack files prevent native removal on Windows.
    source = profile / "vibe-local"
    catalog = {"name": "vibe-local", "owner": {"name": "Sultan Alsubaie"},
               "plugins": [{"name": "vibe", "source": "./vibe"}]}
    index = source / ".claude-plugin" / "marketplace.json"
    if source.exists() or source.is_symlink():
        if source.is_symlink() or not index.is_file() or json.loads(index.read_text(encoding="utf-8")) != catalog:
            raise SetupError(f"unrecognized marketplace at {source}")
    listed = subprocess.check_output([codex, "plugin", "marketplace", "list", "--json"])
    registered = next((m for m in json.loads(listed)["marketplaces"] if m["name"] == "vibe-local"), None)
    if registered and Path(registered["root"]).resolve() != source.resolve():
        raise SetupError("vibe-local is registered to a different marketplace")
    if uninstall:
        if source.exists():
            subprocess.run([codex, "plugin", "remove", "vibe@vibe-local"], check=True)
            if registered:
                subprocess.run([codex, "plugin", "marketplace", "remove", "vibe-local"], check=True)
            shutil.rmtree(source)
        return
    if not source.exists():
        index.parent.mkdir(parents=True)
        index.write_text(json.dumps(catalog), encoding="utf-8")
    with tempfile.TemporaryDirectory(dir=source) as temp:
        staging = Path(temp) / "new"
        for directory in (".codex-plugin", "core", "skills", "agents", "hooks"):
            shutil.copytree(ROOT / directory, staging / directory,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copyfile(ROOT / "LICENSE", staging / "LICENSE")
        destination = source / "vibe"
        previous = Path(temp) / "previous"
        if destination.exists():
            destination.rename(previous)
        try:
            staging.rename(destination)
        except OSError:
            if previous.exists():
                previous.rename(destination)
            raise
    subprocess.run([codex, "plugin", "marketplace", "add", "."], cwd=source, check=True)
    subprocess.run([codex, "plugin", "add", "vibe@vibe-local"], check=True)


def release_version(plugin):
    version = (plugin.get("version") or "0").split("-", 1)[0].split("+", 1)[0]
    return tuple(int(part) for part in version.split("."))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    codex = shutil.which("codex.cmd" if os.name == "nt" else "codex") or shutil.which("codex")
    if not codex:
        parser.exit(1, "Install Codex CLI first, then run this installer again.\n")
    profile = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser()
    profile.mkdir(parents=True, exist_ok=True)
    # Codex selects the first nonempty instruction file at user scope.
    files = (profile / "AGENTS.override.md", profile / "AGENTS.md")
    edits = []
    active = None
    for path in files:
        original, mode = read_rules(path)
        if active is None and (original.strip() or path == files[-1]):
            active = path
        block = ROUTING if path == active and not args.uninstall else ""
        updated = managed_rules(original, START, END, block, prepend=True)
        edits.append((path, original, mode, updated))
    # Reuse an enabled native marketplace installation. Its lifecycle stays with
    # the host, while --uninstall removes the profile entry owned by this tool.
    native_plugins = json.loads(subprocess.check_output(
        [codex, "plugin", "list", "--marketplace", "vibe", "--json"]))["installed"]
    native = next((p for p in native_plugins if p.get("pluginId") == "vibe@vibe" and p.get("enabled")), None)
    packaged = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if args.uninstall or (profile / "vibe-local").exists() or not native:
        local_package(profile, codex, args.uninstall)
    elif release_version(native) < release_version(packaged):
        subprocess.run([codex, "plugin", "marketplace", "upgrade", "vibe"], check=True)
        result = subprocess.check_output([codex, "plugin", "add", "vibe@vibe", "--json"])
        if release_version(json.loads(result)) < release_version(packaged):
            raise SetupError(f"the registered vibe marketplace still serves an older build; it needs {packaged['version']}")
    for edit in edits:
        write_rules(*edit)
    if args.uninstall:
        print("Removed the installer-managed Vibe setup.")
    else:
        print("Vibe is ready. Open Codex in your project and describe your task.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, SetupError, subprocess.CalledProcessError) as error:
        sys.exit(f"Vibe setup did not finish: {error}")
