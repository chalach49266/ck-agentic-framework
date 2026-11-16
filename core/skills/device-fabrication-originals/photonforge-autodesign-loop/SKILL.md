---
name: photonforge-autodesign-loop
description: Use when adapting, running, designing, or documenting autonomous photonic device optimization loops with PhotonForge, Tidy3D, KLayout DRC, preview images, journals, result TSVs, AutoPhotonicDesign, Claude Code, Codex, or iterative keep/discard design experiments.
---

# PhotonForge Autodesign Loop

Use this skill when a design should be improved through a controlled agentic loop rather than one-off manual edits.

## First Read

1. `Design Library/sources/autophotonicdesign-repo.md`
2. `Photonics_Ecosystem/repos/autophotonicdesign/README.md`
3. `Photonics_Ecosystem/repos/autophotonicdesign/program.md`
4. `Design Library/skills/simulation-workflow.md`
5. `references/loop-template.md`

## Loop Contract

Use this fixed shape unless the user asks for something different:

```text
principles -> design change -> preview -> DRC/layer check -> simulate -> log -> keep/discard
```

## Rules

- Keep the human-defined device target, constraints, and allowed edit region in a Markdown `program.md`-style file.
- Restrict agent edits to a small geometry function or source file section.
- Require preview and validation before cloud simulation.
- Count cloud simulations explicitly.
- Keep `output/principles.md`, `output/journal.md`, and `output/results.tsv` or an equivalent durable record.
- Never present an automated result as fabricated or measured unless physical evidence exists.

## Claude Compatibility

For Claude Code, keep task instructions in `program.md`, put project rules in `CLAUDE.md`, and keep the same preview/DRC/simulate/log gates. This skill avoids Codex-only tool assumptions.

## Local Adaptation Targets

- SiN bend or taper experiments from `autophotonicdesign` branches.
- CK0011/FND mode or coupling sweeps after the Tidy3D runtime is verified.
- PhotonForge PDK component exploration with `photonforge-pdk-library`.
