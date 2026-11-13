# Vibe v4.13.0

Vibe can now highlight likely conflicts between its workflow principles and project instructions in Claude Code and Codex. During initial authorized project editing or relevant rule changes, a bounded read-only checker identifies likely contradictions, while the coordinator confirms whether they apply.

The project owner chooses once: align with Vibe, keep a stricter or intentional project exception, or defer. A decision is stored in the existing project decisions record using an evidence fingerprint, so unchanged questions do not recur. A requested alignment is never mistaken for completed migration. Existing hooks, CI, approvals and production release gates remain unchanged until a scoped replacement is validated.

The feature adds one optional Python helper and an on-demand reference, not a startup scanner, slash command, agent or extra test gate. Executable hooks follow Codex's trust settings. Scanning is conservative: dynamic scripts or nuanced rules may need human review. Live Claude/Codex behavior and elapsed-time savings require independent runtime evidence; none is claimed by this release.
