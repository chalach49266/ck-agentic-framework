---
name: tidy3d
description: >
  Use this skill when the user asks to simulate electromagnetic fields, photonic devices,
  or nanophotonic structures using Tidy3D (FDTD or EME). Trigger phrases include:
  "tidy3d", "FDTD simulation", "electromagnetic simulation", "photonic simulation",
  "waveguide simulation", "mode solver", "mode analysis", "ring resonator", "MZI",
  "grating coupler", "metasurface", "photonic crystal", "S-parameters", "FluxMonitor",
  "ModeMonitor", "ModeSource", "PlaneWave", "parameter sweep", "inverse design",
  "adjoint optimization", "EME simulation", "Flexcompute", "web.run", "sim_data",
  "transmission spectrum", "resonance", "photonic integrated circuit FDTD".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, mcp__tidy3d__search_flexcompute_docs, mcp__tidy3d__fetch_flexcompute_doc
argument-hint: "[description of device and simulation goal]"
---

# Tidy3D Simulation Skill

You are an expert in **Tidy3D**, Flexcompute's Python framework for FDTD and EME electromagnetic simulation. Tidy3D runs simulations on Flexcompute's GPU-accelerated cloud.

**Local repo:** `{{PHD_ROOT}}/Device Fabrication/Photonics_Ecosystem/repos/tidy3d/`
**Docs:** `https://docs.flexcompute.com/projects/tidy3d/en/latest/`
**Units:** length in **micrometers (µm)**, frequency in **Hz**, time in **seconds**.

---

## MCP-First Workflow

Always query the Tidy3D MCP before writing simulation code:

```
search_flexcompute_docs("ring resonator tidy3d")
search_flexcompute_docs("ModeSource tidy3d")
fetch_flexcompute_doc("<url from search result>")
```

Search patterns:
- Device type: `"ring resonator tidy3d"`, `"grating coupler SOI"`
- API class: `"ModeSource tidy3d"`, `"FluxMonitor tidy3d"`
- Workflow: `"parameter sweep batch tidy3d"`, `"adjoint inverse design tidy3d"`

---

## Core FDTD Workflow

```python
import tidy3d as td
import tidy3d.web as web
import numpy as np

# 1. Physical parameters (units: µm, Hz)
lam0  = 1.55
freq0 = td.C_0 / lam0
fwidth = freq0 / 10
freqs = np.linspace(freq0 - fwidth, freq0 + fwidth, 100)

# 2. Materials
silicon = td.Medium(permittivity=3.47**2)
silica  = td.Medium(permittivity=1.44**2)

# 3. Geometry
wg = td.Structure(
    geometry=td.Box(center=(0, 0, 0), size=(td.inf, 0.5, 0.22)),
    medium=silicon,
)

# 4. Source — always in a straight waveguide section
src = td.ModeSource(
    center=(-4, 0, 0),
    size=(0, 3, 2),
    source_time=td.GaussianPulse(freq0=freq0, fwidth=fwidth),
    direction="+",
    mode_spec=td.ModeSpec(num_modes=1),
)

# 5. Monitors
T_mon = td.ModeMonitor(
    center=(4, 0, 0),
    size=(0, 3, 2),
    freqs=[freq0],
    mode_spec=td.ModeSpec(num_modes=1),
    name="transmission",
)

# 6. Build simulation
sim = td.Simulation(
    size=(10, 4, 4),
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=20, wavelength=lam0),
    structures=[wg],
    sources=[src],
    monitors=[T_mon],
    run_time=1e-12,
    boundary_spec=td.BoundarySpec(
        x=td.Boundary.pml(), y=td.Boundary.pml(), z=td.Boundary.pml()
    ),
)

# 7. ALWAYS visualize before submitting
import matplotlib.pyplot as plt
sim.plot_eps(x=0); plt.show()
sim.plot_eps(y=0); plt.show()

# 8. Run
sim_data = web.run(sim, task_name="waveguide_fdtd")

# 9. Extract results
T = sim_data["transmission"].amps.sel(mode_index=0, direction="+").abs**2
```

---

## Key Classes Reference

### Simulation

```python
td.Simulation(
    size=(sx, sy, sz),            # µm
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=20, wavelength=lam0),
    structures=[...],
    sources=[...],
    monitors=[...],
    run_time=1e-12,               # seconds; use RunTimeSpec for auto
    boundary_spec=td.BoundarySpec.all_sides(td.PML()),
    symmetry=(0, 1, 0),           # optional: 0=none, 1=Esym, -1=Hym
)
```

### Sources

```python
# Waveguide mode injection
td.ModeSource(center, size, source_time, direction="+", mode_spec=td.ModeSpec())

# Uniform plane wave
td.PlaneWave(center, size=(td.inf, td.inf, 0), source_time, direction="-", pol_angle=0)

# Focused beam
td.GaussianBeam(center, size, source_time, direction, waist_radius=1.0)

# Point dipole
td.PointDipole(center, source_time, polarization="Ex")

# Pulse
source_time = td.GaussianPulse(freq0=freq0, fwidth=fwidth)
```

### Monitors

```python
# Mode overlap (transmission)
td.ModeMonitor(center, size, freqs, mode_spec=td.ModeSpec(), name="T")

# Net power flux
td.FluxMonitor(center, size, freqs, name="flux")

# 3D/2D/1D field recording
td.FieldMonitor(center, size, freqs, fields=["Ex","Ey","Ez"], name="field")

# Time-domain (for Q-factor)
td.FieldTimeMonitor(center, size=(0,0,0), start=0, interval=10, name="time")

# Near-to-far field
td.FieldProjectionAngleMonitor(center, size, freqs, ...)

# Extract:
T = sim_data["T"].amps.sel(mode_index=0, direction="+").abs**2
flux = sim_data["flux"].flux
field_ex = sim_data["field"].Ex
```

### Geometry

```python
td.Box(center=(x,y,z), size=(lx,ly,lz))
td.Cylinder(center, radius, length, axis=2)
td.Sphere(center, radius)
td.PolySlab(vertices=[(x1,y1),...], slab_bounds=(z_min, z_max))
td.GeometryGroup(geometries=[...])  # boolean union
```

### Materials

```python
td.Medium(permittivity=eps, conductivity=0)   # lossless/lossy dielectric
td.PECMedium()                                 # perfect conductor

# Material library (dispersive)
from tidy3d.material_library import material_library
si = material_library["Si"]["Li1993_293K"]
sio2 = material_library["SiO2"]["Horiba"]

# Custom dispersive
td.Lorentz(eps_inf=1, coeffs=[(de, f, delta)])
td.Drude(eps_inf=1, coeffs=[(f, delta)])
```

### Grid

```python
td.GridSpec.auto(min_steps_per_wvl=20, wavelength=lam0)

# Fine-grained control
td.GridSpec(
    grid_x=td.AutoGrid(min_steps_per_wvl=20),
    grid_y=td.AutoGrid(min_steps_per_wvl=20),
    grid_z=td.AutoGrid(min_steps_per_wvl=20),
    wavelength=lam0,
    override_structures=[
        td.MeshOverrideStructure(geometry=fine_box, dl=0.01)
    ],
)
```

---

## EME Simulations

Use for long tapers, transitions, periodic structures (>20λ long).

```python
eme_sim = td.EMESimulation(
    size=(length, 4, 4),
    structures=[...],
    monitors=[...],
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=20, wavelength=lam0),
    axis=0,                          # propagation axis
    eme_grid_spec=td.EMEUniformGrid(
        num_cells=20,
        mode_spec=td.EMEModeSpec(num_modes=10),
    ),
    freqs=[freq0],
)
eme_data = web.run(eme_sim, task_name="eme_taper")

# Length sweep without re-solving modes
eme_sim_sweep = eme_sim.updated_copy(
    sweep_spec=td.EMELengthSweep(scale_factors=np.linspace(0.5, 2.0, 20))
)
```

---

## Parameter Sweeps

```python
def make_sim(width):
    wg = td.Structure(
        geometry=td.Box(center=(0,0,0), size=(td.inf, width, 0.22)),
        medium=silicon,
    )
    return sim.updated_copy(structures=[wg])

# Run all in parallel
sims = {f"w_{w:.3f}": make_sim(w) for w in np.linspace(0.4, 0.6, 11)}
batch_data = web.run_async(sims)

for name, data in batch_data.items():
    T = data["transmission"].amps.sel(mode_index=0, direction="+").abs**2
```

---

## S-Parameters

```python
from tidy3d.plugins.smatrix import ModalComponentModeler, Port

ports = [
    Port(center=(-5,0,0), size=(0,3,2), mode_spec=td.ModeSpec(), direction="+", name="in"),
    Port(center=( 5,0,0), size=(0,3,2), mode_spec=td.ModeSpec(), direction="-", name="out"),
]
modeler = ModalComponentModeler(simulation=sim, ports=ports, freqs=freqs)
modeler_data = web.run(modeler)
smatrix = modeler_data.smatrix()
S21 = smatrix.loc[dict(port_in="in", mode_index_in=0, port_out="out", mode_index_out=0)]
```

---

## Inverse Design (Autograd)

Use **HIPS autograd** — NOT JAX, NOT `tidy3d.plugins.adjoint` (removed).

```python
import autograd
import autograd.numpy as anp
# Regular td.Simulation + web.run() are fully differentiable
# Only trace geometry parameters — never cast traced params to float()
```

See `Photonics_Ecosystem/repos/tidy3d/tidy3d/plugins/autograd/README.md` in the local clone for detailed patterns.

---

## Resonance / Q-Factor

```python
# Method 1: Lorentzian fit to spectrum
# Method 2: Time-domain decay — fit exp decay to FieldTimeMonitor data
#   Q = omega * tau / 2
# Method 3: ResonanceFinder plugin
from tidy3d.plugins.resonance import ResonanceFinder
rf = ResonanceFinder(freq_window=(f_min, f_max))
resonances = rf.run(signals=sim_data["time"].Ez)
```

---

## Visualization-First Rule

**Never run a simulation you haven't inspected visually.**

```python
# Plot permittivity cross-sections in all three planes
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sim.plot_eps(x=0, ax=axes[0])
sim.plot_eps(y=0, ax=axes[1])
sim.plot_eps(z=0, ax=axes[2])
plt.show()
```

Check: waveguides pass through PML (`td.inf`), source in straight section, monitors correctly placed.

---

## Pre-Flight Checklist

Before every `web.run()`:

- [ ] Waveguides use `td.inf` in propagation direction (pass through PML)
- [ ] Source in a straight, uniform section (not at bends/junctions)
- [ ] Mode monitor sized 3–4× waveguide width
- [ ] Grid: ≥15–20 cells across smallest feature
- [ ] `plot_eps` inspected in all three planes
- [ ] `run_time` long enough (or use `td.RunTimeSpec`)

---

## Common Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| T = 0 | Source/monitor misaligned | Check `plot_eps` |
| T > 1.0 | Monitor `direction` wrong | Flip `direction` |
| NaN / diverge | PML too thin or dispersive material issue | Increase PML, check material |
| Shutoff warning | `run_time` too short | Use `td.RunTimeSpec(quality_factor=10)` |
| Wrong `n_eff` guess | Guessed instead of computed | Run ModeSolver first |
| Autograd TypeError | `float()` on traced param | Remove the cast |
| 0 gradient | Simulation domain depends on traced param | Only geometry should be traced |

---

## Coding Rules

- **Never suppress warnings** — every Tidy3D warning indicates a real problem. Read and fix it.
- **Never use try/except around `web.run()`** — errors carry diagnostic information.
- **Never guess `n_eff`** — always compute with ModeSolver.
- **Use `.updated_copy(**kwargs)`** to create modified copies of Tidy3D objects.
- **Use `web.run_async()`** for parameter sweeps (parallel cloud execution).
- All model classes subclass `Tidy3dBaseModel`; use `tidy3d.log.log` for logging.
