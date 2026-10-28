from dataclasses import dataclass, field, asdict
from typing import Literal, Union
import numpy as np
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.contracts.observation import BinProbabilities
from cevns_pyeft.rates.differential import p_smearing_csi
from .selection import LegacyComponentAcceptance

PE_BINS_9 = np.array([0.001, 8.001, 12.001, 16.001, 20.001, 24.001, 32.001, 40.001, 48.001, 60.001])
PE_BINS_9.setflags(write=False)
PE_WIDTHS_9 = np.diff(PE_BINS_9)
PE_WIDTHS_9.setflags(write=False)
# Keep the legacy exported mapping picklable for existing multiprocessing Fast
# builders. Each observation snapshots it into its own immutable selection.
DEFAULT_ACCEPTANCE = {"e": 0.848, "mu": 0.997, "mub": 0.848}
ArrayLike = Union[float, int, np.ndarray]
EfficiencyModel = Literal["CsI2021"]


@dataclass(frozen=True)
class CsI2021EfficiencyParams:
    a: float = 1.32045
    b: float = 0.285979
    c: float = 10.8646
    d: float = -0.3333

    def __post_init__(self):
        if not all(np.isfinite(value) for value in asdict(self).values()):
            raise ValueError("efficiency parameters must be finite")


def efficiency_csi2021(pe: ArrayLike, *, params: CsI2021EfficiencyParams = CsI2021EfficiencyParams()) -> ArrayLike:
    x = np.asarray(pe, dtype=float)
    eff = params.a / (1.0 + np.exp(-params.b * (x - params.c))) + params.d
    eff = np.maximum(eff, 0.0)
    return float(eff) if np.isscalar(pe) else eff


def efficiency(pe: ArrayLike, *, model: EfficiencyModel = "CsI2021") -> ArrayLike:
    if model != "CsI2021":
        raise ValueError(f"Unknown efficiency model: {model}")
    return efficiency_csi2021(pe)


@dataclass(frozen=True)
class CsI2021Efficiency:
    params: CsI2021EfficiencyParams = field(default_factory=CsI2021EfficiencyParams)

    def __call__(self, observed):
        return efficiency_csi2021(observed, params=self.params)

    def describe(self):
        return {"model_id": "csi2021_logistic_legacy", "parameters": asdict(self.params)}


@dataclass(frozen=True)
class ConstantEfficiency:
    value: float

    def __post_init__(self):
        if not np.isfinite(self.value) or not 0 <= self.value <= 1:
            raise ValueError("efficiency must be a probability")

    def __call__(self, observed):
        return np.full_like(np.asarray(observed, dtype=float), self.value)

    def describe(self):
        return {"model_id": "constant_efficiency", "value": self.value}


@dataclass(frozen=True)
class CsIGammaResponse:
    def density(self, observed, recoil_keV, *, target):
        return np.asarray(p_smearing_csi(observed, recoil_keV), dtype=float)

    def describe(self):
        return {"model_id": "legacy_csi_gamma", "quenching": (0.0554628, 4.30681, -111.707, 840.384),
                "gamma_a": 0.0749, "gamma_b": 9.56}


@dataclass(frozen=True)
class CsI2021Observation:
    selection: LegacyComponentAcceptance
    response: CsIGammaResponse = field(default_factory=CsIGammaResponse)
    efficiency: object = field(default_factory=CsI2021Efficiency)
    axis_name: str = field(default="reconstructed PE spectrum", init=False)
    axis_unit: str = field(default="PE", init=False)

    def validate(self, binning, component_ids):
        if len(binning.axes) != 1 or (binning.axes[0].name, binning.axes[0].unit) != (self.axis_name, self.axis_unit):
            raise ValueError("CsI observation requires the reconstructed PE axis")
        for key in component_ids:
            self.selection.acceptance(key)

    def bin_probabilities(self, *, target, recoil_keV, binning, component_id):
        from scipy.integrate import quad
        self.validate(binning, (component_id,))
        edges = binning.axes[0].edges
        acceptance = self.selection.acceptance(component_id)
        values = np.array([[quad(lambda x: float(self.response.density(x, float(t), target=target)) * float(self.efficiency(x)),
                                 a, b, epsabs=1e-11, epsrel=1e-10)[0] * acceptance
                            for a, b in zip(edges[:-1], edges[1:])] for t in recoil_keV])
        return BinProbabilities(recoil_keV, binning, values, (self.selection.selection_id,))

    def describe(self):
        return ModuleDescriptor("observation", "csi2021_legacy_observation", capabilities=("sampled_density_1d", "bin_probabilities_1d"),
                                parameters={"response": self.response.describe(), "efficiency": self.efficiency.describe(),
                                            "selection_id": self.selection.selection_id, "acceptance": self.selection.values,
                                            "axis_name": self.axis_name, "axis_unit": self.axis_unit},
                                dependencies=("response", "efficiency", "selection"))
