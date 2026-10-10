from __future__ import annotations

import numpy as np
import pytest

from cevns_pyeft.experiments.conus_plus.source import (
    COMPONENTS,
    ENERGY_SUPPORT_MEV,
    FLUX_UNIT,
    LOW_END_POLICY,
    NORMALIZATION_UNCERTAINTY_FRACTION,
    TIME_BASIS,
    TOTAL_FLUX_CM2_S,
    differential_flux,
    fission_fractions,
    kopeikin_nodes,
    load_reactor_flux,
    mueller_coefficients,
    normalization_integral,
    source_state,
)
from cevns_pyeft.experiments.specs import load_experiment_spec


def test_source_tables_match_registered_evidence():
    energies, values = kopeikin_nodes()
    coefficients = mueller_coefficients()
    fractions = fission_fractions()

    assert energies.shape == values.shape == (32,)
    assert energies[0] == pytest.approx(0.01)
    assert energies[-1] == pytest.approx(2.0)
    assert values[0] == pytest.approx(0.0774)
    assert values[-1] == pytest.approx(1.3)
    assert tuple(coefficients) == COMPONENTS
    assert all(coefficients[key].shape == (6,) for key in COMPONENTS)
    assert fractions == {
        "U235": 0.56,
        "U238": 0.07,
        "Pu239": 0.31,
        "Pu241": 0.06,
    }
    assert sum(fractions.values()) == pytest.approx(1.0, abs=1.0e-15)


def test_matching_and_nonnegative_normalization_diagnostics():
    assert normalization_integral() == pytest.approx(
        6.461355163040059,
        rel=2.0e-13,
    )
    assert LOW_END_POLICY == "linear_extrapolation_clamped_nonnegative"

    for component in COMPONENTS:
        left = differential_flux(component, 2.0 - 1.0e-9)
        at_match = differential_flux(component, 2.0)
        assert left == pytest.approx(at_match, rel=3.0e-9)


def test_total_flux_is_component_sum_and_has_strict_support():
    energies = np.linspace(-0.1, 10.1, 20001)
    components = np.stack(
        [differential_flux(component, energies) for component in COMPONENTS]
    )
    total = differential_flux("total", energies)

    assert np.all(np.isfinite(components))
    assert np.all(components >= 0.0)
    np.testing.assert_allclose(total, components.sum(axis=0), rtol=2.0e-15)
    assert differential_flux("total", -1.0) == 0.0
    assert differential_flux("total", 10.000001) == 0.0
    assert differential_flux("total", 0.0) == 0.0
    assert differential_flux("total", 0.006) == 0.0
    assert differential_flux("total", 0.01) > 0.0


def test_detector_site_absolute_normalization():
    low_nodes, _ = kopeikin_nodes()
    zero_crossing = 0.006538461538461538
    low_grid = np.concatenate(([0.0, zero_crossing], low_nodes))
    low_integral = np.trapezoid(differential_flux("total", low_grid), low_grid)

    nodes, weights = np.polynomial.legendre.leggauss(256)
    high_grid = 0.5 * (8.0 * nodes + 12.0)
    high_integral = 4.0 * np.dot(
        weights,
        differential_flux("total", high_grid),
    )
    assert low_integral + high_integral == pytest.approx(
        TOTAL_FLUX_CM2_S,
        rel=2.0e-13,
    )


def test_scalar_array_state_and_metadata_contract():
    scalar = differential_flux("total", 3.0)
    array = differential_flux("total", np.array([[0.0, 2.0], [3.0, 11.0]]))
    state = source_state()
    loaded = load_reactor_flux()

    assert isinstance(scalar, float)
    assert array.shape == (2, 2)
    assert state.particle_kind == "antinu"
    assert state.rho.shape == (3, 3)
    assert loaded["state"].particle_kind == "antinu"
    assert loaded["basic"]["fluxUnit"] == FLUX_UNIT
    assert loaded["basic"]["timeBasis"] == TIME_BASIS
    assert loaded["basic"]["energySupportMeV"] == ENERGY_SUPPORT_MEV
    assert loaded["basic"]["normalizationUncertaintyFraction"] == pytest.approx(
        NORMALIZATION_UNCERTAINTY_FRACTION
    )
    assert loaded["measured"]["total"](3.0) == pytest.approx(scalar)
    with pytest.raises(ValueError, match="component"):
        differential_flux("unknown", 3.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite"):
        differential_flux("total", np.nan)


def test_selected_exposure_profile_and_mueller_extension_metadata():
    spec = load_experiment_spec("conus_plus_2025_c2c3c5_ge73_pyeft").data
    exposure = spec["exposure"]
    source = spec["source"]

    assert exposure["calculation_profile"] == "user_selected_equal_119_each"
    assert exposure["values_kg_day"] == [119.0, 119.0, 119.0]
    assert exposure["selected_sum_kg_day"] == pytest.approx(357.0)
    assert exposure["raw_observed_values_kg_day"] == [111.15, 103.40, 111.86]
    assert exposure["raw_observed_sum_kg_day"] == pytest.approx(326.41)
    np.testing.assert_allclose(
        exposure["target_nucleus_seconds"],
        np.full(3, 8.481814035536064e31),
        rtol=2.0e-15,
    )

    assert source["mueller_fit_domain_mev"] == [2.0, 8.0]
    assert source["high_energy_extension_domain_mev"] == [8.0, 10.0]
    assert source["high_energy_extension_policy"] == (
        "continue_same_mueller_polynomial_baseline"
    )
    assert source["high_energy_extension_status"] == (
        "model_assumption_requires_P07_binwise_sensitivity"
    )


def test_mueller_baseline_is_integrable_on_fit_and_extension_domains():
    nodes, weights = np.polynomial.legendre.leggauss(128)

    def integrate(a: float, b: float) -> float:
        grid = 0.5 * ((b - a) * nodes + (a + b))
        return 0.5 * (b - a) * float(
            np.dot(weights, differential_flux("total", grid))
        )

    fitted = integrate(2.0, 8.0)
    extended = integrate(8.0, 10.0)

    assert np.isfinite(fitted) and fitted > 0.0
    assert np.isfinite(extended) and extended > 0.0
    assert fitted + extended < TOTAL_FLUX_CM2_S

