import math

import numpy as np
import pytest

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.foundation.units import cm2_per_GeV_to_cm2_per_keV
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import (
    _sm_left_dim6,
    differential_flavor_kernel_nn,
)
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.cross_section import (
    amplitude_kernel_to_dsigma_cm2_per_GeV,
)
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS, Li2026LECs
from cevns_pyeft.theory.li2026.left_to_ci import left_to_ci
from cevns_pyeft.theory.li2026.responses import RKinematics, responses_R


def _single_entry(value=1.0 + 0.0j):
    matrix = np.zeros((3, 3), dtype=np.complex128)
    matrix[0, 1] = value
    return matrix


def _trapz(y, x):
    trapezoid = getattr(np, "trapezoid", None)
    if trapezoid is not None:
        return float(trapezoid(y, x))
    return float(np.trapz(y, x))


def test_li2026_lecs_match_current_proof_table():
    lecs = DEFAULT_LECS
    expected = {
        "L1": 1.855,
        "L2": -1.017,
        "L3": 0.6377,
        "L4": -0.220,
        "L5": 1.38e-3,
        "L6": -0.49e-3,
        "L7": -6.76e-3,
        "L8": 2.65e-3,
        "L9": 11.52e-3,
        "L10": 24.05e-3,
        "L11": -17.7e-3,
        "L12": -13.9e-3,
        "L13": -50.4e-3,
        "L14": -0.306,
        "B0_m_u": 6200.0e-6,
        "B0_m_d": 13300.0e-6,
        "sigma_u_p": 18.5e-3,
        "sigma_d_p": 36.0e-3,
        "sigma_u_n": 16.7e-3,
        "sigma_d_n": 39.7e-3,
    }

    for name, value in expected.items():
        assert getattr(lecs, name) == pytest.approx(value)


def test_foundation_lec_table_is_the_source_for_li2026_defaults():
    lecs = Li2026LECs()

    for index in range(1, 15):
        assert getattr(lecs, f"L{index}") == c.LECs_known[f"L{index}"]

    assert c.LECs_known["L6"] < 0.0
    assert c.LECs_known_sigma["L11"] == pytest.approx(2.0e-3)
    assert c.LECs_unknown_NDA["g1"] == pytest.approx(c.Lambda_chi)
    assert c.LECs_unknown_NDA["g5"] == pytest.approx(1.0)


def test_c10_current_proof_pion_pole_contains_mN():
    coeff_u = 2.0e-6 + 3.0e-7j
    coeff_d = -4.0e-7 + 1.0e-7j
    c77_coeff = -8.0e-8
    left = {
        (7, 5, "u"): _single_entry(coeff_u),
        (7, 5, "d"): _single_entry(coeff_d),
        (7, 7, ""): _single_entry(c77_coeff),
    }
    kin = {"E_nu": 0.05, "q0": 1.0e-5, "qabs": 0.01}
    lecs = DEFAULT_LECS
    ci = left_to_ci(left, **kin)
    q2 = kin["q0"] ** 2 - kin["qabs"] ** 2
    c10_ud_p = lecs.B0_m_u * coeff_u - lecs.B0_m_d * coeff_d
    expected = (
        lecs.g_A
        * lecs.m_N
        * c10_ud_p
        / (lecs.m_pi**2 - q2)
        + (lecs.L11 + lecs.L12) * coeff_u
        + lecs.L12 * coeff_d
        + lecs.L14 * c77_coeff
    )

    assert ci.p[10][0, 1] == pytest.approx(expected)


def test_legacy_c10_equal_light_quark_mass_is_not_current_proof():
    left = {
        (7, 5, "u"): _single_entry(1.0e-6),
        (7, 5, "d"): _single_entry(2.0e-6),
    }
    kin = {"E_nu": 0.05, "q0": 1.0e-5, "qabs": 0.01}

    current = left_to_ci(left, **kin)
    legacy = left_to_ci(
        left,
        c10_mass_mode="legacy_equal_light_quark_mass",
        **kin,
    )

    assert not np.isclose(current.p[10][0, 1], legacy.p[10][0, 1])
    with pytest.raises(ValueError, match="Unknown c10_mass_mode"):
        left_to_ci(left, c10_mass_mode="paper", **kin)


def test_cm2_per_GeV_to_cm2_per_keV_boundary_and_recoil_integral():
    response = ResponseDB("data/responses/responses_all.json").get("Ge73")
    energy = 0.005
    mA = float(response.get_basic("A")) * c.AMU_GEV
    amplitude_kernel = flavor_kernel_onebody_li2026(
        response,
        E_nu_GeV=energy,
        ER_keV=0.5,
        left_hat=_sm_left_dim6(True, 0.23873),
    ).kernel

    core = amplitude_kernel_to_dsigma_cm2_per_GeV(
        amplitude_kernel,
        E_nu_GeV=energy,
        m_A_GeV=mA,
    )
    rate = cm2_per_GeV_to_cm2_per_keV(core)

    assert np.all(core.diagonal().real > rate.diagonal().real)
    nonzero = np.abs(rate) > 0.0
    np.testing.assert_allclose(core[nonzero] / rate[nonzero], 1.0e6)

    er_kev = np.linspace(0.1, 0.6, 7)
    core_values = np.array([core[0, 0].real for _ in er_kev])
    rate_values = cm2_per_GeV_to_cm2_per_keV(core_values)
    integral_gev_axis = _trapz(core_values, er_kev * c.keV)
    integral_kev_axis = _trapz(rate_values, er_kev)
    assert math.isclose(integral_gev_axis, integral_kev_axis, rel_tol=1e-14)


def test_rates_kernel_remains_explicit_per_keV_wrapper():
    response = ResponseDB("data/responses/responses_all.json").get("Ge73")
    rates_kernel = differential_flavor_kernel_nn(
        response,
        ER_keV=0.5,
        Enu_MeV=5.0,
        include_sm=True,
        sin2thetaW=0.23873,
    ).kernel_cm2_per_keV
    core_kernel = amplitude_kernel_to_dsigma_cm2_per_GeV(
        flavor_kernel_onebody_li2026(
            response,
            E_nu_GeV=0.005,
            ER_keV=0.5,
            left_hat=_sm_left_dim6(True, 0.23873),
        ).kernel,
        E_nu_GeV=0.005,
        m_A_GeV=float(response.get_basic("A")) * c.AMU_GEV,
    )

    np.testing.assert_allclose(
        rates_kernel,
        cm2_per_GeV_to_cm2_per_keV(core_kernel),
        rtol=1e-14,
        atol=0.0,
    )


def test_y_from_qb_is_dimensionless():
    q_gev = 0.012
    b_invgev = c.b_ho_invgev(133)
    expected = (q_gev * b_invgev / 2.0) ** 2

    assert c.y_from_qb(q_gev, b_invgev) == pytest.approx(expected)


def test_response_terms_have_uniform_gevm2_scaling_for_c13_contract():
    scale = 2.5
    ci_basis = {
        1: (_single_entry(3.0e-6), np.zeros((3, 3), dtype=np.complex128)),
        13: (_single_entry(4.0e-9), np.zeros((3, 3), dtype=np.complex128)),
    }
    scaled_kin = RKinematics(
        Enu=0.05 * scale,
        qabs=0.01 * scale,
        m_A=67.95 * scale,
        m_N=0.938 * scale,
    )
    scaled_ci = {
        1: (ci_basis[1][0] / scale**2, ci_basis[1][1] / scale**2),
        13: (ci_basis[13][0] / scale**3, ci_basis[13][1] / scale**3),
    }

    base = responses_R(
        ci_basis,
        RKinematics(Enu=0.05, qabs=0.01, m_A=67.95, m_N=0.938),
        tau=0,
        taup=0,
    )["M"]
    scaled = responses_R(scaled_ci, scaled_kin, tau=0, taup=0)["M"]

    np.testing.assert_allclose(scaled, base / scale**2, rtol=1e-14, atol=0.0)
