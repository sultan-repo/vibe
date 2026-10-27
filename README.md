# Vibe

An outcome-driven software delivery standard for [Claude Code](https://code.claude.com). Vibe discovers and challenges requirements, builds one approved increment at a time, verifies observable outcomes, and reassesses against the product's objective.

Lifecycle: **DISCOVER → CHALLENGE → ENRICH → APPROVE → BUILD → VERIFY → REASSESS**

Vibe uses **Claude only**. There are no external reviewer CLIs, sign-in requirements or model-specific reviewer settings.

## How it works

- **Always-on core** (`core/CLAUDE.md`): risk classification, evidence, requirements continuity and git discipline.
- **`discover`**: a one-screen checkpoint of confirmed requirements, missing decisions, tradeoffs and scope; no application code before approval.
- **`build`**: implement the next approved increment, run tests and user journeys, update evidence and commit. A fresh-context Claude reviewer may check meaningful substantial changes; tiny edits do not require repeated review.
- **`reassess`**: review product alignment at milestones. Run a consolidated independent **Claude reviewer** gate before merging high-risk code, declaring a release ready, or on explicit request. Normal milestones do not run a code reviewer automatically.
- **Safety**: the force-push hook denies shared-history rewrites and fails closed when validation is unavailable.
- **Selective learning and recovery**: STATUS.md holds a checked resume anchor for interrupted substantial work. An optional, project-scoped `docs/LESSONS.md` stores repeated proven fixes, not every conversation or edit.
- **Targeted security preflight**: an on-demand checklist examines relevant security-sensitive surfaces at applicable high-risk/release gates, without installing a scanner or adding review rounds.

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

1. In your project, run `/discover` (or `/vibe:discover`) with the idea, intended users, objective and constraints. Approve the checkpoint.
2. `/build` implements the next approved increment, with tests and evidence. Say "through the milestone" to complete approved increments consecutively.
3. Use `/reassess` at milestones to check alignment. Before merging a high-risk change or preparing a release, Reassess runs its required final Claude review and reports a clear readiness verdict.
4. Small day-to-day requests can be made in normal conversation without extra ceremony.

The repository is the memory: `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`, `docs/STATUS.md` (or named equivalents).

## What we adopted from ECC, and what we skipped

Vibe borrows the *principles* of evidence-backed lessons and reliable handoffs from [ECC](https://github.com/affaan-m/ECC) without copying the full memory/runtime system:

- **Lessons** are project-specific, optional and added only after two independently evidenced repeats, or a verified rule explicitly requested by the owner. They are loaded only when relevant. Never auto-promote global rules or store transcripts/secrets.
- **Session recovery** reuses STATUS.md, kept to one screen: checked HEAD, test evidence, important unsuccessful approach, exact next approved step and verification command. No separate session log or memory database.
- **Security preflight** is a conditional checklist at affected high-risk/release gates. It inspects changed paths and existing tests; it is not a secret scanner or a claim of security certification.
- **Specialists**: use a relevant project-installed skill when useful. Vibe does not install packs or spawn additional agents by default.

No new hooks, dependencies, required setup questions, autonomous observers or code-review cycles were added. This design deliberately prioritizes low workflow overhead; reduced errors or time savings should be measured in real project use rather than assumed.


## Repository layout

```text
core/CLAUDE.md                     always-on rules
core/PROJECT-CLAUDE.template.md    per-project instructions
skills/discover/                   discover, challenge, enrich, approve
skills/build/                      build and local verification; optional lessons/handoff reference
skills/build/references/           high-risk rules and Claude review guidance
skills/reassess/                   alignment and conditional final review gates
skills/reassess/references/        risk-scoped security preflight
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
