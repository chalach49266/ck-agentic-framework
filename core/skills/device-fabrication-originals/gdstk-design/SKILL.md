---
name: gdstk-design
description: >
  Use this skill when the user asks to create, modify, or analyze GDSII/OASIS photonic or electronic layouts
  using gdstk (GDSII Tool Kit). Trigger phrases include: "create a layout", "draw a polygon", "make a GDS file",
  "boolean operation", "photonic design", "IC layout", "GDSII", "OASIS", "gdstk", "chip layout",
  "waveguide layout", "mask design", "layout design", "gds file", "polygon operations".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: "[description of layout to create]"
---

# gdstk Layout Design Skill

You are an expert in **gdstk** (GDSII Tool Kit), a high-performance C++/Python library for creating and manipulating GDSII and OASIS IC/photonic layout files. Use this skill to help design chip layouts, photonic circuits, MEMS structures, and any planar geometry.

## Core Workflow

Always follow this pattern:

```python
import gdstk
import numpy as np

# 1. Create library (default unit = 1 um, precision = 1 nm)
lib = gdstk.Library(name="DESIGN", unit=1e-6, precision=1e-9)

# 2. Create cells
cell = lib.new_cell("CELL_NAME")

# 3. Add geometry to cells
cell.add(gdstk.rectangle((0, 0), (10, 5), layer=1, datatype=0))

# 4. Save
lib.write_gds("output.gds")
# or lib.write_oas("output.oas")
```

## Key Classes

### Geometry Primitives
- `gdstk.Polygon(points, layer, datatype)` - arbitrary polygon from vertex list
- `gdstk.rectangle(corner1, corner2, **kwargs)` - rectangle
- `gdstk.regular_polygon(center, side_length, sides, **kwargs)` - N-sided regular polygon
- `gdstk.ellipse(center, radius, inner_radius=None, **kwargs)` - circle, ellipse, ring, arc
- `gdstk.racetrack(center, straight_length, radius, **kwargs)` - stadium shape
- `gdstk.cross(center, full_size, arm_size, **kwargs)` - cross/plus shape
- `gdstk.text(text, size, position, **kwargs)` - text as polygons

### Paths (for waveguides, interconnects)
- `gdstk.FlexPath(points, width, offset=0, bend_radius=None, ...)` - flexible paths with bends
- `gdstk.RobustPath(initial_point, width, offset=0, ...)` - handles sharp angles, width functions

### Hierarchy
- `gdstk.Library(name, unit, precision)` - top-level container
- `gdstk.Cell(name)` - named geometry container (use `lib.new_cell()`)
- `gdstk.Reference(cell, origin, rotation, magnification, x_reflection, columns, rows, spacing)` - cell instance/array
- `gdstk.Label(text, origin, layer, texttype)` - text annotation (no geometry)

### Operations
- `gdstk.boolean(operand1, operand2, operation)` - "or", "and", "not", "xor"
- `gdstk.offset(polygons, distance, ...)` - dilate (positive) or erode (negative)
- `gdstk.slice(polygons, position, axis)` - cut along x or y line
- `gdstk.inside(points, polygons)` - point-in-polygon test
- `gdstk.contour(data, level)` - extract contours from 2D data

### File I/O
- `gdstk.read_gds(filename)` - read GDSII -> Library
- `gdstk.read_oas(filename)` - read OASIS -> Library
- `lib.write_gds(filename)` - save as GDSII
- `lib.write_oas(filename)` - save as OASIS

## Layer Convention

Always define layers clearly at the top of the script:

```python
LAYERS = {
    "waveguide":    {"layer": 1, "datatype": 0},
    "slab":         {"layer": 2, "datatype": 0},
    "metal":        {"layer": 10, "datatype": 0},
    "via":          {"layer": 11, "datatype": 0},
    "label":        {"layer": 100, "texttype": 0},
}
```

## Common Patterns

### Waveguide with Bends
```python
path = gdstk.FlexPath(
    [(0, 0), (100, 0), (100, 50), (200, 50)],
    width=0.5,
    bend_radius=10,
    layer=1,
    simple_path=True
)
```

### Tapered Waveguide
```python
path = gdstk.RobustPath((0, 0), 0.5, layer=1)
path.segment((50, 0), width=2.0)  # linear taper from 0.5 to 2.0
```

### Boolean: Etch Window
```python
outer = gdstk.rectangle((-5, -5), (5, 5))
inner = gdstk.rectangle((-2, -2), (2, 2))
frame = gdstk.boolean(outer, inner, "not", layer=1)
```

### Array of Structures
```python
ref = gdstk.Reference(unit_cell, (0, 0), columns=10, rows=10, spacing=(20, 20))
```

### Hierarchical Design
```python
# Build bottom-up
via = lib.new_cell("VIA")
via.add(gdstk.rectangle((-0.5, -0.5), (0.5, 0.5), layer=11))

device = lib.new_cell("DEVICE")
device.add(gdstk.Reference(via, (5, 5)))
device.add(gdstk.FlexPath([(0,0),(10,0)], 0.5, layer=1))

top = lib.new_cell("TOP")
top.add(gdstk.Reference(device, (0, 0), columns=4, rows=4, spacing=(50, 50)))
```

## Best Practices

1. **Units**: Default is micrometers. State units clearly. Use `unit=1e-6, precision=1e-9`.
2. **Cell names**: Must be unique within a Library. Use UPPER_SNAKE_CASE.
3. **Hierarchy**: Use References for repeated structures - saves file size and memory.
4. **Boolean ops**: Costly on complex polygons. Simplify inputs when possible.
5. **Bend radius**: Always set `bend_radius` on FlexPath for smooth waveguide bends.
6. **simple_path=True**: Use on FlexPath for single-trace paths (no parallel edges).
7. **Flattening**: Use `cell.flatten()` only when needed (e.g., before boolean ops across cells).
8. **Validation**: Use `lib.top_level()` to verify hierarchy; check for duplicate cell names.

## Additional Resources

For complete API details, see [references/api-reference.md](references/api-reference.md).
