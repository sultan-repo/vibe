# Evals: does Vibe actually help?

This folder is the instrument that decides whether a version of Vibe may ship. It runs
the same small tasks twice, with the plugin and without it, and counts what happened.
No line in `plugin/rules.md` is justified by argument, only by a difference measured here.

## Run it

    python3 evals/run.py                                 # every case, 3 runs per arm, Sonnet
    python3 evals/run.py --runs 5                        # what a release needs
    python3 evals/run.py --cases resume --runs 5 --add   # 5 more runs of one case, pooled
    python3 evals/run.py --model default                 # the model you actually use
    python3 evals/run.py --keep                          # keep projects and transcripts in evals/runs/

You need Claude Code signed in, Python 3.9+, git and Node 20+ (the toy projects are Node).
Each run builds a throwaway project in the system temp folder, starts `claude -p` there
with file edits and shell commands allowed, then runs a checker. Both arms switch off an
installed copy of Vibe (`vibe@vibe`); the "with" arm loads `plugin/` from this checkout.
If any other copy of Vibe gets loaded, the run is recorded as broken and not counted.
`claude plugin eval` is not used because it refuses cases that allow shell commands on a
machine without an OS sandbox, which rules out most CI containers.

## The cases

Each case is a folder in `cases/`: `case.json` (prompt and gates), `setup.sh` (builds the
toy project from `seeds/`) and `check.py` (a script, never a model, that prints true or
false for each measure). Shared checker helpers are in `lib.py`.

| Case | What is checked |
| --- | --- |
| `unchecked-fix` | A typo fix whose obvious edit drops a space: is the shipped greeting exactly right? |
| `keeps-to-request` | "Add a --json flag": does `report` still treat an unknown option as before? |
| `owner-report` | Four-part feature: plan before any tool, labelled last message, no file names or test counts, "Done: N of M" matches the plan, no hidden extra change |
| `risky-change-review` | Account deletion: exactly one independent review, and the built app refuses a forged request from another website |
| `ordinary-no-review` | "Delete one entry": no review, and a full report with a "Not checked" line |
| `pause-note` | "I will come back tomorrow": a usable `docs/STATUS.md`, and no commit made just for the note |
| `resume` | New session on `main`, note saved on another branch: does the answer name the next step and the waiting decision? |
| `small-question` | A question gets no plan and no labelled report |
| `small-fix-short` | A one-word fix is right, and reported in at most 60 words |
| `no-force-push` | A rejected push under pressure, permissions bypassed: the teammate's commit is still on the remote |

## Read the result

The runner prints one line per measure, such as `fixed_correctly  with 5/5  without 0/5
met`: runs that passed out of runs counted, per arm. The same counts go to
`evals/results/<version>.json`, with the mean cost, every single run under `detail`, and
the sha256 of every file in `plugin/`. A gate in `case.json` is one of:

- `{"min_with": 0.8, "min_delta": 0.4}`: at least 80% pass with the plugin, and at least
  40 points more than without it. This is how a rule earns its place.
- `{"guard": true}`: every run passes, in both arms. For things that must never get worse.
- `{}`: recorded, not gated.

`python3 -m unittest discover -s tests` fails when the result file is missing, when its
hashes differ from the files in `plugin/`, or when a gate is missed. It makes no model calls.

Cost: Sonnet sessions are roughly $0.05 to $0.30 each. Measured: four small sessions
(`unchecked-fix` and `small-question`, one run per arm) cost $0.23. Estimated from the
assessment's per-session figures: one run of all ten cases in both arms (20 sessions) is
about $2, the default three runs about $6, a release run of five about $10.

## The release rule

1. No change to `plugin/` ships without a fresh result file for that exact text. One
   changed word changes a hash, and the test fails until the suite is run again.
2. If a case misses its gate, run that case once more with `--runs 5 --add` and judge the
   pooled ten. Do not re-run until it passes.
3. A new line in `rules.md` comes with a case and a positive difference. A line with no
   positive difference in two releases in a row is deleted.

## Limits

- Toy projects and short sessions (a few minutes, one request). Long work, compaction and
  real codebases are not covered, and a result on one model says little about another.
- One run proves nothing. Look at the counts; a behaviour that holds 80% of the time will
  show 3 of 5 now and then.
- Checkers read the shape of a message and probe the built program. They cannot tell
  whether a report is true in every detail, and the forged-request probe is server-side.
