# PhotonForge GDS Design Workflow

## Minimal Skeleton

```python
from dataclasses import dataclass
import photonforge as pf

@dataclass(frozen=True)
class Params:
    name: str = "PF_DEVICE"
    width: float = 0.5
    length: float = 50.0

def build(p: Params) -> pf.Component:
    pf.config.default_technology = pf.basic_technology()
    c = pf.Component(p.name)
    path = pf.Path((0, 0), p.width)
    path.segment([(p.length, 0)], width=(p.width, "constant"))
    c.add((1, 0), path)
    return c

if __name__ == "__main__":
    p = Params()
    c = build(p)
    pf.write_layout(f"{p.name}.gds", c)
```

## Project Pattern

For positive-resist masks, use:

```text
final exposure = broad write field - protected keepout
```

Keep staging layers inspectable and write only the final exposure layer.

## Local Runtime

Use:

```bash
# .venv/bin/python is not an interpreter as of 2026-09-10 (OneDrive flattened the venv
# symlinks); it exits 0 with no output. Call the base interpreter against the site-packages.
PYTHONPATH=".venv/lib/python3.12/site-packages" /opt/anaconda3/bin/python3 -u your_script.py
```

Do not assume default `python3` imports the same PhotonForge/Tidy3D environment.
