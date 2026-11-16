#!/usr/bin/env python3
"""Report the active PhotonForge runtime and installed PDK packages."""

from importlib import import_module


PACKAGES = [
    "photonforge",
    "tidy3d",
    "siepic_forge",
    "siepic_sin_forge",
    "luxtelligence_lnoi400_forge",
    "luxtelligence_ltoi300_forge",
]


def main() -> None:
    for name in PACKAGES:
        try:
            mod = import_module(name)
        except Exception as exc:
            print(f"{name}: FAIL {type(exc).__name__}: {exc}")
            continue
        print(
            f"{name}: OK version={getattr(mod, '__version__', 'unknown')} "
            f"file={getattr(mod, '__file__', 'unknown')}"
        )


if __name__ == "__main__":
    main()
