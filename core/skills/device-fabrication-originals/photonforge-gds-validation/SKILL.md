---
name: photonforge-gds-validation
description: Use when checking, inspecting, validating, or reviewing PhotonForge-generated GDS/OASIS files, layer/datatype contents, cell hierarchy, bounding boxes, PDK exports, positive-resist writer layers, CK/FND mask handoff readiness, or before BEAMER/KLayout/fabrication use.
---

# PhotonForge GDS Validation

Use this skill before trusting any PhotonForge-generated file as a fabrication or simulation handoff artifact.

## First Read

1. `Design Library/methods/design-to-fabrication-workflow.md`
2. `Design Library/tools/photonforge.md`
3. `Design Library/tools/klayout-klive.md`
4. `Design Library/concepts/positive-resist-layout.md` for positive-resist files
5. `references/validation-checklist.md`

## Workflow

1. Confirm the source script, parameter block, and generated GDS path.
2. Run `scripts/inspect_gds.py <path-to-gds>`.
3. Check top cells, bounds, layer/datatype inventory, and empty-cell risks.
4. Confirm final writer layers match the intended process.
5. For positive-resist layouts, verify staging layers are not confused with the final exposure layer.
6. Open or preview the layout before simulation or BEAMER.
7. Update the owning design/tool page if the file becomes a new source of truth.

## Pass Criteria

- Source script exists and can regenerate the GDS.
- GDS can be read by an independent tool.
- Top cell and bounding box are expected.
- Layer/datatype set is expected.
- Preview or KLayout inspection is clean.
- No optical-performance claim is made from GDS alone.

## Helpers

- `scripts/inspect_gds.py`: uses `gdstk` if available, with a PhotonForge fallback.
- `references/validation-checklist.md`: handoff checklist.
