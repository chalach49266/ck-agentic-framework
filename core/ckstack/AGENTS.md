# AGENTS.md (ckstack)

For Codex, and any agent that reads AGENTS.md. ckstack is the owner's rulebook for ck-run work.

## ck-run started you (a worker)
Read `~/PhD_local/ckstack/agents/ck-worker.md` first. Then read the playbook and the domain skills that your task
file names: `~/PhD_local/ckstack/playbooks/<name>.md`, `~/PhD_local/grok-bot-skills/<name>/SKILL.md`.
The header ck-run gave you (MODE, READ-ONLY, HARD RULES, OUTPUT CONTRACT) wins over these files.

## You route the owner's asks (the Grok Bot role)
Read `~/PhD_local/ckstack/ck-mode/SKILL.md`. Start agents only through ck-run
(`~/PhD_local/ck-dispatch/bin/ck-run`).

## You edit ckstack itself
- Keep files short: ck-mode about 120 to 180 lines, the principles about one page, a playbook 20 to 45 lines,
  a skill 15 to 40 lines.
- Plain, short English: the owner reads English as a second language. No invented numbers: TODO(verify).
- Every ck-run command must match `~/PhD_local/ck-dispatch/docs/v4.md` and `ck-run <command> --help`.
- Aliases, tiers and lanes come from `~/PhD_local/ck-dispatch/config/models.json`. Change `models.md` and the lane
  table in `ck-mode/SKILL.md` together.
- A new rule that a check enforces gets a row in the table in `README.md`.
- Third-party ideas: rewrite them in your own words and credit them in `LICENSE-THIRD-PARTY.md`.
