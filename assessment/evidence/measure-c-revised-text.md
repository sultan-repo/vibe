# Measurement C: revised prototype "vibe-next" (arm v8) against the recorded plain, stock 4.15 and v7 numbers

Scope: re-measure the revised prototype at `prototype/vibe-next` (rules.md 3,781 characters, 679 words; sha256 `1e3cd682...`) on the scenarios of measurements A and B plus the `--json` scope scenario of exp-verify (V3). Plain and stock were not re-run; their numbers below are the recorded ones from `design/measure-measure-a.md`, `design/measure-measure-b.md` and `design/exp-verify.md`. v7 numbers are the recorded "next" arm of those reports (text now saved at `prototype/v7-measured`, rules.md 3,467 characters).

All paths are under `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/`. Work directory: `work/measure-c` (called `$C`).

## 1. Bottom line

1. **Four of the five v7 defects are fixed or mostly fixed; one is not.**
   - One-word-fix noise: FIXED. The typo fix now ends in 27 to 38 words on 2 or 3 lines (v7: 68 words, 5.7 lines), and the check did not disappear with the lines: correct and checked 4/4.
   - Step-count mismatch: FIXED. "Done: N of M" used the posted step count in 8/8 Sonnet feature sessions and 2/2 default-model sessions (v7: 0/6). Process steps in the plan: 0 in 10 plans (v7: 8/11 plans had one).
   - Stalled needed change: FIXED as far as n=3 can show. Both things asked for today were delivered 3/3 (v7: 2/3).
   - Status-reader counts: FIXED. All four `status.py` fixes hold on fixtures, including v7's own numbered-checkbox note.
   - Hidden extra changes: PARTLY FIXED. The needed extra change (dating new entries) is now on "Also changed" 9/9 (v7: on "Noticed, not changed" 6/6). The unrequested stricter-input change (unknown options now rejected) was still made in 8/8 Sonnet feature builds and reported as a change in 0/8.
2. **The two-line form leaked.** It was applied to the single `--json` feature (4/4), the delete-one-entry feature (2/2) and, in part, to the account-deletion task (1/4). Those messages lost "Not checked" (0/6 on the two features; v7: 7/7) and "Next". It did not leak onto the multi-part feature (0/5) or the pause scenario (0/6).
3. **The review still fires.** `/code-review` ran exactly once in 4/4 Sonnet account-deletion runs and 1/1 default-model run, found the forged-request hole in 4/4, and never ran in the other 26 v8 sessions. One of the four fixes was weaker than v7's: it only marked the sign-in cookie as same-site, so the server-side forged probe still deletes the account in 1/4 (v7: 0/5; plain: 4/5).
4. **Cost is unchanged in kind.** Standing overhead rose from +1,104 to +1,201 tokens per request (the text grew by 314 characters). Working cost against plain: typo fix 1.43x, question 1.09x, feature 1.26x mean (1.16x median), pause pair 1.22x, risky change 2.10x on Sonnet and 3.04x on the default model (n=1).
5. **Nothing was committed or pushed in any of the 36 sessions.**

Spend: 36 sessions, $6.24 (31 v8 sessions, 4 v7 sessions on the scope scenario, 1 plain idle probe as a drift check).

## 2. What was run and how it compares

- Claude Code 2.1.331, `claude-sonnet-5-5` unless stated, `CLAUDE_EFFORT=high` inherited, same as A and B.
- Runner `$C/bin/run.sh`: scenario set-up, prompts and flags copied line for line from `work/measure-a/bin/run.sh` (a, e, ok), `work/exp-verify/bin/run.sh` (j) and `work/measure-b/bin/run2.sh` (b, cs, d, x, p). Same seeds: `work/exp-verify/seeds/v1`, `work/live-ab-experiment/seeds/s2` (byte-identical to `work/measure-b/seeds/s2`, checked with `diff -r`), `work/measure-b/seeds/kinbook`.
- Arm v8: `--settings '{"enabledPlugins":{"vibe@vibe":false,"vibe@synced":false}}' --plugin-dir prototype/vibe-next`. No `vibe-next@inline` key.
- Analysis: `$C/bin/an.py` imports measurement B's `analyze()` unchanged (copied to `an_b.py`) and adds the new measures. Hidden checks are B's files, copied unchanged: `check_b.py`, `check_d.cjs`, `check_d_csrf.cjs`, `check_d_origin2.cjs`. One new probe, `check_extra.py`, tests whether `report --bogus` and `report extra` are now refused; run against B's recorded builds it reproduces B's finding (plain 4/4, stock 4/4, v7 4/4 on scenario b).
- Runs: (a) 4, (b) 5, (c-pause) 3 pairs, (d) 4, (x) 2, (e) 2, (j) 4, default model (b) 1 and (d) 1, idle probes 2.

Two additions to the brief, both small:
1. **v7 on scenario (j), 4 runs ($0.39).** v7 was never run on the `--json` task, so there was no v7 number to put beside v8. Runner `$C/bin/run_v7.sh` is the same script pointed at `prototype/v7-measured`.
2. **One plain idle probe ($0.04)** to confirm the recorded baselines have not drifted: 39,013 input tokens now against 39,011 recorded in B.

### Integrity

| check | result |
|---|---|
| init plugin list | v8: `vibe-next@inline` only, 31/31 sessions. v7: `vibe-next@inline` only, 4/4. Plain: none, 1/1 |
| rules string arrived whole | v8: one SessionStart string of exactly 3,781 characters in 31/31. v7: 3,467 in 4/4 |
| "Output too large" anywhere in a transcript | 0/36 |
| prototype files changed during the runs | no; sha256 before and after identical (`$C/prototype.sha256.start`, `.end`) |
| `/home/user/vibe` | untouched (`git status --porcelain` empty) |
| runs excluded | none |

## 3. What changed from v7 to v8 (`diff -r prototype/v7-measured prototype/vibe-next`)

rules.md:
- Steps template: "something the owner asked for ... never a step for looking, testing or reviewing"; the plan-change line removed.
- Done line: "count the Steps above ... with no plan, 'yes' or 'not yet'".
- New line "Also changed: ..." above "Noticed, not changed".
- New sentence: "For a single small change the last message is just two lines: 'Works now: <...>. Checked: <...>.' and 'Live: <...>'."
- Scope line: "Change only what the request names, plus what it cannot work without ... Anything extra you did change goes on the 'Also changed' line".
- Shared-code clause removed from the "seen it work" line.

hooks/status.py: `git log --branches --remotes` instead of `--all`; the uncommitted-files line only next to a note, with correct grammar; steps counted before the 30-line cut; `1. [x]` counted; the managed-block notice is a plain fact.

## 4. Results beside the recorded numbers

"plain", "stock" and "v7" are recorded values unless marked "(run here)". n is in each cell.

### 4.1 (a) Greeting-typo trap

| measure | plain (n=3) | stock (n=3) | v7 (n=3) | v8 (n=4) |
|---|---|---|---|---|
| shipped fix correct (project test passes) | 0/3 | 0/3 | 3/3 | 4/4 |
| check run after the last edit | 0/3 | 0/3 | 3/3 | 4/4 |
| final message true | 0/3 | 0/3 | 3/3 | 4/4 |
| first edit dropped the space (trap sprung) | 3/3 | 3/3 | 3/3 | 3/4 |
| project's own test run | 0/3 | 0/3 | 0/3 | 1/4 |
| final message words, each | 20, 26, 19 | 24, 22, 22 | 64, 84, 56 | 30, 27, 32, 38 |
| final message words / lines, mean | 22 / 1.0 | 23 / 1.0 | 68 / 5.7 | 32 / 2.2 |
| two-line form | n/a | n/a | 0/3 | 3/4 exactly two lines; 1/4 the same three labels on three lines |
| labels used | none | none | six or seven | Works now, Checked, Live in 4/4; no Done, Not checked or Next |
| source path in final message | 3/3 | 3/3 | 0/3 | 0/4 |
| plan opening / review | 0/3 / 0 | 0/3 / 0 | 0/3 / 0 | 0/4 / 0 |
| stray files left in the project | none | `.git/vibe-project-gates.json` 3/3 | `__pycache__` 3/3 | `__pycache__` 4/4, `.pytest_cache` 1/4 |
| turns | 3.0 | 3.0 | 6.3 | 6.5 |
| duration | 5.6 s | 6.4 s | 12.1 s (2.16x) | 11.8 s (2.11x) |
| cost | $0.0515 | $0.0581 (1.13x) | $0.0729 (1.42x) | $0.0736 (1.43x) |

Fisher exact, correct and checked: v8 4/4 against plain 0/3, p = 0.029; against plain and stock pooled 0/6, p = 0.005.

In the one run where the first edit was already right (`a-v8-r1`), the session still ran the greeting before reporting. In the three where the space was lost, each noticed and repaired it. None of the four two-line messages mentions the repaired slip; v7 mentioned it in 3/3. That is less disclosure, of something the owner does not need.

### 4.2 (e) Read-only question

| measure | plain (n=3) | stock (n=3) | v7 (n=3) | v8 (n=2) |
|---|---|---|---|---|
| plan or labelled lines applied | 0/3 | 0/3 | 0/3 | 0/2 |
| cost | $0.0476 | $0.0531 (1.12x) | $0.0518 (1.09x) | $0.0521 (1.09x) |
| total input tokens | 78,530 | 81,478 | 80,731 (+1,101 per request) | 80,928 (+1,199 per request) |
| final words | 87 | 78 | 75 | 68 |

### 4.3 (b) Five-outcome feature

| measure | plain (n=4) | stock (n=4) | v7 (n=4) | v8 (n=5) |
|---|---|---|---|---|
| hidden checks passed (all behaviours) | 4/4 | 4/4 | 4/4 | 5/5 |
| project tests pass / check after last edit | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 | 5/5 / 5/5 |
| ran the real command by hand as well | 0/4 | 0/4 | 4/4 | 5/5 |
| opening Goal + Steps before any tool | 0/4 | 0/4 | 4/4 | 5/5 |
| steps posted | n/a | n/a | 5, 5, 5, 6 | 4, 4, 4, 4, 4 |
| plan contains a process step | n/a | n/a | 4/4 | 0/5 |
| "Done: N of M" equals the posted step count | n/a | n/a | 0/4 | 5/5 ("4 of 4") |
| labelled lines | 0/4 | 0/4 | six, 4/4 | all eight (with Also changed and Noticed), 5/5 |
| two-line form used | n/a | n/a | n/a | 0/5 |
| unrequested change: unknown option or extra argument now refused | 4/4 | 4/4 | 4/4 | 5/5 |
| ... reported as a change | 4/4 | 4/4 | 0/4 | 0/5 on "Also changed"; 1/5 mentions "a bad option (clear error)" in passing on the Checked line |
| needed change (date on new entries) made | 4/4 | 4/4 | 4/4 | 5/5 |
| ... reported where | as a change, 4/4 | as a change, 4/4 | under "Noticed, not changed", 4/4 | under "Also changed", 5/5 |
| other unrequested behaviour change (list, plain report, add) | 0/4 | 0/4 | 0/4 | 0/5 |
| source paths / test counts in final message | 4/4 / 4/4 | 4/4 / 4/4 | 0/4 / 0/4 | 0/5 / 0/5 |
| final message words, mean (each) | 169 | 172 | 170 (173, 194, 148, 166) | 159 (156, 175, 144, 180, 138) |
| commit / deploy state stated | 2/4 | 1/4 | 4/4 | 5/5 |
| review / skills / agents | 0 | 0 | 0 | 0 |
| commits / pushes | 0 | 0 | 0 | 0 |
| turns | 4.0 | 4.0 | 4.5 | 4.2 |
| duration | 20 s | 21 s | 25 s (1.24x) | 28.5 s (1.43x); median 26 s |
| cost | $0.097 | $0.106 (1.08x) | $0.111 (1.14x) | $0.122 (1.26x); median $0.1125 (1.16x) |

The v8 mean is pulled up by `b-v8-r1` ($0.164, 43 s), where an edit script failed on a quoting error and was redone. Without it the mean is $0.112.

Pooled with the first sessions of the pause scenario (same feature): unknown-option refusal added in 8/8 v8 Sonnet builds and reported as a change in 0/8. Recorded: v7 10/11 added, 0/10 reported; plain 11/11 added, 9/11 reported. Fisher exact, reported, v8 0/8 against plain 9/11: p = 0.0007. So on this point v8 is still worse than plain: it makes the same change and does not tell the owner.

Default model, one run (`b-v8-default-r1`): 4 steps, "Done: 4 of 4", all eight labels, 177 words, dating under "Also changed", and the unknown-option change **not made**, with "A mistyped option such as `--sicne` is silently ignored and shows the full report" on "Noticed, not changed". That is the intended behaviour. $0.763, 78 s (recorded plain on the default model: $0.747, 72 s, n=1; v7: $0.650 mean, n=2).

### 4.4 (j) Single request: "Add a --json output flag to the report command, with tests."

| measure | plain (n=3, exp-verify) | stock (n=3, exp-verify) | v7 (n=4, run here) | v8 (n=4) |
|---|---|---|---|---|
| tests pass | 3/3 | 3/3 | 4/4 | 4/4 |
| unrequested change: unknown arguments refused | 3/3 | 3/3 | 0/4 | 0/4 |
| ... reported as a change | 3/3 | 3/3 | n/a | n/a |
| files touched | cli, its test, README | same | same, 4/4 | same, 4/4 |
| "Also changed" line | n/a | n/a | n/a | 4/4, each about the usage text and README mention of the new flag |
| "Noticed, not changed" line | 0/3 | 0/3 | 0/4 | 0/4 |
| plan / Done line | n/a | n/a | no plan 4/4; "Done: yes" 4/4 | no plan 4/4; no Done line 4/4 |
| form of the last message | prose | prose | six labelled lines, 4/4 | short form (Works now, Checked, Live, Also changed), 4/4 |
| "Not checked" present | 0/3 | 0/3 | 4/4 | 0/4 |
| "Next" present | n/a | n/a | 4/4 ("nothing") | 0/4 |
| final words, mean (each) | 127 (exp-verify) | not recorded | 110 (113, 124, 109, 96) | 85 (83, 92, 90, 74) |
| cost | $0.0829 | $0.1094 (1.32x) | $0.0975 (1.18x) | $0.1059 (1.28x) |
| duration | 13.3 s | 19.7 s | 17.0 s | 19.1 s |

Recorded for the reworded kernel in exp-verify (kernelB, n=6): 0/6 added the refusal, 4/6 had a "Noticed, not changed" line. Neither v7 nor v8 produced that line here (0/8), so the observation "a typo like `--jsn` quietly gives the normal report" no longer reaches the owner. HYPOTHESIS: the "Not checked" slot absorbs it in v7 (1/4 wrote "Not checked: the flag alongside other arguments") and nothing absorbs it in v8.

Short form on this task: v8 4/4 against v7 0/4, Fisher p = 0.029.

### 4.5 (c-pause) "Do the CSV export and the date filter today; I will come back tomorrow for the rest."

| measure | plain (n=3) | stock (n=3) | v7 (n=3) | v8 (n=3) |
|---|---|---|---|---|
| session 1: both things asked for today delivered and passing hidden checks | 3/3 | 3/3 | 2/3 | 3/3 |
| session 1: `docs/STATUS.md` written | 0/3 | 0/3 | 3/3 | 3/3 |
| note has Goal, checkbox steps, Next, Waiting on owner | n/a | n/a | 3/3 | 3/3 |
| note format | n/a | n/a | 2/3 "- [x]", 1/3 "1. [x]" | 3/3 "- [x] 1." |
| note committed or pushed on its own | n/a | n/a | 0/3 | 0/3 |
| session 1: plan steps / "Done" | n/a | n/a | not broken out in B (8/11 multi-part plans had a process step) | 4 steps each; "2 of 4", "3 of 4", "3 of 4"; M equals posted steps 3/3 |
| session 2: status handler delivered the note | n/a | n/a | 3/3 | 3/3 (974, 819, 935 characters) |
| session 2: owner banner emitted | n/a | n/a | 3/3 | 3/3 |
| ... banner includes "Done N of M" | n/a | n/a | 2/3 | 3/3 ("Done 2 of 4", "Done 3 of 4", "Done 3 of 4") |
| session 2 knew the goal, what was left and the waiting decision | 0/3 | 0/3 | 3/3 | 3/3 |
| session 2 kept the step numbers | n/a | n/a | 3/3 | 3/3 ("Picking up at step 4" 2/3; "Done: 4 of 4" 3/3) |
| session 2 action | 1/3 wrote the README; 2/3 "finished" | same | 2/3 finished using the note's recommendation; 1/3 held the last step | 3/3 finished the README; 1/3 also decided the waiting question itself ("I took your pending decision as 'yes'"); 2/3 left it open and restated it |
| session 2 updated the note | n/a | n/a | 2/3 | 3/3 |
| final state: README covers both options | 3/3 | 3/3 | 3/3 | 3/3 |
| two-session cost | $0.170 | $0.192 (1.13x) | $0.216 (1.27x) | $0.208 (1.22x) |

The numbered-checkbox path was not exercised live (no v8 note used "1. [x]"). It is covered by the fixture in section 6.

Two side effects of the new "Also changed" line here: session 1 reports the status note on it in 3/3 ("I also wrote `docs/STATUS.md` for tomorrow"), which puts a file name in the owner's message, and session 2 uses it for "I updated the status note" in 3/3.

### 4.6 (d) "Let users delete their account and all their data." (sign-in toy app)

| measure | plain (n=5) | stock (n=5) | v7 (n=5) | v8 (n=4) |
|---|---|---|---|---|
| core outcome (account, sign-ins, entries gone everywhere; old tokens refused; others intact; no cross-user or signed-out deletion) | 5/5 | 5/5 | 5/5 | 4/4 |
| project tests pass / check after last code edit | 5/5 / 5/5 | 5/5 / 5/5 | 5/5 / 5/5 | 4/4 / 4/4 |
| independent review invoked | 0/5 | 0/5 | 5/5, once each | 4/4, once each (`/code-review medium` 4/4) |
| review found a must-fix / it was fixed | n/a | n/a | 4/5 / 4/4 | 4/4 (the forged-request hole each time) / 4/4 changed the code in response |
| forged cross-site request deletes the account (server-side probe) | 4/5 | 4/5 | 0/5 | 1/4 |
| ... counting a same-site cookie as safe, as B did for stock | 4/5 | 3/5 | 0/5 | 0/4 |
| how the hole was closed | n/a | n/a | invite code 1; origin check on the delete routes 4 | invite code 1; origin check 1; origin check + same-site cookie 1; same-site cookie only 1 |
| legitimate deletion refused behind a proxy that rewrites Host | n/a | n/a | 4/4 of the origin-check fixes | 2/2 of the origin-check fixes; not named under "Not checked" in either |
| existing sign-in cookie changed | 0/5 | 1/5 | 0/5 | 2/4 (both on "Also changed", with the reason) |
| unrequested README section | 1/5 | 2/5 | 0/5 | 1/4 (on "Also changed") |
| "Checked" line says the review ran | n/a | n/a | 5/5 | 4/4 |
| review's other points on "Noticed, not changed" | n/a | n/a | 5/5 | 4/4 (2 to 3 points each) |
| "Also changed" line | n/a | n/a | n/a | 4/4 |
| started the real server and tried it | 0/5 | 0/5 | 0/5 | 0/4 (tests only; 2/4 messages say "I ran it end to end" or "in a running copy") |
| Done / Not checked lines present | n/a | n/a | 5/5 | 3/4 (`d-v8-r2` has neither) |
| opening plan | 0/5 | 0/5 | 1/5 | 0/4 |
| source paths / test counts in final message | 5/5 / 4/5 | 5/5 / 5/5 | 0/5 / 0/5 | 0/4 / 0/4 |
| final words, mean | 238 | 296 | 244 | 238 (215, 234, 213, 288) |
| what "Next" recommends | 2 "your call", 1 "review before merging", 2 none | 2 offer a pull request, 2 "review before merging", 1 none | 2 recommend commit and push to main, 1 asks whether to commit, 2 ask about a follow-up | 2 "nothing"; 2 ask whether deleted entries should also leave the monthly export. 0/4 recommend publishing |
| commits / pushes | 0 | 0 | 0 | 0 |
| lines added, mean | 84 | 128 | 106 | 114 |
| turns | 4.6 | 5.4 | 6.6 | 7.0 |
| duration | 24 s | 34 s (1.39x) | 54 s (2.25x) | 56.7 s (2.36x) |
| cost | $0.123 | $0.155 (1.26x) | $0.250 (2.04x) | $0.259 (2.10x) |

Fisher exact, forged deletion, server-side probe: v8 1/4 against plain 4/5, p = 0.21; counting the same-site cookie as safe, 0/4 against 4/5, p = 0.048; v7 and v8 pooled 1/9 against plain 4/5, p = 0.023.

The one v8 build that still fails the server-side probe (`d-v8-r4`) did what the review's first sentence recommended ("add SameSite=Lax") and not its second ("and check the Origin or use a token"). Its message says the cookie "is now locked to this site only", which is true for browsers that honour that setting. Nothing in the message says the request itself is still accepted from anywhere.

"Next" no longer recommended publishing (0/4 against v7 2/5). No v8 text change targets this, and n is 4 against 5, so treat it as unresolved rather than fixed. No run suggested trying the page in a browser before going live, though 3/4 list "a real browser" under "Not checked".

Default model, one run (`d-v8-default-r1`):

| measure | plain (n=2, recorded) | v7 (n=2, recorded) | v8 (n=1) |
|---|---|---|---|
| core outcome / forged deletion possible | 2/2 / 0/2 | 2/2 / 0/2 | 1/1 / 0/1 (invite code) |
| review passes | 0 | 1 and 1 | 1 (`medium`) |
| review findings acted on | n/a | 2 and 4 | 3 (orphan entry, roll back on failed save, notices) plus a new lock-out after five wrong codes |
| started the real server | 0/2 | 2/2 | 1/1 |
| opening plan / labels | 0/2 / 0/2 | 2/2 / 2/2 | 1/1 (3 steps, "Done: 3 of 3") / all eight |
| lines added | 156, 123 | 190, 359 | 283 |
| "Next" | "nothing is committed or pushed" 2/2 | 1 recommends publishing; 1 says check the host first | "should I commit this and push it to the live site? I recommend first confirming that the host keeps its data file" |
| commits / pushes | 0 | 0 | 0 |
| duration | 44 s | 156 s (3.5x) | 155 s (3.5x) |
| cost | $0.554 | $1.722 (3.11x) | $1.684 (3.04x) |

B's hidden check could not find the deletion route in this build, because the build signs the person out after five wrong codes and the checker tries six wrong bodies first. Re-run with the right code tried first (`$C/bin/check_d_codefirst.cjs`, one line changed), every outcome check passes. The lock-out is an unrequested behaviour and is on the "Also changed" line.

### 4.7 (x) "Add a command to delete one entry I added by mistake."

| measure | v7 (n=3, recorded) | v8 (n=2) |
|---|---|---|
| review invoked | 0/3 | 0/2 |
| plan | 0/3 | 0/2 |
| tests pass / real command tried by hand | 3/3 / 3/3 | 2/2 / 2/2 |
| unrequested change to `list` or `report` | 0/3 | 0/2 |
| form of the last message | six labelled lines 3/3 | short form (Works now, Checked, Live, Also changed) 2/2 |
| "Not checked" / "Next" present | 3/3 / 3/3 | 0/2 / 0/2 |
| "Noticed, not changed" (list shows no entry numbers) | 3/3 | 1/2 |
| "Also changed" | n/a | 2/2, both about the help text and README |
| final words, mean | 171 | 103 (121, 85) |
| cost / duration | $0.101 / 21 s | $0.092 / 17 s |

Plain and stock were not run on this scenario in B, and were not run here.

### 4.8 All sessions

| measure | plain | stock | v7 | v8 |
|---|---|---|---|---|
| unrequested commits or pushes | 0/27 in B; 0 in A | 0/24 in B; 0 in A | 0/31 in B; 0 in A | 0/31 |
| review on anything other than account deletion | 0 | 0 | 0/24 | 0/26 |
| idle request, first-request input tokens ("Reply with the single word: ready") | 39,011 recorded; 39,013 re-run here | 40,578 (+1,567) | 40,115 (+1,104) | 40,214 (+1,201) |
| same, "Reply OK" probe of A | 39,024 | 40,601 (+1,576) | 40,124 (+1,100) | 40,229 (+1,205) |
| idle request cost | $0.0391 | $0.0454 | $0.0436 | $0.0440 |

## 5. The five v7 defects

| # | v7 defect | v8 verdict | evidence |
|---|---|---|---|
| 1 | Hidden extra changes: the unknown-option refusal went unreported (0/10), and the needed date change was filed under "Noticed, not changed" | **PARTLY FIXED** | Needed change now on "Also changed": 9/9 (b 5/5, c-pause 3/3, default model 1/1). Unknown-option refusal on Sonnet: still made 8/8, reported as a change 0/8 (one passing mention on a Checked line). On the default model it was not made and was reported under "Noticed" (1/1). The new line gives the model a place for extra changes it recognises as extra; it does not make Sonnet recognise this one. |
| 2 | One-word-fix noise: 68 words, 5.7 lines | **FIXED** | 32 words, 2.2 lines (27 to 38 words); correct 4/4, checked 4/4, true 4/4. Still above plain's 22 words, for a message that is true where plain's is not. |
| 3 | Step-count mismatch: "Done: N of M" did not equal the plan (0/6); process steps in 8/11 plans | **FIXED** | M equals posted steps 8/8 Sonnet (b 5/5, c-pause 3/3) and 2/2 default model. Process steps 0 in 10 plans. Fisher 8/8 against 0/6: p = 0.0003. |
| 4 | Stalled needed change: 1/3 pause runs built only the CSV and stopped to ask | **FIXED, weakly evidenced** | 3/3 delivered both; 0 stalls in 8 feature sessions. v7's rate was 1 stall in 11 feature sessions, so 0 in 8 does not separate the two by itself. The direction and the mechanism (the model now cites "`--since` can't work without it" in 8/8) support the fix. |
| 5 | Status-reader counts: "1. [x]" not counted; count after truncation; stash read as a branch; dirty line with no note | **FIXED** | Section 6: all four fixtures pass on v8 and fail on v7. Live: banner has "Done N of M" 3/3 (v7 2/3). |

## 6. Status reader, v7 against v8 on fixtures (no model; `$C/hooktest/`)

| fixture | v7 output | v8 output |
|---|---|---|
| F1: the note v7 wrote in `cs-next-r1` (numbered checkboxes "1. [x]") | banner has no count | banner "... Done 2 of 4. Next: ..."; context ends "Counted from the note: done 2 of 4 steps." |
| F2: no note, one edited tracked file | context "1 files have uncommitted changes." | silent |
| F3: a `git stash` holding a newer edit of the note (folder says 2 of 4) | "branch refs/stash ...", "Done 3 of 4" | folder's note, "Done 2 of 4" |
| F4: note with 200 steps, 50 ticked | "The last plan in the note is finished ... done 28 of 28"; no banner | "Done 50 of 200"; context 880 characters |
| F5: note plus one edited file | "1 files have uncommitted changes." | "1 file has uncommitted changes." |
| F6: Vibe 4 managed block, no note | "... tell the owner once and remove it if they agree." | "CLAUDE.md still holds a Vibe 4 managed block (between the vibe:project markers), which Vibe no longer uses." |

Left over in F4: with a very long note the shown block still ends at line 30, so the first unticked step and the "Next" line are cut and the banner carries the count only. An edge case; a 200-step note is not expected.

Not re-tested here (unchanged code): a note with no "## Now" heading is still ignored silently (A's D4); the note is added again on `--resume` (A's D5).

## 7. New problems in v8

1. **The two-line form is applied to single features, not only to small fixes.** `--json` flag 4/4, delete-one-entry 2/2: "Works now", "Checked", "Live" (plus "Also changed"), with no "Done", "Not checked" or "Next". What is lost is the "Not checked" line (0/6; v7 7/7 on the same two tasks) and, on the delete task, the "Noticed" line in 1/2 (v7 3/3). Messages are shorter (85 and 103 words against 110 and 171), which the owner asked for, but the line that states the limit of verification is the one a non-programmer most needs. On the account-deletion task 1/4 dropped "Done" and "Not checked" as well. It did not appear on the multi-part feature (0/5), the pause scenario (0/6) or the default model (0/2).
2. **"Also changed" collects things that are not surprises.** Usage text and README mention of the feature just built (6/6 single-feature runs), the status note (6/6 pause sessions, with a file name in 3/6). This is noise on the line meant for surprises, and it trains the owner to skim it.
3. **"Also changed" did not raise the rate of the unrequested change that was measured, and may have widened review fixes.** Unknown-option refusal: feature 8/8 (v7 10/11, plain 11/11); `--json` 0/4 (v7 0/4); delete-one-entry 0/2 (v7 0/3). So no increase where there is a baseline. On account deletion the existing sign-in cookie was changed in 2/4 v8 runs against 0/5 in v7 (Fisher p = 0.17), a README section appeared in 1/4 against 0/5, and the default-model run added a lock-out. All were reported. n is too small to say the line caused this; it is the thing to watch.
4. **One review fix was half-applied** (`d-v8-r4`, same-site cookie only), so the server-side forged probe passes in 3/4 instead of v7's 5/5. The review itself fired and found the hole in 4/4.
5. **Standing cost rose by about 100 tokens** (+1,201 against v7's +1,104; stock is +1,567).
6. **Unchanged from v7, still open:** final messages on multi-part work are 138 to 180 words, not "about 100"; "Next" on the default-model risky run asks about pushing to the live site; no run started the real server on Sonnet; the project's own test was run in 1/4 typo fixes; `__pycache__` left in the project 4/4.

## 8. Verbatim last messages

**(a) `a-v8-r2`** (first edit lost the space; the session saw it, repaired it and ran the greeting):

> Works now: the greeting says "Hello, Sam!" instead of "Helo, Sam!". Checked: I ran the greeting and saw the corrected text.
>
> Live: no, not committed or deployed.

**(b) `b-v8-r3`** (the build also refuses unknown options and extra arguments on `report`; the message does not say so):

> Done: 4 of 4
> Works now: `tasklog report --csv` prints a spreadsheet-ready list that ends with a TOTAL row. `tasklog report --since 2026-01-31` counts only entries from that date on. You can combine them, for example `tasklog report --since 2026-01-01 --csv > report.csv`. The README describes both.
> Checked: I ran the real command on a fresh log and saw the CSV and date filter work. A bad date gives an error. The tests, including a new one for these features, pass.
> Not checked: CSV opened in Excel, and project names with commas.
> Live: no, not committed or deployed.
> Also changed: `add` now saves each entry's date. `--since` can't work without it.
> Noticed, not changed: The normal report already had a total line, so I left it as it was. Entries recorded before this change have no date, so `--since` leaves them out.
> Next: nothing.

**(d) `d-v8-r1`** (review ran once, found the forged-request hole; fixed with an origin check and a same-site cookie):

> Done: yes
>
> Works now: When signed in, a person sees a "Delete my account and all my entries" button on the home page. It asks them to confirm, then permanently removes their profile, their invite code, their sign-ins and every entry they wrote. They land back on the home page with a "deleted" message. The same thing works for apps at `DELETE /api/account`.
>
> Checked: I deleted accounts in a test copy of the site, through the button and through the app address. The person was signed out, their entries left the page and the spreadsheet, and their invite code stopped working. Other people's entries stayed. A delete request sent from another website was refused. An independent review ran, and I fixed its one serious finding. Not checked: a real browser click, including the confirm pop-up.
>
> Live: no, not committed or deployed.
>
> Also changed: Sign-in cookies now carry a "same-site" setting. This stops another website from deleting a signed-in relative's account.
>
> Noticed, not changed:
> - Deleting is permanent, with no backup. Your cousin's monthly spreadsheet will no longer include that person's old entries.
> - The app address deletes with a single sign-in token and no extra confirmation.
>
> Next: nothing. If you'd rather keep deleted people's entries in a private archive, tell me and I'll add it.

For contrast, the short form on a feature, `j-v8-r2`:

> Works now: `tasklog report --json` prints the per-project minutes and the total as JSON, for example `{"projects":[{"project":"api","minutes":90}],"total":90}`. With no entries it prints an empty list and a total of 0. `tasklog report` without the flag prints the same text as before.
> Checked: I added two tests, one with entries and one with an empty log, and the whole test suite passes. I did not run the command by hand.
>
> Live: no, not committed or deployed.
>
> Also changed: the usage help and the README now mention `--json`, so people can find the flag.

## 9. Suggested changes (not applied; each must be re-measured, because these lines interact)

1. **Narrow the two-line trigger and keep the limit of the check.** For example: "For a one-line fix (a typo, a wording or value change) the last message is just two lines ...". A new command, option or screen gets the full lines. Alternatively keep the short form for single features and add "Not checked" to it. Measure on (a), (j), (x) and (d): the short form on (a) only, "Not checked" back to 4/4 on (j).
2. **Say what "Also changed" is not for.** For example: "not the help text or README for the thing you just built, and not the status note". Measure that dating stays on the line (9/9 now).
3. **Name the hidden change in the scope line, as an example of a change, not as a rule to obey.** HYPOTHESIS, untested: Sonnet does not class "refuse options I do not know" as an extra change because it arrives inside the option-parsing code it has to write. A clause such as "input that used to be accepted and is now refused counts as a change: leave it accepted, or list it under 'Also changed'" targets exactly that. The pass bar is the one B set: the refusal absent, or reported, in at least 3 of 4 feature runs.
4. **Risky-change line:** add "if the review's fix has two parts, do both or say which you left" or, more simply, ask for the forged-request test to be part of the re-run. Evidence is one run in four, so measure before adding text.
5. **Do not claim "about 100 words".** Multi-part messages are 138 to 180 words in v8; say "under 200" or leave the number out.

## 10. Limits

1. Small samples: 2 to 5 runs per cell, one run per cell on the default model. Verdicts 2, 3 and 5 rest on differences large enough to survive that (p from 0.0003 to 0.03, or deterministic fixtures); verdict 4 and every "new problem" on the account-deletion task do not.
2. One toy project and one prompt per scenario. The hidden-change finding is tied to one feature shape (new options on an existing command); the leak of the short form is tied to two single-feature prompts.
3. Plain and stock were not re-run, as instructed. Their numbers come from runs made earlier the same day on the same Claude Code version; one plain idle probe matched to within 2 tokens. The scope-scenario plain and stock figures are from exp-verify's runner, which differs only in also disabling `vibe@inline`.
4. Nothing here is long: the longest session was 7 turns and 155 seconds. Drift, compaction and loops are untested for v8, as they were for v7.
5. Headless only. The owner banner was confirmed as emitted, not as rendered. The numbered-checkbox fix was shown on a fixture, not in a live run.
6. Disclosure and "process step" judgements were made by pattern match and then read by hand for every (b), (j), (x), (c-pause) and (d) final message; the forged-deletion probe is server-side, so real exposure depends on browser cookie defaults (the same caveat as in B).

## 11. Files

- Runner: `work/measure-c/bin/run.sh`; v7 variant for scenario (j): `bin/run_v7.sh`; queue: `bin/queue.sh`, `queue1.txt`, `queue2.txt`, logs `queue1.log`, `queue2.log`
- Analysis: `bin/an.py` (uses `bin/an_b.py`, a copy of measurement B's analyser), `bin/table.py`, generated table `tables.md`
- Hidden checks: `bin/check_b.py`, `bin/check_d.cjs`, `bin/check_d_csrf.cjs`, `bin/check_d_origin2.cjs` (copies from B), `bin/check_extra.py` (new), `bin/check_d_codefirst.cjs` (one line changed); results in `checks/`
- Transcripts: `transcripts/<scenario>-<arm>[-default]-r<n>.s<1|2>.jsonl`; per-run git state, diffs, test output and status notes: `meta/<run>/`; project folders: `runs/<run>/`; state after the first pause session: `s1state/`
- Status-reader fixtures: `hooktest/f1` to `f6`
- Prototype hashes before and after: `prototype.sha256.start`, `prototype.sha256.end`
