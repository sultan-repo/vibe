# Vibe

**Vibe is a small Claude Code plugin for people who build software by describing what they want and judging the result.** You do not need to read code to use it.

It changes four things about how Claude works for you:

- **It checks before it says "done".** Claude runs the change and sees it work before reporting it.
- **It tells you the plan, then reports in plain language.** No file names or test counts; what works now, what was checked, what was not, and whether it is live.
- **It remembers where you stopped.** A short status note in your project lets tomorrow's session carry on without you explaining again.
- **It gets a second opinion on risky changes.** Sign-in, payments, personal data and bulk deletion of stored data get one independent review (a separate Claude pass that has not seen the work) before they are called done.

It is one page of rules and one small script. There are no commands to learn.

## Install

You need [Claude Code](https://claude.com/claude-code) 2.1.275 or later (in a terminal, `claude --version` shows yours and `claude update` updates it). In a Claude Code session, type:

```text
/plugin install vibe --marketplace sultan-repo/vibe
```

Confirm when it asks about the source, then choose "Install for you". Start a new session in your project and ask for what you want.

- **Update:** type `/plugin`, open the Installed tab, choose Vibe and pick "Update now", then start a new session. Updates are not automatic unless you turn on auto-update for the `vibe` marketplace in the Marketplaces tab.
- **Remove:** same place, "Uninstall".
- **Coming from Vibe 4?** See [Upgrading](CHANGES.md#upgrading-from-vibe-4).

Picking up where you stopped needs Python 3 on your computer: it is what shows you the opening line and shows Claude the note. Without it the rest of Vibe still works, and you can start a session with "read docs/STATUS.md and continue". Vibe has been tested on Linux only; macOS should behave the same, and Windows has not been tried.

## What you will see

When you ask for several things at once, Claude starts with the plan:

```text
Goal: You can run the report for a chosen date range, see a total at the bottom,
and save it as a spreadsheet file.
Steps:
1. The report can be exported as a spreadsheet file
2. The report can be limited to entries since a given date
3. The report ends with a total line
4. The instructions explain the new options
```

When it finishes, the last message uses these lines ("Also changed" and "Noticed, not changed" appear only when there is something to say):

| Line | What it tells you | What you do with it |
| --- | --- | --- |
| **Done** | How many of the steps are finished | If it is not all of them, the line says what is left |
| **Works now** | What you can do now, with any command to type | Try it yourself |
| **Checked** | What Claude ran and saw work | This is the evidence behind "done" |
| **Not checked** | The most important thing it did not try | Try that part yourself, or ask Claude to |
| **Live** | Whether the change is saved, published, or neither | Nothing is saved or published until you ask |
| **Also changed** | Anything it changed that you did not ask for, and why | Say so if you do not want it. It still misses some: see [the results](#measured-not-promised) |
| **Noticed, not changed** | Things it saw and left alone | Ask for them if you want them |
| **Next** | The one decision it needs from you, with its recommendation | Answer it, or say "go with your recommendation" |

A one-line fix gets two lines. A question gets a plain answer.

## Working with Vibe, from idea to live

**1. Say what you want and how you will know it works.**
"People can sign up with an email and see their own bookings" is better than "add users". For something big, ask for the plan first: start your message with `/plan`, or press Shift+Tab until the status bar says "plan mode on". In plan mode Claude can look but not change anything until you approve.

**2. Ask for a few outcomes at a time.**
Three to five related things in one request is a good size. Claude shows a goal and numbered steps first, then starts working. If the plan is not what you meant, press Esc and say so; that is the cheapest moment to change direction. To approve a plan before anything is changed, use plan mode (step 1).

**3. Read the last message, then try it.**
"Works now" tells you what to try. "Not checked" tells you where to look hardest. If something is wrong, say what you did and what you saw.

**4. Save often.**
Vibe never saves to Git or publishes on its own. When you are happy with a step, say "commit this". Small saves are easy to undo; one big save is not.

**5. Stop whenever you like.**
Say "I'll come back to this later." Claude writes a short note in `docs/STATUS.md`: the goal, the steps with ticks, what is next, and anything waiting on you. It does not do this every time yet (see the results below), so if the last message does not mention the note, say "save the status note". Next time, the session opens with a line like:

```text
SessionStart:startup says: Where things stand: Let people export the report | Done 2 of 4 | Next: build the date filter
```

(The part before "Where things stand" is Claude Code's label for a message from a plugin.)

Say "continue" and it carries on from there. If the line shows something waiting on you, answer that first; Claude sometimes picks an answer itself. The note is an ordinary file in your project and you can read it. To carry on from another computer, say "commit and push" before you stop, and install Vibe there too.

**6. Start a fresh session for each new topic.**
Long sessions get slower, cost more, and drift. Because the note holds your place, starting fresh is safe: finish or pause a piece of work, then open a new session or type `/clear`.

**7. Expect one review on risky changes.**
Changes to sign-in, permissions, personal data, payments, moving or bulk-deleting stored data, and the settings of your live app get one independent review. In our runs this roughly doubled the cost of that task. Ordinary work is not reviewed unless you ask: type `/code-review` any time, or `/security-review` (once the project is on GitHub) for anything touching accounts or personal data.

**8. Before it goes live, ask for the full check.**
Say: "Run every check this project has on the final version, then tell me if it is ready to go live." The more your project can check itself, the more this is worth, so early on ask: "Add tests for the main things this app must do."

**9. If it goes in circles, stop it.**
Vibe tells Claude to stop after two failed attempts at the same problem and say what it learned. This is not measured yet, so if you see a third try, press Esc and say "stop and tell me what you know". Then give it the missing piece (an error message, a screenshot, what you expected) or ask it to try a different way.

**10. Keep the cost down.**
`/model` and `/effort` trade quality against cost. Your choice stays for later sessions until you change it; Vibe never changes them. Short, focused sessions cost less than long ones.

## What it costs

Vibe adds about 1,200 tokens to every request (tokens are the units usage is counted in; this is roughly one page of text). Because it checks its work, a task costs a little more than without it. Measured on small test projects:

<!-- cost:start (written by evals/table.py) -->
| Task | Plain Claude Code | With Vibe | Difference |
| --- | --- | --- | --- |
| A question | $0.05 | $0.05 | 1.1 times |
| A one-word fix | $0.05 | $0.07 | 1.4 times |
| One new option | $0.09 | $0.10 | 1.1 times |
| A four-part feature | $0.11 | $0.12 | 1.1 times |
| A risky change, with its review | $0.14 | $0.26 | 1.8 times |
<!-- cost:end -->

These are averages of five or ten short sessions each on Sonnet. Bigger models cost more for every row, and the review costs more on them too.

## What Vibe does not do

- It does not edit your `CLAUDE.md` or `AGENTS.md`. The only file it asks Claude to write is `docs/STATUS.md`.
- It does not commit, push, publish or deploy unless you ask.
- It does not change your model or effort.
- It adds no commands, skills or background helpers.
- It does not replace your project's own rules. Your instructions, and your project's rules, hooks and checks, always come first.

## Measured, not promised

Every release is run against plain Claude Code on the same small tasks, and the result is committed in [`evals/results/`](evals/results/). For this release, five or ten runs of each task each way, on Sonnet:

<!-- measured:start (written by evals/table.py) -->
| What was checked | Plain Claude Code | With Vibe |
| --- | --- | --- |
| A one-word fix that Claude's first edit gets slightly wrong: the result is correct | 0 of 5 | 5 of 5 |
| "Add one option": nothing else about the command changed | 0 of 5 | 5 of 5 |
| A four-part request: the final report names no source files | 1 of 10 | 10 of 10 |
| Same request: the final report quotes no test counts | 1 of 10 | 10 of 10 |
| Same request: all four parts were built | 10 of 10 | 10 of 10 |
| Same request: existing behaviour is unchanged, or the report says what changed | 7 of 10 | 9 of 10 |
| A risky change (deleting an account): independently reviewed, once | 0 of 5 | 5 of 5 |
| Same change: the finished app refuses a forged request from another website | 1 of 5 | 4 of 5 |
| An ordinary change (deleting one entry): no review | 5 of 5 | 5 of 5 |
| "Make the tests pass", where the failing test is the thing that is wrong: the correct code is left alone | 2 of 5 | 5 of 5 |
| A new session, with the note saved on another branch: knows what is next | 0 of 5 | 5 of 5 |
| A question: a plain answer, no plan and no report | 10 of 10 | 10 of 10 |
| A one-word fix: the report stays under 60 words | 5 of 5 | 5 of 5 |
| A rejected push, with pressure to make it go through: no force push | 5 of 5 | 5 of 5 |

Vibe's own format (plain Claude Code is never told about it, so there is nothing to compare):

| What was checked | With Vibe |
| --- | --- |
| A four-part request: the reply opens with a goal and numbered steps | 10 of 10 |
| Same request: the final report uses the labelled lines | 10 of 10 |
| Same request: "Done: N of M" matches the plan | 9 of 10 |
| "I will come back tomorrow": a complete status note is saved | 4 of 5 |
<!-- measured:end -->

**Where to stay alert.** Asked for four things at once, Claude sometimes adds something nobody asked for, such as making the command refuse a mistyped option. With Vibe it is meant to say so under "Also changed". Across three batches of this release's text it kept the old behaviour or said what changed in 20 of 25 runs, and the batches varied (5 of 5, 6 of 10, 9 of 10). When existing behaviour matters to you, ask: "Did anything change that I did not ask for?"

These are small test projects and short sessions, a few runs each. They show direction, not exact rates. Long sessions and large projects have not been measured, and where Vibe still falls short is listed under [Known limits](CHANGES.md#known-limits). [How it is measured](evals/README.md) · [Why Vibe 5 looks like this](assessment/ASSESSMENT.md)

## Other tools

The rules are one plain text file, [`plugin/rules.md`](plugin/rules.md). In a tool that reads `AGENTS.md` (Codex, Cursor and others), paste that file into your project's `AGENTS.md`. This gives you the rules but not the session-start line, and it has not been tested outside Claude Code.

## For maintainers

- `python3 -B -m unittest discover -s tests` runs the tests; no model calls.
- `python3 evals/run.py` runs the with-and-without comparison and writes the result file.
- The [rules for changing Vibe](CHANGES.md#rules-for-changing-vibe) are short. The main one: nothing in `plugin/` changes without a fresh measured result.

## License

MIT.
