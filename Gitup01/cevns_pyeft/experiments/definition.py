"""Immutable dataset definitions, separate from numerical implementations."""
from dataclasses import dataclass, field, is_dataclass, replace
from collections.abc import Mapping
from types import MappingProxyType
from pathlib import Path
import hashlib
import json

def plain(value):
    if is_dataclass(value):
        return {k: plain(getattr(value, k)) for k in value.__dataclass_fields__}
    if isinstance(value, Mapping):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if hasattr(value, 'tolist'):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    return value

def digest(value):
    return hashlib.sha256(json.dumps(plain(value), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def snapshot(value):
    """Copy caller-owned containers recursively, including fields of frozen dataclasses."""
    import copy
    from dataclasses import fields
    if isinstance(value, Mapping):
        return MappingProxyType({k:snapshot(v) for k,v in value.items()})
    if isinstance(value,(list,tuple)):
        return tuple(snapshot(v) for v in value)
    if hasattr(value,'setflags'):
        result=value.copy();result.setflags(write=False);return result
    if is_dataclass(value) and not isinstance(value,type):
        return replace(value,**{f.name:snapshot(getattr(value,f.name)) for f in fields(value) if f.init})
    if callable(value) and hasattr(value,'__code__'):
        return value
    if hasattr(value,'describe') and hasattr(value,'__dict__'):
        result=copy.copy(value)
        for key,item in vars(value).items():object.__setattr__(result,key,snapshot(item))
        return result
    return value


def frozen_mapping(value):
    return snapshot(value)

@dataclass(frozen=True)
class ResourceRef:
    id: str
    path: str
    role: str = 'physical'
    semantic: str = ''

@dataclass(frozen=True)
class ObservationDefinition:
    name: str
    unit: str
    edges: tuple[float, ...]
    detector_ids: tuple[str, ...] = ('detector',)
    aggregation: str = 'sum_identical_bins'

    def __post_init__(self):
        import math
        object.__setattr__(self,'edges',tuple(self.edges))
        object.__setattr__(self,'detector_ids',tuple(self.detector_ids))
        if len(self.edges) < 2 or any(not math.isfinite(x) for x in self.edges) or any(b <= a for a,b in zip(self.edges, self.edges[1:])):
            raise ValueError('observation edges must be finite and strictly increasing')
        if len(set(self.detector_ids)) != len(self.detector_ids):
            raise ValueError('duplicate detector identities')

@dataclass(frozen=True)
class SNSRun:
    mass_metadata_kg: float
    baseline_m: float
    total_pot: float
    yield_per_pot: float
    energy_tabulation: tuple[float, float] = (.001, 300.)
    node_support: tuple[float, float] = (.001, 56.)
    num_points: int = 200
    interpolation: bool = True

    def legacy_dataset(self, dataset_id):
        from .coherent.sns import SNSDataset
        return SNSDataset(dataset_id, self.mass_metadata_kg, self.baseline_m, self.total_pot, self.yield_per_pot,
                          *self.energy_tabulation, *self.node_support)

@dataclass(frozen=True)
class StatisticsDefinition:
    evaluator: str
    signal_sigma: float
    background_sigma: float | None = None
    observed: tuple = ()
    background: tuple = ()
    uncertainty: tuple = ()
    lower: tuple = ()
    upper: tuple = ()
    status: str = 'legacy approximate statistics'
    required_exposures: tuple = ()
    kind: str = 'gaussian_one_pull'
    observable_unit: str = 'counts/bin'
    bound_observation: str | None = None
    observable_name: str = 'PE residual spectrum' 

@dataclass(frozen=True)
class ExperimentDefinition:
    dataset_id: str
    experiment_slug: str
    analysis_revision: str
    run_refs: tuple[str, ...]
    physical: object
    observation: ObservationDefinition
    resources: tuple[ResourceRef, ...]
    numerical_profiles: Mapping
    prepare: object
    statistics: StatisticsDefinition | None = None
    release_id: str | None = None
    reproduction_sin2thetaW: float = .2387
    capabilities: Mapping = field(default_factory=dict)
    validation: tuple[str, ...] = ('tests/test_experiment_modularization.py',)

    def __post_init__(self):
        object.__setattr__(self,'physical',snapshot(self.physical))
        object.__setattr__(self,'observation',snapshot(self.observation))
        object.__setattr__(self,'statistics',snapshot(self.statistics))
        object.__setattr__(self,'resources',snapshot(self.resources))
        object.__setattr__(self,'run_refs',tuple(self.run_refs))
        if not self.dataset_id or not callable(self.prepare):
            raise ValueError('definition needs dataset_id and a prepare callable')
        if len({r.id for r in self.resources}) != len(self.resources):
            raise ValueError('duplicate resource IDs')
        if self.statistics is not None and self.statistics.bound_observation is None:
            object.__setattr__(self,'statistics',replace(self.statistics,bound_observation=digest(self.observation)))
        object.__setattr__(self, 'numerical_profiles', frozen_mapping(self.numerical_profiles))
        object.__setattr__(self, 'capabilities', frozen_mapping(self.capabilities))

    def describe(self):
        return {k: plain(getattr(self, k)) for k in self.__dataclass_fields__ if k != 'prepare'}

@dataclass(frozen=True)
class MassTimeExposure:
    """Integrated mass-time; never expanded into invented mass/live time."""
    detector_id: str
    kg_day: float

    def __post_init__(self):
        import math
        if not math.isfinite(self.kg_day) or self.kg_day < 0:
            raise ValueError('kg_day must be finite and non-negative')


def implementation_record(definition):
    """Content hashes of the actual executor dependencies, excluding statistics."""
    from importlib.util import find_spec
    modules = getattr(definition.physical,'implementation_modules',())
    result={}
    for module in modules:
        spec=find_spec(module)
        if spec is None or spec.origin is None:
            raise ValueError(f'missing implementation dependency {module}')
        result[module]=hashlib.sha256(Path(spec.origin).read_bytes()).hexdigest()
    return result
