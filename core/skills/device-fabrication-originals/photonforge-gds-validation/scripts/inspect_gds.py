#!/usr/bin/env python3
"""Inspect a GDS file using gdstk when available, otherwise PhotonForge."""

from __future__ import annotations

import argparse
from pathlib import Path


def inspect_with_gdstk(path: Path) -> bool:
    try:
        import gdstk  # type: ignore
    except Exception:
        return False

    lib = gdstk.read_gds(str(path))
    print(f"reader: gdstk {getattr(gdstk, '__version__', 'unknown')}")
    print(f"cells: {len(lib.cells)}")
    print("top cells:", [cell.name for cell in lib.top_level()])
    layers: set[tuple[int, int]] = set()
    for cell in lib.cells:
        for polygon in cell.polygons:
            layers.add((int(polygon.layer), int(polygon.datatype)))
        for label in cell.labels:
            layers.add((int(label.layer), int(label.texttype)))
    print("layers:", sorted(layers))
    for cell in lib.top_level():
        print(f"bbox {cell.name}: {cell.bounding_box()}")
    return True


def inspect_with_photonforge(path: Path) -> None:
    import photonforge as pf

    pf.config.default_technology = pf.basic_technology()
    components = pf.load_layout(str(path))
    print(f"reader: photonforge {pf.__version__}")
    print(f"components: {len(components)}")
    print("top components:", [c.name for c in pf.find_top_level(*components.values())])
    layers: set[tuple[int, int]] = set()
    for component in components.values():
        layers.update(component.structures.keys())
    print("layers:", sorted(layers))
    for component in pf.find_top_level(*components.values()):
        print(f"bbox {component.name}: {component.bounds()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gds", type=Path)
    args = parser.parse_args()
    path = args.gds
    if not path.exists():
        raise SystemExit(f"missing file: {path}")
    print(f"file: {path}")
    print(f"size: {path.stat().st_size} bytes")
    if not inspect_with_gdstk(path):
        inspect_with_photonforge(path)


if __name__ == "__main__":
    main()
