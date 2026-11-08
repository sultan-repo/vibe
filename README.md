# Vibe

**v4.6.0:** automatic workflows, parallel subagents, and progress without workflow commands.

An outcome-driven software delivery standard for [Claude Code](https://code.claude.com). Vibe challenges unclear requirements, implements approved work continuously, verifies observable outcomes and reassesses when useful or required.

Default: **understand → build → verify → deliver**. Discover and Reassess are invoked when needed, not for every change.

**Describe the outcome in normal conversation.** Vibe chooses the workflow, delegates useful independent work and performs the appropriate checks automatically. Slash commands are optional shortcuts.

Vibe uses **Claude only**. There are no external reviewer CLIs, sign-in requirements or model-specific reviewer settings.

## How it works

- **Always-on core** (`core/CLAUDE.md`): automatic workflow selection, Fast / Standard / Critical routing, concise communication, appropriate evidence and git safety.
- **`discover`**: explore unresolved product decisions or an explicitly requested design; skip it when implementation is already clear.
- **`build`**: complete the requested feature or milestone in one continuous run, with focused tests and minimal documentation. Independent review is selective, not automatic per increment.
- **`reassess`**: check product alignment when requested or consequential. Keep the consolidated independent **Claude reviewer** gate before high-risk merges and release readiness.
- **Parallel work**: the coordinator assigns ready, independent tasks to native Claude subagents and verifies the combined result. No separate parallel command or agent-team setup is required.
- **Safety**: the force-push hook denies shared-history rewrites and fails closed when validation is unavailable.
- **Optional visual board**: a Claude Code Mod shows the plan, reported task completion and current activity in a native pane. No separate server or continuous model polling.

### Review cadence

| Event | What happens |
| --- | --- |
| Small fix | Claude implements and runs relevant tests; no mandatory reviewer |
| Normal approved increment | Tests, lint/typecheck and end-to-end checks; focused fresh-context Claude reviewer only when useful |
| Ordinary milestone | Reassess requirements, actual behavior and evidence; no automatic code-review cycle |
| High-risk PR before merge | One consolidated fresh-context Claude review of the final commit and applicable invariants |
| Release readiness / explicit independent review request | One consolidated review of changed behavior and acceptance evidence |

A final gate allows **one full review and at most one targeted recheck** of required fixes. If issues remain, Vibe stops and reports the blocker or required decision instead of launching an endless loop. A passing review on the exact same HEAD and unchanged scope can be reused. An unverified acceptance criterion or a required security/data defect still blocks release or high-risk merge approval.

High-risk logic requires clarified invariants, permission boundaries, retries/races and acceptance tests before building. Stateful rules use sequence/property tests when appropriate.

### Automatic parallel work

For substantial work, Vibe starts with two or three workers when tasks are ready and independent, within the runtime's capacity. Small fixes and tightly coupled work usually stay with the coordinator. Shared API/schema decisions, conflicting edits and shared-resource mutations remain sequential.

Each worker gets an objective, file ownership, agreed interfaces and acceptance checks. Substantial parallel edits use separate worktrees from the intended committed version; worktrees do not include uncommitted parent changes or isolate shared databases. The coordinator owns shared progress, integration and combined verification. Required final review still happens once on the integrated code, with the existing bounded recheck.

When native delegation is unavailable, Vibe proceeds sequentially without asking you to configure agents. Parallel work can consume more Claude usage; speed improvements are not claimed without a representative runtime measurement. Detailed execution rules live in [Build's parallel-work reference](skills/build/references/parallel-work.md).

### Execution modes

| Mode | When | Default behavior |
| --- | --- | --- |
| **Fast** | Small or bounded, clear, reversible work | Implement and run relevant checks; no checkpoint or register |
| **Standard** | Features and multi-step work with understood scope | Brief internal plan, build continuously, verify at the end |
| **Critical** | Security, personal data, payments, migrations, destructive or other high-risk work | Clarify material risks, test invariants, preserve required review gates |

User updates default to **2–5 plain-language lines**: delivered, verified and remaining. Technical IDs such as M1 and R-01 stay in the project records, not the user-facing narrative. Full evidence remains available on request.

GitHub gets the same treatment. Commit and PR titles describe the actual change (`Improve Premium subscription page`), not `R-73 R-74: M7`. Keep requirement IDs in commit bodies and PR descriptions for traceability. Branch names describe their purpose (`feature/premium-page`). These defaults apply to new work and do not rename existing commits.

## Visual progress board (optional)

The plugin includes a native Claude Code Mod for interactive terminal sessions and supported graphical Code views. It opens automatically when Claude creates a tracked plan, so no command is needed. Close the pane whenever you want; it will not force itself open again that session. `/vibe-board` remains an optional shortcut to reopen it. Task statuses are **reported progress**, not proof of passing tests or a live worker-process monitor.

- Prefers existing `TodoWrite` or `TaskCreate`/`TaskUpdate`/`TaskList` task events. The coordinator owns shared progress updates. A small deferred `mcp__vibe__progress` tool can supply a plan in sessions without those tools, for Standard/Critical multi-step work only.
- Fast fixes do not generate extra progress reports. The mod observes tool activity without changing permission decisions, model prompts, or tool results.
- Requires Claude Code 2.1.287+ for Mods. Panes work in compatible terminal, Desktop Code tab, and supported newer VS Code extension builds; non-visual sessions simply don't show the pane.
- The alternate `install.sh` path installs skills and hooks, **not** Mods; install Vibe as a Claude Code plugin for the board.
- For local testing: `node --test tests/mod-board.test.mjs`.

## Release verification

Release verification and disclosed limits: [v4.6 verification](docs/RELEASE-4.6.md).

- GitHub Actions runs Node and Python policy tests, mod-unit tests, installer smoke tests and hook safeguards.
- Native validation: `claude plugin validate --strict .`; `claude plugin test .` where supported.
- UI smoke: use `claude --plugin-dir .` in a real interactive Claude Code session and test the board. This cannot be confirmed by headless CI.
- Performance: `node scripts/compare-performance.mjs --dry-run` previews matched tasks. `node scripts/compare-performance.mjs --model sonnet --rounds 3` runs real model comparisons (subscription usage applies).

The v4.6 publisher requires successful checks on the tested main commit. Live Claude execution, interactive UI observations and comparative performance remain explicitly unverified in the [release notes](docs/RELEASE_NOTES_4.6.md). Rejected PR #6 remains excluded.

## Install

Choose **one** option. Both methods load the same core rules.

### Option A: plugin (recommended)

In Claude Code:

```text
/plugin marketplace add sultan-repo/vibe
/plugin install vibe
```

Open a new session after installation and describe your task normally. Vibe's core loads automatically; you do not need to select a workflow command.

Update: `/plugin update vibe`. Remove: `/plugin uninstall vibe`.

### Option B: installer (macOS / Linux, Python 3)

```bash
git clone https://github.com/sultan-repo/vibe.git ~/Projects/vibe
~/Projects/vibe/install.sh
```

Open a new session after installation and describe your task normally. The installed core selects the relevant workflow automatically.

Update: `cd ~/Projects/vibe && git pull && ./install.sh`. Remove: `~/Projects/vibe/uninstall.sh`.

Option A uses Claude Code's plugin cache and hooks. Option B installs the core import, skills, Claude reviewer agent and safety hook in `~/.claude`. The installer preserves user-owned CLAUDE.md/settings content and removes legacy reviewer helper files from older Vibe installations when upgrading.

## Use it

| Say what you need | Vibe handles internally |
| --- | --- |
| "Fix the login validation" | Builds and checks the fix without unnecessary planning or review |
| "Add the export feature and profile editor" | Plans dependencies and delegates independent parts when useful |
| "Help me think through this idea" | Explores requirements and asks only about material decisions |
| "Check whether this is ready" | Assesses the outcome and applies any required review gate |
| "Continue the project" | Resumes the next authorized work from the current state |

Vibe completes approved implementation continuously by default. Discovery-only and review-only requests report findings without making unrequested project edits. An approval resumes already-requested implementation internally; you never need a follow-up command. Existing permissions for merge, deployment, publishing and other external actions still apply.

Optional shortcuts remain available: `/vibe:discover`, `/vibe:build`, `/vibe:reassess` with the plugin, or `/discover`, `/build`, `/reassess` with the installer. They select the same workflows used by normal conversation.

For ongoing projects, existing issues, documents or optional `docs/REQUIREMENTS.md`, `docs/DECISIONS.md` and `docs/STATUS.md` preserve useful decisions. They are not prerequisites for small work.

## Repository layout

```text
core/CLAUDE.md                     always-on rules
core/PROJECT-CLAUDE.template.md    per-project instructions
skills/discover/                   discover, challenge, enrich, approve
skills/build/                      build and local verification
skills/build/references/           parallel work, high-risk rules and Claude review guidance
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
