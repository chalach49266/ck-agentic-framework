---
name: photonics-tool-selection
description: >
  Use FIRST for any photonics layout, simulation, viewing or optimisation task in the Device
  Fabrication workspace: decides between gdsfactory, PhotonForge and gdstk for layout; the
  Tidy3D local mode solver, MEEP (local FDTD), Tidy3D cloud FDTD and PhotonForge circuit
  models for simulation; KLayout/klive and the PhotonForge LiveViewer for viewing; and which
  Python runtime runs each one (`px`). Trigger phrases: "which tool", "which solver",
  "photonics simulation", "mode solve", "MEEP or Tidy3D", "coupling gap", "ring Q",
  "photonic layout", "run this script", "which python", "px", "Photonics_Ecosystem".
---

# Photonics tool selection

The photonics counterpart of `microwave-solver-selection`. Tools here are **lanes, not
duplicates**: pick one per task, say why, and do not run a second tool to recompute a result
the first already gave. Validate against an analytic estimate, not against another solver.

Root (call it `PE`):
`{{PHD_ROOT}}/Device Fabrication/Photonics_Ecosystem`.
Wiki route: `Design Library/sources/photonics-ecosystem.md`.

## Runtimes: `px`

```bash
"$PE/bin/px" doctor                       # every runtime, viewer and source clone, with versions
"$PE/bin/px" run layout script.py         # conda env gdsfactory: gdsfactory, gdstk, klayout, PhotonForge 1.4.7, Tidy3D client
"$PE/bin/px" run meep script.py           # conda env meep-fdtd: MEEP 1.33, meep.adjoint, MPB, nlopt
"$PE/bin/px" run forge script.py          # Anaconda python + .venv packages: PhotonForge 1.5.0 + SiEPIC / Luxtelligence PDKs
"$PE/bin/px" klive chip.gds               # push a GDS to a running KLayout (klive, port 8082)
```

The project `.venv/bin/python` exits silently (OneDrive flattened its symlinks). `px run forge`
runs Anaconda's interpreter (the venv's own base) with `-S` and loads only the `.venv`
packages, so Anaconda's NumPy-1.x builds of pyarrow, numexpr and bottleneck stay out. The
older `PYTHONPATH=.venv/... python3` route works but prints NumPy-ABI tracebacks on import. No runtime imports from the source clones under
`$PE/repos/`: they are a knowledge base (read, search, cite).

## Lanes

| Task | Lane | Runtime | Cost |
| --- | --- | --- | --- |
| Parametric CK / FND chip layout, routing, test masks | gdsfactory | `layout` | free |
| Foundry PDK cells (SiEPIC Si / SiN, Luxtelligence LNOI / LTOI) | PhotonForge + PDK | `forge` | free |
| Polygon booleans, GDS readback, layer and datatype checks | gdstk, `klayout.db` | `layout` | free |
| Look at a layout | KLayout + klive (`px klive`, `c.show()`), or the PhotonForge LiveViewer | `layout` / `forge` | free |
| First estimate: effective index, coupling length, FSR, critical coupling | closed form / coupled-mode theory | any | free |
| n_eff, n_g, mode area, mode overlap, bend modes | Tidy3D local mode solver: `ModeSolver(...).solve()` | `layout` | free, local |
| Gap / coupling sweep, ring transmission, Q, 2D device behaviour | MEEP 2D | `meep` | free, local |
| 3D behaviour where 2D is not enough | MEEP 3D (local, slow) | `meep` | free, local |
| Large 3D FDTD, many 3D runs | Tidy3D cloud (`web.run`) | `layout` | **credits: explicit approval** |
| S-matrix of PDK cells and circuits | PhotonForge models: the analytic ones (`AnalyticWaveguideModel`, `AnalyticDirectionalCouplerModel`, `RingModel`, `CircuitModel`, ...) run locally; `Tidy3DModel` (FDTD) and `EMEModel` run on the Tidy3D cloud | `forge` | local, or **credits: approval** |
| Inverse design | MEEP adjoint (`meep.adjoint`, local) or PhIDO; Tidy3D adjoint is cloud | `meep` | local or credits |
| Iterative keep / discard optimisation | `photonforge-autodesign-loop` template | - | depends on the solver |

Notes on two of the lanes:

- `ModeSolver.solve()` computes locally and prints a warning that the cloud mode solver has
  subpixel averaging. To get subpixel averaging locally, install `tidy3d[extras]` and set
  `config.simulation.use_local_subpixel = True`. `td.web.run(mode_solver)` is the cloud path.
- Tidy3D in the `layout` env prints config warnings at import (`~/.tidy3d` is a removed legacy
  location and `~/.config` is not writable). They are harmless; the API key comes from
  `SIMCLOUD_APIKEY` in `~/.zshenv`.

## Order of escalation

```text
closed form -> local mode solver -> MEEP 2D -> MEEP 3D -> Tidy3D cloud (approval)
```

Move up a rung only when the cheaper one cannot answer the question, and say which question
it could not answer.

## Rules

- **No Tidy3D cloud run without the user's explicit approval**, every time.
- **The user runs new or redone simulations.** Hand over a notebook (cached outputs, `RUN` and
  `NPROC` switches, a how-to-read section) instead of launching a batch in-session. Post-
  processing cached results is fine. Never regenerate a notebook the user has executed.
- Scripts and executed notebooks own geometry; a GDS proves an output exists, not that its
  parameters are current.
- Simulated is not fabricated, and fabricated is not measured.
- Read the owner page in `Design Library/` before touching a design family.

## Where the knowledge lives

| Need | Read |
| --- | --- |
| gdsfactory API, examples | `$PE/repos/gdsfactory` (`docs/llms.txt`), `$PE/repos/gdsfactory7/notebooks` |
| Tidy3D API, agent notes | `$PE/repos/tidy3d/AGENTS.md`, `llms.txt`; example notebooks in `$PE/notebooks/Tidy3D-notebooks` |
| MEEP | `$PE/repos/meep` (docs and `python/examples`) |
| PhotonForge PDKs and the design-loop reference | `$PE/repos/siepic-forge`, `luxtelligence-forge`, `autophotonicdesign` |
| PhIDO | `$PE/repos/phido` |

Related skills: `meep`, `tidy3d`, `gdsfactory-design`, `gdstk-design`, `phido-design`,
`photonforge-gds-design`, `photonforge-pdk-library`, `photonforge-live-viewer`,
`photonforge-autodesign-loop`, `microwave-solver-selection`.
