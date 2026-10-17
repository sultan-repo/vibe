# Vibe

An outcome-driven software delivery standard for [Claude Code](https://code.claude.com). It makes Claude discover and challenge requirements before building, keep a traceable requirements register, verify with real evidence, and reassess the product against its objective. Ceremony scales with the size of the work: small fixes go straight to code, substantial features get a one-screen checkpoint first.

Lifecycle: **DISCOVER → CHALLENGE → ENRICH → APPROVE → BUILD → VERIFY → REASSESS**

## What you get

- **Always-on core rules** (about 720 words): how to size work (small / substantial / high-risk), evidence-based verification, when to ask the user and when to decide, fixed continuity files, git discipline.
- **`discover` skill**: requirements discovery, challenge, and enrichment. Produces a one-screen checkpoint with numbered decisions, then seeds `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`, `docs/STATUS.md` and the project CLAUDE.md.
- **`build` skill**: implements the next approved increment, runs tests and user journeys, and uses a focused Claude reviewer for substantial changes when useful. No routine Codex calls for small fixes or normal increments.
- **`reassess` skill**: product alignment at milestones plus **conditional independent reviews** at high-risk pre-merge, release readiness or on explicit request. Normal milestones do not launch Codex.
- **Two-tier reviews**: Claude reviews intermediate substantial changes when worthwhile; optionally choose locally authenticated Codex CLI for consolidated, final independent gates. Review effort follows risk and a read-only helper fails closed on real unverified acceptance gaps.
- **Bounded review**: high-risk rules contract, state-machine tests when applicable, one consolidated Codex review and at most one targeted recheck per gate. Unresolved defects stop the loop and block high-risk merge/release approval.
- **A hook** that denies force-pushes.

## Install

Pick one option. Using both loads the core rules twice.

### Option A: plugin (recommended)

Inside Claude Code:

```
/plugin marketplace add sultan-repo/vibe
/plugin install vibe
```

Open a new session. The skills are `/vibe:discover`, `/vibe:build`, and `/vibe:reassess`.

Update with `/plugin update vibe`. Remove with `/plugin uninstall vibe`.

### Option B: install script

For machines without the plugin system, or to reuse the files with other tools. Needs macOS or Linux with `python3`.

```bash
git clone https://github.com/sultan-repo/vibe.git ~/Projects/vibe && ~/Projects/vibe/install.sh
```

Open a new session. The skills are `/discover`, `/build`, and `/reassess`.

Update with `cd ~/Projects/vibe && git pull && ./install.sh`. Remove with `~/Projects/vibe/uninstall.sh`.

### What it changes on your machine

- **Option A**: only Claude Code's plugin list and cache. A SessionStart hook injects `core/CLAUDE.md` into each session; a PreToolUse hook denies force-pushes.
- **Option B**: `~/.claude/vibe.md` plus one import line appended to `~/.claude/CLAUDE.md`; `~/.claude/skills/discover`, `build`, and `reassess`; `~/.claude/agents/reviewer.md`; `~/.claude/hooks/block-force-push.sh` plus one PreToolUse entry in `~/.claude/settings.json`. The uninstaller reverses exactly this and leaves your other content alone.

## Use it on a project

1. Create the folder, `git init`, open it in Claude Code.
2. Send `/discover` (or `/vibe:discover`) followed by your idea: the problem, the users, the outcome, hard constraints. You get a one-screen checkpoint and no code. Reply with changes as many times as you like; each round revises the checkpoint and the register.
3. Approve by answering the numbered decisions, or say "go with your recommendations". Claude records the decisions and hands off to `build`, which implements the first increment on a branch and reports.
4. Begin every later session with `/build` (or `/vibe:build`). It reads `docs/STATUS.md` and the git log, takes the next approved increment, and stops when it is done. Add "through the milestone" to keep going.
5. Day to day, just ask. Small work goes straight to implementation. Substantial work triggers discover on its own, because the core rules say so.
6. At an ordinary milestone: `/reassess` checks alignment without automatic Codex. Before a high-risk merge or release: `/reassess` performs the required final independent review (or reuses a valid approval for the exact same commit).
7. On first onboarding, Vibe asks whether to use Codex CLI for **final gate reviews**. It remembers the answer in project CLAUDE.md. Claude handles routine code review; Codex does not run on each increment. High-risk code still requires final independent approval before merge. If your chosen final reviewer is unavailable, the gate blocks without silent substitution.

## Codex CLI review (optional)

Choose **Yes** to the one-time reviewer question, install Codex CLI and sign in on the *review machine* (`codex login status`). Vibe uses your current Codex model and selects `medium`, `high`, or `xhigh` reasoning effort per invocation. It does not need or copy your credentials, and does not modify global Codex settings. A model that rejects the selected effort causes an explicit failure, not a silent fallback.

At a pre-merge or release gate, Claude collects all relevant changes into one review brief and commits a clean worktree before invoking the helper. The exact command is in `skills/build/references/review-loop.md`; it uses `codex exec` in read-only mode, requires JSON structured findings, verifies the reviewed commit SHA and only exits successfully with a clean APPROVE verdict. One full Codex review plus at most one targeted recheck is permitted per gate. Test/CI evidence is gathered outside the read-only reviewer. Genuine missing evidence blocks approval; inability to rerun already-verified tests is reported as a non-blocking reviewer limitation. This **does not replace tests, CI, or required GitHub approvals**. The Python 3 helper is bundled in the plugin or installed as `~/.claude/vibe-tools/codex-review.py` using Option B.

## Layout

```
core/CLAUDE.md                    always-on rules
core/PROJECT-CLAUDE.template.md   per-project CLAUDE.md template (discover uses it)
skills/discover/                  DISCOVER → CHALLENGE → ENRICH → APPROVE, with reference checklists
skills/build/                     BUILD → VERIFY, one approved increment per run
skills/reassess/                  alignment review and conditional independent gate
agents/reviewer.md                fresh-context Claude reviewer subagent
scripts/codex-review.py            fail-closed local Codex CLI review helper
scripts/review-result.schema.json  reviewer response contract
skills/build/references/           risk-aware workflow + reviewer brief
hooks/                            hooks.json (plugin), session-start.sh, block-force-push.sh and its tests
.claude-plugin/                   plugin.json and marketplace.json
install.sh / uninstall.sh         Option B
CHANGES.md                        how this grew out of a single 4,200-word master prompt, and why
```

## Why it is split this way

| Layer | Loaded | Holds |
|---|---|---|
| core rules | every turn | only rules that apply to every turn |
| skills | when triggered or invoked; reference files load lazily | multi-step procedures used a few times per project |
| subagent | spawned on demand with a clean context | the independent review |
| hooks | run by Claude Code, cannot be ignored | the one rule that must never be broken |
| project CLAUDE.md | every turn in that repo | objective, commands, conventions |

A single long prompt costs thousands of tokens on every turn and gets ignored in the middle. Keeping the always-on part short and loading the rest on demand is what keeps quality up.

## Tuning

- Too many checkpoints: tighten the **Substantial** definition in `core/CLAUDE.md`.
- Too few questions: move items from "your call" into "Ask me only for".
- Review too expensive: Codex is only triggered at a high-risk pre-merge, release, explicit review request or approved exceptional risk. Claude and tests handle daily development. Do not bypass genuine high-risk gates.
- Project-specific gates (lint, typecheck, tests after every edit) belong in the project's own `.claude/settings.json` as a `PostToolUse` hook on `Edit|Write`.

## Developing the standard itself

```bash
claude plugin validate --strict .        # manifests, skills, agents
python3 hooks/test-force-push-hook.py    # hook behaviour
python3 -m unittest discover -s tests -v # Codex review helper, mocked CLI
```

Test a local checkout for one session without installing it: `claude --plugin-dir /path/to/vibe`.

## Outside Claude Code

Concatenate the layers into one prompt for tools without skills or subagents:

```bash
cat core/CLAUDE.md skills/discover/SKILL.md skills/discover/references/*.md skills/reassess/SKILL.md agents/reviewer.md > vibe-single.md
```

## License

MIT. Fork it, adapt it, and send improvements back as pull requests.
