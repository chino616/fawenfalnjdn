from dataclasses import dataclass, field
from typing import Mapping
import numpy as np
from .validation import freeze, positive


@dataclass(frozen=True)
class StateParameters:
    values: Mapping = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "values", freeze(self.values))


@dataclass(frozen=True)
class TheoryPoint:
    wc_triplets: Mapping = field(default_factory=dict)
    include_sm: bool = True
    sin2thetaW: float = 0.2387
    state: StateParameters = field(default_factory=StateParameters)

    def __post_init__(self):
        object.__setattr__(self, "wc_triplets", freeze({key: np.asarray(value, dtype=complex) for key, value in self.wc_triplets.items()}))
        if not np.isfinite(self.sin2thetaW) or not 0 <= self.sin2thetaW <= 1:
            raise ValueError("sin2thetaW must lie in [0,1]")
        if not isinstance(self.state, StateParameters):
            raise TypeError("state must be StateParameters")


@dataclass(frozen=True)
class IntegrationSettings:
    n_er: int = 21
    n_enu: int = 120
    n_observed_bin: int = 8
    observed_step: float = 3.0
    recoil_min_keV: float = 0.1
    strategy: str = "legacy_csi2021_v1"

    def __post_init__(self):
        for key in ("n_er", "n_enu", "n_observed_bin"):
            value = getattr(self, key)
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 2:
                raise ValueError(f"{key} must be an integer >= 2")
        positive(self.observed_step, "observed_step")
        positive(self.recoil_min_keV, "recoil_min_keV")
        if self.strategy not in ("legacy_csi2021_v1", "bin_probability_v1"):
            raise ValueError(f"unsupported numerical strategy {self.strategy!r}")

    @classmethod
    def legacy_csi2021_v1(cls, *, n_er=21, n_enu=120, n_pe_bin=8, pe_step=3.0):
        return cls(n_er=n_er, n_enu=n_enu, n_observed_bin=n_pe_bin, observed_step=pe_step)
