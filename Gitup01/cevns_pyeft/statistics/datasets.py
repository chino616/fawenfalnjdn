from __future__ import annotations
from cevns_pyeft.foundation.paths import resource_root

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np

from .observables import StatisticalObservable, observable


UncertaintyKind = Literal["symmetric", "asymmetric"]


@dataclass(frozen=True)
class BinnedDataset:
    name: str
    observed: np.ndarray
    observable: StatisticalObservable
    background: np.ndarray | None = None
    uncertainty: np.ndarray | None = None
    lower: np.ndarray | None = None
    upper: np.ndarray | None = None
    signal_norm_sigma: float | None = None
    background_norm_sigma: float | None = None
    uncertainty_kind: UncertaintyKind = "symmetric"
    provenance_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def n_bins(self) -> int:
        return int(self.observed.size)


_CONSTANTS = {
    'PE_BINS_9': ('CsI2021','observation','edges'),
    'CSI2021_OBSERVED_OVER_BIN_WIDTH': ('CsI2021','statistics','observed'),
    'CSI2021_BACKGROUND_OVER_BIN_WIDTH': ('CsI2021','statistics','background'),
    'CSI2021_UNCERTAINTY_OVER_BIN_WIDTH': ('CsI2021','statistics','uncertainty'),
    'CSI2017_BINS_25': ('CsI2017','observation','edges'),
    'AR_BINS_12': ('Ar2020','observation','edges'),
    'AR_OBSERVED': ('Ar2020','statistics','observed'),
    'AR_BACKGROUND': ('Ar2020','statistics','background'),
    'AR_LOWER': ('Ar2020','statistics','lower'),
    'AR_UPPER': ('Ar2020','statistics','upper'),
}

def _definition(sid):
    from importlib import import_module
    from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG, UninstalledExperimentError
    entry=BUILTIN_CATALOG.manifest_entry(sid)
    if not entry.installed:raise UninstalledExperimentError(sid)
    return import_module('.'+entry.definition,'cevns_pyeft.experiments').DEFINITION

def _constant(name):
    sid,section,field=_CONSTANTS[name]
    return np.asarray(getattr(getattr(_definition(sid),section),field),dtype=float)

def __getattr__(name):
    if name in _CONSTANTS:return _constant(name)
    aliases={'D21':'CsI2021','D17':'CsI2017','DAR':'Ar2020'}
    if name in aliases:return _definition(aliases[name])
    raise AttributeError(name)



def _repo_root() -> Path:
    return resource_root()


def _datafiles_dir(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return _repo_root() / "data" / "datafiles"


def _ensure_statistics_loadable(dataset_id: str) -> str:
    """Reject archived/spec-only IDs before legacy statistics are loaded.

    The legacy dataset functions intentionally keep their historical numerical
    implementations. Their lifecycle boundary belongs to the experiment
    Catalog so an archived definition cannot be reintroduced by a fixed-name
    statistics branch.
    """
    from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG

    try:
        canonical = BUILTIN_CATALOG.canonical_id(dataset_id)
    except KeyError:
        # Preserve the historical unknown-name behavior of each caller.
        return str(dataset_id)
    BUILTIN_CATALOG.ensure_loadable(canonical)
    return canonical


def csi2021_dataset() -> BinnedDataset:
    _ensure_statistics_loadable("CsI2021")
    D21 = _definition("CsI2021")
    PE_BINS_9 = _constant("PE_BINS_9")
    CSI2021_OBSERVED_OVER_BIN_WIDTH = _constant("CSI2021_OBSERVED_OVER_BIN_WIDTH")
    CSI2021_BACKGROUND_OVER_BIN_WIDTH = _constant("CSI2021_BACKGROUND_OVER_BIN_WIDTH")
    CSI2021_UNCERTAINTY_OVER_BIN_WIDTH = _constant("CSI2021_UNCERTAINTY_OVER_BIN_WIDTH")
    return BinnedDataset(
        name="CsI2021",
        observed=CSI2021_OBSERVED_OVER_BIN_WIDTH.copy(),
        background=CSI2021_BACKGROUND_OVER_BIN_WIDTH.copy(),
        uncertainty=CSI2021_UNCERTAINTY_OVER_BIN_WIDTH.copy(),
        observable=observable("PE residual spectrum", "counts/PE", PE_BINS_9),
        signal_norm_sigma=D21.statistics.signal_sigma,
        background_norm_sigma=D21.statistics.background_sigma,
        provenance_path="data/experiments/CsI2021/statistics/provenance.yaml",
        metadata={
            "status": "legacy approximate statistics",
            "legacy_source": "cutoff_single.py/cutoff_multi.py CsI2021 profile",
        },
    )


def load_csi2017_reference_data(data_dir: str | Path | None = None) -> dict[str, np.ndarray]:
    _ensure_statistics_loadable("CsI2017")
    if data_dir is None:
        definition=_definition('CsI2017')
        if definition.statistics.observed:
            from cevns_pyeft.experiments.package_loader import read_package
            from cevns_pyeft.foundation.paths import resource_root
            data,arrays=read_package(resource_root()/'data/experiments/COHERENT_CsI/CsI2017')
            s=data['assembly']['statistics']
            return {key:np.array(arrays[s[field+'_ref']],copy=True) for key,field in
                [('data','observed'),('lower','lower'),('upper','upper'),('sigma','uncertainty'),('spectrum','spectrum')]}
    CSI2017_BINS_25 = _constant("CSI2017_BINS_25")
    from cevns_pyeft.foundation.resources import resolve_resource
    from .tables import csi2017_tables
    root=_repo_root()
    canonical='data/experiments/COHERENT_CsI/CsI2017/statistics/'
    paths={key:(Path(data_dir)/f'COHERENT_{key}.txt' if data_dir is not None else resolve_resource(root,canonical+f'COHERENT_{key}.txt')) for key in ('data','lower','upper','spectrum')}
    explicit_schema=Path(data_dir)/'observation_schema.json' if data_dir is not None else root/canonical/'observation_schema.json'
    schema_path=explicit_schema if explicit_schema.exists() else root/canonical/'observation_schema.json'
    return csi2017_tables(paths,schema_path,CSI2017_BINS_25)


def csi2017_dataset(data_dir: str | Path | None = None) -> BinnedDataset:
    _ensure_statistics_loadable("CsI2017")
    D17 = _definition("CsI2017")
    CSI2017_BINS_25 = _constant("CSI2017_BINS_25")
    ref = load_csi2017_reference_data(data_dir)
    return BinnedDataset(
        name="CsI2017",
        observed=ref["data"],
        lower=ref["lower"],
        upper=ref["upper"],
        uncertainty=ref["sigma"],
        observable=observable("PE residual spectrum", "counts/bin", CSI2017_BINS_25),
        signal_norm_sigma=D17.statistics.signal_sigma,
        provenance_path="data/experiments/CsI2017/statistics/provenance.yaml",
        metadata={
            "status": "legacy approximate statistics",
            "legacy_source": "COHERENT_data/lower/upper/spectrum text files",
            "spectrum_reference": ref["spectrum"],
        },
    )


def ar2020_dataset() -> BinnedDataset:
    _ensure_statistics_loadable("Ar2020")
    DAR = _definition("Ar2020")
    AR_BINS_12 = _constant("AR_BINS_12")
    AR_OBSERVED = _constant("AR_OBSERVED")
    AR_BACKGROUND = _constant("AR_BACKGROUND")
    AR_LOWER = _constant("AR_LOWER")
    AR_UPPER = _constant("AR_UPPER")
    return BinnedDataset(
        name="Ar2020",
        observed=AR_OBSERVED.copy(),
        background=AR_BACKGROUND.copy(),
        lower=AR_LOWER.copy(),
        upper=AR_UPPER.copy(),
        observable=observable("PE spectrum", "counts/bin", AR_BINS_12),
        signal_norm_sigma=DAR.statistics.signal_sigma,
        background_norm_sigma=DAR.statistics.background_sigma,
        uncertainty_kind="asymmetric",
        provenance_path="data/experiments/Ar2020/statistics/provenance.yaml",
        metadata={
            "status": "legacy approximate statistics",
            "legacy_source": "cutoff_multi.py/chi2_2d.py Ar2020 arrays",
        },
    )


def load_dataset(name: str, *, data_dir: str | Path | None = None) -> BinnedDataset:
    canonical = _ensure_statistics_loadable(str(name).strip())
    key = canonical.lower()
    if key == "csi2021":
        return csi2021_dataset()
    if key == "csi2017":
        return csi2017_dataset(data_dir)
    if key == "ar2020":
        return ar2020_dataset()
    raise ValueError("dataset must be one of: CsI2021, CsI2017, Ar2020")


__all__ = [
    "AR_BACKGROUND",
    "AR_BINS_12",
    "AR_LOWER",
    "AR_OBSERVED",
    "AR_UPPER",
    "BinnedDataset",
    "CSI2017_BINS_25",
    "CSI2021_BACKGROUND_OVER_BIN_WIDTH",
    "CSI2021_OBSERVED_OVER_BIN_WIDTH",
    "CSI2021_UNCERTAINTY_OVER_BIN_WIDTH",
    "PE_BINS_9",
    "ar2020_dataset",
    "csi2017_dataset",
    "csi2021_dataset",
    "load_csi2017_reference_data",
    "load_dataset",
]


def _installed_constant(name):
    if name not in _CONSTANTS:return True
    from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
    try:return BUILTIN_CATALOG.manifest_entry(_CONSTANTS[name][0]).installed
    except KeyError:return False

__all__ = [name for name in __all__ if _installed_constant(name)]
