"""CONUS+ detector-site reactor antineutrino spectrum.

The source layer owns only the per-second differential flux and source-state
metadata.  Target nuclei, detector exposure, response folding, and binning are
deliberately excluded.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, Literal, Optional, Tuple, Union, cast

import numpy as np

from cevns_pyeft.sources.state import NeutrinoState, pure_flavor_state


ArrayLike = Union[float, int, np.ndarray]
ReactorComponent = Literal["U235", "U238", "Pu239", "Pu241"]
FluxComponent = Literal["U235", "U238", "Pu239", "Pu241", "total"]

DATASET_ID = "conus_plus_2025_c2c3c5_ge73_pyeft"
COMPONENTS: Tuple[ReactorComponent, ...] = (
    "U235",
    "U238",
    "Pu239",
    "Pu241",
)
TOTAL_FLUX_CM2_S = 1.5e13
NORMALIZATION_UNCERTAINTY_FRACTION = 0.046
ENERGY_SUPPORT_MEV = (0.0, 10.0)
MATCH_ENERGY_MEV = 2.0
LOWEST_KOPEIKIN_NODE_MEV = 0.01
LOW_END_POLICY = "linear_extrapolation_clamped_nonnegative"
TIME_BASIS = "per_second"
FLUX_UNIT = "cm^-2 s^-1 MeV^-1"

DEFAULT_DATA_DIR = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "experiments"
    / "CONUS_Plus"
    / DATASET_ID
    / "source"
)


def _scalar_or_array(value: np.ndarray, like: ArrayLike):
    if np.isscalar(like):
        return float(np.asarray(value).reshape(-1)[0])
    return value


def _data_dir_key(data_dir: Optional[str | Path]) -> str:
    root = DEFAULT_DATA_DIR if data_dir is None else Path(data_dir)
    return str(root.resolve())


@lru_cache(maxsize=None)
def _load_tables(
    data_dir_key: str,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, np.ndarray], Dict[str, float]]:
    root = Path(data_dir_key)
    nodes_path = root / "kopeikin_nodes.csv"
    coefficients_path = root / "mueller_coefficients.csv"

    with nodes_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    energies = np.asarray([float(row["energy_mev"]) for row in rows])
    values = np.asarray([float(row["rho_kop"]) for row in rows])
    if energies.shape != (32,) or values.shape != (32,):
        raise ValueError("Kopeikin table must contain exactly 32 nodes")
    if not np.all(np.diff(energies) > 0.0):
        raise ValueError("Kopeikin energies must be strictly increasing")
    if energies[0] != LOWEST_KOPEIKIN_NODE_MEV or energies[-1] != MATCH_ENERGY_MEV:
        raise ValueError("Kopeikin support must run from 0.01 to 2.0 MeV")
    if not np.all(np.isfinite(values)) or np.any(values <= 0.0):
        raise ValueError("Kopeikin node values must be finite and positive")

    coefficients: Dict[str, np.ndarray] = {}
    fractions: Dict[str, float] = {}
    with coefficients_path.open("r", encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            component = row["component"]
            if component not in COMPONENTS:
                raise ValueError(f"Unknown Mueller component {component!r}")
            coefficients[component] = np.asarray(
                [float(row[f"a{index}"]) for index in range(6)],
                dtype=float,
            )
            fractions[component] = float(row["fission_fraction"])
    if tuple(coefficients) != COMPONENTS:
        raise ValueError(
            f"Mueller component order must be {COMPONENTS}, got {tuple(coefficients)}"
        )
    if not np.isclose(sum(fractions.values()), 1.0, rtol=0.0, atol=1.0e-15):
        raise ValueError("Reactor fission fractions must sum to one")

    energies.setflags(write=False)
    values.setflags(write=False)
    for array in coefficients.values():
        array.setflags(write=False)
    return energies, values, coefficients, fractions


def kopeikin_nodes(
    *, data_dir: Optional[str | Path] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """Return copies of the 32 tabulated Kopeikin nodes."""

    energies, values, _, _ = _load_tables(_data_dir_key(data_dir))
    return energies.copy(), values.copy()


def mueller_coefficients(
    *, data_dir: Optional[str | Path] = None
) -> Dict[str, np.ndarray]:
    """Return the six Mueller coefficients for each fission component."""

    _, _, coefficients, _ = _load_tables(_data_dir_key(data_dir))
    return {key: value.copy() for key, value in coefficients.items()}


def fission_fractions(
    *, data_dir: Optional[str | Path] = None
) -> Dict[str, float]:
    """Return the approved fission fractions in canonical component order."""

    _, _, _, fractions = _load_tables(_data_dir_key(data_dir))
    return dict(fractions)


def _mueller_per_fission(
    component: ReactorComponent,
    energy_mev: np.ndarray,
    *,
    data_dir_key: str,
) -> np.ndarray:
    _, _, coefficients, _ = _load_tables(data_dir_key)
    return np.exp(np.polynomial.polynomial.polyval(energy_mev, coefficients[component]))


def _kopeikin_shape(
    energy_mev: np.ndarray,
    *,
    data_dir_key: str,
) -> np.ndarray:
    energies, values, _, _ = _load_tables(data_dir_key)
    result = np.interp(energy_mev, energies, values)
    below = energy_mev < energies[0]
    slope = (values[1] - values[0]) / (energies[1] - energies[0])
    result[below] = values[0] + slope * (energy_mev[below] - energies[0])
    return np.maximum(result, 0.0)


def _raw_component_shape(
    component: ReactorComponent,
    energy_mev: np.ndarray,
    *,
    data_dir_key: str,
) -> np.ndarray:
    energies, values, _, fractions = _load_tables(data_dir_key)
    result = np.zeros_like(energy_mev, dtype=float)
    support = (energy_mev >= ENERGY_SUPPORT_MEV[0]) & (
        energy_mev <= ENERGY_SUPPORT_MEV[1]
    )
    low = support & (energy_mev < MATCH_ENERGY_MEV)
    high = support & ~low

    mueller_at_match = float(
        _mueller_per_fission(
            component,
            np.asarray(MATCH_ENERGY_MEV),
            data_dir_key=data_dir_key,
        )
    )
    match_factor = mueller_at_match / float(values[-1])
    if np.any(low):
        result[low] = (
            fractions[component]
            * match_factor
            * _kopeikin_shape(energy_mev[low], data_dir_key=data_dir_key)
        )
    if np.any(high):
        result[high] = fractions[component] * _mueller_per_fission(
            component,
            energy_mev[high],
            data_dir_key=data_dir_key,
        )
    return result


@lru_cache(maxsize=None)
def _normalization_integral_cached(data_dir_key: str) -> float:
    energies, values, _, fractions = _load_tables(data_dir_key)
    slope = (values[1] - values[0]) / (energies[1] - energies[0])
    zero_crossing = energies[0] - values[0] / slope
    low_energies = np.concatenate(
        ([0.0, zero_crossing], energies)
    )
    low_values = _kopeikin_shape(low_energies, data_dir_key=data_dir_key)
    low_base_integral = float(np.trapezoid(low_values, low_energies))

    mixture_at_match = sum(
        fractions[component]
        * float(
            _mueller_per_fission(
                component,
                np.asarray(MATCH_ENERGY_MEV),
                data_dir_key=data_dir_key,
            )
        )
        for component in COMPONENTS
    )
    low_integral = mixture_at_match / float(values[-1]) * low_base_integral

    nodes, weights = np.polynomial.legendre.leggauss(256)
    high_energies = 0.5 * (
        (ENERGY_SUPPORT_MEV[1] - MATCH_ENERGY_MEV) * nodes
        + ENERGY_SUPPORT_MEV[1]
        + MATCH_ENERGY_MEV
    )
    high_shape = sum(
        fractions[component]
        * _mueller_per_fission(
            component,
            high_energies,
            data_dir_key=data_dir_key,
        )
        for component in COMPONENTS
    )
    high_integral = 0.5 * (
        ENERGY_SUPPORT_MEV[1] - MATCH_ENERGY_MEV
    ) * float(np.dot(weights, high_shape))
    return low_integral + high_integral


def normalization_integral(*, data_dir: Optional[str | Path] = None) -> float:
    """Return the raw-shape integral used for detector-site normalization."""

    return _normalization_integral_cached(_data_dir_key(data_dir))


def differential_flux(
    component: FluxComponent,
    energy_mev: ArrayLike,
    *,
    data_dir: Optional[str | Path] = None,
):
    """Return one component or the total detector-site differential flux.

    Parameters
    ----------
    component:
        One of U235, U238, Pu239, Pu241, or total.
    energy_mev:
        Scalar or array neutrino energy in MeV.

    Returns
    -------
    Scalar or array matching the input shape in cm^-2 s^-1 MeV^-1.
    """

    if component not in (*COMPONENTS, "total"):
        raise ValueError(
            f"component must be one of {(*COMPONENTS, 'total')}, got {component!r}"
        )
    original = energy_mev
    energy = np.asarray(energy_mev, dtype=float)
    if not np.all(np.isfinite(energy)):
        raise ValueError("energy_mev must contain only finite values")
    data_dir_key = _data_dir_key(data_dir)
    if component == "total":
        raw = sum(
            _raw_component_shape(key, energy, data_dir_key=data_dir_key)
            for key in COMPONENTS
        )
    else:
        raw = _raw_component_shape(
            cast(ReactorComponent, component),
            energy,
            data_dir_key=data_dir_key,
        )
    flux = TOTAL_FLUX_CM2_S / _normalization_integral_cached(data_dir_key) * raw
    return _scalar_or_array(flux, original)


def total_differential_flux(
    energy_mev: ArrayLike,
    *,
    data_dir: Optional[str | Path] = None,
):
    """Return the total detector-site differential flux."""

    return differential_flux("total", energy_mev, data_dir=data_dir)


def source_state() -> NeutrinoState:
    """Return the pure electron-antineutrino Flavor state."""

    return pure_flavor_state("e", particle_kind="antinu")


def _component_callable(
    component: FluxComponent,
    data_dir: Optional[str | Path],
) -> Callable[[ArrayLike], Any]:
    def evaluate(energy_mev: ArrayLike):
        return differential_flux(component, energy_mev, data_dir=data_dir)

    return evaluate


def load_reactor_flux(
    dataset: str = DATASET_ID,
    *,
    data_dir: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Return the CONUS+ source interface and explicit source metadata."""

    if dataset != DATASET_ID:
        raise KeyError(f"Unknown CONUS+ source dataset {dataset!r}")
    component_fluxes = {
        component: _component_callable(component, data_dir)
        for component in COMPONENTS
    }
    return {
        "basic": {
            "name": DATASET_ID,
            "particle": "electron_antineutrino",
            "energyUnit": "MeV",
            "fluxUnit": FLUX_UNIT,
            "timeBasis": TIME_BASIS,
            "energySupportMeV": ENERGY_SUPPORT_MEV,
            "matchEnergyMeV": MATCH_ENERGY_MEV,
            "totalFlux_cm^-2_s^-1": TOTAL_FLUX_CM2_S,
            "normalizationUncertaintyFraction": NORMALIZATION_UNCERTAINTY_FRACTION,
            "normalizationRoute": "detector_site_absolute_flux",
            "lowEndPolicy": LOW_END_POLICY,
            "fissionFractions": fission_fractions(data_dir=data_dir),
        },
        "measured": {
            "components": component_fluxes,
            "total": _component_callable("total", data_dir),
        },
        "state": source_state(),
    }


__all__ = [
    "ArrayLike",
    "ReactorComponent",
    "FluxComponent",
    "DATASET_ID",
    "COMPONENTS",
    "TOTAL_FLUX_CM2_S",
    "NORMALIZATION_UNCERTAINTY_FRACTION",
    "ENERGY_SUPPORT_MEV",
    "MATCH_ENERGY_MEV",
    "LOWEST_KOPEIKIN_NODE_MEV",
    "LOW_END_POLICY",
    "TIME_BASIS",
    "FLUX_UNIT",
    "DEFAULT_DATA_DIR",
    "kopeikin_nodes",
    "mueller_coefficients",
    "fission_fractions",
    "normalization_integral",
    "differential_flux",
    "total_differential_flux",
    "source_state",
    "load_reactor_flux",
]

