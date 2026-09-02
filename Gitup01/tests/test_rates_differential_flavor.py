import math
from typing import get_args

import numpy as np
import pytest

from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import (
    NeutrinoFlavor,
    SourceSpecies,
    _build_wc_triplets,
    _sm_left_dim6,
    differential_cross_section_nn,
    differential_flavor_kernel_nn,
)
from cevns_pyeft.theory.li2026.cross_section import (
    dsigma_dER_flavor_kernel_li2026_cm2_per_GeV,
)
from cevns_pyeft.theory.li2026.flavor import (
    contract_density_kernel,
    flavor_projector,
    identity_flavor_matrix,
    zero_flavor_matrix,
)


RESPONSE = ResponseDB("data/responses/responses_all.json").get("Ge73")
E_NU_MEV = 5.0
ER_KEV = 0.5
SIN2THETAW = 0.23873


def _random_density_matrix():
    raw = np.array(
        [
            [1.0 + 0.2j, -0.3j, 0.4],
            [0.1, 0.7 - 0.1j, -0.2j],
            [0.3j, 0.2, 0.5 + 0.4j],
        ],
        dtype=complex,
    )
    rho = raw @ raw.conj().T
    return rho / np.trace(rho)


def _flavor_changing_coefficient():
    coefficient = zero_flavor_matrix()
    coefficient[0, 1] = 1.0e-6 + 2.0e-7j
    coefficient[0, 2] = -4.0e-7 + 1.0e-7j
    return coefficient


def test_source_species_is_distinct_from_neutrino_hilbert_space_flavor():
    assert set(get_args(SourceSpecies)) == {"all", "e", "mu", "mub", "mmb"}
    assert get_args(NeutrinoFlavor) == ("e", "mu", "tau")


def test_build_wc_triplets_preserves_flavor_matrices_for_both_key_styles():
    triplet_value = _flavor_changing_coefficient()
    string_value = 2.0 * triplet_value

    built = _build_wc_triplets(
        left_wcs={"C1u(6)": string_value},
        wc_triplets={(6, 1, "d"): triplet_value},
    )

    np.testing.assert_array_equal(built[(6, 1, "u")], string_value)
    np.testing.assert_array_equal(built[(6, 1, "d")], triplet_value)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"wc_triplets": {(6, 1, "u"): 1.0e-6}},
        {"left_wcs": {"C1u(6)": 1.0e-6}},
    ],
)
def test_build_wc_triplets_rejects_scalar_wilson_values(kwargs):
    with pytest.raises(ValueError, match="shape"):
        _build_wc_triplets(**kwargs)


def test_sm_coefficients_are_flavor_universal_matrices():
    sm = _sm_left_dim6(True, SIN2THETAW)

    assert set(sm) == {
        (6, 1, "u"),
        (6, 1, "d"),
        (6, 2, "u"),
        (6, 2, "d"),
    }
    for coefficient in sm.values():
        assert coefficient.shape == (3, 3)
        np.testing.assert_allclose(
            coefficient,
            coefficient[0, 0] * identity_flavor_matrix(),
            rtol=1e-14,
            atol=0.0,
        )


def test_differential_kernel_shapes_follow_energy_shape_and_support():
    scalar = differential_flavor_kernel_nn(
        RESPONSE,
        ER_keV=ER_KEV,
        Enu_MeV=E_NU_MEV,
        include_sm=True,
        sin2thetaW=SIN2THETAW,
    )
    energies = np.array([0.0, E_NU_MEV, 6.0])
    vector = differential_flavor_kernel_nn(
        RESPONSE,
        ER_keV=ER_KEV,
        Enu_MeV=energies,
        include_sm=True,
        sin2thetaW=SIN2THETAW,
    )

    assert scalar.kernel_cm2_per_keV.shape == (3, 3)
    assert vector.kernel_cm2_per_keV.shape == (3, 3, 3)
    np.testing.assert_array_equal(
        vector.kernel_cm2_per_keV[0],
        zero_flavor_matrix(),
    )
    np.testing.assert_allclose(
        vector.kernel_cm2_per_keV[1],
        scalar.kernel_cm2_per_keV,
        rtol=1e-14,
        atol=0.0,
    )


def test_sm_differential_rate_is_independent_of_physical_density_matrix():
    kernel = differential_flavor_kernel_nn(
        RESPONSE,
        ER_keV=ER_KEV,
        Enu_MeV=E_NU_MEV,
        include_sm=True,
        sin2thetaW=SIN2THETAW,
    ).kernel_cm2_per_keV
    densities = [
        flavor_projector("e"),
        flavor_projector("mu"),
        flavor_projector("tau"),
        _random_density_matrix(),
    ]

    np.testing.assert_allclose(kernel, kernel.conj().T, rtol=1e-14, atol=0.0)
    np.testing.assert_allclose(
        kernel,
        kernel[0, 0] * identity_flavor_matrix(),
        rtol=1e-14,
        atol=0.0,
    )
    values = [
        differential_cross_section_nn(
            RESPONSE,
            ER_keV=ER_KEV,
            Enu_MeV=E_NU_MEV,
            rho=rho,
            particle_kind="nu",
            include_sm=True,
            sin2thetaW=SIN2THETAW,
        ).dsigma_cm2_per_keV
        for rho in densities
    ]

    np.testing.assert_allclose(values, values[0], rtol=1e-13, atol=0.0)
    assert values[0] > 0.0


def test_sm_plus_np_uses_matrix_addition_before_kernel_evaluation():
    np_coefficient = _flavor_changing_coefficient()
    actual = differential_flavor_kernel_nn(
        RESPONSE,
        ER_keV=ER_KEV,
        Enu_MeV=E_NU_MEV,
        wc_triplets={(6, 1, "u"): np_coefficient},
        include_sm=True,
        sin2thetaW=SIN2THETAW,
        basis="np",
    ).kernel_cm2_per_keV

    total_left = _sm_left_dim6(True, SIN2THETAW)
    total_left[(6, 1, "u")] = (
        total_left[(6, 1, "u")] + np_coefficient
    )
    expected = dsigma_dER_flavor_kernel_li2026_cm2_per_GeV(
        RESPONSE,
        E_nu_GeV=E_NU_MEV * 1.0e-3,
        ER_keV=ER_KEV,
        left_hat=total_left,
        basis="np",
    )

    np.testing.assert_allclose(actual, 1.0e-6 * expected, rtol=1e-14, atol=0.0)
    assert abs(actual[1, 2]) > 0.0


def test_density_api_contracts_each_energy_kernel_and_preserves_array_shape():
    rho = _random_density_matrix()
    energies = np.array([0.0, E_NU_MEV, 6.0])
    flavor_result = differential_flavor_kernel_nn(
        RESPONSE,
        ER_keV=ER_KEV,
        Enu_MeV=energies,
        include_sm=True,
        sin2thetaW=SIN2THETAW,
    )
    scalar_result = differential_cross_section_nn(
        RESPONSE,
        ER_keV=ER_KEV,
        Enu_MeV=energies,
        rho=rho,
        particle_kind="nu",
        include_sm=True,
        sin2thetaW=SIN2THETAW,
    )
    expected = np.asarray(
        [
            contract_density_kernel(rho, kernel)
            for kernel in flavor_result.kernel_cm2_per_keV
        ]
    )

    assert scalar_result.dsigma_cm2_per_keV.shape == energies.shape
    np.testing.assert_allclose(
        scalar_result.dsigma_cm2_per_keV,
        expected,
        rtol=1e-14,
        atol=0.0,
    )
    assert math.isclose(
        scalar_result.aas.total.real,
        contract_density_kernel(rho, flavor_result.amplitude.kernel),
        rel_tol=1e-14,
        abs_tol=0.0,
    )


def test_scalar_differential_api_requires_explicit_valid_rho():
    with pytest.raises(TypeError, match="rho"):
        differential_cross_section_nn(
            RESPONSE,
            ER_keV=ER_KEV,
            Enu_MeV=E_NU_MEV,
            include_sm=True,
        )

    with pytest.raises(ValueError, match="positive semidefinite"):
        differential_cross_section_nn(
            RESPONSE,
            ER_keV=ER_KEV,
            Enu_MeV=E_NU_MEV,
            rho=np.diag([0.6, 0.6, -0.2]),
            particle_kind="nu",
            include_sm=True,
        )


def test_differential_kernel_rejects_scalar_np_without_silent_promotion():
    with pytest.raises(ValueError, match="shape"):
        differential_flavor_kernel_nn(
            RESPONSE,
            ER_keV=ER_KEV,
            Enu_MeV=E_NU_MEV,
            wc_triplets={(6, 1, "u"): 1.0e-6},
        )
