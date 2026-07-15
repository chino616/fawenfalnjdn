from __future__ import annotations

from typing import Callable, Dict

from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS


EXPERIMENT_REGISTRY: Dict[str, Callable[[], dict]] = {
    "CsI2017": lambda: loadNeutrinoEmpiricalFluxSNS("CsI2017"),
    "CsI2021": lambda: loadNeutrinoEmpiricalFluxSNS("CsI2021"),
    "Ar2020": lambda: loadNeutrinoEmpiricalFluxSNS("Ar2020"),
}


def get_experiment(name: str) -> dict:
    key = str(name).strip()
    if key not in EXPERIMENT_REGISTRY:
        raise KeyError(f"Unknown experiment {name!r}. Available: {list(EXPERIMENT_REGISTRY)}")
    return EXPERIMENT_REGISTRY[key]()


__all__ = ["EXPERIMENT_REGISTRY", "get_experiment"]

