from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np

from .observables import StatisticalObservable, observable

from cevns_pyeft.experiments.coherent.csi2021_definition import DEFINITION as D21
from cevns_pyeft.experiments.coherent.csi2017_definition import DEFINITION as D17
from cevns_pyeft.experiments.coherent.ar2020_definition import DEFINITION as DAR

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


PE_BINS_9 = np.asarray(D21.observation.edges, dtype=float)
CSI2021_OBSERVED_OVER_BIN_WIDTH = np.asarray(D21.statistics.observed, dtype=float)
CSI2021_BACKGROUND_OVER_BIN_WIDTH = np.asarray(D21.statistics.background, dtype=float)
CSI2021_UNCERTAINTY_OVER_BIN_WIDTH = np.asarray(D21.statistics.uncertainty, dtype=float)

CSI2017_BINS_25 = np.asarray(D17.observation.edges, dtype=float)

AR_BINS_12 = np.asarray(DAR.observation.edges, dtype=float)
AR_OBSERVED = np.asarray(DAR.statistics.observed, dtype=float)
AR_BACKGROUND = np.asarray(DAR.statistics.background, dtype=float)
AR_LOWER = np.asarray(DAR.statistics.lower, dtype=float)
AR_UPPER = np.asarray(DAR.statistics.upper, dtype=float)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _datafiles_dir(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return _repo_root() / "data" / "datafiles"


def csi2021_dataset() -> BinnedDataset:
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
    base = _datafiles_dir(data_dir)
    paths = {
        "data": base / "COHERENT_data.txt",
        "lower": base / "COHERENT_lower.txt",
        "upper": base / "COHERENT_upper.txt",
        "spectrum": base / "COHERENT_spectrum.txt",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing CsI2017 legacy data files: " + ", ".join(missing))
    data = np.loadtxt(paths["data"])[:, 1].astype(float)
    lower = np.loadtxt(paths["lower"])[:, 1].astype(float)
    upper = np.loadtxt(paths["upper"])[:, 1].astype(float)
    spectrum = np.loadtxt(paths["spectrum"])[:, 1].astype(float)
    sigma = 0.5 * ((upper - data) + (data - lower))
    return {
        "data": data,
        "lower": lower,
        "upper": upper,
        "spectrum": spectrum,
        "sigma": np.clip(sigma, 1.0e-12, None),
    }


def csi2017_dataset(data_dir: str | Path | None = None) -> BinnedDataset:
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
    key = str(name).strip().lower()
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
