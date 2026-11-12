# Vibe v4.12.1

Repairs four instruction-loading and project-adoption issues in v4.12.0 while preserving Vibe's existing delivery principles.

- The Codex startup hook has a finite context allowance large enough for the full core and bounded continuity/advice payload. A truncated preview is explicitly not a fully loaded standard.
- Adoption preserves the native selected owner-instruction file. Configured Codex fallbacks remain active, including their later owner edits, instead of being shadowed by a new AGENTS.md. Effective fallback order must be known before changing routing; uncertainty leaves files untouched and does not stop applying Vibe principles in-session.
- Safe repair of v4.12's owner-free fallback reminder and generated bridge no longer ignores a bridge that gained owner instructions. Ambiguous owner content is preserved for explicit reconciliation, not copied or discarded.
- Fenced examples with longer closing fences, indented examples and unclosed fences no longer masquerade as a working Claude import.
- Caught multi-file adoption failures roll back completed edits. Concurrent owner edits are never overwritten by rollback; incomplete recovery retains private original copies and reports their location. Abrupt termination is not guaranteed atomic.

Executable hooks follow Codex's trust settings. The patch does not approve hooks automatically, install project test gates, add slash commands or reintroduce vibe-board. A changed hook may need the host's normal trust review. Reuse before rebuilding, affected/expanded/release testing, required review and publication protections remain unchanged.

Regression tests cover instruction selection, transport and recovery. They do not prove universal live-model compliance, application defect detection or time/token savings. Updating Vibe does not silently rewrite every existing project; adoption happens during authorized project work under the preserved rules.
