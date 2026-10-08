# Delivery Standard

An outcome-driven software delivery standard for [Claude Code](https://code.claude.com). It makes Claude discover and challenge requirements before building, keep a traceable requirements register, verify with real evidence, and reassess the product against its objective. Ceremony scales with the size of the work: small fixes go straight to code, substantial features get a one-screen checkpoint first.

Lifecycle: **DISCOVER → CHALLENGE → ENRICH → APPROVE → BUILD → VERIFY → REASSESS**

## What you get

- **Always-on core rules** (about 720 words): how to size work (small / substantial / high-risk), evidence-based verification, when to ask the user and when to decide, fixed continuity files, git discipline.
- **`discover` skill**: requirements discovery, challenge, and enrichment. Produces a one-screen checkpoint with numbered decisions, then seeds `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`, `docs/STATUS.md` and the project CLAUDE.md.
- **`reassess` skill**: product alignment review and definition of done at milestones. Ends with Done, Done with disclosed gaps, or Not done.
- **`reviewer` subagent**: an independent reviewer with a fresh context for high-risk work. Reads and runs checks, never edits.
- **A hook** that denies force-pushes.

## Install

Pick one option. Using both loads the core rules twice.

### Option A: plugin (recommended)

Inside Claude Code:

```
/plugin marketplace add sultan-repo/delivery-standard
/plugin install delivery-standard
```

Open a new session. The skills are `/delivery-standard:discover` and `/delivery-standard:reassess`.

Update with `/plugin update delivery-standard`. Remove with `/plugin uninstall delivery-standard`.

### Option B: install script

For machines without the plugin system, or to reuse the files with other tools. Needs macOS or Linux with `python3`.

```bash
git clone https://github.com/sultan-repo/delivery-standard.git ~/Projects/delivery-standard && ~/Projects/delivery-standard/install.sh
```

Open a new session. The skills are `/discover` and `/reassess`.

Update with `cd ~/Projects/delivery-standard && git pull && ./install.sh`. Remove with `~/Projects/delivery-standard/uninstall.sh`.

### What it changes on your machine

- **Option A**: only Claude Code's plugin list and cache. A SessionStart hook injects `core/CLAUDE.md` into each session; a PreToolUse hook denies force-pushes.
- **Option B**: `~/.claude/delivery-standard.md` plus one import line appended to `~/.claude/CLAUDE.md`; `~/.claude/skills/discover` and `reassess`; `~/.claude/agents/reviewer.md`; `~/.claude/hooks/block-force-push.sh` plus one PreToolUse entry in `~/.claude/settings.json`. The uninstaller reverses exactly this and leaves your other content alone.

## Use it on a project

1. Create the folder, `git init`, open it in Claude Code.
2. Send `/discover` (or `/delivery-standard:discover`) followed by your idea: the problem, the users, the outcome, hard constraints. You get a one-screen checkpoint. Answer the numbered decisions, or say "go with your recommendations". Claude creates the project CLAUDE.md, seeds the three `docs/` files, and starts the first increment on a branch.
3. Day to day, just ask. Small work goes straight to implementation. Substantial work triggers discover on its own, because the core rules say so.
4. Begin later sessions with "continue". Claude reads `docs/STATUS.md` and the git log first.
5. At a milestone or before a release: `/reassess`.
6. Auth, payments, personal data, migrations, and large diffs get the reviewer subagent automatically. You can also ask: "have the reviewer check this".

## Layout

```
core/CLAUDE.md                    always-on rules
core/PROJECT-CLAUDE.template.md   per-project CLAUDE.md template (discover uses it)
skills/discover/                  DISCOVER → CHALLENGE → ENRICH → APPROVE, with reference checklists
skills/reassess/                  alignment review and definition of done
agents/reviewer.md                independent reviewer subagent
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
- Review too expensive: narrow the **High-risk** list.
- Project-specific gates (lint, typecheck, tests after every edit) belong in the project's own `.claude/settings.json` as a `PostToolUse` hook on `Edit|Write`.

## Developing the standard itself

```bash
claude plugin validate --strict .        # manifests, skills, agents
python3 hooks/test-force-push-hook.py    # hook behaviour
```

Test a local checkout for one session without installing it: `claude --plugin-dir /path/to/delivery-standard`.

## Outside Claude Code

Concatenate the layers into one prompt for tools without skills or subagents:

```bash
cat core/CLAUDE.md skills/discover/SKILL.md skills/discover/references/*.md skills/reassess/SKILL.md agents/reviewer.md > delivery-standard-single.md
```

## License

MIT. Fork it, adapt it, and send improvements back as pull requests.
