"""Direct CONUS+ C2/C3/C5 event-count integration.

The implementation deliberately stays on the Slow path:

    differential reactor flux [cm^-2 s^-1 MeV^-1]
    x d sigma / dT [cm^2 keVnr^-1]
    x dE_nu [MeV]
    x nuclei per kg [kg^-1]
    x seconds per day [s day^-1]
    x detector exposure [kg day]
    x reconstructed-bin acceptance [dimensionless]
    x dT [keVnr]

No Fast kernel, cumulative cache, reference-count rescaling, thermal-power
normalization, detector mass, or live time is applied here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Tuple

import numpy as np

from cevns_pyeft.experiments.conus_plus.detector_response import (
    BIN_EDGES_EVEE,
    DETECTOR_ORDER,
    detector_bin_acceptance,
)
from cevns_pyeft.experiments.conus_plus.source import (
    COMPONENTS,
    ENERGY_SUPPORT_MEV,
    differential_flux,
    kopeikin_nodes,
    source_state,
)
from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import differential_cross_section_nn
from cevns_pyeft.theory.kinematics import (
    minimum_neutrino_energy_GeV,
    two_body_recoil_max_GeV,
)


from .definition import DEFINITION
DEFAULT_SETTINGS = DEFINITION.physical
DATASET_ID = DEFINITION.dataset_id
RESPONSE_KEY = DEFAULT_SETTINGS.response_key
SIN2_THETA_W = DEFINITION.reproduction_sin2thetaW
NUCLEI_PER_KG = DEFAULT_SETTINGS.nuclei_per_kg
SECONDS_PER_DAY = DEFAULT_SETTINGS.seconds_per_day
EXPOSURES_KG_DAY = np.asarray([x.kg_day for x in DEFAULT_SETTINGS.exposures])
EXPOSURES_KG_DAY.setflags(write=False)
ENERGY_REGION_LABELS = DEFAULT_SETTINGS.energy_region_labels
ENERGY_REGION_BOUNDS_MEV = DEFAULT_SETTINGS.energy_region_bounds_mev

DEFAULT_RESPONSE_JSON = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "responses"
    / "responses_all.json"
)

Triplet = Tuple[int, int, str]


def _gauss_interval(
    order: int,
    lower: float,
    upper: float,
) -> tuple[np.ndarray, np.ndarray]:
    if int(order) != order or order < 2:
        raise ValueError("quadrature order must be an integer >= 2")
    if not np.isfinite(lower) or not np.isfinite(upper) or upper < lower:
        raise ValueError("quadrature interval must have finite upper >= lower")
    if upper == lower:
        return np.empty(0, dtype=float), np.empty(0, dtype=float)
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    midpoint = 0.5 * (upper + lower)
    half_width = 0.5 * (upper - lower)
    return midpoint + half_width * nodes, half_width * weights


def _energy_segments(
    recoil_kev: float,
    energy_range_mev: Optional[tuple[float, float]] = None,
    *, settings=DEFAULT_SETTINGS, source_data_dir=None,
) -> tuple[tuple[float, float], ...]:
    if not np.isfinite(recoil_kev) or recoil_kev < 0.0:
        raise ValueError("recoil_kev must be finite and non-negative")

    support_min, support_max = map(float, settings.source.energy_support_mev)
    if energy_range_mev is None:
        requested_min, requested_max = support_min, support_max
    else:
        requested_min, requested_max = map(float, energy_range_mev)
        if (
            not np.isfinite(requested_min)
            or not np.isfinite(requested_max)
            or requested_max < requested_min
        ):
            raise ValueError(
                "energy_range_mev must have finite upper >= lower"
            )

    mass_gev = settings.target_A * float(c.AMU_GEV)
    kinematic_min_mev = float(
        minimum_neutrino_energy_GeV(float(recoil_kev) * c.keV, mass_gev)
        / c.MeV
    )
    minimum_mev = max(kinematic_min_mev, support_min, requested_min)
    maximum_mev = min(support_max, requested_max)
    if minimum_mev >= maximum_mev:
        return ()

    low_nodes, _ = kopeikin_nodes(data_dir=source_data_dir)
    diagnostic_breaks = np.asarray([b[1] for b in settings.energy_region_bounds_mev[:-1]], dtype=float)
    candidate_breaks = np.concatenate((low_nodes, diagnostic_breaks))
    internal_breaks = candidate_breaks[
        (candidate_breaks > minimum_mev)
        & (candidate_breaks < maximum_mev)
    ]
    breaks = np.unique(
        np.concatenate(([minimum_mev], internal_breaks, [maximum_mev]))
    )
    return tuple(
        (float(lower), float(upper))
        for lower, upper in zip(breaks[:-1], breaks[1:])
        if upper > lower
    )


def _real_nonnegative(values: np.ndarray, *, name: str) -> np.ndarray:
    array = np.asarray(values)
    if np.iscomplexobj(array):
        scale = max(1.0, float(np.max(np.abs(array.real), initial=0.0)))
        if np.max(np.abs(array.imag), initial=0.0) > 1.0e-10 * scale:
            raise ValueError(f"{name} has a non-negligible imaginary part")
        array = array.real
    array = np.asarray(array, dtype=float)
    if np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    scale = max(1.0, float(np.max(np.abs(array), initial=0.0)))
    if np.min(array, initial=0.0) < -1.0e-12 * scale:
        raise ValueError(f"{name} must be non-negative")
    return np.maximum(array, 0.0)


def true_recoil_rate_components_per_kg_day(
    recoil_kev: np.ndarray | float,
    responses_json: str | Path = DEFAULT_RESPONSE_JSON,
    wc_triplets: Optional[Mapping[Triplet, object]] = None,
    *,
    include_sm: bool = True,
    sin2theta_w: float = SIN2_THETA_W,
    n_energy: int = DEFINITION.numerical_profiles['slow']['n_energy'],
    energy_range_mev: Optional[tuple[float, float]] = None,
    c10_mass_mode: str = DEFAULT_SETTINGS.c10_mass_mode,
    settings=DEFAULT_SETTINGS, source_data_dir=None,
) -> np.ndarray:
    """Return component rates in events/(kg day keVnr).

    The output follows the recoil shape and then the four COMPONENTS.
    Energy integration is split at every Kopeikin node and the 2 MeV join.
    An optional energy range isolates a region without rescaling its flux.
    """

    original = np.asarray(recoil_kev, dtype=float)
    if np.any(~np.isfinite(original)) or np.any(original < 0.0):
        raise ValueError("recoil_kev must be finite and non-negative")
    if not np.isfinite(sin2theta_w):
        raise ValueError("sin2theta_w must be finite")

    response = ResponseDB(responses_json).get(settings.response_key)
    state = source_state()
    flat = original.reshape(-1)
    rates = np.zeros((flat.size, len(COMPONENTS)), dtype=float)

    for recoil_index, recoil in enumerate(flat):
        for lower, upper in _energy_segments(
            float(recoil),
            energy_range_mev=energy_range_mev, settings=settings, source_data_dir=source_data_dir,
        ):
            energy_mev, weights_mev = _gauss_interval(
                n_energy,
                lower,
                upper,
            )
            differential = differential_cross_section_nn(
                response,
                ER_keV=float(recoil),
                Enu_MeV=energy_mev,
                rho=state,
                basis="np",
                wc_triplets=dict(wc_triplets or {}),
                include_sm=bool(include_sm),
                sin2thetaW=float(sin2theta_w),
                c10_mass_mode=str(c10_mass_mode),
            ).dsigma_cm2_per_keV
            differential = _real_nonnegative(
                np.asarray(differential),
                name="differential cross section",
            )
            for component_index, component in enumerate(COMPONENTS):
                integrand = (
                    np.asarray(
                        differential_flux(component, energy_mev, data_dir=source_data_dir, settings=settings.source),
                        dtype=float,
                    )
                    * differential
                )
                rates[recoil_index, component_index] += float(
                    np.dot(weights_mev, integrand)
                )

    rates *= settings.nuclei_per_kg * settings.seconds_per_day
    return _real_nonnegative(
        rates.reshape(original.shape + (len(COMPONENTS),)),
        name="true recoil rate",
    )


def _coerce_exposures(
    exposures_kg_day: Optional[Mapping[str, float] | np.ndarray],
) -> np.ndarray:
    if exposures_kg_day is None:
        result = np.asarray(EXPOSURES_KG_DAY, dtype=float)
    elif isinstance(exposures_kg_day, Mapping):
        if set(exposures_kg_day) != set(DETECTOR_ORDER):
            raise ValueError(
                f"exposure mapping keys must be {DETECTOR_ORDER}"
            )
        result = np.asarray(
            [
                exposures_kg_day[detector]
                for detector in DETECTOR_ORDER
            ],
            dtype=float,
        )
    else:
        result = np.asarray(exposures_kg_day, dtype=float)
    if result.shape != (len(DETECTOR_ORDER),):
        raise ValueError(
            "exposures_kg_day must have one entry per detector"
        )
    if np.any(~np.isfinite(result)) or np.any(result < 0.0):
        raise ValueError(
            "exposures_kg_day must be finite and non-negative"
        )
    return result


def slow_counts_conus_plus(
    responses_json: str | Path = DEFAULT_RESPONSE_JSON,
    wc_triplets: Optional[Mapping[Triplet, object]] = None,
    *,
    include_sm: bool = True,
    sin2theta_w: float = SIN2_THETA_W,
    exposures_kg_day: Optional[Mapping[str, float] | np.ndarray] = None,
    n_recoil: int = DEFINITION.numerical_profiles['slow']['n_recoil'],
    n_energy: int = DEFINITION.numerical_profiles['slow']['n_energy'],
    c10_mass_mode: str = DEFAULT_SETTINGS.c10_mass_mode,
    settings=DEFAULT_SETTINGS, source_data_dir=None, bin_edges_evee=None,
) -> dict[str, Any]:
    """Directly integrate the CONUS+ candidate reconstructed spectrum."""

    exposure = _coerce_exposures([e.kg_day for e in settings.exposures] if exposures_kg_day is None else exposures_kg_day)
    BIN_EDGES_EVEE = np.asarray(DEFINITION.observation.edges if bin_edges_evee is None else bin_edges_evee)
    ENERGY_SUPPORT_MEV = settings.source.energy_support_mev
    ENERGY_REGION_BOUNDS_MEV = settings.energy_region_bounds_mev
    ENERGY_REGION_LABELS = settings.energy_region_labels
    NUCLEI_PER_KG = settings.nuclei_per_kg
    SECONDS_PER_DAY = settings.seconds_per_day
    RESPONSE_KEY = settings.response_key
    mass_gev = settings.target_A * float(c.AMU_GEV)
    recoil_max_kev = float(
        two_body_recoil_max_GeV(
            float(ENERGY_SUPPORT_MEV[1]) * c.MeV,
            mass_gev,
        )
        / c.keV
    )
    recoil_nodes, recoil_weights = _gauss_interval(
        n_recoil,
        0.0,
        recoil_max_kev,
    )

    region_rates = np.stack(
        [
            true_recoil_rate_components_per_kg_day(
                recoil_nodes,
                responses_json,
                wc_triplets,
                include_sm=include_sm,
                sin2theta_w=sin2theta_w,
                n_energy=n_energy,
                energy_range_mev=bounds,
                c10_mass_mode=c10_mass_mode, settings=settings, source_data_dir=source_data_dir,
            )
            for bounds in ENERGY_REGION_BOUNDS_MEV
        ],
        axis=-1,
    )
    component_rates = np.sum(region_rates, axis=-1)

    acceptances = np.stack(
        [
            detector_bin_acceptance(recoil_nodes, detector, settings=settings.detector, edges_evee=BIN_EDGES_EVEE)
            for detector in DETECTOR_ORDER
        ],
        axis=0,
    )
    counts_by_region = np.einsum(
        "t,tcr,dtb,d->dcrb",
        recoil_weights,
        region_rates,
        acceptances,
        exposure,
        optimize=True,
    )
    counts_by_region = _real_nonnegative(
        counts_by_region,
        name="energy-region reconstructed counts",
    )
    counts = np.sum(counts_by_region, axis=2)
    detector_counts_by_region = np.sum(counts_by_region, axis=1)
    detector_counts = np.sum(counts, axis=1)
    combined_counts_by_region = np.sum(
        detector_counts_by_region,
        axis=0,
    )
    combined_counts = np.sum(detector_counts, axis=0)

    return {
        "counts_per_detector_component_bin": counts,
        "counts_per_detector_component_energy_region_bin": counts_by_region,
        "counts_per_detector_energy_region_bin": detector_counts_by_region,
        "combined_counts_per_energy_region_bin": combined_counts_by_region,
        "counts_per_detector_bin": detector_counts,
        "combined_counts_per_bin": combined_counts,
        "detector_totals": np.sum(detector_counts, axis=1),
        "component_totals": np.sum(counts, axis=(0, 2)),
        "energy_region_totals": np.sum(
            combined_counts_by_region,
            axis=1,
        ),
        "total_events": float(np.sum(combined_counts)),
        "detector_order": DETECTOR_ORDER,
        "component_order": COMPONENTS,
        "energy_region_labels": ENERGY_REGION_LABELS,
        "energy_region_bounds_mev": ENERGY_REGION_BOUNDS_MEV,
        "bin_edges_evee": BIN_EDGES_EVEE.copy(),
        "true_recoil_nodes_kev": recoil_nodes,
        "true_recoil_weights_kev": recoil_weights,
        "true_recoil_rate_components_energy_region_per_kg_day_kev": (
            region_rates
        ),
        "true_recoil_rate_components_per_kg_day_kev": component_rates,
        "true_recoil_rate_total_per_kg_day_kev": np.sum(
            component_rates,
            axis=-1,
        ),
        "detector_bin_acceptance": acceptances,
        "normalization": {
            "flux_unit": "cm^-2 s^-1 MeV^-1",
            "differential_cross_section_unit": "cm^2 keVnr^-1",
            "nuclei_per_kg": NUCLEI_PER_KG,
            "seconds_per_day": SECONDS_PER_DAY,
            "exposures_kg_day": exposure.copy(),
            "response_bin_acceptance_unit": "dimensionless",
            "output_unit": "expected_events_per_bin",
            "reference_count_rescaling": False,
        },
        "quadrature": {
            "method": (
                "Gauss-Legendre; E_nu split at Kopeikin nodes, "
                "8 MeV diagnostic boundary and support end"
            ),
            "n_recoil": int(n_recoil),
            "n_energy_per_segment": int(n_energy),
            "recoil_support_kev": [0.0, recoil_max_kev],
            "energy_support_mev": list(ENERGY_SUPPORT_MEV),
        },
        "model": {
            "dataset_id": DATASET_ID,
            "response_key": RESPONSE_KEY,
            "include_sm": bool(include_sm),
            "sin2theta_w": float(sin2theta_w),
            "particle_kind": "antinu",
            "antinu_kernel_note": (
                "candidate uses the current numerically identical "
                "nu/antinu interaction kernel"
            ),
        },
    }


__all__ = [
    "DATASET_ID",
    "RESPONSE_KEY",
    "SIN2_THETA_W",
    "NUCLEI_PER_KG",
    "SECONDS_PER_DAY",
    "EXPOSURES_KG_DAY",
    "ENERGY_REGION_LABELS",
    "ENERGY_REGION_BOUNDS_MEV",
    "DEFAULT_RESPONSE_JSON",
    "true_recoil_rate_components_per_kg_day",
    "slow_counts_conus_plus",
]
