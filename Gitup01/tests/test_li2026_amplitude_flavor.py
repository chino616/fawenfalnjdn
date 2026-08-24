import numpy as np
import pytest

from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import _sm_left_dim6
from cevns_pyeft.theory.li2026.amplitude import (
    _contract_R_W,
    amplitude_squared_onebody_li2026,
    flavor_kernel_onebody_li2026,
)
from cevns_pyeft.theory.li2026.flavor import (
    contract_density_kernel,
    flavor_projector,
    identity_flavor_matrix,
    zero_flavor_matrix,
)


RESPONSE = ResponseDB("data/responses/responses_all.json").get("Ge73")


def _sm_universal_left():
    return {
        key: value * identity_flavor_matrix()
        for key, value in _sm_left_dim6(True, 0.23873).items()
    }


def _flavor_changing_left():
    lnc = zero_flavor_matrix()
    lnc[0, 1] = 1.0e-6 + 2.0e-7j
    lnc[0, 2] = -4.0e-7 + 1.0e-7j
    lnv = zero_flavor_matrix()
    lnv[0, 1] = 2.0e-7 - 3.0e-7j
    lnv[0, 2] = 5.0e-7j
    return {
        (6, 1, "u"): lnc,
        (7, 3, "u"): lnv,
        (7, 4, "u"): 2.0 * lnv,
    }


def test_contract_r_w_contracts_only_isospin_axes():
    response = np.arange(36, dtype=float).reshape(3, 3, 2, 2).astype(complex)
    nuclear = np.array([[1.0, 2.0], [3.0, 4.0]])

    contracted = _contract_R_W(response, nuclear)

    assert contracted.shape == (3, 3)
    np.testing.assert_array_equal(
        contracted,
        np.einsum("abij,ij->ab", response, nuclear, optimize=True),
    )


@pytest.mark.parametrize(
    "response_shape,nuclear_shape,message",
    [
        ((3, 3, 2), (2, 2), "R must have shape"),
        ((3, 3, 2, 2), (3, 3), "W must have shape"),
    ],
)
def test_contract_r_w_rejects_invalid_shapes(response_shape, nuclear_shape, message):
    with pytest.raises(ValueError, match=message):
        _contract_R_W(np.zeros(response_shape), np.zeros(nuclear_shape))


def test_sm_universal_kernel_is_flavor_universal_and_density_independent():
    result = flavor_kernel_onebody_li2026(
        RESPONSE,
        E_nu_GeV=0.005,
        ER_keV=0.5,
        left_hat=_sm_universal_left(),
        basis="np",
    )

    assert result.kernel.shape == (3, 3)
    assert all(piece.shape == (3, 3) for piece in result.pieces.values())
    np.testing.assert_allclose(result.kernel, result.kernel.conj().T)
    np.testing.assert_allclose(
        result.kernel,
        result.kernel[0, 0] * identity_flavor_matrix(),
    )

    rates = [
        contract_density_kernel(flavor_projector(flavor), result.kernel)
        for flavor in ("e", "mu", "tau")
    ]
    np.testing.assert_allclose(rates, rates[0])
    assert rates[0] > 0.0


def test_physical_flavor_changing_kernel_is_hermitian_and_psd():
    result = flavor_kernel_onebody_li2026(
        RESPONSE,
        E_nu_GeV=0.005,
        ER_keV=0.5,
        left_hat=_flavor_changing_left(),
        basis="iso",
    )

    np.testing.assert_allclose(result.kernel, result.kernel.conj().T)
    assert np.min(np.linalg.eigvalsh(result.kernel)) >= -1.0e-20
    assert abs(result.kernel[1, 2]) > 0.0


def test_legacy_amplitude_name_returns_kernel_with_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="FlavorKernelResult"):
        legacy = amplitude_squared_onebody_li2026(
            RESPONSE,
            E_nu_GeV=0.005,
            ER_keV=0.5,
            left_hat=_sm_universal_left(),
            basis="np",
        )
    canonical = flavor_kernel_onebody_li2026(
        RESPONSE,
        E_nu_GeV=0.005,
        ER_keV=0.5,
        left_hat=_sm_universal_left(),
        basis="np",
    )

    np.testing.assert_array_equal(legacy.kernel, canonical.kernel)
    assert legacy.basis == canonical.basis
