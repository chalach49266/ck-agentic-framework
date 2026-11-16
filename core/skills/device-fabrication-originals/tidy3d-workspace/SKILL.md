---
name: tidy3d-workspace
description: >
  Use when working with the Flexcompute Tidy3D stack in this workspace: the local `Photonics_Ecosystem/repos/tidy3d/` Python
  client clone, Tidy3D notebooks, ring resonator and coupling simulations, ModeSolver / ModeMonitor
  setup, Q-factor extraction, EME, inverse design, or Flexcompute MCP docs lookup. Trigger phrases:
  "tidy3d", "Flexcompute", "FDTD", "EME", "ModeSource", "ModeMonitor", "ResonanceFinder",
  "web.run", "Photonics_Ecosystem/notebooks/Tidy3D-notebooks", "Projects/Simulation/tidy3D", "ring resonator simulation",
  "Q-factor", "coupling sweep".
---

# Tidy3D Workspace Skill

Workspace map for Tidy3D work in Device Fabrication: where the clone, notebooks and project simulations live, and the workflow rules. For the Tidy3D API itself use the `tidy3d` skill; for choosing between Tidy3D, MEEP and the mode solver use `photonics-tool-selection`.

Use this skill for Tidy3D work in this repository. It covers both:

1. **Local project simulations** in `Photonics_Ecosystem/notebooks/Tidy3D-notebooks/` and `Projects/Simulation/tidy3D/`
2. **The full upstream client clone** in `Photonics_Ecosystem/repos/tidy3d/`

## Where Tidy3D Lives In This Workspace

- **Upstream client clone**: `Photonics_Ecosystem/repos/tidy3d/`
- **Agent-facing repo summary**: `Photonics_Ecosystem/repos/tidy3d/llms.txt`
- **Repo workflow guidance**: `Photonics_Ecosystem/repos/tidy3d/AGENTS.md`
- **AI workflow docs**: `Photonics_Ecosystem/repos/tidy3d/docs/ai/simulation_tips.rst`, `Photonics_Ecosystem/repos/tidy3d/docs/ai/flex_agent.rst`
- **Project notebooks**: `Photonics_Ecosystem/notebooks/Tidy3D-notebooks/`
- **Project simulation notebooks**: `Projects/Simulation/tidy3D/`
- **Workspace wiki page**: `Design Library/tools/tidy3d.md`
- **Workspace source note**: `Design Library/sources/tidy3d-python-client-repo.md`
- **Existing Cursor rule**: `.cursor/rules/tidy3d-assistant.mdc`

## First Files To Read

Read only what you need, in this order:

1. `Photonics_Ecosystem/repos/tidy3d/llms.txt`
   Use first for fast orientation: key classes, plugins, workflows, failure modes.
2. `Design Library/tools/tidy3d.md`
   Use for workspace-specific context and notebook paths.
3. `Photonics_Ecosystem/repos/tidy3d/docs/ai/simulation_tips.rst`
   Use for simulation workflow rules and common mistakes.
4. `Photonics_Ecosystem/repos/tidy3d/README.md`
   Use for install, auth, docs links, MCP setup.
5. `Photonics_Ecosystem/repos/tidy3d/AGENTS.md`
   Use only when editing the upstream clone itself.

## Mandatory Workflow

### 1. Search official docs first

Use the Flexcompute MCP docs tools before writing or changing simulation code:

- `search_flexcompute_docs`
- `fetch_flexcompute_doc`

Search patterns that work well:
- `"ring resonator tidy3d"`
- `"ModeSource tidy3d"`
- `"ModeMonitor tidy3d"`
- `"parameter sweep batch tidy3d"`
- `"ResonanceFinder tidy3d"`

Break requests into:
- device
- figure of merit
- workflow type

### 2. Visualize before running

Never recommend running a simulation that has not been visually checked.

Inspect geometry with:

```python
sim.plot_eps(x=0)
sim.plot_eps(y=0)
sim.plot_eps(z=0)
```

Confirm:
- waveguides extend through PML
- sources are in straight sections
- monitors are placed where intended
- dimensions look physically sensible

### 3. Keep the physics explicit

- Do not guess `n_eff` when a mode solve can compute it.
- Do not suppress warnings.
- Do not hide `web.run()` failures behind broad `try/except`.
- Flag likely simulation cost when geometry or sweep size is large.

## Workspace-Specific Simulation Paths

### Core notebooks

- `Photonics_Ecosystem/notebooks/Tidy3D-notebooks/microring_resonator.ipynb`
- `Photonics_Ecosystem/notebooks/Tidy3D-notebooks/tidy3d_quickstart.ipynb`
- `Photonics_Ecosystem/notebooks/Tidy3D-notebooks/radius_sweep_corrected.py`

### Project notebooks

- `Projects/Simulation/tidy3D/tidy3d_ck000_circular_ring_sweep.ipynb`
- `Projects/Simulation/tidy3D/tidy3d_microring_coupling_transmission.ipynb`
- `Projects/Simulation/tidy3D/tidy3d_microring_mode_visualization.ipynb`
- `Projects/Simulation/tidy3D/tidy3d_general_mode_visualization.ipynb`

Use these first before inventing a new notebook from scratch.

## Common Tasks

### Ring resonator / coupling work

Typical goals:
- gap sweeps
- through/drop transmission
- linewidth extraction
- Q-factor estimation
- mode visualization in couplers or rings

Relevant concepts in the wiki:
- `Design Library/concepts/q-factor.md`
- `Design Library/concepts/coupling.md`

### Mode analysis

Use mode solving to:
- confirm TE/TM content
- compute effective index
- build `ModeSource` / `ModeMonitor` setups

### Q-factor extraction

Prefer one of:
- linewidth fitting from a transmission spectrum
- time-domain decay from `FieldTimeMonitor`
- `tidy3d.plugins.resonance.ResonanceFinder`

### Parameter sweeps

Prefer `web.run_async()` for batches when multiple independent simulations are needed.

## Repo-Level Work

If the task is about modifying the cloned `Photonics_Ecosystem/repos/tidy3d/` source itself:

1. Read `Photonics_Ecosystem/repos/tidy3d/AGENTS.md`
2. Follow `uv` workflows only
3. Reuse existing scripts and tests

Canonical commands:

```bash
cd tidy3d
uv sync --frozen --extra dev
uv run pre-commit run --all-files
uv run pytest -q tests/test_web/
```

## API / Version Notes

The local clone is on the `develop` branch and advertises version `2.11.0` in `pyproject.toml`.

Do not assume examples written against older workspace notes still reflect the current API. If you spot older patterns, verify against:
- `Photonics_Ecosystem/repos/tidy3d/llms.txt`
- official docs via MCP
- the current local source tree

## Plugin Surface To Remember

The local repo highlights these plugin families:
- `tidy3d.plugins.mode`
- `tidy3d.plugins.resonance`
- `tidy3d.plugins.smatrix`
- `tidy3d.plugins.invdes`
- `tidy3d.plugins.waveguide`
- `tidy3d.plugins.design`

## When Editing The Wiki

If a Tidy3D change should be reflected in the Design Library:

1. Update `Design Library/tools/tidy3d.md`
2. Add or refresh a page in `Design Library/sources/` if a new source was ingested
3. Update `Design Library/index.md` if a new page was added
4. Append an entry to `Design Library/log.md`
