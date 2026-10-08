# Delivery Standard v4.0

The v3.0 "Universal AI Software Engineering & Delivery Standard" master prompt, restructured for Claude Code. Same objective and lifecycle, split into layers so the always-on part stays short and the heavy procedures load only when needed.

```
delivery-standard/
  core/CLAUDE.md                    always-on rules (~720 words)      → ~/.claude/CLAUDE.md
  core/PROJECT-CLAUDE.template.md   per-project facts and objective  → <repo>/CLAUDE.md
  skills/discover/                  DISCOVER→CHALLENGE→ENRICH→APPROVE → ~/.claude/skills/discover/
  skills/reassess/                  alignment review + definition of done → ~/.claude/skills/reassess/
  agents/reviewer.md                independent reviewer, fresh context  → ~/.claude/agents/reviewer.md
  hooks/                            optional deterministic guard (force-push) → ~/.claude/hooks/ + settings.json
  install.sh                        one-command global install (re-runnable)
  CHANGES.md                        what changed from v3.0 and why
```

## Why this split

| Layer | Loaded | Holds |
|---|---|---|
| `~/.claude/CLAUDE.md` | every turn, every project | rules that must apply to every single turn: sizing, verification, approval triggers, continuity files, git |
| skills | only when triggered or `/invoked`; reference files load lazily | multi-step procedures and checklists used a few times per project |
| subagent | spawned on demand with a clean context | the independent review, which cannot be independent inside the main context |
| hooks | run by the harness, cannot be ignored | the few rules that must hold with zero exceptions |
| project CLAUDE.md | every turn in that repo | the objective, commands, conventions (the old PROJECT ASSIGNMENT block) |

The v3.0 prompt was ~4,200 words (~5,700 tokens) on every turn. Most of it applies to a few turns per project. Long always-on instructions dilute attention and get ignored; Anthropic's own guidance for CLAUDE.md is to keep only what would cause mistakes if removed.

## Install (global, one time)

From this folder:

```bash
./install.sh
```

It copies the core to `~/.claude/delivery-standard.md` and adds one import line to `~/.claude/CLAUDE.md`, installs the two skills and the reviewer agent, and registers the force-push hook in `~/.claude/settings.json`. Re-run it after editing the bundle. Keep the bundle itself in a git repo so the standard has history.

## Per project

1. Create the folder, `git init`, open it in Claude Code.
2. `/discover <the idea>`. If there is no CLAUDE.md yet, discover creates it from the template with the agreed objective. Claude produces the checkpoint, you answer the numbered decisions, Claude seeds `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`, `docs/STATUS.md` and starts building.
3. Day to day: just ask. Small work goes straight to implementation. Substantial work triggers `/discover` on its own because the core tells it to.
4. At a milestone or before release: `/reassess`.
5. For high-risk changes Claude spawns the `reviewer` subagent on its own; you can also ask: "have the reviewer check this".

For a team repo where teammates lack the global install, copy `core/CLAUDE.md` into `<repo>/.claude/rules/delivery-standard.md` and the skills into `<repo>/.claude/skills/`, and commit them.

## Using it outside Claude Code

Concatenate the layers into one prompt for tools that have no skills or subagents:

```bash
cat core/CLAUDE.md skills/discover/SKILL.md skills/discover/references/*.md skills/reassess/SKILL.md agents/reviewer.md > delivery-standard-single.md
```

## Tuning

- Too many checkpoints: tighten the **Substantial** definition in `core/CLAUDE.md`.
- Too few questions: move items from "your call" to "Ask me only for".
- Review too expensive: narrow the **High-risk** list; the reviewer runs only for those and on request.
- Project-specific gates (lint, typecheck, tests on every edit): add a `PostToolUse` hook on `Edit|Write` in the repo's `.claude/settings.json`. That is the highest-value hook and it is project-specific, so it is not shipped here.
