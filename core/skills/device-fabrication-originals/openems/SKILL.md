---
name: openems
description: >
  Use when simulating with openEMS (open-source FDTD, time domain) through its Python
  interface: broadband S-parameters, near fields and pulse response of microstrip, CPW,
  antennas and other board-scale structures; building CSXCAD geometry from GDS polygons;
  meshing; lumped ports; field dumps; viewing models in AppCSXCAD. Trigger phrases:
  "openEMS", "CSXCAD", "AppCSXCAD", "FDTD microwave", "microstrip simulation", "patch
  antenna", "time-domain RF simulation", "lumped port", "thirds rule", "nf2ff".
  Check `microwave-solver-selection` first: openEMS is the wrong tool for electrically
  small or high-Q structures.
---

# openEMS (FDTD) skill

openEMS 0.37.0 with CSXCAD 0.7.0, built from source on this machine.

| What | Where |
| --- | --- |
| Solver, AppCSXCAD | `~/opt/openEMS/bin` |
| Python bindings (`openEMS`, `CSXCAD`) | conda env `microwave` (`/opt/anaconda3/envs/microwave/bin/python`) |
| Source, docs, tutorials (knowledge base) | `Device Fabrication/Microwave_Ecosystem/repos/openEMS-Project` |
| Project wrapper | `Device Fabrication/Microwave_Ecosystem/nvmw/solvers/openems.py` |
| GDS-to-openEMS reference flows | `Microwave_Ecosystem/repos/gds2openEMS`, `repos/pyems`, `repos/gerber2ems` |

Docs to read in the clone: `doc-src/concepts/*.rst` (mesh, ports, dumps, simulation),
`doc-src/postproc/*.rst`, tutorials in `openEMS/python/Tutorials/` (`MSL_NotchFilter.py`,
`MRI_Loop_Coil.py` for B1 maps, `Simple_Patch_Antenna.py`).

## When it fits

- Structure is a tenth of a guided wavelength or larger, and low Q.
- You want the whole band from one run, a pulse response, or radiation (NF2FF).

Not for: electrically small structures (the time step follows the smallest cell, so a
quasi-static field costs minutes: use Palace or the sheet solver); high Q (the run must
wait out the ring-down); micron features in millimetre domains.

## Through the project wrapper

```python
from nvmw import components
from nvmw.solvers import openems
d = components.microstrip_line(length=20000)          # um
r = openems.run(d, out_dir="output", quality="normal")   # draft | normal | fine
r.freq, r.s            # Hz, S[nf, i, j]
r.z_in_f0, r.rois[0].b # input impedance; B (T per sqrt(W) incident), shape (3, ny, nx)
openems.view(d)        # opens the model in AppCSXCAD
```

Runs go to `~/mw_runs/<design>/<tag>_p<port>/` (outside OneDrive); `openems.log` holds
the solver output.

## Raw API essentials

```python
from CSXCAD import ContinuousStructure
from openEMS import openEMS
fdtd = openEMS(NrTS=2_000_000, EndCriteria=1e-4)
fdtd.SetGaussExcite(f0, fc)                         # centre and 20 dB half-width, Hz
fdtd.SetBoundaryCond(["PML_8"] * 4 + ["PEC", "PML_8"])   # xmin xmax ymin ymax zmin zmax
csx = ContinuousStructure(); fdtd.SetCSX(csx)
mesh = csx.GetGrid(); mesh.SetDeltaUnit(1e-6)       # drawing unit: um
sub = csx.AddMaterial("sub", epsilon=3.66, kappa=2 * pi * f0 * EPS0 * 3.66 * tand)
sub.AddBox([x0, y0, -h], [x1, y1, 0], priority=1)
metal = csx.AddConductingSheet("cu", conductivity=5.8e7, thickness=35e-6)   # thickness in metres
metal.AddPolygon(points.T, "z", 0.0, priority=10)   # points shape (2, N), zero-thickness sheet
port = fdtd.AddLumpedPort(1, 50, start, stop, "z", 1.0, priority=5)   # last number: excite amplitude
dump = csx.AddDump("Hf", dump_type=11, file_type=1, frequency=[f0]); dump.AddBox(a, b)
fdtd.Run(sim_path, cleanup=True, numThreads=0)
port.CalcPort(sim_path, freq, ref_impedance=50)
s11 = port.uf_ref / port.uf_inc;  zin = port.uf_tot / port.if_tot
p_inc = 0.5 * abs(port.uf_inc) ** 2 / 50            # peak phasors
```

`dump_type` 10 / 11 are frequency-domain E / H (0 / 1 time domain). Read HDF5 dumps with
`openEMS.utilities.HDF5Dump` (`SetPlane('z', pos=metres)`, `GetFieldAtIndex(f_idx=0)`
returns `(3, nx, ny)`, `GetMesh(region=True)['lines']` in metres). B = mu0 H; normalise
by sqrt(p_inc) for tesla per sqrt(W).

## Meshing rules that matter

1. **Never put a mesh line on a metal edge.** openEMS makes a mesh edge metal when its
   midpoint is inside the polygon. Use the thirds rule at every long axis-aligned edge:
   one line 0.3 cell inside the metal, one 0.6 cell outside.
2. **Never let a third line fall in that straddling cell.** If it does, transverse metal
   stubs appear with nothing joining their tips: a comb that acts as a slow-wave
   structure. Seen here: a 50 ohm microstrip's eps_eff read 3.2-3.4 instead of 2.86, and
   a 0.2 um change in strip width switched the artefact on. Keep the cell narrower than
   the smoothing resolution so `SmoothMeshLines` cannot split it.
3. Check what the mesh made of the model: `fdtd.Run(path, setup_only=True, debug_pec=True)`
   writes `PEC_dump.vtp` (needs PEC metal, `AddMetal`). Every transverse metal edge should
   end on a longitudinal one.
4. At least four cells through each substrate layer; grade cells by a ratio of 1.5 or less.
5. Pass whole polygon outlines. Slicing curved shapes into trapezoids leaves slivers
   thinner than a cell, which openEMS drops ("Unused primitive" in the log).
6. Extend in-plane lumped ports about 0.7 cell into the metal at both ends, so that after
   snapping the port resistor still touches both conductors.

Resolution used by the wrapper: `draft` 3, `normal` 5, `fine` 8 cells across the narrowest
trace. Throughput on this machine is about 100 million cell-steps per second.

## Extracting line parameters

Do not read a propagation constant from the S21 phase of one lumped-port line: the port
discontinuities shift it by tens of percent. Simulate two lengths and take the eigenvalues
of `T_long @ inv(T_short)`: they are exp(-/+ gamma * delta_L) regardless of the ports.
Validated here: eps_eff within 0.5 % of Hammerstad-Jensen for five strip widths
(`Microwave_Ecosystem/tests/test_field_solvers.py`).

## Viewing

- Model: `AppCSXCAD model.xml` (write it with `csx.Write2XML`), or `mw view csxcad`.
- Fields: VTK dumps (`file_type=0`) open in ParaView (not installed; `brew install --cask paraview`).
- What the solver saw: `--debug-PEC`, `--debug-material`.

## Log lines worth acting on

- "Unused primitive": geometry fell between mesh lines and is missing from the model.
- "timestep seems to be very small": a tiny cell somewhere; expect a long run.
- Energy not decaying: resonant structure. Stop and use Palace.
