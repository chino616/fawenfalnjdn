from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pytest

from cevns_pyeft.experiments.conus.slow_counts_conus_plus_ge73_pheno import (
    AVOGADRO_MOL_INV,
    SlowIntegrationSettings,
    nuclei_per_kg_ge73,
    slow_counts_conus_plus_ge73_pheno,
    target_time_normalization,
    true_recoil_grid_keVnr,
)
from cevns_pyeft.experiments.registry import get_experiment_spec

RUN_DIR = Path("workflows/experiment-integration/runs/conus_plus_ge73_pheno")
REFERENCE = Path("tests/reference_conus_plus_ge73_pheno/slow_reference.npy")
FAST_TEST_SETTINGS = SlowIntegrationSettings(n_true_recoil=41, n_neutrino=80, reco_step_evee=5.0)


def test_public_callable_shape_units_components_and_nonnegative_counts():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    out = slow_counts_conus_plus_ge73_pheno(
        experiment_spec=spec,
        integration_settings=FAST_TEST_SETTINGS,
        return_components=True,
    )

    counts = np.asarray(out["counts_total"], dtype=float)
    assert counts.shape == (19,)
    assert out["axes"] == ("reco_energy_evee",)
    assert out["unit"] == "expected_events_per_bin"
    assert np.all(np.isfinite(counts))
    assert np.all(counts >= 0.0)
    assert np.allclose(out["counts_per_bin"]["total"], counts)
    assert np.allclose(out["counts_per_bin"]["nuebar_Ge73"], counts)
    assert out["reco_energy_bins_evee"].shape == (20,)
    assert out["dndT_true_per_keVnr"].shape == out["true_recoil_grid_keVnr"].shape
    assert out["dndE_reco_per_evee"].shape == out["reco_energy_grid_evee"].shape


def test_target_time_normalization_applies_exposure_once_and_scales_linearly():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    assert math.isclose(nuclei_per_kg_ge73(spec), AVOGADRO_MOL_INV * 1000.0 / 73.0, rel_tol=1.0e-15)
    expected_target_seconds = AVOGADRO_MOL_INV * 1000.0 / 73.0 * 119.0 * 86400.0
    assert math.isclose(target_time_normalization(spec), expected_target_seconds, rel_tol=1.0e-15)

    base = spec.as_dict()
    half = dict(base)
    half_detector = dict(base["detector"])
    half_detector["exposure_kg_day"] = 59.5
    half["detector"] = half_detector

    full_counts = slow_counts_conus_plus_ge73_pheno(experiment_spec=base, integration_settings=FAST_TEST_SETTINGS)[
        "counts_total"
    ]
    half_counts = slow_counts_conus_plus_ge73_pheno(experiment_spec=half, integration_settings=FAST_TEST_SETTINGS)[
        "counts_total"
    ]
    assert np.allclose(half_counts, 0.5 * full_counts, rtol=1.0e-12, atol=1.0e-12)


def test_default_reference_reproducibility():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    assert REFERENCE.exists()
    reference = np.load(REFERENCE)
    out = slow_counts_conus_plus_ge73_pheno(spec, integration_settings=SlowIntegrationSettings())
    assert np.allclose(out["counts_total"], reference, rtol=1.0e-12, atol=1.0e-12)
    assert math.isclose(float(np.sum(reference)), 150.49434598713285, rel_tol=1.0e-12)


def test_supported_complex_coefficients_and_model_selectors():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    complex_counts = slow_counts_conus_plus_ge73_pheno(
        experiment_spec=spec,
        wc_triplets={(6, 1, "u"): 1.0e-8 + 2.0e-9j},
        integration_settings=FAST_TEST_SETTINGS,
    )["counts_total"]
    assert complex_counts.shape == (19,)
    assert np.all(np.isfinite(complex_counts))
    assert np.all(complex_counts >= 0.0)

    helm_counts = slow_counts_conus_plus_ge73_pheno(
        experiment_spec=spec,
        cross_section_model="helm_sm",
        integration_settings=FAST_TEST_SETTINGS,
    )["counts_total"]
    assert helm_counts.shape == (19,)
    assert np.all(np.isfinite(helm_counts))
    assert np.all(helm_counts >= 0.0)

    with pytest.raises(ValueError, match="helm_sm supports only"):
        slow_counts_conus_plus_ge73_pheno(
            experiment_spec=spec,
            cross_section_model="helm_sm",
            wc_triplets={(6, 1, "u"): 1.0e-8},
            integration_settings=FAST_TEST_SETTINGS,
        )


def test_support_endpoint_and_diagnostics_are_finite_and_labeled():
    grid = true_recoil_grid_keVnr()
    assert grid[0] == 0.0
    assert math.isclose(grid[-1], 2.940351893369968, rel_tol=1.0e-12)

    artifact_paths = [
        RUN_DIR / "artifacts" / "true_recoil_spectrum.csv",
        RUN_DIR / "artifacts" / "reconstructed_spectrum.csv",
        RUN_DIR / "artifacts" / "slow_bin_counts.csv",
        RUN_DIR / "artifacts" / "slow_convergence.csv",
    ]
    figure_paths = [
        RUN_DIR / "figures" / "true_recoil_spectrum.png",
        RUN_DIR / "figures" / "reconstructed_spectrum.png",
        RUN_DIR / "figures" / "slow_bin_counts.png",
    ]
    assert all(path.exists() and path.stat().st_size > 0 for path in artifact_paths + figure_paths)

    with (RUN_DIR / "artifacts" / "slow_bin_counts.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 19
    assert {"bin", "E_low_eVee", "E_high_eVee", "counts"}.issubset(rows[0])
    counts = np.array([float(row["counts"]) for row in rows])
    assert np.all(np.isfinite(counts))
    assert np.all(counts >= 0.0)

    with (RUN_DIR / "artifacts" / "slow_convergence.csv").open(encoding="utf-8", newline="") as handle:
        convergence = list(csv.DictReader(handle))
    assert {row["label"] for row in convergence} == {"coarse", "medium", "default_reference"}
    medium = next(row for row in convergence if row["label"] == "medium")
    assert float(medium["total_relative_delta_vs_reference"]) < 1.0e-3
    assert float(medium["max_bin_relative_delta_vs_reference"]) < 1.0e-3


def test_slow_module_has_no_fast_or_statistics_dependency():
    import cevns_pyeft.experiments.conus.slow_counts_conus_plus_ge73_pheno as slow_module

    text = Path(slow_module.__file__).read_text(encoding="utf-8").lower()
    assert "fast" not in text
    assert "kernel" not in text
    assert "statistics" not in text
