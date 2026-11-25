# Changes

## Rules for changing Vibe

These exist because Vibe 4 tripled in size in five weeks without anyone measuring whether it helped.

1. **Nothing in `plugin/` changes without a fresh measured result and a new version.** Raise the version in `plugin/.claude-plugin/plugin.json`, run `python3 evals/run.py`, and commit the result file. CI fails if the plugin differs from what was measured, and the release fails if the plugin changed under an already published version (installed copies only update when the version changes).
2. **`plugin/rules.md` has a budget of 3,800 characters.** An addition needs a deletion.
3. **A line that shows no difference in two releases is deleted.** So is any new skill, agent or hook that cannot show one.
4. **Nothing user-visible ships without being seen once in a real session.**

## 5.0.0 - 2026-11-25

Vibe 5 is a rewrite. It keeps what was measured to help and removes everything else. The full reasoning and the measurements are in `assessment/ASSESSMENT.md`.

### What changed for you

- **Vibe now reaches Claude in full.** Vibe 4 sent 15,368 characters at session start, and Claude Code cut that to a 2,000-character preview, so most rules and the saved status never arrived. Vibe 5 sends one page of about 3,800 characters, all of it delivered, and delivers it again after `/clear` and after compaction.
- **A plan first, and a report you can read.** A request with three or more parts opens with a goal and numbered steps in your words. Each task ends with the same short lines: Done, Works now, Checked, Not checked, Live, Also changed, Noticed-not-changed, Next.
- **Checked before "done".** Claude runs the nearest check, or tries the app, before it reports a change as working.
- **A wrong test is not a reason to break working code.** When a failing test contradicts what the project says it does, Claude stops and asks instead of bending the code to the test (5 of 5 runs, against 2 of 5 without Vibe).
- **One independent review for risky changes.** Sign-in, permissions, personal data, payments, migrating or bulk-deleting stored data, and production settings get one pass of the built-in `/code-review` before they are called done. Ordinary work does not.
- **A status note that works.** When you stop with steps left, Claude writes `docs/STATUS.md`. The next session reads it, also when it was saved on another branch and nothing newer has been committed where you are, and shows you one line: where things stand, what is next, what is waiting on you.
- **Smaller.** About 1,200 tokens per request, down from about 1,570, and nothing runs before each shell command any more.

### Removed

- The six skills (`build`, `discover`, `reassess`, `effort-low`, `effort-medium`, `effort-high`) and both agents (`reviewer`, `worker`). In matched runs they were not invoked or changed nothing.
- Automatic project adoption, the managed policy block and the governance scanner. Vibe no longer edits `AGENTS.md` or `CLAUDE.md`.
- Model and effort routing. Use `/model` and `/effort`; Vibe changes neither.
- The force-push guard. It blocked the safe `--force-with-lease`, let other force pushes through, and blocked every shell command when Python was missing. The eval suite keeps a case that fails if Claude ever force-pushes; a corrected guard returns only if it does.
- The verification cache and pre-push template.
- `install.sh`, `uninstall.sh`, `install-codex.py` and the Codex plugin files. The marketplace plugin is the only supported install.
- The phrase-matching tests, the per-release documents under `docs/`, and the unused benchmark script.

### Upgrading from Vibe 4

| You have | What to do |
| --- | --- |
| The plugin from the marketplace | Run `claude plugin update vibe@vibe` in a terminal, then start a new session |
| A `docs/STATUS.md` from Vibe 4 | Nothing. It is still read; the next time Claude saves the note it uses the new, simpler format |
| A block between `<!-- vibe:project:start -->` and `<!-- vibe:project:end -->` in `AGENTS.md` or `CLAUDE.md` | Delete it, or ask Claude to. It holds Vibe 4 rules that now disagree with Vibe 5 |
| A "Delivery" section that Vibe 4 wrote into your `CLAUDE.md` | Delete it, or ask Claude to |
| Vibe installed with `install.sh` | Run the 4.15 uninstaller once (`uninstall.sh` at tag `v4.15.0`), then install the plugin. The uninstaller deletes `~/.claude/skills/build`, `discover`, `reassess`, `effort-low`, `effort-medium`, `effort-high` and `~/.claude/agents/reviewer.md`, `worker.md`: move any of your own files with those names first |
| Vibe in Codex | Run `python3 install-codex.py --uninstall` from a checkout of tag `v4.15.0`. If you installed it through Codex's own plugin marketplace, remove it there instead. To keep the rules, paste `plugin/rules.md` into your `AGENTS.md` (not tested on Codex) |

### Known limits

What the measurements for this release showed Vibe does not do yet. Counts are in `evals/results/5.0.0.json` and `assessment/evidence/`.

- **Unrequested changes are not always reported.** On a single request Claude now leaves other behaviour alone (5 of 5 runs, against 0 of 5 without Vibe). On a four-part request it still sometimes makes the program refuse input it used to accept. Across three batches of this text it kept the old behaviour or said so under "Also changed" in 20 of 25 runs, and the batches varied (5 of 5, 6 of 10, 9 of 10). The first 5.0.0 wording of that line managed 0 of 5.
- **The status note is not written every time.** A complete note was written in 4 of 5 sessions that ended with "I will come back tomorrow", and none is written when a session is cut off. If the last message does not mention the note, say "save the status note".
- **A resumed session sometimes decides for you.** When the note says something is waiting on the owner, the next session usually asks, but sometimes picks an answer and carries on.
- **Reports run long.** The rule says about 100 words; reports on a four-part request were 160 to 220.
- **The review costs money and is not a guarantee.** A sensitive change cost 1.8 times as much as the same change without the review on Sonnet (2.8 times in one run on a larger model). In 1 of 5 runs the finished app still accepted a forged request from another website after the review.
- **No force-push guard.** Claude did not force-push in any measured run, with or without Vibe, so the guard was removed. A case in the eval suite fails the release if that ever changes.
- **Two rules are not measured yet:** running every check once before anything reaches users, and stopping after two failed attempts. They are there on judgment and are the first candidates for deletion.
- **Not tested:** sessions longer than a few minutes, automatic compaction in a long session, real-size projects, Windows, and any tool other than Claude Code.

## Earlier versions

Release notes for 4.5.0 to 4.15.0 are on the [GitHub releases page](https://github.com/sultan-repo/vibe/releases). In one line each:

- **4.15** model and effort routing by task tier.
- **4.14** focused checks for routine deployments; full end-to-end runs only for formal releases.
- **4.13** owner-controlled governance scan for conflicting project rules.
- **4.12** Codex installation and shared `AGENTS.md` rules; 4.12.1 fixed truncated startup text on Codex.
- **4.11** reuse-before-rebuilding guidance.
- **4.10** automatic project adoption; skills hidden from the slash menu; progress board removed.
- **4.9** affected, expanded and release test scopes.
- **4.8** status checkpoints and the startup status check.
- **4.7** focused checks by default; effort skills; optional verification cache.
- **4.6** automatic workflow selection and parallel workers.
- **4.5** continuous execution, concise reporting, progress board.
- **4.0 to 4.4** split of the always-on core from skills; discover, build and reassess; reviewer agent.

## Design budget

Vibe 4.0 was written to fix a 4,201-word prompt that restated rules in five places, leaned on prohibitions, and depended on words like "substantial" that it never defined. Those are still the tests for any change: say each rule once, say what to do and why, and tie it to something Claude can observe.
