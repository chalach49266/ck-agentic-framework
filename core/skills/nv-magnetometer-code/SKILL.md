---
name: nv-magnetometer-code
description: >-
  Use for NV compact magnetometer code, notebooks, ODMR and lock-in experiments,
  nv_toolkit, B-field reconstruction, sensitivity estimates, or verified
  performance numbers.
---
# NV magnetometer code and experiments
Project: NV Compact Magnetometer/nv_magnetometer_project in the owner's PhD folder on their Mac; code edits happen in the local copy at ~/PhD_local.
System: NV-center magnetometer on RFSoC4x2 plus qick-dawg (lock-in ODMR sweeps, two-point and four-point lock-in, MultipointLockinODMR parked acquisition, B-field reconstruction via nv_toolkit).

1. Read nv_magnetometer_project/README.md, then the parent CLAUDE.md and NV Project wiki (index.md, wiki/maps/ai_retrieval_guide.md).
2. Scope: Modules/, notebooks/, notebook_modules/, nv_toolkit, phase1, scripts, analysis, sensitivity estimates, figures.
3. Every notebook keeps its PROJECT_ROOT setup cell. Modules/Detection/V2 notebooks are generated; never hand-edit them.
4. data/** stays local; raw measured CSVs are authoritative and never altered.
5. Use the pinned qickdawg_venv (Python 3.13) from requirements.txt; no venvs or clones inside OneDrive.
6. Edit code only when the owner asks, test changes, preserve uncertainty (current figures are uncalibrated).
7. Give AQS work only verified numbers traced to measured data. File valuable findings into the NV Project wiki with a log.md entry.
8. Heavy code work can go to Claude Code, Codex or Cursor via their prompt skills, started in the NV Compact Magnetometer folder.
