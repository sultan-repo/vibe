# Channel experiment: which channel makes owner-facing reporting rules change Claude Code's behaviour?

Key: `exp-channel`. Runs made 2026-11-24/25 on Claude Code 2.1.331. All numbers below were measured in this session from saved transcripts unless marked HYPOTHESIS. Work directory: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel`.

## 1. Bottom line

1. **Wording decides, not channel.** The kernel-v0 progress rules (prose, with the trigger "for work of more than a few steps") changed nothing that matters on Sonnet 5.5 through any channel: 0 of 8 scenario-B runs opened with a goal and step list, 15 of 16 runs still reported test counts, and the final message kept its shape. The same rules rewritten as a literal fill-in template with an observable trigger were followed in 12 of 12 scenario-B runs delivered by hook or output style, and all 22 Sonnet runs with the rewritten text ended with the labelled lines (Works now / Checked / Not checked / Live / Next).
2. **SessionStart hook and plugin output style performed the same.** With identical text: v0 hook 0/2 and v0 style 0/2 openings; v2 hook 3/3 and v2 style 3/3. Delivering the progress section through both at once added about 216 tokens per request and no compliance. The output style brings costs the hook does not: it overrides the user's own style, does not exist on Codex or in subagents, and puts the session on a different prompt-cache prefix that was cold on first use here ($0.12 extra on Sonnet, about $0.49 on Fable, one time per model and flag set).
3. **Model matters as much as wording for loose prose.** Fable 5.2 followed the v0 prose through hook and through style alike (goal + 6 steps, no test count, "built and checked"), but its final message got longer (224 and 190 words against 180 plain) and the hook run cost 27% more. With the final template (v5) Fable produced 102 words at +2% cost.
4. **"Done N of M" as live progress never happened.** 0 of 48 runs emitted a Done line before the final message. The model finishes the job in 3 to 14 tool calls, most often one large shell script that edits every file and runs the tests, and then lists the Done lines retrospectively. A variant that said "work through the outcomes one at a time" changed nothing (0/2).
5. **The CLAUDE.md control arm is not a valid test of project memory.** Claude Code refused to load any CLAUDE.md under the session scratchpad (debug log quoted in section 3). What that arm measured instead: the model found the file with `cat` in its first or second shell call in 8 of 8 runs, then followed the final-message template (4/4 with v2) but could not produce the opening it had not yet read (0/4).
6. **The template has one measured downside.** Unrequested changes were mentioned in the final message in 11 of 24 template runs against 19 of 22 plain and v0 runs; the fixed lines leave no place for them. It also still leaks test counts (12 of 22 Sonnet runs) and misses its word cap (3 of 18).
7. Cost of the working variant on Sonnet: about 0.9K input tokens per request, no measurable change in dollars, time or turns (scenario B: $0.105 against $0.102 plain, n=16 against 2). All 48 runs passed their tests and a separate functional check.

N is small (2 to 4 runs per cell, one toy project, runs of 12 to 90 seconds). The wording effect is large and consistent (0/8 against 12/12 on the opening); everything finer than that is indicative only.

## 2. Method

### Arms

| arm | rules text | how it reaches the model |
|---|---|---|
| plain | none | nothing |
| claudemd | kernel-v0 whole | `CLAUDE.md` committed in the toy project. Not auto-loaded in this environment, see section 3 |
| hook | kernel-v0 whole (2,476 chars) | plugin `vx-hook`: one SessionStart command, `cat "${CLAUDE_PLUGIN_ROOT}/context.md"` |
| style | kernel-v0 split | plugin `vx-style`: header, "Doing the work" and "Continuity" by the same hook (1,864 chars); "Progress the owner can follow" as `output-styles/vibe.md` with `name`, `description`, `keep-coding-instructions: true`, `force-for-plugin: true` |
| both | kernel-v0 whole + progress again | plugin `vx-both`: whole kernel by hook and the progress section also as the output style |
| hook2, style2, claudemd2 | kernel with progress section v2 | same three channels (added after the first 23 runs) |
| hook3, hook4, hook5 | progress section v3, v4, v5 | hook only |

Every arm ran with `--settings '{"enabledPlugins":{"vibe@vibe":false,"vibe@synced":false,"vibe@inline":false}}'`; prototype arms added `--plugin-dir`. Init events list only the prototype plugin and four built-in `cc-plugin-*` entries in every run, so no installed Vibe copy was active.

Only the progress section differs between text versions; the header, "Doing the work" and "Continuity" are byte-identical to `design/kernel-v0.md`.

Progress section v0 (611 chars), as given:

```
## Progress the owner can follow
- For work of more than a few steps, open with the goal in one sentence and a numbered list of 3 to 7 outcome steps in the owner's words. When a step finishes, say "Done N of M: <outcome>". If the plan changes, say so in one line.
- Final message: what works now; whether it is built, checked or live; what is next; any decision needed. A few short lines. Describe outcomes ("Only invited relatives can now see private details"); keep file paths, commands and test counts for when asked.
- Say plainly what was not checked. Only call something done after you have seen it work.
```

Progress section v2 (952 chars), the first rewrite:

```
## Keeping the owner informed
The owner cannot read code and follows the work only through your messages. File names, function names, exit codes and test counts mean nothing to them; leave them out unless asked. Commands the owner would type themselves are fine.

When a request asks for more than one thing, write this before your first tool call:
Goal: <one sentence: what the owner will be able to do>
1. <outcome, in the owner's words>
2. <one line per thing asked for>

Each time one of those outcomes works and you have checked it, write one line before moving on: "Done 2 of 4: <outcome>".

End every piece of work with these four lines and nothing after them, under 100 words in all:
Works now: <what the owner can now do>
Checked: <how you saw it work>. Not checked: <what you did not try, or "nothing">
Live: <"no, not committed or deployed", or where it is live>
Next: <the next step, or the one decision you need, with your recommendation>
```

v3 = v2 with the Done sentence changed to "Work through the outcomes one at a time. When one works and you have checked it, write one line before starting the next". v4 = trigger raised to "three or more things", the word cap removed, a single "Done 4 of 4." tally line, "Next" narrowed to one decision or "nothing". v5 is in section 8.

### Command

```
claude -p "<prompt>" --model sonnet|fable --max-turns 40 --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Write,Glob,Grep,Bash,Skill,Agent,Task,TodoWrite,TaskCreate,TaskUpdate,TaskList,TaskGet" \
  --output-format stream-json --verbose --include-hook-events --settings '<disable vibe>' [--plugin-dir <prototype>]
```

Same flags as round one's `live-ab-experiment/bin/run.sh`. Each run started from a fresh copy of seed `s2` (the `tasklog` Node CLI, 7 passing tests), `git init -b main`, one initial commit. Arms of a batch ran concurrently. `--model sonnet` resolved to `claude-sonnet-5-5`, `--model fable` to `claude-fable-5-2` (init events). No permission denials, no Skill, Agent or task-tool calls, and no commits in any run.

### Scenarios

- A: "Add a --json output flag to the report command, with tests."
- B: "Add CSV export, a --since date filter and a total line to the report command, and update the README."

### Runs

48 scenario runs: the planned 20 (5 arms x 2 scenarios x 2, Sonnet), the planned 3 on Fable (plain, hook, style; scenario B), and 25 variant runs. Plus 14 short probes (12 logged). 60 logged nested invocations cost $10.60 in total.

### Measures

Computed by `bin/analyze.py` and `bin/table.py` from the stream-json transcript and the post-run tree, then read by hand for every final message. "Code spans" counts backticked spans (commands the owner types included). "Internal paths/ids" counts source file paths and camelCase identifiers. "Test count" is any numeral attached to tests ("all 10 tests", "3 new ones"). "Works" is a separate functional check (`bin/accept.sh`): the real CLI is run against a temp log for `--json`, or for `--csv`, `--since` past, future and malformed.

## 3. Delivery checks

| check | result | evidence |
|---|---|---|
| Hook text arrives whole | yes: `hook_response` output 2,476 chars (v0), 1,864 (style arm), 2,817 (v2), 2,843 (v3, v5), 2,882 (v4); exit 0; no "Output too large" | `transcripts/P-*.jsonl`, every run's hook event |
| Output style active | yes: the model quotes a block headed "# Output Style: vx-style:vibe" and says the system prompt opens by referring to an Output Style | `transcripts/probe2-style.jsonl`, `probe2-both.jsonl`, `probe4-*.json` |
| Init event shows the style | no: `output_style` reads `"default"` in every style-arm init event. The field cannot be used to verify a forced plugin style | `transcripts/P-style-sonnet-r0.jsonl` |
| Software-engineering section present | not on Sonnet 5.5 by default, in any arm (model self-report in hook and style arms). With `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=0` and the style, the section is present ("Default to writing no comments.") and the first request is 48.8K tokens instead of 39.9K | `probe2-*.jsonl`, `probe4-style-ssp0.json` |
| CLAUDE.md loaded as memory | **no** | debug log: `[CLAUDE.md] not loading .../runs/P-claudemd-sonnet-r0/CLAUDE.md: it, or what it links to, is in a session's scratchpad, a folder laid out like one (claude/<project>/<session id>/scratchpad), or a folder named .artifact-work.` (`probe/debug-claudemd.log:102`). First-request input is 39,038 tokens against 39,031 plain. The model, asked directly, answered "NO. I don't see any project CLAUDE.md content in my context." |
| Always-on token cost (first request, input incl. cache) | plain 39,031; hook v0 +781; style v0 +801; both v0 +997; hook v2 +891; hook v5 +912 | first assistant usage, runs `A-*-r1`, `B-*-r1` |

Prompt-cache note. A styled session uses a different cached system-prompt prefix from a default session. The first styled run for each model and flag set wrote the whole prefix and read nothing: `P-style` and `P-both` (Sonnet: 39.8K and 40.0K written, 0 read, $0.159 and $0.160 against $0.041 plain), `probe2-style`, `probe2-both`, `B-style-fable-r1` (41,264 written, 0 read) and `probe4-style-ssp0`. Later styled runs read about 29.4K from cache, including the first run of a style with different text (`B-style2-sonnet-r1`), so the styled prefix is shared across style contents. Prices fitted from this session's usage and cost fields (exact fit over 44 Sonnet runs): Sonnet $4.00 per million cache-write tokens, $0.10 cache-read, $10 output; Fable about $16, $0.20, $40. HYPOTHESIS: a real user of a forced style pays this cold write more often than a default-style user, because the default prefix is kept warm by every other session; this experiment cannot tell how warm either prefix is for a typical owner.

## 4. Per-arm means

One row per arm, model and scenario. Fractions are runs.

| arm | rules text | channel | model | scenario | n | final words | final lines | code spans | internal paths/ids (runs) | test count (runs) | Checked/Live labels (runs) | says what was not checked (runs) | goal + numbered steps before first tool (runs) | Done tally in final (runs) | Done lines mid-run (runs) | tests pass and feature works | turns | seconds | cost $ | input tokens (k) | output tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| plain | none | none | sonnet | B | 2 | 188 | 6.5 | 18.5 | 2/2 | 2/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 4.0 | 23 | 0.102 | 164 | 2918 |
| claudemd | v0 | CLAUDE.md in repo (not auto-loaded here; model cat'ed it) | sonnet | B | 2 | 154 | 5.5 | 10.5 | 0/2 | 1/2 | 0/2 | 1/2 | 0/2 | 0/2 | 0/2 | 2/2 | 4.0 | 19 | 0.096 | 166 | 2207 |
| hook | v0 | SessionStart hook | sonnet | B | 2 | 153 | 6.5 | 10.0 | 0/2 | 2/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 4.5 | 22 | 0.105 | 190 | 2671 |
| style | v0 | hook + progress rules as output style | sonnet | B | 2 | 166 | 6.0 | 12.0 | 0/2 | 2/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 6.0 | 27 | 0.122 | 260 | 3232 |
| both | v0 | hook (all) + output style (progress) | sonnet | B | 2 | 182 | 6.5 | 10.0 | 0/2 | 2/2 | 1/2 | 1/2 | 0/2 | 0/2 | 0/2 | 2/2 | 4.5 | 29 | 0.126 | 193 | 4088 |
| hook2 | v2 | SessionStart hook | sonnet | B | 3 | 140 | 6.3 | 5.0 | 0/3 | 2/3 | 3/3 | 3/3 | 3/3 | 2/3 | 0/3 | 3/3 | 4.7 | 20 | 0.103 | 198 | 2539 |
| style2 | v2 | hook + progress rules as output style | sonnet | B | 3 | 131 | 6.7 | 3.7 | 0/3 | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 4.3 | 24 | 0.108 | 184 | 2978 |
| claudemd2 | v2 | CLAUDE.md in repo (not auto-loaded; cat'ed) | sonnet | B | 4 | 123 | 7.8 | 3.5 | 0/4 | 0/4 | 4/4 | 4/4 | 0/4 | 4/4 | 0/4 | 4/4 | 4.0 | 22 | 0.100 | 167 | 2513 |
| hook3 | v3 | SessionStart hook | sonnet | B | 2 | 135 | 5.0 | 4.0 | 0/2 | 1/2 | 2/2 | 2/2 | 2/2 | 1/2 | 0/2 | 2/2 | 4.0 | 19 | 0.100 | 168 | 2492 |
| hook4 | v4 | SessionStart hook | sonnet | B | 2 | 159 | 5.5 | 5.0 | 0/2 | 1/2 | 2/2 | 2/2 | 2/2 | 2/2 | 0/2 | 2/2 | 5.5 | 23 | 0.113 | 236 | 2850 |
| hook5 | v5 | SessionStart hook | sonnet | B | 2 | 143 | 9.5 | 4.0 | 0/2 | 1/2 | 2/2 | 2/2 | 2/2 | 2/2 | 0/2 | 2/2 | 5.0 | 24 | 0.110 | 193 | 2846 |
| plain | none | none | sonnet | A | 2 | 112 | 4.5 | 9.0 | 2/2 | 2/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 12.0 | 21 | 0.102 | 208 | 2437 |
| claudemd | v0 | CLAUDE.md in repo (not auto-loaded here; model cat'ed it) | sonnet | A | 2 | 100 | 2.5 | 7.5 | 1/2 | 2/2 | 0/2 | 1/2 | 0/2 | 0/2 | 0/2 | 2/2 | 4.5 | 13 | 0.081 | 165 | 1284 |
| hook | v0 | SessionStart hook | sonnet | A | 2 | 116 | 5.0 | 7.5 | 2/2 | 2/2 | 0/2 | 1/2 | 0/2 | 0/2 | 0/2 | 2/2 | 4.0 | 13 | 0.081 | 165 | 1320 |
| style | v0 | hook + progress rules as output style | sonnet | A | 2 | 90 | 3.5 | 5.0 | 1/2 | 2/2 | 0/2 | 1/2 | 0/2 | 0/2 | 0/2 | 2/2 | 8.5 | 17 | 0.097 | 211 | 1877 |
| both | v0 | hook (all) + output style (progress) | sonnet | A | 2 | 104 | 4.0 | 6.0 | 0/2 | 2/2 | 0/2 | 1/2 | 0/2 | 0/2 | 0/2 | 2/2 | 14.0 | 23 | 0.120 | 282 | 2778 |
| hook2 | v2 | SessionStart hook | sonnet | A | 2 | 104 | 5.5 | 3.0 | 0/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 0/2 | 2/2 | 11.5 | 23 | 0.109 | 236 | 2483 |
| hook4 | v4 | SessionStart hook | sonnet | A | 2 | 120 | 7.0 | 5.0 | 0/2 | 2/2 | 2/2 | 2/2 | 0/2 | 2/2 | 0/2 | 2/2 | 10.0 | 16 | 0.097 | 211 | 1922 |
| hook5 | v5 | SessionStart hook | sonnet | A | 2 | 82 | 5.5 | 3.0 | 0/2 | 2/2 | 2/2 | 2/2 | 0/2 | 2/2 | 0/2 | 2/2 | 9.0 | 18 | 0.097 | 191 | 2060 |
| plain | none | none | fable | B | 1 | 180 | 6.0 | 15.0 | 0/1 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 5.0 | 65 | 0.681 | 226 | 7645 |
| hook | v0 | SessionStart hook | fable | B | 1 | 224 | 12.0 | 8.0 | 0/1 | 0/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 | 6.0 | 88 | 0.866 | 288 | 10589 |
| style | v0 | hook + progress rules as output style | fable | B | 1 | 190 | 11.0 | 7.0 | 0/1 | 0/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 | 1/1 | 5.0 | 75 | 1.255 | 230 | 9135 |
| hook2 | v2 | SessionStart hook | fable | B | 1 | 130 | 8.0 | 3.0 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 | 8.0 | 69 | 0.774 | 237 | 8115 |
| hook4 | v4 | SessionStart hook | fable | B | 1 | 266 | 14.0 | 4.0 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 | 5.0 | 81 | 0.811 | 233 | 9872 |
| hook5 | v5 | SessionStart hook | fable | B | 1 | 102 | 5.0 | 4.0 | 0/1 | 0/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 | 5.0 | 64 | 0.696 | 232 | 7461 |

## 5. Per-run rows

`y*` in "checked+delivery stated" means the message has an explicit "Checked" statement and a commit/deploy/live statement. "not-checked" is `specific` (names something not tried), `nothing` (says "Not checked: nothing") or `no`.

| run | final lines | final words | code spans | internal paths/ids | test count | checked+delivery stated | not-checked | opening goal+steps | Done lines (final / mid-run) | ran real CLI | tests pass (n) | works | extra: rejects unknown options | turns | tools | dur s | cost $ | total in tok | out tok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-plain-sonnet-r1 | 5 | 109 | 8 | 2 | y | y | no | n | 0 / 0 | y | y (10) | y | y | 10 | 9 | 18.9 | 0.097 | 207972 | 2181 |
| A-plain-sonnet-r2 | 4 | 114 | 10 | 3 | y | n | no | n | 0 / 0 | n | y (10) | y | y | 14 | 13 | 23.5 | 0.107 | 208767 | 2693 |
| A-claudemd-sonnet-r1 | 2 | 93 | 6 | 0 | y | y | no | n | 0 / 0 | n | y (10) | y | y | 5 | 4 | 12.9 | 0.083 | 165610 | 1373 |
| A-claudemd-sonnet-r2 | 3 | 106 | 9 | 2 | y | y | specific | n | 0 / 0 | n | y (10) | y | y | 4 | 3 | 12.4 | 0.079 | 164083 | 1195 |
| A-hook-sonnet-r1 | 5 | 103 | 7 | 2 | y | y | no | n | 0 / 0 | n | y (10) | y | y | 4 | 3 | 12.3 | 0.080 | 164959 | 1276 |
| A-hook-sonnet-r2 | 5 | 128 | 8 | 2 | y | y | specific | n | 0 / 0 | n | y (10) | y | y | 4 | 3 | 14.2 | 0.082 | 165213 | 1364 |
| A-style-sonnet-r1 | 4 | 98 | 5 | 0 | y | y | no | n | 0 / 0 | n | y (10) | y | y | 13 | 12 | 23.5 | 0.113 | 256031 | 2561 |
| A-style-sonnet-r2 | 3 | 81 | 5 | 1 | y | y | specific | n | 0 / 0 | n | y (9) | y | n | 4 | 3 | 11.3 | 0.080 | 165403 | 1193 |
| A-both-sonnet-r1 | 3 | 107 | 7 | 0 | y | y | no | n | 0 / 0 | y | y (10) | y | y | 14 | 13 | 24.0 | 0.124 | 303586 | 2912 |
| A-both-sonnet-r2 | 5 | 102 | 5 | 0 | y | y | specific | n | 0 / 0 | y | y (10) | y | y | 14 | 13 | 21.5 | 0.115 | 259697 | 2643 |
| A-hook2-sonnet-r1 | 6 | 115 | 2 | 0 | y | y* | nothing | y | 1 / 0 | y | y (10) | y | y | 14 | 13 | 26.0 | 0.120 | 260386 | 2938 |
| A-hook2-sonnet-r2 | 5 | 92 | 4 | 0 | y | y* | nothing | y | 1 / 0 | y | y (10) | y | y | 9 | 8 | 19.2 | 0.097 | 210800 | 2028 |
| A-hook4-sonnet-r1 | 6 | 116 | 5 | 0 | y | y* | specific | n | 1 / 0 | n | y (9) | y | n | 11 | 10 | 17.2 | 0.098 | 211841 | 1965 |
| A-hook4-sonnet-r2 | 8 | 125 | 5 | 0 | y | y* | specific | n | 1 / 0 | n | y (10) | y | y | 9 | 8 | 15.8 | 0.096 | 210506 | 1879 |
| A-hook5-sonnet-r1 | 6 | 84 | 3 | 0 | y | y* | nothing | n | 0 / 0 | n | y (10) | y | y | 14 | 13 | 23.6 | 0.114 | 215706 | 2886 |
| A-hook5-sonnet-r2 | 5 | 80 | 3 | 0 | y | y* | nothing | n | 0 / 0 | n | y (10) | y | y | 4 | 3 | 11.7 | 0.081 | 165530 | 1235 |
| B-plain-sonnet-r1 | 7 | 191 | 20 | 4 | y | y | no | n | 0 / 0 | n | y (10) | y | y | 4 | 3 | 22.7 | 0.102 | 163933 | 2882 |
| B-plain-sonnet-r2 | 6 | 186 | 17 | 2 | y | n | no | n | 0 / 0 | y | y (10) | y | y | 4 | 3 | 22.5 | 0.102 | 164612 | 2953 |
| B-claudemd-sonnet-r1 | 6 | 174 | 12 | 0 | y | n | specific | n | 0 / 0 | y | y (9) | y | y | 4 | 3 | 19.3 | 0.099 | 166316 | 2344 |
| B-claudemd-sonnet-r2 | 5 | 134 | 9 | 0 | n | y | no | n | 0 / 0 | y | y (8) | y | y | 4 | 3 | 18.8 | 0.094 | 166254 | 2070 |
| B-hook-sonnet-r1 | 7 | 171 | 10 | 0 | y | y | no | n (goal only) | 0 / 0 | y | y (9) | y | y | 4 | 3 | 20.1 | 0.103 | 167601 | 2571 |
| B-hook-sonnet-r2 | 6 | 135 | 10 | 0 | y | y | no | n | 0 / 0 | y | y (11) | y | y | 5 | 4 | 23.5 | 0.108 | 212248 | 2771 |
| B-style-sonnet-r1 | 6 | 173 | 13 | 0 | y | y | no | n | 0 / 0 | y | y (10) | y | y | 6 | 5 | 28.1 | 0.125 | 260267 | 3323 |
| B-style-sonnet-r2 | 6 | 159 | 11 | 0 | y | y | no | n | 0 / 0 | y | y (9) | y | y | 6 | 5 | 25.6 | 0.120 | 259661 | 3142 |
| B-both-sonnet-r1 | 8 | 203 | 11 | 0 | y | y* | no | n | 0 / 0 | y | y (12) | y | y | 5 | 4 | 37.4 | 0.153 | 217316 | 5758 |
| B-both-sonnet-r2 | 5 | 162 | 9 | 0 | y | n | specific | n | 0 / 0 | n | y (10) | y | y | 4 | 3 | 19.9 | 0.099 | 167808 | 2419 |
| B-hook2-sonnet-r1 | 5 | 150 | 5 | 0 | y | y* | nothing | y | 1 / 0 | y | y (8) | y | y | 5 | 4 | 22.5 | 0.107 | 213136 | 2594 |
| B-hook2-sonnet-r2 | 8 | 133 | 4 | 0 | n | y* | nothing | y | 4 / 0 | y | y (8) | y | y | 5 | 4 | 20.5 | 0.111 | 212718 | 2961 |
| B-hook2-sonnet-r3 | 6 | 138 | 6 | 0 | y | y* | specific | y | 0 / 0 | n | y (8) | y | y | 4 | 3 | 17.1 | 0.093 | 166950 | 2061 |
| B-style2-sonnet-r1 | 9 | 136 | 4 | 0 | y | y* | specific | y | 4 / 0 | y | y (9) | y | y | 4 | 3 | 23.9 | 0.104 | 167925 | 2866 |
| B-style2-sonnet-r2 | 5 | 122 | 3 | 0 | n | y* | nothing | y | 1 / 0 | y | y (9) | y | y | 4 | 3 | 22.3 | 0.106 | 168573 | 2914 |
| B-style2-sonnet-r3 | 6 | 134 | 4 | 0 | n | y* | nothing | y | 1 / 0 | y | y (10) | y | y | 5 | 4 | 25.9 | 0.115 | 214480 | 3154 |
| B-claudemd2-sonnet-r1 | 8 | 123 | 3 | 0 | n | y* | nothing | n | 4 / 0 | y | y (9) | y | y | 4 | 3 | 24.3 | 0.104 | 166349 | 2776 |
| B-claudemd2-sonnet-r2 | 9 | 121 | 5 | 0 | n | y* | nothing | n | 4 / 0 | y | y (10) | y | y | 4 | 3 | 23.8 | 0.107 | 167524 | 3043 |
| B-claudemd2-sonnet-r3 | 9 | 134 | 3 | 0 | n | y* | specific | n | 4 / 0 | y | y (8) | y | y | 4 | 3 | 22.0 | 0.097 | 166637 | 2304 |
| B-claudemd2-sonnet-r4 | 5 | 115 | 3 | 0 | n | y* | specific | n | 1 / 0 | n | y (8) | y | y | 4 | 3 | 18.3 | 0.091 | 165889 | 1928 |
| B-hook3-sonnet-r1 | 4 | 107 | 5 | 0 | n | y* | specific | y | 0 / 0 | n | y (8) | y | y | 4 | 3 | 16.1 | 0.096 | 167262 | 2250 |
| B-hook3-sonnet-r2 | 6 | 163 | 3 | 0 | y | y* | nothing | y | 1 / 0 | y | y (8) | y | y | 4 | 3 | 22.6 | 0.104 | 168382 | 2735 |
| B-hook4-sonnet-r1 | 6 | 160 | 5 | 0 | y | y* | specific | y | 1 / 0 | y | y (8) | y | y | 6 | 5 | 24.8 | 0.118 | 259704 | 3005 |
| B-hook4-sonnet-r2 | 5 | 158 | 5 | 0 | n | y* | nothing | y | 1 / 0 | y | y (8) | y | y | 5 | 4 | 21.4 | 0.107 | 212570 | 2694 |
| B-hook5-sonnet-r1 | 9 | 150 | 3 | 0 | y | y* | nothing | y | 0 / 0 | y | y (8) | y | y | 5 | 4 | 21.7 | 0.108 | 171181 | 2711 |
| B-hook5-sonnet-r2 | 10 | 136 | 5 | 0 | n | y* | nothing | y | 0 / 0 | y | y (10) | y | y | 5 | 4 | 25.5 | 0.113 | 214540 | 2982 |
| B-plain-fable-r1 | 6 | 180 | 15 | 0 | y | y | no | n | 0 / 0 | y | y (12) | y | y | 5 | 4 | 65.2 | 0.681 | 225664 | 7645 |
| B-hook-fable-r1 | 12 | 224 | 8 | 0 | n | y* | no | y | 1 / 0 | y | y (17) | y | y | 6 | 5 | 87.7 | 0.866 | 288490 | 10589 |
| B-style-fable-r1 | 11 | 190 | 7 | 0 | n | y* | no | y | 1 / 0 | y | y (11) | y | y | 5 | 4 | 75.0 | 1.255 | 229895 | 9135 |
| B-hook2-fable-r1 | 8 | 130 | 3 | 0 | n | y* | specific | y | 4 / 0 | y | y (15) | y | y | 8 | 7 | 68.8 | 0.774 | 236960 | 8115 |
| B-hook4-fable-r1 | 14 | 266 | 4 | 0 | n | y* | specific | y | 1 / 0 | y | y (15) | y | y | 5 | 4 | 81.0 | 0.811 | 233171 | 9872 |
| B-hook5-fable-r1 | 5 | 102 | 4 | 0 | n | y* | specific | y | 0 / 0 | y | y (14) | y | y | 5 | 4 | 64.3 | 0.696 | 232157 | 7461 |

Extra facts across all 48 runs: `docs/STATUS.md` created 0 times (the task finished in one session, so the rule's condition never applied); 7 of 14 v0 hook, style and both runs looked for `docs/STATUS.md` in their first shell call (2 of 25 with later texts, 0 of 5 plain). Every run but two also made `report` reject unknown options, which nobody asked for (plain 5/5, v0 17/18, v2 and later 24/25).

## 6. Verbatim final messages, scenario B

**plain, Sonnet** (`B-plain-sonnet-r1`, 191 words, 7 non-empty lines, $0.102)

No message before the first tool call. Final message:

> `tasklog report` now takes `--csv` and `--since YYYY-MM-DD`, and the README and usage text describe both. All 10 tests pass, including new ones for both options.
>
> - **`--csv`:** it prints a `project,minutes` header, one row per project and a `TOTAL` row. Minutes are plain numbers, and project names containing commas or quotes are quoted.
> - **`--since`:** it counts only entries on or after the given date. Both `--since 2026-11-01` and `--since=2026-11-01` work. A malformed date or an unknown option exits with code 2 and a message.
> - **Both together:** the two options combine.
> - **Total line:** the text report already ended with a `TOTAL` line, so I left it as is. The CSV gets its own total row.
>
> **Dates on entries:** entries had no date, so `--since` had nothing to filter on. `add` now stores a `date` (local `YYYY-MM-DD`) on each new entry. Entries recorded before this change have no date, so `--since` leaves them out, because I can't tell when they happened. Reports without `--since` still count them. The README says this too.
>
> The changes are in `src/cli.js` and `src/report.js`, with tests added to `test/cli.test.js` and `test/report.test.js`. Nothing is committed.

**claudemd (v0 text, file read by the model), Sonnet** (`B-claudemd-sonnet-r1`, 174 words, 6 non-empty lines, $0.099)

No message before the first tool call. Final message:

> `tasklog report` now takes `--csv` and `--since YYYY-MM-DD`, and the README describes both. I ran the test suite and all 9 tests pass, including two new ones for these options. I didn't try the commands by hand in a terminal.
>
> - **Total line:** the report already printed one, so I left it as it was. The CSV output also ends with a `TOTAL` row.
> - **CSV:** `--csv` prints a `project,minutes` header, one row per project, then the `TOTAL` row. Minutes are whole numbers, not "1h 30m". Project names with commas or quotes are escaped.
> - **`--since`:** only entries recorded on or after that date are counted, and it works together with `--csv`. A bad date or an unknown option prints an error and exits with code 2.
> - **Dates on new entries:** entries had no date, so `--since` had nothing to filter on. `tasklog add` now records today's date.
> - **Existing entries have no date:** they are left out whenever `--since` is used. Say if you'd rather count them or give them a date.

**hook (v0), Sonnet. The only v0 Sonnet run that wrote anything before its first tool call** (`B-hook-sonnet-r1`, 171 words, 7 non-empty lines, $0.103)

Opening message, before the first tool call:

> Goal: add CSV export, a `--since` filter and a total line to the report command, then update the README.

Final message:

> `tasklog report` now has `--csv` and `--since YYYY-MM-DD`, and the README describes both. All 9 tests pass, including new ones for both options, a bad date and an unknown option. I also ran the command by hand and it worked.
>
> - **CSV:** `--csv` prints `project,minutes` rows and then a `TOTAL` row. Project names containing commas or quotes are quoted correctly.
> - **Since filter:** `--since` only counts entries recorded on or after that date. A malformed date or an unknown option prints an error and exits with code 2.
> - **Total line:** the table already ended with a `TOTAL` line, so I didn't change it.
> - **Dates:** entries had no date, so `add` now saves today's date with each new entry.
>
> Entries you logged before this change have no date. When you use `--since`, they are left out, and the README says so. If you'd rather count them, I could treat undated entries as always included. I didn't do that because it would make the filter's totals misleading.
>
> I haven't committed anything.

**style (v0), Sonnet** (`B-style-sonnet-r1`, 173 words, 6 non-empty lines, $0.125)

No message before the first tool call. Final message:

> `tasklog report` now has `--csv` and `--since`, and the README describes both. All 10 tests pass, and I also tried the commands by hand, including a bad date. Nothing is committed yet.
>
> - **CSV:** `tasklog report --csv` prints `project,minutes` rows with a final `TOTAL` row. Minutes are plain numbers, and project names with commas or quotes are quoted correctly.
> - **Since filter:** `tasklog report --since 2026-02-01` counts only entries from that date on. It also accepts `--since=2026-02-01`. A missing or invalid date prints a message and exits with an error.
> - **Total line:** the normal report already ended with a `TOTAL` line, so I left that as it was.
>
> **Dates:** entries didn't store a date, so `add` now records today's date on every new entry. Entries you logged before this change have no date, and `--since` leaves them out. Without `--since`, they're still counted.
>
> Decision for you: if you'd rather treat old undated entries as counting toward `--since`, say so. I'd keep them excluded, since there's no way to know when they happened.

**both (v0), Sonnet** (`B-both-sonnet-r2`, 162 words, 5 non-empty lines, $0.099)

No message before the first tool call. Final message:

> `tasklog report` now takes `--csv` and `--since YYYY-MM-DD`, and the README describes both. All 10 tests pass, including new ones for each option and for bad input. I only ran the tests, not the real command by hand.
>
> - **CSV:** `--csv` prints a `project,minutes` header, one row per project and a `TOTAL` row. Project names containing commas or quotes are quoted correctly.
> - **Since:** `--since` only counts entries on or after the date you give. A malformed date, or an unknown option, prints an error and exits with code 2.
> - **Total line:** the normal report already had one, so I left it as it was.
>
> **Decision for you:** entries never stored a date before, so `--since` had nothing to filter on. New entries now record the date they were added. Existing entries have no date, so `--since` leaves them out. If you'd rather count them, say so. I can add a date to old entries, but I'd have to guess it.

**hook2 (v2), Sonnet** (`B-hook2-sonnet-r2`, 133 words, 8 non-empty lines, $0.111)

Opening message, before the first tool call:

> Goal: The report command can export CSV, filter by start date, and show a total line, and the README explains it.
> 1. CSV export
> 2. A --since date filter
> 3. A total line
> 4. README updated

Final message:

> Done 1 of 4: CSV export
> Done 2 of 4: the `--since` date filter
> Done 3 of 4: total line (the report already had one, so I kept it and added a matching total row to the CSV)
> Done 4 of 4: README updated
>
> Works now: `tasklog report --csv` and `tasklog report --since 2026-11-01` work alone or together. A bad or missing date gives a clear error. New entries now save the date they were added.
> Checked: ran the test suite, including a new test of the filter, the CSV and the error cases. Also ran the real command once. Not checked: nothing else.
> Live: no, not committed or deployed.
> Next: Entries logged before this change have no date, so `--since` leaves them out. Want a one-time fix that gives them a date?

**style2 (v2), Sonnet** (`B-style2-sonnet-r1`, 136 words, 9 non-empty lines, $0.104)

Opening message, before the first tool call:

> Goal: You can run the report command with CSV output, a start-date filter and a total line, and the README explains how.
> 1. Report can export CSV
> 2. Report accepts a --since date filter
> 3. Report shows a total line
> 4. README is updated
>
> Let me look at the project first.

Final message:

> Done 1 of 4: CSV export works.
> Done 2 of 4: `--since` works.
> Done 3 of 4: the total line was already there. It also shows in the CSV and in `--since` reports.
> Done 4 of 4: README updated.
>
> Works now: `tasklog report --since 2026-11-01 --csv` gives a spreadsheet-ready export with a total row. Each option also works on its own. New entries are stamped with the date they were added.
> Checked: all 9 tests pass, including new ones for the date filter, CSV and a bad date. I also ran the real command and saw CSV output and the empty result.
> Not checked: opening the CSV in a spreadsheet app.
> Live: no, not committed or deployed.
> Next: Entries you logged before this change have no date, so `--since` skips them. Want me to commit this?

**claudemd2 (v2 text, file read by the model), Sonnet** (`B-claudemd2-sonnet-r3`, 134 words, 9 non-empty lines, $0.097)

No message before the first tool call. Final message:

> Done 1 of 4: CSV export works.
> Done 2 of 4: the date filter works.
> Done 3 of 4: the total line was already there and still shows.
> Done 4 of 4: the README is updated.
>
> Works now: `tasklog report --csv` prints a spreadsheet-ready list ending in a total. `tasklog report --since 2026-11-01` counts only work from that date on. You can use both together. New entries now record their date. Entries you logged before this change have no date, so `--since` leaves them out.
> Checked: I ran the project's tests, which all pass, and tried both options on a sample log, including a bad date, which gives a clear error.
> Not checked: how the CSV opens in Excel.
> Live: no, not committed or deployed.
> Next: Decide whether to commit this. I recommend yes.

**hook3 (v3), Sonnet** (`B-hook3-sonnet-r1`, 107 words, 4 non-empty lines, $0.096)

Opening message, before the first tool call:

> Goal: You'll be able to run the report command with CSV output, a start-date filter, and a total line, and the README will explain them.
> 1. CSV export for the report
> 2. A --since date filter
> 3. A total line at the end of the report
> 4. README updated

Final message:

> Works now: `tasklog report --csv` prints `project,minutes` rows plus a TOTAL row. `--since 2026-01-31` counts only entries from that date on. The two options work together. The README covers both. The plain report already had a total line, so I left it alone.
> Checked: the full test suite passes, including new tests for CSV, `--since` and bad dates. Not checked: I didn't try it against your real log file.
> Live: no, not committed or deployed.
> Next: old entries have no date, so `--since` skips them. New entries are dated from now on. Tell me if you'd rather old entries count as "always included". Should I commit this?

**hook4 (v4), Sonnet** (`B-hook4-sonnet-r1`, 160 words, 6 non-empty lines, $0.118)

Opening message, before the first tool call:

> Goal: You can run the report command with a date cutoff, get a total line, and export the result as CSV, and the README explains how.
> 1. The report can be exported as CSV.
> 2. The report can be limited to entries since a given date.
> 3. The report shows a total line.
> 4. The README describes the new options.
>
> I'll start by looking at the project.

Final message:

> Done 4 of 4.
> Works now: `tasklog report --csv` prints `project,minutes` rows with a final `TOTAL` row. `tasklog report --since 2026-11-01` counts only entries from that date on, and you can combine the two options. The total line was already in the normal report, so I kept it and added it to the CSV. The README describes both options.
> Checked: All 8 tests pass, including a new one for the two options. I also ran the command by hand: CSV output, a future date giving "No entries yet.", and a malformed date giving a clear error.
> Not checked: Opening the CSV in a spreadsheet app.
> Live: no, not committed or deployed.
> Next: Entries had no date before, so `--since` ignores your existing entries. Only entries added from now on can be filtered. If you want old entries included, tell me what date to give them and I'll add it. I'd suggest that only if you have a date in mind.

**hook5 (v5), Sonnet** (`B-hook5-sonnet-r1`, 150 words, 9 non-empty lines, $0.108)

Opening message, before the first tool call:

> Goal: You'll be able to run the report command with CSV output, a start-date filter, and a total line, and the README will explain them.
> 1. CSV export
> 2. --since date filter
> 3. Total line
> 4. README updated

Final message:

> Done: 4 of 4 (the total line was already in the report, so I kept it and added it to the CSV too).
> Works now:
> - `tasklog report --csv` prints rows of project and minutes, with a TOTAL row at the end.
> - `tasklog report --since 2026-11-01` counts only entries from that date on. The two options can be used together.
> - A badly formatted date or an unknown option gives an error message.
> - The README describes both options.
>
> Checked: I ran the tests, including a new one for these options, and all 8 pass. I also ran the real command and saw the CSV and the date filter work. Not checked: nothing.
> Live: no, not committed or deployed.
> Next: Entries you recorded before this change have no date, so `--since` leaves them out. I recommend that, but if you'd rather count them, tell me and I'll change it.

**plain, Fable** (`B-plain-fable-r1`, 180 words, 6 non-empty lines, $0.681)

No message before the first tool call. Final message:

> `tasklog report` now takes `--since YYYY-MM-DD` and `--csv`, and the README documents both. All 12 tests pass and a real run from the command line behaved as expected; nothing is committed.
>
> - **Total line:** the plain report already ended with a `TOTAL` line, so I left that as is. The CSV output also ends with a `TOTAL` row.
> - **`--since`:** entries had no dates, so `add` now stamps each new entry with the local date. The filter is inclusive of the given day.
> - **Existing entries:** anything recorded before this change has no date, so a `--since` report leaves it out and prints how many were skipped on stderr (e.g. `tasklog: skipped 1 undated entry`). Without `--since` they are counted as before.
> - **`--csv`:** prints `project,minutes` to stdout with minutes as a plain number, so you save it with `tasklog report --csv > report.csv`. It combines with `--since`.
>
> Decision for you: the `TOTAL` row in the CSV matches the text report, but it will be double-counted if you sum the column in a spreadsheet. Say if you want it dropped.

**hook (v0), Fable** (`B-hook-fable-r1`, 224 words, 12 non-empty lines, $0.866)

Opening message, before the first tool call:

> Goal: the report command can export CSV, filter by a start date, and show a total, with the README explaining all three.
>
> 1. Understand how the report command works today
> 2. Add the `--since` date filter
> 3. Add the total line
> 4. Add CSV export
> 5. Check it all works, including a bad-input case
> 6. Update the README

Final message:

> Done 6 of 6. The report command now does all three things and the README explains them.
>
> **What works now**
> - **Date filter:** `tasklog report --since 2026-11-01` counts only entries from that day onward.
> - **CSV export:** `tasklog report --csv` prints the report as CSV, and it combines with `--since`. Add `> report.csv` to save it to a file.
> - **Total line:** the normal report already had one. I added a `TOTAL` row to the CSV as well.
> - **Bad input:** a mistyped date or option gives a clear message instead of a wrong report.
>
> **Things you should know**
> - **Entries had no dates before this change.** New entries are now stamped with the day they are added. Older entries can't be placed in time, so `--since` leaves them out and says how many it skipped; a plain report still counts everything.
> - **The `TOTAL` row in the CSV** will be double-counted if you sum the column in a spreadsheet. Say if you'd rather the CSV had no total row.
> - **`tasklog list`** doesn't show the new dates; I left it alone since you didn't ask.
>
> **Status:** built and checked — the project's tests pass and I tried each option by hand, including bad dates and a log with old undated entries. Nothing is committed yet.
>
> **Next:** tell me if you want this committed.

**style (v0), Fable** (`B-style-fable-r1`, 190 words, 11 non-empty lines, $1.255)

Opening message, before the first tool call:

> Goal: the report command gains CSV export, a `--since` date filter and a total line, with the README brought up to date.
>
> 1. See how the report command works today
> 2. Add the `--since` date filter
> 3. Add the total line
> 4. Add CSV export
> 5. Check it all works, including a bad-input case
> 6. Update the README

Final message:

> Done 6 of 6: all three report features work and the README describes them.
>
> **What works now**
> - `tasklog report --since 2026-11-01` counts only entries from that day onward.
> - `tasklog report --csv` prints the report as CSV (header, one row per project, a `TOTAL` row); redirect it to a file to save it. It combines with `--since`.
> - The total line was already there in the plain report, so I left it as is and added a matching `TOTAL` row to the CSV.
> - A bad date or unknown option gives a short error instead of a wrong report.
>
> **Things you should know**
> - Entries had no date before, so `add` now stamps each new entry with the day it was recorded.
> - Entries logged before this change have no date. They still count in the plain report, but a `--since` report leaves them out and says how many were skipped.
>
> **Status:** built and checked — the project's tests pass, including new ones for these features, and I ran the real command for each case plus a bad date. Nothing is committed.
>
> **Decision for you:** should I commit this?

**hook5 (v5), Fable** (`B-hook5-fable-r1`, 102 words, 5 non-empty lines, $0.696)

Opening message, before the first tool call:

> Goal: You can run the report for a chosen date range, see a total at the bottom, and save it as a spreadsheet-friendly CSV file.
> 1. The report can be exported as CSV
> 2. The report can be limited to entries since a given date
> 3. The report ends with a total line
> 4. The README explains the new options

Final message:

> Done: 4 of 4
> Works now: `tasklog report --since 2026-01-31` counts only entries from that date on, `--csv` gives a spreadsheet version (add `> report.csv` to save it), and both end with a TOTAL line. The README covers all of it.
> Checked: ran the project's tests and tried the real command, including a wrong date. Not checked: opening the CSV in a spreadsheet app.
> Live: no, not committed or deployed.
> Next: entries had no dates until now, so `--since` skips everything you logged before today and says how many. I recommend keeping that; say if you'd rather old entries were always counted.


## 7. Reading

### Which channel produces owner-language, short, stepwise reporting?

None of them does it on its own, and each of them does it with the right text.

- With v0 prose on Sonnet 5.5, hook, output style, both together, and a repo file the model read all gave the same result: no step list (0/8 on B), final messages 134 to 203 words on B against 186 to 191 plain, test counts in 15 of 16 runs. This reproduces round one's "no effect" with the rule delivered whole, so truncation was not the only reason the stock rule failed.
- With v2 text, hook and style both gave the opening 3/3 and the labelled final lines 3/3. Hook-delivered v3, v4 and v5 held at 2/2 each on B.
- A file in the repo that the model happened to read mid-run was enough for the final-message template (4/4). So the final-message rules do not need a privileged channel at all; they need to be a template.
- The opening list needs the rules in context before the first tool call. Hook and style satisfy that; a file the model reads with its first shell command does not (0/4).

What separates v0 from v2, confounded (all three changed at once): an observable trigger ("asks for more than one thing" instead of "more than a few steps"), a literal fill-in shape instead of a description, and one sentence of reason ("the owner cannot read code and follows the work only through your messages").

### Which sub-rules stick

Sonnet 5.5, text v2 or later (22 runs: 16 B, 6 A):

| sub-rule | result |
|---|---|
| Labelled final lines (Works now / Checked / Not checked / Live / Next) | 22/22 |
| No source file paths or function names | 22/22 clean (plain: 4/4 runs had them) |
| No exit-code talk | 22/22 clean (plain 4/4 and v0 9/16 mentioned exit codes) |
| States whether it is live or committed | 22/22 (plain 2/4, v0 14/16) |
| Goal and numbered steps before the first tool call, scenario B, hook or style | 12/12 |
| Says what was not checked | line present 22/22; names something specific in 8, says "nothing" in 14 |
| No test counts | partial: counts still present in 12/22 (A 6/6, B 6/16); plain 4/4, v0 15/16 |
| "Under 100 words" | not met: 3 of 18 capped runs, all on scenario A. The cap still shortens: Fable 102 and 130 words with a cap, 266 without (v4); Sonnet B 123 to 143 with, 159 without |
| Done line as each outcome finishes | 0/48 mid-run. Done lines appear only in the final message, as a tally |
| "Leave this line out if you gave no numbered list" (v4) | 0/2 |
| Trigger threshold | v2 "more than one thing" produced a goal and a 2-step list for the single-feature request A (2/2, noise). "Three or more things" (v4, v5) did not (0/4), and still fired on B (4/4) |
| "Change only what the request needs" (unchanged kernel line) | no effect: unrequested unknown-option rejection added in 41 of 43 kernel runs and 5 of 5 plain runs |
| Mentions unrequested changes in the final message (no template slot for it) | worse with the template: 11 of 24 runs, against 19 of 22 for plain and v0 |

Partial following with v0 prose on Sonnet: the format rules did nothing, but three softer effects showed. Source file paths dropped (4/16 runs against 4/4 plain), delivery status was stated more often (14/16 against 2/4), and when the real command had not been run the model said so in 4 of 7 such runs (plain 0 of 2). With v2 and later that last disclosure rose to 5 of 7; the two misses are below.

Honesty of the new lines. "Not checked: nothing" was written 14 times. In one run (`A-hook5-sonnet-r2`) only the test suite had been run, and in another (`A-hook5-sonnet-r1`) "ran the command by hand" meant calling the module from `node -e`, not the real entry point. The `or "nothing"` option in the template is an easy exit and should go (untested change).

"Next:" turned into "want me to commit this?" in 11 of 15 v2 and v3 runs. That is a prompt for the owner on every task. v4 and v5 narrowed the line to "the one decision you need from the owner ... or nothing"; after that 9 of 10 runs wrote a real decision or "nothing" and 1 asked about committing.

Side-effect disclosure got worse, and this is the template's main cost. Almost every run changed behaviour nobody asked for (unknown options are now rejected). Plain and v0 runs said so in the final message in 19 of 22 cases. Template runs said so in 11 of 24, and on scenario B in 5 of 18. The fixed lines have no slot for "what else I changed", so it falls out.

### What it costs

- Tokens: +781 (v0) to +912 (v5) input tokens on every request, cached after the first. At the measured Sonnet cache-read price that is about $0.0001 per request and $0.004 for the first write.
- Dollars, time, turns on Sonnet: no measurable difference. Scenario B: plain $0.102, 23 s, 4.0 turns (n=2); v2 and later $0.105, 22 s, 4.5 turns (n=16); v0 arms $0.113, 24 s, 4.8 turns (n=8). Run-to-run spread ($0.079 to $0.153) follows whether the model edited with one script or with separate Edit calls, not the arm.
- Extra visible text: the opening list adds 36 to 67 words before the first tool call.
- Fable (n=1 each, scenario B): plain $0.681; hook v0 $0.866 (+27%, 39% more output tokens, 17 tests in the suite against 12, 227 lines added against 155); hook v2 $0.774 (+14%); hook v4 $0.811 (+19%); hook v5 $0.696 (+2%); style v0 $1.255, of which about $0.49 is the cold cache write, leaving about $0.77 (+13%).
- Output style only: the one-time cold-prefix write described in section 3, and the loss of whatever output style the owner had chosen.

### Does the output style suppress coding behaviour or tests?

Not observed. All 12 runs with an active output style (style, both, style2) pass their tests and the functional check; the Sonnet suites ended with 9 to 12 tests against 10 plain. On Sonnet 5.5 and Fable 5.2 the default system prompt has no software-engineering section to lose, so `keep-coding-instructions` has nothing to keep (probe, and the docs say the same). Not tested: behaviour under the full system prompt, or a style without `keep-coding-instructions`.

One thing to watch, any channel: with v2 and later, Sonnet added fewer separate test cases on scenario B (1.6 new test blocks on average against 3.0 plain and 2.8 v0) while the number of added assertions stayed close (6.7 against 7.5 and 7.4). All features worked. This could be consolidation into fewer tests or a side effect of telling the model that test counts do not matter; n is too small to say.

## 8. Recommendation

**Channel.** One SessionStart hook that prints the whole kernel as plain text, under 3,000 characters, with no matcher so it re-fires after compaction. Do not ship the output style: it matched the hook and did not beat it, it overrides the owner's own style, it is absent on Codex and in subagents, and it changes the prompt-cache prefix. Do not deliver the same rules twice. Do not rely on CLAUDE.md or AGENTS.md edits for this (round one already rejected adoption; here a repo file was read too late for the opening).

**Wording.** Replace the prose rule ("2-5 short lines / no file paths or test counts / built-checked-live", and kernel-v0's version of it) with a fill-in template, an observable trigger and one sentence of reason. The tested text (v5, 978 characters; whole kernel 2,843 characters, about 910 tokens per request):

```
## Keeping the owner informed
The owner cannot read code and follows the work only through your messages. File names, function names, exit codes and test counts mean nothing to them; leave them out unless asked. Commands the owner would type themselves are fine.

When a request asks for three or more things, write this before your first tool call:
Goal: <one sentence: what the owner will be able to do>
1. <outcome, in the owner's words>
2. <one line per thing asked for>
In longer work, write "Done 2 of 4: <outcome>" as each outcome is checked.

Your last message is only these lines, under 100 words in all:
Done: <"4 of 4", or "3 of 4" and what is left; for a single request just "yes" or "not yet">
Works now: <what the owner can now do>
Checked: <how you saw it work>. Not checked: <what you did not try, or "nothing">
Live: <"no, not committed or deployed", or where it is live>
Next: <the one decision you need from the owner, with your recommendation, or "nothing">
```

Results for v5 through the hook: Sonnet B 2/2 opening list, 2/2 labelled lines, 136 and 150 words (plain 186 and 191); Sonnet A 2/2 no opening list (correct for a single request), 80 and 84 words (plain 109 and 114); Fable B opening list, 102 words (plain 180), cost +2%. All five runs pass tests and the functional check.

Changes I would still make to v5, each untested (HYPOTHESIS):

1. Drop `or "nothing"` from the Not-checked line; ask for "the most important thing you did not try".
2. Add "in plain words, no counts" to the Checked line: test counts survived in 3 of 4 Sonnet v5 runs.
3. Stop promising live "Done N of M" progress. Keep the tally in the final message (it forces a count against the opening list), and treat mid-run progress as unproven until it is tested on work that spans many tool calls.
4. Add a line "Also changed: <anything you changed that was not asked for, or "nothing">". Without it the template hid unrequested behaviour changes in 13 of 24 runs.
5. Reword "Change only what the request needs": it had no effect in 41 of 43 runs. That is a separate experiment.

## 9. The improved variant

The brief asked for one improved variant of the best arm, 2 runs. The best arm was the hook (equal to style on behaviour, cheaper and portable). Variant v2 through the hook, scenario B, Sonnet: 3 of 3 runs opened with the goal and four outcome steps, 3 of 3 ended with the labelled lines, final message 133 to 150 words (plain 186 to 191), test count still present in 2 of 3, cost $0.103 (plain $0.102). So it improved, clearly on structure and owner language, modestly on length, not on live progress.

Because runs cost about $0.10, I went further than asked: the same v2 text through the output style (3 runs) and a repo file (4 runs) to separate wording from channel, and three hook-only refinements (v3, v4, v5; 2 Sonnet B runs each, plus A and Fable runs for v4 and v5). v3 failed its one aim. v4 fixed the over-triggering on single requests but lengthened messages when the word cap was removed. v5 restored the cap and is the recommended text.

## 10. Limits

1. Small N: 2 to 4 runs per cell on Sonnet, 1 per cell on Fable. Only the v0-against-template contrast (0/8 against 12/12) is strong; arm differences in cost, turns and test effort are within noise.
2. One toy project and two short tasks that the model finishes in 3 to 14 tool calls and under 90 seconds. Mid-run progress, plan changes, STATUS.md continuity, compaction survival and second-prompt behaviour were not exercised. Whether the rules still hold at turn 200 is unknown.
3. The CLAUDE.md arm did not test auto-loaded project memory: this environment refuses memory files under the scratchpad, and I was limited to writing there. A valid control needs the toy project outside any scratchpad path.
4. Headless `-p` runs in a cloud container whose base prompt is about 39K tokens. Absolute token overheads transfer; percentages and cache behaviour may not. Interactive sessions were not tested.
5. v2 changed trigger, template and reason together, so which of the three carries the effect is not known. v5 was run 5 times in total.
6. Measures are regex plus my reading of every final message; "owner language" has no blind rater. Codex was not run.

## 11. Files

- Report: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/design/exp-channel.md`
- Prototype plugins: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/plugins/vx-hook`, `vx-style`, `vx-both`, `vx-hook2`, `vx-style2`, `vx-hook3`, `vx-hook4`, `vx-hook5`
- Rule texts: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/text/` (`kernel.md` = v0, `kernel-v2.md` ... `kernel-v5.md`, `progress*.md`)
- Runner, analyzers, functional check: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/bin/run.sh`, `analyze.py`, `table.py`, `accept.sh`, `report.py`
- Transcripts (stream-json): `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/transcripts/` (run ids `<scenario>-<arm>-<model>-r<n>`; probes `P-*`, `probe2-*`, `probe3-*`, `probe4-*`)
- Per-run metadata, diffs, test output: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/meta/<run id>/`; final trees: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/runs/<run id>/`
- Machine-readable rows: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/rows.json`; tables: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/tables.md`, `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/means.md`
- CLAUDE.md refusal log: `/tmp/claude-0/-home-user-vibe/319f44f5-1818-5ce8-b943-d0cf6a9e5c7a/scratchpad/work/exp-channel/probe/debug-claudemd.log`

Side effects outside the work directory, none made by hand: loading prototypes with `--plugin-dir` made Claude Code create eight empty folders `/root/.claude/plugins/data/vx-*-inline`. `/root/.claude/settings.json` gained `"theme": "auto"` at 00:14:54 UTC while nested sessions from this and other agents were running; I did not edit that file and `enabledPlugins` is unchanged. `/home/user/vibe` is clean (`git status --porcelain` empty).
