# Vibe v4.12.1 release candidate

Merging to `main` is a production delivery because marketplace installations use this repository. The owner authorized this repair and publication. Run Vibe checks on the integrated candidate before merge and record skipped checks as pending; an unavailable check is not a pass.

## Patch scope

Repair complete Codex core transport, preserve native owner-instruction selection during adoption, recognize fenced import examples correctly, and recover from caught multi-file write failures. Do not change verification cadence, release gates, review requirements, reuse-first decisions, automatic workflow selection or hook trust. This patch does not add the separately proposed version-comparison or end-of-turn checkpoint features.

## Validation

Exercise installation, reinstallation and removal in disposable profiles. Check real Codex prompt construction before and after adoption for populated/empty overrides, configured fallback ordering, later owner edits and v4.12 repairs. Assert actual owner-rule contents, not just a reminder to find them. Validate both plugin manifests and the actual startup payload, including bounded Unicode continuity text, against the configured Codex context allowance. Keep strict Claude plugin validation and the existing native Codex installation checks.

Test longer closing fences, indented and unclosed examples, preserved imports, malformed/ambiguous rules, second/third-write failure, deletion rollback, concurrent edits and private recovery retention. Caught failures must restore completed edits or report an incomplete transaction with recovery copies. Do not claim crash-proof or adversarially atomic multi-file writes.

For release, exercise an ordinary task in each supported host and record observed workflow behavior. Changes to delivery controls require independent review of the exact final commit and the existing bounded targeted recheck when needed. Deterministic prompt construction and transport tests cannot certify live model adherence or approval of a hook. Record any unavailable runtime/reviewer evidence honestly rather than treating a test count as an approval.

The trusted-main publisher must tag only the successfully tested merged commit. Verify the published tag and release target against that SHA. No changes to branch protections, CI permissions or publication guards are part of this patch.
