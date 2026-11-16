---
name: microwave-autodesign-loop
description: >
  Use when designing, optimising or iterating a microwave structure through the full agent
  loop: edit design.py, check the layout, route to the fitting solver, simulate, log, keep
  or discard. Covers the `mw` harness, the design folder layout, the experiment ledger and
  the rules of the loop. Trigger phrases: "microwave design loop", "optimise the antenna",
  "iterate the microwave design", "auto design", "mw simulate", "mw log", "NV microwave
  delivery design", "improve the Rabi frequency", "design a matched loop".
---

# Microwave auto-design loop

A controlled loop, modelled on the PhotonForge autodesign loop, for microwave structures
that drive NV spins:

```text
principles -> size (closed form) -> edit -> DRC -> preview -> route -> simulate -> log -> keep / discard
```

Harness (call its folder `MW`):
`{{PHD_ROOT}}/Device Fabrication/Microwave_Ecosystem`.
Designs live in `Projects/Microwave Design/<name>/`, one folder per design.

## Commands

```bash
mw="$MW/bin/mw"   # or add $MW/bin to PATH
mw doctor                                   # solvers installed?
mw new <name> --component omega_loop        # creates design.py, program.md, run_design.ipynb, output/
cd <name>
mw size                                     # closed-form estimates (free)
mw drc                                      # must print DRC PASSED
mw preview N                                # output/preview.png, GDS, pushes to KLayout if open
mw route                                    # solver per stage, with reasons
mw simulate > output/run.log 2>&1           # runs the planned stages once each
mw log N --hypothesis "..." --lesson "..."  # KEPT / DISCARDED / CRASH, reverts if not kept
mw status                                   # ledger and best design
mw view klayout|csxcad|qucs                 # open a GUI for a person
```

Components: `omega_loop`, `cpw_short`, `cpw_line`, `microstrip_line`, `split_ring`, `grid_strip`
(wide strip with a gold-grid laser window, solder pads, optional metal lid), `double_split_ring`.
Stackups: `pcb_ro4350b_20mil`, `pcb_fr4_1p6mm`, `chip_au_on_sio2_si`, `chip_au_on_diamond`,
`chip_au_on_sapphire` (100 nm) and `chip_au300nm_`, `chip_au1um_`, `chip_au2um_`, `chip_au3um_on_sapphire`.

## Who runs the simulations

The user has asked (2026-09-24) that new or redone simulation batches be handed over rather
than run for a whole session. Run the loop autonomously when the user asks for an autonomous
run. Otherwise prepare the design folder and point them to `run_design.ipynb` in it: it builds,
checks, routes, and simulates when `RUN = True`, and shows the cached result otherwise
(Jupyter kernel **Python (microwave)**). A single quick check of your own code change is fine.

## First read

1. `program.md` in the design folder: the task, constraints and loop steps.
2. `output/principles.md`: fill it in before experiment 1.
3. `output/results.tsv` and `output/journal.md`: what was tried and learned.

## Design folder contract

| File | Who edits |
| --- | --- |
| `design.py`, block between the `AGENT-TUNABLE` markers (`PARAMS`) | the agent |
| Everything below that block: component, stackup, band, `NV_REGION`, `NV`, `RULES`, `CONSTRAINTS`, `MATCH`, `fom()` | the human; it defines the problem |
| `output/principles.md` | the agent, once, up front |
| `output/journal.md`, `results.tsv`, `best_design.py`, `best_metric.txt`, `experiments/NNNN/` | the harness |

## Per experiment

1. Review the ledger. 2. Propose ONE change and predict its effect on Rabi rate,
bandwidth and uniformity. 3. `mw size`. 4. Edit `PARAMS`. 5. `mw drc`, then
`mw preview N` and look at the picture. 6. `mw route`. 7. `mw simulate`. 8. Look at
`output/result.png` and `output/schematic.png`. 9. `mw log N ...` with a lesson written
**after** reading the numbers.

## What the numbers mean

- **FOM** (default): Rabi frequency per sqrt(W) of available power, averaged over the NV
  region, at the worse edge of the band. Higher is better.
- `rabi_f0_MHz_per_sqrtW`, `nonuniformity_pct` (std/mean over the region),
  `bandwidth_3dB_MHz`, `delivered_f0_pct`, `power_for_target_rabi_W`.
- Rabi frequency = 28.024 GHz/T x B_perp / sqrt(2): 1.98 MHz per gauss of peak field.

## Rules

- One field solve per geometry; the matching network is redesigned by the circuit lane
  for every geometry and never needs a new field solve.
- Never skip DRC or the preview to save time: a port that does not bridge two conductors
  or an NV region inside the metal wastes a solver run.
- Treat a visual anomaly as real until a diagnostic proves otherwise.
- Write the lesson after the result, including for discarded and crashed runs.
- Never present a simulated result as fabricated or measured.
- A cloud solver needs the user's explicit approval.

## Strategy that held up in practice

- Field per ampere is geometry; amperes per watt is matching.
- Remove inductance that makes no field at the NV region (feed legs) before anything else.
- Gains go roughly as 1 / loop radius until the NV region reaches the trace.
- On thick copper, widening a trace buys little resistance (current rides the edges) and
  costs uniformity.
- With a figure of merit at the band edge, a broad imperfect match beats a sharp one.

Reference run: `Projects/Microwave Design/omega_pcb_v1/` (7 experiments, about 15 s each).

Related skills: `microwave-solver-selection`, `microwave-gds-design`, `openems`, `palace`,
`qucs-s`.
