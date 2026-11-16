# PhotonForge PDK Index

## Installed Packages

```python
import photonforge as pf

import siepic_forge
pf.config.default_technology = siepic_forge.ebeam()
print(siepic_forge.component_names)

import siepic_sin_forge
pf.config.default_technology = siepic_sin_forge.ebeam()
print(siepic_sin_forge.component_names)

import luxtelligence_lnoi400_forge as lnoi
pf.config.default_technology = lnoi.lnoi400()
print(lnoi.component_names)

import luxtelligence_ltoi300_forge as ltoi
pf.config.default_technology = ltoi.ltoi300()
print(ltoi.component_names)
```

## Local Source Repos

| PDK | Source repo |
| --- | --- |
| SiEPIC Si and SiN | `Photonics_Ecosystem/repos/siepic-forge` |
| Luxtelligence LNOI400 and LTOI300 | `Photonics_Ecosystem/repos/luxtelligence-forge` |

## Process Fit

Use SiEPIC SiN as the first public PDK reference for this Device Fabrication workspace. Treat Luxtelligence PDKs as broader PhotonForge capability references unless the task is about TFLN/TFLT specifically.
