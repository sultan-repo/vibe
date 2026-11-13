# Vibe v4.14.0

**Feature-level testing by default.** Small fixes and ordinary feature deployments, including auto-deploying merges to production, now use focused unit/integration/component and feature-scoped browser/API acceptance checks for the delivered behavior and its relevant errors/recovery. Full user-journey E2E is not run automatically for routine feature work.

Full end-to-end verification is still required at formal production release/promotion or when the owner explicitly requests E2E. High-risk invariants, unknown impact, required CI and project-specific review/testing gates remain in force; broader checks are used where impact cannot be bounded. Existing project gate scripts are not silently changed by installing Vibe.

The policy works for Claude Code and Codex. Vibe's own merge to main is a formal release and keeps its full CI and trusted-main publication workflow. No new worker, skill command, mandatory selector, or automatic test loop has been introduced. Real-world time savings have not been measured.

Executable hooks follow Codex's trust settings. This patch does not approve hooks or replace project-specific permissions.
