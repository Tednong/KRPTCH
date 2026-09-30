---
name: chatgpt-pro-oracle
description: Send one explicitly requested mission (design advice, research, review) to a signed-in web ChatGPT Latest/6 Pro session through the third-party codex-web-gpt-automation (Oracle + DevSpace) and read back the saved answer. Local Windows/macOS Claude Code only. Use only when the user asks for a ChatGPT Pro second opinion.
disable-model-invocation: true
---

# chatgpt-pro-oracle — ChatGPT Pro second opinion from Claude Code

Claude Code adapter for [ventianima-lab/codex-web-gpt-automation](https://github.com/ventianima-lab/codex-web-gpt-automation)
(community project, not an OpenAI product). That project is built for Codex;
its runner is a plain Python CLI, so Claude Code calls it directly through Bash
and never uses its Codex skills.

## Where this works

- Local **Windows 11 / macOS 12+** only. It drives a signed-in Chrome profile
  and needs a stable public HTTPS endpoint. It does **not** work in headless
  cloud sessions (no display, no Chrome, no login).
- One-time setup is the user's job, following that repo's `docs/FIRST_INSTALL.en.md`:
  `python install.py` → `python doctor.py` → `python onboard.py start --root <this repo>`.
  ChatGPT login, registering the ChatGPT app as `codex`, and DevSpace Owner
  approval are manual. Never ask for or record passwords, tokens or cookies.
- The KRPTCH repo root must be one of the approved DevSpace roots.

## Data rules (KRPTCH)

The mission and every file ChatGPT reads leave the machine. Do not put ROM or
disc data, keys, or copyrighted game text dumps in the mission or in files under
the approved root that it may read. Describe formats, offsets, and small
excerpts instead.

## Paths

The installer deploys to `$CODEX_HOME` (default `~/.codex`; `%USERPROFILE%\.codex`
on Windows). Runner: `<home>/bin/chatgpt_oracle_run.py`.

```bash
RUN="${CODEX_HOME:-$HOME/.codex}/bin/chatgpt_oracle_run.py"   # macOS
```
```powershell
$RUN = "$env:USERPROFILE\.codex\bin\chatgpt_oracle_run.py"     # Windows
```

If `$RUN` is missing, stop and tell the user to finish the install; do not
attempt to install it yourself.

## Procedure

1. **Write the mission** as a UTF-8 file inside the repo, e.g.
   `.codex-tmp/mission-<topic>.md` (gitignore it; do not commit). State the
   objective, the files to read (repo-relative), constraints, and the answer
   format wanted. Planning/research/review are just prompt content — there are
   no separate modes.
2. **Dry run** (starts no browser, submits nothing) and show the user the result:
   ```bash
   python3 "$RUN" execute --project-root "$PWD" --mission-path "$PWD/.codex-tmp/mission-<topic>.md" --model latest --effort pro --dry-run
   ```
3. **Live run only after the user OKs it**: same command without `--dry-run`.
   `--effort extra-high` is also supported. Never silently change model/effort.
4. **Read the saved output** the runner reports (its run dir holds `output.md`)
   and summarize it for the user. Treat the answer as an opinion to verify
   (emulator, hanpatch gates), not as ground truth. Captured output proves the
   answer was saved, not that anything in it is correct.

## Failure and recovery

On timeout or connection loss keep the same run and tab; never resubmit:
```bash
python3 "$RUN" reconnect --run-dir <exact run dir> --dry-run   # then without --dry-run
```
If the tab is gone, report that and ask the user how to proceed. Do not touch
other runs, change approved roots, auth, or account settings, or use the
`settle-*`, `recover`, `adjudicate` subcommands (historical exact-recovery only).
