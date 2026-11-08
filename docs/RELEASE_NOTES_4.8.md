# Vibe v4.8.0

Vibe keeps a short, durable handoff so the next session can find the work already underway and continue with the next approved task.

## What changed

- **Concrete checkpoints:** record the active task and branch before substantial work starts, before ending a turn where work started, finished, was cancelled or became blocked, after every merge/release/deploy, and immediately when the owner mentions a new session, restart, handover or being away.
- **One coordinator-owned record:** commit and push the canonical project status, or update its existing authoritative tracker, under existing permissions. Preserve unfinished work on named remote branches. A handoff kept only in scratch, chat or an unpushed branch is incomplete; disclose a blocked save.
- **A short Now summary:** at most ten content lines covering the update date and code baseline, current position, active work and branches, next task and owner input. Necessary resume details and history stay below it.
- **Automatic startup context:** plugin and manual installations load the project's Now summary when present. The local-only hook can flag an outdated baseline, unknown comparison or unmentioned unmerged branches without loading the full history. Manual startup files live in Vibe's own directory, preserving personal startup scripts and registrations.
- **Useful freshness checks:** saving only the status record does not immediately make it stale. Other documentation changes are not exempt. Branch information is explicitly last known local information, not a live GitHub lookup.
- **Lightweight operation:** no per-turn hook, network request, model call or extra reviewer. Unchanged turns need no status rewrite. Simultaneous changes are combined; checkpointing does not introduce another full product gate.

## Boundaries

Existing project instructions, authorization, hooks and required CI retain precedence. A status-only push can still trigger a project's existing checks; this version does not bypass them or change the verification cache's tree identity. Product verification evidence retains its original scope.

The startup hook reads `docs/STATUS.md`; projects using an issue tracker declare it in project instructions and resume from that source through normal coordination. Startup does not fetch tracker data. Unknown local Git information is reported honestly, and unfamiliar branches are reconciliation hints rather than proof of forgotten work.

No workflow can recover work that was never saved before abrupt termination. Vibe checkpoints earlier and makes persistence failures explicit; it does not promise lossless recovery or measured zero overhead. Updating an installed plugin also does not change an already running session until the updated instructions and hooks are loaded.

## Verification

See [verification details](RELEASE-4.8.md). Publication uses successful trusted main CI, pins the release to that tested commit and adds the source SHA and CI link to the published release. Runtime speed, token savings and the owner's live Claude session have not been benchmarked for this release.
