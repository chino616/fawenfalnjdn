from dataclasses import dataclass, field
from typing import Mapping, Protocol
import numpy as np
from cevns_pyeft.sources.state import validate_density_matrices, validate_particle_kind
from .parameters import StateParameters
from .modules import ModuleDescriptor
from .validation import coordinates, freeze, positive, readonly


@dataclass(frozen=True)
class POTExposure:
    total_pot: float
    run_id: str = "run"

    def __post_init__(self):
        positive(self.total_pot, "total_pot", zero=True)
        if not self.run_id:
            raise ValueError("run_id is required")


@dataclass(frozen=True)
class LiveTimeExposure:
    seconds: float
    run_id: str

    def __post_init__(self):
        positive(self.seconds, "seconds", zero=True)
        if not self.run_id:
            raise ValueError("run_id is required")


@dataclass(frozen=True)
class IntegratedRunReference:
    run_id: str

    def __post_init__(self):
        if not self.run_id:
            raise ValueError("run_id is required")


RunExposure = POTExposure | LiveTimeExposure | IntegratedRunReference


@dataclass(frozen=True)
class EnergySupport:
    integration_domain_MeV: tuple[float, float]
    tabulation_domain_MeV: tuple[float, float] | None = None
    physical_domain_MeV: tuple[float, float] | None = None
    breakpoints_MeV: tuple[float, ...] = ()
    outside_policy: str = "zero"
    interpolation_id: str = "none"
    convention_id: str = "explicit"

    def __post_init__(self):
        for name in ("integration_domain_MeV", "tabulation_domain_MeV", "physical_domain_MeV"):
            pair = getattr(self, name)
            if pair is not None:
                if len(pair) != 2 or not np.all(np.isfinite(pair)) or pair[0] < 0 or pair[1] <= pair[0]:
                    raise ValueError(f"invalid {name}")
                object.__setattr__(self, name, tuple(pair))
        lo, hi = self.integration_domain_MeV
        breaks = tuple(self.breakpoints_MeV)
        if any(not lo < x < hi for x in breaks) or any(b <= a for a, b in zip(breaks, breaks[1:])):
            raise ValueError("breakpoints must be strictly increasing inside integration domain")
        object.__setattr__(self, "breakpoints_MeV", breaks)
        if self.outside_policy != "zero":
            raise ValueError("only explicit zero outside support is implemented")


@dataclass(frozen=True)
class FluenceLine:
    line_id: str
    energy_MeV: float
    fluence_per_cm2: float

    def __post_init__(self):
        if not self.line_id:
            raise ValueError("line_id is required")
        positive(self.energy_MeV, "line energy")
        positive(self.fluence_per_cm2, "line fluence", zero=True)


@dataclass(frozen=True)
class IncidentStateBatch:
    energy_MeV: np.ndarray
    rho: np.ndarray
    particle_kind: str
    state_model_id: str
    parameter_dependencies: tuple[str, ...] = ()

    def __post_init__(self):
        energy = coordinates(self.energy_MeV, "state energy")
        if np.any(energy <= 0):
            raise ValueError("state energy must be positive")
        object.__setattr__(self, "energy_MeV", energy)
        object.__setattr__(self, "particle_kind", validate_particle_kind(self.particle_kind))
        object.__setattr__(self, "rho", readonly(validate_density_matrices(self.rho, energy_shape=energy.shape), dtype=complex))

    def require_coordinates(self, energy_MeV, particle_kind):
        if not np.array_equal(self.energy_MeV, energy_MeV) or self.particle_kind != particle_kind:
            raise ValueError("incident state coordinates or particle identity do not match query")


class FluenceComponent(Protocol):
    component_id: str
    particle_kind: str
    support: EnergySupport
    lines: tuple[FluenceLine, ...]

    def continuum(self, energy_MeV: np.ndarray) -> np.ndarray: ...
    def state_at(self, energy_MeV: np.ndarray, *, parameters: StateParameters) -> IncidentStateBatch: ...


@dataclass(frozen=True)
class DetectorFluence:
    components: tuple[FluenceComponent, ...]
    run_id: str
    normalization_record: Mapping = field(default_factory=dict)
    continuum_unit: str = "cm^-2 MeV^-1"
    line_unit: str = "cm^-2"

    def __post_init__(self):
        if self.continuum_unit != "cm^-2 MeV^-1" or self.line_unit != "cm^-2":
            raise ValueError("DetectorFluence requires cm^-2 MeV^-1 continuum and cm^-2 lines")
        if not self.run_id:
            raise ValueError("run_id is required")
        components = tuple(self.components)
        ids = [part.component_id for part in components]
        if len(set(ids)) != len(ids) or any(not name for name in ids):
            raise ValueError("fluence component IDs must be unique and nonempty")
        for part in components:
            validate_particle_kind(part.particle_kind)
            line_ids = [line.line_id for line in part.lines]
            if len(set(line_ids)) != len(line_ids):
                raise ValueError(f"duplicate line IDs in {part.component_id}")
        object.__setattr__(self, "components", components)
        object.__setattr__(self, "normalization_record", freeze(self.normalization_record))


class SourceModel(Protocol):
    def for_run(self, run: RunExposure) -> DetectorFluence: ...
    def describe(self) -> ModuleDescriptor: ...
