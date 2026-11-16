---
name: microwave-autodesign-loop
description: >-
  Device Fabrication: use to iterate a microwave structure through the full mw
  agent loop (edit design.py, check layout, route solver, simulate, log, keep or
  discard).
---
# microwave-autodesign-loop (Device Fabrication)
The full recipe lives on the owner's Mac (machine {{MACHINE_ID}}) at `{{PHD_ROOT}}/Device Fabrication/.agents/skills/microwave-autodesign-loop/` (mirrored in .claude/skills and .cursor/skills).
1. Read that folder's SKILL.md and any helper files it names, and follow it.
2. Also follow .agents/AGENTS.md and the Design Library wiki-first rules (phd-wiki-rules skill).
3. Never run Flexcompute or Tidy3D cloud jobs without the owner's explicit go-ahead. Raw folders read-only, no clones or venvs in OneDrive, no invented numbers.
4. When handing work to Claude Code, Codex or Cursor, start them in the Device Fabrication folder; they read the same file.
