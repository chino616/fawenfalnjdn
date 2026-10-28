"""Explicit observation inputs for the two protected legacy folding strategies."""
from dataclasses import dataclass,field
from pathlib import Path
import hashlib
from cevns_pyeft.contracts.modules import ModuleDescriptor

@dataclass(frozen=True)
class TabulatedEfficiency:
    path: object
    columns: tuple
    low: float
    threshold: float | None = None
    _evaluate: object = field(init=False,repr=False,compare=False)
    def __post_init__(self):
        from cevns_pyeft.experiments.base import _interp_eff
        object.__setattr__(self,'path',Path(self.path).resolve())
        object.__setattr__(self,'columns',tuple(self.columns))
        object.__setattr__(self,'_evaluate',_interp_eff(self.path,*self.columns,low=self.low,threshold=self.threshold))
    def __call__(self,x):return self._evaluate(x)
    def describe(self):
        return {'model_id':'legacy_tabulated_efficiency','path':str(self.path),'columns':self.columns,'low':self.low,'threshold':self.threshold}

@dataclass(frozen=True)
class DeterministicPEObservation:
    pe_per_keV: float
    slow_pe_nodes: int
    efficiency: object
    axis_name: str = field(default='reconstructed PE spectrum',init=False)
    axis_unit: str = field(default='PE',init=False)
    def describe(self):
        return ModuleDescriptor('observation','deterministic_PE_legacy',parameters={'pe_per_keV':self.pe_per_keV,
            'slow_pe_nodes':self.slow_pe_nodes,'efficiency':self.efficiency.describe()})

@dataclass(frozen=True)
class ObservedGaussianObservation:
    mean_linear: float
    mean_quadratic: float
    sigma_coefficient: float
    efficiency: object
    axis_name: str = field(default='reconstructed PE spectrum',init=False)
    axis_unit: str = field(default='PE',init=False)
    def describe(self):
        return ModuleDescriptor('observation','sigma_observed_Gaussian_legacy',parameters={'mean_linear':self.mean_linear,
            'mean_quadratic':self.mean_quadratic,'sigma_coefficient':self.sigma_coefficient,'efficiency':self.efficiency.describe()})
