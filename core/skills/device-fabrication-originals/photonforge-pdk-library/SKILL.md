---
name: photonforge-pdk-library
description: Use when selecting, installing, importing, probing, or designing with PhotonForge PDKs in this workspace, including SiEPIC Si, SiEPIC SiN, Luxtelligence LNOI400, Luxtelligence LTOI300, foundry technology activation, component discovery, PDK component names, and PDK-backed GDS generation.
---

# PhotonForge PDK Library

Use this skill when PhotonForge design should use a foundry or public PDK instead of only primitive shapes.

## Installed PDKs

| PDK | Package | Module | Technology factory | Component access |
| --- | --- | --- | --- | --- |
| SiEPIC EBeam Si | `siepic-forge` | `siepic_forge` | `ebeam()` | `component(name)`, `component_names` |
| SiEPIC EBeam SiN | `siepic-sin-forge` | `siepic_sin_forge` | `ebeam()` | `component(name)`, `component_names` |
| Luxtelligence LNOI400 | `luxtelligence-lnoi400-forge` | `luxtelligence_lnoi400_forge` | `lnoi400()` | `component`, `component_names` |
| Luxtelligence LTOI300 | `luxtelligence-ltoi300-forge` | `luxtelligence_ltoi300_forge` | `ltoi300()` | `component`, `component_names` |

## First Read

1. `Design Library/tools/siepic-forge.md`
2. `Design Library/tools/photonforge.md`
3. `Photonics_Ecosystem/README.md`
4. `references/pdk-index.md`

## Workflow

1. Run `scripts/probe_pdk_imports.py` to confirm imports and component access.
2. Pick the PDK by material and process intent, not by component availability alone.
3. Set `pf.config.default_technology` before creating PDK components.
4. Print or inspect `component_names` before guessing a component name.
5. For project SiN/CK/FND work, prefer SiEPIC SiN only after checking layer/process assumptions against the Device Fabrication process pages.
6. For LNOI/LTOI work, treat Luxtelligence design rules as external and contact-required; use the packages for technology/component examples, not as verified foundry permission.

## Guardrails

- PDK components do not validate the local fabrication process.
- PDK layer stacks may not match IMSE/SiN process assumptions.
- Do not combine PDK and hand-authored project layers without a written mapping.
- Always run `photonforge-gds-validation` on exported layouts.

## Helpers

- `scripts/probe_pdk_imports.py`: import and component-name probe.
- `references/pdk-index.md`: package/module/import summary.
