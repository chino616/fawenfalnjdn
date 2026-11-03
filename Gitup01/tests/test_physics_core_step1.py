from __future__ import annotations

import math

import numpy as np
import pytest

from cevns_pyeft.core.interaction_point import evaluate_li2026_point
from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.sources.state import pure_flavor_state
from cevns_pyeft.theory.kinematics import two_body_recoil_max_GeV


RESPONSE = ResponseDB("data/responses/responses_all.json").get("Cs133")


def test_step1_point_contract_freezes_support_units_and_state_label():
    energy = 30.0 * c.MeV
    endpoint_keV = two_body_recoil_max_GeV(
        energy, float(RESPONSE.get_basic("A")) * c.AMU_GEV
    ) / c.keV
    point = evaluate_li2026_point(
        RESPONSE,
        energy_GeV=energy,
        recoil_keV=1.0,
        rho=pure_flavor_state("mu", particle_kind="nu").rho,
        include_sm=True,
    )

    assert point.isotope_id == "Cs133"
    assert point.supported
    assert point.endpoint_keV == pytest.approx(endpoint_keV)
    assert point.kernel_cm2_per_keV.shape == (3, 3)
    assert point.kernel_cm2_per_keV.flags.writeable is False
    assert point.dsigma_cm2_per_keV > 0.0
    assert point.particle_kernel == "legacy_shared_nu_antinu"


def test_step1_outside_support_returns_zero_without_exposure_or_detector_layers():
    energy = 30.0 * c.MeV
    endpoint_keV = two_body_recoil_max_GeV(
        energy, float(RESPONSE.get_basic("A")) * c.AMU_GEV
    ) / c.keV
    point = evaluate_li2026_point(
        RESPONSE,
        energy_GeV=energy,
        recoil_keV=1.01 * endpoint_keV,
        rho=pure_flavor_state("mu").rho,
        include_sm=True,
    )

    assert not point.supported
    np.testing.assert_array_equal(point.kernel_cm2_per_keV, 0.0)
    assert point.dsigma_cm2_per_keV == 0.0


def test_step1_rejects_mass_convention_mismatch_and_invalid_state():
    with pytest.raises(ValueError, match="target_mass_GeV"):
        evaluate_li2026_point(
            RESPONSE,
            energy_GeV=30.0 * c.MeV,
            recoil_keV=1.0,
            rho=pure_flavor_state("mu").rho,
            target_mass_GeV=1.001 * float(RESPONSE.get_basic("A")) * c.AMU_GEV,
        )

    with pytest.raises(ValueError, match="positive semidefinite"):
        evaluate_li2026_point(
            RESPONSE,
            energy_GeV=30.0 * c.MeV,
            recoil_keV=1.0,
            rho=np.diag([0.6, 0.6, -0.2]),
        )
