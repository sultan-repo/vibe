# Prototype: `vibe-next`

This is the design recommended in section 5 of `../ASSESSMENT.md`, exactly as measured in section 6 (the revised text). It is evidence for the assessment, not a release. It has the open defects listed in section 6.4, and no eval suite or tests of its own yet.

| File | Size | What it does |
| --- | --- | --- |
| `vibe-next/rules.md` | 3,781 characters | The owner's standing preferences. Delivered whole at session start, after `/clear` and after compaction |
| `vibe-next/hooks/hooks.json` | 19 lines | Two SessionStart handlers (rules; status) and one PreCompact line |
| `vibe-next/hooks/status.py` | 126 lines | Reads `docs/STATUS.md`, from the working folder if it has unsaved edits, otherwise the newest committed copy on any branch. Read-only. Prints nothing when there is nothing to say |
| `vibe-next/hooks/run.sh` | 7 lines | Runs the reader; exits quietly if Python 3 is not usable |
| `vibe-next/hooks/keep.txt` | 1 line | What a compaction summary must keep |

## Trying it

It is named `vibe-next` so it can load beside an installed Vibe without clashing. To compare it fairly, switch the installed Vibe off for that session:

```sh
claude --plugin-dir /path/to/assessment/prototype/vibe-next \
  --settings '{"enabledPlugins":{"vibe@vibe":false}}'
```

Then give it a request with three or more parts, a one-line fix, and a change that touches sign-in or deletes stored data, and compare with a plain session.

## Before any of this ships

- Change the name to `vibe` and build the eval suite and size tests described in section 5.5.
- Fix or accept each defect in section 6.4, re-running the suite after every wording change: the lines interact.
- Run the core cases on the model you actually use, and look at the session-start line once in a real terminal.
- Ship it together with the deletions in roadmap step 1, as one change.
