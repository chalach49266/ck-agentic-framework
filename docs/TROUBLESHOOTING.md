# Troubleshooting

Each problem: **symptom → cause → fix**. Sources: the owner's notes on the source PC (2026-11-15), the setup
code (`setup/windows/setup_support.py`, `setup/windows/setup.cmd`), the platform READMEs, and the build logs in
`verification/` (local only).

## Setup

| Symptom | Cause | Fix |
|---|---|---|
| `Setup failed: Refusing existing symlink destination: ...` | An old install linked `~/PhD_local/ck-dispatch` (or ckstack, grokbot-mod, grok-bot-skills) to another folder. Setup never writes through a link. | Move the link aside yourself (`mv ~/PhD_local/ck-dispatch ~/PhD_local/ck-dispatch.old`), then run setup again. |
| `Setup failed: Existing file: ~/.local/bin/ck-run; move it aside first.` | A `ck-run` file that is not setup's link is there. | `mv ~/.local/bin/ck-run ~/.local/bin/ck-run.old`, run again. |
| `Setup failed: Existing unrelated link: ~/.local/bin/ck-run` | `ck-run` links to another install. | Check where: `readlink ~/.local/bin/ck-run`. Move it aside if it is old. |
| `WARNING: SKIP superpowers@...: project folder is missing: .../Device Fabrication` | The plugin installs "local" to Device Fabrication, and that folder is missing. Setup continues. | Restore the folder, then rerun setup with the same Windows user and PhD path to install the plugin. |
| `Setup failed: Marketplace <name> already uses another source: ...` | A marketplace with the same name points elsewhere. | Look: `claude plugin marketplace list`. If the old one is wrong: `claude plugin marketplace remove <name>`, run again. |
| `Keep the source ... separate from the install destination ...` | The repo was cloned inside `~/PhD_local/ck-dispatch` (or another install folder). | Clone to `~/ck-agentic-framework` instead. |
| `HOME and PHD_ROOT must be absolute WSL paths ...` | The PhD folder path is relative or has quotes, `$`, `\` or braces. | Pass a plain path like `/mnt/c/Users/{{WIN_USER}}/Documents/PhD` (spaces are fine inside quotes on the command line). |
| `Windows user must contain letters, digits, ...` | Odd characters in `--win-user`. | Use the folder name from `ls /mnt/c/Users`. |
| `Pass --phd-root ... when running without a terminal or with --yes` | Setup has no explicit PhD path and will not guess one. Nothing was changed. | Pass the full WSL path with `--phd-root`. `setup.cmd` asks for it and passes it to WSL. Its profile-based default is offered only if the folder exists. |
| Config points to the wrong PhD folder | A previous install used the wrong path. | Rerun `setup.cmd` in PowerShell and enter the correct full WSL path, or rerun `bash setup/windows/setup.sh --yes --win-user ... --phd-root ...` in WSL. |
| `setup.cmd` fails at the WSL step | The distro is not named `Ubuntu` (`setup.cmd` calls `wsl.exe -d Ubuntu`). | `wsl -l -v` in PowerShell. Install `Ubuntu` (`wsl --install -d Ubuntu`). |
| `gb`, `cdev` not found in PowerShell | The user PATH changed, but the window is old. | Open a new PowerShell window (or restart Herdr). Check `where.exe gb`. |
| Setup takes minutes at the end | It runs the offline tests (402 tests in about 263 s on the source build, `verification/offline-suite-final.log`). | Normal. Use `--no-tests` and run `python3 -I ~/PhD_local/ck-dispatch/tests/run_all.py` later. |
| Plugin installs fail with no network | Marketplaces come from GitHub. | `--no-plugins` (skills still install); add plugins when online. |
| Herdr look not applied | Herdr was not installed when `setup.cmd` ran, or Herdr was open. | Restart Herdr. Or: `herdr-app do layout.switch --name main-ck`. |
| Your old Herdr settings are gone | `setup.cmd` replaced `settings.json`, `keys.json` or a theme. | The old file is kept once as `<name>.bak` in `%USERPROFILE%\.config\herdr-app`. |
| Your old Claude settings changed | Setup merged `theme`, `modelSettings`, `agentPushNotifEnabled`. | Other keys stay. The original is in `~/.claude/settings.json.bak`. |

## Grok Bot and ck-run

| Symptom | Cause | Fix |
|---|---|---|
| Race agents sit still, waiting for approval | `ck-run race` uses `--mode read` by default. Read mode stalls agents on write approval. | Always pass `--mode auto` to a race. |
| Grok Bot is not woken when a run ends | The ask id or slug was a shell variable (`--ask $A`). The mod finds launches by reading the command text. | Type ask ids and slugs literally. Check `/grokbot status`. Read the `.out` file yourself once. |
| Grok Bot mode is off after `/clear` or `/resume` | These end the mode. | Type `/grokbot`. Then `ck-run board` and `ck-run reattach`. |
| A typed `ck-run run ...` is refused in Grok Bot mode | The mod gate allows only `ck-run launch` for runs (so the run survives and is watched). | Use `ck-run launch <slug> run ...`. Never work around the gate. |
| `exit 2`, write scope refused | A write scope inside `~/PhD_local` must already exist and be its own git repo. | `mkdir` the folder and `git init` it first (or pick an existing repo). |
| `exit 2`, "ANDON raised for ..." | An andon is up for that project. | Only your words clear it: `ck-run andon clear --project <name> --note "<your words>"`. |
| `exit 2`, "slug used; pick a new one" | Each launch slug is used once. | New slug, e.g. `<ask>-fix1`. |
| `exit 2`, `--ask` missing or unknown ask | Every run needs an open ask. | `ck-run ask open ...` first; the error shows the line. |
| `exit 3`, "stopped by the watchdog: no activity for N s" | The run was silent for twice its stall time. | Look at the pane. Often an approval prompt or a login. Fix, then a new run. |
| `exit 4` or `exit 5` | The rule check flagged the run (raw folders, credentials, cloud sims). | Stop the chain: `ck-run andon raise --project <name> --reason "<line>"`. You decide. A mention of a test fixture named like a credential file can also flag (seen in the build run): read the details first. |
| `exit 6` busy | Another live run claims the same path. | Wait (`ck-run active`), or use other paths. |
| `exit 7` over budget | The ask's budget is used. | Say "go" with your words (`--over "<your words>"`), or close the ask. |
| Codex shows "folder settings can run code" | One-time Codex trust warning in a new folder. | Not a blocker. Accept once. |
| Codex run says model `UNKNOWN` | Codex does not print its model name. | Fine. `ck-run models` shows what was asked for. |
| Claude runs end `partial` in Device Fabrication | The workspace has a wiki-first rule; a smoke test does not read the wiki. | Expected for a smoke test. |
| A run left without a result after a Claude restart | Its watcher died. | `ck-run reattach` (safe to repeat). |
| `agy` / gemini runs fail | agy is not installed (it was not on the source PC either). | Install and sign in to agy, or use another lane model. |
| Read-mode agents ask to write `result.md` | Read mode needs approval for the two outbox files. | Approve those two writes only. ck-run can also recover the final reply. |

## Live panes (Windows PC)

| Symptom | Cause | Fix |
|---|---|---|
| Runs open in tmux / Windows Terminal, not in Herdr | The caller is not in Herdr, or it is an old Claude session started without `HC_TERMINAL_ID`. | Start Grok Bot from Herdr (`gb` in a Herdr tab, or `gbh`). For an old session: `export CK_LIVE_HOST=herdr CK_HERDR_PARENT=<hc address>`. |
| Runs open in Herdr but you wanted tmux | `CK_LIVE_HOST` or `HC_TERMINAL_ID` is set. | Start that session with `CK_LIVE_HOST=wsl claude`. |
| Herdr panes of one ask and tmux windows at once | Should not happen: the router picks one side. | Check `config/workspaces.json` `live.osascript` = `~/PhD_local/ck-dispatch/platform/auto/osascript`. |
| All terminals closed at once | Someone ran `hc server stop` or `hc server restart`. | Never run them. Restart Herdr; then `ck-run reattach`. |
| Agents list colors look wrong after a Herdr update | `mods/agents-ck` is a clone of Herdr's `agents` mod and keeps the old code. | Compare with `mods/agents` in `%USERPROFILE%\.config\herdr-app`. Back to Herdr's look: `herdr-app do layout.switch --name main`. |
| A finished pane does not close | It was used, or it ended partial, or it had a problem. | Only clean `ok` runs close themselves (after 300 s). Close it by hand. |
| No Windows Terminal (headless) | The tmux fallback opens a Windows Terminal tab. | `export CK_NO_WT=1`. Watch with `tmux -L ckrun ls` and `tmux -L ckrun attach -t ck<id>`. |
| Edits to `~/PhD_local/ck-dispatch` are refused | Only on an install where those folders are links to `/mnt/c/...` (the old source PC layout): ck-run checks the real path is inside `~/PhD_local`. | A copy install (this repo's setup) does not have this. |
| Herdr help | | `hc.exe --skill`, and `AGENTS.md` in the Herdr config folder. |

## Mac

UNVERIFIED until the Mac part is merged. Known from the old Mac line (`archive/ck-dispatch-2026-11-15/`):

| Symptom | Cause | Fix |
|---|---|---|
| The Mac sleeps during a long run | `caffeinate -i` stops idle sleep only, not lid-close sleep on battery. | Keep the lid open or on power. |
| Runs open in the wrong host | The old Mac line used `CK_RUN_HOST=iterm` or `CK_RUN_HOST=herdr:<terminal id>` to force a host. | See `setup/mac/README.md` for the current Mac rule. |
| Runs try tmux + Windows Terminal on the Mac | The installed config points `live.osascript` to `platform/auto/osascript`, a PC router. It reads the caller's env from `/proc`, which macOS does not have, so it falls back to the WSL (tmux) script. | The Mac config must point `live.osascript` to the Mac host (`/usr/bin/osascript` for iTerm2, or the Mac Herdr adapter). |
