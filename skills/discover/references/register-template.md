# Continuity file templates

Create these on first need. Never create a second file for the same purpose. If the project already tracks requirements elsewhere (issues, ADRs, a tasks file), use that and name it in the shared project instructions.

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

Coverage check (run internally during milestone reassessment): every `approved` row has implementation or a disposition; every `implemented` row has acceptance checks; nothing approved disappeared; nothing unapproved was built.

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

Keep `Now` at the top, with at most ten content lines. Replace that summary when state changes; keep necessary resume details and meaningful history below it. Do not append an entry for every turn. Only the coordinator edits this record.

```markdown
# Status

## Now
Updated: <YYYY-MM-DD HH:MM UTC> | <full default-branch baseline SHA>
Position: <current milestone; distinguish built, checked and live>
In progress: <active tasks with exact pushed branch names, or none>
Next task: <one concrete approved action and where to continue>
Waiting on owner: <decision or input needed, or none>

## Resume details
Objective: <one sentence, if not already in project rules>
Branches and partial work: <saved location, completed parts and remaining work>
Blockers: <technical or external blocker and how to unblock>
Known limitations: <accepted, with who accepted>
Final review gate: <not required | pending high-risk merge/release | approved full SHA and scope, plus test/CI evidence>
Deferred: <item, reason>

## History
<Keep relevant milestone, release and handoff entries here, newest first.>
```

`Updated` names the default-branch code baseline the summary describes, not the commit that will contain the summary. Use a full commit SHA. Subsequent commits changing only `docs/STATUS.md` do not make that baseline stale; other documentation changes are not exempt. The startup hook compares locally known Git references only and never fetches. An unfamiliar unmerged branch is a reconciliation hint, not proof that its work is forgotten. When default-branch information is unavailable, it reports that limit.

Keep this record on the project's canonical shared branch, or use its existing authoritative issue tracker and name that source in project CLAUDE.md. A pushed feature branch alone is not a discoverable handoff from a fresh default checkout. Preserve unfinished work on the named remote branches without merging it prematurely. Use existing push/issue permissions and branch rules; if saving remotely is blocked, record the exact gap and tell the owner. Chat may summarize or link the record; scratch, temporary files and unpushed branches cannot be the only copy.

Test of done: a fresh session given only “Continue from docs/STATUS.md” (or the declared tracker) can locate the saved work, understand its state and perform the next approved action. Startup reads only the short summary; the coordinator reads the detailed section when resuming. Tracker-backed projects use their declared source during normal resume, with no network lookup in the startup hook.
