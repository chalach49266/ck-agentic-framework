# gdsfactory API Reference

Full docs: https://gdsfactory.github.io/gdsfactory/

## Component

The primary layout canvas. Inherits from `kf.DKCell`.

```python
c = gf.Component(name="optional")  # or via @gf.cell decorator
```

**Adding geometry:**
- `c.add_polygon(points, layer)` - raw polygon
- `c << component` - add instance (returns ComponentReference)
- `c.add_ref(component)` - same as `<<`
- `c.add_label(text, position, layer)` - text label
- `c.add_array(component, columns, rows, spacing)` - arrayed instances

**Ports:**
- `c.add_port(name, center, width, orientation, layer, port_type)` - single port
- `c.add_ports(ports, prefix)` - multiple ports from dict/list
- `c.ports` - dict of all ports
- `c.get_ports_list(orientation=0)` - filter ports

**Properties:**
- `c.bbox` - bounding box
- `c.center`, `c.xmin`, `c.xmax`, `c.ymin`, `c.ymax`
- `c.xsize`, `c.ysize` - dimensions
- `c.settings` - creation parameters (from @cell)
- `c.info` - arbitrary metadata dict

**Export:**
- `c.write_gds(filename)` - GDSII
- `c.write_oas(filename)` - OASIS
- `c.show()` - stream to KLayout
- `c.plot()` - matplotlib
- `c.to_3d(layer_stack)` - 3D trimesh

**Operations:**
- `c.flatten()` - resolve all references
- `c.copy()` - deep copy
- `c.mirror()` - mirror geometry
- `c.get_netlist()` - extract circuit netlist
- `c.area(layer)` - total area on layer

## ComponentReference (Instance)

Returned by `c << component`. Wraps a reference to another Component.

```python
ref = c << gf.components.straight()
```

**Positioning:**
- `ref.move(origin)` - translate to position
- `ref.move(origin, destination)` - translate from origin to destination
- `ref.rotate(angle, center)` - rotate (degrees)
- `ref.mirror_x(x0=0)` / `ref.mirror_y(y0=0)` - mirror
- `ref.connect(port_name, other_port)` - snap to port

**Properties:**
- `ref.ports` - dict of ports (transformed to instance coordinates)
- `ref.x`, `ref.y`, `ref.center`
- `ref.xmin`, `ref.xmax`, `ref.ymin`, `ref.ymax`
- `ref.xsize`, `ref.ysize`

## Port

Connection point defining interface geometry.

```python
gf.Port(
    name="o1",
    center=(0, 0),
    width=0.5,
    orientation=180,    # degrees, direction port faces
    layer=(1, 0),
    port_type="optical",  # "optical", "electrical", "placement"
)
```

## CrossSection

Defines the extrusion profile for paths.

```python
xs = gf.CrossSection(
    sections=[
        gf.Section(width=0.5, layer=(1,0), name="core"),
        gf.Section(width=2.0, layer=(2,0), name="clad", offset=0),
    ],
    radius=10,
    radius_min=5,
)
```

**Built-in cross-sections:**
| Name | Description |
|------|-------------|
| `strip` | 220nm Si, 500nm width, (1,0) |
| `rib` | Rib waveguide with slab |
| `slot` | Slot waveguide |
| `nitride` | SiN waveguide, (34,0) |
| `metal1` / `metal2` / `metal3` | Metal traces |
| `metal_routing` | Wide metal routing |
| `heater_metal` | Heater trace (47,0) |
| `pin` | PIN junction cross-section |
| `pn` | PN junction cross-section |
| `strip_heater_metal` | Strip + heater |

Access: `gf.cross_section.strip()` or `gf.get_cross_section("strip")`

## Path

Trajectory for cross-section extrusion.

```python
p = gf.path.straight(length=10)
p = gf.path.euler(radius=10, angle=90)
p = gf.path.arc(radius=10, angle=45)
p = gf.path.spiral_archimedean(min_bend_radius=5, separation=2, number_of_loops=3)
p = gf.path.smooth(points, radius=10)  # smooth path through waypoints
```

**Extrusion:**
```python
c = gf.path.extrude(path, cross_section=xs)
```

**Transition (taper between cross-sections):**
```python
trans = gf.path.transition(
    cross_section1=gf.cross_section.strip(width=0.5),
    cross_section2=gf.cross_section.strip(width=2.0),
    width_type="linear",  # or "sine", "parabolic"
)
c = gf.path.extrude(gf.path.straight(length=20), cross_section=trans)
```

## Routing Functions

### route_single
```python
gf.routing.route_single(
    component,          # parent Component
    port1,              # source Port
    port2,              # destination Port
    cross_section="strip",
    bend="bend_euler",
    straight="straight",
    steps=None,         # [{"dx": 10}, {"dy": 20}] for waypoints
    waypoints=None,     # explicit (x,y) waypoints
    auto_widen=False,
    taper=None,
)
```

### route_bundle
```python
gf.routing.route_bundle(
    component,
    ports1,             # list of source Ports
    ports2,             # list of destination Ports
    cross_section="strip",
    separation=3.0,     # spacing between parallel routes
    bend="bend_euler",
    sort_ports=True,
    enforce_port_ordering=True,
    path_length_match_loops=None,
    path_length_match_extra_length=0,
)
```

### route_bundle_all_angle
```python
gf.routing.route_bundle_all_angle(component, ports1, ports2, cross_section="strip")
```

### IO Routing
```python
# Fiber array with loopback
c = gf.routing.add_fiber_array(component, grating_coupler="grating_coupler_elliptical", with_loopback=True)

# Fiber single
c = gf.routing.add_fiber_single(component)

# Electrical pads
c = gf.routing.add_electrical_pads_top(component)
c = gf.routing.add_electrical_pads_shortest(component)
c = gf.routing.add_pads_top(component, pad="pad")
```

## PDK

```python
pdk = gf.Pdk(
    name="my_pdk",
    layers=layer_map,            # LayerMap
    layer_stack=layer_stack,     # LayerStack (3D info)
    cross_sections=cross_sections,  # dict[str, CrossSectionFactory]
    cells=cells,                 # dict[str, CellFactory]
    layer_views=layer_views,     # KLayout display properties
    layer_transitions=layer_transitions,  # auto-taper rules
)
pdk.activate()
```

**LayerStack (3D properties):**
```python
from gdsfactory.technology import LayerStack, LayerLevel

layer_stack = LayerStack(
    layers={
        "core": LayerLevel(layer=(1,0), thickness=0.22, zmin=0, material="si"),
        "clad": LayerLevel(layer=(99,0), thickness=3.0, zmin=-1.0, material="sio2"),
        "metal1": LayerLevel(layer=(41,0), thickness=0.5, zmin=1.5, material="al"),
    }
)
```

## File I/O

```python
# Import GDS
c = gf.read.import_gds("file.gds")

# Read from YAML
c = gf.read.from_yaml("design.pic.yml")

# From numpy array
c = gf.read.from_np(np_array, nm_per_pixel=20, layer=(1,0))

# Write
c.write_gds("out.gds")
c.write_oas("out.oas")
```

## Layout Utilities

```python
# Pack components into minimum area
packed = gf.pack(component_list, spacing=10, max_size=(500, 500))

# Grid arrangement
g = gf.grid(component_list, shape=(2, 3), spacing=(50, 50))
g = gf.grid_with_text(component_list)  # adds labels

# Boolean operations
c = gf.boolean(A=comp_a, B=comp_b, operation="not", layer=(1,0))
# operations: "or", "and", "not", "xor"
```

## ComponentSpec Pattern

Many gdsfactory functions accept flexible component specifications:

```python
from gdsfactory.typings import ComponentSpec

# All equivalent:
c = gf.get_component("mmi1x2")                              # string
c = gf.get_component(gf.components.mmi1x2)                  # callable
c = gf.get_component({"component": "mmi1x2", "settings": {"width_mmi": 5}})  # dict
c = gf.get_component(partial(gf.components.mmi1x2, width_mmi=5))  # partial
```

## Available PDKs (Open Source)

| PDK | Install |
|-----|---------|
| Generic (default) | Built-in |
| SiEPIC EBeam (UBC) | `pip install ubcpdk` |
| Cornerstone | `pip install cspdk` |
| GlobalFoundries 180nm | `pip install gf180` |
| SkyWater 130nm | `pip install sky130` |
| IHP SiGe | `pip install ihp` |

## Simulation via gplugins

```python
pip install "gplugins[tidy3d,sax,femwell,meow,meep,elmer]"
```

| Plugin | Use |
|--------|-----|
| `gplugins.tidy3d` | FDTD, mode solving |
| `gplugins.meep` | Open-source FDTD |
| `gplugins.sax` | S-parameter circuit sim |
| `gplugins.femwell` | FEM modes, thermal, TCAD |
| `gplugins.meow` | EME propagation |
| `gplugins.lumerical` | Ansys Lumerical interface |
| `gplugins.devsim` | TCAD device simulation |
