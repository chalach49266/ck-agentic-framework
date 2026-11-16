---
name: photonics-design
description: >-
  Use for photonic layout or simulation work in the PhD Device Fabrication
  workspace: gdsfactory, gdstk, PhIDO, PhotonForge, MEEP, Tidy3D, GDS
  validation.
---
# Photonics design (Device Fabrication)
Workspace: {{PHD_ROOT}}/Device Fabrication on the owner's Mac.

1. Read .agents/AGENTS.md, then the Design Library wiki: index.md, maps/ai-retrieval-guide.md, one domain map and owner page, and questions/open-questions.md before treating any design as validated.
2. Pick tools with the photonics-tool-selection skill in .agents/skills, then follow the matching skill (gdsfactory-design, photonforge-*, meep, tidy3d, phido-*). Use Photonics_Ecosystem/ and bin/px (px doctor, px run layout|meep|forge).
3. Python scripts and executed notebooks are authoritative for geometry; a GDS only proves an output exists.
4. Never run Tidy3D (cloud credits) without the owner's explicit go-ahead.
5. Raw folders (Projects/, Fabrication/, Paper/) are read-only unless asked. No clones or venvs inside OneDrive.
6. File useful syntheses back into the Design Library with a log.md entry. Cite wiki pages used and preserve uncertainty.
7. Heavy coding or simulation runs can be handed to Claude Code, Codex or Cursor with the claude-code-prompt, codex-prompt or cursor-agent-prompt skills, started in the Device Fabrication folder.
