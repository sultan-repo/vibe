# Evidence behind section 6 of the assessment

These are the working write-ups of the live experiments, as their authors left them. They are raw: paths that begin with `/tmp/claude-0/...` pointed at a session scratch directory that no longer exists, and "v7" and "v8" are the first and the revised prototype text.

| File | What it is | Sessions |
| --- | --- | --- |
| `exp-verify.md` | Does a short, fully delivered core change behaviour? Unchecked fix, hidden regression, scope. Plain, Vibe 4.15 and a candidate core, with ablations | 110 |
| `exp-channel.md` | Through which channel do reporting rules work: startup hook, output style, both, repo file? | 62 |
| `measure-a-first-text.md` | Prototype, first text: delivery checks, tool-free native eval, one-line fix, read-only question | 31 plus 24 eval runs |
| `measure-b-first-text.md` | Prototype, first text: multi-part feature, pause and resume, risky change with review, default model | 82 |
| `measure-c-revised-text.md` | Prototype, revised text, beside the recorded numbers. Vibe 5.0 ships one further revision of this text; its numbers are in `../../evals/results/` | 36 |

The round-one audits, their verifier reports, the research notes, the three competing designs, the critic and the judges are not in the repository; they were delivered separately as an archive.
