# gdstk API Reference

Full documentation: https://heitzmann.github.io/gdstk/

## Polygon

```python
gdstk.Polygon(points, layer=0, datatype=0)
```

**Properties**: `points`, `layer`, `datatype`, `size`, `repetition`

**Methods**:
- `area()` - polygon area
- `perimeter()` - polygon perimeter
- `bounding_box()` - returns ((min_x, min_y), (max_x, max_y))
- `contain(*points)` - point-in-polygon test
- `copy()` - deep copy
- `mirror(p1, p2=(0,0))` - mirror about line p1-p2
- `rotate(angle, center=(0,0))` - rotate in radians
- `scale(sx, sy=sx, center=(0,0))` - scale
- `translate(dx, dy=None)` - translate
- `fillet(radius, tolerance=0.01)` - round corners
- `fracture(max_points=199, precision=1e-3)` - split into smaller polygons

## Curve

Step-by-step polygon outline builder.

```python
c = gdstk.Curve((0, 0), tolerance=0.01)
c.segment((1, 0))          # straight line
c.arc(radius, initial_angle, final_angle)  # circular arc
c.cubic(controls)           # cubic Bezier
c.cubic_smooth(controls)    # smooth cubic Bezier (auto tangent)
c.quadratic(controls)       # quadratic Bezier
c.bezier(controls)          # general Bezier
c.interpolation(points, angles=None, curl_start=1, curl_end=1)  # spline
c.commands("l", 1, 0, ...)  # SVG-like path commands

poly = gdstk.Polygon(c.points(), layer=1)
```

## FlexPath

Flexible path with constant or variable width. Best for waveguides and interconnects.

```python
fp = gdstk.FlexPath(
    points,              # list of (x, y)
    width,               # number or list (multi-track)
    offset=0,            # number or list
    joins="natural",     # "natural", "miter", "bevel", "round", callable
    ends="flush",        # "flush", "round", "extended", (ext1, ext2), callable
    bend_radius=None,    # auto-curve at corners
    bend_function=None,  # custom bend
    tolerance=2e-4,
    simple_path=False,   # True = single centerline path
    scale_width=True,
    layer=0,
    datatype=0,
)
```

**Methods**:
- `segment(end_point, width=None, offset=None)` - straight segment
- `arc(radius, initial_angle, final_angle, width=None, offset=None)` - circular arc
- `turn(radius, angle, width=None, offset=None)` - relative turn
- `parametric(path_function, width=None, offset=None)` - parametric curve
- `bezier(control_points, width=None, offset=None)` - Bezier segment
- `interpolation(points, angles=None, ...)` - spline through points
- `to_polygons()` - convert to Polygon list
- `spine()` - get centerline points
- `path_position(s)` - point and direction at parameter s
- `translate()`, `rotate()`, `mirror()`, `scale()`

## RobustPath

Handles width/offset as functions of path parameter. Better for complex geometries.

```python
rp = gdstk.RobustPath(
    initial_point,
    width,               # number, list, or callable(u) -> number
    offset=0,            # number, list, or callable(u) -> number
    ends="flush",
    tolerance=2e-4,
    max_evals=1000,
    simple_path=False,
    scale_width=True,
    layer=0,
    datatype=0,
)
```

**Methods**: Same as FlexPath (`segment`, `arc`, `turn`, `parametric`, `bezier`, `interpolation`)

Width/offset functions receive parameter `u` in [0, 1]:
```python
rp.segment((100, 0), width=lambda u: 0.5 + u * 1.5)  # tapers from 0.5 to 2.0
```

## Library

```python
lib = gdstk.Library(name="library", unit=1e-6, precision=1e-9)
```

**Methods**:
- `new_cell(name)` - create and add a new Cell
- `add(*cells)` - add existing cells
- `remove(*cells)` - remove cells
- `top_level()` - cells not referenced by others
- `write_gds(filename, max_points=199, timestamp=None)` - save GDSII
- `write_oas(filename, compression_level=6, ...)` - save OASIS
- `layers_and_datatypes()` - set of (layer, datatype) used
- `layers_and_texttypes()` - set of (layer, texttype) used

## Cell

```python
cell = lib.new_cell("NAME")
```

**Properties**: `name`, `polygons`, `paths`, `references`, `labels`

**Methods**:
- `add(*elements)` - add polygons, paths, references, labels
- `remove(*elements)` - remove elements
- `area(by_spec=False)` - total area (optionally per layer/datatype)
- `bounding_box()` - bounding box of all geometry
- `flatten(apply_repetitions=True)` - resolve all references in-place
- `copy(name, deep_copy=True)` - copy cell
- `get_polygons(apply_repetitions=True, include_paths=True, depth=None, layer=None, datatype=None)` - extract all polygons
- `get_paths(apply_repetitions=True, depth=None, layer=None, datatype=None)` - extract paths
- `get_labels(apply_repetitions=True, depth=None, layer=None, texttype=None)` - extract labels
- `dependencies(recursive=True)` - referenced cells
- `write_svg(filename, ...)` - export SVG

## Reference

```python
ref = gdstk.Reference(
    cell,                    # Cell or cell name
    origin=(0, 0),
    rotation=0,              # radians
    magnification=1,
    x_reflection=False,
    columns=1, rows=1,       # array
    spacing=None,            # (dx, dy) for arrays
)
```

## Boolean & Offset

```python
# Boolean: "or", "and", "not", "xor"
result = gdstk.boolean(operand1, operand2, "not", precision=1e-3, layer=0, datatype=0)
# Returns list of Polygon

# Offset (dilate/erode)
result = gdstk.offset(polygons, distance, join="miter", tolerance=2, precision=1e-3,
                       use_union=False, layer=0, datatype=0)
# distance > 0 = dilate, < 0 = erode

# Slice
result = gdstk.slice(polygons, position, axis, precision=1e-3, layer=0, datatype=0)
# axis: "x" or "y". position: number or list. Returns list of polygon lists.
```

## File I/O

```python
# Read
lib = gdstk.read_gds(filename, unit=0, tolerance=0, filter=None)
lib = gdstk.read_oas(filename, unit=0, tolerance=0)

# Inspect without loading
info = gdstk.gds_info(filename)     # dict with cell names, etc.
unit, precision = gdstk.gds_units(filename)

# Raw cells (fast, no decode)
raw = gdstk.read_rawcells(filename)  # dict of RawCell

# Streaming writer (for very large files)
writer = gdstk.GdsWriter(filename, name="LIB", unit=1e-6, precision=1e-9)
writer.write(cell1)
writer.write(cell2)
writer.close()
```

## Repetition (Efficient Arrays)

```python
poly = gdstk.rectangle((0, 0), (1, 1))
poly.repetition = gdstk.Repetition(columns=5, rows=3, spacing=(2, 2))
# More efficient than multiple References for identical elements
```

## Utility Functions

```python
gdstk.inside(points, polygons)       # list of bool
gdstk.all_inside(points, polygons)   # single bool
gdstk.any_inside(points, polygons)   # single bool
gdstk.contour(data, level=0)         # extract contour polygons from 2D array
```
