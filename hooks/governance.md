# Owner-controlled project governance

Load on initial authorized project editing or when relevant instructions, hooks or CI change. Do not run a project-wide scan every turn or require an initialization command. This guidance applies equally in Claude Code and Codex. The project remains under higher-priority host and user instructions.

Run the optional bundled helper internally:
- Plugin: `python3 <installed Vibe root>/hooks/governance.py scan --project-dir <active project root>`
- Manual Claude installer: `python3 ~/.claude/vibe-tools/governance.py scan --project-dir <active project root>`

The scanner reads bounded root and nested Claude/Codex instructions and active executable Git hooks. It executes no project scripts, performs no network request and writes nothing during scanning. Returned matches are **candidates**, not authoritative interpretations. Inspect actual host instruction precedence (including configured Codex fallbacks), project hooks, related scripts and CI triggers. A full production/integration gate or intentional project-specific security requirement is not automatically a conflict. Treat incomplete inspection as uncertainty, never as permission to weaken protections.

For each confirmed consequential contradiction, ask the owner once with a recommended default and three choices:
1. **Align with Vibe**: authorize a scoped, validated change to instructions and their executable enforcement. Keep the old protection active until the new one passes existing project acceptance and delivery checks.
2. **Keep project rule**: record an intentional project-specific exception, which remains in force.
3. **Defer**: keep current requirements, do not repeat the question for identical evidence, and disclose consequential unresolved implications when relevant.

After an explicit owner answer, the coordinator may call `governance.py decide --project-dir <root> --id <candidate-id> --fingerprint <hash-from-scan> --choice keep-project|align-vibe|defer --owner-confirmed`. Never use the owner confirmation flag without actual approval. This writes only a small managed section within existing `docs/DECISIONS.md`, creating it only for a recorded decision if absent. The choice is tied to the detected evidence fingerprint. Changed evidence is unresolved again. An alignment choice is marked **alignment-pending**, not proof that project instructions, checks or hooks were changed. Keep-project and defer decisions suppress repeat questions until relevant evidence changes.

The helper is conservative: semantic, dynamic, inherited or custom script conflicts may be missed. Verify meaningful suspected conflicts manually, without loading all project documents into every context. Do not automatically migrate or uninstall CI/hook protection, alter permissions, bypass the host, or claim an unrun test passed. Apply Vibe's default workflow to compatible work while a material decision is pending. This is not a new reviewer, project register, full gate or startup enforcement hook.
