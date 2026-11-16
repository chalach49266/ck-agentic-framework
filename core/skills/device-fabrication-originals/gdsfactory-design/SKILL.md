---
name: gdsfactory-design
description: >
  Use this skill when the user asks to design photonic, electronic, quantum, or MEMS chip layouts
  using gdsfactory. Trigger phrases include: "gdsfactory", "photonic design", "photonic circuit",
  "waveguide", "MMI", "coupler", "ring resonator", "MZI", "grating coupler", "routing",
  "cross section", "PDK", "chip layout", "taper", "bend euler", "splitter", "PIC design",
  "photonic integrated circuit", "add fiber array", "pad array", "spiral", "heater",
  "transmon", "flux qubit", "SNSPD", "superconducting", "quantum chip".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: "[description of photonic/electronic design]"
---

# gdsfactory Design Skill

You are an expert in **gdsfactory**, the leading open-source Python framework for chip design (photonics, analog, quantum, MEMS). gdsfactory provides 400+ parametric components, automated routing, PDK management, and simulation integration.

## Core Workflow

```python
import gdsfactory as gf

# 1. Create component
c = gf.Component()

# 2. Add instances with << operator
mmi = c << gf.components.mmi1x2()
bend = c << gf.components.bend_euler(radius=10)

# 3. Connect via ports
bend.connect("o1", mmi.ports["o2"])

# 4. Expose ports
c.add_port("o1", port=mmi.ports["o1"])

# 5. Export
c.write_gds("output.gds")
c.show()  # stream to KLayout
```

## The @cell Decorator

Always use `@gf.cell` for reusable parametric components. It provides automatic caching and deterministic naming:

```python
@gf.cell
def my_waveguide(length: float = 10, width: float = 0.5) -> gf.Component:
    c = gf.Component()
    s = c << gf.components.straight(length=length, cross_section=gf.cross_section.strip(width=width))
    c.add_port("o1", port=s.ports["o1"])
    c.add_port("o2", port=s.ports["o2"])
    return c
```

## Instances and Ports

```python
c = gf.Component()

# Add instance (reference) - uses << operator
ref = c << gf.components.mmi1x2()

# Move/rotate
ref.move((10, 0))
ref.rotate(90)
ref.mirror_x()

# Connect port-to-port (snaps and rotates automatically)
bend = c << gf.components.bend_euler()
bend.connect("o1", ref.ports["o2"])

# Expose ports to parent
c.add_port("o1", port=ref.ports["o1"])
c.add_ports(ref.ports, prefix="mmi_")
```

**Port naming**: optical = "o1","o2"..., electrical = "e1","e2"..., pad = "pad_1"...

## Key Components (400+)

### Waveguides & Bends
- `gf.components.straight(length, cross_section)` - straight waveguide
- `gf.components.bend_euler(radius, angle, cross_section)` - Euler bend (adiabatic)
- `gf.components.bend_circular(radius, angle)` - circular arc bend
- `gf.components.bend_s(size, cross_section)` - S-bend
- `gf.components.wire_straight()` / `wire_corner()` - electrical traces

### Splitters & Couplers
- `gf.components.mmi1x2(width_mmi, length_mmi)` - 1x2 MMI
- `gf.components.mmi2x2(width_mmi, length_mmi)` - 2x2 MMI
- `gf.components.coupler(gap, length)` - directional coupler
- `gf.components.coupler_ring(gap, radius)` - ring bus coupler

### Resonators
- `gf.components.ring_single(gap, radius, length_x)` - single bus ring
- `gf.components.ring_double(gap, radius)` - add-drop ring
- `gf.components.ring_single_heater()` - thermally tuned ring
- `gf.components.disk(radius)` - disk resonator

### MZIs
- `gf.components.mzi(delta_length)` - Mach-Zehnder interferometer
- `gf.components.mzi_phase_shifter()` - MZI with heater

### Grating Couplers
- `gf.components.grating_coupler_elliptical()` - elliptical GC
- `gf.components.grating_coupler_rectangular()` - rectangular GC
- `gf.components.grating_coupler_array()` - GC array

### Tapers
- `gf.components.taper(length, width1, width2)` - linear taper
- `gf.components.taper_cross_section(cross_section1, cross_section2, length)` - XS transition

### Pads & Vias
- `gf.components.pad(size)` - bond pad
- `gf.components.pad_array(columns, rows)` - pad array
- `gf.components.via_stack(size, layers)` - metal via stack

### Spirals & Delay Lines
- `gf.components.spiral(length)` - compact spiral
- `gf.components.spiral_racetrack()` - racetrack spiral
- `gf.components.delay_snake(length)` - serpentine delay line

### Quantum Components
- `gf.components.transmon()` - transmon qubit
- `gf.components.flux_qubit()` - flux qubit
- `gf.components.snspd()` - superconducting nanowire single-photon detector
- `gf.components.resonator_cpw()` - CPW resonator
- `gf.components.coupler_capacitive()` - capacitive coupler

### Shapes & Utility
- `gf.components.rectangle(size, layer)` - rectangle
- `gf.components.circle(radius, layer)` - circle
- `gf.components.text(text, size, layer)` - text label
- `gf.components.die()` - full die with alignment marks

## Routing

```python
c = gf.Component()
mmi1 = c << gf.components.mmi1x2()
mmi2 = c << gf.components.mmi1x2()
mmi2.move((100, 50))

# Single route
gf.routing.route_single(c, mmi1.ports["o2"], mmi2.ports["o1"], cross_section="strip")

# Bundle route (multiple ports)
gf.routing.route_bundle(c,
    [mmi1.ports["o2"], mmi1.ports["o3"]],
    [mmi2.ports["o2"], mmi2.ports["o3"]],
    cross_section="strip",
    separation=5,
)

# With waypoint steps
gf.routing.route_single(c, port1, port2, steps=[{"dy": 30}, {"dx": 100}])

# Electrical routing
gf.routing.route_bundle_electrical(c, eports1, eports2, cross_section="metal_routing")

# All-angle routing
gf.routing.route_bundle_all_angle(c, ports1, ports2)
```

### Fiber & Pad IO
```python
# Add fiber array to component
c_with_fibers = gf.routing.add_fiber_array(component, with_loopback=True)

# Add electrical pads
c_with_pads = gf.routing.add_electrical_pads_top(component)
```

## Paths and CrossSections

```python
# Define a path
import numpy as np
p = gf.path.euler(radius=10, angle=90)
# or: gf.path.straight(length=20)
# or: gf.path.arc(radius=10, angle=45)
# or: gf.path.spiral_archimedean(min_bend_radius=5, separation=2)

# Define a cross-section
xs = gf.cross_section.strip(width=0.5, layer=(1,0))
# Built-in: strip, rib, slot, nitride, metal1, metal2, metal3, heater_metal, pin, pn

# Extrude path with cross-section
c = gf.path.extrude(p, cross_section=xs)

# Transition between cross-sections
trans = gf.path.transition(
    cross_section1=gf.cross_section.strip(width=0.5),
    cross_section2=gf.cross_section.strip(width=2.0),
)
c = gf.path.extrude(gf.path.straight(length=20), cross_section=trans)
```

## Generic PDK Layers

```python
from gdsfactory.generic_tech import LAYER

LAYER.WG        # (1,0)  - 220nm Si waveguide
LAYER.SLAB150   # (2,0)  - 150nm shallow etch
LAYER.SLAB90    # (3,0)  - 90nm deep etch
LAYER.WGN       # (34,0) - SiN waveguide
LAYER.GE        # (5,0)  - Germanium
LAYER.HEATER    # (47,0) - Heater metal
LAYER.M1        # (41,0) - Metal 1
LAYER.M2        # (45,0) - Metal 2
LAYER.M3        # (49,0) - Metal 3
LAYER.VIA1      # (44,0) - Via 1
LAYER.VIA2      # (43,0) - Via 2
LAYER.N         # (20,0) - N-doping
LAYER.P         # (21,0) - P-doping
LAYER.FLOORPLAN # (64,0) - Floorplan
```

## PDK Setup

```python
pdk = gf.Pdk(
    name="my_fab",
    layers=LAYER,
    cross_sections={"strip": strip_xs, "rib": rib_xs},
    cells={"mmi1x2": my_mmi1x2, "straight": my_straight},
    layer_stack=layer_stack,
)
pdk.activate()

# Now resolve by string
c = gf.get_component("mmi1x2")
xs = gf.get_cross_section("strip")
```

## YAML-Based Design

```yaml
instances:
  mmi:
    component: mmi1x2
    settings:
      width_mmi: 4.5
  bend:
    component: bend_euler

connections:
  bend,o1: mmi,o2

routes:
  optical:
    links:
      mmi,o3: bend,o1
    settings:
      cross_section: strip

ports:
  o1: mmi,o1
  o2: bend,o2
```

Load: `c = gf.read.from_yaml("design.pic.yml")`

## Boolean Operations

```python
c = gf.boolean(A=component_a, B=component_b, operation="not", layer=(1,0))
# operations: "or", "and", "not", "xor"
```

## Layout Utilities

```python
# Pack components tightly
packed = gf.pack([c1, c2, c3], spacing=10)

# Grid arrangement
grid = gf.grid([c1, c2, c3, c4], shape=(2, 2), spacing=(20, 20))

# Grid with text labels
grid = gf.grid_with_text([c1, c2, c3])
```

## Simulation (via gplugins)

```python
import gplugins as sim

# Tidy3D FDTD
sim.tidy3d.get_simulation(component, wavelength_start=1.5, wavelength_stop=1.6)

# SAX circuit simulation
import sax
netlist = component.get_netlist()
circuit, _ = sax.circuit(netlist=netlist, models=models)
S = circuit(wl=np.linspace(1.5, 1.6, 100))

# Mode solving
sim.tidy3d.get_modes(cross_section=xs, wavelength=1.55, num_modes=4)
```

## Best Practices

1. **Always use `@gf.cell`** for reusable components - enables caching and reproducibility.
2. **Connect via ports** - never manually position geometry; use `ref.connect("o1", other.ports["o2"])`.
3. **Use `<<` operator** to add instances: `ref = c << gf.components.straight()`.
4. **Expose ports** on every component - they define the interface for routing and hierarchy.
5. **Use cross_section strings** when a PDK is active: `cross_section="strip"` instead of creating objects.
6. **Prefer Euler bends** (`bend_euler`) over circular - they're adiabatic and lower-loss.
7. **Route bundles** for multi-port connections instead of individual routes.
8. **Check DRC** before tapeout: `c.show()` streams to KLayout for visual inspection.
9. **Use `ComponentSpec`** type hints (str | callable | dict) for flexible component parameters.
10. **Leverage hierarchy** - build small cells, compose into larger ones via References.

## Additional Resources

For complete API details, see [references/api-reference.md](references/api-reference.md).
For the component catalog, see [references/components.md](references/components.md).
