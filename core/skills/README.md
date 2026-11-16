# Grok Bot skills

Top-level folders: my registered Grok Bot skills (one SKILL.md each). The Device Fabrication ones point to the originals in the workspace.

## Agent delegation (through `~/PhD_local/ck-dispatch/bin/ck-run`, v4 since 2026-11-05)

- `ck-delegate/`: one ask per request (`ck-run ask open`, sizes S/M/L with budgets ck-run counts, exit 7 = over budget), models by lane (`ck-run route --lane`), detached launches (`ck-run launch`), race, panel and loop, a review only with a reason (`--trigger`), and one finish card per ask (`ck-run ask close`); summaries only.
- `claude-code-prompt/`: run a task in Claude Code (claude: opus, opus-max, sonnet, haiku).
- `codex-prompt/`: run a task in Codex (codex: sol, sol-fast, astra).
- `cursor-agent-prompt/`: run a task in the Cursor CLI agent (agent: grok, composer).
- `antigravity-prompt/`: run a task in Antigravity (agy: gemini).

All four prompt skills use ck-run's auto mode by default (the owner 2026-11-02): each agent's own safety-reviewed auto mode, injected by ck-run. They never pass skip-permissions, yolo, force, full-access or any permission flag themselves, and they edit only inside the write scope. Since 2026-11-05 there is no automatic Claude review after cursor and agy runs; the rule check still runs.

The router that picks size, pattern, playbook and models is ckstack: `~/PhD_local/ckstack/ck-mode/SKILL.md`. ck-run guide: `~/PhD_local/ck-dispatch/docs/v4.md`.

## PhD rules and tools

- `phd-wiki-rules/`: wiki-first rules for Device Fabrication and NV Compact Magnetometer.
- `fab-records/`, `microwave-design/`, `nv-magnetometer-code/`, `photonics-design/`: Grok Bot domain skills.
- Device Fabrication skills (point to the workspace originals): `flexcompute-rf`, `gdsfactory-design`, `gdstk-design`, `meep`, `microwave-autodesign-loop`, `microwave-gds-design`, `microwave-solver-selection`, `openems`, `palace`, `phido-design`, `phido-photonics-library`, `photonforge-autodesign-loop`, `photonforge-gds-design`, `photonforge-gds-validation`, `photonforge-live-viewer`, `photonforge-pdk-library`, `photonforge-repo-maintenance`, `photonics-tool-selection`, `qucs-s`, `tidy3d`, `tidy3d-workspace`.

`device-fabrication-originals/`: full copies of Device Fabrication/.agents/skills (snapshot).

OpenClaw general-purpose skills in the NV folder are intentionally not included.

## Claude Code stand-in (2026-11-04, v4 2026-11-05)

When Grok usage is out, the owner types `/grokbot` in Claude Code: Claude follows these same skills as CK.
Playbook and mod: `~/PhD_local/grokbot-mod/` (`GROKBOT.md` v4, one page; the v3 text is kept in `GROKBOT_v3_2026-11-05.md`).
Router logs: `~/PhD_local/grokbot_router/`. Framework: `PhD/AI_Agent_Framework/AI_Agent_Delegation_Framework_v4.md`.
