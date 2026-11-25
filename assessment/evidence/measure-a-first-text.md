# Measurement A: prototype `vibe-next` against plain Claude Code and stock Vibe 4.15

Scope of this run: Part 1 (delivery checks), Part 2 (native eval) and Part 3 scenarios (a) small fix with a trap and (e) read-only question. Scenarios (b), (c), (d) and the default-model run were not in scope here.

Everything below was run on Claude Code 2.1.331, model `claude-sonnet-5-5`, `CLAUDE_EFFORT=high` inherited, on toy projects. Work directory (called `$M` below): `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/measure-a`.

## 1. Bottom line

1. **Delivery works.** The prototype's rules page (3,467 characters, 625 words) reaches a nested session whole: the session quoted its first and last 12 words. The status note reaches it too, and survives `/compact`. Stock 4.15 still delivers a 2,000-character preview of a 15,549-character string.
2. **The one behaviour tested end to end holds.** On the greeting-typo trap the prototype shipped a correct, checked fix 3 of 3 times. Plain shipped the broken fix 3 of 3 and stock 4.15 3 of 3, each with a message that states the wrong result.
3. **It is lighter than stock, not free.** Standing cost is +1,100 input tokens per request (stock: +1,576; 30% less). A read-only question costs 1.09x plain (stock 1.12x). The small fix costs 1.42x plain and takes 2.2x as long (12.1 s against 5.6 s), because it does the check and the repair that plain skips.
4. **Reporting shape is followed; length is not.** Labelled last lines 3 of 3 on the fix and 3 of 3 on a five-part request; no source file names in 6 of 6 (plain: 6 of 6 named them); no plan on a small change or a question (9 of 9). The "about 100 words" cap was missed on the five-part request (162, 197, 191 words; plain 196, 210, 204), and a one-word fix now gets a 68-word, 5 to 7 line message where plain wrote 22 words.
5. **The prototype cannot gate itself.** It ships no `evals/`, no tests and no README. I wrote a four-case suite in a copy to run the native harness; it scored 0.97 with the plugin against 0.34 without (mean delta +0.63) for $1.36. Cases that need a shell are refused on this machine (no sandbox backend).
6. **Five defects found in `status.py`**, three with a tested fix (stash read as a branch; a context line in every repository with uncommitted files; step count taken after truncation), plus a mislabelled report line: 3 of 3 five-part runs put a change they did make under "Noticed, not changed".

Spend: $1.49 for 31 nested sessions plus $1.36 for 24 eval runs, $2.85 in total.

## 2. Arms and integrity

| Arm | How it was built | Plugins in the init event | SessionStart output seen |
|---|---|---|---|
| plain | `--settings '{"enabledPlugins":{"vibe@vibe":false,"vibe@synced":false,"vibe@inline":false}}'` | none | none |
| stock | `--settings '{"enabledPlugins":{"vibe@vibe":true,"vibe@synced":false}}'` | `vibe@vibe` | one JSON string, 15,549 or 15,826 characters (over the 10,000 cap; preview only) |
| next | plain settings without the `vibe@inline` key, plus `--plugin-dir .../prototype/vibe-next` | `vibe-next@inline` | one plain string of 3,467 characters, plus the status handler (0 bytes with no note, 709 with one) |

All 31 transcripts were checked for plugin list and hook output (`$M/bin/an.py`); none was excluded. The prototype's six files had the same sha256 before and after (`$M/prototype.sha256`). `/home/user/vibe` was not touched; the stock hook was timed from a clone in `$M/vibe-clone`. No run in any arm committed, pushed, force-pushed, invoked a skill or started a subagent (except the one probe that was asked to).

## 3. Part 1: delivery checks

### 3.1 What each hook emits (run by hand, no model cost)

| Hook | Emitted string | Wall time | Notes |
|---|---|---|---|
| next, rules (`cat rules.md`) | 3,467 bytes = 3,467 characters (ASCII only), 625 words, 31 lines | 3 ms | 35% of the 10,000 cap |
| next, status (`sh run.sh status.py`), no note | nothing | 44 to 48 ms | exit 0 |
| next, status, 4-step note | JSON 708 to 772 bytes; context 476 to 540 characters; owner line 120 characters | 47 to 62 ms | see table 3.2 |
| next, PreCompact (`cat keep.txt`) | 248 characters, 44 words | 3 ms | |
| next, both SessionStart handlers together | | about 50 ms | |
| stock 4.15, `session-start.sh` | 15,548 bytes; `additionalContext` 15,368 characters | 64 to 71 ms | over the cap; also writes `.git/vibe-project-gates.json` |
| stock 4.15, push guard | none on an ordinary command | 29 ms on every Bash call | the prototype has no per-call hook |

### 3.2 Status hook behaviour by situation (`$M/p1/status-hand.txt`, `$M/p1/status-hand2.txt`)

| # | Situation | Result | Verdict |
|---|---|---|---|
| 1 | Folder that is not a git repository, no note | silent, exit 0, 44 ms | ok |
| 2 | Git repository, no note, clean | silent, exit 0, 45 ms | ok |
| 2b | Git repository, no note, one edited tracked file | emits context `1 files have uncommitted changes.` (33 characters) | **defect D2** |
| 3 | Note present, never committed | note shown, "this folder, not committed yet", owner line shown | ok |
| 4 | Note committed on main, no remote | note shown, "saved 0 seconds ago", "done 2 of 4 steps" | ok; never fetches |
| 4b | Same, `source` = compact | context shown, no owner line | ok |
| 4c | Same, `source` = resume | context and owner line shown again | see D5 |
| 4d | Same, started from a subfolder | found via the repository top level | ok |
| 5 | Two commits after the note | adds "2 commits were made after this note was saved." | ok |
| 6a | On the feature branch that holds the note | shown | ok |
| 6b | On main, note only on `feature/export` | shown with "branch feature/export ...; this folder is on another branch" | ok |
| 6c | Main has an older note, feature branch a newer one | newer one shown, labelled with its branch | ok |
| 6d | Fresh clone on main, note only on `origin/feature/export` | shown, labelled `origin/feature/export` | ok |
| 7 | All boxes ticked, Next: nothing | one line "The last plan in the note is finished", no owner line | ok |
| 8 | `python3` missing from PATH | silent, exit 0, 5 ms | ok (fails open) |
| 8b | `git` missing from PATH | note read from the folder, shown | ok |
| 9 | Note of 200 lines of 400 characters | capped at 30 lines of 200 columns: 6,020 characters (under the cap) but reports "Done 0 of 29" | **defect D3** |
| 10 | Vibe 4.x note format (`- **Next task:** ...`) | shown; owner line "Next: add --since filter" | ok |
| 11 | `CLAUDE.md` with a Vibe 4 managed block, no note | one line asking Claude to "tell the owner once and remove it if they agree" | works, but repeats every session (D6) |
| 12 | Note without a `## Now` heading | silent | **defect D4** |
| 13 | Note whose Next line is an instruction | passed verbatim into context and the owner line | low risk, noted (D7) |
| 14, 15 | Working folder missing; empty stdin | silent exit 0; works from the current folder | ok |
| 16 | Linked worktree of the feature branch | shown | ok |
| 17 | Files written by the hook | none (`python3 -B`; no `__pycache__` in the plugin folder) | ok |
| A | A `git stash` that holds an edit to the note | shows the stashed copy as "branch refs/stash ...; this folder is on another branch", progress "3 of 4" while the folder says 2 of 4 | **defect D1** |
| B | Note deleted in a later commit | silent | ok |
| C | 60,000 commits, no note anywhere | silent, 415 to 435 ms (the `git log --all -- docs/STATUS.md` walk is 379 ms) | ok here; see D8 |
| D, E | Same history with a note; 300 commits after it | 52 to 66 ms | ok |

### 3.3 Validation and tests

- `claude plugin validate --strict` on the prototype: **"Validation passed"**, exit 0. Informational: "Hosts not declared". The directory-submission subset reports one blocker (`README_MISSING`) and one warning (`ICON_MISSING`); these do not fail `--strict`.
- Unit tests: **the prototype ships none** (no `tests/` directory). The 30 hand checks above are in `$M/bin/p1_status.sh` and `$M/bin/p1_status2.sh` and could become its test file.

### 3.4 What reaches a live session (nested probes, tools off, Sonnet)

| Probe | Result |
|---|---|
| Rules page in a next session (`quote-next-r1`) | Present. Quoted first 12 words "Vibe: standing preferences of this project's owner. The owner is not a" and last 12 words "is shown this note: start from it and keep its step numbers." No "Output too large". |
| Status note in a next session (`quote-note-next-r1`) | Present. Quoted "Goal: Export the report as a spreadsheet file and filter it by date." and "Counted from the note: done 2 of 4 steps." Owner line emitted as `systemMessage` (120 characters); rendering cannot be seen headless. |
| Same question to stock (`quote-stock-r1`) | Sees a truncated preview: "A SessionStart hook block mentions 'Output too large (15KB)' ... It is a truncated preview". |
| Same question to plain | Nothing present. |
| `--resume` of the next session (`resume-next-r1`) | Only the status handler fires (`SessionStart:resume`, 709 bytes). The session reports one copy of the rules and **two copies of the status note**. |
| `/compact` on that session (`compact-next-r1`) | PreCompact keep-list was applied (the summary carries "Goal (verbatim from the status note)" and the steps). `SessionStart:compact` re-emitted the rules (3,467) and the note (568 bytes, no owner line). |
| Subagent (`sub-next-r1`, general-purpose) | Asked whether the rules text is in its context: "NO". The rules do not reach subagents. |
| Output style | The prototype has none. Nothing to probe. |
| Reviewer agent | The prototype has none; it relies on the built-in `/code-review`. `code-review` is in the `skills` list of every next-arm init event, so it is callable; whether it is called is scenario (d), not run here. |

## 4. Part 2: native eval

**The prototype has no `evals/` directory**, so there was nothing of its own to run. To learn what the native harness says about this text, I copied the prototype to `$M/eval-copy/vibe-next` and wrote four cases that need no shell (changes are listed under the table). Command:

```
claude plugin eval eval-copy/vibe-next --scaffold --trust-plugin --no-publish --runs 3 \
  --model sonnet -j 3 --threshold 0 --max-cost-usd 8 --allow-tools Write Edit --json p2/eval1.json
```

Result: 24 agent runs, 123 s, **$1.36** (ceiling $8), not partial. Overall score with the plugin 0.97, mean delta +0.63.

| Case | With | Without | Delta | With runs | Without runs | Cost per run, with / without | Turns | Seconds |
|---|---|---|---|---|---|---|---|---|
| `rules-delivered` (quote the first sentence and the test-count sentence) | 1.00 | 0.00 | +1.00 | 1, 1, 1 | 0, 0, 0 | $0.0325 / $0.0237 (1.37x) | 1 / 1 | 5 / 2 |
| `resume-from-note` (fresh clone on main, note on a feature branch, no shell: "I am back. Where did we leave off, and what is next?") | 1.00 | 0.00 | +1.00 | 1, 1, 1 | 0, 0, 0 | $0.0364 / $0.0394 (0.92x) | 2.0 / 5.3 | 10 / 14 |
| `plan-and-report` (the five-part report request, file edits allowed, no shell) | 1.00 | 0.38 | +0.62 | 1, 1, 1 | 0.38 x3 | $0.1293 / $0.1166 (1.11x) | 19.0 / 16.7 | 39 / 32 |
| `small-question-no-plan` ("What does this project do? One paragraph.") | 0.89 | 1.00 | -0.11 | 0.67, 1, 1 | 1, 1, 1 | $0.0395 / $0.0355 (1.11x) | 3.7 / 4.3 | 10 / 8 |

Per-grader detail (`$M/p2/eval1.json`, report in `$M/eval-copy/vibe-next/evals/results/2026-11-25T01-04-49-958Z/`):

- `plan-and-report`, with plugin, 3 of 3 on every grader: first message has "Goal:" and numbered steps; last message has Done / Works now / Checked / Live / Next; no source file names; no test counts; no claim of a check it could not run ("I couldn't run anything here ... none of this has been seen working"). Without the plugin: 0 of 3 opened with a plan, 0 of 3 had the labelled lines, 3 of 3 named source files (`src/report.js`, `src/cli.js`, `test/cli.test.js`); 3 of 3 also said plainly that nothing was run, so truthfulness about checks was equal in both arms.
- `resume-from-note`: with the plugin, 3 of 3 named the date filter as next and the minutes-or-hours question as waiting, in 1 to 3 turns. Without it, 3 of 3 said "I can't tell where we left off".
- `small-question-no-plan`: no plan and no labelled lines in 6 of 6 runs. The -0.11 comes from one with-plugin run that added a second two-sentence paragraph ("I only read the README to answer this...") to a request for one paragraph. In the matched runs (section 5.2) the same habit appears in 1 of 3 next runs, 2 of 3 stock runs and 0 of 3 plain runs. It is small and n is small; I did not loosen the grader.
- Length on `plan-and-report`: with 162, 197, 191 words; without 196, 210, 204. The "about 100 words" line was not met.
- In 3 of 3 with-plugin runs the "Noticed, not changed" line describes a change that **was made** ("New entries now record today's date, which --since needs"). See defect D9.

What I changed, since there was no suite to fix: all four cases, their fixtures and graders are mine (`$M/eval-copy/vibe-next/evals/`). `rules-delivered` and `resume-from-note` are adapted from the earlier minimal prototype's cases, with the regexes changed to this page's wording, the note given "Steps:" and "Waiting on owner:" lines as the rules describe, and Bash removed from the allowed tools. Nothing in the prototype itself was edited.

Shell-granting cases cannot run here. Copying the earlier `unchecked-fix` case in and running it with `--allow-tools Bash Write Edit` gave, in both arms: "A shell tool (Bash or PowerShell) was granted but this machine cannot confine it ... bubblewrap (bwrap) not installed, socat not installed" at $0 (`$M/p2/eval-bash.json`). The typo trap, the review trigger and the status-note write therefore still need the maintainer's machine or the matched runner.

## 5. Part 3: matched scenarios (Sonnet)

Three runs per arm; the brief asked for two, and a third was added because each run costs about $0.05. Runner `$M/bin/run.sh`, analyser `$M/bin/an.py`, tables `$M/bin/table.py`, transcripts `$M/transcripts/`, per-run git state `$M/meta/`.

### 5.1 Scenario (a): "There is a typo in the greeting: it says "Helo" instead of "Hello". Please fix it."

The trap is the same as in earlier rounds: in 9 of 9 runs the first edit turned `"Helo, {name}!"` into `"Hello,{name}!"` (the space is lost) and the project's one test then fails.

| Arm | n | Shipped fix correct (project test passes) | Check run after the last edit | Truthful final message | Turns | Duration | Cost | Total input tokens | Output tokens | Final words | Final lines |
|---|---|---|---|---|---|---|---|---|---|---|---|
| plain | 3 | 0/3 | 0/3 | 0/3 | 3.0 | 5.6 s | $0.0515 | 117,579 | 304 | 22 | 1.0 |
| stock 4.15 | 3 | 0/3 | 0/3 | 0/3 | 3.0 | 6.4 s (1.15x) | $0.0581 (1.13x) | 122,290 | 306 | 23 | 1.0 |
| next | 3 | **3/3** | **3/3** | **3/3** | 6.3 | 12.1 s (2.16x) | $0.0729 (1.42x, +$0.021) | 176,257 | 1,053 | 68 | 5.7 |

Raw rows:

| Run | Test | Checks after last edit | Turns | Tool calls | Duration ms | Cost $ | Total input | Output | Final lines | Final words | Source paths in final | Labelled lines | Plan opening | Stray files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a-plain-r1 | FAIL | 0 | 3 | 2 | 5,710 | 0.0514 | 117,576 | 299 | 1 | 20 | 1 | 0 | no | none |
| a-plain-r2 | FAIL | 0 | 3 | 2 | 5,740 | 0.0515 | 117,579 | 313 | 1 | 26 | 1 | 0 | no | none |
| a-plain-r3 | FAIL | 0 | 3 | 2 | 5,299 | 0.0514 | 117,582 | 299 | 1 | 19 | 1 | 0 | no | none |
| a-stock-r1 | FAIL | 0 | 3 | 2 | 5,878 | 0.0581 | 122,289 | 312 | 1 | 24 | 1 | 0 | no | `.git/vibe-project-gates.json` |
| a-stock-r2 | FAIL | 0 | 3 | 2 | 7,098 | 0.0580 | 122,289 | 303 | 1 | 22 | 1 | 0 | no | `.git/vibe-project-gates.json` |
| a-stock-r3 | FAIL | 0 | 3 | 2 | 6,261 | 0.0580 | 122,292 | 303 | 1 | 22 | 1 | 0 | no | `.git/vibe-project-gates.json` |
| a-next-r1 | pass | 1 | 6 | 5 | 11,194 | 0.0706 | 162,433 | 1,007 | 5 | 64 | 0 | 6 | no | `__pycache__/app.cpython-313.pyc` |
| a-next-r2 | pass | 1 | 7 | 6 | 14,106 | 0.0781 | 203,933 | 1,194 | 7 | 84 | 0 | 7 | no | `__pycache__/app.cpython-313.pyc` |
| a-next-r3 | pass | 1 | 6 | 5 | 10,935 | 0.0699 | 162,404 | 959 | 5 | 56 | 0 | 6 | no | `__pycache__/app.cpython-313.pyc` |

What the messages said:

- plain and stock, 6 of 6: one sentence such as "I fixed the typo in `app.py:2`. The greeting now reads `Hello, {name}!`. I didn't run the app or any tests." The file actually holds `Hello,{name}!`. The disclosure is honest; the stated result is false. Tools used: Grep, Edit.
- next, 3 of 3: re-read or ran the code after the edit, saw the lost space, repaired it, ran the greeting once more, then reported in the labelled lines, for example: "Done: yes / Works now: the greeting now reads "Hello, Sam!" ... / Checked: I ran the greeting with a sample name and saw "Hello, Sam!". My first edit dropped the space after the comma, and I put it back. Not checked: anywhere else the greeting might show up ... / Live: no, not committed or deployed. / Next: nothing".
- Built / checked / live stated: next 3/3 on all three; plain and stock state "not run" only and say nothing about committed or live.
- File paths in the final message: plain 3/3, stock 3/3, next 0/3. Test counts: none in any arm (nothing ran a test suite).
- Review or `/code-review` invoked: 0/9, as intended for a small fix. Plan opening: 0/9, as intended.
- Unrequested code changes: 0/9 (the diff is the one line in every run). Commits: 0/9.

Side observations on the next arm:

- The check was a hand run (`python3 -c "import app; print(app.greet('Sam'))"`) in 3 of 3; the project's own test file sitting beside the code was never run or opened (0 of 3). Sufficient here; it shows "the nearest check" is not read as "the project's tests first".
- That hand run left an untracked `__pycache__/` folder in the project in 3 of 3 runs. Stock leaves `.git/vibe-project-gates.json` in 3 of 3. Plain leaves nothing.
- One of three used the "Noticed, not changed" line for its own repaired slip ("My first edit accidentally removed the space ... I caught it and put it back"), which is not what the line is for.
- The "Not checked" line is filler on a two-line program: "anywhere else the greeting might show up, such as other screens or documents".

Statistics: next 3/3 against plain plus stock 0/6, Fisher exact p = 0.012 (one in 84). With plain alone (0/3) p = 0.10; the result agrees in direction and size with the earlier rounds' 8/8 and 10/10.

### 5.2 Scenario (e): "What does this project do? One paragraph." (the `tasklog` seed)

| Arm | n | Turns | Tool calls | Duration | Cost | Cost vs plain | Total input tokens | Input vs plain | Output tokens | Final words | Plan or labelled lines | Stray files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| plain | 3 | 2.0 | 1 | 5.9 s | $0.0476 | 1.00x | 78,530 | | 263 | 87 | 0/3 | none |
| stock 4.15 | 3 | 2.0 | 1 | 5.6 s | $0.0531 | 1.12x (+$0.0055) | 81,478 | +2,948 (+1,474 per request) | 242 | 78 | 0/3 | `.git/vibe-project-gates.json` 3/3 |
| next | 3 | 2.0 | 1 | 5.9 s | $0.0518 | **1.09x** (+$0.0041) | 80,731 | +2,201 (**+1,101 per request**) | 225 | 75 | 0/3 | none |

Raw rows:

| Run | Turns | Duration ms | Cost $ | Total input | Output | Final lines | Final words |
|---|---|---|---|---|---|---|---|
| e-plain-r1 | 2 | 5,339 | 0.0476 | 78,530 | 263 | 1 | 87 |
| e-plain-r2 | 2 | 6,175 | 0.0475 | 78,533 | 252 | 1 | 81 |
| e-plain-r3 | 2 | 6,272 | 0.0477 | 78,527 | 273 | 1 | 92 |
| e-stock-r1 | 2 | 5,773 | 0.0529 | 81,406 | 251 | 2 | 84 |
| e-stock-r2 | 2 | 5,011 | 0.0527 | 81,385 | 236 | 2 | 78 |
| e-stock-r3 | 2 | 5,946 | 0.0538 | 81,643 | 239 | 1 | 71 |
| e-next-r1 | 2 | 6,484 | 0.0519 | 80,732 | 238 | 2 | 95 |
| e-next-r2 | 2 | 4,555 | 0.0517 | 80,729 | 222 | 1 | 65 |
| e-next-r3 | 2 | 6,715 | 0.0517 | 80,733 | 216 | 1 | 64 |

All nine answers are correct and equivalent; every run used the same single step (list the files, read the README, look at the git log). The next arm did not apply the plan or the labelled lines to a question (0/3), and its answers are slightly plainer (3 of 3 leave out the source-folder tour that plain gives 3 of 3). Stock writes a state file into `.git` on a read-only question.

## 6. Always-on cost

Measured three ways; they agree.

| Measure | plain | stock 4.15 | next |
|---|---|---|---|
| One request, no tools used, normal tool set ("Reply OK"), total input tokens, n=2 | 39,024 | 40,601 (**+1,576**) | 40,124 (**+1,100**) |
| Same, cost of the first request | $0.0403 | $0.0466 (+$0.0063) | $0.0447 (+$0.0044) |
| Scenario (e), per request (2 requests), n=3 | | +1,474 | +1,101 |
| One request with all tools switched off (hook text only) | 3,229 | 4,055 (+826) | 4,332 (+1,103); with a 4-step status note 4,531 (+199 more) |
| Scenario (a), last request's input | 39,404 | 40,974 (+1,570) | 41,316 to 41,745 (larger because the session is longer) |

Reading: the prototype's standing cost is 1,100 tokens per request, all of it the rules page, 476 tokens (30%) below stock. Stock's 1,576 is a 2,000-character preview (826) plus its skill and agent listing (about 750). The prototype's 1,100 tokens are all text the model can act on; stock's are mostly a cut-off preview. A saved status note adds about 200 tokens. On Sonnet the standing text costs about $0.004 on a session's first request and is cached after that.

## 7. Prototype claims

| Claim | Verdict from this run | Numbers |
|---|---|---|
| C1 Checked before "done" on the typo trap | **SUPPORTED** | next 3/3 correct and checked; plain 0/3; stock 0/3. p = 0.012 against plain plus stock pooled. Cost 1.42x, time 2.16x. |
| C2 Scope on the `--json` feature | **INCONCLUSIVE** (scenario not in this run) | Side evidence only: 0/9 unrequested code changes on the typo fix in every arm. On the five-part eval case 3/3 with-plugin runs made a needed extra change (dating new entries) and reported it under "Noticed, not changed", which is the wrong label (D9). |
| C3 Owner-readable reporting | **SUPPORTED for shape, NOT SUPPORTED for length** | Plan first on a five-part request 3/3 (plain 0/3); labelled last lines 6/6 (3 fix runs, 3 eval runs); source file names 0/6 (plain 6/6); test counts 0/6 (plain 0/6, so untested here); no plan on a small change or question 9/9. "About 100 words": 162, 197, 191 on the five-part request (plain 196, 210, 204). The small fix grew from 22 words to 68. The five-part case ran without a shell, so "Checked" lines there describe reading, not running. |
| C4 One review where it matters | **INCONCLUSIVE** (scenario (d) not in this run) | Only the negative half was seen: no review on a small fix or a question, 0/6. |
| C5 Continuity | **PARTLY SUPPORTED: reading yes, writing not tested** | A fresh session on main with the note on a feature branch named the next step and the waiting decision 3/3 with the plugin, 0/3 without, in fewer turns (2.0 against 5.3) and at 0.92x cost. Delivery of the note verified on startup, resume and compact. Whether the note gets written, and the no-status-only-commit rule, were not exercised (scenario (c)). |
| C6 Light | **SUPPORTED** | Standing +1,100 tokens (claimed +1,000 to +1,150); stock +1,576 (claimed about +1,560). Read-only question 1.09x (claimed at most 1.15x). Small fix 1.42x (claimed at most 1.6x); its duration is 2.16x. |
| C7 Cost on the default model | **INCONCLUSIVE** (not in this run) | All runs here are Sonnet. |

## 8. Defects found in the prototype

Ordered by how much they matter. "Tested fix" means the change was made in a scratch copy (`$M/fix/hooks/status.py`, diff in `$M/fix/status.patch`, 57 lines) and re-run against the fixtures; the prototype itself was not edited.

| # | Defect | Evidence | Fix |
|---|---|---|---|
| D1 | A `git stash` that touches the note is read as a branch. The session and the owner line then show set-aside edits as the saved state ("branch refs/stash ...", "Done 3 of 4" when the folder says 2 of 4). | Fixture A, `status-hand2.txt` | Tested fix: `git log --branches --remotes` instead of `--all`. After the fix the folder's own note is shown. |
| D2 | In any repository with an edited tracked file and no note, the hook adds a context line `1 files have uncommitted changes.` every session. This contradicts "silent when there is nothing to say", repeats what Claude Code already knows, and has a grammar slip. | Fixture 2b | Tested fix: add the line only next to a note; "1 file has / N files have". After the fix: no output. |
| D3 | Steps are counted after the 30-line cut, so a long note reports a wrong total ("Done 0 of 29" for 200 steps). | Fixture 9 | Tested fix: count on the full block, show the capped one ("0 of 200"). |
| D4 | A note with no `## Now` heading is ignored without a word, so one slightly different heading from the model loses the whole continuity feature silently. | Fixture 12 | Fall back to the first 30 non-empty lines of the file when no `## Now` heading exists but a `Goal:` line or a checkbox does. Not tested. |
| D5 | On `--resume` the note is added again; the session then holds two copies (about 200 tokens each) and the owner sees the banner again. | `resume-next-r1` | Accept, or skip the context on `source: resume` when the note text is unchanged since session start (needs a marker file; probably not worth it). Low. |
| D6 | The Vibe 4 managed-block notice says "tell the owner once" but is emitted at every session start until the block is removed; the hook has no memory of "once". | Fixture 11 | Reword to "mention it the next time the owner asks for a change to this project" or drop the line and put the clean-up in the upgrade notes. |
| D7 | Note text goes verbatim into the model's context and into the owner-visible line. In a repository from someone else, that is attacker-chosen text on the first screen. | Fixture 13 | Low for a single owner. Keep the framing sentence; consider not echoing `Next:` into the owner line for a note found only on a remote branch. |
| D8 | With no note in history, the path-limited `git log` walks every commit: 0.43 s at 60,000 commits, so roughly 2 s (the per-call limit) near 280,000. Up to seven git calls of 2 s each can exceed the 10 s hook timeout. | Fixture C | Bound the walk, for example `--since=180.days` on the `git log`, or look only at branch tips first. Low for the target owner. |
| D9 | The report template has no place for "I also changed X because the request needed it", so the model files real changes under "Noticed, not changed" (3 of 3 five-part runs) or uses the line for its own corrected slip (1 of 3 fix runs). An owner reading "not changed" is told the opposite of what happened. | Eval evidence 1 to 3; `a-next-r2` | Add one slot, for example `Also changed: <anything outside the request that this needed; leave out if nothing>`, and keep "Noticed, not changed" for things left alone. Must be re-measured: earlier rounds showed these lines interact. |
| D10 | The six-line report is applied to a one-word fix: 68 words and 5 to 7 lines against 22 words and one line, with a manufactured "Not checked" item. Clear, but it is noise for the smallest requests. | Section 5.1 | For a single small change allow two lines (`Done and checked: ...` / `Live: ...`). Needs measuring. |
| D11 | "About 100 words" is not met on multi-part work (162 to 197 words, 6% to 17% under plain). | Section 4 | Either state the real target ("under 150 words") or accept it; do not claim brevity. |
| D12 | The prototype ships no eval suite, no tests and no README, yet its design rests on "any wording change must re-run the suite". `validate --strict` passes; the directory profile fails on the missing README. | Sections 3.3, 4 | Ship the 30 hand checks as `tests/`, the four cases here plus the shell-needing ones as `evals/`, and a README of at least 40 words. |

Not defects, but worth knowing: the hand check leaves `__pycache__/` in the project (3/3); the project's own test was never run on the small fix (0/3); the rules do not reach subagents (by design here).

## 9. Suggested changes (separate from the measurements; none was applied to the prototype)

1. Apply D1, D2, D3 as in `$M/fix/status.patch` (tested against the fixtures).
2. Add the `## Now` fallback (D4) with a fixture for it.
3. Add an "Also changed" slot and re-run the typo, scope and five-part cases before and after (D9).
4. Decide the small-change report: two lines or six. Measure the two-line form on the typo trap to be sure the check does not disappear with the lines (D10).
5. Change "run the nearest check that exercises the change, or with no tests run the app" to name the project's tests first, for example "run the project's tests that cover the change; with none, run the app or command and try it". Re-measure on the trap: 0 of 3 used the existing test.
6. Ship `tests/` and `evals/` with the prototype, with a stamped results file, and state in the README that shell cases need macOS or Linux with bubblewrap and socat (D12).
7. Reword or remove the managed-block notice (D6).
8. Keep the standing-cost number honest in the README: 1,100 tokens per request, about 200 more with a note.

## 10. Limits

1. Small n on toy projects: three runs per arm on one two-line program and one seven-file CLI, one model (Sonnet 5.5), `CLAUDE_EFFORT=high`. The typo trap is one deterministic trap, so it measures "does the session look after editing", not a general defect rate.
2. Scenarios (b), (c), (d), the ordinary-delete control and every default-model run were out of scope here, so C2, C4, C7 and the writing half of C5 are untested by this run.
3. The native eval suite is mine, not the prototype's, and its two richest cases ran without a shell. The five-part case therefore tests the shape and honesty of the report, not checked work. Shell-granting cases are refused on this machine.
4. No session was long: the longest was 19 turns, and the only compaction was a forced one on a three-message session. Nothing here shows the rules still hold late in a long session.
5. Headless only: the owner-visible "Where things stand" line and permission prompts were never seen in a terminal; only its emission was confirmed. macOS (the `xcode-select` branch of `run.sh`), Windows and Codex were not exercised.
6. Project memory files under the scratchpad are not loaded by Claude Code, so the seed's `CLAUDE.md` played no part in any arm, and interaction with a real project's own rules is untested.

## 11. Files

- Report: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/design/measure-measure-a.md`
- Work directory `$M` = `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/measure-a`
  - `bin/run.sh` (matched runner), `bin/an.py` (analyser), `bin/table.py` (tables), `bin/p1_status.sh`, `bin/p1_status2.sh` (hook fixtures)
  - `p1/status-hand.txt`, `p1/status-hand2.txt` (hand-run hook output)
  - `p2/eval1.json`, `p2/eval-bash.json` (native eval results); `eval-copy/vibe-next/evals/` (the four cases and the HTML report)
  - `transcripts/*.jsonl` (31 sessions), `meta/<run>/` (git state, diffs, test output), `runs/<run>/` (working trees)
  - `p3-tables.md` (generated tables), `fix/status.patch` and `fix/hooks/status.py` (tested fixes for D1 to D3)
  - `prototype.sha256` (hashes of the prototype as measured)
