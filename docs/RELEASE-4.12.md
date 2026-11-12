# Vibe v4.12.0 release candidate

Merging to `main` is a production delivery because marketplace installations use this repository. Run Vibe checks on the integrated candidate before merge and record skipped checks as pending.

Exercise installation, reinstallation and removal in disposable profiles. From an empty project, verify first-prompt visibility in Codex with untrusted hooks, then test the configured startup and shell-check commands separately. Validate both Claude manifests and exercise its startup hook. Check migration from existing Claude instructions, preservation of owner rules and repeated adoption. For release, exercise an ordinary task in each supported host and record observed workflow behavior.

Changes to delivery controls require independent review of the exact final commit and the existing bounded targeted recheck when needed. Package discovery alone cannot certify execution or approval of a hook.
