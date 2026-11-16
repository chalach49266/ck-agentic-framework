# Set up a Mac

This installs copies under your home folder. It does not change your PhD projects. Keep the checkout separate
from the installed folders. Read [AGENT_SETUP.md](../../AGENT_SETUP.md#m-mac-steps) for the agent workflow.

The source is the live Mac runner and its portable preferences, read for this build. The older archive is not
installed. Offline tests and temporary-home installs are the proof here. A real new Mac, agent logins, live
windows, plugin downloads and phone access remain **UNVERIFIED** until you check them on your machine.

## Before you start

Install these applications yourself. Use their normal installers. Setup does not download them or sign you in.
The observed source Mac used native Claude and Cursor installers, global npm Codex under Homebrew, a standalone
agy executable, iTerm in the user Applications folder, and the App Store Tailscale app. The exact original
bootstrap commands are UNKNOWN. No agent executables are bundled in this repo.

| Item | Check in your terminal | Purpose |
|---|---|---|
| Git | `git --version` | Source checkout |
| Python | `python3 --version` | Python must support the union type syntax used by core; use Python 3.10 or later (core/ck-dispatch/ckdispatch/config.py) |
| Claude Code | `command -v claude` | Orchestrator; open `claude` and use `/login` |
| Codex | `command -v codex` | Sign in with `codex login` |
| Cursor agent | `command -v agent` | Sign in with `agent login` |
| agy (optional) | `command -v agy` | Gemini lane uses agy, not the separate gemini executable |
| iTerm | Open iTerm from Applications | Default live host and fallback |
| Herdr (optional host) | `command -v hc`; `command -v herdr-app` | Open Herdr once so its core and stock mods exist |
| GitHub CLI | `gh auth status` | Needed to get the private repo; logins are not copied |
| Tailscale (phone only) | Open the Tailscale app | See [PHONE.md](../../docs/PHONE.md) |

Keep agent binaries on `~/.local/bin`, `/opt/homebrew/bin` or `/usr/local/bin`, or edit the installed config's
`bin_dirs` after setup. The runner intentionally uses a fixed PATH. Do not source old shell files to discover
settings. They may contain private values.

### Install Herdr itself

Do this before installing the framework if you want Herdr as a host. The framework copies preferences; it does
not install the Herdr application or core. The [vendor download page](https://herdr.dev/download/) offers both:

- **Terminal installer:** run the vendor's command yourself in Terminal:

  ```bash
  curl -fsSL https://releases.herdr.dev/app/install.sh | sh
  ```

- **Disk image:** download the Mac `.dmg` from that same page, open it, and drag Herdr to Applications.

Open Herdr once. Ensure `~/.local/bin` is on your PATH, then check `command -v hc` and `command -v herdr-app`.
Do not run either installer as part of an offline framework test.

**Source Mac method — guess from evidence:** the app is at `~/Applications/Herdr.app`, core is under
`~/.local/share/herdr-core`, and `~/.local/bin/hc` links into that core. The app has no `com.apple.quarantine`
flag. These observations suggest the terminal install script was used rather than the disk image; they do not
prove the installation history. The disk-image option is also supported by the vendor. A fresh installation
remains UNVERIFIED here.

## Choose your paths

`{{MAC_USER}}` means your short Mac account name. `id -un` shows it. `{{PHD_ROOT}}` means the full parent folder
that contains `Device Fabrication` and `NV Compact Magnetometer`. It may be in OneDrive. Use quotes around paths
with spaces. Replace placeholder text before running these examples.

Coursework is separate on the source Mac. The installer offers `--coursework-root` for that workspace. Its default
is `~/Downloads/WashU HW`. Confirm the installed `washu` root and writable course pairs before a coursework run.
The template's generic course names are examples. Setup does not guess your courses or modify their rule files.

## Dry run first

From the repository root:

```bash
bash setup/mac/setup.sh --dry-run --mac-user '{{MAC_USER}}' --phd-root '{{PHD_ROOT}}'
```

The dry run lists every file copy, backup rule, link, settings merge, plugin command and check. It creates no
folders, starts no external commands and changes no files. A bare `--dry-run` without a terminal stops if the
PhD path is missing. This is intentional. No path is silently selected. In a terminal, setup asks for the user
and path. An existing candidate path may be offered for confirmation. `--yes` always needs `--phd-root`.

## Install

After reading the plan:

```bash
bash setup/mac/setup.sh --yes --mac-user '{{MAC_USER}}' --phd-root '{{PHD_ROOT}}'
```

To use another coursework folder, add `--coursework-root '/full/path/to/coursework'` to both commands.

For an offline install, add `--no-plugins`. Bundled skills and preferences still copy, but Claude marketplaces and
plugin installation are skipped. To run the suite separately, add `--no-tests`. The short CLI smoke still runs.
Do not use a real install just to test this script. Use the temporary-home method below.

The installer follows this order:

- Copy `core/ck-dispatch`, `core/ckstack`, `core/grokbot-mod`, and `core/skills` into `~/PhD_local`. Skills become
  `grok-bot-skills`. Fill local path placeholders. Copy mode keeps the source checkout separate.
- Render the installed workspace config. Mac uses `platform/mac/osascript`, native caffeinate, and Homebrew bins.
  Windows template and adapters stay as shipped.
- Link `~/.local/bin/ck-run`. Refuse an unrelated existing file or link. Do not write through symlink destinations.
- Write `~/.ck_shortcuts.zsh`. Add its source line once at the end of `~/.zshrc`. Existing shell and Conda setup
  stay in place. Open a new terminal. `cdev` and `cnv` go to the project and open Claude with Grok Bot activation.
  `gb` and `grokbot` open it in `~/PhD_local`. `phd` only changes folder.
- Copy portable Mac Herdr files into `~/.config/herdr-app`: `layouts/ck-main.json`, `mods/ck-agents`, `mods/ck-pane`,
  `mods/ck-tabs`, themes, `settings.json`, and keyboard shortcuts in `keys.json`. These are not SSH keys. Use the
  original task's **copy only if absent** option for every Herdr file. An existing file is left untouched, with
  `kept yours: <path>` printed. To adopt a newer bundled Herdr file, compare it and move your copy aside yourself.
- Before replacing any differing installed core file, `~/.ck_shortcuts.zsh`, startup file or merged Claude settings,
  save its current contents as `<file>.bak-YYYYMMDD-HHMMSS`. A same-second collision adds `-1`, `-2`, and so on;
  no existing backup is replaced. Identical files create no backups. Old `.bak` files are left alone. Plugin
  stores already present are kept so a repeat install cannot reset pending Grok Bot jobs.
- Create a native `/bin/bash` link named `agent` for the Cursor pane icon. No machine-specific executable is copied.
- Unless `--no-plugins` is set, register marketplaces and install the plugin list from `setup/common/claude`.
  A conflicting marketplace source stops setup. Missing Device Fabrication skips its local plugin with a warning.
- Merge shared Claude settings, then the Mac portable preference overlay. Keep other settings and back up each change.
  Mac uses its source model effort and UI preferences. No permission history, login or generated host context copies.
  If the installed iTerm app has `cc-status`, merge its hooks without replacing unrelated hooks.
- Run `setup/common/smoke.sh`, then the core suite and Mac host tests unless `--no-tests` is set.

No Herdr machine list, active window document, terminal state, private key, Claude login or run ledger is installed.
The installer does not switch a running Herdr layout. After setup, select `ck-main` in Herdr's layout picker, or use:

```bash
herdr-app do layout.switch --name ck-main
```

Close and reopen the app if its mods do not refresh. To return to the stock look, select `main`. Never stop or
restart herdr-core from an agent terminal.

## Check the install

Open a new terminal. Run:

```bash
command -v ck-run
ck-run models
ck-run --help
bash setup/common/smoke.sh
python3 -I ~/PhD_local/ck-dispatch/tests/run_all.py
python3 -I -m unittest discover -s ~/PhD_local/ck-dispatch/platform/mac/tests
```

Open the installed `~/PhD_local/ck-dispatch/config/workspaces.json`. Check every workspace root against the folders
you restored. A successful offline smoke proves the CLI starts; it does not prove model login or window launch.
For a later live check, run `bash setup/common/smoke.sh --live` from Herdr or iTerm. This starts real agents in auto
mode. It was not run for this build.

## Choose the host

Read [the Mac host README](../../core/ck-dispatch/platform/mac/README.md). Normally, a caller in Herdr stays beside
its own terminal. A caller outside Herdr uses native iTerm. `CK_RUN_HOST=iterm` forces iTerm. `CK_RUN_HOST=herdr`
selects Herdr. `CK_RUN_HOST=herdr:<terminal address>` chooses a main terminal explicitly. These are Mac settings;
Windows keeps its own router variables. Existing session reads always use their saved identity.

## Temporary-home check

This does not install into your real home. It skips plugin downloads and runs the suite separately:

```bash
test_home=$(mktemp -d)
mkdir -p "$test_home/PhD files"
HOME="$test_home" bash setup/mac/setup.sh --dry-run --mac-user test-user --phd-root "$test_home/PhD files" --no-plugins --no-tests
HOME="$test_home" bash setup/mac/setup.sh --yes --mac-user test-user --phd-root "$test_home/PhD files" --no-plugins --no-tests
HOME="$test_home" bash setup/mac/setup.sh --yes --mac-user test-user --phd-root "$test_home/PhD files" --no-plugins --no-tests
HOME="$test_home" "$test_home/.local/bin/ck-run" models
HOME="$test_home" "$test_home/.local/bin/ck-run" --help
```

The same command is safe to repeat. Installed core copies are updated with timestamped backups; existing Herdr
files are kept. Run `python3 -I -m unittest discover -s setup/mac/tests -v` for the install/edit/reinstall regression.
Check the files before removing the temporary folder. Review-fix evidence is local in
`verification/fix1/RESULTS.md` and is not committed.
