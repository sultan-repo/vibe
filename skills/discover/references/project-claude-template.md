# <Project name>

## Objective
<The problem, intended users, useful outcome and success measure.>

## Non-goals and constraints
- <Non-goals, stack, compatibility requirements and prohibited actions.>

## Commands (the coordinator runs these)
- Install/run: `<commands>`
- Affected checks: `<feature-specific unit/integration/component and scoped UI/API acceptance tests, lint/type checks>`
- Expanded checks: `<shared consumers, critical invariants and broader regression; full if impact is unbounded>`
- Full release gate: `<complete relevant project suite and end-to-end journeys>`

## Delivery
This project follows Vibe v4.14 with change-aware verification. Normal requests select the workflow; the user does not run workflow commands.
- Progress: short, natural updates for a nontechnical owner in their language. Explain the useful result, current focus, next step and any real decision. Keep engineering details in records; distinguish work finished from checked and available to users.
- Milestones: <usable outcomes; feature completion is not automatically a full-suite trigger>
- During implementation: affected or expanded checks based on cumulative impact and dependencies, no automatic full suite or independent reviewer per package/commit/non-deploying push. Keep cheap broad checks when selection adds overhead.
- Uncertain/shared/high-risk changes: cover affected consumers and critical invariants before merge; zero selected tests for changed behavior is not a pass. Use full relevant checks when impact cannot be bounded.
- Routine feature deployment, including auto-deploying main: affected/expanded checks plus feature-specific acceptance checks and deployment smoke/rollback checks; full E2E is not automatic. Security and data-change invariants still apply.
- Formal production release/promotion: full relevant checks and E2E once on the integrated candidate, including small formal releases; reuse only valid full evidence. Explicit project integration gates still apply. Feature acceptance and release readiness are separate.
- Independent review: affected high-risk behavior or an explicit owner request; low-risk documentation, performance and refactoring do not require it.
- Model effort: Vibe selects native low/medium/high effort by the current work; honor explicit owner choices and host limits. Confirm effective settings from available runtime evidence when adopting, without user commands or global settings changes.
- Deployment boundary: <which actions cause routine production deployment versus formal release/promotion; preserve current required checks and prerequisites>
- Standing permissions: <none, or exact authorized repository/branches/actions/checks/exclusions>
- Existing hooks/CI: <applicable project requirements; preserve them until an authorized replacement is validated>

Test selection uses the integration base, cumulative diff, affected journeys and existing dependency/test information, not filenames alone. Record coverage and deferred full E2E in existing tracking. Validate a new selection mapping with a bounded targeted/full comparison before relaxing an existing project gate; do not repeat that comparison for every feature.

For duplicate verification, the coordinator may adapt Vibe's optional verification-cache helper and pre-push template to the existing gate. Its modes remain quick/full: map affected/expanded selections through a scope-aware adapter and release to full. Reuse requires the actual pushed tree, a clean stable checkout, sufficient coverage, selection base/filters and unchanged declared context. Full includes quick only if the project defines that relationship. Keep full evidence separate; a failed/interrupted rerun invalidates prior evidence for those inputs. Test reuse does not replace required CI or reviewer approval. No owner setup command is needed.

The coordinator applies Vibe's small managed project policy during first authorized editing, without workflow commands. Policy adoption does not certify that hooks/CI were migrated. Prefer optional evidence-only enforcement only after a separate verification path is working; missing evidence still blocks promotion.

## Conventions and continuity
<Only conventions that cannot be inferred from code. Use existing issues/ADRs/tasks; create extra records only when needed.>
Continuity source: <canonical docs/STATUS.md on the shared branch, or the existing authoritative issue/tracker link; omit for one-off work that needs no record>.
The coordinator owns shared decision/status files; workers return their text in reports. Follow the core's start, state-change and handoff triggers, not merges alone. Keep a ten-line Now summary with Updated (date and code baseline), Position, In progress (branches), Next task and Waiting on owner; resume details/history stay below it. Save the record and referenced unfinished work remotely under existing permissions; disclose any gap. A new session must be able to resume from the declared source alone.
Batch simultaneous changes. Finalize tracked edits before the formal release full gate and keep its evidence outside tracked files; later status-only edits need applicable document checks, preserving required hooks/CI. Startup automatically loads docs/STATUS.md's Now block when present and may warn using local Git information; it performs no network lookup. No owner command is needed.
