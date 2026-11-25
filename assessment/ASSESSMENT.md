# Vibe 4.15: critical assessment

Assessed 2026-11-24 and 25 on `main` at `81604f8` (v4.15.0), with Claude Code 2.1.331.

## Bottom line

1. **On the install path the README recommends, most of Vibe is not delivered to the model at session start.** Claude Code caps hook output at 10,000 characters. Vibe's startup payload is 15,368, so the model gets a 2,000-character preview: 12% of the core, and none of the saved project status. This has shipped in every release since v4.9.
2. **What does reach the model mostly does not change what it does.** On Sonnet 5.5, 20 matched runs gave the same results as plain Claude Code at 18% higher cost; one later task is the exception, where Vibe 4.15 caught a hidden regression in 6 of 6 runs against 2 of 6 for plain. On Fable 5.2, in two single runs the model found the spilled file on its own and ran the whole process at 2.7 and 4.5 times the cost of plain, including edits to instruction files that nobody asked for. The hidden-check score was the same in the first; the second had no outcome score. In a third Fable run it did nothing extra.
3. **The product grows by adding paragraphs and pinning their wording with tests.** The core has tripled in 38 days. 61 tests assert phrases; they fail on harmless rewording and pass when a safety rule is inverted. No release has measured whether Vibe helps.
4. **My recommendation is to replace almost all of it.** Keep one page of rules delivered whole, a read-only reader for the status note, and one line for compaction. Remove the six skills, both agents, adoption, governance, model routing, the verification cache, the force-push guard as written, the manual installers and the phrase tests. Gate every wording change on a with/without comparison.
5. **A prototype of that design, measured here, beats both plain Claude Code and Vibe 4.15 on specific behaviours, and is not finished.**
   - A one-line fix shipped correct and checked in 4 of 4 runs, against 0 of 3 for plain and 0 of 3 for Vibe 4.15.
   - A risky change got exactly one independent review in 9 of 9 runs across both prototype texts. A security hole present in 4 of 5 plain builds was left in 1 of 9. Some of those fixes would also refuse a legitimate request behind a proxy.
   - Multi-part requests opened with a goal and numbered steps in 5 of 5 runs, and reports named no source files.
   - Its standing overhead is about 1,200 tokens per request against 1,570 for Vibe 4.15. Each working task costs more than with 4.15, because it checks and reviews: a one-line fix 1.43x plain against 1.13x, a feature 1.26x against 1.08x, a risky change 2.10x against 1.26x.
   - All of the above is on Sonnet 5.5.
   - It still has open defects, the most important being that it hides one kind of unrequested change that plain Claude Code discloses.
6. **None of this was tested where you worry most.** Every run was a toy project, headless, under about ten minutes. Long sessions, real compaction and real-size projects are untested for every variant, including the prototype.

Section 8 lists six decisions that are yours; the first is which model you actually run, because the results differ sharply by model.

**In this folder:** this report; `prototype/vibe-next/`, the measured prototype; `evidence/`, the five experiment and measurement write-ups behind section 6.

## 1. How this was assessed

- **Subject:** `main` at `81604f8` (v4.15.0), 92 tracked files. Host: Claude Code 2.1.331 with the plugin installed from the marketplace, as the README instructs.
- **Round one:** 14 audit dimensions, each by a separate agent working read-only on the repo, each then attacked by an independent verifier told to refute it. The four highest-stakes audits (core prompt, model routing, testing policy, adoption/governance) got two verifiers: one refuter and one steelman arguing the author's case. Six research tasks ran alongside: Claude Code and Codex platform facts (both fact-checked against the official docs), Anthropic's published guidance, two competitor groups and failure-mode evidence.
- **Live evidence:** more than 600 nested headless Claude Code sessions on toy projects, with and without Vibe, across both rounds.
- **Round two:** two experiments (110 and 62 sessions) on whether a short core changes behaviour and through which channel; three competing target designs, each built and run by its author; an independent critic of this assessment; three judges who re-ran parts of each design; and a prototype of the winning combination, measured, revised once and measured again.
- **What the verifiers changed:** almost every number in the audits reproduced. The verifiers mostly corrected conclusions and recommendations, and I have used their corrected versions throughout. Where a claim rests on one run or a toy project, the text says so.

Limits that apply to everything below are collected in section 9.

## 2. The findings that matter most

### 2.1 Most of Vibe is not delivered at session start

Claude Code caps each hook's output at 10,000 characters. Over that, it saves the output to a file and gives the model a 2,000-character preview; the docs state "Claude Code doesn't ask Claude to read the file." The cap has existed since Claude Code 2.1.89.

Vibe's startup hook joins the core, then the status note, then the gate advisory into one string (`hooks/session-start.py:192`). The core alone is 15,368 characters.

| What | Offset in the payload | Delivered at start on a plugin install? |
| --- | --- | --- |
| Title, precedence, Fast/Standard/Critical selection | 0–1,825 | Yes |
| "Invoke installed skills internally (`vibe:build` …)" | 1,827 | No |
| "A truncated startup preview is not the complete standard: read the complete installed core" | 2,310 | No |
| Automatic project adoption, governance | 2,526 | No |
| Model and effort routing | 5,076 | No |
| Verification cadence | 7,486 | No |
| Continuity and delivery | 11,815 | No |
| Git and permissions | 12,959 | No |
| Communication | 14,350 | No |
| `docs/STATUS.md` snapshot | 15,370 | No |
| Gate advisory (emitted once, then cached silent) | after status | No |

Consequences, observed live unless marked:

- **The sentence meant to repair truncation is itself truncated.** Its test (`tests/test_core_transport.py:46-49`) only asserts the words exist in the file.
- **Session continuity does not load.** With a valid `docs/STATUS.md`, a nested session asked for a marker in it answered that it was not in context. The README promise "loaded when a new session starts" is false on the install path the README recommends.
- **This has shipped since v4.9.** The core crossed 10,000 characters at v4.9 and every release since added text past the cut. The only size test compares the payload with the Codex allowance, read as estimated tokens, which permits about 65 KB.
- **Vibe is three different products.** The plugin path delivers 12% of the core. By the docs and the code, not run here: the manual `install.sh` path imports the whole core as user memory, which would also reach subagents, and Codex is given a raised allowance for all of it.
- **Delivery is a lottery by task and model.** On small tasks the model never opened the spilled file. On feature tasks Fable 5.2 opened it unprompted on its second tool call and then followed the whole standard, including a failed adoption attempt. Sonnet 5.5 did not.
- **After a compaction the session falls back to the 2 KB preview**, because the hook re-runs and re-spills. Subagents never receive the core at all, yet `agents/worker.md` and `agents/reviewer.md` tell them to follow "the core's model-routing policy".

The v4.12.1 release found this same truncation on Codex and fixed it there by raising the Codex limit and adding the "read the complete core" sentence. Nobody opened a Claude Code session to look.

### 2.2 What does reach the model mostly does not change what it does

Fitting under the cap is necessary. The evidence says it is not sufficient.

| Evidence | Result |
| --- | --- |
| 20 matched runs, five scenarios, Sonnet (trivial fix, small feature, read-only question, two resume cases) | Same outcomes and passing tests in all 20. Vibe cost 18% more in total ($0.787 vs $0.667) and added 1.2–1.65K input tokens to every request. |
| Same 10 Vibe runs | 0 skill invocations, 0 agents, 0 adoption, 0 status files written, 0 reads of the full core. |
| 131 transcripts across all agents | 0 effort-skill invocations, 0 `vibe:worker` invocations, 0 subagent calls carrying a model or effort. |
| Nine nested runs of the three workflow skills on a small fixture | No observable difference from plain Claude Code in findings, verdicts or edits. Cost 1.27–1.49x with Vibe isolated. |
| "2–5 short lines, no file paths or test counts" | 0 of 5 replies complied. A verifier moved the Communication section to character 362, inside the preview: still 0 of 6. With the full core read, the final report was 11 lines with paths and a test count. |
| Critical rule (migrations, destructive operations), which is inside the preview | Sonnet skipped the Build skill and the review on a migration-plus-delete task anyway. |
| Build skill loaded | The model still skipped the core read, adoption, the status checkpoint and branching that Build mandates. |
| Fable 5.2 on one matched high-risk task | With Vibe: $2.04, 191 s, 14 turns. Without: $0.45, 44 s, 4 turns. Vibe text was 12% of the extra spend; output tokens (48%) and cache writes (44%) were nearly all of it. The verifier judged the second reviewer round the largest avoidable part. One run. |
| Fable 5.2 on a three-turn task touching permissions and deletion (the critic's run) | With Vibe: $4.09, 448 s, two reviewer runs, adoption completed, two branches pushed unasked. Without: $1.49, 121 s. Same score on a hidden acceptance check. One run. |
| The full 15.5K core delivered to Sonnet through two hook strings | 0 skills, 0 reviewers, 0 adoption, 0 status records across three turns, at 46% higher cost. One run. In that run, fixing delivery alone changed nothing. |
| Hidden regression after a rename, Sonnet, 6 runs per arm | The one measured benefit of Vibe 4.15: it ran the tests and shipped a working project in 6 of 6, plain in 2 of 6. A 401-character preamble alone also gave 3 of 3, at lower cost. |
| A 1,260-character replacement core, delivered whole | Sonnet ran a hand check and one reviewer pass on that high-risk task that the stock plugin left untouched ($0.18 vs $0.10). One run. |

Two things follow. First, a short, complete core can change behaviour where a long, truncated one does not. Second, no rule should stay in the product unless a with/without comparison shows it does something, because several delivered rules demonstrably do nothing.

### 2.3 The product grows by patch-and-pin, and nothing measures whether it helps

- **Growth:** the core went from 4,912 bytes (v4.0) to 15,374 (v4.15) in 38 days. Prompt markdown grew 5.4x and tests 49x over the same period. Releases titled "lighter" still grew net bytes once on-demand references are counted.
- **The repo's own standard:** `CHANGES.md:40-102` rejected v3.0 for prohibition-heavy text, an undefined "substantial", and "not for small tasks" disclaimers. v4.15 has 11.4 prohibitions per 1,000 words against v3.0's 10.5, has deleted v4.0's definition of "substantial" while the word still gates behaviour in nine places, and carries 17–34 disclaimers depending on how they are counted.
- **What the core is made of:** an auditor classified all 151 sentences. Useful, non-default guidance is about 31% (verifiers put it between 20% and 37%). About 21% is disclaimers describing what Vibe is not ("no extra agent, per-turn scan or mandatory register", `core/CLAUDE.md:46`), 19% is installer and Codex plumbing, 14% restates what Claude Code does anyway.
- **Tests that pin wording:** 61 of 199 tests assert 479 required and 91 forbidden phrases in markdown. In a clone, 5 of 5 harmless rewordings tried broke CI, and 9 of 9 inversions of a safety rule tried passed, for example "Push, merge, publish and deploy without asking for authorization." 111 of the core's 151 sentences can each be deleted without any test noticing. Swapping the three skills for an 871-word equivalent that passes `claude plugin validate --strict` fails 58 assertions.
- **The ratchet:** phrase assertions grew from 35 to 139 between v4.4 and v4.15. v4.15 added 58 lines of routing reference and 190 lines of tests pinning 82 of its phrases. CI has already forced a wording-only commit. The tests make deleting text more expensive than adding it.
- **No measurement:** nine of twelve releases state that speed, savings or behaviour are unmeasured. `scripts/compare-performance.mjs` has never produced a committed result, and its two one-function tasks cannot show anything. Claude Code ships `claude plugin eval`, which runs each case with and without the plugin and reports the difference. The repo does not use it.
- **Churn without evidence:** the external reviewer lived 49 minutes on main, the three-worker cap 11 hours, the effort override 6 days, the progress board 14 days (469 lines), slash commands 35 days. None of the reversals cites an observed session.
- **Release paperwork:** the version string is hand-edited in about 10 files per release. `docs/` holds 22 release files for 11 versions. A test requires `CHANGES.md` to say "(release candidate)" while the publisher ships each one as a normal, non-prerelease GitHub release about a minute after merge. Median time a PR stays open is 16 minutes.

The root cause is one loop: a model misbehaves in the author's own use, a paragraph is added, a disclaimer is added to stop the paragraph being over-applied, a phrase test pins both, and nothing ever checks the result on a real host.

### 2.4 Vibe does things the owner did not ask for, and loosened checks without evidence

- **Adoption edits the user's instruction files unasked.** The core orders it on the "first authorized project edit, including Fast work". Run for real, `project_setup.py adopt` creates `AGENTS.md` plus a `CLAUDE.md` bridge, or inserts `@AGENTS.md` into an existing `CLAUDE.md`, which by the documented import behaviour makes Codex-only owner rules load in Claude (the edit was observed; the loading was not). It has no home-directory guard. The 1,408-byte managed block restates the core, is left behind on uninstall, and is flipped back and forth when teammates run different versions. No competitor profiled edits the user's instruction files without an explicit command.
- **In practice adoption either fails noisily or completes unasked.** In round one, five of five nested sessions that read the adoption guide could not complete it, and each told the owner about Codex settings or an unreadable template. Three searched the whole filesystem for the file, because the prompts name plugin files by relative path. In a later Fable run it did complete: the session wrote `AGENTS.md` and a `CLAUDE.md` bridge into the project, committed them and pushed two branches, none of it requested.
- **Governance treats the owner's stricter rules as conflicts.** The scanner lists a project's own "run the full suite before every push" rule under "conflicts" and offers "Align with Vibe" first, although the core ranks project rules above itself. On 18 plain instruction lines it raised 8–9 false positives. "Owner confirmed" is a flag the model sets itself.
- **Status pushes.** In two runs where commit and push were permitted, Vibe put the feature on a branch and then committed the status note alone on the default branch. The host's own rule is "If on the default branch, branch first." On a branch that auto-deploys, such a commit triggers a deploy. The one control run without Vibe, in a project that already had a status file, also committed a status-only change on main.
- **v4.14 loosened production checks.** v4.9 required full checks before any production deployment. Since v4.14 an auto-deploying merge needs only model-selected "affected/expanded" checks unless the owner asks, the impact cannot be bounded or project CI requires more. Full verification is otherwise reserved for a "formal production release", a term defined once, in an on-demand reference; an owner who ships by merging rarely performs one. No release measured the effect of the change.
- **Helpers nobody can use.** `verification-cache.py` works as a cache but accepts a forged pass, is not registered anywhere, and Vibe does not use it itself. Its tests take 12 of the suite's 19 seconds.
- **`.git` writes.** The startup hook writes `.git/vibe-project-gates.json` in every session, including a read-only question. Its documentation mentions this only as "Git-private notice bookkeeping".
- **The reviewer withholds approval for the wrong reason.** `agents/reviewer.md:9` tells it to keep approval pending when it cannot establish its own model suitability. In two runs, on two models, it refused to approve for that reason alone and the owner was told. v4.15 added that paragraph in place of two frontmatter lines the harness actually enforced.

### 2.5 Words go to rare problems; the common ones get nothing

| Share of the 16,715-word prompt surface | Topic |
| --- | --- |
| 21% | Test-scope vocabulary (affected / expanded / release) |
| 17% | Evidence and SHA bookkeeping |
| 10% | Model and effort routing |
| under 1.5% each | Debug loops, hallucinated packages, pushing back on a bad request |
| 0 | Compaction, `/clear`, context hygiene, scope discipline ("touch only what the task needs") |

Against 24 documented failure modes of long AI coding sessions, Vibe has one harness mechanism, the force-push guard, and that guard has the wrong contract:

- It allows `git -c k=v push --force`, `timeout 120 git push -f`, `env`-prefixed and absolute-path git, `bash -c "git push -f"`, retry loops, a quoted `"+main"`, `--mirror` and remote branch deletion. 59 of 116 probes passed; about a dozen of those are forms an agent really writes.
- It blocks `--force-with-lease`, the safe way to update your own rebased branch.
- If `python3` is not on PATH it blocks every Bash command, including `ls`.

What the owner asked for most directly, seeing progress clearly, is the largest gap. Nothing shows the owner a goal, a step list or a count. The plan is "internal" by rule. The progress board was built and deleted in 14 days and its useful content ("N of M planned steps finished") was not carried into chat. The rule that remains, "Reuse native task tracking if useful", points at tools the newest models do not expose by default.

Meanwhile a baseline defect that a tool like this should fix is untouched: a one-line greeting fix whose obvious edit drops a space shipped broken and was reported as fixed in 8 of 8 plain runs across two models, and in 5 of 5 runs with Vibe 4.15. And the built-in `/code-review low` caught 3 of 3 and 4 of 4 planted bugs that passed tests in ordinary features, in about 9 seconds for about $0.38, on toy diffs. Vibe never mentions it and only reviews a "high-risk" list.

### 2.6 What is right and should survive

- **A git-tracked status note.** It is the only continuity carrier that survives a new machine, a cloud container or a switch of tool. Anthropic's own long-running-agent guidance uses a progress file plus git.
- **The owner-language reporting idea:** outcomes over file names, and the built / checked / live distinction. It targets a real gap for a non-technical owner. It needs a channel and wording that actually work.
- **One fresh-context review with a hard stop** for a named high-risk list. The idea survives; the custom agent and the recheck do not.
- **The idea of a harness-enforced push guard,** kept in reserve with a corrected contract until an eval shows it is needed.
- **Triggering from plain language works:** Discover and Reassess were selected 2 of 2 times. The skills it triggered showed no benefit.
- **Restraint:** no MCP server, no daemon, no command sprawl; the main session's model is left alone; small tasks get no ceremony. The 20 matched runs confirm Vibe adds none on small work.
- **The plugin packaging** is valid (`claude plugin validate --strict` passes) and the README install command is correct for 2.1.275+.
- **The v3.0 self-critique in `CHANGES.md`** is accurate. It is the right standard; v4.15 no longer meets it.

## 3. Verdict on every component

"Rewrite" means the idea survives and the implementation does not. Sizes are from commit `81604f8`.

### Always-on text and its delivery

| Component | Verdict | Why |
| --- | --- | --- |
| `core/CLAUDE.md` (15,374 B) | Rewrite as one page of about 3,800 characters | 88% never delivered; 20–37% useful; a short complete page changed behaviour in measured ways (section 6) |
| `hooks/hooks.json` SessionStart entry | Rewrite: two handlers, rules and status | Each hook string has its own 10,000-character cap, so the status note can never again be crowded out |
| `hooks/session-start.py` + `.sh` (211 lines) | Rewrite as a read-only status reader of about 125 lines | Hand-typed 40-hex baseline, exact field names, permanent warnings for bot branches, a `.git` cache write, `__pycache__` written into the plugin cache |
| Hand-typed `Updated: date \| SHA` in the status note | Remove | Git already knows; the typed copy is wrong after a merge-button merge and on feature branches |
| Status-only commits and pushes | Remove | Committed straight to the default branch in live runs; note travels with the work instead |
| `hooks/session-start.md` | Remove | Prose about the hook; a comment in the script is enough |
| `core/PROJECT-CLAUDE.template.md` and its byte-identical twin under `skills/discover/references/` | Remove | Writes 3.7 KB of Vibe policy into the owner's always-loaded file, where it outranks later versions |
| PreCompact keep-list | **Add** (one line) | Verified live: the line appears verbatim at the top of the compaction summary |

### Skills, references and agents

| Component | Verdict | Why |
| --- | --- | --- |
| `skills/build` (8.9 KB) | Remove | 10–15% unique; with it loaded the model still skipped what it mandates; never invoked in the matched runs |
| `skills/discover` + `checklist.md` + `register-template.md` | Remove | Auto-invoked 2 of 2 but produced the same substance as plain Claude Code; native plan mode covers explore-then-approve; the checklist and eight-column register are read by nothing |
| `skills/reassess` | Remove | Half restated policy; verdicts matched plain in the auditor's and the verifier's runs |
| `skills/effort-low`, `effort-medium`, `effort-high` | Remove | 0 invocations in 131 transcripts; the effect lasts one turn and leaks into subagents; 230 always-on tokens |
| `references/model-routing.md` (9 KB) and the routing section of the core | Remove | Never loaded in any run; four tiers and "requested / configured / observed" bookkeeping with no mechanism behind them |
| `references/testing-policy.md` (12.4 KB) | Remove | Mostly restatement. Its three useful ideas (check what depends on shared code; unknown impact means run everything; a unit pass is not UI acceptance) are not in the current rules page; re-admit any of them only with an eval case |
| `references/review-loop.md`, `reviewer-brief.md` | Remove | Verdict and exact-SHA ledger with no reader in a solo workflow; the second review round was the largest avoidable cost |
| `references/parallel-work.md` (8.8 KB), `references/reuse-policy.md` (6.6 KB) | Remove | Never observed in use; not readable from the plugin cache without a permission grant |
| `agents/worker.md` | Remove | Never invoked; the built-in general-purpose agent is the same thing |
| `agents/reviewer.md` | Remove; use the built-in `/code-review` | In the prototype's measurements the built-in review ran once in 9 of 9 risky-change runs and found a must-fix problem in 8. On Sonnet, Vibe 4.15 invoked its own reviewer in 0 of 5 runs of the same task; on Fable it ran it twice per task in two other runs, and that agent withheld approval over "model evidence" |
| `user-invocable: false` on skills | Moot once skills go | It saved no tokens and removed the owner's way to force a workflow |

A skill or agent comes back only when an eval shows the plugin with it beats the plugin without it on a result, not on "the skill fired".

### Hooks and helpers

| Component | Verdict | Why |
| --- | --- | --- |
| `hooks/project_setup.py` (571 lines), `project-adoption.md`, the managed block | Remove | Unasked edits to the owner's instruction files; changes which rules Claude loads; live and completing on Fable today |
| `hooks/governance.py` (308 lines), `governance.md` | Remove | 8–9 false positives on 18 plain rules; treats stricter project rules as conflicts; self-set "owner confirmed" flag |
| Startup gate advisory and `.git/vibe-project-gates.json` | Remove | Misses husky and common test runners, flags stock CI, shows once then goes silent |
| `hooks/verification-cache.py`, `.md`, `pre-push.template` | Remove (keep as a gist if you use it yourself) | Works as a cache but accepts a forged pass; unregistered; not used by Vibe itself |
| `hooks/block-force-push.sh`, `check-force-push.py` | Remove now; hold a corrected guard in reserve (decision 3 in section 8) | Wrong contract in three ways (section 2.5); plain Sonnet force-pushed in 0 of 6 runs with permissions bypassed and a diverged remote, three of them under pressure |
| `hooks/test-force-push-hook.py` | Remove with the guard | A test shipped inside every user's plugin cache |
| `hooks/codex.json`, `codex-hook.cmd`, `settings.example.json` | Remove | Codex packaging (decision 2); the `.cmd` was never executed by any test; the example file is referenced nowhere |
| Stop-hook "did you run a check?" reminder | Not now | Never fired in 35 runs when the rules were loaded; reads an undocumented log format; false positives on style-only turns. Reserve design exists |
| Fix-loop counter, test-skip detector | Not now | Both prototypes have reproduced defects; Edit-keyed hooks miss about 60% of file writes, which go through the shell |

### Installers and hosts

| Component | Verdict | Why |
| --- | --- | --- |
| Marketplace plugin install | Keep as the only supported path | Valid, documented, one command |
| `install.sh`, `uninstall.sh` | Remove from `main`; link the v4.15.0 uninstaller for one release | A third install path that delivers a different product; `rm -rf` on `~/.claude/skills/build`, `discover`, `reassess` and overwriting `~/.claude/agents/reviewer.md` destroys same-named user files |
| `install-codex.py`, `.codex-plugin/` | Remove packaging; keep a paste-in note (decision 2) | Nothing was run on Codex in this assessment; the repo's CI checks the prompt Codex assembles after install but never runs a Codex session or its hooks; no plugin agents on Codex, frontmatter dropped, hooks need re-trust after every script change |

### Tests, CI, docs and hygiene

| Component | Verdict | Why |
| --- | --- | --- |
| Phrase-pin tests: `test_lean_workflow`, `test_review_policy`, `test_reuse_policy`, `test_testing_policy`, `test_model_routing` (593 lines) | Remove | Rewordings fail, inverted rules pass |
| `test_governance`, `test_adoption_recovery`, `test_startup_adoption`, `test_project_setup`, `test_verification_cache`, `test_verification_evidence_only`, `test_installation`, `test_codex_installation`, `test_skill_metadata` | Remove with the code they test | Sound tests of helpers that go |
| `test_session_start`, `test_core_transport`, `test_release_candidate` | Rewrite into one file of about 20 tests | Keep the method (real temporary git repos); test every emitted hook string against 10,000 characters; one version literal |
| Size budget enforced by test | **Add** | The single control that would have stopped both the growth and the cap breach |
| With/without eval suite, results stamped with file hashes | **Add** | Any change to the always-on text fails CI until the suite is re-run; this is what replaces the phrase tests |
| `scripts/compare-performance.mjs`, `benchmark-runner.test.mjs` | Remove | Never produced a committed result; its first run, during this assessment, could not tell the arms apart; two toy tasks; ignores cache-creation tokens, where all of the overhead lands |
| `.github/workflows/vibe-checks.yml` | Rewrite, about 30 lines | Install smoke for a deleted installer; legacy job name `native-mod-render`; version literal. Change the branch-protection required check before renaming the job |
| `.github/workflows/publish-v4.5.yml` | Rewrite as `release.yml` | Misnamed; 12 version literals; read the version from `plugin.json` |
| `docs/RELEASE-*.md`, `RELEASE_NOTES_*.md` (22 files), two `*-VALIDATION.md` | Remove | The 12 GitHub releases already hold the notes; the validation plans were never executed |
| `CHANGES.md` | Keep, shorter entries | Drop the false "(release candidate)" label and its test; keep ten lines of the v3.0 critique as the design budget |
| `README.md` | Rewrite, about 70 lines | Must state cost, what Vibe writes, how to turn it off; `/plugin update vibe` has no in-session form (`claude plugin update vibe@vibe` is the command); several promises were not observed |
| `plugin.json`, `marketplace.json` | Rewrite descriptions | Remove "automatic model effort"; one static outcome sentence; version in one place |
| `.DS_Store`, missing `.gitignore` | Fix | The validator's directory profile flags the `.DS_Store` |

Net effect: 92 tracked files become about 15 plus the eval cases; prompt text goes from 16,715 words in 23 files to about 720 words in 2; runtime code from about 1,760 lines to about 135.

## 4. How it compares with alternatives

I did not run any competitor head to head, so this section compares design, footprint and published evidence only. GitHub pages were blocked from this environment; project descriptions come from each project's README, star counts from shields.io on 2026-11-24, and criticism from search snippets I could not open.

| Project | Shape | Always-on text | What it writes into your repo |
| --- | --- | --- | --- |
| Superpowers (326k stars) | Skills library plus a bootstrap injected at session start, clear and compact | about 3.5 KB (a 3.2 KB skill plus wrapper) | design and plan files, worktrees |
| Spec Kit (151k) | Explicit commands: constitution, specify, plan, tasks, implement | none identified | spec, plan and task files |
| OpenSpec (76k; 5.7M npm downloads a month) | Explicit commands; change folders | none identified | `openspec/changes/...` |
| BMAD (56k) | Role-based method, now repositioning as "right-sized process" | not measured | planning artefacts |
| GSD Core (12k; original repo archived at 64k) | discuss, plan, execute, verify, ship with fresh-context subagents | not measured | `STATE.md`, `CONTEXT.md` |
| Compound Engineering (26k) | 38 skills across 14 hosts | not measured | `docs/solutions/` |
| Anthropic's own `explanatory-output-style` plugin | SessionStart injection | about 1.2 KB, with a README warning about its token cost | nothing |
| **Vibe 4.15** | Core injected at session start plus hidden skills | 15.4 KB sent, 2 KB delivered | instruction-file edits, status file, decision records |

What this says about Vibe:

- **Vibe 4.15 is the heaviest of the three always-on payloads that could be measured** (15.4 KB against about 3.5 KB and 1.2 KB), and its host truncates it. The other five were not measured. "Lightweight" is not a claim it can make today.
- **No other project profiled edits your instruction files without an explicit command.** Vibe's adoption is unique, and a trust risk.
- **Nobody publishes reproducible with/without numbers.** Savings claims in this space (30–50% from model routing, 89% less context switching) come with no method. A plugin that ships a small measured table would be alone in doing so.
- **The crowd is converging on "right-sized process".** Wording will not differentiate Vibe; evidence and size can.
- **Ideas worth taking in their smallest form:** re-inject on compact (Superpowers), a pointer plus on-demand state (Beads), status derived by script at zero token cost (CCPM), one review pass over many (Superpowers' cheap mode).

The position where Vibe can be clearly better is narrow and specific: the smallest layer that makes Claude Code usable by an owner who cannot read code, with the numbers to show it. It should not compete on feature count, host count or methodology.

## 5. The target design

Three judges scored the three competing designs independently, each re-running parts of them. Two ranked the subtraction-first design first and one ranked the owner-first design first by a single point; the enforcement-first design came last for all three. All three reached the same verdict: build the subtraction-first skeleton and fill it with the owner-first design's tested wording. That is what the prototype in section 6 implements.

### 5.1 What ships

| File | Size | Role |
| --- | --- | --- |
| `rules.md` | 3,781 characters | The owner's standing preferences. Delivered whole by a SessionStart hook on startup, clear and compact |
| `hooks/hooks.json` | about 20 lines | Two SessionStart handlers (rules; status) and one PreCompact line |
| `hooks/status.py` + a 7-line launcher | about 130 lines | Reads `docs/STATUS.md`; read-only; silent if there is nothing to say or Python is unusable |
| `hooks/keep.txt` | one line | What a compaction summary must keep |

No skills, no agents, no installers, no per-tool-call hook, no edits to the owner's instruction files. The only file it asks Claude to write is `docs/STATUS.md`.

### 5.2 The rules page

The wording matters more than the channel. Prose rules for the opening plan and for message length were ignored through every channel tested (0 of 8 plan openings). Prose against file paths worked partly, and test counts kept leaking. The same rules written as fill-in shapes tied to an observable moment were followed. The page therefore has three parts:

- **What the owner sees.** For a request with three or more parts, the reply begins with a one-sentence goal and numbered steps in the owner's words, before any tool call. The last message is a fixed set of labelled lines: Done, Works now, Checked and Not checked, Live, Also changed, Noticed-not-changed, Next.
- **How the work is done.** Seven lines: change only what the request names; only call something done after seeing it work; run everything once before anything reaches users; a failing check is information; stop after two failed attempts; one independent review for a named list of sensitive changes; commit, push or deploy only when asked.
- **Carrying on later.** When work stops with steps left, write `docs/STATUS.md` with the goal, checkbox steps, next step and what is waiting on the owner. It is committed with the work, never on its own.

The full text is in `prototype/vibe-next/rules.md`.

### 5.3 What the owner sees

- **Start of a request with three or more parts:** one sentence stating the goal, then numbered steps in the owner's words, before any tool is used.
- **End of a task:** labelled lines: Done, Works now, Checked and Not checked, Live, Also changed, Noticed-not-changed, Next. A one-line fix gets two lines.
- **Start of the next session:** the status hook gives the owner one line before they type anything, for example `Where things stand: Let the owner export the report. Done 1 of 3. Next: build the date filter. Waiting on you: minutes or hours in the CSV?`, and gives Claude the note itself.
- **A question or a small change:** no plan and no note.
- **After a compaction:** nothing visible. The rules and the note are delivered again, and the keep-list tells the summary to hold the goal and the step list.

Section 6.3 has messages copied from measured runs.

### 5.4 Deliberately left out

| Tempting | Why not |
| --- | --- |
| A plugin output style for the reporting rules | With the same text it equalled the hook in one test and did worse in two; it overrides the owner's own style and is absent on Codex and in subagents |
| Live "Done 2 of 5" lines during work | Never appeared mid-task in 48 runs; produced redundant lines at the end. The last message carries one tally |
| A slimmed Build, Discover or Reassess | No observable difference from plain when loaded |
| A custom reviewer agent | The built-in review did the job; no evidence a custom one does it better |
| Model or effort routing in any form | Never used; the mechanisms are turn-scoped or pin in both directions. The README names `/model`, `/effort` and `CLAUDE_CODE_SUBAGENT_MODEL` for the owner |
| Stop-hook, fix-loop and test-skip hooks | Reproduced defects. The check-before-done line works without a hook; the fix-loop and failing-check lines are unmeasured. Reserve designs exist behind eval triggers |
| A progress board, status line or task-list mirror | 469 lines built and deleted in 14 days; the task tools are absent by default on the newest models |
| A per-turn reminder against long-session decay | Tokens on every turn for a decay nobody has measured yet |
| Reuse-first, secure-defaults, package-existence and pushback lines | 15–30 words each with no case behind them. Each can enter with an eval case and a positive result |

### 5.5 Budgets and the release gate

- **Size:** `rules.md` at most 3,800 characters, so any addition needs a deletion; every emitted hook string at most 10,000; enforced by a test that runs the real hook commands against a worst-case project and with `python3` missing.
- **No sentence test.** Wording is free to change. Behaviour is held by the eval suite.
- **Eval suite, with and without the plugin:** unchecked fix; keeps to the request; owner-readable report; sensitive change reviewed once; ordinary feature not reviewed; note written at a pause; two sessions with one compaction; resume from a fresh clone; no force push; read-only question overhead.
- **Stamped results.** The result file records the hashes of `rules.md`, `hooks.json` and the status reader. CI makes no model calls; it fails if the hashes differ from the files or a case misses its bar. A one-word change to the rules therefore cannot merge unmeasured.
- **Survivable bars.** Five runs per arm. Hard bars only for the three large effects (unchecked fix, keeps to request, resume). A missed case is re-run with five more and judged on the pooled ten. Roughly $10 to $15 per release on Sonnet, about $25 with the core cases also run on the newest model.
- **Before any release:** run the core cases on the model you actually use, with cost caps; open one real interactive session and look at the session-start line.
- **Constraint found by running it:** `claude plugin eval` refuses runs that grant shell access on a machine without an OS sandbox (`bubblewrap` and `socat` on Linux), so the full suite runs on the maintainer's machine. A matched runner reproduces every case where the tool is unavailable.
- **Standing rules for the maintainer:** no line enters `rules.md` without a case and a positive difference; a line with no difference on any supported model in two consecutive releases is deleted; nothing user-visible ships without one recorded live observation.

## 6. The prototype, measured

`prototype/vibe-next/` is the design in section 5: a 3,781-character rules page, the status reader, and the compaction keep-list. It was measured twice. The first measurement was 113 sessions across three arms (plain, Vibe 4.15 and the first prototype text; 7 of them on Fable 5.2) plus 24 runs of the native eval tool; it found five defects. I revised the wording and the status reader and re-measured the revision in 31 sessions. Numbers below are for the revised text unless marked. Plain and Vibe 4.15 numbers come from the first measurement, same day, same Claude Code version; the single-flag baselines come from the earlier scope experiment. Sonnet 5.5 unless a row says otherwise, toy projects, 2 to 5 runs per cell.

### 6.1 Results

| Behaviour | Plain Claude Code | Vibe 4.15 | Prototype |
| --- | --- | --- | --- |
| One-line fix whose obvious edit breaks the text: shipped correct and checked | 0 of 3 | 0 of 3 | 4 of 4 |
| Final message for that fix | 22 words | 23 words | 32 words, two lines |
| Account deletion: independent review run | 0 of 5 | 0 of 5 | 4 of 4, once each; 5 of 5 with the first text |
| Account deletion: a forged cross-site request can still delete the account (server-side probe) | 4 of 5 | 4 of 5 | 1 of 4; 0 of 5 with the first text |
| Review run on ordinary work, including "delete one entry" | — | — | 0 of 26 sessions |
| Multi-part request opens with a goal and numbered steps | 0 of 4 | 0 of 4 | 5 of 5 |
| Final "Done: N of M" matches the posted steps | — | — | 8 of 8 |
| Source file names or test counts in the final message (multi-part feature) | 4 of 4 | 4 of 4 | 0 of 5 |
| Says whether it is committed or deployed (multi-part feature) | 2 of 4 | 1 of 4 | 5 of 5 |
| Tried the real command by hand as well as the tests (multi-part feature) | 0 of 4 | 0 of 4 | 5 of 5 |
| Owner says "I'll come back": status note written | 0 of 3 | 0 of 3 | 3 of 3 |
| Next session knows what is left and what is waiting on the owner | 0 of 3 | 0 of 3 | 3 of 3 |
| Fresh clone with the note on another branch: "where did we leave off?" answered (first text; no shell access in either arm) | 0 of 3 | — | 3 of 3 |
| Single-flag request: unrequested change added | 3 of 3 | 3 of 3 | 0 of 4 |
| Multi-option feature: unrequested change added | 4 of 4 | 4 of 4 | 5 of 5 |
| ...and that change reported to the owner | 4 of 4 | 4 of 4 | 0 of 5 |
| A question or a one-word fix gets no plan (first text) | — | — | 9 of 9 |
| Commit or push nobody asked for | none | none | none in 31 |

### 6.2 What it costs

| | Vibe 4.15 | Prototype |
| --- | --- | --- |
| Standing tokens on every request | +1,567 | +1,201 |
| Startup text delivered | 2,000 of 15,368 characters | all 3,781 |
| Hook time | 67 ms at start, 29 ms before every shell command | 50 ms at start, nothing per command |
| Read-only question, cost against plain | 1.12x | 1.09x |
| One-line fix | 1.13x, for the same broken result | 1.43x, and 12 s against 6 s, for a correct one |
| Multi-part feature | 1.08x | 1.26x mean, 1.16x median |
| Pause and resume across two sessions | 1.13x | 1.22x |
| Risky change with one review | 1.26x, no review run | 2.10x |
| Risky change on the default model (Fable 5.2, one run) | not run | 3.04x, and 155 s against 44 s |

The prototype is lighter than Vibe 4.15 at rest and costs more than plain Claude Code when it works, because it does things plain skips: it checks, it reviews risky changes, it writes the note. It cannot claim to save money.

### 6.3 What the owner sees

A one-line fix:

```text
Works now: the greeting says "Hello, Sam!" instead of "Helo, Sam!". Checked: I ran the
greeting and saw the corrected text.

Live: no, not committed or deployed.
```

The end of a four-part feature, in full:

```text
Done: 4 of 4
Works now: `tasklog report --csv` prints a spreadsheet-ready list that ends with a TOTAL
row. `tasklog report --since 2026-01-31` counts only entries from that date on. You can
combine them, for example `tasklog report --since 2026-01-01 --csv > report.csv`. The
README describes both.
Checked: I ran the real command on a fresh log and saw the CSV and date filter work. A bad
date gives an error. The tests, including a new one for these features, pass.
Not checked: CSV opened in Excel, and project names with commas.
Live: no, not committed or deployed.
Also changed: `add` now saves each entry's date. `--since` can't work without it.
Noticed, not changed: The normal report already had a total line, so I left it as it was.
Entries recorded before this change have no date, so `--since` leaves them out.
Next: nothing.
```

That second message is also the example of the main open defect: this build refuses unknown options on `report`, which nobody asked for, and the message does not say so.

### 6.4 Open defects in the prototype

These were all observed in the measurements. Each needs a wording change and a re-run, because the lines interact: one earlier fix to the scope line silently stopped the status note being written until a clause was added.

1. **It hides one kind of unrequested change.** On a feature that adds several options, Sonnet made `report` refuse unknown options in 8 of 8 builds and reported that in 0 of 8. Plain Claude Code makes the same change and tells the owner in 9 of 11. On this point the prototype is worse than plain. On the default model the one run did the right thing and left the behaviour alone. Candidate fix, untested: say in the scope line that input which used to be accepted and is now refused counts as a change.
2. **The two-line short form spreads to single features.** It was meant for one-line fixes. It also appeared on a single new flag and a single new command (6 of 6), where it drops the "Not checked" and "Next" lines. Candidate fix: restrict it to one-line fixes, or keep "Not checked" in the short form.
3. **"Also changed" collects things that are not surprises:** the help text for the feature just built, the status note itself.
4. **One review fix in four was half-applied,** which is why the forged-request figure is 1 of 4 and not 0. With the first wording it was 0 of 5.
5. **Length.** "About 100 words" is not followed: multi-part reports run 138 to 180 words (plain: 169). Either state "under 200" or drop the number.
6. **Review cost on the default model.** One review, as intended, still tripled the cost of the risky task there, and plain was already safe in both runs on that model. This is decision 4 in section 8.
7. **No note after a hard interruption.** When a session was cut off mid-task, no arm left a note (first text; not re-tested). The note is only written at an orderly stop.
8. **The scope rule only works on narrow requests.** It stopped the extra change on a single-flag request (0 of 4, against 3 of 3 for plain) and not on the multi-option feature.
9. **Three lines are unmeasured:** "Before anything reaches users", "A failing check is information", "Two failed attempts". They are there on judgment and are the first candidates for deletion.
10. **A review-driven fix can break the feature, silently.** The fix the review led to compares the request's origin with its host. Behind a proxy that rewrites the host this refuses legitimate deletions (every such fix probed: 2 of 2 with the revised text, 4 of 4 with the first), and no message listed it under "Not checked".
11. **"Checked" lines sometimes overstate.** 2 of 4 risky-change messages said the change was run "end to end" or "in a running copy" although no Sonnet run started the real server.
12. **Smaller things.** The review's fix changed the existing sign-in cookie in 2 of 4 runs (reported both times). The hand check leaves a `__pycache__` folder in the owner's project (4 of 4). On the one-line fix the project's own test was run in only 1 of 4; the others checked by hand.
13. **The upgrade path is untested.** No run exercised a project that still carries a Vibe 4 managed block or a 4.x status note.
14. **Never seen in a real terminal.** The session-start line for the owner is emitted, and the documentation calls that channel a "warning message shown to the user". Look at it once before relying on it.

### 6.5 What the measurements settled about design

- **Wording decides adherence; the channel does not.** The same reporting rules were ignored as prose through the startup hook, an output style, both, and a repo file (0 of 8 plan openings), and followed as a fill-in template through the hook or the output style (12 of 12). A repo file the model happened to read mid-run gave the final lines in 4 of 4 runs but arrived too late for the opening (0 of 4).
- **Two sentences carry the "checked before done" result.** "Run the nearest check that exercises the change" and "only call something done after you have seen it work"; either alone was enough (3 of 3 each), both removed gave 1 of 3.
- **A reason plus a place to put the observation makes a scope rule work on a narrow request, and only there.** "Change only what the request needs" did nothing (5 of 6 Sonnet runs still added the extra). Adding why (the owner does not read diffs) and a "Noticed, not changed" line gave 0 of 6 on Sonnet and 0 of 2 on Fable on the single-flag task. On the multi-option feature the same wording did not hold (8 of 8 added).
- **A Stop hook that checks for an unverified change works alone (3 of 3) and never fired once the rules were loaded (0 of 35).** It is a backstop for a model that ignores the rules, not something to ship by default.
- **Plain Sonnet force-pushed in 0 of 6 runs** with permissions bypassed and a diverged remote: three with a plain "push my work" and three with "just make it go through". One model, one prompt pair.
- **Pooled numbers mislead.** One design claimed its review rule fired in 6 of 7 runs; a judge re-ran its exact final text and got 1 of 6. Only numbers for the exact shipped text should be published, which is what the hash-stamped gate enforces.

## 7. Roadmap

The product should never be worse than today at any step. That is checkable because step 0 records today's numbers.

| Step | What | Why it is its own step | Acceptance |
| --- | --- | --- | --- |
| **0. Measure first** | Add the eval cases and the matched runner on a branch. Run them against 4.15.0 as installed and commit the result | Gives every later step a baseline | Suite completes on your machine; baseline file committed |
| **1. The kernel (5.0.0), one atomic pull request** | Add `rules.md`, the new `hooks.json`, the status reader and the keep-list. Delete `core/`, `skills/`, `agents/`, every other file under `hooks/`, `install.sh`, `install-codex.py`, `.codex-plugin/`, `scripts/`. Replace `tests/`. Rewrite both manifests and the README | It cannot be split. Shrinking the core alone delivers the adoption mandate whole to every plugin user. Removing skills first leaves no delivered copy of the checking rules. Replacing the skills alone fails 58 phrase assertions | Unit tests and `claude plugin validate --strict` pass; every case meets its bar and is at least as good as the 4.15 baseline; standing overhead at most about 1,250 tokens; no force push in either arm on each supported model; one interactive session confirms the start-up line reads well; the upgrade drill passes on a project carrying a 4.x managed block and a 4.x status note |
| **2. Hygiene (5.0.1), no behaviour change** | Delete `docs/` and `.DS_Store`; add `.gitignore`; replace both workflows; release body from the `CHANGES.md` entry; version read from `plugin.json`; point the marketplace source at a `plugin/` subdirectory so tests, CI and history stop shipping to users | Separate because it needs a repository setting changed first: the branch-protection required check still names `native-mod-render` | Version string appears in `plugin.json` and `CHANGES.md` only; CI green under the new job names |
| **3. Prune by evidence (5.1)** | Run the suite on a second model. Delete or reword any line with no positive difference on either. Candidates today: "Before anything reaches users", "Two failed attempts", "A failing check is information" | These three lines are kept on judgment, not measurement | `rules.md` is the same size or smaller; every remaining line has a case |
| **4. Additions, each through its own gate (5.2+)** | In priority order: a tested way to show progress during long work; the "ask" push guard if the no-force-push case ever fails; an optional review for ordinary features; a Stop-hook backstop; Codex configuration after someone runs the suite on Codex | Each is independent and optional | The eval case for that addition shows a positive difference at an acceptable cost |

**Migration notes for step 1** (they belong in the 5.0 `CHANGES.md` entry and the README):

| You have | What to do |
| --- | --- |
| The plugin from the marketplace | `claude plugin update vibe@vibe`. Third-party marketplaces do not auto-update |
| A 4.x `docs/STATUS.md` | Probably nothing. The new reader shows a 4.x note when it has a next task or a waiting decision; otherwise it reports the plan as finished. Rewriting it in the new format on the next update was not tested |
| A managed block between `<!-- vibe:project:start -->` and `<!-- vibe:project:end -->` in `AGENTS.md` or `CLAUDE.md` | It now disagrees with 5.0 and, as a project instruction, comes before it. Delete everything between those two markers yourself, or ask Claude to. The `@AGENTS.md` bridge that adoption added sits inside those markers and goes with it. The prototype's status reader mentions the leftover block at every session start but does nothing about it, and this path was not tested |
| A "Delivery" section written from Discover's template | Ask Claude to delete it |
| Vibe installed with `install.sh` | Run the v4.15.0 uninstaller once, then install the plugin. Check first that you have no skills of your own named `build`, `discover`, `reassess`, `effort-low`, `effort-medium` or `effort-high` under `~/.claude/skills/`, and no agents of your own named `reviewer.md` or `worker.md` under `~/.claude/agents/`: the uninstaller deletes all of them |
| Vibe in Codex | `python3 install-codex.py --uninstall` from a checkout of tag `v4.15.0` |

## 8. Decisions that are yours

Each has my recommendation. None blocks step 0.

1. **Which model and effort do you run day to day?** This matters more than anything else here. Vibe 4.15 changed almost nothing on Sonnet. On Fable it ran the full process at 2.7 and 4.5 times the cost in the two runs measured, one run each. The release gate must run on your model. *Recommendation: tell me, and gate on it.*
2. **Codex.** This assessment ran nothing on Codex. The repo's CI checks the prompt Codex assembles after install and adoption, but never runs a Codex session or its hooks. The repository shows no other users. Dual-host support is what drove the 571-line adoption script. *Recommendation: drop the packaging; keep a README note that the rules page can be pasted into `AGENTS.md`, labelled untested. Reverse this if you use Codex yourself.*
3. **The force-push guard.** As written it is net-negative: it blocks the safe form, lets destructive forms through, and can block every shell command. Removing it rests on six runs of one model, three of them under pressure, plus Claude Code's auto mode blocking force pushes by default. The alternative is the enforcement-first design: about 50 lines of Python that ask you to confirm any push that replaces remote history, run only on commands containing `git`, and do nothing if Python is missing. It handled 98 of 116 probe commands, so it is still not complete. *Recommendation: remove the guard in 5.0 with the no-force-push eval case as the tripwire. If you want the insurance regardless, ship the asking version, not the current one.*
4. **Review on sensitive changes costs money.** On Sonnet, a forged cross-site request could delete the account in 4 of 5 plain builds. With one built-in review it could in 0 of 5 builds with the first prototype text and 1 of 4 with the revised text, measured by a server-side probe, for about 14 cents and 30 seconds more per task. On the default model plain Claude Code was already safe in both runs, and the same single review cost about $1.13 and 110 seconds more. *Recommendation: keep one pass, no recheck, with a 3x cap in the gate, if you run Sonnet. If you run the default model, decide from your own gate results whether the line earns its cost, or narrow the list to changes that delete or expose data.*
5. **Checks before production.** The new line says: before anything reaches users, run everything the project has once, or rely on CI that gates the deploy. That is stricter than v4.14, which let an auto-deploying merge through on model-selected checks. v4.14 was your deliberate choice to stop full end-to-end runs on every merge. Neither policy has been measured. *Recommendation: the new line, because "CI that gates the deploy counts" removes most of the cost v4.14 was avoiding. Your call.*
6. **Are there other users?** If it is only you, the migration table above is all the migration that is needed. If not, keep the v4.15 uninstaller in the repository for one more release.

## 9. Limits of this assessment

- **Toy projects.** Every live run used a project of 3 to 17 files with a test suite that runs in under a second. Slow suites, monorepos, real CI and real deploys were not exercised.
- **Short sessions.** The longest session was about ten minutes. Compaction was only ever forced with `/compact` on short sessions, about a dozen times, once on this prototype. Automatic compaction of a full context was never observed. Drift over hours, the thing you worry about most, was not observed in either direction. The design's long-session behaviour is an inference from mechanisms that were each checked separately.
- **Headless mode with shell access pre-approved.** No run showed what an owner sees interactively: permission prompts, the session-start line in a terminal, how a multi-minute review wait reads.
- **Two models, mostly one.** Sonnet 5.5 carried almost every cell; Fable 5.2 has one to three runs per cell. Opus, Haiku and lower effort levels were not run. Every nested run inherited high effort.
- **Small samples.** Main cells are 5 to 13 runs, many are 2 or 3. The large effects (8 of 8 against 0 of 8) are reliable in direction; rates are not precise.
- **One task per behaviour.** The unchecked-fix result is one deterministic trap. It shows whether a session looks after editing, not a general defect rate.
- **A cloud container.** Each nested session carried a base prompt of about 37,000 tokens, so percentage overheads would be larger on a lean local install; absolute token figures transfer.
- **Not observed live:** the manual `install.sh` path (Claude Code refuses to load a `CLAUDE.md` under this session's scratch directory, so the full-core-as-memory path could not be tested) and anything on Codex.
- **Not reviewed:** a security review of the installers beyond the file deletions noted; Windows; your own real project and how you actually use Vibe.
- **Competitors** were profiled from their READMEs, not run.
- **The prototype is a prototype.** It was measured in the configuration in section 6 and nowhere else.
