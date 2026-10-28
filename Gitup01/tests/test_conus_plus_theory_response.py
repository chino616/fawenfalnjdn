import numpy as np

from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import differential_cross_section_nn
from cevns_pyeft.sources.state import pure_flavor_state


SIN2_THETA_W = 0.23857
RESPONSE = ResponseDB("data/responses/responses_all.json").get_by_symbol_A(
    "Ge", 73
)


def test_conus_plus_routes_to_ge73_full_nuclear_response():
    assert RESPONSE.name == "Ge73"
    assert RESPONSE.get_basic("A") == 73
    assert RESPONSE.get_basic("Z") == 32
    assert RESPONSE.get_basic("N") == 41
    assert set(RESPONSE.keys()) == {
        "Delta",
        "M",
        "MPhiPP",
        "PhiPP",
        "PhiPT",
        "SigmaP",
        "SigmaPDelta",
        "SigmaPP",
    }


def test_conus_plus_sm_route_is_explicit_and_sigma_p_delta_is_zero():
    common = dict(
        resp=RESPONSE,
        ER_keV=0.5,
        Enu_MeV=5.0,
        rho=pure_flavor_state("e", particle_kind="antinu"),
        sin2thetaW=SIN2_THETA_W,
    )

    without_sm = differential_cross_section_nn(include_sm=False, **common)
    with_sm = differential_cross_section_nn(include_sm=True, **common)

    assert without_sm.dsigma_cm2_per_keV == 0.0
    assert with_sm.dsigma_cm2_per_keV > 0.0
    assert with_sm.particle_kind == "antinu"
    np.testing.assert_array_equal(with_sm.aas.pieces[-1], 0.0 + 0.0j)


def test_conus_plus_antineutrino_label_preserves_current_kernel_approximation():
    common = dict(
        resp=RESPONSE,
        ER_keV=0.5,
        Enu_MeV=5.0,
        include_sm=True,
        sin2thetaW=SIN2_THETA_W,
    )
    antinu = differential_cross_section_nn(
        rho=pure_flavor_state("e", particle_kind="antinu"),
        **common,
    )
    nu = differential_cross_section_nn(
        rho=pure_flavor_state("e", particle_kind="nu"),
        **common,
    )

    assert antinu.particle_kind == "antinu"
    assert nu.particle_kind == "nu"
    np.testing.assert_allclose(
        antinu.dsigma_cm2_per_keV,
        nu.dsigma_cm2_per_keV,
        rtol=0.0,
        atol=0.0,
    )
