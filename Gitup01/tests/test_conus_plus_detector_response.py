import numpy as np
import pytest

from cevns_pyeft.experiments.conus_plus.detector_response import (
    BIN_EDGES_EVEE,
    DETECTOR_THRESHOLDS_EVEE,
    detector_bin_acceptance,
    efficiency_reconstructed,
    mean_reconstructed_energy_evee,
    quenching_factor,
    resolution_sigma_evee,
    response_contract,
    response_density_evee,
    response_interval_probability_evee,
)


def test_lindhard_mapping_is_finite_bounded_and_monotonic():
    recoil = np.linspace(0.0, 3.0, 301)
    quenching = quenching_factor(recoil)
    mean = mean_reconstructed_energy_evee(recoil)

    assert quenching[0] == 0.0
    assert mean[0] == 0.0
    assert np.all(np.isfinite(quenching))
    assert np.all((0.0 <= quenching) & (quenching < 1.0))
    assert np.all(np.diff(mean) >= 0.0)


def test_resolution_is_positive_and_uses_mean_ionization_energy():
    mean = np.array([0.0, 160.0, 350.0])
    sigma = resolution_sigma_evee(mean)

    assert sigma[0] == pytest.approx(20.38)
    assert np.all(sigma > 0.0)
    assert np.all(np.diff(sigma) > 0.0)


@pytest.mark.parametrize("recoil_kev", [0.1, 0.5, 1.0, 2.0])
def test_gaussian_is_nonnegative_and_normalized_on_full_real_line(recoil_kev):
    mean = mean_reconstructed_energy_evee(recoil_kev)
    sigma = resolution_sigma_evee(mean)
    grid = np.linspace(mean - 10.0 * sigma, mean + 10.0 * sigma, 20001)
    density = response_density_evee(grid, recoil_kev)

    assert np.all(density >= 0.0)
    assert np.trapezoid(density, grid) == pytest.approx(1.0, rel=2.0e-8)
    assert response_interval_probability_evee(
        recoil_kev, mean - 12.0 * sigma, mean + 12.0 * sigma
    ) == pytest.approx(1.0, abs=1.0e-15)


@pytest.mark.parametrize(
    "detector, threshold",
    sorted(DETECTOR_THRESHOLDS_EVEE.items()),
)
def test_efficiency_is_exact_step_on_reconstructed_energy(detector, threshold):
    values = efficiency_reconstructed(
        np.array([threshold - 1.0e-9, threshold, threshold + 1.0e-9]),
        detector,
    )
    np.testing.assert_array_equal(values, np.array([0.0, 1.0, 1.0]))


def test_detector_bin_acceptance_keeps_migration_losses_outside_window():
    recoil = np.array([0.2, 0.5, 1.0, 2.0])
    acceptance = detector_bin_acceptance(recoil, "C3")

    assert acceptance.shape == (4, 19)
    assert np.all((0.0 <= acceptance) & (acceptance <= 1.0))
    assert np.all(np.sum(acceptance, axis=-1) <= 1.0)
    assert np.any(np.sum(acceptance, axis=-1) < 0.99)

    expected = np.array(
        [
            response_interval_probability_evee(value, 160.0, 350.0)
            for value in recoil
        ]
    )
    np.testing.assert_allclose(np.sum(acceptance, axis=-1), expected)


def test_detector_thresholds_apply_independently_on_common_bins():
    recoil = 1.0
    c2 = detector_bin_acceptance(recoil, "C2")
    c3 = detector_bin_acceptance(recoil, "C3")
    c5 = detector_bin_acceptance(recoil, "C5")

    assert c2.shape == c3.shape == c5.shape == (19,)
    assert c2[0] == 0.0 and c2[1] == 0.0
    assert c5[0] == 0.0
    assert np.sum(c3) >= np.sum(c5) >= np.sum(c2)


def test_scalar_array_broadcast_and_invalid_inputs():
    reco = np.array([100.0, 160.0, 200.0])[:, None]
    recoil = np.array([0.2, 0.5, 1.0])[None, :]
    density = response_density_evee(reco, recoil)
    assert density.shape == (3, 3)

    with pytest.raises(ValueError, match="finite and non-negative"):
        mean_reconstructed_energy_evee(-0.1)
    with pytest.raises(KeyError, match="unknown CONUS"):
        efficiency_reconstructed(200.0, "C4")


def test_response_contract_records_full_domain_and_no_window_renormalization():
    contract = response_contract()

    assert contract["resolution_model"] == "full_real_line_Gaussian"
    assert contract["efficiency_model"] == (
        "detector_specific_exact_reconstructed_energy_step"
    )
    assert contract["analysis_window_renormalization"] is False
    assert contract["analysis_edges_evee"] == BIN_EDGES_EVEE.tolist()
