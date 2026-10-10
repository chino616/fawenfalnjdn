from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np

from .observables import PredictionVector, observable, prediction_vector
from .parameters import Triplet


SOURCE_COMPONENT_LABELS = {"e": "nu_e", "mu": "nu_mu", "mub": "nubar_mu", "total": "total"}


@dataclass(frozen=True)
class RawComponentPrediction:
    experiment: str
    mode: str
    components: dict[str, PredictionVector]
    pe_bins: np.ndarray
    metadata: dict[str, object]

    @property
    def total(self) -> PredictionVector:
        return self.components["total"]


def _responses_default() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "responses" / "responses_all.json"


def _raw_observable_from_edges(bin_edges: object):
    return observable("reconstructed PE spectrum", "events/bin", np.asarray(bin_edges, dtype=float))


def _prediction_from_backend_result(
    result: Mapping[str, object],
    *,
    experiment: str,
    mode: str,
    include_sm: bool,
) -> RawComponentPrediction:
    pe_bins = np.asarray(result["pe_bins"], dtype=float)
    stat_obs = _raw_observable_from_edges(pe_bins)
    raw_counts = result["counts_per_bin"]
    if not isinstance(raw_counts, Mapping):
        raise ValueError("backend result missing counts_per_bin mapping")
    components: dict[str, PredictionVector] = {}
    for key in ("e", "mu", "mub", "total"):
        if key not in raw_counts:
            raise ValueError(f"backend result missing source component {key!r}")
        components[key] = prediction_vector(
            np.asarray(raw_counts[key], dtype=float),
            stat_obs,
            metadata={
                "experiment": experiment,
                "mode": mode,
                "include_sm": bool(include_sm),
                "source_component": SOURCE_COMPONENT_LABELS[key],
            },
        )
    return RawComponentPrediction(
        experiment=str(experiment),
        mode=str(mode),
        components=components,
        pe_bins=pe_bins,
        metadata={
            "experiment": str(experiment),
            "mode": str(mode),
            "include_sm": bool(include_sm),
            "source_components": dict(SOURCE_COMPONENT_LABELS),
        },
    )


def predict_raw_components(
    experiment: str,
    wilson_np: Mapping[Triplet, object] | None = None,
    *,
    mode: str = "slow",
    responses_json: str | Path | None = None,
    fast_kernel_path: str | Path | None = None,
    include_sm: bool = True,
    sin2thetaW: float = 0.2387,
    **kwargs,
) -> RawComponentPrediction:
    dataset = str(experiment)
    wc = dict(wilson_np or {})
    responses = Path(responses_json) if responses_json is not None else _responses_default()
    if mode == "slow":
        if dataset == "CsI2021":
            from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import slow_counts_csi2021

            result = slow_counts_csi2021(responses, wc, include_sm=include_sm, sin2thetaW=sin2thetaW, **kwargs)
        elif dataset == "CsI2017":
            from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import slow_counts_csi2017

            result = slow_counts_csi2017(responses, wc, include_sm=include_sm, sin2thetaW=sin2thetaW, **kwargs)
        elif dataset == "Ar2020":
            from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import slow_counts_ar2020

            result = slow_counts_ar2020(responses, wc, include_sm=include_sm, sin2thetaW=sin2thetaW, **kwargs)
        else:
            raise ValueError("experiment must be one of: CsI2021, CsI2017, Ar2020")
    elif mode == "fast":
        if fast_kernel_path is None:
            raise ValueError("fast mode requires fast_kernel_path")
        from cevns_pyeft.kernels.storage import reconstruct_saved_kernel

        _kernel, result = reconstruct_saved_kernel(
            fast_kernel_path,
            wc,
            include_sm=include_sm,
            sin2thetaW=sin2thetaW,
        )
    else:
        raise ValueError("mode must be 'slow' or 'fast'")

    return _prediction_from_backend_result(
        result,
        experiment=dataset,
        mode=mode,
        include_sm=include_sm,
    )


def predict_raw_counts(
    experiment: str,
    wilson_np: Mapping[Triplet, object] | None = None,
    *,
    mode: str = "slow",
    responses_json: str | Path | None = None,
    fast_kernel_path: str | Path | None = None,
    include_sm: bool = True,
    sin2thetaW: float = 0.2387,
    **kwargs,
) -> PredictionVector:
    return predict_raw_components(
        experiment,
        wilson_np,
        mode=mode,
        responses_json=responses_json,
        fast_kernel_path=fast_kernel_path,
        include_sm=include_sm,
        sin2thetaW=sin2thetaW,
        **kwargs,
    ).total


__all__ = ["RawComponentPrediction", "SOURCE_COMPONENT_LABELS", "predict_raw_components", "predict_raw_counts"]
