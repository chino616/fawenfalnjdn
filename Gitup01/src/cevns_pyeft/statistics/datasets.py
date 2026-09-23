from __future__ import annotations

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


PE_BINS_9 = np.array(
    [0.001, 8.001, 12.001, 16.001, 20.001, 24.001, 32.001, 40.001, 48.001, 60.001],
    dtype=float,
)
CSI2021_OBSERVED_OVER_BIN_WIDTH = np.array(
    (1.021, 13.195, 18.941, 13.059, 11.043, 5.977, 1.838, 2.274, -0.831),
    dtype=float,
)
CSI2021_BACKGROUND_OVER_BIN_WIDTH = np.array(
    (0.0, 0.229, 0.455, 0.48, 0.429, 0.329, 0.229, 0.179, 0.154),
    dtype=float,
)
CSI2021_UNCERTAINTY_OVER_BIN_WIDTH = np.array(
    (
        0.454695767,
        3.816688713,
        4.717813051,
        4.304453263,
        3.858024691,
        2.543540564,
        2.466380071,
        2.339616402,
        1.785714286,
    ),
    dtype=float,
)

CSI2017_BINS_25 = np.linspace(0.001, 50.0, 26, dtype=float)

AR_BINS_12 = np.linspace(0.001, 120.001, 13, dtype=float)
AR_OBSERVED = np.array(
    (174.3294, 164.8672, 82.4428, 46.6318, 13.6262, 22.2221, 7.8176, 20.0156, 25.6136, 15.01212, 21.41103, 6.01039),
    dtype=float,
)
AR_BACKGROUND = np.array(
    (100.9960159, 106.1752988, 77.09163347, 59.16334661, 44.02390438, 36.45418327, 34.86055777, 28.0876494, 22.50996016, 18.92430279, 16.53386454, 16.13545817),
    dtype=float,
)
AR_LOWER = np.array(
    (143.625498, 140.0398406, 62.74900398, 29.6812749, -1.394422311, 8.167330677, -4.581673307, 7.768924303, 13.74501992, 4.183266932, 10.55776892, -3.784860558),
    dtype=float,
)
AR_UPPER = np.array(
    (218.5258964, 196.6135458, 106.5737052, 66.73306773, 30.47808765, 38.04780876, 21.71314741, 33.26693227, 38.44621514, 26.4940239, 32.8685259, 15.33864542),
    dtype=float,
)


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
        signal_norm_sigma=0.125,
        background_norm_sigma=0.35,
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
        signal_norm_sigma=0.28,
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
        signal_norm_sigma=0.12,
        background_norm_sigma=0.146,
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
