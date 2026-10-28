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
    from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
    dataset = BUILTIN_CATALOG.canonical_id(str(experiment))
    if dataset not in ("CsI2021", "CsI2017", "Ar2020"):
        raise ValueError(f"legacy statistical predictor does not support {dataset!r}")
    wc = dict(wilson_np or {})
    responses = Path(responses_json) if responses_json is not None else _responses_default()
    if mode == "slow":
        if dataset == "CsI2021":
            from cevns_pyeft.contracts import IntegrationSettings, TheoryPoint
            from cevns_pyeft.core.predict import predict
            from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
            from cevns_pyeft.sources.sns import LEGACY_COMPONENT_IDS
            from .adapters import to_statistical_vector

            unknown = set(kwargs) - {"c10_mass_mode", "n_er", "n_enu", "n_pe_bin", "pe_step"}
            if unknown:
                raise TypeError(f"unexpected CsI2021 parameter(s): {sorted(unknown)}")
            model = make_csi2021_model(responses, c10_mass_mode=str(kwargs.get("c10_mass_mode", "quark_mass_resolved")))
            settings = IntegrationSettings.legacy_csi2021_v1(
                n_er=int(kwargs.get("n_er", 21)), n_enu=int(kwargs.get("n_enu", 120)),
                n_pe_bin=int(kwargs.get("n_pe_bin", 8)), pe_step=float(kwargs.get("pe_step", 3.0)))
            prediction = predict(model, parameters=TheoryPoint(wc, include_sm=bool(include_sm), sin2thetaW=float(sin2thetaW)), numerics=settings)
            components = {}
            for key in ("e", "mu", "mub", "total"):
                vector = to_statistical_vector(prediction, component_id=None if key == "total" else LEGACY_COMPONENT_IDS[key])
                components[key] = PredictionVector(vector.values, vector.observable, {
                    **dict(vector.metadata or {}),
                    "experiment": dataset, "mode": mode, "include_sm": bool(include_sm),
                    "source_component": SOURCE_COMPONENT_LABELS[key]})
            return RawComponentPrediction(dataset, mode, components, prediction.axes[0].edges.copy(), {
                "experiment": dataset, "mode": mode, "include_sm": bool(include_sm), "source_components": dict(SOURCE_COMPONENT_LABELS)})
        elif dataset == "CsI2017":
            from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import slow_counts_csi2017

            result = slow_counts_csi2017(responses, wc, include_sm=include_sm, sin2thetaW=sin2thetaW, **kwargs)
        elif dataset == "Ar2020":
            from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import slow_counts_ar2020

            result = slow_counts_ar2020(responses, wc, include_sm=include_sm, sin2thetaW=sin2thetaW, **kwargs)
        else:
            raise ValueError("experiment must be one of: CsI2021, CsI2017, Ar2020")
    elif mode == "fast":
        if kwargs:
            raise TypeError(f"saved kernel cannot consume overrides: {sorted(kwargs)}")
        if fast_kernel_path is None:
            raise ValueError("fast mode requires fast_kernel_path")
        from cevns_pyeft.kernels.storage import load_fastscan_template
        from cevns_pyeft.kernels.basis import coeff_tensor_from_triplets
        from cevns_pyeft.kernels.reconstruction import reconstruct_counts_from_kernel
        _kernel = load_fastscan_template(fast_kernel_path)
        actual_id = _kernel["metadata"].get("dataset")
        if actual_id != dataset:
            raise ValueError(f"requested dataset {dataset!r} differs from kernel dataset {actual_id!r}")
        expected = BUILTIN_CATALOG.definition(dataset).observation.edges
        if not np.array_equal(_kernel["metadata"].get("pe_bins"), _kernel["pe_bins"]) or not np.array_equal(_kernel["pe_bins"], expected):
            raise ValueError(f"{dataset}: saved kernel observation/binning mismatch")
        targets = tuple(_kernel['targets'])
        valid_targets = (('Ar40',),) if dataset == 'Ar2020' else (('CsI',),('Cs133','I127'),('Cs133','I127','CsI'))
        if targets not in valid_targets or set(_kernel['source_flavors']) != {'e','mu','mub'} or len(_kernel['source_flavors']) != 3:
            raise ValueError(f'{dataset}: saved kernel target/source layout mismatch')
        result = reconstruct_counts_from_kernel(_kernel, coeff_tensor_from_triplets(
            _kernel['basis'], wc, include_sm=include_sm, sin2thetaW=sin2thetaW))

    else:
        raise ValueError("mode must be 'slow' or 'fast'")

    prediction = _prediction_from_backend_result(
        result,
        experiment=dataset,
        mode=mode,
        include_sm=include_sm,
    )
    if mode == 'fast':
        prediction.metadata['kernel_identity'] = 'legacy_identity; checked dataset, bins, source/target layout; no full physics fingerprint'
    return prediction


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
