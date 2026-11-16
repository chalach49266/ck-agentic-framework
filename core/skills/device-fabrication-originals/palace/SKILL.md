---
name: palace
description: >
  Use when simulating with AWS Palace (open-source 3D finite-element electromagnetics,
  frequency domain): driven S-parameters with adaptive fast frequency sweeps, eigenmodes
  and Q of resonators, fields at probe points, lumped ports, finite-conductivity metal,
  meshing a GDS layout with gmsh, writing the JSON config, reading the CSV results.
  Trigger phrases: "Palace", "AWS Palace", "FEM microwave", "eigenmode", "resonator Q",
  "adaptive frequency sweep", "gmsh mesh", "lumped port FEM", "superconducting resonator",
  "CPW resonator simulation", "probe field". Check `microwave-solver-selection` first.
---

# Palace (finite-element) skill

Palace v0.18.1 (config schema 1-7-0), built from source on this machine.

| What | Where |
| --- | --- |
| Launcher and binary | `~/opt/palace/bin/palace` (wraps `mpirun`) |
| Installed config schema (authoritative) | `~/opt/palace/bin/schema/config-schema.json` |
| Source, docs, examples (knowledge base, pinned to v0.18.1) | `Device Fabrication/Microwave_Ecosystem/repos/palace` |
| Project wrapper | `Device Fabrication/Microwave_Ecosystem/nvmw/solvers/palace.py` |
| GDS-to-Palace reference flows | `Microwave_Ecosystem/repos/gds2palace`, `repos/gplugins/gplugins/palace` |
| Mesher | `gmsh` Python module in conda env `microwave` |

Docs to read in the clone: `docs/src/guide/*.md` (problem types, boundaries, post-processing),
`docs/src/reference.md` (formulas and normalisation), `docs/src/examples/*.md`,
example configs in `examples/cpw`, `examples/rings`, `examples/cavity2d`.

## When it fits

- Electrically small structures with thick or wide metal (current crowds to the edges).
- Resonators: frequency, loaded Q, field at resonance.
- Micron features on millimetre chips, curved geometry: the mesh conforms, and there is
  no time step to shrink.

Not for pulse response in time (use openEMS or an equivalent circuit).

## Through the project wrapper

```python
from nvmw import components
from nvmw.solvers import palace
d = components.omega_loop()
r = palace.run(d, mode="driven", out_dir="output")                       # one frequency: about 5 s
r = palace.run(d, mode="driven", freqs_hz=(2.3e9, 3.4e9, 201))           # adaptive sweep: about 17 s
# The pipeline solves at f0 only for structures under 0.03 wavelengths (router mode "driven-point")
# and fits R + jwL across the band: within 0.43 % of the swept figure of merit, about 4x faster.
r = palace.run(d, mode="eigenmode", n_modes=4, np_procs=6)               # modes and Q: minutes
r.freq, r.s, r.z_in_f0, r.rois[0].b      # B in tesla per sqrt(W) incident, (3, ny, nx)
r.extra["eig_f_GHz"], r.extra["eig_Q"]   # eigenmode results
```

Each run writes `model.msh`, `mesh.png` (look at it), `config.json`, `palace.log` and
`postpro/` under `~/mw_runs/<design>/<tag>/`.

## Running it directly

```bash
palace -np 4 config.json          # MPI processes; no OpenMP in this build
palace --dry-run config.json      # validate the config against the installed schema
```

**MPI on this laptop.** Set these in the environment or multi-process runs can fail with
"PML add procs failed" in `MPI_Init` after the machine changes network, because PMIx
advertises its server on the LAN address:

```bash
export PMIX_MCA_pif_base_retain_loopback=1 PMIX_MCA_ptl_base_if_include=lo0
```

The wrapper sets them. Do not add PRRTE loopback options: they break the launch.

## Config skeleton (verified against v0.18.1)

```json
{
  "Problem": {"Type": "Driven", "Verbose": 2, "Output": "postpro"},
  "Model": {"Mesh": "model.msh", "L0": 1e-6},
  "Domains": {
    "Materials": [{"Attributes": [1], "Permittivity": 1.0, "Permeability": 1.0},
                  {"Attributes": [2], "Permittivity": 3.66, "Permeability": 1.0, "LossTan": 0.0037}],
    "Postprocessing": {"Probe": [{"Index": 1, "Center": [0, 0, 100]}]}
  },
  "Boundaries": {
    "Conductivity": [{"Attributes": [100], "Conductivity": 5.8e7, "Thickness": 35}],
    "PEC": {"Attributes": [101]},
    "Absorbing": {"Attributes": [102], "Order": 1},
    "LumpedPort": [{"Index": 1, "R": 50, "Excitation": true, "Attributes": [200], "Direction": "+X"}]
  },
  "Solver": {
    "Order": 2,
    "Driven": {"Samples": [{"Type": "Linear", "MinFreq": 2.3, "MaxFreq": 3.4, "NSample": 201},
                           {"Type": "Point", "Freq": [2.87], "AddToPROM": true}],
               "AdaptiveTol": 1e-3},
    "Linear": {"Type": "Default", "KSPType": "GMRES", "Tol": 1e-8, "MaxIts": 500}
  }
}
```

- Lengths (`Thickness`, probe `Center`) are in mesh units (`L0`); frequencies in GHz.
- `"AdaptiveTol" > 0` turns the sweep into an adaptive fast sweep: a few full solves, then
  a reduced model fills in every frequency, probes included.
- Multi-element ports (CPW): `"Elements": [{"Attributes": [a], "Direction": "+Y"}, {"Attributes": [b], "Direction": "-Y"}]`.
- Several excitations in one job: give each port `"Excitation": <port index>`.
- Eigenmodes: `"Problem": {"Type": "Eigenmode"}`, `"Solver": {"Eigenmode": {"N": 4, "Target": 1.4, "Tol": 1e-6}}`
  (`Target` in GHz is the lower bound of the search).

## Metal

`Conductivity` with `Thickness` is valid from films far thinner than the skin depth
(resistive sheet) to thick conductors: Palace uses the finite-thickness surface impedance
and applies it to both faces of an internal sheet. Without `Thickness` it is the
thick-conductor formula only. For eigenmodes use PEC metal instead (see below).

## Outputs

| File | Content |
| --- | --- |
| `port-S.csv` | `f (GHz)`, `|S[i][j]| (dB)`, `arg(S[i][j]) (deg.)` |
| `port-V.csv`, `port-I.csv` | `V_inc[1]`, `Re{V[1]}`, `Im{V[1]}`, ... (peak phasors) |
| `probe-B.csv`, `probe-E.csv` | `Re{B_x[k]}`, `Im{B_x[k]}`, ... per probe index, per frequency |
| `eig.csv` | mode, `Re{f} (GHz)`, `Im{f}`, `Q`, error estimates |
| `domain-E.csv` | electric and magnetic energy |

**Power normalisation.** Palace excites each port with `V_inc * conj(I_inc) = 1 W` in
peak phasors, which is 0.5 W of time-averaged incident power. To quote a field per
sqrt(W) of time-averaged power, divide by `sqrt(|V_inc|^2 / (2 Z0))` (the wrapper does).

## Meshing with gmsh (what the wrapper does)

1. Air box, one box per dielectric layer, metal as plane surfaces at z = 0, each port as a
   rectangle between the conductors (or a vertical rectangle for a ground-to-strip port).
2. `occ.fragment(air, everything else)` to make it conformal, then use the returned map to
   find which pieces came from which input.
3. Physical groups become Palace attributes: volumes per material, surfaces for metal,
   ground, the outer absorbing boundary and each port slot.
4. Mesh size from a `Distance` + `Threshold` field on metal and port edges (fine there,
   growing with distance) and a `Box` field around each NV region.
5. Write Gmsh format 2.2.

Dielectric layers thinner than the local mesh size (a 2 um oxide under a chip layout) are
merged into the layer below, with a warning: resolving them costs millions of elements.
That barely changes inductance or the near field but does change line capacitance and
substrate loss.

## Cost on this machine

| Problem | Mesh | Time |
| --- | --- | --- |
| Omega loop, one frequency | 16k tetrahedra, order 2 | 5 s on 4 processes |
| Omega loop, 201-point adaptive sweep | same | 17 s (4 full solves) |
| Split ring, 4 eigenmodes, PEC metal | 31k tetrahedra | 6 min on 6 processes, 4.6 GB |
| Chip shorted CPW (6 um tip, 1.2 mm grounds), one frequency | 68k tetrahedra, 490k unknowns | about 150 s on 4 processes, 3 GB |
| Same, adaptive sweep (4 full solves) | same | 590 s |

The wrapper coarsens the mesh until it is under 90k tetrahedra (40k for eigenmodes) and
warns when it does.

## Eigenmode caveats

- The finite-conductivity boundary depends on sqrt(frequency), which makes the
  eigenproblem nonlinear and roughly 100x slower. The wrapper solves eigenmodes with PEC
  metal, so the reported Q covers radiation, dielectric loss and port loading but **not
  conductor loss**.
- `"Linear": {"Type": "SuperLU", "MGMaxLevels": 1}` makes the direct solver factorise the
  full system; without `MGMaxLevels: 1` it only solves the lowest-order multigrid level.
- Modes with Q near 1 are radiating box modes, not resonances; the wrapper drops Q < 5.
- For a port-coupled open resonator, prefer the adaptive driven sweep: the resonance and
  loaded Q come from the response in under a minute.

## Viewing

`mesh.png` from the wrapper shows the surface mesh on metal and ports. For 3D fields add
`"Save"` under `Solver.Driven` (or `Eigenmode.Save`) and open `postpro/paraview/` in
ParaView 5.12 or newer (not installed here; `brew install --cask paraview`).

## Version note

The knowledge clone is pinned to the installed tag. If it is ever moved to `main`, the
docs may describe options the installed binary rejects: `palace --dry-run` and the
installed schema decide.
