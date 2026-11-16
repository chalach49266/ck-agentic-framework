---
name: fab-records
description: >-
  Use for fabrication recipes, fab run logs, ESEM images, and measurement
  results in the PhD Device Fabrication workspace, including comparing intended
  versus actual process settings.
---
# Fab records (Device Fabrication)
Workspace: {{PHD_ROOT}}/Device Fabrication on the owner's Mac.

1. Read .agents/AGENTS.md, then the Design Library wiki: index.md, maps/ai-retrieval-guide.md, the fabrication and experiments pages, and questions/open-questions.md.
2. Sources: Fabrication/, Projects/ESEM, Projects/Result. Summarize runs and compare intended versus actual settings.
3. Recipe packages are authoritative for intended settings; run-specific experiment pages for what was actually done.
4. ESEM supports morphology and lateral CD but never proves etch depth without cross-section, step-height or AFM data.
5. Preserve uncertainty; never turn estimates into confirmed facts.
6. Raw folders are read-only unless asked. Keep Design Library/fabrication and experiments pages current and append to log.md.
7. After moving or renaming anything, run python3 "Design Library/_tools/check_paths.py". Cite wiki pages used.
