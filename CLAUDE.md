# KRPTCH

Korean fan-translation patches for retro games.

## Tooling (auto-available in every session)

- `create-kr-patch` skill (`.claude/skills/create-kr-patch`): analysis and decision guidance for ROM/disc reverse engineering, Hangul fonts/encoding, text reinsertion, hooks, and emulator verification. Use it for any 한글패치 task.
- `hanpatch` skill (`.claude/skills/hanpatch`) and CLI (`hanpatch`, installed by the SessionStart hook): gate-enforced translation pipeline (extract, fonts, translate, qa, gates, build, verify). Use it for the translate/QA/build stages.

Use `create-kr-patch` for investigation and strategy, `hanpatch` for the gated translation pipeline. ROMs and keys are supplied by the user and must not be committed.

## Emulator control (emucap)

- `emucap-control` and `emucap-track` MCP servers (`.mcp.json`) come from mcpads/emucap. `.claude/emucap/run.sh` installs the checksum-verified prebuilt core to `~/.emucap-core/` on session start; bump `VERSION` there to upgrade.
- Start every emulator task with the Control MCP's `bootstrap()`. Pass `get_rom_info.rom_sha1` unchanged to Tracking `run_start` and log interventions with `log_intervention`.
- Emulator hosts/adapters (Mesen2, Mednafen, etc.) are not preinstalled; prepare the one needed via `adapters/<adapter>/README.md` in `~/.emucap-core/<version>/`. Cloud sessions have no display, so only headless-capable adapters will work there.
