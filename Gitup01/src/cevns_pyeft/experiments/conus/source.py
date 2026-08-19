from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ArrayLike = float | int | np.ndarray

PHI0_CM2_S = 1.5e13
ENERGY_MIN_MEV = 0.01
MATCH_ENERGY_MEV = 2.0
ENERGY_MAX_MEV = 10.0


@dataclass(frozen=True)
class ReactorFluxTables:
    mueller: dict[str, dict[str, float]]
    kopeikin_energy_mev: np.ndarray
    kopeikin_rho: np.ndarray


def _asarray(x: ArrayLike) -> np.ndarray:
    return np.atleast_1d(np.asarray(x, dtype=float))


def _scalar_or_array(values: np.ndarray, like: ArrayLike):
    if np.isscalar(like):
        return float(np.asarray(values).reshape(-1)[0])
    return values


def _trapz(y: np.ndarray, x: np.ndarray) -> float:
    trapezoid = getattr(np, "trapezoid", None)
    if trapezoid is not None:
        return float(trapezoid(y, x))
    return float(np.trapz(y, x))


def _data_dir_from_spec(experiment_spec: Any) -> Path:
    path = getattr(experiment_spec, "path", None)
    if path is None and isinstance(experiment_spec, dict):
        raw = experiment_spec.get("_spec_path") or experiment_spec.get("path")
        path = Path(raw) if raw else None
    if path is None:
        return Path(__file__).resolve().parents[4] / "data" / "experiments" / "conus_plus_ge73_pheno"
    return Path(path).resolve().parent


def _read_mueller(path: Path) -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            isotope = str(row["isotope"]).strip()
            rows[isotope] = {
                "fission_fraction": float(row["fission_fraction"]),
                "a0": float(row["a0"]),
                "a1": float(row["a1"]),
                "a2": float(row["a2"]),
                "a3": float(row["a3"]),
                "a4": float(row["a4"]),
                "a5": float(row["a5"]),
            }
    return rows


def _read_kopeikin(path: Path) -> tuple[np.ndarray, np.ndarray]:
    energy: list[float] = []
    rho: list[float] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            energy.append(float(row["energy_mev"]))
            rho.append(float(row["rho_kop"]))
    e = np.asarray(energy, dtype=float)
    r = np.asarray(rho, dtype=float)
    if e.ndim != 1 or e.size != 32:
        raise ValueError(f"Expected 32 Kopeikin nodes, got {e.size}")
    if np.any(np.diff(e) <= 0):
        raise ValueError("Kopeikin energy nodes must be strictly increasing")
    return e, r


def load_reactor_flux_tables(experiment_spec: Any) -> ReactorFluxTables:
    data_dir = _data_dir_from_spec(experiment_spec)
    mueller = _read_mueller(data_dir / "mueller_coefficients.csv")
    energy, rho = _read_kopeikin(data_dir / "kopeikin_low_energy_spectrum.csv")
    return ReactorFluxTables(mueller=mueller, kopeikin_energy_mev=energy, kopeikin_rho=rho)


def mueller_spectrum_shape(E_MeV: ArrayLike, tables: ReactorFluxTables) -> ArrayLike:
    energy = _asarray(E_MeV)
    out = np.zeros_like(energy, dtype=float)
    powers = np.vstack([energy**i for i in range(6)])
    for params in tables.mueller.values():
        coeffs = np.asarray([params[f"a{i}"] for i in range(6)], dtype=float)
        out += float(params["fission_fraction"]) * np.exp(np.sum(coeffs[:, None] * powers, axis=0))
    return _scalar_or_array(out, E_MeV)


def kopeikin_spectrum_shape(E_MeV: ArrayLike, tables: ReactorFluxTables) -> ArrayLike:
    energy = _asarray(E_MeV)
    out = np.interp(energy, tables.kopeikin_energy_mev, tables.kopeikin_rho, left=0.0, right=0.0)
    return _scalar_or_array(out, E_MeV)


def release_reactor_spectrum_shape(E_MeV: ArrayLike, tables: ReactorFluxTables) -> ArrayLike:
    energy = _asarray(E_MeV)
    out = np.zeros_like(energy, dtype=float)
    rho_mueller_match = float(mueller_spectrum_shape(MATCH_ENERGY_MEV, tables))
    rho_kop_match = float(kopeikin_spectrum_shape(MATCH_ENERGY_MEV, tables))
    if rho_kop_match <= 0.0:
        raise ValueError("Kopeikin spectrum at 2 MeV must be positive")
    c_match = rho_mueller_match / rho_kop_match
    low = (energy >= ENERGY_MIN_MEV) & (energy < MATCH_ENERGY_MEV)
    high = (energy >= MATCH_ENERGY_MEV) & (energy <= ENERGY_MAX_MEV)
    out[low] = c_match * np.asarray(kopeikin_spectrum_shape(energy[low], tables), dtype=float)
    out[high] = np.asarray(mueller_spectrum_shape(energy[high], tables), dtype=float)
    out = np.where(out > 0.0, out, 0.0)
    return _scalar_or_array(out, E_MeV)


def _normalization_integral(tables: ReactorFluxTables, *, n_grid: int = 20001) -> float:
    if n_grid < 1001:
        raise ValueError("n_grid must be >= 1001")
    low_edges = tables.kopeikin_energy_mev[
        (tables.kopeikin_energy_mev >= ENERGY_MIN_MEV) & (tables.kopeikin_energy_mev <= MATCH_ENERGY_MEV)
    ]
    grid = np.unique(np.concatenate([low_edges, np.linspace(MATCH_ENERGY_MEV, ENERGY_MAX_MEV, int(n_grid))]))
    shape = np.asarray(release_reactor_spectrum_shape(grid, tables), dtype=float)
    return _trapz(shape, grid)


def load_conus_plus_ge73_reactor_flux(experiment_spec: Any) -> dict[str, Any]:
    tables = load_reactor_flux_tables(experiment_spec)
    rho_mueller_match = float(mueller_spectrum_shape(MATCH_ENERGY_MEV, tables))
    rho_kop_match = float(kopeikin_spectrum_shape(MATCH_ENERGY_MEV, tables))
    c_match = rho_mueller_match / rho_kop_match
    norm = _normalization_integral(tables)
    if norm <= 0.0:
        raise ValueError("Reactor flux normalization integral must be positive")

    def shape(E_MeV: ArrayLike) -> ArrayLike:
        return release_reactor_spectrum_shape(E_MeV, tables)

    def flux(E_MeV: ArrayLike) -> ArrayLike:
        values = PHI0_CM2_S * _asarray(shape(E_MeV)) / norm
        return _scalar_or_array(values, E_MeV)

    return {
        "basic": {
            "name": "conus_plus_ge73_pheno_reactor_flux",
            "flavor": "electron_antineutrino",
            "energy_unit": "MeV",
            "flux_unit": "cm^-2 s^-1 MeV^-1",
            "phi0_cm^-2_s^-1": PHI0_CM2_S,
            "energy_support_MeV": (ENERGY_MIN_MEV, ENERGY_MAX_MEV),
            "zero_below_MeV": ENERGY_MIN_MEV,
            "matching_energy_MeV": MATCH_ENERGY_MEV,
            "c_match": c_match,
            "normalization_integral": norm,
        },
        "tables": {
            "mueller": tables.mueller,
            "kopeikin_energy_mev": tables.kopeikin_energy_mev.copy(),
            "kopeikin_rho": tables.kopeikin_rho.copy(),
        },
        "measured": {
            "energyUnit": "MeV",
            "fluxUnit": "cm^-2 s^-1 MeV^-1",
            "nuebar": flux,
            "shape": shape,
        },
    }


__all__ = [
    "ENERGY_MAX_MEV",
    "ENERGY_MIN_MEV",
    "MATCH_ENERGY_MEV",
    "PHI0_CM2_S",
    "ReactorFluxTables",
    "kopeikin_spectrum_shape",
    "load_conus_plus_ge73_reactor_flux",
    "load_reactor_flux_tables",
    "mueller_spectrum_shape",
    "release_reactor_spectrum_shape",
]
