from pathlib import Path

import numpy as np
import pytest

from cevns_pyeft.experiments.conus_plus.slow_counts import (
    COMPONENTS,
    DETECTOR_ORDER,
    ENERGY_REGION_BOUNDS_MEV,
    ENERGY_REGION_LABELS,
    EXPOSURES_KG_DAY,
    NUCLEI_PER_KG,
    SECONDS_PER_DAY,
    slow_counts_conus_plus,
    true_recoil_rate_components_per_kg_day,
)


RESPONSES = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "responses"
    / "responses_all.json"
)


@pytest.fixture(scope="module")
def small_result():
    return slow_counts_conus_plus(
        RESPONSES,
        n_recoil=18,
        n_energy=4,
    )


def test_normalization_ledger_constants_are_unique_and_reproducible():
    expected_nuclei_per_kg = 1.0 / (73.0 * 1.6605390666e-27)
    assert NUCLEI_PER_KG == pytest.approx(expected_nuclei_per_kg)
    assert SECONDS_PER_DAY == 86400.0
    np.testing.assert_allclose(EXPOSURES_KG_DAY, [119.0, 119.0, 119.0])
    assert np.sum(EXPOSURES_KG_DAY) == pytest.approx(357.0)


def test_true_recoil_rate_has_component_axis_and_physical_support():
    recoil = np.array([0.5, 1.0, 2.0, 3.0])
    rates = true_recoil_rate_components_per_kg_day(
        recoil,
        RESPONSES,
        n_energy=4,
    )
    assert rates.shape == (4, len(COMPONENTS))
    assert np.all(np.isfinite(rates))
    assert np.all(rates >= 0.0)
    assert np.sum(rates[:3]) > 0.0
    np.testing.assert_array_equal(rates[-1], np.zeros(len(COMPONENTS)))


def test_energy_region_rates_sum_to_the_direct_unsplit_integral():
    recoil = np.array([0.2, 0.8, 1.5, 2.5])
    direct = true_recoil_rate_components_per_kg_day(
        recoil,
        RESPONSES,
        n_energy=8,
    )
    split = sum(
        (
            true_recoil_rate_components_per_kg_day(
                recoil,
                RESPONSES,
                n_energy=8,
                energy_range_mev=bounds,
            )
            for bounds in ENERGY_REGION_BOUNDS_MEV
        ),
        start=np.zeros_like(direct),
    )
    np.testing.assert_allclose(split, direct, rtol=2.0e-10, atol=0.0)


def test_slow_output_contract_and_component_sums(small_result):
    component = small_result["counts_per_detector_component_bin"]
    by_region = small_result[
        "counts_per_detector_component_energy_region_bin"
    ]
    detector = small_result["counts_per_detector_bin"]
    combined = small_result["combined_counts_per_bin"]

    assert component.shape == (3, 4, 19)
    assert by_region.shape == (3, 4, 2, 19)
    assert detector.shape == (3, 19)
    assert combined.shape == (19,)
    assert small_result["detector_order"] == DETECTOR_ORDER
    assert small_result["component_order"] == COMPONENTS
    assert small_result["energy_region_labels"] == ENERGY_REGION_LABELS
    assert small_result["energy_region_bounds_mev"] == ENERGY_REGION_BOUNDS_MEV
    assert np.all(np.isfinite(by_region)) and np.all(by_region >= 0.0)
    np.testing.assert_allclose(component, np.sum(by_region, axis=2))
    np.testing.assert_allclose(detector, np.sum(component, axis=1))
    np.testing.assert_allclose(combined, np.sum(detector, axis=0))
    np.testing.assert_allclose(
        combined,
        np.sum(
            small_result["combined_counts_per_energy_region_bin"],
            axis=0,
        ),
    )
    assert small_result["total_events"] == pytest.approx(
        float(np.sum(combined))
    )


def test_energy_region_split_is_unscaled_and_nontrivial(small_result):
    region = small_result["combined_counts_per_energy_region_bin"]
    assert region.shape == (2, 19)
    assert np.sum(region[0]) > np.sum(region[1]) > 0.0
    assert region[1, -1] > 0.0
    fraction = np.divide(
        region[1],
        np.sum(region, axis=0),
        out=np.zeros(19),
        where=np.sum(region, axis=0) > 0.0,
    )
    assert fraction[-1] > fraction[0]


def test_detector_threshold_masks_and_exposure_scaling(small_result):
    detector = small_result["counts_per_detector_bin"]
    assert detector[0, 0] == 0.0 and detector[0, 1] == 0.0
    assert detector[2, 0] == 0.0
    assert detector[1, 0] > 0.0

    doubled = slow_counts_conus_plus(
        RESPONSES,
        exposures_kg_day=2.0 * EXPOSURES_KG_DAY,
        n_recoil=18,
        n_energy=4,
    )
    np.testing.assert_allclose(
        doubled["counts_per_detector_bin"],
        2.0 * detector,
        rtol=2.0e-13,
        atol=0.0,
    )


def test_reference_counts_are_not_used_as_a_rescaling_target(small_result):
    assert small_result["normalization"]["reference_count_rescaling"] is False
    assert small_result["model"]["sin2theta_w"] == pytest.approx(0.23857)
    assert small_result["model"]["particle_kind"] == "antinu"


def test_direct_slow_path_accepts_a_complex_flavor_wilson_matrix():
    coefficient = np.zeros((3, 3), dtype=np.complex128)
    coefficient[0, 1] = 1.0e-6 + 2.0e-7j
    result = slow_counts_conus_plus(
        RESPONSES,
        wc_triplets={(6, 1, "u"): coefficient},
        n_recoil=8,
        n_energy=2,
    )
    counts = result["counts_per_detector_bin"]
    assert counts.shape == (3, 19)
    assert np.all(np.isfinite(counts))
    assert np.all(counts >= 0.0)
    assert result["total_events"] > 0.0
