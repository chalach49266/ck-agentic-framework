---
name: phido-design
description: >
  Use this skill when the user asks to design, query, or work with PhIDO (Photonics Intelligent
  Design and Optimization) photonic integrated circuits. Trigger phrases include: "PhIDO",
  "phido", "photonic circuit design", "silicon photonics", "MZI heater", "TiN heater",
  "PIN diode MZI", "PN diode", "ring resonator", "WDM demultiplexer", "traveling wave MZM",
  "SOI photonics", "photonic PDK", "component library", "SAX simulation", "photonic netlist",
  "GDS layout silicon", "DRC photonic", "MZI modulator", "thermo-optic", "plasma dispersion",
  "photonic circuit YAML", "photonic schematic", "edge coupler", "grating coupler photonic",
  "polarization splitter", "mode converter", "waveguide crossing", "directional coupler silicon".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: "[description of photonic circuit or component query]"
---

# PhIDO Photonic Circuit Design Skill

You are an expert in **PhIDO** (Photonics Intelligent Design and Optimization), a silicon photonics component library and AI-powered design automation tool. The library is located at:

```
{{PHD_ROOT}}/Device Fabrication/Photonics_Ecosystem/repos/phido/
```

PhIDO is built on **GDSFactory** (layout), **SAX** (S-parameter circuit simulation), and **KLayout** (DRC). It targets **silicon-on-insulator (SOI)** platforms, primarily **C-band (1530–1565 nm)**.

---

## Technology Platform

- **Waveguide:** Single-mode strip, 0.5 µm width
- **Primary band:** C-band (1450–1650 nm); some components support O-band
- **Modulation types:** Thermo-optic (TO), Plasma dispersion (PN/PIN), Traveling-wave RF
- **Simulation:** Pre-computed FDTD (.npz files) + analytical models via SAX

### Layer Stack
| Layer | Material | Number |
|-------|----------|--------|
| WG core | Silicon waveguide | 1 |
| Slab | Silicon slab | 3 |
| N-doped | N-type implant | 20 |
| P-doped | P-type implant | 21 |
| N++ | Heavy N-dope | 24 |
| P++ | Heavy P-dope | 25 |
| TiN heater | TiN resistor | 47 |
| M1/M2/M3 | Metal interconnects | 41, 45, 46 |
| Via | Contact vias | 44 |

---

## Complete Component Library (35 Components)

### Port Naming Convention
- Ports: `o1, o2, o3, o4, ...` (counter-clockwise)
- Inputs: `o1, o2` (left side); Outputs: `o3, o4` (right side)
- 1×N ports: sequential left-to-right numbering

---

### 1. Passive Routing

#### `straight`
- **Ports:** 1×1 (`o1` → `o2`)
- **Parameters:** `length` (µm, default 10), `cross_section` (strip)
- **Models:** FDTD + analytical (neff=2.34, ng=3.4, loss=0.001 dB/µm)
- **Bandwidth:** 100 nm

#### `bend_euler`
- **Ports:** 1×1
- **Parameters:** `radius` (µm, default 10), `angle` (°, default 90), `p` (Euler param, default 0.5), `width` (default 0.5)
- **Models:** FDTD NPZ + analytical
- **Bandwidth:** 100 nm

#### `_bend_s`
- S-bend for intermediate connections

---

### 2. Beam Splitters & Couplers

#### `_mmi1x2` — MMI 1×2 Splitter
- **Ports:** 1×2 (1 input `o1`, 2 outputs `o2, o3`)
- **Parameters:**
  - `length_mmi`: 12.8 µm
  - `width_mmi`: 3.8 µm
  - `gap_mmi`: 0.25 µm
  - `length_taper`: 10.0 µm
  - `width_taper`: 1.4 µm
- **Bandwidth:** 50 nm; Loss: <0.5 dB

#### `_mmi2x2` — MMI 2×2 Coupler
- **Ports:** 2×2
- **Parameters:**
  - `length_mmi`: 5.5 µm
  - `width_mmi`: 2.5 µm
  - `gap_mmi`: 0.25 µm
  - `length_taper`: 10.0 µm, `width_taper`: 1.0 µm
- **S-params:** Reciprocal 2×2 (tau, j·kappa)
- **Bandwidth:** 50 nm

#### `_directional_coupler`
- **Ports:** 2×2
- **Parameters:** `length` (coupling length, default 20 µm), `dy` (port spacing, default 4 µm), `dx` (bend length, default 10 µm)
- **Bandwidth:** 50 nm

#### `_directional_coupler_adiabatic`
- Adiabatic variant for low-loss broadband coupling

#### `coupler_ring`
- **Ports:** 2×2 (for ring resonator input coupling)
- **Parameters:** `gap` (default 0.2 µm), `radius` (default 10 µm), `length_x` (parallel coupling, default 4 µm)
- **Bandwidth:** 100 nm

---

### 3. Ring Resonators

#### `mrr_1x1` — Micro-Ring Resonator (single bus)
- **Ports:** 1×1
- **Parameters:** `gap` (default 0.2 µm), `radius` (default 10 µm)
- **Sub-components:** `coupler_ring` + `bend_euler` + `straight`
- **Bandwidth:** 50 nm

#### `mrr_2x2` — Double-Bus Ring Resonator
- **Ports:** 2×2 (add-drop configuration)
- **Parameters:** Same as mrr_1x1
- **Bandwidth:** 50 nm

#### `mrr_1x1_heater_tin` — Tunable Ring with TiN Heater
- Thermally tunable ring resonator

#### `mrm_1x1_pndiode` — Ring Modulator with PN Diode
- High-speed ring modulator (GHz range)

---

### 4. Mach-Zehnder Interferometers

#### `mzi_arm` — MZI Arm Building Block
- **Ports:** 1×1
- **Sub-components:** 6× bend_euler + 2× straight
- **Parameter:** `length_y` (vertical arm extent)

#### `mzi1` — Basic 1×1 MZI
- **Ports:** 1×1
- **Parameters:** `delta_length` (path diff, default 10 µm), `length` (arm, default 10 µm)
- **Bandwidth:** 50 nm

#### `mzi_2x2_heater_tin_cband` — 2×2 MZI + TiN Heater ⭐
- **Ports:** 2×2
- **Parameters:** `delta_length` (default 40 µm), `length` (heater arm, default 320 µm)
- **Sub-components:** `_mmi2x2` + 2× `heater_tin_cband`
- **Specs:**
  - Band: 1450–1650 nm
  - Bandwidth: 200 KHz modulation
  - Insertion loss: 2 dB
  - Extinction ratio: 25 dB
  - Drive voltage: 0.75 V
  - Footprint: ~516 × 295 µm

#### `mzi_1x2_pindiode_cband` — 1×2 MZI + PIN Diode (VOA)
- **Ports:** 1×2
- **Parameters:** `delta_length` (default 100 µm), `length` (default 320 µm)
- **Specs:** BW 30 KHz, IL 2–20 dB (VOA capable), ER 25 dB, FP ~428 × 512 µm

#### `mzi_2x2_pindiode_cband` — 2×2 MZI + PIN Diode ⭐
- **Ports:** 2×2
- **Parameters:** `delta_length` (default 40 µm), `length` (default 320 µm)
- **Specs:** BW 1 GHz, IL 2–20 dB, ER 25 dB, FP ~502 × 462 µm

#### `mzi_1x1_heater_tin_cband` — 1×1 MZI + TiN Heater
- **Ports:** 1×1; thermo-optic phase control

#### `mzi_1x1_heater_doped_si_cband` — 1×1 MZI + Doped Si Heater

#### `mzi_1x1_pindiode_cband` — 1×1 MZI + PIN Diode

#### `mzi_2x2_pn_diode` — 2×2 MZI + PN Diode

---

### 5. Phase Shifters & Active Elements

#### `heater_tin_cband` — TiN Thermo-Optic Phase Shifter
- **Ports:** 1×1
- **Parameters:** `length` (default 300 µm)
- **Layers:** Si WG (1) + TiN (47) + Ti/TiN/Au metal stack + vias
- **Specs:** BW 30 KHz, IL 1 dB, power 25 mW, FP ~397 × 130 µm

#### `heater_doped_si_cband` — Doped Silicon Heater

#### `pndiode` — PN Junction Phase Shifter (Reverse Bias)
- **Ports:** 1×1
- **Parameters:** `length` (default 600 µm)
- **Doping:** N (layer 20) + P (layer 21) + N++/P++ contacts
- **Specs:** BW 20 GHz, IL 6.5 dB, power 2 mW, FP ~640 × 168.5 µm

#### `pindiode_cband` — PIN Junction Modulator/VOA (Forward Bias)
- **Ports:** 1×1
- **Parameters:** `length` (default 500 µm)
- **Specs:** BW 1 GHz, IL 2–20 dB (variable attenuator), FP ~510 × 162.2 µm

#### `tw_mzm` — Traveling-Wave Mach-Zehnder Modulator ⭐
- **Ports:** 1×1
- **Parameters:** `delta_length` (50 µm), `length` (320 µm), `dy` (80 µm)
- **Sub-components:** `_mmi1x2` + 2× `pndiode` + traveling-wave RF electrodes (M2/M3)
- **Specs:** BW 20 GHz, IL 6.5 dB, ER 4.4 dB, FP ~532 × 468.5 µm

---

### 6. Detectors

#### `photodetector` — Germanium Photodetector
- **Ports:** 1×1
- **Parameters:** `length` (default 40 µm)
- **Technology:** Ge-on-Si heterojunction
- **Bandwidth:** 100 nm

---

### 7. I/O & Coupling

#### `edge_coupler` — Inverse Taper Edge Coupler
- **Ports:** 1×1
- **Parameters:** `length` (default 10 µm), `width1` (0.2 µm), `width2` (0.5 µm)

#### `_gc` — Grating Coupler
- Vertical fiber-to-chip coupling

#### `mode_converter` — TE0-to-TE1 Mode Converter
- **Ports:** 2×2
- **Parameters:** `gap` (default 0.3 µm), `length` (default 10 µm)

#### `crossing` — Waveguide Crossing
- **Ports:** 2×2 (two crossing paths)
- Low-loss crossing for routing

#### `polarization_splitter_rotator` — PSR
- **Ports:** 1×2 → 2×2 effective
- **Parameters:** Multi-stage tapers, `gap` 0.15 µm, `length_coupler` 7 µm
- **Bandwidth:** 70 nm; splits TE/TM and rotates TM→TE

#### `laser` — Integrated Laser Source
- **Ports:** 1×1 output; placeholder/stub

---

### 8. Complex Circuits

#### `wdm_mzi1x4` — 1×4 CWDM Demultiplexer ⭐
- **Ports:** 1×4 (1 input, 4 wavelength outputs)
- **Architecture:** Binary MZI tree
  - Stage 1: `mzi_1x2_pindiode_cband` (splitter)
  - Stage 2: 2× `mzi_2x2_heater_tin_cband` (demux)
  - Delta lengths: [100.965, 151.4, 126.2] µm
- **Specs:** Channels at 1271/1291/1311/1331 nm, 20 nm spacing, IL 2.5 dB, ER 23 dB
- **Reference:** Optica Express DOI:10.1364/OE.21.011652
- **Footprint:** ~1 mm × 0.5 mm

---

## YAML Netlist Format

PhIDO uses a GDSFactory-compatible YAML format for circuit definition:

```yaml
instances:
  mzi1:
    component: mzi_2x2_heater_tin_cband
    settings:
      length: 320
      delta_length: 100
  pd1:
    component: photodetector
    settings:
      length: 40
  ec1:
    component: edge_coupler

routes:
  optical:
    links:
      mzi1,o3: pd1,o1
      ec1,o2: mzi1,o1
    settings:
      cross_section: strip

ports:
  input: ec1,o1
  output_thru: mzi1,o4
```

---

## Circuit Design Workflow

1. **Natural language → Entity extraction** (LLM identifies components/specs)
2. **Component selection** (match to DesignLibrary)
3. **Circuit DSL (YAML)** generation
4. **Schematic** (DOT graph visualization)
5. **Layout + Simulation** (GDSFactory layout + SAX S-param simulation)
6. **DRC** (KLayout design rule check)

---

## Common Design Recipes

### Optical Switch (2×2 MZI)
```yaml
instances:
  sw:
    component: mzi_2x2_heater_tin_cband
    settings: {length: 320, delta_length: 40}
```
- Drive one arm heater to shift phase → toggle between bar/cross state
- Switching power ~25 mW, speed ~200 KHz

### High-Speed Modulator (TW-MZM)
```yaml
instances:
  mod:
    component: tw_mzm
    settings: {length: 500, delta_length: 50}
```
- Up to 20 GHz modulation bandwidth
- Use traveling-wave RF electrodes

### Ring-Based Filter
```yaml
instances:
  ring:
    component: mrr_1x1
    settings: {gap: 0.2, radius: 10}
  bus:
    component: straight
    settings: {length: 50}
routes:
  optical:
    links:
      bus,o2: ring,o1
```

### CWDM Demux (4 channels)
```yaml
instances:
  demux:
    component: wdm_mzi1x4
```
- 1271/1291/1311/1331 nm outputs
- Thermally tunable via integrated TiN heaters

### Cascaded MZI Tree (1×N splitter)
- Use `mzi_2x2_heater_tin_cband` nodes in binary tree
- Connect `o3` of stage N to `o1` of stage N+1

---

## Modulation Technology Selection Guide

| Application | Component | BW | Technology |
|-------------|-----------|-----|------------|
| Optical switch | `mzi_2x2_heater_tin_cband` | 200 KHz | Thermo-optic |
| VOA / intensity control | `pindiode_cband` | 1 GHz | PIN plasma |
| High-speed data | `tw_mzm` | 20 GHz | PN traveling-wave |
| Phase trimming | `heater_tin_cband` | 30 KHz | Thermo-optic |
| Ring tuning | `mrr_1x1_heater_tin` | 30 KHz | Thermo-optic |

---

## Running PhIDO

```bash
cd "{{PHD_ROOT}}/Device Fabrication/Photonics_Ecosystem/repos/phido/"
export PYTHONPATH='.'
source venv/bin/activate
make run
# or: streamlit run PhotonicsAI/Photon/webapp.py
```

Web UI at `http://localhost:8501`

### API Keys required (`.env` file):
- `OPENAI_API_KEY` — always required (formatting step)
- `ANTHROPIC_API_KEY` — for Claude models
- `GOOGLEGENAI_API_KEY` — for Gemini models
- `DEEPSEEK_API_KEY`, `NVIDIA_API_KEY` — optional

---

## Simulation with SAX

Each component exposes a model function:

```python
from PhotonicsAI.KnowledgeBase.DesignLibrary.mzi_2x2_heater_tin_cband import get_model

# Get FDTD-based model
model_func = get_model(model="fdtd")

# Get analytical model (faster)
model_func = get_model(model="ana")
```

Circuit-level simulation via SAX recursive netlists uses these per-component S-parameter functions.

---

## Key File Paths

| File | Purpose |
|------|---------|
| `PhotonicsAI/KnowledgeBase/DesignLibrary/` | All 35 component `.py` files |
| `PhotonicsAI/KnowledgeBase/FDTD/cband/` | Pre-computed FDTD `.npz` models |
| `PhotonicsAI/Photon/prompts.yaml` | LLM prompts for each workflow step |
| `PhotonicsAI/Photon/templates.yaml` | Circuit templates (WDM, MZI, transceiver, IQ-mod) |
| `PhotonicsAI/Photon/DemoPDK.py` | PDK registration of all components |
| `PhotonicsAI/Photon/utils.py` | Docstring extraction, netlist tools |
| `PhotonicsAI/Photon/drc/drc_script.drc` | KLayout DRC rules |

---

## Adding Custom Components

1. Create `PhotonicsAI/KnowledgeBase/DesignLibrary/my_component.py`
2. Define geometry using GDSFactory (layers, ports)
3. Add `get_model()` returning SAX-compatible S-parameter function
4. Update `templates.yaml` and `prompts.yaml`
5. Register in `DemoPDK.py`

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: kfactory.routing.generic` | `pip install kfactory==0.21.1` |
| Logger error | `mkdir -p PhotonicsAI/log` |
| Import errors | `export PYTHONPATH='.'` |
| pygraphviz build fail | `sudo apt-get install build-essential python3-dev swig` |
| GDS layer number errors | Auto-handled by PhIDO fallback strategy |
