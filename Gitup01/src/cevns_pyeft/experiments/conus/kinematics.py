from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import differential_cross_section_nn
from cevns_pyeft.sources.state import pure_flavor_state
from cevns_pyeft.theory.kinematics import minimum_neutrino_energy_GeV
from cevns_pyeft.theory.li2026.flavor import zero_flavor_matrix

ArrayLike = float | int | np.ndarray

GE73_A = 73
GE73_Z = 32
GE73_N = 41
DEFAULT_RESPONSE_KEY = "Ge73"
DEFAULT_SIN2THETAW = 0.23873
AVAILABLE_CROSS_SECTION_MODELS = ("full_response", "helm_sm")
AVAILABLE_KINEMATICS = ("publication_reproduction", "heavy_nucleus_approximation")
REACTOR_NUEBAR_STATE = pure_flavor_state("e", particle_kind="antinu")


def _asarray(x: ArrayLike) -> np.ndarray:
    return np.atleast_1d(np.asarray(x, dtype=float))


def _scalar_or_array(values: np.ndarray, like_a: ArrayLike, like_b: ArrayLike):
    if np.isscalar(like_a) and np.isscalar(like_b):
        return float(np.asarray(values).reshape(-1)[0])
    return values


def _legacy_scalar_wilson_to_electron_only(
    coefficients: Mapping[tuple[int, int, str], complex] | None,
) -> dict[tuple[int, int, str], np.ndarray]:
    """Map CONUS legacy scalar Wilson inputs to the reactor antinu_e state."""

    out: dict[tuple[int, int, str], np.ndarray] = {}
    for key, value in dict(coefficients or {}).items():
        matrix = zero_flavor_matrix()
        matrix[0, 0] = complex(value)
        out[key] = matrix
    return out


def ge73_target_mass_gev(A: int = GE73_A) -> float:
    return float(A) * float(c.AMU_GEV)


def enu_min_heavy_nucleus_conus_ge73(T_keVnr: ArrayLike, mA_GeV: float | None = None) -> ArrayLike:
    mass = ge73_target_mass_gev() if mA_GeV is None else float(mA_GeV)
    recoil = _asarray(T_keVnr)
    out = 1000.0 * np.sqrt(np.maximum(mass * recoil * 1.0e-6 / 2.0, 0.0))
    return float(out[0]) if np.isscalar(T_keVnr) else out


def enu_min_exact_conus_ge73(T_keVnr: ArrayLike, mA_GeV: float | None = None) -> ArrayLike:
    mass = ge73_target_mass_gev() if mA_GeV is None else float(mA_GeV)
    recoil = _asarray(T_keVnr)
    out = np.asarray(
        [
            minimum_neutrino_energy_GeV(float(value) * 1.0e-6, mass) * 1000.0
            for value in recoil.reshape(-1)
        ],
        dtype=float,
    ).reshape(recoil.shape)
    return float(out[0]) if np.isscalar(T_keVnr) else out


def recoil_max_exact_keV(E_nu_MeV: ArrayLike, mA_GeV: float | None = None) -> ArrayLike:
    mass = ge73_target_mass_gev() if mA_GeV is None else float(mA_GeV)
    energy_gev = _asarray(E_nu_MeV) * 1.0e-3
    out_gev = 2.0 * energy_gev * energy_gev / (mass + 2.0 * energy_gev)
    out = out_gev * 1.0e6
    return float(out[0]) if np.isscalar(E_nu_MeV) else out


def physical_support_mask(
    E_nu_MeV: ArrayLike,
    T_keVnr: ArrayLike,
    *,
    kinematics: str = "publication_reproduction",
) -> np.ndarray:
    if kinematics not in AVAILABLE_KINEMATICS:
        raise ValueError(f"Unknown kinematics {kinematics!r}; expected one of {AVAILABLE_KINEMATICS}")
    energy, recoil = np.broadcast_arrays(_asarray(E_nu_MeV), _asarray(T_keVnr))
    threshold_fn = (
        enu_min_heavy_nucleus_conus_ge73
        if kinematics == "heavy_nucleus_approximation"
        else enu_min_exact_conus_ge73
    )
    threshold = np.full_like(energy, np.inf, dtype=float)
    recoil_ok = recoil >= 0.0
    if np.any(recoil_ok):
        threshold[recoil_ok] = _asarray(threshold_fn(recoil[recoil_ok]))
    return (energy > 0.0) & (recoil >= 0.0) & (energy >= threshold)


def q_from_recoil_MeV(T_keVnr: ArrayLike, mA_GeV: float | None = None) -> ArrayLike:
    mass = ge73_target_mass_gev() if mA_GeV is None else float(mA_GeV)
    recoil = _asarray(T_keVnr)
    q_gev = np.sqrt(np.maximum(2.0 * mass * recoil * 1.0e-6, 0.0))
    out = q_gev * 1000.0
    return float(out[0]) if np.isscalar(T_keVnr) else out


def helm_form_factor_ge73(T_keVnr: ArrayLike, *, A: int = GE73_A, skin_fm: float = 0.9) -> ArrayLike:
    q_mev = _asarray(q_from_recoil_MeV(T_keVnr, ge73_target_mass_gev(A)))
    q_fm_inv = q_mev / float(c.HBARC_MEV_FM)
    radius_fm = 1.2 * float(A) ** (1.0 / 3.0)
    r0_sq = max(radius_fm * radius_fm - 5.0 * skin_fm * skin_fm, 0.0)
    r0_fm = math.sqrt(r0_sq)
    x = q_fm_inv * r0_fm
    j1_over_x = np.empty_like(x)
    small = np.abs(x) < 1.0e-6
    j1_over_x[small] = 1.0 / 3.0 - x[small] ** 2 / 30.0
    xs = x[~small]
    j1_over_x[~small] = (np.sin(xs) / xs**2 - np.cos(xs) / xs) / xs
    form = 3.0 * j1_over_x * np.exp(-0.5 * (q_fm_inv * skin_fm) ** 2)
    return float(form[0]) if np.isscalar(T_keVnr) else form


def weak_charge_ge73(*, sin2thetaW: float = DEFAULT_SIN2THETAW, Z: int = GE73_Z, N: int = GE73_N) -> float:
    return float(N) - (1.0 - 4.0 * float(sin2thetaW)) * float(Z)


def helm_sm_differential_cross_section(
    E_nu_MeV: ArrayLike,
    T_keVnr: ArrayLike,
    *,
    sin2thetaW: float = DEFAULT_SIN2THETAW,
    kinematics: str = "publication_reproduction",
) -> ArrayLike:
    energy, recoil = np.broadcast_arrays(_asarray(E_nu_MeV), _asarray(T_keVnr))
    out = np.zeros_like(energy, dtype=float)
    allowed = physical_support_mask(energy, recoil, kinematics=kinematics)
    if np.any(allowed):
        e_gev = energy[allowed] * 1.0e-3
        t_gev = recoil[allowed] * 1.0e-6
        mA = ge73_target_mass_gev()
        qw = weak_charge_ge73(sin2thetaW=sin2thetaW)
        ff = np.asarray(helm_form_factor_ge73(recoil[allowed]), dtype=float)
        kin = np.maximum(1.0 - mA * t_gev / (2.0 * e_gev * e_gev), 0.0)
        dsigma_dT_gev = float(c.G_F) ** 2 * mA * qw * qw * kin * ff * ff / (4.0 * math.pi)
        out[allowed] = dsigma_dT_gev * float(c.GEV_INV2_TO_CM2) * 1.0e-6
    return _scalar_or_array(out, E_nu_MeV, T_keVnr)


def _response_path_from_spec(experiment_spec: Any) -> Path:
    path = getattr(experiment_spec, "path", None)
    if path is None and isinstance(experiment_spec, dict):
        raw = experiment_spec.get("_spec_path") or experiment_spec.get("path")
        path = Path(raw) if raw else None
    root = Path(path).resolve().parents[3] if path is not None else Path(__file__).resolve().parents[4]
    return root / "data" / "responses" / "responses_all.json"


def differential_cross_section_conus_ge73(
    E_nu_MeV: ArrayLike,
    T_keVnr: ArrayLike,
    experiment_spec: Any | None = None,
    *,
    model: str = "full_response",
    kinematics: str = "publication_reproduction",
    left_wcs: Mapping[str, complex] | None = None,
    wc_triplets: Mapping[tuple[int, int, str], complex] | None = None,
    include_sm: bool = True,
    sin2thetaW: float = DEFAULT_SIN2THETAW,
    responses_json: str | Path | None = None,
    basis: str = "np",
    c10_mass_mode: str = "quark_mass_resolved",
) -> ArrayLike:
    if kinematics not in AVAILABLE_KINEMATICS:
        raise ValueError(f"Unknown kinematics {kinematics!r}; expected one of {AVAILABLE_KINEMATICS}")
    if model == "helm_sm":
        if left_wcs or wc_triplets:
            raise ValueError("helm_sm supports only the Standard Model weak-charge comparison, not EFT coefficients")
        if not include_sm:
            return _scalar_or_array(np.zeros_like(np.broadcast_arrays(_asarray(E_nu_MeV), _asarray(T_keVnr))[0]), E_nu_MeV, T_keVnr)
        return helm_sm_differential_cross_section(E_nu_MeV, T_keVnr, sin2thetaW=sin2thetaW, kinematics=kinematics)
    if model != "full_response":
        raise ValueError(f"Unknown model {model!r}; expected one of {AVAILABLE_CROSS_SECTION_MODELS}")

    energy, recoil = np.broadcast_arrays(_asarray(E_nu_MeV), _asarray(T_keVnr))
    out = np.zeros_like(energy, dtype=float)
    allowed = physical_support_mask(energy, recoil, kinematics=kinematics)
    if np.any(allowed):
        db_path = Path(responses_json) if responses_json is not None else _response_path_from_spec(experiment_spec)
        resp = ResponseDB(db_path).get(DEFAULT_RESPONSE_KEY)
        for idx in zip(*np.where(allowed)):
            out[idx] = float(
                differential_cross_section_nn(
                    resp,
                    ER_keV=float(recoil[idx]),
                    Enu_MeV=float(energy[idx]),
                    basis=basis,  # type: ignore[arg-type]
                    left_wcs=dict(left_wcs or {}),
                    wc_triplets=_legacy_scalar_wilson_to_electron_only(wc_triplets),
                    include_sm=include_sm,
                    sin2thetaW=sin2thetaW,
                    c10_mass_mode=c10_mass_mode,
                    rho=REACTOR_NUEBAR_STATE,
                ).dsigma_cm2_per_keV
            )
    return _scalar_or_array(out, E_nu_MeV, T_keVnr)


__all__ = [
    "AVAILABLE_CROSS_SECTION_MODELS",
    "AVAILABLE_KINEMATICS",
    "DEFAULT_RESPONSE_KEY",
    "DEFAULT_SIN2THETAW",
    "GE73_A",
    "GE73_N",
    "GE73_Z",
    "REACTOR_NUEBAR_STATE",
    "differential_cross_section_conus_ge73",
    "enu_min_exact_conus_ge73",
    "enu_min_heavy_nucleus_conus_ge73",
    "ge73_target_mass_gev",
    "helm_form_factor_ge73",
    "helm_sm_differential_cross_section",
    "physical_support_mask",
    "q_from_recoil_MeV",
    "recoil_max_exact_keV",
    "weak_charge_ge73",
]
