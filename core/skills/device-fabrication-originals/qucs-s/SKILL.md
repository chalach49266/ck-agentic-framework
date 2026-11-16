---
name: qucs-s
description: >
  Use for RF circuit-level simulation and schematics with Qucs-S and its Qucsator-RF
  engine: S-parameter and AC analysis of lumped and transmission-line networks, matching
  networks, filters, cascades of Touchstone blocks, component loss and catalogue values;
  writing Qucs netlists and .sch schematics; running headless; rendering a schematic to an
  image. Trigger phrases: "Qucs", "Qucs-S", "Qucsator", "matching network", "L-match",
  "Smith chart", "S-parameter circuit", "Touchstone", "s1p", "s2p", "RF netlist",
  "ngspice". Check `microwave-solver-selection` first: the circuit lane takes a structure's
  impedance as given and never computes fields.
---

# Qucs-S / Qucsator-RF skill

| What | Where |
| --- | --- |
| Qucsator-RF 1.0.7 (headless engine) | `~/opt/qucsator_rf/bin/qucsator_rf` |
| Qucs-S 26.1.1 app (GUI; bundles the same engine) | `/Applications/qucs-s.app/Contents/MacOS/qucs-s` |
| ngspice 47 | `/opt/homebrew/bin/ngspice` |
| Source (knowledge base) | `Device Fabrication/Microwave_Ecosystem/repos/qucs_s`, `repos/qucsator_rf` |
| Project wrapper | `Device Fabrication/Microwave_Ecosystem/nvmw/solvers/qucs.py` |
| Example schematics | `Microwave_Ecosystem/repos/qucs_s/examples/qucsator/RF/` |

## When it fits

Anything built from lumped parts, ideal or modelled lines, and blocks whose S-parameters
are already known. A run takes about 15 ms, so searching every catalogue value is cheap.
It never computes a field: get the structure's impedance from a field lane (or closed
form) once, then do all matching and tuning here.

## Headless run

```bash
qucsator_rf -i circuit.net -o circuit.dat      # netlist in, text dataset out
qucs-s -n -i design.sch -o design.net          # schematic -> netlist
qucs-s -p -i design.sch -o design.pdf          # schematic -> PDF (see "Rendering")
qucs-s --list-entries                          # schematic + netlist line format of every component
```

## Netlist syntax (Qucsator)

```text
# comment
Pac:P1 n0 gnd Num="1" Z="50 Ohm" P="1 W" f="2.87 GHz"
C:C1 n0 n1 C="0.7 pF"
L:L1 n1 n2 L="2 nH"
R:R1 n2 gnd R="0.8 Ohm"
IProbe:Pr1 n1 nload
SUBST:Sub1 er="3.66" h="0.508 mm" t="35 um" tand="0.0037" rho="1.72e-8" D="0.15e-6"
MLIN:MS1 a b Subst="Sub1" W="1.1 mm" L="10 mm" Model="Hammerstad" DispModel="Kirschning"
CLIN:CL1 a b Subst="Sub1" W="1 mm" S="1 mm" L="10 mm" Backside="Air" Approx="yes"
TLIN:Line1 a b Z="50 Ohm" L="10 mm" Alpha="0 dB"
SPfile:X1 nload gnd File="{/abs/path/structure.s1p}" Data="rectangular" Interpolator="linear" duringDC="open"
.SP:SP1 Type="lin" Start="2.3 GHz" Stop="3.4 GHz" Points="401"
.AC:AC1 Type="lin" Start="2.3 GHz" Stop="3.4 GHz" Points="401"
Eqn:Eqn1 dBS11="dB(S[1,1])" Export="yes"
```

`gnd` is the reference node. `SPfile` takes N port nodes then the reference node. Other
RF parts with built-in models: `MCOUPLED`, `MSTEP`, `MTEE`, `MGAP`, `MOPEN`, `MVIA`,
`COPEN`, `CSHORT`, `BOND`, `SPIRALIND`, `COAX`, `Attenuator`, `Circulator`, `Isolator`, `Amp`.

## Dataset

Plain text: `<indep frequency N>` / `<dep S[1,1] frequency>` blocks, one number per line,
complex as `+1.2e-01-j3.4e-02`. `.SP` results hang on `frequency`; `.AC` results
(`node.v`, `Pr1.i`) on `acfrequency`. `nvmw.solvers.qucs.read_dataset` returns arrays.

**Power delivered to a load:** an S-parameter analysis gives no voltages. Add an `.AC`
analysis and an `IProbe` in series with the load: with `Pac ... P="1 W"` the phasors are
peak values, so `P_load = 0.5 * Re(V * conj(I))` is the fraction of the available watt
that reaches the load, and `|I|` is load current per sqrt(W).

## Matching through the wrapper

```python
from nvmw.solvers import qucs
load = qucs.Touchstone("output/loop.s1p")        # or qucs.SeriesRL(r_ohm, l_henry)
cands = qucs.design_match(load, 2.87e9, (2.77e9, 2.97e9), "work/", q_c=150, q_l=40)
best = cands[0]; print(best.describe())           # ranked; last entry is direct drive
sch = qucs.write_schematic(best, load, "output/match.sch")
qucs.render_schematic(sch, "output/schematic.png")
```

What the search does and why:

- Component loss is modelled as a series resistance from the part's Q. At 2.87 GHz a
  0.7 pF capacitor with Q = 150 has 0.5 ohm, comparable to a small loop's resistance,
  so an ideal-component match overstates delivered power by about a factor of two.
- Capacitors come from the RF catalogue grid (0.1 pF steps to 2 pF, E24 above), not plain
  E24, which is far too coarse below 1 pF. 0.1 pF is the practical floor.
- Default objective is delivered power at the worse **band edge**. A broad, imperfect
  match often beats a sharp one for a drive that must cover a band.

## Schematic files

`.sch` is text: `<Components>` lines `<Type Name active x y tx ty mirror rotate "value" show ...>`
and `<Wires>` lines `<x1 y1 x2 y2 "" 0 0 0 "">`. Two-terminal parts have their pins 30
units either side of the centre along their axis (`rotate` 1 = vertical). Check a
generated drawing by exporting its netlist with `qucs-s -n` and comparing connectivity.

## Rendering

The GUI cannot be told which file to open: it ignores a file named on its command line and
does not handle the macOS open-document event. `mw view qucs` launches the app and puts the
schematic's path on the clipboard for File > Open.

`qucs-s -p -o file.png` leaves the background uninitialised (black or noise). Print to
PDF instead, rasterise with `sips -s format png -Z 3400 file.pdf --out file.png`, flatten
onto white and crop. `qucs.render_schematic` does all of that. Open the `.sch` in the app
for a person: `mw view qucs`.

## Pitfalls

- The engine prints "checker notice, variable `S' ... not yet defined" for equations that
  use S-parameters: harmless.
- A Touchstone path inside a `.sch` is relative to the schematic's folder; in a netlist
  use an absolute path in braces.
- Sub-0.1 pF matching values mean the topology is wrong for the load: pad parasitics
  will dominate. Change the topology or the structure.
