---
name: PhD wiki rules
description: Use for any question or task about the owner's PhD work in Device Fabrication (Design Library wiki) or NV Compact Magnetometer (NV Project wiki), including AQS startup material.
---
# PhD wiki rules (from the workspaces' AGENTS.md and CLAUDE.md)

Base on the user's Mac: `{{PHD_ROOT}}`. Rule files: Device Fabrication `.agents/AGENTS.md` (canonical), `.cursor/AGENTS.md`, root `CLAUDE.md`, schema `Design Library/CLAUDE.md`. NV Compact Magnetometer: root `CLAUDE.md` plus schema `NV Project/CLAUDE.md`. Since 2026-10-31 both workspaces also have pointer `AGENTS.md` files (Device Fabrication root; NV root and `NV Project/`). They send Codex, Cursor and agy to the CLAUDE.md files and repeat the hard rules; the CLAUDE.md files win if they conflict. Re-read the relevant file before changing wiki structure.

## Ownership
- Agents own the wiki files (`Design Library/`, `NV Project/`). The human owns raw sources; they are read-only unless the user explicitly asks.
- Don't leave important synthesis only in chat: file it into the owning page and append to `log.md` as `## [YYYY-MM-DD] <type> | <title>` (types: ingest, query, lint, update, experiment, graph-cleanup, reorganization).

## Answering a question
1. Read the wiki `index.md`, then the retrieval guide (`Design Library/maps/ai-retrieval-guide.md` or `NV Project/wiki/maps/ai_retrieval_guide.md`).
2. Read one domain or authority map (NV: `workspace_source_map` or `experiment_pipeline_map`) and one or two owner pages. Aim for about three pages; only scan raw folders or tool repos when the wiki lacks the detail.
3. For how-to-run / tool questions check the tools-and-skills map first.
4. Check open questions (`Design Library/questions/open-questions.md`, `NV Project/wiki/questions/open_questions.md`) before calling anything validated.
5. Answer citing the wiki pages used; if non-trivial, update the owner page and log.

## Source of truth
- Device Fabrication: executed scripts/notebooks/manifests > generated GDS and KLayout/BEAMER > run-specific fab/experiment pages > simulations > overview/maps > ideas, literature, pitches. GDS proves an output exists, not current parameters. Recipe packages = intended settings; run pages = what was actually done. ESEM shows morphology and lateral CD, not etch depth without cross-section/AFM/step height. Simulation is not measurement; no microwave structure has been fabricated or measured.
- NV: raw measured CSVs and code in `nv_magnetometer_project/` are authoritative for what was measured; `data_inventory` for data counts and trust; experiment pages for what a branch supports; `experiment_pipeline_map` for whether evidence supports a claim. Slides, reports, patents, proposals (including AQS) are communication layers, never stronger than data.
- Preserve uncertainty; never turn targets, estimates or candidate events into confirmed facts.

## Never
- Run Tidy3D or Flexcompute RF (cloud credits) without an explicit go-ahead.
- Put git clones, venvs or node_modules in OneDrive (heavy trees live in `~/PhD_local/` as symlinks).
- Use Device Fabrication `.venv/bin/python` (broken); use `px run forge` or `px doctor`. NV env: `qickdawg_venv` (Python 3.13); `qickdawg_py310` is broken.
- Leave dangling wikilinks or wikilink raw files (put raw paths in backticks); avoid all-to-all link lists.
- Clutter the NV root (only folders, CLAUDE.md, Workspace Graph Index.md, the mag CLI pair).

## Tools
- Photonics: `Photonics_Ecosystem/bin/px` (`px doctor`, `px run layout|meep|forge script.py`).
- Microwave: `Microwave_Ecosystem` `mw`/nvmw; choose a solver with `mw route` before running, solve each geometry once; tests `bin/mw-test`; runs go to `~/mw_runs/`.

## After changes
- Moves/renames: `python3 "Design Library/_tools/check_paths.py"` or `python3 "NV Project/_tools/check_paths.py"`, then `build_graph_index.py`.
- Skill edits: edit the canonical `.agents/skills/` copy, then `sync_skills.py --apply`.
- Cloud sync truth: `python3 "Device Fabrication/Design Library/_tools/onedrive_sync_check.py"` (Finder badges can lie).
- New wiki pages need the frontmatter (title, type, tags, source_count, last_updated), a 2-4 sentence summary, a link to a map/hub, and an index entry.
