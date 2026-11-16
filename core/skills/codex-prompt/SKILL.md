---
name: Codex prompt
description: Use when the user asks you to prompt, ask, or run something in ChatGPT Codex (the codex CLI) on their Mac; the run always goes through ck-run.
---
# Run a task in Codex through ck-run

Runner: `~/PhD_local/ck-dispatch/bin/ck-run` (full usage: `~/PhD_local/ck-dispatch/README.md` or `ck-run run --help`).
Call it from the Grok Bot shell: a Claude Code hook (merge-gate) blocks any command containing `codex exec`. Never call `codex`
directly.
**Claude Code stand-in (the owner 2026-11-04):** Claude Code may call ck-run from its own session ONLY when the owner
asked it to stand in for Grok Bot (Grok usage out) by typing `/grokbot`. The grokbot mod enforces this: with the mode off
it refuses every ck-run command that starts or changes work (`run`, `review`, `accept`, `launch`, `race`, `panel`, `loop`,
`reattach`, `ask` and `andon` changes) and `agent_runs/*.sh` launches. Stand-in rules: `~/PhD_local/grokbot-mod/GROKBOT.md`.
Asks, budgets, lanes, review reasons and finish cards: see the `ck-delegate` skill (v4).

1. **Machine.** Use ListMachines (cursor namespace) if you don't know the user's computer id; run every command with that machineId.
2. **Workspace.** `PHD={{PHD_ROOT}}`
   - Device Fabrication: `cd "$PHD/Device Fabrication"` and `--workspace devfab`.
   - NV Compact Magnetometer (AQS too): `cd "$PHD/NV Compact Magnetometer"` and `--workspace nv`.
   - Framework/setup work (framework docs, ck-dispatch, skills, agent setup): `cd "$PHD"`. ck-run knows only devfab|nv,
     so pass the one whose rules apply (devfab if both); edits go to a `~/PhD_local/<repo>` write scope.
   - ck-run sets the agent's cwd itself (`-C <workspace>`; the scope in edit mode). Tell the user the folder and mode first.
3. **Task file.** Write the task to `~/PhD_local/agent_runs/<slug>_prompt.md` (`ck-run launch` needs it there): the owner's
   words, then "Do only this:". Name file paths instead of pasting content (cap 200 KB).
4. **Mode.**
   - Auto (default, approved by the owner 2026-11-02 22:34 CST): add no mode flag. ck-run injects `-s workspace-write -c approval_policy="on-request" -c approvals_reviewer="auto_review" -m <model>`
     (v4: the model of the alias or tier, plus `-c model_reasoning_effort="<effort>"` when the alias has one). The agent works
     on its own: it marks unknowns instead of stopping, lists open questions under "Questions for the owner" at the end of its
     summary, and keeps `PROGRESS.md` in its work folder. Writes stay inside `--write-scope` if given, else the workspace minus raw
     folders and rule files (checked after the run). It runs in an iTerm2 window (`ck-run launch` adds `--interactive`).
     After the run, read the "Questions for the owner" list and relay it to the user.
   - Read: add `--mode read` for look-only tasks. Codex runs with `-s read-only`.
   - Edit (scoped, legacy): only if the user asked for a change in this conversation. Add `--mode edit --approved "<user's words> (YYYY-MM-DD HH:MM CST)"
     --write-scope <folder>`. Allowed scope: a workspace subfolder that is not raw or a rule file (NV: only inside `NV Project/`), or a
     `~/PhD_local/<repo>` git repo. Codex gets `-s workspace-write` with network off and can write only in the scope.
   - Never pass skip-permissions, `--dangerously-bypass-approvals-and-sandbox`, yolo, `--full-auto`, force, `danger-full-access`, or any
     permission flag (`-s`, `-c`, `--add-dir`, ...). ck-run sets the auto flags itself and refuses them from you, along with every bypass flag (exit 2). Don't work around a refusal.
5. **Launch** (v4: detached, returns at once). Open the ask first (`ck-delegate`), then:
   ```
   cd "<folder>" && ~/PhD_local/ck-dispatch/bin/ck-run launch <slug> run --ask <A> --model sol \
     --workspace <devfab|nv> --title "<short title>"
   ```
   launch adds `--prompt-file ~/PhD_local/agent_runs/<slug>_prompt.md` and `--interactive`, writes `<slug>.sh` and prints
   `slug:`, `sh:`, `out:`, `pid:`. The run's output goes to `~/PhD_local/agent_runs/<slug>.out`, which ends with
   `ck-run exit=N`. Grok Bot: start one background watcher (block_until_ms 0) and wait for its notice; don't poll:
   `until grep -q '^ck-run exit=' ~/PhD_local/agent_runs/<slug>.out; do sleep 20; done; cat ~/PhD_local/agent_runs/<slug>.out`
   Runs go in parallel (no workspace lock). Edit runs claim their write folders automatically (so do auto runs given
   `--write-scope`); pass `--claim <path>` (repeatable) for other files you will edit.
   **Model:** `--model sol` (gpt-6.1-sol, high effort), `sol-fast` (gpt-6.1-sol, low effort) or `astra` (gpt-6-astra);
   an alias implies codex, so `--agent` may be left out. With `--agent codex` and no `--model`, the ask size picks it:
   `sol-fast` (S), `sol` (M, L). Astra (top tier) only for an L step with `--tier top`, a race, or when the owner names it.
   ck-run adds `-m` and the effort itself; never pass them. `--timeout <s>` for long jobs (default from the ask size:
   S 10 min, M 30 min, L 2 h; max 7200), `--parent <run_id>` for a follow-up.
   Lanes (`ck-run route --lane <lane>`): Sol is the worker for lab code, bug fixes, numbers (the code), wiki records and
   repo work, and the check for writing that leaves the lab. Astra takes hard steps and races.
6. **Read only the summary.** `~/PhD_local/agent_runs/<slug>.out` holds the `summary.md` path (line 1), the summary (max 10 lines)
   and the exit line. Don't open stdout.log, last.md or result.md unless the user asks. `ck-run show <run_id>` re-prints a summary.
   Exit: 0 ok · 1 partial · 2 refused (nothing ran) · 3 failed/timeout/stalled · 4 flagged (needs a human look) · 5 violation
   · 6 busy (file/folder claim conflict) · 7 over budget (nothing ran).
7. **Session id and resume.** `R` = the folder of the summary path (`~/PhD_local/agent_runs/<run_id>`). Read just these two fields:
   ```
   python3 -I -c 'import json,sys;print(json.load(open(sys.argv[1]))["session_id"])' "$R/result.json"; grep -m1 '^# cwd:' "$R/cmd.txt"
   ```
   When the user asks (v4 cards carry no run ids), give the run id, the session id (Codex thread id) and `cd "<cwd>" && codex resume <session_id> -s read-only`.
   A resume runs outside ck-run's guards; your own follow-ups use `--parent <run_id>` (through `ck-run launch`).
8. **Follow up at once.** When the notice arrives, close the ask with its finish card (`ck-run ask close`), or take the next
   step, as in `ck-delegate`. A review only with a reason: `ck-run review <run_id> --by <other agent> --trigger
   leaves-lab|hardware-or-raw|agent-unsure|you-asked` (launch it like a run). Session id and resume command on request.
9. **On failure** (not logged in, rate limit, refused, busy, over budget): give the exact error line and the fix (e.g. `codex login`). Never retry
   with looser permissions. Busy (6) = a file/folder claim conflict with a live run (stderr names it): wait for
   that run's notice, or use other paths. Over budget (7) = the ask's budget is used: ask the owner; add
   `--over "<the owner's words>"` only with their real words. If ck-run itself is broken, a raw read-only run
   (`cd "<folder>" && codex exec -s read-only --json - < ~/PhD_local/agent_runs/<slug>_prompt.md`) needs the user's OK first.

Not yet checked live (step 3 skipped Codex): `--output-schema`, the network-off key and the `codex resume -s` flag. Tell the user
when a run is the first live Codex check, and watch its status closely.
