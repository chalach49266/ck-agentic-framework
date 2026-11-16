---
name: CK delegate
description: Use when CK (Grok Bot) hands a PhD task to the agent fleet (claude, codex, cursor, agy) through ck-run v4. Opens an ask with a size and budget, launches runs (solo, pair, race, split, panel, loop), reviews only with a reason, and closes the ask with one finish card.
---
# CK delegate (v4): asks, budgets, launch, finish cards

Runner: `~/PhD_local/ck-dispatch/bin/ck-run` (guide: `~/PhD_local/ck-dispatch/docs/v4.md`). Router (size, pattern,
playbook, models): `~/PhD_local/ckstack/ck-mode/SKILL.md`. Per agent: `claude-code-prompt`, `codex-prompt`,
`cursor-agent-prompt`, `antigravity-prompt`. Each run gets a folder in `~/PhD_local/agent_runs/`; every event goes to
`agent_runs/ledger.jsonl`.

## 0. Who runs this
Grok Bot. Claude Code only as the owner's stand-in, when the owner typed `/grokbot` because Grok usage ran out (the grokbot
mod refuses ck-run commands that start or change work while the mode is off). Stand-in rules:
`~/PhD_local/grokbot-mod/GROKBOT.md`.

## 1. One ask per request (small stays small)
- Open it before any agent starts:
  `ck-run ask open --words "<the owner verbatim>" --size S|M|L --title "<the goal in your words>" [--project P] [--pattern solo|pair|race|split|panel|loop] [--models a,b]`
  Line 1 = the ask id (`A-MMDD-N`); then the start card. Show the owner the start card.
- the owner's words win: "quick", "short", "for now", "no review" = S. "check it", "deep", "race" = a review or a pattern.
- S and reading is enough: answer it yourself, no agent: `ck-run ask answered <ask> --summary "<1-3 lines>"` (it
  closes the ask and prints the finish card).
- The brief = the owner's words + "Do only this:" (S at most 2 steps, M at most 4). Extra ideas go to the Later list
  (`ck-run ask later <ask> "<item>"`), never into new work.
- L: write the plan first (`~/PhD_local/agent_runs/<name>_plan.md`: steps that each end with a check, who does each,
  why with source tags, a block diagram, and a line like `budget: runs=6 parallel=3 reviews=2 fixes=2 wall_min=180`).
  Show the owner the plan card; after the OK, open the ask with `--plan <that file>`.

## 2. Budgets (ck-run counts them)

| | S | M | L |
|---|---|---|---|
| runs (fixes included) | 1 | 2 (1 + 1 fix) | 6 |
| live at the same time | 1 | 1 | 3 |
| reviews | 0 (1 if `you-asked`) | 1 | 2 |
| fix runs (`--parent`) | 0 | 1 | 2 |
| wall time | 15 min | 45 min | 180 min |
| timeout per run | 10 min | 30 min | 2 h |
| stall alarm | 3 min | 5 min | 8 min |

- A race gets one run per racer, all at once. `--parallel N --because "<the owner's words>"` at open allows more at once.
- **Exit 7 = over budget**: nothing started. Ask the owner. Only with the owner's real words, add
  `--over "<the owner's words>"` to that ONE command. Never write the words yourself.
- Wall time over: the ask parks. Write the finish card with what is done.

## 3. Models: lanes and tiers
- `ck-run route --lane <lane>` names the worker, the also-good models and the check model, and skips rate-limited
  agents. Lanes: `quick` (you), `lab-code`, `bug-fix`, `numbers`, `wiki`, `writing`, `decision` (race), `loop`, `repo`,
  `scout`, `mechanical`. `ck-run models` prints the table.
- `--model <alias>` implies the agent: `sol`, `sol-fast`, `astra` (codex); `opus`, `opus-max`, `sonnet`, `haiku`
  (claude); `grok`, `composer` (cursor); `gemini` (agy). A model the owner names wins.
- No `--model`: the ask size picks the tier (S fast, M and L strong). Top tier only for L with `--tier top`, races,
  or a top model the owner names (`--model astra`); `--tier top` in an S or M ask is over budget (exit 7).
- Workspace (OneDrive) edits cannot go to claude: it edits only `~/PhD_local` repos.
- Use the fleet, not a pile: different families on different parts at once; never several agents on one small thing.
- Escalate, don't multiply: fast tier, then one retry on the strong tier, then one advisor run (top tier, other
  family), then ask the owner.

## 4. Launch (detached)
1. `cd` to the work folder. Write the task to `~/PhD_local/agent_runs/<slug>_prompt.md`: the owner's words, "Do only
   this:", paths (not pasted content; cap 200 KB), write scope.
2. `ck-run launch <slug> run --ask <A> --model <alias> --workspace <devfab|nv|washu> --title "<title>" [--write-scope F] [--claim P] [--mode read]`
   It writes `agent_runs/<slug>.sh`, adds `--prompt-file` (your `<slug>_prompt.md`) and `--interactive`, starts the
   run detached and prints `slug:`, `sh:`, `out:`, `pid:`. Slug = `<ask>-<word>` (e.g. `A-1105-4-wiki`, `A-1105-4-fix1`,
   `A-1105-4-review-claude`); a used slug is refused.
3. Tell the owner in one line: who, where, which mode.
4. Wait for the end: `~/PhD_local/agent_runs/<slug>.out` ends with `ck-run exit=N`. Grok Bot: start one background
   watcher (block_until_ms 0): `until grep -q '^ck-run exit=' ~/PhD_local/agent_runs/<slug>.out; do sleep 20; done; cat ~/PhD_local/agent_runs/<slug>.out`.
   Its notice wakes you; don't poll. (The Claude Code stand-in: the mod wakes you, once per launch and once per race
   or panel.)
Modes: auto (default), read (`--mode read`), edit (as before). Runs go in parallel; edit runs claim their write
folders; exit 6 = a claim conflict.

## 5. Patterns
- **solo**: one launch.
- **pair**: the worker's run, then one review from another family, with a reason (section 6).
- **race**: `ck-run race --ask A --prompt-file F --title T --workspace W [--models astra,opus,grok] [--mode read|auto]`
  (read by default).
  It prints the slugs (`<A>-race-<alias>`); wait for each `.out` as in section 4. Then `ck-run race show --ask A`.
  Write ONE answer and show where the models disagree.
- **split**: one launch per part (own slug, own agent), then merge and one check. Parts at the same time need
  parallel ≥ 2 (L, or `--parallel`).
- **panel** (the owner's word "deep", or L writing that leaves the lab): `ck-run panel RUN --by codex,claude,cursor --trigger T [--ask A] [--focus "..."]`.
  Use it in an L ask (2 reviews; 3 need `reviews=3` in the plan budget line).
- **loop**: `ck-run launch <slug> loop --ask A --model <alias> --prompt-file F --workspace W --metric "<cmd>" --target "<op><number>" --max N`.
  The metric is a cheap local check, never a cloud sim. Open an L ask with `--pattern loop`. Each round is one run;
  rounds after the first also count as fixes. Set `runs=N`, `fixes=N-1` and `wall_min` to numbers in the plan budget.

## 6. Review only with a reason
- `ck-run launch <slug> review <run_id> --by <other agent> --trigger <reason> [--focus "..."]`.
- Reasons: `leaves-lab` (numbers or claims go to slides, a paper, a patent, VC or AQS, an email, a purchase),
  `hardware-or-raw` (code that drives lab hardware or touches raw data), `agent-unsure` (partial, not checked, or a
  `guess` on a choice that matters), `you-asked`. No reason, no review. S asks: only `you-asked`.
- Never start a review by habit or "right away". Small asks stay small (the owner 2026-11-05).
- Quick review: verdict first, at most 3 findings, each with proof (a command and its output, a datasheet page, a
  paper figure). Findings without proof are dropped. A finding that does not block the ask goes to Later. A fix run
  only within the budget (M: 1, L: 2); then ask the owner.
- No automatic Claude review after cursor or agy runs any more (the owner 2026-11-05: "no need review, since those one
  are for simple stupid task anyways"). The rule check still runs on every run.

## 7. Exit codes
0 ok · 1 partial · 2 refused (never retry with looser flags) · 3 failed, timeout or stalled · 4 flagged ·
5 violation · 6 busy (claim conflict: wait, or use other paths) · 7 over budget (ask the owner).
- **Exit 4 or 5: stop the chain.** `ck-run andon raise --project <P> --reason "<what happened>"`, give the owner the
  stderr line and the run folder, and do nothing more until the owner decides. Clear it only with the owner's words:
  `ck-run andon clear --project <P> --note "<the owner's words>"`.
- Exit 3 with "stopped by the watchdog": the run hung. Read its work folder's PROGRESS.md and, within the budget,
  launch a short finishing run with `--parent <run_id>`.
- A run whose watcher died (restart, crash): `ck-run reattach` finishes it from what is on disk.

## 8. Close the ask
- `ck-run ask close <ask> --done yes|partial|no [--note "..."]` prints the finish card (at most 8 lines, no run ids:
  done?, what changed, how sure, you should know, your move, Later). It accepts the ask's open ok and partial runs,
  rejects failed ones, and leaves flagged or violation runs for the owner. Give the owner that card as it is.
- the owner answers "yes 2": open a new ask for Later item 2.
- One run only: `ck-run accept <run_id> [--reject] [--by user] --note "..."` still works.

## 9. See it
`ck-run board` (needs you, running, done today; `--md` writes `~/PhD_local/BOARD.md`), `ck-run recall <project>`,
`ck-run digest --since 7d`, `ck-run rules` (what each agent may do; `--check` shows drift), `ck-run models`,
`ck-run thread <run_id>`, `ck-run show <run_id>`.

## Keep Grok Bot tokens low
- Read only the `.out` (summary path, a summary of at most 10 lines, the exit line) and the cards. Never paste
  stdout.log, stderr.log, result.md, prompt.md or the ledger into chat.
- Give agents paths, not pasted content.
- Open result.md only if the owner asks, or the status is partial and the summary cannot answer; then read only the
  part you need.
