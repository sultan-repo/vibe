# Vibe v4.5.0

Vibe 4.5 brings a lighter Claude Code workflow and a visual progress board.

## Highlights
- **Faster workflow design:** Fast, Standard and Critical routes reduce unnecessary discovery checkpoints and let approved implementation continue without stopping at every increment.
- **Clearer communication:** Short user updates and human-readable commit and pull request titles, while keeping traceability details in descriptions.
- **Graphical progress board:** Optional `/vibe-board` command in Claude Code, with task list, reported progress, and activity details.
- **Board compatibility fix:** Native Mod validation now accepts the board module. Fixes the missing-command problem reported with Vibe 4.4.0 on newer Claude Code builds.
- **Safety retained:** Existing force-push protection and risk-aware independent review gates remain in place.

## Verification
- Automated Python/Node tests, safety-hook and installation smoke tests passed.
- `claude plugin validate --strict .` and `claude plugin test .` passed on pinned Claude Code 2.1.314 in GitHub Actions.
- **Not independently confirmed:** Real interactive terminal/Desktop visual smoke test, including Claude Code 2.1.316. Mod rendering in CI is not the same as a user-observed live panel.
- **Performance not measured:** The `scripts/compare-performance.mjs` benchmark is included, but no authenticated plain-Claude-versus-Vibe model runs have been completed. No numeric speedup is claimed.

## Update
In Claude Code, run `/plugin update vibe`, restart your Claude Code session, then run `/vibe-board`. The panel requires the plugin installation method; the standalone installer does not install Mods.

If the panel is missing, check `claude --version`, `claude plugin validate --strict .` against the downloaded v4.5 source, and review the plugin debug log. See [release verification details](docs/RELEASE-4.5.md).

**Excluded:** Rejected PR #6 (selective learning and targeted security extras) is not part of v4.5.
