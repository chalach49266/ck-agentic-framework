---
name: microwave-solver-selection
description: >
  Use FIRST for any microwave / RF simulation or design task, before choosing a solver:
  decides between closed-form sizing, the quasi-static sheet solver, openEMS (FDTD), Palace
  (FEM), Qucs-S / Qucsator-RF (circuit) and Flexcompute RF (cloud) so that each solver is
  used only where it fits and none repeats another's work. Trigger phrases: "which solver",
  "microwave simulation", "RF simulation", "simulate this antenna", "simulate this
  resonator", "S-parameters", "matching network", "B1 field", "Rabi frequency", "NV
  microwave", "ODMR antenna", "CPW", "microstrip", "loop antenna", "split ring".
---

# Microwave solver selection

Solvers here are **lanes, not duplicates**. Pick one lane per task, say why, and never run a
second solver to recompute a result the first already gave.

Root of the tooling (call it `MW`):
`{{PHD_ROOT}}/Device Fabrication/Microwave_Ecosystem`

## Ask the router first

Inside a design folder (one with `design.py`):

```bash
"$MW/bin/mw" route      # which solver each stage will use, and why
"$MW/bin/mw" size       # closed-form estimates: free, always first
```

From Python: `nvmw.router.choose(design, task)` and `nvmw.router.plan(design, goal)`.
Tasks: `size`, `match`, `system`, `b1`, `sparams`, `resonance`, `transient`.

## The lanes

| Lane | Engine | Use it for | Do not use it for |
| --- | --- | --- | --- |
| `analytic` | closed form | First sizing: Z0 and eps_eff of CPW / microstrip, loop field and inductance, skin depth, the short / terminated / matched drive trade, ideal L-match values | Anything where geometry detail decides the answer |
| `qucs` | Qucsator-RF | Matching networks, tuning, component loss and catalogue values, cascades of known blocks (R + jwL or Touchstone) | Fields, or the impedance of a layout that has not been solved yet |
| `sheet` | quasi-static sheet current | R, L and B per ampere of electrically small **thin-film** traces | Thick or wide metal (current crowds to edges), anything not electrically small |
| `palace` | finite elements, frequency domain | Electrically small structures with thick or wide metal; resonators; micron features on millimetre chips; curved geometry | Pulse response in time |
| `openems` | FDTD, time domain | Structures a tenth of a wavelength or larger with low Q; broadband response in one run; pulse ring-up; radiation | Electrically small structures (time step follows the smallest cell); high Q (must wait out ring-down) |
| `flexcompute_rf` | Tidy3D RF, cloud GPU | Problems too large for this machine | Anything, without the user's explicit approval: it spends credits |

## The numbers the router uses

- **Electrical size** = metal extent / guided wavelength at the top of the band. Below
  0.1 the field is quasi-static.
- **Crossover length** l = (skin depth)^2 / metal thickness. A trace narrower than about
  2 l carries DC-like current (sheet lane is valid). 100 nm Au at 2.87 GHz: l = 21 um.
  35 um PCB copper: l = 0.04 um, so copper always crowds to the edges.
- **Expected Q** above about 40, or `design.kind == "resonant"`, rules out time domain.
- **FDTD cost** = cells x steps / 8e7 per second; refused above 30 minutes.
- **Deeply quasi-static** (under 0.03 wavelengths): Palace solves at f0 only and the
  impedance is fitted as R + jwL across the band (mode `driven-point`). On the reference
  omega loop this moved the band-edge figure of merit by 0.43 % and halved the run time; on
  a chip-scale CPW it cuts about 10 minutes to about 2.5.

## One field solve per geometry

For the standard NV goal (`matched_b1`) the plan is three stages:

1. `analytic`: size it.
2. one field lane (`sheet`, `palace` or `openems`): impedance of the bare structure and B
   at the NV region per unit drive.
3. `qucs`: design the matching network around that impedance.

The matched field is then **scaled**, not re-simulated: B is proportional to
sqrt(power delivered) (or to port current). Changing only the matching network never
needs a new field solve.

## Evidence behind the lanes (measured on this machine, 2026-10-12)

- PCB omega loop, 1 mm radius: Palace single frequency 5 s, adaptive 201-point sweep
  17 s; openEMS broadband run 90 s. Input impedance agreed to 2 % and field to 3 %.
  The loop is 0.065 wavelengths across, hence Palace.
- 20 mm microstrip: openEMS 20 s per port for the whole band; eps_eff within 0.5 % of
  Hammerstad-Jensen.
- Sheet lane: loop centre field within 2 % and inductance within 1.5 % of closed form,
  in under a second.
- Palace eigenmode on a port-loaded open resonator: 6 minutes; the adaptive driven sweep
  gives the same resonance and loaded Q in under a minute, so port-coupled resonators
  use the sweep and eigenmode is kept for closed or unloaded resonators.

## Rules

- State the lane and the reason before running anything.
- Validate a lane against a closed-form answer, not against another solver.
- Simulated is not fabricated or measured: say which when reporting.
- Flexcompute RF needs an explicit go-ahead every time.

Related skills: `openems`, `palace`, `qucs-s`, `flexcompute-rf`, `microwave-gds-design`,
`microwave-autodesign-loop`.
