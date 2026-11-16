# PhotonForge GDS Validation Checklist

## Required Checks

- Source script exists.
- Active PhotonForge environment imports.
- GDS exists and has nonzero size.
- Independent GDS read succeeds.
- Top cells are expected.
- Bounding box is plausible.
- Layer/datatype inventory matches the intended write.
- Positive-resist final layer is not confused with staging layers.
- Preview or KLayout inspection exists for fabrication-facing layouts.

## Report Format

```text
file:
source:
top cells:
bounds:
layers:
warnings:
handoff status:
```
