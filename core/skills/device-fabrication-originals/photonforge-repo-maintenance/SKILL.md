---
name: photonforge-repo-maintenance
description: Use when updating, cloning, refreshing, auditing, or summarizing the managed Photonics_Ecosystem source folder, including Flexcompute siepic-forge, autophotonicdesign, luxtelligence-forge, photonforge-view-tool, remote commit checks, fast-forward updates, or workspace graph routing for these repos.
---

# PhotonForge Repo Maintenance

Use this skill to keep `Photonics_Ecosystem/` as the single managed local mirror for PhotonForge-related upstream sources.

## Managed Folder

- Root: `Photonics_Ecosystem/`
- Repo manifest: `Photonics_Ecosystem/repos.tsv`
- Update script: `Photonics_Ecosystem/scripts/update_photonics_repos.sh`

## Workflow

1. Read `Photonics_Ecosystem/repos.tsv`.
2. Run `Photonics_Ecosystem/scripts/update_photonics_repos.sh`.
3. Report each repo as unchanged, updated, cloned, or skipped due to local changes.
4. If a source changed materially, update the relevant Design Library page.
5. If repo membership changes, update `Photonics_Ecosystem/README.md`, `repos.tsv`, `Design Library/data/workspace-inventory.md`, and `Workspace Graph Index.md`.

## Guardrails

- Never reset or discard local repo changes.
- Only fast-forward clean worktrees.
- Keep all PhotonForge ecosystem clones under `Photonics_Ecosystem/repos/`.
- Do not scatter new PhotonForge clones elsewhere in the Device Fabrication workspace.
- Keep package installs in project `.venv` and record dependency changes in `pyproject.toml`/`uv.lock`.

## Claude Compatibility

Claude Code can run the same update script and read the same manifest. Avoid relying on Codex-only memory; summarize changes into the wiki when they matter.
