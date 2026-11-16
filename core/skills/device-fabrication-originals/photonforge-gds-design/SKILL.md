---
name: photonforge-gds-design
description: Use when designing, editing, or generating GDS/OASIS layouts with PhotonForge in the Device Fabrication workspace, especially CK/FND/SiN photonic components, positive-resist layouts, PDK-backed layouts, parametric component construction, PhotonForge paths/components/references/booleans, or requests mentioning PhotonForge GDS design.
---

# PhotonForge GDS Design

Use this skill to build PhotonForge layouts that can survive fabrication handoff. It is compatible with Codex and Claude Code because the core workflow is in this `SKILL.md` and optional helpers are plain scripts.

## First Read

1. `Design Library/tools/photonforge.md`
2. `Design Library/tools/siepic-forge.md` if a PDK is involved
3. `Design Library/concepts/positive-resist-layout.md` for writer-layer logic
4. `Projects/CK Design/Elliptical Ring/CK008_photonforge_ring_variants.py`
5. `references/workflow.md` when a new PhotonForge source file is needed

## Workflow

1. Run PhotonForge with `PYTHONPATH=".venv/lib/python3.12/site-packages" /opt/anaconda3/bin/python3`, not default Anaconda Python alone. As of 2026-09-10 `.venv/bin/python` is NOT an interpreter -- OneDrive flattened the venv symlinks into plain text files, so it produces no output and exits 0 instead of erroring, and anything run that way only looks verified. See `Design Library/tools/photonforge.md`.
2. Confirm `import photonforge as pf` reports PhotonForge 1.5.0 or newer.
3. Choose plain PhotonForge geometry or a PDK from `photonforge-pdk-library`.
4. Centralize dimensions in a dataclass or a small parameter block.
5. Keep staging geometry separate from final writer geometry when using positive resist.
6. Write GDS/OASIS only after building an in-memory smoke test.
7. Produce or update a preview image whenever the layout is fabrication-facing.
8. Run `photonforge-gds-validation` before treating the GDS as handoff-ready.

## Local Patterns

- For positive-resist subtraction, use the CK008 pattern: broad field minus protected keepout.
- Use `pf.Path`, `pf.Circle`, `pf.Rectangle`, `pf.Component`, `pf.Reference`, `pf.boolean`, and `pf.write_layout` for project-local geometry.
- For PDK components, activate a technology first, then instantiate components from the selected PDK module.

## Guardrails

- Generated GDS proves output existence, not optical performance.
- Do not mix project-local layer conventions with PDK layers without an explicit map.
- Do not spend Tidy3D cloud simulation until geometry preview and layer validation pass.
- Record new source scripts and generated files in the relevant Design Library owner page.

## Helpers

- `scripts/photonforge_env_report.py`: reports PhotonForge, Tidy3D, and installed PDK versions.
- `references/workflow.md`: concise layout workflow and code skeleton.
