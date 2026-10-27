# Reuse proven lessons and resume without context loss

This is an **on-demand** reference for Build. It does not add a hook, observer, agent, mandatory file, automatic skill generator, or repeated review.

## Resume a substantial project

At session start, check `git status`, recent `git log`, project CLAUDE.md, REQUIREMENTS.md, DECISIONS.md and STATUS.md as the core already requires. Reconcile them with code before acting.

STATUS.md is the *single active handoff*, not a growing journal. When ending an interrupted or incomplete substantial increment, preserve only:
- **Where:** current milestone, approved requirement IDs, branch and HEAD actually checked;
- **Evidence:** last verified command/result and what remains unverified;
- **Blocker:** failed approach worth avoiding, with error/evidence, or `none`;
- **Next:** the exact first approved action and a command to verify it.

Keep STATUS.md under one screen by **replacing stale state**, not appending session logs. Do not claim a saved status matches HEAD without checking. Never save credentials, sensitive user data, chat transcripts or raw tool output in handoff notes.

## Learn only from evidence, not every interaction

`docs/LESSONS.md` is **optional**, project-scoped and created only when a lesson qualifies. Otherwise do not create it.

Promote a concise reusable lesson only when:
1. The same failure/solution recurs in **two independently observed instances**, each with traceable evidence; **or**
2. The project owner explicitly asks to preserve a pattern, and it has been verified in code/tests.

For each lesson record only a **trigger**, **action**, **evidence references** (issue/commit/test), **scope/limits**, and date. Use one short entry per pattern; update an existing entry rather than duplicating. Never auto-promote a project-specific practice to a global instruction. Cross-project reuse requires user approval after the rule proves relevant in another project.

On Build, read only lessons relevant to the present technology/problem after inspecting the actual repository. Treat lessons as *guidance*, never as higher priority than approved decisions, current code, test evidence, or explicit user instructions. If contradicted, correct or retire the lesson rather than repeating an outdated workaround.

Only check lessons at session resume, after a recurring error, or when Reassess detects the same defect again. Do not run learning analysis or write lessons after every edit, commit, or test.
