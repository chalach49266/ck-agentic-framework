---
name: microwave-gds-design
description: >
  Use when drawing, viewing or checking the layout of a microwave structure for NV spin
  control as GDS: omega loops, shorted or through coplanar waveguides, microstrip lines,
  split-ring resonators, custom metal polygons; defining ports and the NV region; choosing
  a stackup; rendering a preview; pushing to KLayout; running DRC. Trigger phrases:
  "microwave layout", "draw the antenna", "CPW layout", "omega loop GDS", "microwave GDS",
  "preview the microwave design", "microwave DRC", "port definition", "NV region",
  "stackup", "add a microwave component".
---

# Microwave GDS design skill

Layout for microwave structures is done with the `nvmw` package (gdstk and klayout
underneath). Root (call it `MW`):
`{{PHD_ROOT}}/Device Fabrication/Microwave_Ecosystem`.
Run Python with `/opt/anaconda3/envs/microwave/bin/python` and `PYTHONPATH="$MW"`, or use
the `mw` command inside a design folder.

All layout coordinates are **micrometres**. z = 0 is the plane the metal sits on.

## Components (`nvmw.components`)

| Function | Structure | Ports |
| --- | --- | --- |
| `omega_loop(r_mean, trace_w, feed_gap, feed_len, feed_w, stackup, ground_under_loop=False)` | Single-turn loop with two feed legs | one `gap` port between the leg ends |
| `cpw_short(feed_len, s, w, taper_len, s_tip, w_tip, tip_len, short_w, stackup)` | Shorted CPW tapering to a narrow tip (on-chip workhorse) | one `cpw` port |
| `cpw_line(length, s, w, stackup)` | CPW through-line | two `cpw` ports |
| `microstrip_line(length, width=None, stackup)` | Microstrip through-line (width None = 50 ohm) | two `via` ports |
| `split_ring(r_mean, trace_w, split_gap, coupling_gap, stackup)` | Split ring edge-coupled to a 50 ohm microstrip | two `via` ports |

Stackups (`nvmw.stackup.STACKUPS`): `pcb_ro4350b_20mil`, `pcb_fr4_1p6mm`,
`chip_au_on_sio2_si`, `chip_au_on_diamond`. Material numbers are nominal: override them
with real wafer or laminate data (`dataclasses.replace`). Silicon is entered lossless;
set `Layer.sigma` from the wafer resistivity (10 ohm cm = 10 S/m).

## Build, view, check

```python
from nvmw import components, preview, drc
d = components.omega_loop(r_mean=700, trace_w=300)
gds, sidecar = d.write("output")                 # <name>.gds + <name>.mw.json
preview.render(d, "output/preview.png")          # layout, port close-up, NV close-up, stack
preview.show_klive(gds)                          # live view if KLayout is open (klive, port 8082)
report = drc.check(d, {"min_width": 150, "min_space": 150}); print(report.text())
drc.render(d, report, "output/drc.png")          # red width, blue space, magenta port
```

In a design folder: `mw preview N`, `mw drc`, `mw view klayout`.

## What the files carry

- GDS layers: metal `(40, 0)`, port footprints `(45, 0)`, NV regions `(46, 0)`, outline
  `(49, 0)`. They are clear of the photonic chip layers in use; `(20, 0)` is the Cr/Au
  alignment-mark layer. Only `(40, 0)` is mask data. **The microwave metal layer number
  and whether it shares a liftoff with the alignment marks is not decided.**
- The sidecar `<name>.mw.json` carries what GDS cannot: port kind, direction and
  impedance, NV-region height, stackup, parameters. `Design.load(gds)` needs it. A bare
  GDS has no ports and cannot be simulated.
- The Python that built the design is the source of truth; GDS and sidecar are outputs.

## Ports

| Kind | Geometry | Direction |
| --- | --- | --- |
| `gap` | rectangle filling the slot between two metal edges | `x` or `y`: the E-field direction across the slot |
| `cpw` | rectangle spanning both slots and the centre strip of width `s` | axis crossing the slots |
| `via` | footprint under a strip end; vertical port from the backside ground | `z`; needs `backside_ground` |

DRC rejects a port with no metal on either side, metal inside the slot, or a via footprint
not under metal.

## NV region

`Roi(name, center, size, z)`: a rectangle at height `z` above the metal plane (negative =
inside the substrate, e.g. NVs just under a diamond surface the metal sits on). All field
metrics are evaluated there, so set it to where the NV centres really are.

## Custom structures

```python
from nvmw.design import Design, Port, Roi
from nvmw.stackup import STACKUPS
d = Design("my_antenna", STACKUPS["chip_au_on_diamond"], component="custom")
d.add_rect(0, -5, 200, 5)                 # or d.add_metal([(x, y), ...])
d.ports = [Port(1, "gap", (200, -5, 210, 5), "x")]
d.rois = [Roi("nv", (100, 20), (20, 20), z=-0.05)]
d.outline = (-200, -200, 400, 200)
```

To add a reusable component, write a function in `nvmw/components.py` that returns a
`Design` with ports, an NV region, an outline and its arguments in `params`, and add it to
`COMPONENTS`. `Microwave_Ecosystem/tests/test_layout_and_router.py` then builds it, runs
DRC and round-trips the GDS automatically.

## Preview checklist

1. Metal: every trace present and connected; no sliver or gap.
2. Port: fills the gap between two conductors; arrows point across it.
3. NV region: where the NVs are, at the right height (stack panel).
4. Stack: layer order, thicknesses, backside ground.
5. Scale: the title's extent in guided wavelengths makes sense.

A ground plane under a small loop carries image current that cancels most of its field:
`omega_loop` removes it unless `ground_under_loop=True`.

Related skills: `microwave-solver-selection`, `microwave-autodesign-loop`,
`gdstk-design`, `layout-visual-review`.
