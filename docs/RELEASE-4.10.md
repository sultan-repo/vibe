# Vibe v4.10.0 release candidate

Scope: automatic project policy adoption, bounded gate advisories, optional evidence-only promotion enforcement, and removal of the progress board. Existing core verification, native tracking, continuity, review and permission rules remain.

Merging to `main` is a production delivery to plugin users. The owner requested implementation, not a release. Keep this candidate on a feature branch until the owner authorizes delivery and all required evidence is complete.

## Required before merge

1. Identify the exact final PR head, integration base and integrated candidate. Re-evaluate changed inputs or scope rather than reusing stale evidence.
2. Run the complete Python suite, benchmark harness self-test, force-push cases, shell/JSON/YAML checks and isolated install/uninstall smoke. Check both plugin and manual startup paths. Board-only tests are deleted with the component, not skipped. Keep the legacy native-check job ID for branch-protection compatibility.
3. Run strict plugin validation with the repository's pinned Claude Code version. Exercise normal-language routing and automatic policy adoption in an authenticated fresh session; ensure read-only questions make no project edits and the removed board command/tool is absent. An unavailable or skipped check is not a pass. Helper tests cannot certify live model routing, host permissions or project-level defect detection.
4. Obtain one independent fresh-context Claude review of the delivery-control changes on the exact final head. Required fixes get a targeted recheck, not repeated full review loops. Local test reuse does not replace exact-HEAD review or required CI.
5. After authorized merge, let the trusted-main publisher tag only the successfully tested commit. Verify tag/release provenance and actual plugin installation behavior. Do not bypass a failed check or publish from this implementation bundle.

## Adoption boundaries

The managed policy block is automatic during authorized project edits. It preserves existing rules and is not an assertion that executable gates were migrated. Existing projects retain their hooks and CI until an authorized project-level replacement is validated. Evidence-only mode is opt-in and requires a separate verification path. Background worktrees remain conditional on stable inputs and isolated/reserved resources.

This candidate was prepared in a read-only GitHub session. The accompanying local evidence states which deterministic checks ran. Full repository CI, native Claude validation, live model routing and independent approval must be established in the actual checkout before delivery.
