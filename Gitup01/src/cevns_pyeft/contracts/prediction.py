from dataclasses import dataclass, field
from typing import Mapping
import numpy as np
from .observation import Binning
from .validation import coordinates, freeze, readonly


@dataclass(frozen=True)
class RecoilYield:
    component_id: str
    isotope_id: str
    recoil_keV: np.ndarray
    values_per_keV: np.ndarray

    def __post_init__(self):
        recoil = coordinates(self.recoil_keV, "yield recoil", minimum_size=2)
        values = readonly(self.values_per_keV)
        if values.shape != recoil.shape or np.any(values < 0):
            raise ValueError("invalid per-nucleus recoil yield")
        object.__setattr__(self, "recoil_keV", recoil)
        object.__setattr__(self, "values_per_keV", values)


@dataclass(frozen=True)
class Prediction:
    counts: np.ndarray
    binning: Binning
    components: Mapping
    normalization_record: Mapping
    model_record: Mapping
    numerical_record: Mapping
    diagnostics: Mapping = field(default_factory=dict)
    unit: str = "events/bin"

    def __post_init__(self):
        counts = readonly(self.counts)
        components = {key: readonly(value) for key, value in self.components.items()}
        if self.unit != "events/bin" or counts.shape != self.binning.shape or np.any(counts < 0):
            raise ValueError("prediction shape, unit or sign mismatch")
        for key, value in components.items():
            if not isinstance(key, tuple) or len(key) != 2 or value.shape != counts.shape or np.any(value < 0):
                raise ValueError("prediction requires (source,isotope) contributions with bin axes")
        if not np.allclose(sum(components.values(), np.zeros_like(counts)), counts, rtol=1e-12, atol=1e-14):
            raise ValueError("prediction components do not sum to total")
        object.__setattr__(self, "counts", counts)
        object.__setattr__(self, "components", freeze(components))
        for key in ("normalization_record", "model_record", "numerical_record", "diagnostics"):
            object.__setattr__(self, key, freeze(getattr(self, key)))

    @property
    def axes(self):
        return self.binning.axes
