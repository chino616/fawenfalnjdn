import math

import numpy as np
import pytest

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import _sm_left_dim6
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.cross_section import (
    INVGEV_TO_CM,
    dsigma_dER_flavor_kernel_li2026_cm2_per_GeV,
    dsigma_dER_for_density_li2026_cm2_per_GeV,
    dsigma_dER_li2026_cm2_per_GeV,
)
from cevns_pyeft.theory.li2026.flavor import (
    contract_density_kernel,
    flavor_projector,
    identity_flavor_matrix,
    zero_flavor_matrix,
)


RESPONSE = ResponseDB("data/responses/responses_all.json").get("Ge73")
E_NU_GEV = 0.005
ER_KEV = 0.5


def _sm_universal_left():
    return {
        key: value * identity_flavor_matrix()
        for key, value in _sm_left_dim6(True, 0.23873).items()
    }


def _flavor_changing_left():
    coefficient = zero_flavor_matrix()
    coefficient[0, 1] = 1.0e-6 + 2.0e-7j
    coefficient[0, 2] = -4.0e-7 + 1.0e-7j
    return {(6, 1, "u"): coefficient}


def _kernel(left_hat=None, *, basis="np"):
    return dsigma_dER_flavor_kernel_li2026_cm2_per_GeV(
        RESPONSE,
        E_nu_GeV=E_NU_GEV,
        ER_keV=ER_KEV,
        left_hat=_sm_universal_left() if left_hat is None else left_hat,
        basis=basis,
    )


def test_cross_section_kernel_has_flavor_shape_and_expected_units_prefactor():
    amplitude = flavor_kernel_onebody_li2026(
        RESPONSE,
        E_nu_GeV=E_NU_GEV,
        ER_keV=ER_KEV,
        left_hat=_sm_universal_left(),
        basis="np",
    ).kernel
    kernel = _kernel()

    mA = float(RESPONSE.get_basic("A")) * float(c.AMU_GEV)
    expected_scale = (
        mA
        / (8.0 * math.pi * E_NU_GEV**2)
        * 1e-6
        * INVGEV_TO_CM**2
    )

    assert kernel.shape == (3, 3)
    assert np.issubdtype(kernel.dtype, np.complexfloating)
    np.testing.assert_allclose(kernel, amplitude * expected_scale, rtol=1e-14)


def test_sm_cross_section_kernel_is_hermitian_psd_and_flavor_universal():
    kernel = _kernel()

    np.testing.assert_allclose(kernel, kernel.conj().T)
    np.testing.assert_allclose(
        kernel,
        kernel[0, 0] * identity_flavor_matrix(),
    )
    eigenvalues = np.linalg.eigvalsh(kernel)
    assert eigenvalues.min() >= -1e-12 * eigenvalues.max()
    assert eigenvalues.max() > 0.0


def test_sm_density_cross_sections_are_equal_for_all_pure_flavors():
    values = [
        dsigma_dER_for_density_li2026_cm2_per_GeV(
            RESPONSE,
            E_nu_GeV=E_NU_GEV,
            ER_keV=ER_KEV,
            left_hat=_sm_universal_left(),
            rho=flavor_projector(flavor),
            basis="np",
        )
        for flavor in ("e", "mu", "tau")
    ]

    np.testing.assert_allclose(values, values[0])
    assert values[0] > 0.0


def test_density_api_is_exact_trace_rho_kernel_contraction():
    rho = np.array(
        [
            [0.5, 0.1j, 0.0],
            [-0.1j, 0.3, 0.0],
            [0.0, 0.0, 0.2],
        ],
        dtype=complex,
    )
    kernel = _kernel(_flavor_changing_left(), basis="iso")

    actual = dsigma_dER_for_density_li2026_cm2_per_GeV(
        RESPONSE,
        E_nu_GeV=E_NU_GEV,
        ER_keV=ER_KEV,
        left_hat=_flavor_changing_left(),
        rho=rho,
        basis="iso",
    )

    assert actual == pytest.approx(contract_density_kernel(rho, kernel))


@pytest.mark.parametrize(
    "rho,message",
    [
        (np.eye(2), "shape"),
        (
            np.array(
                [[0.5, 0.2, 0.0], [0.0, 0.5, 0.0], [0.0, 0.0, 0.0]],
                dtype=complex,
            ),
            "Hermitian",
        ),
        (np.diag([0.6, 0.6, -0.2]), "positive semidefinite"),
    ],
)
def test_density_api_rejects_invalid_density_matrices(rho, message):
    with pytest.raises(ValueError, match=message):
        dsigma_dER_for_density_li2026_cm2_per_GeV(
            RESPONSE,
            E_nu_GeV=E_NU_GEV,
            ER_keV=ER_KEV,
            left_hat=_sm_universal_left(),
            rho=rho,
            basis="np",
        )


def test_flavor_changing_wilson_produces_non_diagonal_hermitian_kernel():
    kernel = _kernel(_flavor_changing_left(), basis="iso")

    np.testing.assert_allclose(kernel, kernel.conj().T)
    assert abs(kernel[1, 2]) > 0.0
    eigenvalues = np.linalg.eigvalsh(kernel)
    assert eigenvalues.min() >= -1e-12 * eigenvalues.max()


def test_scalar_wilson_coefficient_is_not_silently_promoted():
    with pytest.raises(ValueError, match="shape"):
        _kernel({(6, 1, "u"): 1.0e-6})


def test_legacy_scalar_name_requires_rho_and_delegates_with_warning():
    common = {
        "E_nu_GeV": E_NU_GEV,
        "ER_keV": ER_KEV,
        "left_hat": _sm_universal_left(),
        "basis": "np",
    }

    with pytest.raises(TypeError, match="rho"):
        dsigma_dER_li2026_cm2_per_GeV(RESPONSE, **common)

    with pytest.warns(DeprecationWarning, match="deprecated"):
        legacy = dsigma_dER_li2026_cm2_per_GeV(
            RESPONSE,
            rho=flavor_projector("e"),
            **common,
        )
    canonical = dsigma_dER_for_density_li2026_cm2_per_GeV(
        RESPONSE,
        rho=flavor_projector("e"),
        **common,
    )

    assert legacy == pytest.approx(canonical)
