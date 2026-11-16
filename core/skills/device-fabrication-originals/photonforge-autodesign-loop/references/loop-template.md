# PhotonForge Autodesign Loop Template

## Files

| File | Role |
| --- | --- |
| `program.md` | Human target, constraints, allowed edits, metric |
| `design.py` | Geometry source; limit edits to one function when possible |
| `preview.py` | Generate layout/field preview before simulation |
| `drc.py` | Fabrication or geometry rule check |
| `simulate.py` | Tidy3D or local metric extraction |
| `orchestrate.py` | Log, compare, keep/discard |
| `output/principles.md` | Literature/design principles |
| `output/journal.md` | Hypothesis and lesson log |
| `output/results.tsv` | Structured result table |

## Minimum Loop

```text
read constraints -> propose one change -> edit -> preview -> validate -> simulate -> log -> keep/discard
```

Do not skip preview or validation to save time; those steps protect cloud budget and fabrication relevance.
