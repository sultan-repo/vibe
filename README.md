# Vibe

**Give Claude Code or Codex a task. Vibe helps it plan, build, check, and finish.**

Install Vibe in the agent you use, then describe what you want in plain language. No special commands required.

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

Small fixes take the short path. Larger tasks can use the host's available agents. Risky changes get more careful checks.

## What you get

- **Less babysitting.** Vibe picks the appropriate workflow and keeps approved work moving.
- **Parallel help when useful.** The agent can delegate independent tasks and integrate their results.
- **Reuse before rebuilding.** Checks existing code and suitable libraries before substantial custom work, without adding dependencies for every small helper.
- **Checks without endless review loops.** Focused tests for changed features, broader checks for shared or risky changes, and full verification before formal production releases.
- **Clear progress.** Updates explain what's done, what's next, and what needs your decision.
- **Session continuity.** Project status is saved at work boundaries and loaded when a new session starts.
- **Safer Git operations.** The enabled, trusted shell hook checks for unsafe force-pushes.

## Install

**Claude Code** (2.1.275 or later). Install from the chat:

```text
/plugin install vibe --marketplace sultan-repo/vibe
```

**Codex CLI** (tested with 0.162.1). With Git and Python 3.9+ installed, run in a terminal:

```sh
git clone https://github.com/sultan-repo/vibe.git
python3 vibe/install-codex.py
```

The installer adds Vibe and its startup instruction to your Codex profile. From an existing checkout, run `python3 install-codex.py`. Pull and rerun to update.

Open a new session in **your project** and ask “Fix the login error.” Vibe selects the workflow. In Codex, approving Vibe's two hooks enables automatic status loading and force-push checks. The workflow works before hook approval.

For marketplace-only Codex installation, use `codex plugin marketplace add sultan-repo/vibe` and `codex plugin add vibe@vibe`. This path relies on skill matching until startup hooks are trusted.

## Just describe the task

| You say | Vibe does |
| --- | --- |
| “Fix the login error.” | Makes the fix and runs relevant checks. |
| “Build a family tree app.” | Works through the scope, builds approved features, and verifies milestones. |
| “Add search and export.” | Uses parallel agents if the work can be safely split. |
| “Is this ready to release?” | Checks the integrated result and reports blockers. |
| “Continue where we left off.” | Uses the saved project status to resume. |

You can also ask Vibe to explore an idea without implementing it.

## Automatic project adoption

During authorized edits, Vibe preserves the instruction file your host loads, including configured fallbacks. It uses `AGENTS.md` where safe. Unknown routing and read-only requests leave files unchanged; in-session principles still apply.

Startup can flag potentially expensive project gates when relevant configuration changes. Existing protections stay active until their replacement is authorized and validated. Projects can opt into evidence-only push checks, so missing results block the push without starting a long test run inside it.

## Good to know

- Vibe chooses between fast, standard, and careful workflows based on the task.
- It asks for decisions that materially affect the outcome. Your existing approval and permission rules still apply.
- Session recovery uses the saved project status and local Git context. It cannot recover work that was never saved.
- Parallel agents depend on the task and host permissions.

Existing project test requirements still apply. Finishing a feature does not mean it is ready for release. See [how Vibe selects tests](skills/build/references/testing-policy.md) and [how it chooses reuse](skills/build/references/reuse-policy.md).

In Claude Code, use `/plugin update vibe` or `/plugin uninstall vibe`. Run `python3 install-codex.py --uninstall` to remove installer-managed files. An existing native Codex installation stays under Codex's management.

For alternate installation, detailed behavior, and development instructions, see [the repository docs](docs/) and [change history](CHANGES.md).

## License

MIT.
