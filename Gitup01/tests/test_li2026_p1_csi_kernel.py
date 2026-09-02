from __future__ import annotations

import numpy as np
import pytest

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import (
    _sm_left_dim6,
)
from cevns_pyeft.theory.kinematics import two_body_recoil_max_GeV
from cevns_pyeft.theory.li2026.cross_section import (
    dsigma_dER_flavor_kernel_li2026_cm2_per_GeV,
)
from cevns_pyeft.theory.li2026.flavor import (
    contract_density_kernel,
    contract_density_kernel_grid,
    flavor_projector,
    validate_flavor_kernel,
)


RESPONSE_DB = ResponseDB("data/responses/responses_all.json")
KERNEL_RTOL = 1.0e-10


def _random_density_matrix(rng: np.random.Generator) -> np.ndarray:
    raw = rng.standard_normal((3, 3)) + 1j * rng.standard_normal((3, 3))
    rho = raw @ raw.conj().T
    return rho / float(np.trace(rho).real)


def _random_lnc_left_hat(rng: np.random.Generator):
    left_hat = _sm_left_dim6(True, 0.23873)
    up = 2.0e-6 * (
        rng.standard_normal((3, 3)) + 1j * rng.standard_normal((3, 3))
    )
    down = 1.0e-6 * (
        rng.standard_normal((3, 3)) + 1j * rng.standard_normal((3, 3))
    )
    left_hat[(6, 1, "u")] = left_hat[(6, 1, "u")] + up
    left_hat[(6, 2, "d")] = left_hat[(6, 2, "d")] + down
    return left_hat


def test_p1_tiny_scale_psd_kernel_passes_without_order_one_floor():
    coefficient = 1.0e-20 * np.array(
        [
            [1.0 + 0.2j, -0.3j, 0.4],
            [0.1, 0.7 - 0.1j, -0.2j],
            [0.3j, 0.2, 0.5 + 0.4j],
        ],
        dtype=np.complex128,
    )
    kernel = coefficient.conj().T @ coefficient

    validated = validate_flavor_kernel(
        kernel,
        rtol=KERNEL_RTOL,
        atol=0.0,
        name="tiny kernel",
    )

    np.testing.assert_array_equal(validated, kernel)
    assert contract_density_kernel(
        flavor_projector("mu"),
        kernel,
        kernel_rtol=KERNEL_RTOL,
        kernel_atol=0.0,
    ) > 0.0


def test_p1_tiny_scale_nonhermitian_kernel_is_rejected():
    kernel = np.diag([1.0e-40, 0.5e-40, 0.0]).astype(np.complex128)
    kernel[0, 1] = 0.25e-40j

    with pytest.raises(ValueError, match="not Hermitian"):
        validate_flavor_kernel(
            kernel,
            rtol=KERNEL_RTOL,
            atol=0.0,
            name="tiny non-Hermitian kernel",
        )


def test_p1_tiny_scale_negative_eigenvalue_is_rejected():
    kernel = np.diag([1.0e-40, -1.0e-41, 0.0]).astype(np.complex128)

    with pytest.raises(ValueError, match="positive semidefinite"):
        validate_flavor_kernel(
            kernel,
            rtol=KERNEL_RTOL,
            atol=0.0,
            name="tiny indefinite kernel",
        )


def test_p1_roundoff_negative_contracts_to_zero_but_clear_negative_raises():
    rho = flavor_projector("e")
    roundoff_kernel = np.diag(
        [-1.0e-52, 1.0e-40, 0.5e-40]
    ).astype(np.complex128)

    validate_flavor_kernel(
        roundoff_kernel,
        rtol=KERNEL_RTOL,
        atol=0.0,
    )
    assert contract_density_kernel(
        rho,
        roundoff_kernel,
        kernel_rtol=KERNEL_RTOL,
        kernel_atol=0.0,
    ) == 0.0
    np.testing.assert_array_equal(
        contract_density_kernel_grid(
            rho,
            np.stack([roundoff_kernel, np.zeros((3, 3))]),
            kernel_rtol=KERNEL_RTOL,
            kernel_atol=0.0,
        ),
        np.zeros(2),
    )

    clearly_negative = np.diag(
        [-1.0e-41, 1.0e-40, 0.5e-40]
    ).astype(np.complex128)
    with pytest.raises(ValueError, match="positive semidefinite"):
        contract_density_kernel_grid(
            rho,
            np.stack([roundoff_kernel, clearly_negative]),
            kernel_rtol=KERNEL_RTOL,
            kernel_atol=0.0,
        )


@pytest.mark.parametrize(
    "response_key,seed",
    [
        pytest.param("Cs133", 133, id="Cs-133"),
        pytest.param("I", 127, id="I-127"),
    ],
)
def test_p1_csi_random_lnc_kernels_are_hermitian_psd_and_nonnegative(
    response_key,
    seed,
):
    response = RESPONSE_DB.get(response_key)
    rng = np.random.default_rng(seed)
    left_hat = _random_lnc_left_hat(rng)
    densities = [
        flavor_projector("e"),
        flavor_projector("mu"),
        flavor_projector("tau"),
        _random_density_matrix(rng),
        _random_density_matrix(rng),
    ]
    mass_GeV = float(response.get_basic("A")) * c.AMU_GEV

    for energy_GeV in (0.010, 0.030, 0.050):
        endpoint_GeV = two_body_recoil_max_GeV(energy_GeV, mass_GeV)
        for recoil_fraction in (0.0, 0.25, 0.8, 1.0):
            kernel = dsigma_dER_flavor_kernel_li2026_cm2_per_GeV(
                response,
                E_nu_GeV=energy_GeV,
                ER_keV=recoil_fraction * endpoint_GeV / c.keV,
                left_hat=left_hat,
                basis="np",
            )
            validate_flavor_kernel(
                kernel,
                rtol=KERNEL_RTOL,
                atol=0.0,
                name=f"{response_key} cross-section kernel",
            )

            scale = float(np.linalg.norm(kernel, ord="fro"))
            residual = float(
                np.linalg.norm(kernel - kernel.conj().T, ord="fro")
            )
            assert residual <= KERNEL_RTOL * scale
            eigenvalues = np.linalg.eigvalsh(
                0.5 * (kernel + kernel.conj().T)
            )
            spectral_scale = float(np.max(np.abs(eigenvalues)))
            assert eigenvalues.min() >= -KERNEL_RTOL * spectral_scale

            for rho in densities:
                assert contract_density_kernel(
                    rho,
                    kernel,
                    kernel_rtol=KERNEL_RTOL,
                    kernel_atol=0.0,
                ) >= 0.0
