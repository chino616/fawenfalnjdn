"""Explicit fluence, flux and scaling adapters; callables own their physics."""
from dataclasses import dataclass, replace
from typing import Callable
import numpy as np
from cevns_pyeft.contracts.modules import IncompatibleNormalizationError, ModuleDescriptor, UnsupportedCapabilityError
from cevns_pyeft.contracts.source import DetectorFluence, EnergySupport, FluenceLine, IntegratedRunReference, LiveTimeExposure
from cevns_pyeft.contracts.validation import positive


@dataclass(frozen=True)
class CallableFluenceComponent:
    component_id: str
    particle_kind: str
    support: EnergySupport
    continuum_function: Callable
    state_provider: Callable
    lines: tuple[FluenceLine, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "lines", tuple(self.lines))

    def continuum(self, energy_MeV):
        return np.asarray(self.continuum_function(energy_MeV), dtype=float)

    def state_at(self, energy_MeV, *, parameters):
        return self.state_provider(energy_MeV, parameters=parameters)

    def fixed_state_for_fast(self):
        provider = getattr(self.state_provider, "fixed_state_for_fast", None)
        if provider is None:
            raise UnsupportedCapabilityError(f"{self.component_id}: state provider has no fixed-state contract")
        return provider()


@dataclass(frozen=True)
class IntegratedFluenceSource:
    fluence: DetectorFluence
    descriptor: ModuleDescriptor

    def for_run(self, run):
        if not isinstance(run, IntegratedRunReference) or run.run_id != self.fluence.run_id:
            raise IncompatibleNormalizationError("integrated fluence requires its matching run reference; no additional exposure")
        return self.fluence

    def describe(self):
        return self.descriptor


@dataclass(frozen=True)
class ScaledComponent:
    original: object
    factor: float

    def __post_init__(self):
        positive(self.factor, "fluence scale", zero=True)

    @property
    def component_id(self):
        return self.original.component_id

    @property
    def particle_kind(self):
        return self.original.particle_kind

    @property
    def support(self):
        return self.original.support

    @property
    def lines(self):
        return tuple(replace(line, fluence_per_cm2=line.fluence_per_cm2 * self.factor) for line in self.original.lines)

    def continuum(self, energy_MeV):
        return self.original.continuum(energy_MeV) * self.factor

    def state_at(self, energy_MeV, *, parameters):
        return self.original.state_at(energy_MeV, parameters=parameters)

    def fixed_state_for_fast(self):
        provider = getattr(self.original, "fixed_state_for_fast", None)
        if provider is None:
            raise UnsupportedCapabilityError(f"{self.component_id}: no fixed-state contract")
        return provider()


@dataclass(frozen=True)
class ScaledSource:
    original: object
    factor: float

    def __post_init__(self):
        positive(self.factor, "source scale", zero=True)

    def for_run(self, run):
        base = self.original.for_run(run)
        return DetectorFluence(tuple(ScaledComponent(part, self.factor) for part in base.components), base.run_id,
                               {"original": base.normalization_record, "explicit_scale": self.factor})

    def describe(self):
        return ModuleDescriptor("source", "scaled_source", capabilities=("slow_1d",),
                                parameters={"factor": self.factor, "original": self.original.describe().as_dict()},
                                dependencies=("original_source",))


@dataclass(frozen=True)
class DifferentialFluxSource:
    """Stationary detector flux in cm^-2 s^-1 MeV^-1 (line weights cm^-2 s^-1)."""
    components_per_second: tuple
    descriptor: ModuleDescriptor

    def __post_init__(self):
        object.__setattr__(self, "components_per_second", tuple(self.components_per_second))

    def for_run(self, run):
        if not isinstance(run, LiveTimeExposure):
            raise IncompatibleNormalizationError("per-second flux requires LiveTimeExposure")
        return DetectorFluence(tuple(ScaledComponent(part, run.seconds) for part in self.components_per_second), run.run_id,
                               {"input_unit": "cm^-2 s^-1 MeV^-1", "live_seconds": run.seconds,
                                "output_unit": "cm^-2 MeV^-1", "geometry_included": True})

    def describe(self):
        return self.descriptor
