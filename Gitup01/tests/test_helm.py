from __future__ import annotations

import math

import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.theory.helm import (
    cevns_kinematic_factor,
    dsigma_dER_helm_cm2_per_keV,
    dsigma_dER_helm_density_cm2_per_keV,
    dsigma_dER_helm_kernel_cm2_per_keV,
    helm_form_factor,
    helm_form_factor_squared,
    nuclear_mass_GeV,
    nuclear_weak_charge_matrix,
    recoil_max_keV,
    sm_weak_charge,
)
from cevns_pyeft.theory.li2026.flavor import flavor_projector, identity_flavor_matrix


def test_helm_zero_momentum_normalization() -> None:
    assert helm_form_factor(0.0, 73) == 1.0
    np.testing.assert_allclose(helm_form_factor([0.0, 0.0], 133), [1.0, 1.0])


def test_helm_squared_is_square_of_linear_form_factor() -> None:
    er = np.array([0.0, 0.1, 1.0, 5.0, 20.0])
    f = np.asarray(helm_form_factor(er, 133))
    f2 = np.asarray(helm_form_factor_squared(er, 133))
    np.testing.assert_allclose(f2, f * f, rtol=1e-14, atol=0.0)


def test_mathematica_kinematic_factor_matches_reference_formula() -> None:
    e_mev = 5.0
    er_kev = 0.5
    A = 73
    e = e_mev * c.MeV
    t = er_kev * c.keV
    m_a = nuclear_mass_GeV(A)
    expected = 1.0 - m_a * t / (2.0 * e * e)
    got = cevns_kinematic_factor(e_mev, er_kev, A, kinematics="mathematica")
    assert math.isclose(got, expected, rel_tol=1e-14, abs_tol=0.0)


def test_forbidden_recoil_returns_zero() -> None:
    e_mev = 4.0
    A, Z = 73, 32
    tmax = recoil_max_keV(e_mev, A)
    assert dsigma_dER_helm_cm2_per_keV(e_mev, 1.01 * tmax, A, Z) == 0.0


def test_sm_flavor_kernel_reduces_to_scalar_cross_section() -> None:
    e_mev, er_kev = 30.0, 2.0
    A, Z = 133, 55
    scalar = dsigma_dER_helm_cm2_per_keV(e_mev, er_kev, A, Z)
    kernel = dsigma_dER_helm_kernel_cm2_per_keV(e_mev, er_kev, A, Z)
    np.testing.assert_allclose(kernel, scalar * np.eye(3), rtol=1e-13, atol=0.0)


def test_sm_density_result_is_independent_of_normalized_rho() -> None:
    e_mev, er_kev = 12.0, 0.2
    A, Z = 73, 32
    scalar = dsigma_dER_helm_cm2_per_keV(e_mev, er_kev, A, Z)
    rho = np.array(
        [
            [0.5, 0.25, 0.0],
            [0.25, 0.5, 0.0],
            [0.0, 0.0, 0.0],
        ],
        dtype=np.complex128,
    )
    got = dsigma_dER_helm_density_cm2_per_keV(e_mev, er_kev, A, Z, rho)
    assert math.isclose(got, scalar, rel_tol=1e-13, abs_tol=0.0)


def test_general_flavor_kernel_is_qdagger_q_and_positive_semidefinite() -> None:
    e_mev, er_kev = 30.0, 1.0
    A, Z = 40, 18
    qmat = np.array(
        [
            [1.0 + 0.2j, 2.0, 0.0],
            [0.5j, -1.0, 3.0],
            [0.1, 0.0, 0.7 - 0.4j],
        ],
        dtype=np.complex128,
    )
    kernel = dsigma_dER_helm_kernel_cm2_per_keV(
        e_mev, er_kev, A, Z, weak_charge_matrix=qmat
    )
    assert np.allclose(kernel, kernel.conj().T, atol=1e-14, rtol=1e-14)
    assert np.linalg.eigvalsh(kernel).min() >= -1e-55

    # For a pure initial electron neutrino, summing unobserved final flavors
    # is exactly the electron-column norm of Q.
    rho_e = flavor_projector("e")
    from_trace = dsigma_dER_helm_density_cm2_per_keV(
        e_mev, er_kev, A, Z, rho_e, weak_charge_matrix=qmat
    )
    column_norm = float(np.vdot(qmat[:, 0], qmat[:, 0]).real)
    pref = kernel[0, 0].real / column_norm
    assert math.isclose(from_trace, pref * column_norm, rel_tol=1e-13, abs_tol=0.0)


def test_nucleon_charge_builder_has_correct_sm_limit() -> None:
    A, Z = 133, 55
    s2w = 0.2387
    ident = identity_flavor_matrix()
    qmat = nuclear_weak_charge_matrix(
        A,
        Z,
        proton_coupling=-(1.0 - 4.0 * s2w) * ident,
        neutron_coupling=ident,
    )
    np.testing.assert_allclose(qmat, sm_weak_charge(A, Z, sin2_theta_w=s2w) * ident)
