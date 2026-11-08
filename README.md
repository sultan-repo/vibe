# Vibe

**v4.8.0:** durable session handoffs and automatic startup context, with focused checks, automatic model effort and useful parallel work.

A lightweight delivery layer for [Claude Code](https://code.claude.com). Vibe coordinates approved work, uses focused evidence while building, and checks the complete result at the agreed milestone.

Default: **understand → build → verify → deliver**. Discover and Reassess are invoked when needed, not for every change.

**Describe the outcome in normal conversation.** Vibe chooses the workflow, delegates useful independent work and performs the appropriate checks automatically. Slash commands are optional shortcuts.

Vibe uses **Claude only**. There are no external reviewer CLIs, sign-in requirements or model-specific reviewer settings.

## How it works

- **Always-on core** (`core/CLAUDE.md`): automatic workflow selection, Fast / Standard / Critical routing, concise communication, appropriate evidence and git safety.
- **`discover`**: explore unresolved product decisions or an explicitly requested design; skip it when implementation is already clear.
- **`build`**: complete approved work continuously with affected tests and minimal documentation. Full suites, production builds and browser matrices are not repeated after every edit, worker or ordinary push.
- **`reassess`**: validate the integrated outcome at a major milestone or delivery boundary, reusing current evidence. Independent **Claude review** is reserved for affected high-risk behavior or an explicit request.
- **Parallel work**: the coordinator assigns ready, independent tasks to native Claude subagents and verifies the combined result. No separate parallel command or agent-team setup is required.
- **Model effort**: native low/medium/high controls match the current work. Routine workers default to medium; consequential reviews default to high. No separate classifier agent or global settings rewrite.
- **Safety**: the force-push hook denies shared-history rewrites and fails closed when validation is unavailable.
- **Optional visual board**: a Claude Code Mod shows the plan, reported task completion and current activity in a native pane. No separate server or continuous model polling.

### Automatic effort selection

| Current work | Requested effort |
| --- | --- |
| Bounded mechanical edits | Low |
| Routine implementation and exploration | Medium |
| Difficult debugging, architecture and consequential invariants | High |

Build, Discover and Reassess use native `effort: medium` frontmatter. After loading a workflow, the coordinator can select a different level through three tiny internal skills, hidden from the user command menu. The medium control also lets it return from harder reasoning without reloading a workflow. Short answers do not incur an extra routing call. A problem that remains unresolved can justify escalation; a slow build alone cannot.

The scoped worker inherits the model and defaults to medium. Supported non-fork invocations can override effort per assignment (Claude Code 2.1.292+). The reviewer defaults to high for consequential work. Explicit owner choices and host/environment limits still apply; Vibe does not change the model or saved global settings just to lower effort.

These are [native skill controls](https://code.claude.com/docs/en/model-config#adjust-effort-level) and [subagent controls](https://code.claude.com/docs/en/sub-agents#choose-an-effort-level), not instructions to merely think less. Skill overrides last for the current turn. Reading the files as a fallback does not activate them. The coordinator confirms effective settings from available runtime metadata when adopting or diagnosing; unsupported or forced settings remain a disclosed limitation. Effective effort in the owner's cloud host and resulting speed/quality still need observation in a real run.

### Verification and review cadence

| Event | What happens |
| --- | --- |
| Small fix | Focused evidence for the changed behavior; no mandatory plan or reviewer |
| Normal approved increment | Affected tests and useful lint/type checks; targeted browser/build checks only when the change needs them |
| Major milestone | Full relevant checks and end-to-end journeys once on the final integrated candidate; no automatic reviewer for low-risk work |
| High-risk PR before merge | One consolidated fresh-context Claude review of the final commit and applicable invariants |
| Release/deployment | Require full evidence, reuse a valid milestone run; independent review only for affected high-risk behavior |
| Explicit independent review request | One review of the requested scope |

A final gate allows **one full review and at most one targeted recheck** of required fixes. If issues remain, Vibe stops and reports the blocker or required decision instead of launching an endless loop. A passing review on the exact same HEAD and unchanged scope can be reused. An unverified acceptance criterion or a required security/data defect still blocks release or high-risk merge approval.

High-risk means the actual changed behavior: auth/authorization, identity/security verification, consent, personal data, privacy/deletion, payments, migrations, destructive actions, production configuration, delivery controls or consequential concurrency. A performance/refactor label does not exempt these risks. Test relevant invariants early; do not postpone them to an unrelated milestone.

A major milestone is an agreed usable feature or delivery boundary, not every task or branch. The coordinator defines it in the existing plan. Intermediate work can be implemented with focused checks while milestone E2E remains explicitly pending. Existing project and required CI rules still take precedence.

### Reuse checks, avoid ceremony

Fast work uses the core directly. Larger work loads only relevant references and changed sections, shares concise worker briefs and updates existing records at meaningful boundaries. No new scheduler, mandatory register or continuous model polling is added.

For projects already repeating a gate in verification, push and release scripts, Vibe ships an optional [verification cache and pre-push pattern](hooks/verification-cache.md). The coordinator adapts it to existing project hooks and declared inputs. It matches the actual pushed trees and full/quick mode, requires clean stable inputs, and keeps full evidence from being replaced by a later quick pass. It does not bypass CI or independent-review approval. The helper is not an always-on Claude hook and adds no work to ordinary sessions.

Finalize tracked changes before the full gate and store its evidence outside tracked files. A stack gets one final integration gate only when lower branches cannot deploy independently; use a separate release promotion or one integrated delivery. Merging in quick succession does not create that guarantee.

### Automatic parallel work

For substantial work, Vibe decides which agents the task needs, gives each a suitable role, scope and effort, and launches as many ready independent assignments as are useful. There is no preset team size, starting count or Vibe-imposed numeric ceiling. The task, available resources, existing usage constraints and Claude environment determine the group, without an artificial ramp-up or a user command. Small fixes and tightly coupled work stay with the coordinator. Shared API/schema decisions, conflicting edits and shared-resource mutations remain sequential.

All active workers share one coordinator-managed budget, including any nested workers. Vibe adjusts assignments as tasks finish or become ready, and scales back when shared-resource waits or coordination outweigh the benefit. It uses existing progress reports instead of extra monitoring agents or polling. Host limits still apply; more workers do not mean more review or full-check cycles.

Each worker gets a concise objective, file ownership, interfaces and focused checks. Before assignment, the coordinator checks whether worktrees can actually build and run browser checks, then budgets shared checkout/port/database capacity. Install dependencies per worktree or use another complete checkout when needed; serialize only constrained stages. Workers return results and decision text; the coordinator owns shared logs, integration and milestone verification.

Performance work gets a fixture, target device profiles, success threshold, cycle/time budget and a stop condition. Reuse each candidate's production build across measurements. Iterate on a representative profile and validate the target profiles at the end; mobile-specific problems need mobile evidence early. Report and replan when the budget is exceeded.

When native delegation is unavailable, Vibe proceeds sequentially without asking you to configure agents. Parallel work can consume more Claude usage; speed improvements are not claimed without a representative runtime measurement. Detailed execution rules live in [Build's parallel-work reference](skills/build/references/parallel-work.md).

### Execution modes

| Mode | When | Default behavior |
| --- | --- | --- |
| **Fast** | Small or bounded, clear, reversible work | Implement and run relevant checks; no checkpoint or register |
| **Standard** | Features and multi-step work with understood scope | Brief internal plan, build continuously, verify at the end |
| **Critical** | Security, personal data, payments, migrations, destructive or other high-risk work | Clarify material risks, test invariants, preserve required review gates |

### Progress anyone can follow

User updates default to **2–5 plain-language lines**, like a colleague updating a nontechnical owner. Vibe uses the user's language and explains the useful result, what it is working on, what comes next and any decision needed. It reports meaningful progress and delays without narrating every action or asking the owner to manage the work.

For example:

> The family search now finds people by name. I'm checking that it also works well with larger family trees. Next, I'll finish the phone layout.

When a decision matters:

> I need your choice on who can see phone numbers. I recommend keeping them private unless the person agrees to share them.

When work is finished but not yet published:

> The update is finished and the main journeys have been checked. It's ready to publish, but people using the site won't see it yet.

These examples describe only outcomes actually established by the available evidence. Task and board labels use the same everyday language. Commands, file paths, worker coordination, test counts and technical IDs such as M1 and R-01 stay in details unless requested or needed for a decision. Vibe explains problems by their impact, keeps uncertain results explicit and does not invent percentages or completion times. Progress reporting adds no agents, tests or continuous polling.

GitHub gets the same treatment. Commit and PR titles describe the actual change (`Improve Premium subscription page`), not `R-73 R-74: M7`. Keep requirement IDs in commit bodies and PR descriptions for traceability. Branch names describe their purpose (`feature/premium-page`). These defaults apply to new work and do not rename existing commits.

## Visual progress board (optional)

The plugin includes a native Claude Code Mod for interactive terminal sessions and supported graphical Code views. It opens automatically when Claude creates a tracked plan, so no command is needed. Close the pane whenever you want; it will not force itself open again that session. `/vibe-board` remains an optional shortcut to reopen it. Task statuses are **reported progress**, not proof of passing tests or a live worker-process monitor.

- Prefers existing `TodoWrite` or `TaskCreate`/`TaskUpdate`/`TaskList` task events. The coordinator owns shared progress updates. A small deferred `mcp__vibe__progress` tool can supply a plan in sessions without those tools, for Standard/Critical multi-step work only.
- Fast fixes do not generate extra progress reports. The mod observes tool activity without changing permission decisions, model prompts, or tool results.
- The default view uses simple progress wording and factual step counts. Technical activity stays in Details, and finishing planned steps does not claim the result is checked or available to users.
- Requires Claude Code 2.1.287+ for Mods. Panes work in compatible terminal, Desktop Code tab, and supported newer VS Code extension builds; non-visual sessions simply don't show the pane.
- The alternate `install.sh` path installs skills and hooks, **not** Mods; install Vibe as a Claude Code plugin for the board.
- For local testing: `node --test tests/mod-board.test.mjs`.

## Release verification

Release verification and disclosed limits: [v4.8 verification](docs/RELEASE-4.8.md).

- GitHub Actions runs Node and Python policy tests, mod-unit tests, installer smoke tests and hook safeguards.
- Native validation: `claude plugin validate --strict .`; `claude plugin test .` where supported.
- UI smoke: use `claude --plugin-dir .` in a real interactive Claude Code session and test the board. This cannot be confirmed by headless CI.
- Performance: `node scripts/compare-performance.mjs --dry-run` previews matched tasks. `node scripts/compare-performance.mjs --model sonnet --rounds 3` runs real model comparisons (subscription usage applies).

The v4.8 publisher requires successful checks on the tested main commit. Live Claude execution, interactive UI observations and comparative performance remain explicitly unverified in the [release notes](docs/RELEASE_NOTES_4.8.md). Shorter instructions and fewer default gates are not a measured runtime speedup. Rejected PR #6 remains excluded.

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

**Pick up where you left off.** The coordinator saves the active work, branches, next step and any decision needed in the project's shared status record. It updates when work changes or you mention leaving or starting another session. At startup, Vibe loads the short Now summary automatically and flags possible gaps using local Git information. Both installation methods include this; unchanged conversation turns add no checkpoint work. See the [continuity template](skills/discover/references/register-template.md#docsstatusmd) and [startup behavior](hooks/session-start.md).

## Repository layout

```text
core/CLAUDE.md                     always-on rules
core/PROJECT-CLAUDE.template.md    per-project instructions
skills/discover/                   discover, challenge, enrich, approve
skills/build/                      build and local verification
skills/build/references/           parallel work, high-risk rules and Claude review guidance
skills/reassess/                   alignment and conditional final review gates
skills/effort-{low,medium,high}/    internal native effort controls
agents/worker.md                   scoped worker with medium effort by default
agents/reviewer.md                 fresh-context Claude reviewer
hooks/                             force-push protection; optional verification reuse pattern
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
