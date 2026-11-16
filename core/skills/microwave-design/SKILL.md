---
name: microwave-design
description: >-
  Use for microwave or NV microwave structure work (antennas, resonators, CPWs)
  in the PhD Device Fabrication workspace: nvmw, openEMS, Palace, Qucs-S,
  Flexcompute RF.
---
# Microwave design (Device Fabrication)
Workspace: {{PHD_ROOT}}/Device Fabrication on the owner's Mac.

1. Read .agents/AGENTS.md, then the Design Library wiki: index.md, maps/ai-retrieval-guide.md, one domain map and owner page, and questions/open-questions.md.
2. Use Microwave_Ecosystem/, the nvmw tool, bin/mw and bin/mw-test.
3. Always pick a solver lane with `mw route` or the microwave-solver-selection skill before running, and solve each geometry once. Follow the matching skill in .agents/skills (microwave-gds-design, microwave-autodesign-loop, openems, palace, qucs-s, flexcompute-rf).
4. Solvers live in ~/opt/ and runs go to ~/mw_runs/, outside OneDrive.
5. Never run Flexcompute RF or Tidy3D (cloud credits) without the owner's explicit go-ahead. Microwave work is simulation-only so far.
6. Raw folders (Projects/Microwave Design, Fabrication/) are read-only unless asked. File useful syntheses into the Design Library with a log.md entry, cite wiki pages, preserve uncertainty.
