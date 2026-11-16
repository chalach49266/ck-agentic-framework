---
name: phido-photonics-library
description: >
  Use when working with the PhIDO (Photonics Intelligent Design and Optimization) photonic component
  data library, when designing or referencing photonic circuits from PhIDO's KnowledgeBase/DesignLibrary,
  when adding or documenting new photonic components in PhIDO format, or when building circuits with
  PhIDO components (MZI, MRR, MMI, bends, straight, heaters, couplers, modulators, WDM, edge couplers,
  photodetectors, lasers). Trigger phrases: "PhIDO", "PhIDO component", "DesignLibrary", "PhotonicsAI
  KnowledgeBase", "phido photonics library", "mzi_1x1_heater_tin_cband", "mrr_1x1", "PhIDO template".
---

# PhIDO Photonics Component Library Skill

Use this skill when working with the **PhIDO** (Photonics Intelligent Design and Optimization) photonic component data library in this workspace. PhIDO provides a structured design library, circuit templates, and LLM-driven workflows for photonic integrated circuit design.

## Where PhIDO Lives in This Workspace

- **Component library (Python)**: `Photonics_Ecosystem/repos/phido/PhotonicsAI/KnowledgeBase/DesignLibrary/`
- **Circuit templates (YAML)**: `Photonics_Ecosystem/repos/phido/PhotonicsAI/Photon/templates.yaml`
- **LLM prompts**: `Photonics_Ecosystem/repos/phido/PhotonicsAI/Photon/prompts.yaml`
- **PDK / layout entry**: `Photonics_Ecosystem/repos/phido/PhotonicsAI/Photon/DemoPDK.py`
- **Config (paths)**: `Photonics_Ecosystem/repos/phido/PhotonicsAI/config.py` — `PATH.pdk` points to DesignLibrary.

Component discovery is done by scanning `PATH.pdk` for `*.py` files (excluding `__init__.py`) and extracting the **module-level docstring** from each file. The docstring is used for LLM component selection and for port/spec info in the circuit DSL.

## Component File Contract

Each component in DesignLibrary is a Python module that:

1. **Docstring (required)**  
   First line is a short description. After `---` comes YAML that PhIDO parses for names, ports, labels, and args. Example:

   ```python
   """Short description.

   ---
   Name: Human-readable name
   Description: Longer description (optional).
   ports: 1x1
   NodeLabels:
       - passive
   Bandwidth: 100 nm
   Args:
       -length: straight length (um)
   """
   ```

   - **ports**: Port layout, e.g. `1x1`, `1x2`, `2x2`, `1x4`. Used for connectivity and templates.
   - **NodeLabels**: Tags for filtering (e.g. `passive`, `active`, `modulator`).
   - **Args**: Parameter names and short descriptions; shown in UI and used for schematic/layout.

2. **GDSFactory cell**  
   A `@gf.cell` function whose name matches the **filename** (without `.py`). It returns a `gf.Component` with named ports (e.g. `o1`, `o2`).

3. **SAX model (optional)**  
   A `get_model(model="fdtd"|"ana")` function that returns a dict of callables for circuit simulation (e.g. `sax.reciprocal(...)` or FDTD-derived data).

When adding or editing components, keep docstring YAML and the cell name/filename in sync so that `utils.search_directory_for_docstrings()` and DemoPDK continue to see the component.

## Component Categories (DesignLibrary)

- **Waveguides & bends**: `straight`, `bend_euler`, `_bend_s`, `_bezier_curve`
- **Splitters & couplers**: `_mmi1x2`, `_mmi2x2`, `_directional_coupler`, `_directional_coupler_adiabatic`, `coupler_ring`
- **Resonators**: `mrr_1x1`, `mrr_2x2`, `mrr_1x1_heater_tin`, `mrm_1x1_pndiode`
- **MZIs**: `mzi_arm`, `mzi1`, `mzi_1x1_heater_doped_si_cband`, `mzi_2x2_heater_tin_cband`, `mzi_1x1_pindiode_cband`, `mzi_1x2_pindiode_cband`, `mzi_2x2_pindiode_cband`, `mzi_2x2_pn_diode`
- **Phase shifters / modulators**: `heater_tin_cband`, `heater_doped_si_cband`, `pindiode_cband`, `pndiode`, `tw_mzm`
- **I/O & active**: `_gc`, `edge_coupler`, `laser`, `photodetector`
- **Other**: `crossing`, `mode_converter`, `polarization_splitter_rotator`, `wdm_mzi1x4`

For a concise list of components with ports and args, see [references/components.md](references/components.md).

## Circuit Templates and DSL

- **templates.yaml** defines named templates (e.g. `TEMPLATE_wdd0`, `CIRCUIT_wdd0`) with `doc`, `nodes`, `edges`, and `properties`. Nodes reference component **module names** (filename without `.py`) and `params` for the cell.
- Circuit DSL produced by PhIDO has `nodes` (component + params + placement) and `edges` (e.g. `link: N1,2:N2,1`). Port info for each node can be filled from the component docstring YAML (see `get_ports_info` in DemoPDK).

When suggesting or generating circuits, use component names exactly as in DesignLibrary (e.g. `mzi_1x1_heater_tin_cband`, not a different spelling).

## Adding a New Component (Checklist)

1. Add a new `.py` file in `PhotonicsAI/KnowledgeBase/DesignLibrary/` (same directory as existing components).
2. Implement the module-level docstring with `---` and YAML: `Name`, `ports`, `NodeLabels`, `Args` at minimum.
3. Implement a `@gf.cell` function with the same name as the filename; expose ports on the component.
4. Optionally implement `get_model(model="fdtd"|"ana")` for SAX simulation.
5. If the circuit should be offered in the app, add or extend entries in `PhotonicsAI/Photon/templates.yaml` and optionally prompts in `prompts.yaml`.

No need to register the file elsewhere—PhIDO discovers it via `utils.search_directory_for_docstrings(PATH.pdk)`.

## Running PhIDO

From the repo root (e.g. `Photonics_Ecosystem/repos/phido`): set `PYTHONPATH` to the release directory, then e.g. `streamlit run PhotonicsAI/Photon/webapp.py` or `make run`. Ensure a `log` directory exists under `PhotonicsAI/` if the app expects it.
