# Changes from the Mac build

This build uses the current live Mac host code, not the older archive. The live files and inventories were read
only. No live installation, login, app server, remote machine record or PhD project was changed.

## Mac-owned files

- `core/ck-dispatch/platform/mac/osascript`: the shared AppleScript protocol routed to native iTerm or Mac Herdr.
- `core/ck-dispatch/platform/mac/herdr.py`: live Mac launch, layout, labels and safe delayed-close helpers. The
  standalone import path and Cursor icon shell path are adapted to this folder. Attribution is made portable.
- `core/ck-dispatch/platform/mac/tests/`: a copied fake Herdr fixture and offline protocol tests. No real app or
  model request. The fake adds terminal lookup for the adapter's persistent window check.
- `setup/mac/setup.sh` and `setup_support.py`: Mac copy installer. Its copy, JSON rendering, marketplace and
  plugin installation, recursive settings merge, safe destination checks and backups follow the read-only
  Windows `setup_support.py` implementation. Windows installer files are unchanged.
- `setup/mac/ck_shortcuts.zsh`: Mac project shortcuts plus Grok Bot activation, following the shared shortcut
  intent while keeping existing PATH order. The installer appends a single source line to zsh startup.
- `setup/mac/claude.json`: portable live Mac preferences over the common settings. No grants, machine context,
  transcript, token or credential copy. iTerm status hooks are created only if the destination app has the helper.
- `setup/mac/herdr/`: live Mac `ck-main`, `ck-agents`, `ck-pane`, `ck-tabs`, keyboard shortcuts, settings and themes.
  Runtime view documents, terminal state, machine lists and app binaries are excluded.
- Mac setup and host READMEs: detailed steps, checks, backups and limits.

## Every change outside the Mac folders

| File | Change | Why / Windows effect |
|---|---|---|
| `core/ck-dispatch/ckdispatch/live.py` | On Darwin only, reserve `live-host.json` and `herdr.log` as runner control files; pass the new pane's own `HC_TERMINAL_ID` through the live agent wrapper; forward only Mac host-selection variables when invoking the exact Mac adapter path | Mac host choice otherwise disappears in the clean transport environment. Only a pane identity enters the agent environment. Windows branches and adapters are unchanged. |
| `setup/common/placeholders.json` | Document Mac user/home/coursework inputs, the historical WSL_HOME compatibility token, and private network placeholders | Manifest documentation only; Windows renderer remains unchanged. |
| `setup/windows/herdr/mods/*/gpui-kit.d.ts`, `setup/mac/herdr/mods/*/gpui-kit.d.ts`, `.gitignore` | Removed the 6 auto-generated type files (~22.7k lines each); `.gitignore` now ignores `gpui-kit.d.ts` | The owner asked to drop them (2026-11-16). Herdr writes this file on every run and its header says to keep it out of git. Editor type hints only; the mods import `gpui-kit` from the Herdr runtime, so Windows and Mac behaviour do not change. |
| `README.md` | Replace Mac draft labels and quick start | Point a new Mac at the implemented installer. |
| `AGENT_SETUP.md` | Replace section M | Give the Mac agent a concrete install and check sequence. Windows steps are unchanged. |
| `docs/PHONE.md` | Replace Mac-side method and remove stale syntax caveat | Describe destination Remote Login checks, Mac-to-PC machine syntax, and actual Tailscale-only access limits. No network action was run. |
| `docs/TROUBLESHOOTING.md` | Replace the Mac table | Cover the implemented adapter, installer, permissions, backups and phone checks. |
| `PROGRESS.md` | Record scoped build completion and remaining checks | Resume and handoff record. |
| `docs/CHANGES_FROM_MAC.md` | This change register | Keep the small shared change reviewable. |

The repository's `config/workspaces.json` remains the Windows template. The **installed Mac copy** is rendered
with the Mac adapter path, native caffeinate, Homebrew bin paths and a separate coursework root. Shared ckstack,
skill text, Windows setup, `platform/auto`, `platform/herdr`, `platform/wsl`, and `archive` are unchanged.

## Evidence limits

Proof level: `fake_or_tests` for the executed installer and host checks. Local logs and check results belong in
`verification/build/RESULTS.md` (gitignored). A fresh Mac install, online marketplace/plugin installation, macOS
Automation grants, live pane visuals, actual close timing, a live agent race and phone access remain UNVERIFIED.
An offline CLI smoke does not prove account login or a real agent completion.

## Agent talk port

- `core/ck-dispatch/ckdispatch/herdr.py`, `talk.py` and the runner, CLI, launch, prompts, views and ledger
  wire up the completion doorbell, `question.md` relay and **NEEDS YOU**, capped `ck-run say`, a live review
  steer and `ck-run race stop --ask <ask> --keep <slug>`. The audit records message attempts before calling hc.
  A matching Grok Bot pending output owns the completion wake in auto mode. The runner sends to local addresses.
- `core/ck-dispatch/platform/mac/` launches Herdr agents with `--no-notify`, records the pane identity and derives
  the pane name from the job title plus a run-specific suffix. Its native iTerm route still uses its own transport.
- `core/ck-dispatch/platform/herdr/osascript` retains `--no-notify` and adds the run label and saved local pane
  metadata at launch. The shared code uses the existing PC hc and close calls. The PC adapter keeps its existing
  job-title naming scheme. PC to do: verify this hook with the Windows/WSL host. The harness here uses fake hc.
- `core/ck-dispatch/config/models.json` sets `sol`, `sol-fast` and `sol-max` to `gpt-6.2-sol`, and `astra`
  to `gpt-6.2-astra`. Both installers use this file. The direct Codex auto fallback and pinned tests agree with the
  shared defaults. The existing model evidence in `_verified` records earlier checks.
- `core/ckstack/` and `core/grokbot-mod/` include the worker, CK, and race instructions. The mod gates `say`
  as a write command. The offline framework, Mac transport, setup, and rendered mod suites cover the change.
- `review --live` opts in to steering, with the existing ask review, parallel and fix limits. Launch's automatic
  `--interactive` opens a normal review pane. A worker question stays visible until a confirmed answer or ask closure.
- The direct `ck-herdr` launch gate port is N/A because `ck-herdr` is archived in this framework.
  See `archive/ck-herdr/`. Live delivery and Windows host behavior are UNVERIFIED.

## Bot messages and silent progress

- `core/ck-dispatch/ckdispatch/messages.py` and the shared CLI, guards, ledger and Herdr transport add
  `ck-run msg`, `msg reply` and `msg log --in`. Each send checks the recipient's live Grok Bot label and
  records the attempt before calling Herdr. Replies resolve the hostname in Herdr's wrapper through the configured peer list.
- Shared config, runner, wait loop, talk and board code publish complete `progress.md` lines on the verified worker
  pane and show the last one on the board. `herdr.progress` defaults to `label` and can be set to `off`.
  Progress sends no terminal input. The existing Mac adapter supplies the pane identity and hc calls.
- The PC adapter looks for `hc.exe` on PATH and supports the default Herdr install path
  `C:\Users\<user>\AppData\Local\Programs\herdr-core\hc.exe`. Its Grok Bot shortcut passes the local
  pane identity into WSL. PC to do: verify the installed shortcut, PATH/default resolution and delivery on a live PC.
- The Grok Bot mod labels its own pane when active, gates `msg` as a write, and logs bot envelopes outside the
  human prompt log. The ckstack worker and router guides, Grok Bot guide and `docs/HOW_TO_USE.md` describe the workflow.
