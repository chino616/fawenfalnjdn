import numpy as np
import pytest

from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import slow_counts_csi2017
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import slow_counts_csi2021
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import _sm_left_dim6
from cevns_pyeft.theory.li2026.cross_section import (
    dsigma_dER_flavor_kernel_li2026_cm2_per_GeV,
    dsigma_dER_for_density_li2026_cm2_per_GeV,
    dsigma_dER_li2026_cm2_per_GeV,
)
from cevns_pyeft.theory.li2026.flavor import (
    flavor_projector,
    identity_flavor_matrix,
    zero_flavor_matrix,
)


RESPONSE = ResponseDB("data/responses/responses_all.json").get("Cs133")
RESPONSES_JSON = "data/responses/responses_all.json"
E_NU_GEV = 0.03
ER_KEV = 5.0
RHO_E = flavor_projector("e")


def _electron_only(value):
    matrix = zero_flavor_matrix()
    matrix[0, 0] = value
    return matrix


def _sm_universal_left():
    return {
        key: value * identity_flavor_matrix()
        for key, value in _sm_left_dim6(True, 0.23873).items()
    }


@pytest.mark.parametrize(
    "label,left_hat,universal",
    [
        ("SM", _sm_universal_left(), True),
        ("single_C6u1", {(6, 1, "u"): _electron_only(1.0e-6)}, False),
        ("single_C6d1", {(6, 1, "d"): _electron_only(-7.0e-7)}, False),
        ("single_d7_LNC", {(7, 1, "u"): _electron_only(2.0e-7)}, False),
        ("single_d8_LNC", {(8, 1, "d"): _electron_only(-1.0e-8)}, False),
        (
            "complex_point",
            {
                (6, 1, "u"): _electron_only(1.0e-6 + 2.0e-7j),
                (7, 1, "d"): _electron_only(-3.0e-7 + 1.0e-7j),
                (8, 1, "u"): _electron_only(2.0e-8 - 5.0e-9j),
            },
            False,
        ),
    ],
)
def test_non_conus_legacy_scalar_points_match_electron_density_contraction(
    label,
    left_hat,
    universal,
):
    """Phase F9: old scalar semantics are electron-only matrices plus rho_e."""

    kernel = dsigma_dER_flavor_kernel_li2026_cm2_per_GeV(
        RESPONSE,
        E_nu_GeV=E_NU_GEV,
        ER_keV=ER_KEV,
        left_hat=left_hat,
        basis="np",
    )
    density_result = dsigma_dER_for_density_li2026_cm2_per_GeV(
        RESPONSE,
        E_nu_GeV=E_NU_GEV,
        ER_keV=ER_KEV,
        left_hat=left_hat,
        rho=RHO_E,
        basis="np",
    )
    with pytest.warns(DeprecationWarning, match="deprecated"):
        legacy_name_result = dsigma_dER_li2026_cm2_per_GeV(
            RESPONSE,
            E_nu_GeV=E_NU_GEV,
            ER_keV=ER_KEV,
            left_hat=left_hat,
            rho=RHO_E,
            basis="np",
        )

    assert label
    assert density_result == pytest.approx(float(kernel[0, 0].real), rel=1.0e-14)
    assert legacy_name_result == pytest.approx(density_result, rel=1.0e-14)
    if universal:
        np.testing.assert_allclose(
            kernel,
            kernel[0, 0] * identity_flavor_matrix(),
            rtol=1.0e-14,
            atol=0.0,
        )
    else:
        expected = zero_flavor_matrix()
        expected[0, 0] = kernel[0, 0]
        np.testing.assert_allclose(kernel, expected, rtol=1.0e-14, atol=0.0)


@pytest.mark.parametrize(
    "slow_counts,settings",
    [
        (slow_counts_csi2017, {"n_enu": 6}),
        (slow_counts_csi2021, {"n_er": 3, "n_enu": 6, "n_pe_bin": 3, "pe_step": 3.0}),
    ],
)
def test_non_conus_legacy_scalar_counts_use_source_flavor_density(
    slow_counts,
    settings,
):
    """Counts-level legacy scalar semantics: electron-only Wilson plus source rho."""

    baseline = slow_counts(RESPONSES_JSON, include_sm=True, **settings)["counts_per_bin"]
    shifted = slow_counts(
        RESPONSES_JSON,
        wc_triplets={(6, 1, "u"): _electron_only(1.0e-6)},
        include_sm=True,
        **settings,
    )["counts_per_bin"]

    np.testing.assert_allclose(shifted["mu"], baseline["mu"], rtol=1.0e-13, atol=1.0e-12)
    np.testing.assert_allclose(shifted["mub"], baseline["mub"], rtol=1.0e-13, atol=1.0e-12)
    assert np.max(np.abs(shifted["e"] - baseline["e"])) > 1.0e-10
    np.testing.assert_allclose(
        shifted["total"] - baseline["total"],
        shifted["e"] - baseline["e"],
        rtol=1.0e-13,
        atol=1.0e-12,
    )
