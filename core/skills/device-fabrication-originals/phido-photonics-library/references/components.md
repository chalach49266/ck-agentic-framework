# PhIDO DesignLibrary — Component Reference

Summary of components in `Photonics_Ecosystem/repos/phido/PhotonicsAI/KnowledgeBase/DesignLibrary/`. Module name = filename without `.py`. Used by PhIDO for docstring search and DemoPDK.

## Component list (module_name → ports, description)

| Module name | Ports | Description |
|-------------|--------|-------------|
| `straight` | 1x1 | Straight single-mode waveguide (photonic wire). Args: length |
| `bend_euler` | 1x1 | Euler bend. Args: radius, angle, npoints |
| `_bend_s` | 1x1 | S-bend (bezier). Args: size, npoints |
| `_bezier_curve` | 1x1 | Bend with bezier curve |
| `_mmi1x2` | 1x2 | MMI 1×2 splitter. Args: length_mmi, width_mmi, gap_mmi, length_taper, width_taper |
| `_mmi2x2` | 2x2 | MMI 2×2. Args: width_mmi, length_mmi, etc. |
| `_directional_coupler` | 2x2 | Directional coupler. Args: gap, length |
| `_directional_coupler_adiabatic` | 2x2 | Adiabatic directional coupler |
| `coupler_ring` | 2x2 | Ring coupler (for rings). Args: gap, radius |
| `mrr_1x1` | 1x1 | Single-bus microring. Args: gap, radius |
| `mrr_2x2` | 2x2 | Double-bus microring |
| `mrr_1x1_heater_tin` | 1x1 | Microring with TiN heater. Args: gap, radius |
| `mrm_1x1_pndiode` | 1x1 | Microring modulator with PN diode |
| `mzi_arm` | 1x1 | MZI arm |
| `mzi1` | 1x1 | Basic MZI. Args: length, delta_length, etc. |
| `mzi_1x1_heater_doped_si_cband` | 1x1 | 1×1 MZI, doped-Si heater (C-band) |
| `mzi_2x2_heater_tin_cband` | 2x2 | 2×2 MZI, TiN heater (C-band) |
| `mzi_1x1_pindiode_cband` | 1x1 | 1×1 MZI, PIN diode (C-band) |
| `mzi_1x2_pindiode_cband` | 1x2 | 1×2 MZI, PIN diode (C-band) |
| `mzi_2x2_pindiode_cband` | 2x2 | 2×2 MZI, PIN diode (C-band) |
| `mzi_2x2_pn_diode` | 2x2 | 2×2 MZI, PN diode |
| `heater_tin_cband` | 1x1 | TiN thermo-optic heater (C-band). Args: length |
| `heater_doped_si_cband` | 1x1 | Doped-Si heater (C-band) |
| `pindiode_cband` | 1x1 | PIN diode (C-band) |
| `pndiode` | 1x1 | PN diode |
| `tw_mzm` | 1x1 | Traveling-wave MZM (pn + TW electrode) |
| `_gc` | 1x0 | Grating coupler (I/O) |
| `edge_coupler` | 1x1 | Inverse taper edge coupler |
| `laser` | 1x1 | Tunable laser |
| `photodetector` | 1x1 | Germanium photodetector |
| `crossing` | 1x1 | Waveguide crossing |
| `mode_converter` | 2x2 | TE0↔TE1 mode converter |
| `polarization_splitter_rotator` | 1x2 | PSR (TE/TM split) |
| `wdm_mzi1x4` | 1x4 | 1×4 WDM (cascaded MZI lattice) |

## Docstring YAML (after `---`)

PhIDO parses the part after `---` as YAML. Common keys:

- **Name**: Display / search name.
- **Description**: Longer text (optional).
- **ports**: Port layout string, e.g. `1x1`, `1x2`, `2x2`, `1x4`.
- **NodeLabels**: List of tags, e.g. `passive`, `active`, `modulator`.
- **Bandwidth**: Optional, e.g. `50 nm`, `100 nm`.
- **Args**: List of `-param: description` for the cell parameters.
- **aka** / **Technology** / **Design wavelength**: Optional metadata.

Example:

```yaml
Name: straight waveguide
Description: Single-mode straight waveguide.
ports: 1x1
NodeLabels:
    - passive
Bandwidth: 100 nm
Args:
    -length: straight length (um)
```

## Usage in code

- **List components**: Use `utils.search_directory_for_docstrings(directory=PATH.pdk)` (from `PhotonicsAI.Photon.utils` and `PhotonicsAI.config`). Returns list of `{module_name, docstring, file_path}`.
- **Import cell**: `from PhotonicsAI.KnowledgeBase.DesignLibrary import <module_name>` then call `<module_name>(**params)` (function name = module name).
- **Import models**: Same package; call `get_model(model="fdtd"|"ana")` from the module and use with SAX.
