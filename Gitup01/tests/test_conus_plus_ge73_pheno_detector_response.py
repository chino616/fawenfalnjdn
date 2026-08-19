from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

from cevns_pyeft.experiments.conus.detector_response import (
    EFFICIENCY_THRESHOLD_EVEE,
    GE_Z,
    LINDHARD_K,
    RECO_BIN_COUNT,
    conus_ge73_efficiency,
    conus_ge73_response_density,
    lindhard_quenching_ge,
    mean_reconstructed_energy_evee,
    reco_energy_bin_edges_evee,
    resolution_width_evee,
)
from cevns_pyeft.experiments.registry import get_experiment_spec

RUN_DIR = Path("workflows/experiment-integration/runs/conus_plus_ge73_pheno")


def test_lindhard_quenching_matches_document_formula_and_is_physical():
    recoil = np.array([0.0, 0.05, 0.1, 0.5, 1.0, 3.0])
    epsilon_l = 11.5 * GE_Z ** (-7.0 / 3.0) * recoil
    g = 3.0 * epsilon_l**0.15 + 0.7 * epsilon_l**0.6 + epsilon_l
    expected = LINDHARD_K * g / (1.0 + LINDHARD_K * g)

    actual = lindhard_quenching_ge(recoil)
    assert np.allclose(actual, expected, rtol=1.0e-14, atol=0.0)
    assert np.all(np.isfinite(actual))
    assert np.all((actual >= 0.0) & (actual < 1.0))
    assert np.all(np.diff(actual) >= 0.0)
    assert lindhard_quenching_ge(0.0) == 0.0


def test_mean_mapping_and_resolution_are_finite_monotonic_and_scalar_safe():
    recoil = np.array([0.0, 0.05, 0.1, 0.5, 1.0, 3.0])
    mean = mean_reconstructed_energy_evee(recoil)
    sigma = resolution_width_evee(mean)

    assert isinstance(mean_reconstructed_energy_evee(0.5), float)
    assert isinstance(resolution_width_evee(25.0), float)
    assert np.all(np.isfinite(mean))
    assert np.all(np.diff(mean) >= 0.0)
    assert np.all(mean >= 0.0)
    assert np.all(np.isfinite(sigma))
    assert np.all(sigma > 0.0)
    assert math.isclose(resolution_width_evee(0.0), 20.38, rel_tol=0.0, abs_tol=1.0e-12)


def test_response_density_is_nonnegative_normalized_and_has_expected_moments():
    recoil = 0.5
    mean = float(mean_reconstructed_energy_evee(recoil))
    sigma = float(resolution_width_evee(mean))
    reco = np.linspace(mean - 12.0 * sigma, mean + 12.0 * sigma, 20001)
    density = np.asarray(conus_ge73_response_density(reco, recoil), dtype=float)

    assert isinstance(conus_ge73_response_density(mean, recoil), float)
    assert np.all(np.isfinite(density))
    assert np.all(density >= 0.0)

    norm = float(np.trapezoid(density, reco))
    moment1 = float(np.trapezoid(reco * density, reco))
    moment2 = float(np.trapezoid((reco - mean) ** 2 * density, reco))
    assert math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=2.0e-6)
    assert math.isclose(moment1 / norm, mean, rel_tol=0.0, abs_tol=2.0e-4)
    assert math.isclose(math.sqrt(moment2 / norm), sigma, rel_tol=2.0e-5, abs_tol=0.0)


def test_response_density_broadcasting_and_invalid_recoil_behavior():
    reco = np.array([100.0, 160.0, 220.0])
    recoil = np.array([0.1, 0.5, 1.0])
    out = conus_ge73_response_density(reco, recoil)
    assert out.shape == (3,)
    assert np.all(np.isfinite(out))
    assert np.all(out >= 0.0)

    matrix = conus_ge73_response_density(reco[:, None], recoil[None, :])
    assert matrix.shape == (3, 3)
    assert np.all(matrix >= 0.0)
    assert conus_ge73_response_density(160.0, -1.0) == 0.0


def test_efficiency_step_acts_on_reconstructed_energy():
    points = np.array([159.999, 160.0, 160.001, 350.0])
    expected = np.array([0.0, 1.0, 1.0, 1.0])
    actual = conus_ge73_efficiency(points)
    assert np.array_equal(actual, expected)
    assert conus_ge73_efficiency(159.999) == 0.0
    assert conus_ge73_efficiency(EFFICIENCY_THRESHOLD_EVEE) == 1.0
    assert np.all((actual >= 0.0) & (actual <= 1.0))


def test_analysis_bin_edges_match_experiment_spec():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    edges = reco_energy_bin_edges_evee(spec)
    assert edges.shape == (RECO_BIN_COUNT + 1,)
    assert np.allclose(edges, np.arange(160.0, 350.0 + 10.0, 10.0))
    assert np.all(np.diff(edges) == 10.0)


def test_phase6_diagnostics_exist_and_are_labeled_after_generation():
    grid = RUN_DIR / "artifacts" / "detector_response_grid.csv"
    figures = [
        RUN_DIR / "figures" / "mean_mapping.png",
        RUN_DIR / "figures" / "resolution_width.png",
        RUN_DIR / "figures" / "detector_response_slices.png",
        RUN_DIR / "figures" / "efficiency.png",
    ]
    assert grid.exists()
    assert all(path.exists() and path.stat().st_size > 0 for path in figures)

    with grid.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {
        "T_keVnr",
        "mean_eVee",
        "sigma_eVee",
        "E_reco_eVee",
        "response_density_per_eVee",
        "efficiency",
    }.issubset(rows[0])
    densities = np.array([float(row["response_density_per_eVee"]) for row in rows])
    efficiencies = np.array([float(row["efficiency"]) for row in rows])
    assert np.all(np.isfinite(densities))
    assert np.all(densities >= 0.0)
    assert np.all((efficiencies >= 0.0) & (efficiencies <= 1.0))


def test_detector_response_module_has_no_phase7_or_source_dependencies():
    import cevns_pyeft.experiments.conus.detector_response as detector_response

    path = Path(detector_response.__file__)
    text = path.read_text(encoding="utf-8")
    forbidden = [
        "source",
        "differential_cross_section",
        "slow_counts",
        "bin_events",
        "exposure",
        "_rate_per_kg",
    ]
    assert not any(token in text for token in forbidden)
