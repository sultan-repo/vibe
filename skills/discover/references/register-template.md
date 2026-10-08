# Continuity file templates

Create these on first need. Never create a second file for the same purpose. If the project already tracks requirements elsewhere (issues, ADRs, a tasks file), use that and name it in the project CLAUDE.md.

## docs/REQUIREMENTS.md

One row per material requirement, meaning a behavior or constraint that would be a problem if forgotten. Do not register every acceptance detail; put those in the Acceptance cell or in tests.

```markdown
# Requirements register

Objective: <one sentence>
Last reconciled: <date> against commit <sha>

| ID | Requirement | Origin | Priority | Status | Acceptance | Implementation | Evidence |
|----|-------------|--------|----------|--------|------------|----------------|----------|
| R-01 | <observable behavior or constraint> | user / discovery / policy / technical | must / should / could | approved | <how we will know it works> | <files, module, PR> | <test name + run date, or "unverified"> |
```

Field rules:
- **ID**: stable, never reused. R-NN for requirements. Use N-NN for non-functional ones if useful.
- **Origin**: `user` (asked for), `discovery` (found and approved), `policy` (compliance, security, project rule), `technical` (necessary to make another requirement work).
- **Status**: `proposed` → `approved` → `in-progress` → `implemented` → `verified`; or `blocked`, `deferred`, `superseded`. Only `verified` means acceptance was observed to pass on the current code. Record the reason when something becomes `deferred` or `superseded`.
- **Evidence**: the test or check and when it ran, or a short observation. Write `unverified` rather than leaving it blank.

Coverage check (run at milestones, by `/reassess`): every `approved` row has implementation or a disposition; every `implemented` row has acceptance checks; nothing approved disappeared; nothing unapproved was built.

## docs/DECISIONS.md

```markdown
# Decisions

## YYYY-MM-DD: <decision in one line>
Context: <why it came up>
Options: <A, B, C with one-line tradeoffs>
Decision: <what and why>
Consequences: <what this constrains or enables>
```

## docs/STATUS.md

Keep under one screen. Replace, do not append.

```markdown
# Status

Objective: <one sentence>
Milestone: <current milestone and what "done" means for it>
Done so far: <three to six lines>
In progress: <what and where>
Blocked: <blocker and the decision or input needed>
Known limitations: <accepted, with who accepted>
Deferred: <item, reason>
Next approved actions: <numbered>
```
