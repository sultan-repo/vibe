# Vibe v4.15.0 release verification

Merging to `main` is a production delivery and formal Vibe plugin release. Complete required evidence before merge. A skipped, cancelled, failed or unavailable required check is not a pass. This file defines the gate; actual results and exact SHAs belong in PR #22 and its CI records.

## Scope

Publish capability-based model/effort routing for Claude Code and Codex. The implementation was independently reviewed at `75b409e8427d7df5686f4a8237f194683fd4448f`, based on v4.14.0 at `af080f173bb183ef8471ed4cd2381d50b3e638fb`. Release preparation aligns both plugin versions, marketplace description, core heading, CI version assertion, publisher and release-regression expectations with v4.15.0, without changing the reviewed routing behavior. Historical notes and releases remain unchanged.

## Before merge

Require successful `validate` and `native-mod-render` jobs on the exact final integrated candidate. Retain full repository policy/configuration tests, benchmark self-tests, force-push safeguards, shell/JSON checks, installer smoke, strict native Claude plugin validation and the Codex installation/first-prompt tests. The generic job may skip the three CLI-dependent Codex cases only when the native job actually runs and passes those same cases. Inspect the current jobs and their logs, not only the workflow badge.

Record head, integration base and tested tree. A changed base or source needs applicable current evidence. Obtain one focused independent targeted recheck of the release-preparation delta and its interaction with the previously reviewed implementation on the exact final head. Earlier approval cannot certify a changed candidate by itself. Do not alter source after this check without reassessing the evidence.

The owner must authorize merge and publication. Preserve the normal PR path and required checks; do not bypass protections. Version metadata must match before merge because marketplace installations follow main.

## Publication

Keep existing read-only PR permissions and trusted-main-only publication controls. The publisher accepts successful main-push checks, checks out their exact SHA, rejects stale main candidates and conflicting tags, and publishes v4.15.0 with the tested commit and CI URL. Verify the published release and tag point to that tested commit; a successful workflow that skipped publication is not proof of a release. No manual tag rewrite or permission expansion is needed.

## Preserved behavior and limits

V4.14's focused feature testing, full formal-release verification, governance, permissions, continuity, reuse-first decisions and existing project gates remain unchanged. Routing uses supported native controls and respects scoped preferences; it is not a service that guarantees every future host or model will work without updates.

Static tests and native package/installation validation cannot certify authenticated end-to-end model selection, real-account fallback behavior, live adherence or measured cost/token/time savings. These remain unverified unless separately observed under [the routing validation plan](MODEL-ROUTING-VALIDATION.md). Requested/configured/observed settings stay distinct. No project gates, global defaults or provider credentials are changed by this release preparation.
