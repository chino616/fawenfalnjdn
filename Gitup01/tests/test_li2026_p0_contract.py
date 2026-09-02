from __future__ import annotations

import math

import numpy as np
import pytest

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import (
    _sm_left_dim6,
    differential_flavor_kernel_nn,
)
from cevns_pyeft.theory.kinematics import two_body_recoil_max_GeV
from cevns_pyeft.theory.li2026.cross_section import (
    dsigma_dER_flavor_kernel_li2026_cm2_per_GeV,
)
from cevns_pyeft.theory.li2026.flavor import (
    dagger,
    identity_flavor_matrix,
    zero_flavor_matrix,
)
from cevns_pyeft.theory.li2026.operators import (
    canonicalize_wilson_coefficients,
)


RESPONSE = ResponseDB("data/responses/responses_all.json").get("Ge73")
E_NU_GEV = 0.005
E_NU_MEV = 5.0
SIN2THETAW = 0.23873


def _sm_left():
    return _sm_left_dim6(True, SIN2THETAW)


def _core_kernel(*, energy=E_NU_GEV, recoil_keV=0.5, left_hat=None):
    return dsigma_dER_flavor_kernel_li2026_cm2_per_GeV(
        RESPONSE,
        E_nu_GeV=energy,
        ER_keV=recoil_keV,
        left_hat=_sm_left() if left_hat is None else left_hat,
    )


def test_p0_core_and_rates_unit_ratio_is_one_million():
    core_value = float(_core_kernel()[0, 0].real)
    rate_value = float(
        differential_flavor_kernel_nn(
            RESPONSE,
            ER_keV=0.5,
            Enu_MeV=E_NU_MEV,
            include_sm=True,
            sin2thetaW=SIN2THETAW,
        ).kernel_cm2_per_keV[0, 0].real
    )

    assert core_value > 0.0
    assert rate_value > 0.0
    assert math.isclose(
        core_value / rate_value,
        1.0e6,
        rel_tol=1.0e-14,
        abs_tol=0.0,
    )


def test_p0_exact_two_body_support_includes_endpoint_only():
    mass_GeV = float(RESPONSE.get_basic("A")) * c.AMU_GEV
    endpoint_GeV = two_body_recoil_max_GeV(E_NU_GEV, mass_GeV)
    endpoint_keV = endpoint_GeV / c.keV
    below_keV = np.nextafter(endpoint_GeV, 0.0) / c.keV
    above_keV = np.nextafter(endpoint_GeV, math.inf) / c.keV

    at_zero = _core_kernel(recoil_keV=0.0)
    below = _core_kernel(recoil_keV=below_keV)
    at_endpoint = _core_kernel(recoil_keV=endpoint_keV)
    above = _core_kernel(recoil_keV=above_keV)

    assert at_zero[0, 0].real > 0.0
    assert below[0, 0].real > 0.0
    assert at_endpoint[0, 0].real >= 0.0
    np.testing.assert_array_equal(above, zero_flavor_matrix())


@pytest.mark.parametrize("energy", [0.0, -E_NU_GEV])
def test_p0_theory_core_rejects_nonpositive_neutrino_energy(energy):
    with pytest.raises(ValueError, match="E_nu_GeV"):
        _core_kernel(energy=energy)


def test_p0_theory_core_rejects_negative_recoil():
    with pytest.raises(ValueError, match="ER_GeV"):
        _core_kernel(recoil_keV=-1.0e-6)


def test_p0_malformed_string_key_is_not_silently_ignored():
    with pytest.raises(ValueError, match="Cannot parse"):
        canonicalize_wilson_coefficients(
            left_wcs={"BAD": identity_flavor_matrix()}
        )


def test_p0_unknown_triplet_is_not_silently_ignored_even_off_support():
    with pytest.raises(KeyError, match="Unknown Li2026"):
        _core_kernel(
            recoil_keV=100.0,
            left_hat={(6, 99, "u"): identity_flavor_matrix()},
        )


@pytest.mark.parametrize(
    "bad_value",
    [
        np.eye(2, dtype=complex),
        np.diag([np.nan, 0.0, 0.0]).astype(complex),
        np.diag([np.inf, 0.0, 0.0]).astype(complex),
        np.array(
            [[1.0, complex(0.0, np.inf), 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        ),
    ],
)
def test_p0_wilson_shape_and_finiteness_are_strict(bad_value):
    with pytest.raises(ValueError):
        canonicalize_wilson_coefficients(
            wc_triplets={(6, 1, "u"): bad_value}
        )


def test_p0_duplicate_string_and_triplet_inputs_are_rejected():
    coefficient = identity_flavor_matrix()
    with pytest.raises(ValueError, match="Duplicate"):
        canonicalize_wilson_coefficients(
            left_wcs={"C1u(6)": coefficient},
            wc_triplets={(6, 1, "u"): coefficient},
        )


def test_p0_sm_coefficients_are_scalar_times_identity():
    for coefficient in _sm_left().values():
        np.testing.assert_allclose(
            coefficient,
            coefficient[0, 0] * identity_flavor_matrix(),
            rtol=1.0e-14,
            atol=0.0,
        )


def test_p0_complex_coherent_state_matches_explicit_final_flavor_sum():
    coefficient = np.array(
        [
            [1.0 + 2.0j, -0.5 + 0.3j, 0.2],
            [0.1 - 0.4j, 2.0 - 1.0j, -0.7j],
            [0.7j, -0.2 + 1.1j, 0.5 - 0.6j],
        ],
        dtype=np.complex128,
    )
    psi = np.array([1.0, 1.0j, 0.0], dtype=np.complex128) / math.sqrt(2.0)
    rho = np.outer(psi, psi.conj())

    explicit = float(np.sum(np.abs(coefficient @ psi) ** 2))
    kernel = dagger(coefficient) @ coefficient
    contracted = float(np.trace(rho @ kernel).real)
    wrong_orientation = float(
        np.trace(rho @ (coefficient @ dagger(coefficient))).real
    )

    assert math.isclose(contracted, explicit, rel_tol=1.0e-14, abs_tol=0.0)
    assert not math.isclose(
        wrong_orientation,
        explicit,
        rel_tol=1.0e-6,
        abs_tol=1.0e-12,
    )

