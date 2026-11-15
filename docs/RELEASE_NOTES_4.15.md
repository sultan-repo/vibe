# Vibe v4.15.0

## Match models to the work

Vibe now guides Claude Code and Codex to choose model and reasoning effort using four task tiers: **fast, balanced, deep and maximum**. It resolves suitable choices from available native capabilities, aliases/catalogs and your preferences instead of hardcoding model versions. New models can be considered when the host exposes them and their suitability is established; newness alone is not evidence of quality.

Useful subagent assignments select both a suitable model and supported effort where native controls allow it. Your main-session model stays unchanged unless an authorized native switch is safe. Explicit model/effort preferences, role settings, account limits and budgets remain respected. Loading a workflow no longer unconditionally resets your effort choice.

## Preserve quality without extra ceremony

Unknown capabilities, rejected controls or weaker fallbacks must not silently lower the quality bar for consequential work. Requested, configured and observed model/effort settings are recorded distinctly when useful; missing runtime evidence stays unknown.

Discovery is reused within a session and refreshed only for relevant changes. There is no new routing service, external leaderboard, per-turn lookup, classifier agent or mandatory register. Existing testing, formal-release verification, independent review, permissions, project governance and continuity rules remain intact. Executable hooks follow Codex's trust settings; this release does not grant hook approval or change project-specific gates.

## Verification and limits

Adds 20 routing-policy regression tests and a bounded real-host validation plan. Repository/native checks and independent code review validate the implementation and packaging, not authenticated live routing or every provider/account fallback. No measured speed, cost or token savings, unchanged defect-detection rate, or universal future-model guarantee is claimed.

See the [release verification requirements](https://github.com/sultan-repo/vibe/blob/v4.15.0/docs/RELEASE-4.15.md) and [routing validation plan](https://github.com/sultan-repo/vibe/blob/v4.15.0/docs/MODEL-ROUTING-VALIDATION.md). Actual release evidence is recorded in PR #22 and the publication provenance below.
