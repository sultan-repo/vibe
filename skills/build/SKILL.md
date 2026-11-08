---
name: build
description: 'Automatically implement requested features, fixes and approved project work from normal conversation. Resume, build, delegate independent work in parallel and verify the complete outcome with risk-appropriate checks. Use for requests to add, change, fix, build or continue software; no slash command is required. Exclude explanation, discovery-only and review-only requests.'
---

# Build: finish the approved outcome

Input: `$ARGUMENTS` may name a feature, milestone or requirement ID. Without arguments, use the user's current request and the next authorized work in project state. **Continuous delivery is the default**: finish the requested scope, not just its first internal increment.

Select this workflow internally from the user's intent. Never ask the user to run a command to start, resume, delegate or verify work. Use other installed Vibe skills internally when their conditions apply.

## 1. Check context selectively
- Read project CLAUDE.md and the relevant code/tests. Check `git status` and recent history before editing. If STATUS.md exists and work is being resumed, reconcile it with the current code.
- Read REQUIREMENTS.md, DECISIONS.md, and other records **only where they affect this work**. Reuse existing issue/task tracking; do not create documentation solely to unlock Build.
- Missing continuity files do **not** force Discover. For clear, approved work, proceed. Invoke `discover` only when product intent or a consequential decision is unresolved (or the user asked for discovery).

## 2. Choose the route and scope
- **Fast:** implement a bounded, understood change with focused checks. Do not automatically launch a reviewer or create checkpoint files for small fixes.
- **Standard:** briefly plan the authorized feature internally, then implement all connected increments in the current request. No automatic user pause between increments.
- **Critical:** identify high-risk invariants, action scope and recovery behavior. Load `references/review-loop.md` only for relevant high-risk work or a final review gate. Ask about genuinely ambiguous rules, not routine engineering choices.
- Incorporate previously approved decisions; never silently approve a proposed feature. If new scope is needed, ask once with a recommendation while continuing unaffected work.
- For Standard/Critical work, identify ready independent tasks and their actual dependencies in the existing plan. Automatically delegate useful parallel work using `references/parallel-work.md`; do not wait for the user to request workers. Keep a short or tightly coupled task in the main agent.

## 3. Implement continuously
- Work on a feature branch for substantial changes. Deliver the user journey, including relevant failure, empty and recovery paths.
- Prefer the smallest effective implementation. Do not introduce speculative frameworks, agents, dependencies, broad refactors or duplicate planning artifacts.
- Add or update acceptance tests. For stateful Critical rules, use sequence/property tests where valuable, otherwise explain equivalent deterministic coverage.
- Run relevant tests, lint/typecheck, and exercise user-visible behavior where the app can run. Fix failures without weakening checks.
- Continue through the approved feature or milestone **without stopping after each increment**. Commit coherent deliverables with human-readable, action-first commit titles. When tracking requirement IDs, put them in the commit body, not the title. Use purpose-based branch names and descriptive PR titles.
- For a multi-step Standard/Critical task, reuse native Claude task tracking if already used. If those tools are unavailable **and** `mcp__vibe__progress` is present, optionally publish 3–7 meaningful outcome steps to the visual board once, then update only when a step changes status. Never call this tool for Fast work or on every code change; skip it if reporting would slow a short task. Completing a progress item is not the same as verifying acceptance.
- The coordinator owns the shared plan and board updates, including worker progress. Let the board open automatically from tracked work on supported surfaces; respect a dismissed pane and continue normally without a board. Do not ask the user to run `/vibe-board`.

## 4. Verify and hand off
- Mark requirements verified only with passing acceptance evidence on the current code. Record commands/results and unresolved limitations accurately.
- Integrate worker results before checking the combined user journey. Run affected acceptance/integration checks on the combined code; isolated worker checks do not establish that the pieces work together. Resolve incomplete or failed assignments before reporting the requested outcome complete.
- Update existing STATUS.md and requirement records **once at a meaningful milestone or interruption**, not at each intermediate edit. Keep the handoff concise. Do not create a register for a standalone routine fix.
- Build normally relies on direct verification. For substantial changes when a specific independent check materially helps, the fresh-context Claude `reviewer` may perform one focused check; **do not automatically** review every increment or unchanged code.
- **Before a high-risk merge or release**, invoke `reassess` for the consolidated final Claude review, or reuse a valid review of the exact same final HEAD/scope with current evidence. Required security/data findings still block readiness. Reassess owns the one targeted recheck and stop rule.
- Do not equate a reviewer verdict with test evidence or claim checks passed when they did not run.

## 5. Tell the user what matters
Default to a short plain-language report: **Delivered**, **Verified**, **Remaining** (only if applicable). Use feature names, not `M1`/`M2` or `R-01`; put internal traceability in files. Give exact commands/results when they matter. Disclose blockers and unverified outcomes. Do not output a six-section, 15-line process report by default.

Stop only when the requested work is complete or a real blocker, material decision or external permission is required. Do not stop simply because an internal increment, checklist or milestone boundary was reached.
