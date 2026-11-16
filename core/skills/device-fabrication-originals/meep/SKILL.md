---
name: meep
description: >
  Use this skill when the user asks to simulate electromagnetic fields, compute
  transmittance/reflectance spectra, find resonant modes, model photonic devices,
  or design optical/microwave structures using MEEP (MIT Electromagnetic Equation
  Propagation — FDTD). Trigger phrases include: "FDTD simulation", "meep", "electromagnetic
  simulation", "transmittance spectrum", "reflectance", "resonant mode", "PML",
  "waveguide simulation", "optical cavity", "S-parameters", "near-field", "far-field",
  "adjoint optimization", "photonic bandgap", "Mie scattering", "mode decomposition",
  "antenna simulation", "microwave simulation", "photonic crystal".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: "[description of structure and simulation goal]"
---

# MEEP Electromagnetic Simulation Skill

You are an expert in **MEEP** (MIT Electromagnetic Equation Propagation), a free open-source FDTD electromagnetic simulation package from NanoComp/MIT. Use this skill to help design and simulate optical, photonic, and microwave structures.

**Local repository:** `{{PHD_ROOT}}/Device Fabrication/Photonics_Ecosystem/repos/meep/`
**Docs:** `meep.readthedocs.io/en/latest`
**Cite as:** Oskooi et al., Comp. Phys. Comm. 181, 687 (2010).

---

## Core Workflow

Every MEEP script follows this pattern:

```python
import meep as mp
import numpy as np
import matplotlib.pyplot as plt

# 1. Define cell size
cell = mp.Vector3(sx, sy, sz)   # sz=0 → 2D simulation

# 2. Define geometry (list of GeometricObjects)
geometry = [
    mp.Block(size=mp.Vector3(mp.inf, w, mp.inf),
             center=mp.Vector3(),
             material=mp.Medium(epsilon=12)),
]

# 3. Define sources
sources = [
    mp.Source(mp.GaussianSource(frequency=fcen, fwidth=df),
              component=mp.Ez,
              center=mp.Vector3(-0.5*sx + dpml, 0)),
]

# 4. PML absorbing boundaries
pml_layers = [mp.PML(dpml)]

# 5. Build simulation
sim = mp.Simulation(
    cell_size=cell,
    boundary_layers=pml_layers,
    geometry=geometry,
    sources=sources,
    resolution=resolution,   # pixels per unit length (≥8/λ in highest ε)
)

# 6. Add flux monitors (before run)
flux_region = mp.FluxRegion(center=mp.Vector3(0.5*sx - dpml, 0),
                             size=mp.Vector3(0, sy))
trans = sim.add_flux(fcen, df, nfreq, flux_region)

# 7. Run
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez,
        mp.Vector3(0.5*sx - dpml, 0), 1e-3))

# 8. Post-process
flux_data = mp.get_fluxes(trans)
freqs = mp.get_flux_freqs(trans)
```

---

## Units (Critical)

MEEP uses **dimensionless units** where the speed of light c = 1.

| Quantity | MEEP unit | Conversion |
|----------|-----------|------------|
| Length | a (arbitrary) | Set a = 1 µm → 1 unit = 1 µm |
| Frequency | c/a | f_MEEP = a/λ (in vacuum) |
| Time | a/c | — |
| ε, µ | dimensionless | Direct values |

**Examples:**

- Telecom (a = 1 µm, λ = 1.55 µm): `fcen = 1/1.55 ≈ 0.645`
- Visible (a = 1 µm, λ = 0.532 µm): `fcen = 1/0.532 ≈ 1.88`
- Microwave (a = 1 mm, f = 10 GHz): `fcen = (10e9 × 1e-3) / 3e8 ≈ 0.0333`

---

## Key Classes

### Geometry

```python
mp.Block(size, center, material)           # Rectangular box / slab
mp.Cylinder(radius, height, center, material)  # Cylinder (axis=z by default)
mp.Sphere(radius, center, material)        # Sphere
mp.Cone(radius, radius2, height, center, material)  # Truncated cone
mp.Wedge(radius, wedge_angle, center, material)     # Wedge
mp.Prism(vertices, height, center, material)        # Arbitrary prism (2D polygon extruded)
```

### Materials

```python
mp.Medium(epsilon=12)                      # Simple lossless dielectric
mp.Medium(epsilon=3.5, mu=1)              # Magnetic material
mp.Medium(epsilon=complex(3.5, 0.01))     # Lossy (imaginary part = loss)
mp.metal                                  # Perfect metal (ε → −∞)

# Dispersive (Drude-Lorentz)
mp.Medium(epsilon=1,
          E_susceptibilities=[
              mp.LorentzianSusceptibility(frequency=1.0, gamma=0.1, sigma=1.0)
          ])

# From materials library
from meep.materials import SiO2, Si, Au, Al
```

### Sources

```python
mp.ContinuousSource(frequency=fcen)       # CW sinusoid
mp.GaussianSource(frequency=fcen, fwidth=df)  # Broadband pulse (use for spectra)
mp.CustomSource(src_func=f, center_frequency=fcen)  # Arbitrary time profile

# Source objects
mp.Source(src, component=mp.Ez, center=pt, size=sz)
mp.EigenModeSource(src, center=pt, size=sz, eig_band=1)   # Waveguide mode
mp.GaussianBeamSource(src, beam_x0=pt, beam_kdir=kdir, beam_w0=w0, ...)
```

**Field components:** `mp.Ex, mp.Ey, mp.Ez, mp.Hx, mp.Hy, mp.Hz`

### Boundary Conditions

```python
mp.PML(thickness)                          # All sides
mp.PML(thickness, direction=mp.X)         # X only
mp.PML(thickness, direction=mp.X, side=mp.High)  # +X face only
mp.Absorber(thickness)                    # Alternative to PML for non-PML-friendly media
```

### Monitors

```python
# Flux (power spectrum) — add before run, read after
flux = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=pt, size=sz))

# Fields at a point or volume
sim.add_dft_fields([mp.Ez], fcen, df, nfreq, center=pt, size=sz)

# Near-to-far field transform
n2f = sim.add_near2far(fcen, df, nfreq, mp.FluxRegion(center=pt, size=sz))
```

---

## Common Simulation Patterns

### Transmittance/Reflectance Spectrum

```python
# Two-run method: normalize with empty cell first
# Run 1: empty cell → incident flux
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, pt, 1e-3))
incident_flux = mp.get_fluxes(flux_in)
sim.save_flux("incident", flux_in)   # save for subtraction

# Run 2: with structure → transmitted + reflected
sim.reset_meep()
# rebuild with geometry
sim.load_minus_flux("incident", flux_refl)  # subtract incident from reflected monitor
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, pt, 1e-3))

T = np.array(mp.get_fluxes(flux_trans)) / np.array(incident_flux)
R = -np.array(mp.get_fluxes(flux_refl)) / np.array(incident_flux)
```

### Resonant Mode (Harminv)

```python
# Use a narrow-band source and Harminv to extract resonances
sim.run(
    mp.after_sources(mp.Harminv(mp.Ez, mp.Vector3(), fcen, df)),
    until_after_sources=400
)
# Harminv prints: frequency, decay rate, Q factor, amplitude
```

### Visualization

```python
# Before running — visualize geometry
sim.plot2D()
plt.savefig("geometry.png")

# During run — output fields
sim.run(
    mp.at_beginning(mp.output_epsilon),
    mp.at_every(0.6, mp.output_efield_z),
    until=200
)

# After run — plot specific field
eps_data = sim.get_array(center=mp.Vector3(), size=cell, component=mp.Dielectric)
ez_data  = sim.get_array(center=mp.Vector3(), size=cell, component=mp.Ez)
plt.figure()
plt.imshow(eps_data.transpose(), interpolation='spline36', cmap='binary')
plt.imshow(ez_data.transpose(),  interpolation='spline36', cmap='RdBu', alpha=0.9)
plt.colorbar()
```

### GDSII Import (for Device Fabrication layouts)

```python
gdsii_file = "design.gds"
si    = mp.Medium(index=3.45)
sio2  = mp.Medium(index=1.44)

geometry = mp.get_GDSII_prisms(si, gdsii_file, layer=1, zmin=0, zmax=0.22)
# Combine with other geometry as usual
```

### Parallel Run (MPI)

```bash
mpirun -np 4 python simulation.py
# Or with conda-installed meep (parallel version):
conda activate mp
mpirun -np 4 python simulation.py
```

---

## Common Use Cases

### Ring Resonator Q-Factor

```python
import meep as mp
import numpy as np

fcen, df = 0.15, 0.1
r, w = 3.0, 0.5   # ring radius, waveguide width

geometry = [
    # Bus waveguide
    mp.Block(mp.Vector3(mp.inf, w, mp.inf), center=mp.Vector3(0, -r-w, 0),
             material=mp.Medium(epsilon=12)),
    # Ring (approximated as a bent waveguide; use Harminv to extract Q)
    mp.Cylinder(radius=r + w/2, material=mp.Medium(epsilon=12)),
    mp.Cylinder(radius=r - w/2, material=mp.air),
]

sim = mp.Simulation(cell_size=mp.Vector3(16, 16, 0),
                    boundary_layers=[mp.PML(1.0)],
                    geometry=geometry,
                    sources=[mp.Source(mp.GaussianSource(fcen, fwidth=df),
                                       mp.Ez, mp.Vector3(-7, -r-w))],
                    resolution=10)
sim.run(mp.after_sources(mp.Harminv(mp.Ez, mp.Vector3(0, -r-w), fcen, df)),
        until_after_sources=300)
```

### Waveguide Transmittance (Straight → Bent)

```python
# Two runs: (1) straight reference, (2) bent waveguide
# Normalize transmitted flux in run 2 by incident flux from run 1
# → bending loss in dB

fcen, df = 0.15, 0.1
dpml, res = 1.0, 10

def make_sim(bent=False):
    geo = [mp.Block(mp.Vector3(mp.inf, 1, mp.inf), center=mp.Vector3(),
                    material=mp.Medium(epsilon=12))]
    if bent:
        geo.append(mp.Block(mp.Vector3(1, mp.inf, mp.inf),
                            center=mp.Vector3(3.5, -1.5),
                            material=mp.Medium(epsilon=12)))
        geo.append(mp.Cylinder(radius=1, center=mp.Vector3(3.5, 0),
                               material=mp.air))
    return mp.Simulation(cell_size=mp.Vector3(16, 16, 0),
                         boundary_layers=[mp.PML(dpml)],
                         geometry=geo,
                         sources=[mp.Source(mp.GaussianSource(fcen, fwidth=df),
                                            mp.Ez, mp.Vector3(-7, 0))],
                         resolution=res)
```

### Mie Scattering Cross Section

```python
r = 1.0   # sphere radius (units of a)
fcen, df, nfreq = 1.0, 0.5, 50

geometry = [mp.Sphere(radius=r, center=mp.Vector3(),
                      material=mp.Medium(epsilon=4))]

# Total-field / scattered-field (TFSF) source
sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df),
                     component=mp.Ez,
                     center=mp.Vector3(0, 0),
                     size=mp.Vector3(0, 0))]
# → use sim.add_flux on a box around the sphere; normalize vs. empty cell
```

### Photonic Crystal Bandgap (1D)

```python
# 1D alternating dielectric stack
a, d, eps_hi = 1.0, 0.5, 12.0
geometry = [mp.Block(size=mp.Vector3(d, mp.inf, mp.inf),
                     center=mp.Vector3(),
                     material=mp.Medium(epsilon=eps_hi))]

k_points = [mp.Vector3(kx) for kx in np.linspace(0, 0.5, 20)]
# Use mpb (MIT Photonic Bands) for band structure, or MEEP with Bloch BCs:
sim = mp.Simulation(cell_size=mp.Vector3(a, 1, 0),
                    geometry=geometry,
                    boundary_layers=[],
                    k_point=mp.Vector3(0.3),
                    resolution=32)
```

---

## Installation (macOS, via Conda)

```bash
conda create -n meep -c conda-forge pymeep
conda activate meep
python -c "import meep as mp; print(mp.__version__)"
```

For parallel:
```bash
conda create -n meep -c conda-forge pymeep=*=mpi_openmpi*
```

---

## Best Practices

1. **Resolution:** Use ≥ 8 pixels per wavelength in the highest-ε material. Start with 10, refine to 20+ for production.
2. **PML thickness:** ≥ half a wavelength in the background medium. Use `mp.PML(dpml)` where `dpml ≥ 0.5/fcen`.
3. **Cell size:** Add `2×dpml` padding on each side beyond your structure. Never let structures overlap PML.
4. **2D vs 3D:** Prototype in 2D first — much faster. Switch to 3D only for final validation.
5. **Broadband spectra:** Always use `GaussianSource` with `fwidth ≈ 0.2 × fcen` for smooth spectra. Run `until_after_sources=stop_when_fields_decayed(...)`.
6. **Symmetry:** Exploit `mp.Mirror(mp.Y, phase=-1)` etc. to halve/quarter cell size when geometry permits.
7. **Flux normalization:** Always run the empty (no structure) case first and normalize.
8. **Units:** Document your `a` (length unit) at the top of every script. Convert all frequencies before the script, not inline.
9. **Output files:** MEEP outputs HDF5. Use `h5py` or `h5utils` to read. `sim.plot2D()` for quick inline visualization.
10. **Adjoint:** Use `meep.adjoint` module for inverse design / topology optimization (requires additional setup).

---

## Simulation Checklist

Before running:
- [ ] Resolution appropriate for smallest feature and highest ε?
- [ ] PML thickness ≥ 0.5/fcen?
- [ ] Structure does NOT overlap PML?
- [ ] Source is inside PML boundary (not at edge)?
- [ ] Flux monitors placed outside geometry, inside PML?
- [ ] Empty-cell normalization run planned?
- [ ] `stop_when_fields_decayed` used (not a fixed `until`) for spectra?

---

## Related Skills

- `gdstk-design` — Create GDSII layouts for import into MEEP via `mp.get_GDSII_prisms()`
- `gdsfactory-design` — Higher-level photonic layout → GDS → MEEP workflow
- `tidy3d` — Cloud FDTD alternative (faster for 3D, requires API key)
