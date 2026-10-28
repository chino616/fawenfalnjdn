import math

import numpy as np
import pytest

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.foundation.units import cm2_per_GeV_to_cm2_per_keV
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import (
    differential_cross_section_nn,
    differential_flavor_kernel_nn,
)
from cevns_pyeft.sources.state import pure_flavor_state
from cevns_pyeft.theory.kinematics import (
    is_two_body_recoil_allowed,
    minimum_neutrino_energy_GeV,
    two_body_recoil_max_GeV,
)


RESPONSE = ResponseDB("data/responses/responses_all.json").get_by_symbol_A(
    "Ge", 73
)
MASS_GEV = 73.0 * c.AMU_GEV
STATE = pure_flavor_state("e", particle_kind="antinu")


@pytest.mark.parametrize(
    "energy_mev, expected_tmax_kev",
    [(5.0, 0.7351960600988574), (10.0, 2.9403518933699684)],
)
def test_exact_endpoint_and_inverse_relation(energy_mev, expected_tmax_kev):
    energy_gev = energy_mev * c.MeV
    endpoint_gev = two_body_recoil_max_GeV(energy_gev, MASS_GEV)

    assert endpoint_gev / c.keV == pytest.approx(expected_tmax_kev)
    assert minimum_neutrino_energy_GeV(endpoint_gev, MASS_GEV) == pytest.approx(
        energy_gev, rel=1.0e-14
    )
    assert is_two_body_recoil_allowed(energy_gev, endpoint_gev, MASS_GEV)
    assert not is_two_body_recoil_allowed(
        energy_gev, endpoint_gev * (1.0 + 1.0e-10), MASS_GEV
    )


def test_zero_recoil_and_invalid_inputs_are_distinct():
    assert minimum_neutrino_energy_GeV(0.0, MASS_GEV) == 0.0
    assert is_two_body_recoil_allowed(5.0 * c.MeV, 0.0, MASS_GEV)

    with pytest.raises(ValueError, match="positive and finite"):
        two_body_recoil_max_GeV(0.0, MASS_GEV)
    with pytest.raises(ValueError, match="non-negative and finite"):
        minimum_neutrino_energy_GeV(-c.keV, MASS_GEV)


def test_rate_is_positive_inside_support_and_zero_above_endpoint():
    endpoint_kev = two_body_recoil_max_GeV(5.0 * c.MeV, MASS_GEV) / c.keV
    inside = differential_cross_section_nn(
        RESPONSE,
        ER_keV=endpoint_kev * (1.0 - 1.0e-10),
        Enu_MeV=5.0,
        rho=STATE,
        include_sm=True,
        sin2thetaW=0.23857,
    )
    outside = differential_cross_section_nn(
        RESPONSE,
        ER_keV=endpoint_kev * (1.0 + 1.0e-10),
        Enu_MeV=5.0,
        rho=STATE,
        include_sm=True,
        sin2thetaW=0.23857,
    )

    assert inside.particle_kind == "antinu"
    assert inside.dsigma_cm2_per_keV > 0.0
    assert outside.dsigma_cm2_per_keV == 0.0


def test_zero_energy_grid_node_returns_zero_kernel_with_expected_axes():
    kernel = differential_flavor_kernel_nn(
        RESPONSE,
        ER_keV=0.5,
        Enu_MeV=np.array([0.0, 5.0]),
        include_sm=True,
        sin2thetaW=0.23857,
    ).kernel_cm2_per_keV

    assert kernel.shape == (2, 3, 3)
    np.testing.assert_array_equal(kernel[0], np.zeros((3, 3), dtype=complex))
    assert np.all(np.isfinite(kernel[1]))


def test_differential_unit_conversion_is_owned_once():
    assert c.MeV == pytest.approx(1.0e-3)
    assert c.keV == pytest.approx(1.0e-6)
    assert cm2_per_GeV_to_cm2_per_keV(1.0) == pytest.approx(1.0e-6)

    endpoint_gev = two_body_recoil_max_GeV(5.0 * c.MeV, MASS_GEV)
    assert math.isclose(
        minimum_neutrino_energy_GeV(endpoint_gev, MASS_GEV) / c.MeV,
        5.0,
        rel_tol=1.0e-14,
    )
