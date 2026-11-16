---
name: flexcompute-rf
description: >
  Use when the user asks about Flexcompute RF / Flex RF / Tidy3D RF (cloud GPU full-wave RF
  solver): TerminalComponentModeler, lumped and wave ports, 2D transmission-line analysis,
  antenna far-field metrics, GDS / ODB++ / STEP import, RF material library, RF-photonic
  co-design such as modulator electrodes. Trigger phrases: "Flexcompute RF", "Flex RF",
  "flex_rf", "Tidy3D RF", "TerminalComponentModeler", "wave port", "DirectivityMonitor",
  "RF photonics", "CPW electrode", "travelling-wave electrode". Every solve spends cloud
  credits: never run one without the user's explicit approval. Check
  `microwave-solver-selection` first; the local lanes cover most work.
---

# Flexcompute RF skill

Flexcompute RF is a GPU-parallel full-wave RF solver that runs **in the cloud**. In this
workspace it is a documented, routed capability that is **not run by default**: the
standing rule is no Tidy3D cloud credits without an explicit go-ahead. The local lanes
(closed form, sheet solver, Palace, openEMS, Qucsator-RF) come first.

## What it offers (from the product page, 2026-10)

- 2D layout import (ODB++, GDSII) and 3D CAD import (STEP, STL)
- RF materials library, automated mesh generation
- Wave ports with automatic impedance calculation
- Lumped ports and elements compatible with SPICE, Touchstone and circuit models
- Arbitrary field and voltage / current probes
- 2D transmission-line analysis; 3D full-wave device S-parameters
- Far-field analysis with antenna metrics
- A shared geometry and material stack with PhotonForge for RF-photonic co-design
  (Mach-Zehnder modulator electrodes, microring modulator electrodes, SMA-to-CPW
  transitions, power dividers, antenna arrays)

Product page: `https://www.flexcompute.com/flexcompute-rf/`.
Docs: `https://docs.flexcompute.com/rf/latest/` (examples under `/examples/`).

## Where to read

| Source | Where |
| --- | --- |
| Live docs | the `tidy3d` MCP tools `search_flexcompute_docs` / `fetch_flexcompute_doc` with `package="flex-rf"` |
| Client source | `Device Fabrication/Photonics_Ecosystem/repos/tidy3d/tidy3d/plugins/microwave`, `.../components/microwave`, `.../plugins/smatrix` |
| RF example notebooks | `Device Fabrication/Photonics_Ecosystem/notebooks/Tidy3D-notebooks/tidy3d-notebooks-develop/`: `GroundedCPWViaFence`, `CPWRFPhotonics1`, `CPWRFPhotonics2`, `DifferentialStripline`, `HybridMicrostripCPWBandpassFilter`, `CoupledLineBandpassFilter`, `SMAEdgeMount`, `LinearLumpedElements`, `MicroringRFElectrode`, `EdgeFeedPatchAntennaBenchmark`, `CircularlyPolarizedPatchAntenna`, `PlanarHelicalAntennaArray`, `IntegratedVivaldiAntenna`, `AntennaCharacteristics`, `RFParameterSweep`, `RFAutograd1RectangularPatchAntenna`, `ThroughSiliconVia` |
| RF agent-loop reference | branch `rf_transmission_lines` of `Photonics_Ecosystem/repos/autophotonicdesign` (T-rail CPW electrode on thin-film lithium tantalate) |

## Core objects (docs v0.1.0)

- `TerminalComponentModeler`: runs one simulation per port and returns the S-matrix.
  `ports` takes lumped and wave ports; `radiation_monitors` adds antenna metrics;
  `run_only` and `element_mappings` skip redundant columns; `s_param_def` is `"pseudo"`
  (default, Marks and Williams), `"power"` (Kurokawa) or `"symmetric_pseudo"`.
- Wave port to 2D analysis: `port.to_mode_solver(simulation=sim, freqs=...)`, then
  `web.run(...)`. Results: `mode_data.modes_info["n eff"]`, `["loss (dB/cm)"]`,
  `mode_data.transmission_line_data.Z0`. **This 2D solve is also submitted to the cloud.**
- `DirectivityMonitor` in `radiation_monitors`, then `tcm_data.get_antenna_metrics_data()`:
  `directivity`, `gain`, `realized_gain`, `radiation_efficiency`, `reflection_efficiency`,
  `axial_ratio`, `partial_gain(pol_basis="circular")`.
- Phase convention is the physics one: take `-np.conjugate(gamma)` and
  `np.conjugate(Z0)` to compare with engineering-convention tools (openEMS, Qucs, Palace
  S-parameters).

Confirm any signature against the live docs before writing code: the API is young.

## When it is the right lane

- The problem is too large for this machine (package-scale boards, long travelling-wave
  electrodes, antenna arrays), or
- RF and optical models must share one PhotonForge geometry and stack.

For an NV microwave structure of chip or small-board size, the local lanes are faster to
iterate and free.

## Before any run

1. Say what will be submitted, how many simulations (one per port), and that it spends
   credits. Wait for an explicit yes.
2. Check the geometry locally first: preview, DRC, and where possible a coarse local solve.
3. Estimate cost before submitting (`web.estimate_cost` on the uploaded task).
4. Record the task id and cost with the result.

Related skills: `microwave-solver-selection`, `tidy3d`, `photonforge-gds-design`.
