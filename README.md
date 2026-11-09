# Vibe

**Give Claude Code a task. Vibe helps it plan, build, check, and finish.**

Vibe is a lightweight workflow plugin for [Claude Code](https://code.claude.com). Just describe what you want in plain language. No special commands required.

## How it works

```text
         YOU
          |
   "Build this feature"
          |
          v
    +-----------+
    |   VIBE    |
    +-----------+
          |
          v
   Understand the task
          |
          v
   Plan only if needed
          |
          v
   Build the solution
      /    |    \
     /     |     \
  Agent  Agent  Agent    <- parallel when useful
     \     |     /
      \    |    /
          v
   Check the result
          |
          v
   Report what's done
          |
          v
         YOU
```

Small fixes take the short path. Larger tasks can use multiple Claude agents. Risky changes get more careful checks.

## What you get

- **Less babysitting.** Vibe picks the appropriate workflow and keeps approved work moving.
- **Parallel help when useful.** Independent tasks can run with Claude subagents, then get integrated.
- **Checks without endless review loops.** Focused tests for changed features, broader checks for shared or risky changes, and full verification before production delivery.
- **Clear progress.** Updates explain what's done, what's next, and what needs your decision.
- **Session continuity.** Project status is saved at work boundaries and loaded when a new session starts.
- **Safer Git operations.** A hook protects against unsafe force-pushes.

Vibe uses Claude Code's native capabilities. It doesn't require a separate AI service or reviewer CLI.

## Install

In Claude Code, run:

```text
/plugin marketplace add sultan-repo/vibe
/plugin install vibe
```

Start a **new Claude Code session**, then describe your task normally.

## Just talk to Claude

| You say | Vibe does |
| --- | --- |
| “Fix the login error.” | Makes the fix and runs relevant checks. |
| “Build a family tree app.” | Works through the scope, builds approved features, and verifies milestones. |
| “Add search and export.” | Uses parallel agents if the work can be safely split. |
| “Is this ready to release?” | Checks the integrated result and reports blockers. |
| “Continue where we left off.” | Uses the saved project status to resume. |

You can also ask Vibe to explore an idea without implementing it.

## Optional progress board

On supported Claude Code interfaces, Vibe can show a simple progress board. It opens automatically for tracked plans, or you can reopen it with `/vibe-board`.

The board shows reported task progress, not a live guarantee that tests have passed.

## Good to know

- Vibe chooses between fast, standard, and careful workflows based on the task.
- It asks for decisions that materially affect the outcome. Your existing approval and permission rules still apply.
- Session recovery uses the saved project status and local Git context. It cannot recover work that was never saved.
- Parallel agents are optional and depend on the task and available Claude resources.

Existing project test requirements still apply. Finishing a feature does not mean it is ready for release. See [how Vibe selects tests](skills/build/references/testing-policy.md).

**Update:** `/plugin update vibe`  
**Uninstall:** `/plugin uninstall vibe`

For alternate installation, detailed behavior, and development instructions, see [the repository docs](docs/) and [change history](CHANGES.md).

## License

MIT.
