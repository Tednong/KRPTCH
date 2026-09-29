# KRPTCH

Korean fan-translation patches for retro games.

## Tooling (auto-available in every session)

- `create-kr-patch` skill (`.claude/skills/create-kr-patch`): analysis and decision guidance for ROM/disc reverse engineering, Hangul fonts/encoding, text reinsertion, hooks, and emulator verification. Use it for any 한글패치 task.
- `hanpatch` skill (`.claude/skills/hanpatch`) and CLI (`hanpatch`, installed by the SessionStart hook): gate-enforced translation pipeline (extract, fonts, translate, qa, gates, build, verify). Use it for the translate/QA/build stages.

Use `create-kr-patch` for investigation and strategy, `hanpatch` for the gated translation pipeline. ROMs and keys are supplied by the user and must not be committed.
