---
name: Cursor agent prompt
description: Use when the user asks you to prompt, ask, or run something in the Cursor CLI agent (agent / cursor-agent) on their Mac; the run always goes through ck-run.
---
# Run a task in the Cursor CLI agent through ck-run

Runner: `~/PhD_local/ck-dispatch/bin/ck-run` (full usage: `~/PhD_local/ck-dispatch/README.md` or `ck-run run --help`).
Call it from the Grok Bot shell and never call `agent` directly.
**Claude Code stand-in (the owner 2026-11-04):** Claude Code may call ck-run from its own session ONLY when the owner
asked it to stand in for Grok Bot (Grok usage out) by typing `/grokbot`. The grokbot mod enforces this: with the mode off
it refuses every ck-run command that starts or changes work (`run`, `review`, `accept`, `launch`, `race`, `panel`, `loop`,
`reattach`, `ask` and `andon` changes) and `agent_runs/*.sh` launches. Stand-in rules: `~/PhD_local/grokbot-mod/GROKBOT.md`.
Asks, budgets, lanes, review reasons and finish cards: see the `ck-delegate` skill (v4).

0. **Installed and logged in?** `PATH="$HOME/.local/bin:$HOME/.cursor/bin:/opt/homebrew/bin:$PATH" agent status`. If it's missing,
   tell the user; install nothing without their OK. If it isn't logged in, start `NO_OPEN_BROWSER=1 agent login` in the background
   and give the user the printed link.
1. **Machine.** Use ListMachines (cursor namespace) if you don't know the user's computer id; run every command with that machineId.
2. **Workspace.** `PHD={{PHD_ROOT}}`
   - Device Fabrication: `cd "$PHD/Device Fabrication"` and `--workspace devfab`.
   - NV Compact Magnetometer (AQS too): `cd "$PHD/NV Compact Magnetometer"` and `--workspace nv`.
   - Framework/setup work (framework docs, ck-dispatch, skills, agent setup): `cd "$PHD"`. ck-run knows only devfab|nv,
     so pass the one whose rules apply (devfab if both); edits go to a `~/PhD_local/<repo>` write scope.
   - ck-run sets `--workspace` and the cwd itself. Tell the user the folder and the mode before you start.
3. **Task file.** Write the task to `~/PhD_local/agent_runs/<slug>_prompt.md` (`ck-run launch` needs it there): the owner's
   words, then "Do only this:". Name file paths instead of pasting content (cap 200 KB).
4. **Mode.**
   - Auto (default, approved by the owner 2026-11-02 22:34 CST): add no mode flag. ck-run injects `--trust --sandbox enabled --force`
     (allow-all, the owner 2026-11-03). **No Claude review after the run** since 2026-11-05 (the owner: "no need review, since
     those one are for simple stupid task anyways"; config `post_review.enabled` is false); ck-run's rule check still runs.
     The agent works
     on its own: it marks unknowns instead of stopping, lists open questions under "Questions for the owner" at the end of its
     summary, and keeps `PROGRESS.md` in its work folder. Writes stay inside `--write-scope` if given, else the workspace minus raw
     folders and rule files (checked after the run). It runs in an iTerm2 window (`ck-run launch` adds `--interactive`).
     After the run, read the "Questions for the owner" list and relay it to the user.
   - Read: add `--mode read` for look-only tasks. Cursor runs with `--mode plan --sandbox enabled --trust`. Print mode without plan mode can
     write and run shell, so plan mode is the guard.
   - Edit (scoped, legacy): only if the user asked for a change in this conversation. Add `--mode edit --approved "<user's words> (YYYY-MM-DD HH:MM CST)"
     --write-scope <folder>`. Allowed scope: a workspace subfolder that is not raw or a rule file (NV: only inside `NV Project/`), or a
     `~/PhD_local/<repo>` git repo. Cursor then starts in the scope with its sandbox on (no plan mode).
   - Never pass `--force` (= `--yolo`, "Run Everything"), skip-permissions, full-access, `--auto-review` yourself, `--approve-mcps`, or any
     permission flag (`--sandbox`, `--add-dir`, ...). ck-run sets the auto flags itself and refuses them from you, along with every bypass flag (exit 2). Don't work around a refusal.
5. **Launch** (v4: detached, returns at once). Open the ask first (`ck-delegate`), then:
   ```
   cd "<folder>" && ~/PhD_local/ck-dispatch/bin/ck-run launch <slug> run --ask <A> --model grok \
     --workspace <devfab|nv> --title "<short title>"
   ```
   launch adds `--prompt-file ~/PhD_local/agent_runs/<slug>_prompt.md` and `--interactive`, writes `<slug>.sh` and prints
   `slug:`, `sh:`, `out:`, `pid:`. The run's output goes to `~/PhD_local/agent_runs/<slug>.out`, which ends with
   `ck-run exit=N`. Grok Bot: start one background watcher (block_until_ms 0) and wait for its notice; don't poll:
   `until grep -q '^ck-run exit=' ~/PhD_local/agent_runs/<slug>.out; do sleep 20; done; cat ~/PhD_local/agent_runs/<slug>.out`
   Runs go in parallel (no workspace lock). Edit runs claim their write folders automatically (so do auto runs given
   `--write-scope`); pass `--claim <path>` (repeatable) for other files you will edit.
   **Model:** `--model grok` (Grok 4.7 at high effort, slug `grok-4.7-high`) or `composer` (composer-2.5); an alias implies cursor, so `--agent` may be left
   out. With `--agent cursor` and no `--model`, the ask size picks it: `composer` (S), `grok` (M, L). ck-run adds
   `--model <slug>` itself. `--parent <run_id>` for a follow-up. A first run can take about 200 s (default timeout from
   the ask size: S 10 min, M 30 min, L 2 h).
   Lanes (`ck-run route --lane <lane>`): Grok 4.7 is the worker for scouting (literature, datasheets, the web) and a
   third view next to Sol and Opus; Composer takes mechanical sweeps (renames, links, tables).
6. **Read only the summary.** `~/PhD_local/agent_runs/<slug>.out` holds the `summary.md` path (line 1), the summary (max 10 lines)
   and the exit line. Don't open stdout.log or result.md unless the user asks. `ck-run show <run_id>` re-prints a summary.
   Exit: 0 ok · 1 partial · 2 refused (nothing ran) · 3 failed/timeout/stalled · 4 flagged (needs a human look) · 5 violation
   · 6 busy (file/folder claim conflict) · 7 over budget (nothing ran).
7. **Session id and resume.** `R` = the folder of the summary path (`~/PhD_local/agent_runs/<run_id>`). Read just these two fields:
   ```
   python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["session_id"])' "$R/result.json"; grep -m1 '^# cwd:' "$R/cmd.txt"
   ```
   When the user asks (v4 cards carry no run ids), give the run id, the session (chat) id and `cd "<cwd>" && agent --resume <session_id> --mode plan`.
   A resume runs outside ck-run's guards; your own follow-ups use `--parent <run_id>` (through `ck-run launch`).
8. **Follow up at once.** When the notice arrives, close the ask with its finish card (`ck-run ask close`), or take the next
   step, as in `ck-delegate`. A review only with a reason: `ck-run review <run_id> --by <other agent> --trigger
   leaves-lab|hardware-or-raw|agent-unsure|you-asked` (launch it like a run). Session id and resume command on request.
9. **On failure** (not logged in, rate limit, refused, busy, over budget): give the exact error line and the fix. Never retry with looser
   permissions. Busy (6) = a file/folder claim conflict with a live run (stderr names it): wait for that run's
   notice, or use other paths. Over budget (7) = the ask's budget is used: ask the owner; add `--over "<the owner's words>"`
   only with their real words. If ck-run itself is broken, a raw read-only run
   (`cd "<folder>" && agent -p --mode plan --sandbox enabled --trust --output-format json "$(cat ~/PhD_local/agent_runs/<slug>_prompt.md)"`) needs the user's OK.

Cursor gives no tool log, so ck-run checks its rules from the output text and the disk (stray writes show as flagged or violation).
Since 2026-11-05 no Claude review follows a cursor run; ask for a review with a reason (`--trigger`) when one is needed.
