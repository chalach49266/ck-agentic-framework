# Architecture

One diagram per idea. Each diagram has a few lines of plain text under it.
Sources: `core/ck-dispatch/docs/v4.md`, `core/grokbot-mod/GROKBOT.md`, `core/ckstack/ck-mode/SKILL.md`,
`core/ck-dispatch/platform/*/README.md`, `core/ck-dispatch/platform/auto/osascript`.

## 1. The whole chain

```mermaid
flowchart LR
  U([You]) --> G["Grok Bot<br/>Claude Code with /grokbot on"]
  G -->|"1 ask open"| R[ck-run]
  G -->|"2 launch / race / panel"| R
  R -->|"guards + budget + claims"| AG["Agent CLI<br/>claude / codex / agent / agy"]
  AG --> PANE["Live pane<br/>Herdr (PC) · iTerm2 or Herdr (Mac)"]
  AG -->|"result.md, summary.md"| RUN[(run folder)]
  RUN --> R
  R -->|"ledger.jsonl + slug.out"| MOD["grokbot mod<br/>(Claude Code plugin)"]
  MOD -->|"wake: run finished"| G
  G -->|"3 ask close"| CARD([Finish card])
```

- **Grok Bot** is the orchestrator. Today it is Claude Code with the `/grokbot` mode on (a stand-in for the real
  Grok Bot). It does not do heavy work itself. It routes.
- **ck-run** (`~/PhD_local/ck-dispatch/bin/ck-run`) is the only way to start an agent. It checks guards, the ask's
  budget and path claims, builds the agent's command, and writes everything to the ledger.
- **Agents** are the CLIs, each signed in by you: `claude`, `codex`, cursor `agent`, `agy`.
- **Panes**: each run is visible in its own live terminal pane.
- **The mod** watches launches of this session and wakes Grok Bot once when they end.

## 2. One ask, start to finish

```mermaid
sequenceDiagram
  participant You
  participant GB as Grok Bot
  participant CR as ck-run
  participant AG as Agent
  participant MOD as grokbot mod
  You->>GB: "do: write the wiki page"
  GB->>CR: ck-run ask open --words ... --size M --title ...
  CR-->>GB: ask id + start card
  GB-->>You: start card (goal, size, budget)
  GB->>GB: write agent_runs/<slug>_prompt.md
  GB->>CR: ck-run launch <slug> run --ask <id> --model sol ...
  CR->>AG: start in a live pane (detached)
  AG-->>CR: result.md, then summary.md
  CR->>CR: rule check, ledger, "ck-run exit=N" in <slug>.out
  MOD->>GB: "<slug> finished (exit N)"
  GB->>CR: ck-run ask close <id>
  CR-->>GB: finish card
  GB-->>You: finish card (changed, how sure, your move, later)
```

- An **ask** is one request from you. Every run, review and fix carries its ask id (`A-MMDD-N`).
- You see one **start card** and one **finish card** per ask. No per-run reports.
- A run is started **detached** (`ck-run launch`), so it keeps going if Claude restarts.

## 3. Words to size, pattern and models

```mermaid
flowchart TD
  W["Your first word<br/>quick · do · plan · race · check · recall<br/>split · deep · fix · loop · why · number · teach"] --> M["grokbot mod adds a line<br/>[ck: trigger=... size=... pattern=... models=...]"]
  M --> R["ck-mode router<br/>(core/ckstack/ck-mode/SKILL.md)"]
  R --> S{Size}
  S -->|S| SELF["Grok Bot answers itself,<br/>or 1 fast run"]
  S -->|M| ONE["1 run (+1 fix, +1 review)"]
  S -->|L| PLAN["plan card first, then up to 6 runs"]
  R --> L["Lane picks the model<br/>(config/models.json)"]
```

- The size sets a **budget** that ck-run counts (runs, live at once, reviews, fixes, minutes). Over budget = exit 7.
- The **lane** picks who works and who checks, for example `writing`: opus works, sol checks.
- Full tables: [`HOW_TO_USE.md`](HOW_TO_USE.md).

## 4. Patterns

```mermaid
flowchart LR
  subgraph P_solo["solo"]
    A1[one agent]
  end
  subgraph P_pair["pair"]
    B1[worker] --> B2[reviewer, other family]
  end
  subgraph P_race["race"]
    C0[same task] --> C1[opus] & C2[sol / astra] & C3[grok]
    C1 & C2 & C3 --> C4[race show: one merged answer]
  end
  subgraph P_panel["panel"]
    D0[one finished run] --> D1[review 1] & D2[review 2] & D3[review 3]
  end
  subgraph P_loop["loop"]
    E1[run] --> E2[metric] --> E3{target?} -->|no| E1
  end
```

- **solo**: one agent. **pair**: one agent, then one review by another agent.
- **race**: the same task to 2 or 3 models at once. Grok Bot merges ONE answer and shows where they disagree.
- **split**: parts of a job to different agents at the same time. **panel**: 2 or 3 reviews of one run.
- **loop**: improve one number step by step with a cheap local metric. Never a cloud simulation.

## 5. Where the panes open (Windows PC)

```mermaid
flowchart TD
  CALL["ck-run needs a window<br/>(config live.osascript = platform/auto/osascript)"] --> ENV{"Caller's env<br/>(read from parent processes)"}
  ENV -->|"CK_LIVE_HOST=herdr<br/>or HC_TERMINAL_ID set"| H["platform/herdr/osascript<br/>pane in Herdr, under Grok Bot"]
  ENV -->|"CK_LIVE_HOST=wsl<br/>or nothing set"| T["platform/wsl/osascript<br/>tmux session + Windows Terminal tab"]
  FOLLOW["Follow-up call<br/>(read, type, close)"] --> SID{Session id}
  SID -->|"%7 (tmux pane)"| T
  SID -->|"t12 (Herdr address)"| H
```

- ck-run was built on the Mac. It talks to "iTerm2" through a program named `osascript`. On the PC that program is a
  stand-in script, so `ckdispatch/` needs no change.
- The router sends a new window to **where the caller runs**: Herdr or WSL, never both.
- ck-run cleans the environment of its children, so the router reads the env of its **parent** processes.
- Herdr sets `HC_TERMINAL_ID` in every Herdr terminal. The `.cmd` shortcuts forward it into WSL (`WSLENV`).
- Follow-ups go to the side that owns the run. Herdr window ids start at 5000; tmux ones are below.

## 6. Herdr layout (Windows PC)

```mermaid
flowchart LR
  subgraph tab["Grok Bot's tab"]
    direction LR
    GB["Grok Bot<br/>(left half)"]
    subgraph right["right half"]
      direction TB
      P1["run 1 · header: name, status circle, close"]
      P2["run 2"]
      P3["run 3"]
    end
  end
```

- Each run under a Grok Bot is a Herdr **sub-agent** (`hc run --parent`) and a pane in Grok Bot's tab.
- First run: right of Grok Bot (half the width). Next runs: stacked below on the right (3 runs = 1/2, 1/4, 1/4).
- Circle colors (layout `main-ck`, mod `agents-ck`): **green** = done, **yellow** = needs you, **red** = failed.
- A clean finished pane closes itself after `live.close_tab_after_s` (300 s in `core/ck-dispatch/config/workspaces.json`).
  A pane with a problem stays.
- When a run writes `result.json`, its pane sends Herdr a "done" or "error" state, so the Agents list updates at once.
- Herdr runs live in herdr-core (`hc.exe`), so they keep going when the Herdr window closes.

## 7. Wake: how Grok Bot knows a run ended

```mermaid
sequenceDiagram
  participant GB as Grok Bot (Claude Code)
  participant MOD as grokbot mod
  participant OUT as agent_runs/<slug>.out
  GB->>MOD: Bash: ck-run launch <slug> ... (slug typed literally)
  MOD->>MOD: add <slug> to the waiting list
  loop every 20 s
    MOD->>OUT: last line "ck-run exit=N"?
  end
  OUT-->>MOD: ck-run exit=0
  MOD->>GB: "[ck-run] <slug> finished (exit 0). Read the .out ..."
  MOD-->>GB: notification
```

- The mod finds launches by **reading the command text**. So type the ask id and slug literally (never `$A`).
- A race or panel wakes Grok Bot early for each run that ends, then once more when the last one ends.
- With the mode off: a notification and a log line, but no wake.

## 8. Safety layers

```mermaid
flowchart LR
  REQ[launch request] --> GATE["mod gate<br/>(mode on? typed run refused)"]
  GATE --> GUARD["ck-run guards<br/>no bypass flags, write scopes, clean env"]
  GUARD --> BUD["ask budget<br/>exit 7"]
  BUD --> AND["andon<br/>exit 2 while raised"]
  AND --> CLM["claims<br/>exit 6 on overlap"]
  CLM --> RUN[agent runs]
  RUN --> RC["rule check<br/>raw folders, credentials, cloud sims"]
  RC -->|"4 flagged / 5 violation"| STOP["stop the chain: andon raise"]
  RC -->|"0 ok / 1 partial"| CARD[card]
```

- The agent gets a clean environment: no keys or tokens.
- Each agent runs in its own safety-reviewed auto mode; ck-run adds the flags. Nobody else may pass them.
- Raw data folders and rule files are protected (per workspace, in `config/workspaces.json`).
- Exit codes: 0 ok · 1 partial · 2 refused · 3 failed/timeout/stalled · 4 flagged · 5 violation · 6 busy · 7 over budget.

## 9. Install layout

```mermaid
flowchart LR
  subgraph repo["this repo"]
    C1[core/ck-dispatch]
    C2[core/ckstack]
    C3[core/grokbot-mod]
    C4[core/skills]
    S1[setup/windows]
    S2[setup/common]
  end
  subgraph home["WSL home (or Mac home)"]
    H1["~/PhD_local/ck-dispatch"]
    H2["~/PhD_local/ckstack"]
    H3["~/PhD_local/grokbot-mod"]
    H4["~/PhD_local/grok-bot-skills"]
    H5["~/PhD_local/agent_runs<br/>(runs, ledger)"]
    H6["~/.local/bin/ck-run, ck-open<br/>~/.ck_shortcuts.sh"]
    H7["~/.claude/settings.json<br/>plugins + prefs"]
  end
  subgraph win["Windows side"]
    W1["%USERPROFILE%\.local\bin\*.cmd"]
    W2["%USERPROFILE%\.config\herdr-app"]
  end
  C1 --> H1
  C2 --> H2
  C3 --> H3
  C4 --> H4
  S1 --> H6
  S1 --> W1
  S1 --> W2
  S2 --> H7
```

- Setup **copies** `core/` and fills placeholders (`{{PHD_ROOT}}`, `{{WIN_USER}}`, ...). The repo stays clean.
- `agent_runs/` (ledger, run folders, locks) stays local, off OneDrive.
- `archive/` is never installed.

## 10. Files ck-run keeps

| Path (under `~/PhD_local/agent_runs/`) | What |
|---|---|
| `ledger.jsonl` | every event: asks, launches, results, stalls, andon |
| `<run id>/` | one run: packet, prompt, result.md / result.json, summary.md |
| `<slug>.sh`, `<slug>.out`, `<slug>_prompt.md` | a launch: its script, its output (last line `ck-run exit=N`), its task |
| `.windows/<ask id>.json` | the live window of an ask |
| `.andon/<name>.json` | a raised andon |
| `.claims/` | live runs and the paths they claim |
| `grokbot_standin_log.md` | the mod's launch log |
