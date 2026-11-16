# grokbot-mod: `/grokbot` makes Claude Code your Grok Bot stand-in

Made 2026-11-04 for the owner, while Grok Bot usage is out. Type `/grokbot` in any Claude Code session and Claude acts
as Grok Bot (CK): the orchestrator that routes work to claude, codex, cursor and agy through
`~/PhD_local/ck-dispatch/bin/ck-run`, the same framework Grok Bot uses (`~/PhD_local/grok-bot-skills/ck-delegate`).

The command enables the same dispatch workflow in Claude Code.

## v4 (2026-11-05)

Trigger words, a short status line, a text board, and documented launches form the workflow.

- **Trigger words** (mode on). When your prompt starts with trigger words, Grok Bot gets one more line. Example:
  `race: why is the fibre coupling stuck at 5%?` gives
  `[ck: trigger=race size=auto pattern=race models=astra+opus+grok playbook=auto]`.
  Words: `quick do plan race check recall`, `split deep fix loop why number teach`, model words
  `sol astra opus sonnet haiku grok composer gemini`, sizes `S M L` (upper case only). The mod reads the first line
  up to the first `:` or the first word that is not a trigger word. "Grok Bot ..." does not count as the model `grok`.
  `/grokbot <task>` puts the same line in its first note.
- **Status line** (mode on, every 20 s): `Grok Bot ON · sol 12m · opus 3m · grok 1m · 1 needs you`. One token per
  live run: model alias and minutes, from `agent_runs/.claims/*.json` and the ledger. "Needs you" counts, in the
  last 24 h: an ask refused over budget and not approved since, a stall of a live run, a flagged or violation result
  with no accept or reject. The mod reads only the end of the ledger (at most 2000 lines). Nothing to show: the line
  stays `Grok Bot ON (/grokbot off)`.
- **Views** (any mode, read only): `/grokbot board`, `/grokbot today`, `/grokbot recall <project>`,
  `/grokbot rules`, `/grokbot models` (table below). The mod runs `~/PhD_local/ck-dispatch/bin/ck-run` and shows the
  first 60 lines.
- **Wake and notify.** Launches made in this session are watched every 20 s. When one ends, the mod logs the result
  (as before), sends a notification (`<slug>: finished, exit N`), and wakes Grok Bot once:
  `[ck-run] <slug> finished (exit N). Read ~/PhD_local/agent_runs/<slug>.out, then write the finish card (ck-run ask close) or the next step.`
  A race or a panel wakes once, when all its runs have ended. When a prompt starts a turn first, the same text goes
  with that prompt instead. While the mode is off: log and notification only, no wake. A launch made in another
  session is logged at your next prompt (as before) and never wakes you.
- **Gate v4.** Always allowed (read only): `show thread active limits route board digest recall rules models
  scoreboard`, `ask list`, `ask show`, `andon list`, `race show`, and any `--help` or `--dry-run`. Mode off: every
  command that starts runs or changes asks is refused (`run dispatch review accept launch race panel loop reattach`,
  `ask open|close|park|later|answered`, `andon raise|clear`). Mode on: all of those pass, except a typed
  `ck-run run`, `dispatch` or `review` (use `ck-run launch <slug> run|review ...` or a documented
  `agent_runs/<slug>.sh`). A `ck-run launch` must write its slug as plain text and keep its iTerm window (no
  `--no-live`). `ck-run launch`, and the runs that `race`, `panel` and `reattach` start, get a `launch` entry in
  `agent_runs/grokbot_standin_log.md` and go on the waiting list. A launch that ck-run refuses is not watched.
- The gate checks each shell command. Mentions of commands in ordinary text stay allowed.
- The reminder says the playbook loads ckstack (`~/PhD_local/ckstack/ck-mode/SKILL.md`). The first note attaches
  ck-mode when that file exists.

## Use

| Type | What happens |
|---|---|
| `/grokbot` | Mode ON. Claude gets the full playbook (`GROKBOT.md`) once, the status line shows `Grok Bot ON (/grokbot off)`. Then type your task. |
| `/grokbot <task>` | Mode ON, and `<task>` is sent as your next prompt right away. Example: `/grokbot check the current task` |
| `/grokbot status` | Shows ON/off, since when, and the playbook, ck-mode, router-log, session-log and framework paths, and the launches still running. |
| `/grokbot off` | Mode OFF. Back to normal Claude Code. Live ck-run jobs keep going. |
| `/grokbot board` | `ck-run board`: what needs you, what runs, what was done today. Any mode, read only (v4). |
| `/grokbot today` | `ck-run digest --since 1d`: per project, today's asks, runs and agent time (v4). |
| `/grokbot recall <project>` | `ck-run recall <project>`: a few lines on the project, its asks, the next move (v4). |
| `/grokbot rules` | `ck-run rules`: what each agent may do, and the owner's decisions (v4). |
| `/grokbot models` | `ck-run models`: model aliases, tiers and lanes (v4). |

While the mode is on, Claude:
- opens an ask, selects a lane and model, then uses `ck-run launch` (one iTerm2 window per ask, one tab per run);
- answers small asks itself, reviews only with a reason, and gives one finish card through `ck-run ask close`;
- writes `agent_runs/<slug>_prompt.md`; ck-run writes the launch file, output, run folder and ledger;
- keeps the router log: `~/PhD_local/grokbot_router/PROGRESS.md`, or the project's own;
- ends replies with "Questions for the owner".

The mod itself logs your prompts verbatim (only while the mode is on) to
`~/PhD_local/grokbot_router/sessions/<YYYY-MM-DD>_<session-id-8>.md`.

The mode belongs to one conversation. A new session, `/clear`, `/resume`, `/branch` and every ck-run worker start
with it off, so workers never think they are Grok Bot. Type `/grokbot` again after any of those (after `/clear` a
toast says so and the status line clears).

**ck-run gate.** Enable Grok Bot mode before dispatching. While the mode is off, the mod refuses any Bash command
that runs `ck-run run`, `dispatch`, `review` or `accept`, or launches an `agent_runs/*.sh` file, with the message
"grokbot: ck-run dispatches from Claude Code are allowed only in Grok Bot mode ...". Read-only commands
(`ck-run show`, `thread`, `active`, `limits`, `route`, `--help` of those, `cat` of a `.sh`) always work. The gate is
also in the delegation skills' text (`grok-bot-skills` main, commit 7224a03).
The gate reads only shell code: text that merely mentions a dispatch (a heredoc that writes a prompt file, a `.sh`
file or a log line; a quoted `echo`/`grep`/commit message) is allowed. Quoted code that a shell runs
(`bash -c "..."`, `eval`, `osascript -e '...'`, `bash <<EOF`) is still checked. (False positive found and fixed
2026-11-04 17:30: a Python heredoc that wrote "ck-run accept" into a log was refused.) `--help` and `--dry-run` start
nothing and always pass.

**Every agent run is documented in `~/PhD_local/agent_runs`.** In Grok Bot mode:
- A `ck-run run`, `dispatch` or `review` typed directly is refused. Runs start only from a launch file.
- A launch is allowed only if: the `.sh` is a full path inside `~/PhD_local/agent_runs/` and exists; every ck-run line
  in it has `--interactive`; every `--prompt-file` is an existing file inside `agent_runs/` (a `run` needs one; a
  `review` does not); and the output goes to `agent_runs/<slug>.out` or `agent_runs/<slug>_<name>.out`, redirected by
  the launching command or inside the `.sh` (never a scratchpad or `/tmp`). A direct agent session opened in iTerm by
  `osascript` (no ck-run line, the ck-dispatch exception) must name its saved `agent_runs/<slug>_prompt.md`.
- The mod writes **`~/PhD_local/agent_runs/grokbot_standin_log.md`** itself: a `launch` entry (launch file, prompt,
  output, the ck-run line as written, Claude session, raw prompt log), an `accept`/`reject` entry (run id, by, note),
  and a `result` entry once the `.out` holds `ck-run exit=N` (run id(s), exit code, run folder, summary). Results are
  logged when the next prompt or task notice arrives, in any session (the waiting list is kept in the mod's store);
  `/grokbot status` shows what is still waiting. No exit line after 8 h = a `no result` entry (the watcher probably died).
## Files

| Path | What |
|---|---|
| `GROKBOT.md` | **The playbook**: the rules Claude follows as Grok Bot. Edit it to change the behaviour; the next `/grokbot` sends the new text. |
| `grokbot/` | The mod (a Claude Code plugin of function hooks). |
| `grokbot/hooks/register.ts` | The code: `/grokbot` command, prompt reminder, prompt log, ck-run gate, `/clear` handling. |
| `grokbot/types/index.d.ts` | Its state contract (`grokbot.mode`: on, since, sessionLog). |
| `grokbot/tests/grokbot.test.ts` | 15 tests (`claude plugin test grokbot`). |
| `~/PhD_local/agent_runs/grokbot_standin_log.md` | The mod's run log: every launch, accept/reject and result in Grok Bot mode (created on first use). |
| `.claude-plugin/marketplace.json` | Makes this folder a local marketplace named `ck-grokbot`. |
| `../grokbot_router/` | Router log (`PROGRESS.md`) and the mod's raw session logs (`sessions/`). |

Framework doc (OneDrive): `PhD/AI_Agent_Framework/Claude_Code_as_Grok_Bot.md`.

## Install state (2026-11-04)

Installed at user scope, so `/grokbot` is in every new Claude Code session:
```
claude plugin marketplace add ~/PhD_local/grokbot-mod
claude plugin install grokbot@ck-grokbot --scope user
```
`claude plugin list` shows `grokbot@ck-grokbot ... Read from: ~/PhD_local/grokbot-mod/grokbot`. Claude Code reads
the mod from this folder itself (no copy), so a code edit here takes effect in new sessions, or after
`/reload-plugins` in a running one. `GROKBOT.md` edits need no reload.

Remove it: `claude plugin uninstall grokbot@ck-grokbot` and `claude plugin marketplace remove ck-grokbot`.

## How it works (and one limit)

- `session.start` registers `/grokbot`. `command.run` answers it: sets the session state, sets the status line, writes
  the session log, and returns the playbook as a hidden note to Claude (`context`). For `/grokbot <task>`, a 50 ms
  timer submits the task as your prompt (a command hook may not submit itself; it would wait on its own turn).
- `prompt.submit`, while on: logs your words and attaches a one-paragraph `[Grok Bot mode ON ...]` reminder to every
  prompt that starts a turn (your prompts and ck-run completion notices). The reminder is what keeps the mode through
  a context compaction: it tells Claude to Read `GROKBOT.md` again when the playbook is no longer in context.
- `tool.call` on Bash (the gate): refuses ck-run dispatches while the mode is off (see above). It judges before the
  command runs, and refuses if the check itself fails.
- `command.run` on `/clear`, `/resume`, `/branch`: the engine resets the mode to off there and skips `session.start`,
  so the hook clears the status line, logs "/clear ended Grok Bot mode" and shows a toast (bug found live 2026-11-04:
  the status line kept saying ON after `/clear`).
- **Limit:** the mod does not put the playbook in the system prompt. On Team and Enterprise plans the built-in guard
  `cc-plugin-sec-default` skips user mods' `prompt.compose` hooks (it does the same to the `skins` mod). Checked live
  2026-11-04: a compose hook was skipped, so it was removed and replaced by the per-prompt reminder. Not worked around.
