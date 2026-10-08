---
name: build
description: Implement the next approved increment of a project that has been through discover. Applies pending checkpoint decisions to docs/REQUIREMENTS.md, picks the next approved work (or the increment named in the arguments), builds it under the core rules, runs the checks, exercises the user journey, updates status and evidence, and commits on the feature branch. Use to kick off development after a checkpoint is approved, and at the start of every later session instead of "continue". Triggers: "build", "start building", "kick off", "continue the project", "next increment", "go".
---

# Build: the next approved increment

Input: `$ARGUMENTS` names an increment, a milestone, or requirement IDs. If empty, take the next approved item in the order listed in `docs/STATUS.md`.

## 1. Load state
- Read the project CLAUDE.md, `docs/STATUS.md`, `docs/REQUIREMENTS.md`, `docs/DECISIONS.md`.
- Check `git status` and recent `git log`. Reconcile saved state with reality before building anything new: a requirement marked implemented with no code, or code with no requirement, gets corrected first.
- If there is no register or STATUS.md, the project has not been through discover. For substantial work, run the `discover` skill first and stop at its checkpoint. For a small task, implement it directly without this skill.

## 2. Apply decisions
If the conversation contains answers to checkpoint decisions (yes, no, changes, "go with your recommendations"), update the register: `proposed` becomes `approved`, or `deferred` with the reason. Record the choices in DECISIONS.md and restate in one line what is now in scope. Never promote a proposed item without an answer.

## 3. Pick the increment
Take the named increment, or the next approved one. State it in one line: the requirement IDs and what will be observable when it is done. If it is high-risk (auth, payments, personal data, migrations, destructive operations, production config), say so: it gets an independent review before being called verified.

## 4. Implement
Follow the core rules:
- Work on a feature branch. Make the smallest coherent change that delivers the whole user journey for the increment, including failure, empty, and recovery paths.
- Real behavior only. No placeholders standing in for required functionality.
- Add or update tests that express the acceptance criteria.
- Run the relevant tests, type checks, and linters. If the app can run here and the change is user-visible, exercise the journey and report what you saw.
- Fix what breaks. Never weaken a check to get green.

## 5. Verify and record
- For each requirement touched: `implemented` when the code is complete; `verified` only when its acceptance criteria were observed to pass on the current code. Write the command and result in the Evidence column, or `unverified`.
- High-risk increments: spawn the `reviewer` subagent with the requirement IDs, the diff, and the evidence. Address its findings. After three cycles with findings still open, stop and present the unresolved finding with options.
- Update STATUS.md: done so far, in progress, blocked, known limitations, next approved actions. Commit with a message naming the requirement IDs.

## 6. Report and stop
Report in the core's milestone format (Delivered, Requirements, Verified, Discoveries, Alignment, Remaining), about 15 lines, and name the next increment. Stop there. If the user asked to continue through the milestone, repeat from step 3 until its increments are done or a decision is needed.

A discovery that changes scope goes back to the `discover` checkpoint for a decision. It does not go straight into code.
