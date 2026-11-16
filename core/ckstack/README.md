# ckstack: the owner's own pstack

v0, written 2026-11-05 23:25 CST for ck-run v4. Home: `~/PhD_local/ckstack`.

ckstack is the rulebook for the owner's bots: Grok Bot, its Claude Code stand-in, and every agent that ck-run starts
(Codex, Claude, Cursor with Grok or Composer, agy with Gemini). It has one router (`ck-mode`), 12 principles,
12 playbooks for lab work, 13 small skills, and one brief every agent reads first. ck-run enforces the budgets, review
reasons and proof levels; ckstack says how to use them. The ideas come from pstack and the Cursor plugins (see
Credits), rebuilt around the owner's own rules and domain skills.

## Files
| File | What |
|---|---|
| `ck-mode/SKILL.md` | the router: trigger words to size, pattern, playbook and models; start and finish cards |
| `principles/PRINCIPLES.md` | the 12 principles: rule, why, the owner's example, what enforces it |
| `playbooks/*.md` | quick-answer, lab-code, bug-fix, numbers, wiki-records, outside-writing, design-loop, sim-handoff, fab-run, repo-work, research-scout, pickup |
| `skills/*/SKILL.md` | recall, ketchup, why, number, teach, race, split, panel, verify, reflect, correct, sharpen, plain |
| `agents/ck-worker.md` | the brief every agent reads first |
| `models.md` | the lanes in words (the source of truth is `ck-dispatch/config/models.json`) |
| `AGENTS.md` | the pointer for Codex and other agents |
| `.claude-plugin/`, `.cursor-plugin/` | plugin files for Claude Code (local marketplace `ckstack`) and Cursor |

## How the owner uses it
Type the ask as usual. Grok Bot answers with a start card: size, pattern, models, budget. Reply only to change it.
Or start with a word:

| Word | You get | Uses |
|---|---|---|
| `quick` | one short answer, no review | `playbooks/quick-answer.md` |
| `do` | one agent does one job | the lane's playbook |
| `plan` | a plan card first; work after your OK | the lane's playbook |
| `race` | Astra + Opus + Grok 4.7 on one question, one merged answer | `skills/race` |
| `check` | one review from another family | the lane's check |
| `recall` | catch me up; what waits for me | `playbooks/pickup.md`, `skills/recall`, `skills/ketchup` |
| `split` | parts run in parallel on different agents | `skills/split` |
| `deep` | 2 or 3 reviewers with different lenses | `skills/panel` |
| `fix` | reproduce, root cause, fix, test | `playbooks/bug-fix.md` |
| `loop` | improve one number until a target | `playbooks/design-loop.md` |
| `why` | where a choice came from, with sources | `skills/why`, `playbooks/research-scout.md` |
| `number` | what else this number could be, and what limits it | `skills/number`, `playbooks/numbers.md` |
| `teach` | explain it so I understand it | `skills/teach` |

Put model words with the leading triggers, before `:` or the task text: `sol astra opus sonnet haiku grok composer gemini`.
Size words: `S M L`.
```
quick: <question>
do sol: <task>
plan split: <project step>
race: <decision>
recall <project>
```
Sizes: S = 1 run, no review unless you ask, 15 min. M = 1 run + 1 fix, 1 review with a reason, 45 min.
L = from the plan card (default 6 runs, 3 at once, 2 reviews, 180 min). Over a budget, ck-run stops (exit 7) and
Grok Bot asks you. Your words open the way: `--over "<your words>"`. At the end you get one finish card: done?, what
changed, how sure, what you should know, your move, the Later list ("yes 2" starts Later item 2).

## How it plugs in
1. Grok Bot and the stand-in read `ck-mode/SKILL.md` first (GROKBOT.md v4 says so; the real Grok Bot: see Install).
2. ck-run's prompt says: FIRST read `agents/ck-worker.md`, the playbook, and the domain skills named in the task
   (`~/PhD_local/grok-bot-skills/<name>/SKILL.md`). Plain files read by path work for all four CLIs.
3. ck-run reads `config/models.json` (lanes, tiers) and counts the budgets. ckstack never sets flags itself.
4. The grokbot mod reads the trigger words and adds one line: `[ck: trigger=... size=... pattern=... models=... playbook=...]`.
5. It learns: `skills/reflect` each week, `skills/correct` when a mistake repeats, the scoreboard for lane changes.
   the owner approves each change.

## Install (three ways, one folder)
- Claude Code: `claude plugin marketplace add ~/PhD_local/ckstack`, then `claude plugin install ckstack@ckstack`.
  Every skill has `disable-model-invocation: true`: nothing loads by itself. They show as `/ckstack:<name>`, and
  Grok Bot mode reads them by path.
- Codex: workers get the paths in their task file. A standing pointer is one line in `~/.codex/AGENTS.md`
  ("ck-run workers: read ~/PhD_local/ckstack/AGENTS.md"). That file is the owner's: add it only with the owner's OK.
- Cursor and Grok Bot: `.cursor-plugin/plugin.json`. TODO(verify): how the owner's Grok Bot registers skills (open
  since the share package). The Cursor plugin schema has a `grokbot` client id, so the format is meant for Grok Bot
  too; the exact install step is not known yet.

## Rule and what enforces it
Check = something refuses or stops when the rule is broken. Auto = a tool does it for you. Text = only written
down; `skills/correct` turns a text rule that is broken twice into a check.

| Rule | Enforced by | Kind |
|---|---|---|
| Every run belongs to an ask | ck-run: `--ask` required (`asks.required`), exit 2; a review takes its run's ask | check |
| A budget per ask: runs, live at once, reviews, fixes, wall time | ck-run ask gate, exit 7; `--over "<the owner's words>"` is logged | check |
| A review needs one of 4 reasons | `ck-run review --trigger`, exit 2 without it; S takes only `you-asked` | check |
| Raw data is read-only | ck-run guards and the rule check (exit 5) | check |
| No cloud simulation | prompt hard rules; the rule check flags cloud jobs | check |
| Stop the chain on a flag or violation | exit 4 or 5; `ck-run andon` blocks new runs in the project | check |
| Every launch is written down in `agent_runs` | `ck-run launch` writes the `.sh` and `.out`; the mod refuses a typed `ck-run run` | check, auto |
| Code and config match the owner's decisions | `ck-run rules --check` (exit 1 on drift) | check |
| Proof level, source tags, what else and limit, Later, plain summary | required fields in `schema/result.schema.json` | check (fields), text (honesty) |
| No invented numbers | prompt hard rules; `numbers[].source` and `verified` | check (fields), text |
| Trigger words | the grokbot mod's `[ck: ...]` line; the table in `ck-mode` | auto |
| Stalled runs do not wait for the timeout | the watchdog (3, 5, 8 min by size); `caffeinate` while runs are live | auto |
| Times come from tools | ledger stamps; the `ck-run launch` header | auto |
| The right model for the job | `config/models.json` lanes; `ck-run route --lane` | auto (default) |
| One finish card per ask, no run ids | `ck-run ask close` builds it from the result fields | auto |
| S asks: Grok Bot answers itself | `ck-mode`; `ck-run ask answered` records it | text |
| Findings need proof; fix root causes; explain the number | `agents/ck-worker.md`, the playbooks, `skills/panel`, `skills/number` | text |
| Subtract before you add | `principles/PRINCIPLES.md` | text |
| Plain words, one page first, plans get diagrams | `skills/plain`, `ck-mode` | text |

## Credits
Ideas adapted from pstack (Lauren Tan, MIT) and from the Cursor plugins repository (MIT): orchestrate,
cursor-team-kit, advisor, thermos, teaching, continual-learning, cli-for-agent, and dyl-stack (Dylan Gattey, MIT).
The text is rewritten in our own words; a few short phrases (such as "deeper, not bigger") are kept. Details and the
MIT notice: `LICENSE-THIRD-PARTY.md`.
