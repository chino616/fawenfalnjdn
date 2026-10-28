from __future__ import annotations

from .datasets import BinnedDataset, ar2020_dataset, csi2017_dataset, csi2021_dataset
from .observables import PredictionVector, validate_prediction_for_observable
from .profiling import (
    ProfileResult,
    profile_ar2020_bounded,
    profile_ar2020_irls,
    profile_gaussian_one_pull,
    profile_gaussian_two_pull,
)


def chi2_csi2021(prediction: PredictionVector, dataset: BinnedDataset | None = None) -> ProfileResult:
    ds = dataset or csi2021_dataset()
    signal = validate_prediction_for_observable(prediction, ds.observable)
    if ds.background is None or ds.uncertainty is None:
        raise ValueError("CsI2021 dataset requires background and symmetric uncertainty")
    return profile_gaussian_two_pull(
        signal,
        ds.observed,
        ds.background,
        ds.uncertainty,
        sigma_alpha=float(ds.signal_norm_sigma),
        sigma_beta=float(ds.background_norm_sigma),
    )


def chi2_csi2017(prediction: PredictionVector, dataset: BinnedDataset | None = None) -> ProfileResult:
    ds = dataset or csi2017_dataset()
    signal = validate_prediction_for_observable(prediction, ds.observable)
    if ds.uncertainty is None:
        raise ValueError("CsI2017 dataset requires symmetric uncertainty")
    return profile_gaussian_one_pull(
        signal,
        ds.observed,
        ds.uncertainty,
        sigma_alpha=float(ds.signal_norm_sigma),
    )


def chi2_ar2020_irls(prediction: PredictionVector, dataset: BinnedDataset | None = None) -> ProfileResult:
    ds = dataset or ar2020_dataset()
    signal = validate_prediction_for_observable(prediction, ds.observable)
    if ds.background is None or ds.lower is None or ds.upper is None:
        raise ValueError("Ar2020 dataset requires background and asymmetric lower/upper arrays")
    return profile_ar2020_irls(
        signal,
        ds.observed,
        ds.background,
        ds.lower,
        ds.upper,
        sigma_alpha=float(ds.signal_norm_sigma),
        sigma_beta=float(ds.background_norm_sigma),
    )


def chi2_ar2020_bounded(prediction: PredictionVector, dataset: BinnedDataset | None = None) -> ProfileResult:
    ds = dataset or ar2020_dataset()
    signal = validate_prediction_for_observable(prediction, ds.observable)
    if ds.background is None or ds.lower is None or ds.upper is None:
        raise ValueError("Ar2020 dataset requires background and asymmetric lower/upper arrays")
    return profile_ar2020_bounded(
        signal,
        ds.observed,
        ds.background,
        ds.lower,
        ds.upper,
        sigma_alpha=float(ds.signal_norm_sigma),
        sigma_beta=float(ds.background_norm_sigma),
    )


def chi2_for_dataset(
    prediction: PredictionVector,
    dataset: BinnedDataset,
    *,
    ar_method: str = "irls",
) -> ProfileResult:
    key = dataset.name.lower()
    if key == "csi2021":
        return chi2_csi2021(prediction, dataset)
    if key == "csi2017":
        return chi2_csi2017(prediction, dataset)
    if key == "ar2020":
        if ar_method == "irls":
            return chi2_ar2020_irls(prediction, dataset)
        if ar_method in {"bounded", "minimize"}:
            return chi2_ar2020_bounded(prediction, dataset)
        raise ValueError("ar_method must be 'irls' or 'bounded'")
    raise ValueError(f"unsupported dataset: {dataset.name!r}")


def sum_chi2(profiles: list[ProfileResult] | tuple[ProfileResult, ...]) -> float:
    return float(sum(float(profile.chi2) for profile in profiles))


__all__ = [
    "chi2_ar2020_bounded",
    "chi2_ar2020_irls",
    "chi2_csi2017",
    "chi2_csi2021",
    "chi2_for_dataset",
    "sum_chi2",
]
