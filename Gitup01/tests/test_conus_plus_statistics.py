import numpy as np
import pytest

from cevns_pyeft.experiments.conus_plus.statistics import (
    QuadraticSpectrum1D,
    QuadraticSpectrum2D,
    profile_paper_eq33,
)
from cevns_pyeft.statistics.parameters import (
    VectorNSIParameters,
    vector_nsi_to_np_wilson,
)


def test_eq33_profile_matches_closed_form_and_keeps_negative_excess():
    signal = np.linspace(0.2, 4.0, 19)
    observed = signal.copy()
    observed[[2, 11]] = [-1.0, -0.4]
    sigma = np.linspace(2.0, 4.0, 19)
    result = profile_paper_eq33(signal, observed, sigma)

    weight = 1.0 / sigma**2
    expected_alpha = np.sum(weight * signal * (observed - signal)) / (
        np.sum(weight * signal**2) + 0.169**-2
    )
    expected_chi2 = np.sum(
        ((observed - (1.0 + expected_alpha) * signal) / sigma) ** 2
    ) + (expected_alpha / 0.169) ** 2
    assert result.alpha == pytest.approx(expected_alpha, rel=0.0, abs=1.0e-14)
    assert result.chi2 == pytest.approx(expected_chi2, rel=0.0, abs=1.0e-13)


def test_eq33_rejects_wrong_shape_and_poisson_like_zero_sigma():
    with pytest.raises(ValueError, match="19"):
        profile_paper_eq33(np.ones(18), np.ones(18), np.ones(18))
    with pytest.raises(ValueError, match="strictly positive"):
        profile_paper_eq33(np.ones(19), np.ones(19), np.zeros(19))


def test_quadratic_spectrum_1d_reconstructs_independent_point():
    x0 = 0.24
    a = np.linspace(1.0, 2.0, 19)
    b = np.linspace(-0.4, 0.3, 19)
    c = np.linspace(0.2, 0.8, 19)

    def direct(x):
        dx = x - x0
        return a + b * dx + c * dx**2

    model = QuadraticSpectrum1D.from_symmetric_samples(
        x0,
        0.05,
        direct(x0 - 0.05),
        direct(x0),
        direct(x0 + 0.05),
    )
    np.testing.assert_allclose(model.evaluate(0.317), direct(0.317), rtol=0.0, atol=1.0e-14)


def test_quadratic_spectrum_2d_reconstructs_cross_term():
    a = np.linspace(1.0, 2.0, 19)
    bx = np.linspace(-0.4, 0.3, 19)
    by = np.linspace(0.5, -0.2, 19)
    cxx = np.linspace(0.2, 0.8, 19)
    cxy = np.linspace(-0.3, 0.4, 19)
    cyy = np.linspace(0.1, 0.6, 19)

    def direct(x, y):
        return a + bx * x + by * y + cxx * x**2 + cxy * x * y + cyy * y**2

    h = 0.1
    model = QuadraticSpectrum2D.from_axis_and_corner_samples(
        h,
        direct(0.0, 0.0),
        direct(-h, 0.0),
        direct(h, 0.0),
        direct(0.0, -h),
        direct(0.0, h),
        direct(h, h),
    )
    np.testing.assert_allclose(model.evaluate(0.07, -0.04), direct(0.07, -0.04), rtol=0.0, atol=1.0e-14)


def test_vector_nsi_flavor_changing_emu_and_etau_have_identical_norms():
    emu = vector_nsi_to_np_wilson(
        VectorNSIParameters(epsilon_emu_uV=0.07, epsilon_emu_dV=-0.04)
    )
    etau = vector_nsi_to_np_wilson(
        VectorNSIParameters(epsilon_etau_uV=0.07, epsilon_etau_dV=-0.04)
    )
    for triplet in ((6, 1, "u"), (6, 1, "d")):
        np.testing.assert_allclose(emu[triplet], emu[triplet].conj().T)
        np.testing.assert_allclose(etau[triplet], etau[triplet].conj().T)
        assert np.linalg.norm(emu[triplet]) == pytest.approx(
            np.linalg.norm(etau[triplet]), rel=0.0, abs=1.0e-18
        )
