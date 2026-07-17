from __future__ import annotations

from typing import Callable, Dict

from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS
from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import slow_counts_ar2020
from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import slow_counts_csi2017
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import slow_counts_csi2021


EXPERIMENT_REGISTRY: Dict[str, Callable[[], dict]] = {
    "CsI2017": lambda: loadNeutrinoEmpiricalFluxSNS("CsI2017"),
    "CsI2021": lambda: loadNeutrinoEmpiricalFluxSNS("CsI2021"),
    "Ar2020": lambda: loadNeutrinoEmpiricalFluxSNS("Ar2020"),
}

EXPERIMENT_SLOW_COUNT_REGISTRY: Dict[str, Callable] = {
    "CsI2017": slow_counts_csi2017,
    "CsI2021": slow_counts_csi2021,
    "Ar2020": slow_counts_ar2020,
}


def get_experiment(name: str) -> dict:
    key = str(name).strip()
    if key not in EXPERIMENT_REGISTRY:
        raise KeyError(f"Unknown experiment {name!r}. Available: {list(EXPERIMENT_REGISTRY)}")
    return EXPERIMENT_REGISTRY[key]()


def get_slow_count_function(name: str) -> Callable:
    key = str(name).strip()
    if key not in EXPERIMENT_SLOW_COUNT_REGISTRY:
        raise KeyError(f"Unknown slow-count experiment {name!r}. Available: {list(EXPERIMENT_SLOW_COUNT_REGISTRY)}")
    return EXPERIMENT_SLOW_COUNT_REGISTRY[key]


__all__ = ["EXPERIMENT_REGISTRY", "EXPERIMENT_SLOW_COUNT_REGISTRY", "get_experiment", "get_slow_count_function"]
