from __future__ import annotations

import math
import csv
from pathlib import Path

import numpy as np
import pytest

from cevns_pyeft.experiments.conus.kinematics import (
    AVAILABLE_CROSS_SECTION_MODELS,
    differential_cross_section_conus_ge73,
    enu_min_heavy_nucleus_conus_ge73,
    ge73_target_mass_gev,
    helm_form_factor_ge73,
    physical_support_mask,
    recoil_max_exact_keV,
    weak_charge_ge73,
)
from cevns_pyeft.experiments.registry import get_experiment_spec

RUN_DIR = Path("workflows/experiment-integration/runs/conus_plus_ge73_pheno")


def test_publication_reproduction_enu_min_and_endpoint():
    mass = ge73_target_mass_gev()
    recoil = np.array([0.0, 0.1, 1.0, 3.0])
    expected = 1000.0 * np.sqrt(mass * recoil * 1.0e-6 / 2.0)
    assert np.allclose(enu_min_heavy_nucleus_conus_ge73(recoil), expected, rtol=1.0e-12, atol=0.0)
    assert enu_min_heavy_nucleus_conus_ge73(0.0) == 0.0

    emax = recoil_max_exact_keV(10.0)
    e_gev = 10.0e-3
    expected_endpoint = 2.0 * e_gev * e_gev / (mass + 2.0 * e_gev) * 1.0e6
    assert math.isclose(emax, expected_endpoint, rel_tol=1.0e-12)
    assert emax > 0.0


def test_physical_support_mask_and_scalar_array_behavior():
    energies = np.array([1.0, 3.0, 10.0])
    recoils = np.array([0.01, 1.0, 10.0])
    mask = physical_support_mask(energies, recoils)
    assert mask.dtype == bool
    assert mask.shape == energies.shape
    assert bool(physical_support_mask(5.0, 0.1)[0])
    assert not bool(physical_support_mask(0.0, 0.1)[0])
    assert not bool(physical_support_mask(1.0, -0.1)[0])


def test_full_response_cross_section_reuses_shared_callable():
    spec = get_experiment_spec("conus_plus_ge73_pheno")
    scalar = differential_cross_section_conus_ge73(5.0, 0.5, spec, model="full_response")
    assert isinstance(scalar, float)
    assert math.isfinite(scalar)
    assert scalar >= 0.0

    arr = differential_cross_section_conus_ge73(np.array([2.0, 5.0]), np.array([0.05, 0.5]), spec)
    assert arr.shape == (2,)
    assert np.all(np.isfinite(arr))
    assert np.all(arr >= 0.0)


def test_helm_sm_form_factor_and_restrictions():
    assert math.isclose(helm_form_factor_ge73(0.0), 1.0, rel_tol=0.0, abs_tol=1.0e-12)
    assert weak_charge_ge73() > 0.0

    sm = differential_cross_section_conus_ge73(5.0, 0.5, model="helm_sm")
    assert math.isfinite(sm)
    assert sm >= 0.0

    with pytest.raises(ValueError, match="helm_sm supports only"):
        differential_cross_section_conus_ge73(5.0, 0.5, model="helm_sm", wc_triplets={(6, 1, "u"): 1.0})

    assert set(AVAILABLE_CROSS_SECTION_MODELS) == {"full_response", "helm_sm"}


def test_phase5_diagnostic_artifacts_are_finite_and_labeled():
    endpoints = RUN_DIR / "artifacts" / "kinematic_endpoints.csv"
    grid = RUN_DIR / "artifacts" / "cross_section_grid.csv"
    full_fig = RUN_DIR / "figures" / "cross_section_vs_recoil.png"
    compare_fig = RUN_DIR / "figures" / "full_response_vs_helm.png"
    assert endpoints.exists()
    assert grid.exists()
    assert full_fig.exists() and full_fig.stat().st_size > 0
    assert compare_fig.exists() and compare_fig.stat().st_size > 0

    with endpoints.open(encoding="utf-8", newline="") as handle:
        endpoint_rows = list(csv.DictReader(handle))
    assert endpoint_rows
    assert all(float(row["recoil_max_exact_keV"]) >= 0.0 for row in endpoint_rows)

    with grid.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["model"] for row in rows} == {"full_response", "helm_sm"}
    assert {row["kinematics"] for row in rows} == {"publication_reproduction"}
    values = np.array([float(row["dsigma_dT_cm2_per_keV"]) for row in rows])
    assert np.all(np.isfinite(values))
    assert np.all(values >= 0.0)
