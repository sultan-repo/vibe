# Vibe v4.13.0 release candidate

Merging to `main` is a production delivery. The owner authorized merge and publication of v4.13.0 after the release gates pass. Complete required evidence before merge. Treat skipped or unavailable checks as pending; a skipped check is not a pass.

## Scope and safety
Owner-controlled governance is shared by Claude Code and Codex. The bounded scanner checks likely conflicts in instruction files and active Git hooks, but does not execute project scripts or change enforcement. Actual applicability must be confirmed by the coordinator, including effective host instructions, CI and deployment boundaries. The owner may align, keep an exception, or defer. Recorded alignment remains pending until project safeguards are reconciled and validated.

Never silently override project safeguards, remove required full delivery tests, install mandatory full per-push gates, introduce slash-command requirements or consume a research agent for governance. A new owner decision is needed only for material unresolved conflicts or changed evidence.

## Before merge
Run the full repository regression suite, force-push and install/uninstall checks, both existing CI job IDs, strict Claude plugin validation and native Codex first-prompt tests. Check read-only scanning, example/managed-block exclusions, actual executable hooks, symlink safety, owner confirmation, decisions, fingerprint invalidation and lack of gate mutation. Check normal conversational routing in fresh Claude and Codex sessions if available; synthetic test passes cannot certify live model adherence. Record unavailable live evidence honestly.

Delivery-control changes require one independent review of the exact final HEAD, with at most one targeted recheck for necessary fixes. Publication uses existing trusted-main guards and must match the tested SHA. No production rollout is authorized by opening this PR.
