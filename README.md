# Vibe

**v4.5.0 release candidate:** faster builds, readable updates, and optional native graphical progress.

An outcome-driven software delivery standard for [Claude Code](https://code.claude.com). Vibe challenges unclear requirements, implements approved work continuously, verifies observable outcomes and reassesses when useful or required.

Default: **understand → build → verify → deliver**. Discover and Reassess are invoked when needed, not for every change.

Vibe uses **Claude only**. There are no external reviewer CLIs, sign-in requirements or model-specific reviewer settings.

## How it works

- **Always-on core** (`core/CLAUDE.md`): Fast / Standard / Critical routing, concise communication, appropriate evidence and git safety.
- **`discover`**: explore unresolved product decisions or an explicitly requested design; skip it when implementation is already clear.
- **`build`**: complete the requested feature or milestone in one continuous run, with focused tests and minimal documentation. Independent review is selective, not automatic per increment.
- **`reassess`**: check product alignment when requested or consequential. Keep the consolidated independent **Claude reviewer** gate before high-risk merges and release readiness.
- **Safety**: the force-push hook denies shared-history rewrites and fails closed when validation is unavailable.
- **Optional visual board**: a Claude Code Mod shows the plan, reported task completion and current activity in a native pane. No separate server or continuous model polling.

### Review cadence

| Event | What happens |
| --- | --- |
| Small fix | Claude implements and runs relevant tests; no mandatory reviewer |
| Normal approved increment | Tests, lint/typecheck and end-to-end checks; focused fresh-context Claude reviewer only when useful |
| Ordinary milestone | Reassess requirements, actual behavior and evidence; no automatic code-review cycle |
| High-risk PR before merge | One consolidated fresh-context Claude review of the final commit and applicable invariants |
| Release readiness / explicit review request | One consolidated review of changed behavior and acceptance evidence |

A final gate allows **one full review and at most one targeted recheck** of required fixes. If issues remain, Vibe stops and reports the blocker or required decision instead of launching an endless loop. A passing review on the exact same HEAD and unchanged scope can be reused. An unverified acceptance criterion or a required security/data defect still blocks release or high-risk merge approval.

High-risk logic requires clarified invariants, permission boundaries, retries/races and acceptance tests before building. Stateful rules use sequence/property tests when appropriate.

### Execution modes

| Mode | When | Default behavior |
| --- | --- | --- |
| **Fast** | Small or bounded, clear, reversible work | Implement and run relevant checks; no checkpoint or register |
| **Standard** | Features and multi-step work with understood scope | Brief internal plan, build continuously, verify at the end |
| **Critical** | Security, personal data, payments, migrations, destructive or other high-risk work | Clarify material risks, test invariants, preserve required review gates |

User updates default to **2–5 plain-language lines**: delivered, verified and remaining. Technical IDs such as M1 and R-01 stay in the project records, not the user-facing narrative. Full evidence remains available on request.

GitHub gets the same treatment. Commit and PR titles describe the actual change (`Improve Premium subscription page`), not `R-73 R-74: M7`. Keep requirement IDs in commit bodies and PR descriptions for traceability. Branch names describe their purpose (`feature/premium-page`). These defaults apply to new work and do not rename existing commits.

## Visual progress board (optional)

The plugin includes a native Claude Code Mod for interactive terminal sessions and supported graphical Code views. Run `/vibe-board` to open it, or let it open once when Claude creates a tracked plan. Close the pane whenever you want; it will not force itself open again that session. Task statuses are **reported progress**, not proof of passing tests.

- Prefers existing `TodoWrite` or `TaskCreate`/`TaskUpdate` task events. A small deferred `mcp__vibe__progress` tool can supply a plan in sessions without those tools, for Standard/Critical multi-step work only.
- Fast fixes do not generate extra progress reports. The mod observes tool activity without changing permission decisions, model prompts, or tool results.
- Requires Claude Code 2.1.287+ for Mods. Panes work in compatible terminal, Desktop Code tab, and supported newer VS Code extension builds; non-visual sessions simply don't show the pane.
- The alternate `install.sh` path installs skills and hooks, **not** Mods; install Vibe as a Claude Code plugin for the board.
- For local testing: `node --test tests/mod-board.test.mjs`.

## Release verification

Release checklist: [v4.5 readiness](docs/RELEASE-4.5.md).

- GitHub Actions runs Node and Python policy tests, mod-unit tests, installer smoke tests and hook safeguards.
- Native validation: `claude plugin validate --strict .`; `claude plugin test .` where supported.
- UI smoke: use `claude --plugin-dir .` in a real interactive Claude Code session and test the board. This cannot be confirmed by headless CI.
- Performance: `node scripts/compare-performance.mjs --dry-run` previews matched tasks. `node scripts/compare-performance.mjs --model sonnet --rounds 3` runs real model comparisons (subscription usage applies).

No v4.5 release should be published until real UI observations are recorded and comparative results are measured or explicitly disclosed as unmeasured. Rejected PR #6 is excluded.

## Install

Choose **one** option. Both methods load the same core rules.

### Option A: plugin (recommended)

In Claude Code:

```text
/plugin marketplace add sultan-repo/vibe
/plugin install vibe
```

Open a new session. Skills: `/vibe:discover`, `/vibe:build`, `/vibe:reassess`.

Update: `/plugin update vibe`. Remove: `/plugin uninstall vibe`.

### Option B: installer (macOS / Linux, Python 3)

```bash
git clone https://github.com/sultan-repo/vibe.git ~/Projects/vibe
~/Projects/vibe/install.sh
```

Open a new session. Skills: `/discover`, `/build`, `/reassess`.

Update: `cd ~/Projects/vibe && git pull && ./install.sh`. Remove: `~/Projects/vibe/uninstall.sh`.

Option A uses Claude Code's plugin cache and hooks. Option B installs the core import, skills, Claude reviewer agent and safety hook in `~/.claude`. The installer preserves user-owned CLAUDE.md/settings content and removes legacy reviewer helper files from older Vibe installations when upgrading.

## Use it

1. For clear work, ask Claude to build it or use `/build` (`/vibe:build`). It completes the approved task continuously by default.
2. Use `/discover` when product requirements need exploration or a material choice is unresolved. Do not repeat discovery for an already approved feature.
3. Use `/reassess` when you want an outcome review. High-risk merge and release-readiness gates still require independent review.
4. Fast fixes can be requested in ordinary conversation without extra ceremony.

For ongoing projects, existing issues, documents or optional `docs/REQUIREMENTS.md`, `docs/DECISIONS.md` and `docs/STATUS.md` preserve useful decisions. They are not prerequisites for small work.

## Repository layout

```text
core/CLAUDE.md                     always-on rules
core/PROJECT-CLAUDE.template.md    per-project instructions
skills/discover/                   discover, challenge, enrich, approve
skills/build/                      build and local verification
skills/build/references/           high-risk rules and Claude review guidance
skills/reassess/                   alignment and conditional final review gates
agents/reviewer.md                 fresh-context Claude reviewer
hooks/                             fail-closed force-push protection and tests
.claude-plugin/                    plugin metadata
install.sh / uninstall.sh          alternative installer and cleanup
CHANGES.md                         version history
```

## Developing Vibe

```bash
claude plugin validate --strict .
python3 hooks/test-force-push-hook.py
python3 -m unittest discover -s tests -v
```

Test a checkout in one session using `claude --plugin-dir /path/to/vibe`.

## License

MIT.
