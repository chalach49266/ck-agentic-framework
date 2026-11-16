#!/usr/bin/env python3
"""Probe installed PhotonForge PDK imports and show sample component names."""

from importlib import import_module


PDKS = [
    ("siepic_forge", "ebeam"),
    ("siepic_sin_forge", "ebeam"),
    ("luxtelligence_lnoi400_forge", "lnoi400"),
    ("luxtelligence_ltoi300_forge", "ltoi300"),
]


def component_sample(mod: object) -> list[str]:
    names = getattr(mod, "component_names", [])
    try:
        return sorted(str(name) for name in names)[:12]
    except TypeError:
        return []


def main() -> None:
    pf = import_module("photonforge")
    print(f"photonforge: {getattr(pf, '__version__', 'unknown')}")
    for module_name, factory_name in PDKS:
        try:
            mod = import_module(module_name)
            factory = getattr(mod, factory_name)
            tech = factory()
            pf.config.default_technology = tech
            print(
                f"{module_name}: OK version={getattr(mod, '__version__', 'unknown')} "
                f"factory={factory_name}"
            )
            print(f"  sample components: {component_sample(mod)}")
        except Exception as exc:
            print(f"{module_name}: FAIL {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
