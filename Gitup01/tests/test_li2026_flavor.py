import numpy as np
import pytest

from cevns_pyeft.theory.li2026.flavor import (
    FLAVOR_ORDER,
    N_FLAVOR,
    as_flavor_matrix,
    contract_density_kernel,
    dagger,
    flavor_projector,
    identity_flavor_matrix,
    validate_density_matrix,
    zero_flavor_matrix,
)


def test_canonical_flavor_order_and_constructors():
    assert FLAVOR_ORDER == ("e", "mu", "tau")
    assert N_FLAVOR == 3
    assert zero_flavor_matrix().shape == (3, 3)
    assert zero_flavor_matrix().dtype == np.complex128
    np.testing.assert_array_equal(identity_flavor_matrix(), np.eye(3))


@pytest.mark.parametrize("flavor,index", [("e", 0), ("mu", 1), ("tau", 2)])
def test_flavor_projector(flavor, index):
    expected = np.zeros((3, 3), dtype=complex)
    expected[index, index] = 1.0
    np.testing.assert_array_equal(flavor_projector(flavor), expected)


def test_flavor_projector_rejects_unknown_flavor():
    with pytest.raises(ValueError, match="Unknown neutrino flavor"):
        flavor_projector("x")


def test_as_flavor_matrix_validates_shape_and_finiteness():
    matrix = as_flavor_matrix(np.eye(3))
    assert matrix.dtype == np.complex128

    with pytest.raises(ValueError, match=r"shape \(3,3\)"):
        as_flavor_matrix(1.0)
    with pytest.raises(ValueError, match="non-finite real"):
        as_flavor_matrix(np.diag([np.inf, 0.0, 0.0]))
    with pytest.raises(ValueError, match="non-finite imaginary"):
        bad = np.eye(3, dtype=complex)
        bad[0, 1] = complex(0.0, np.inf)
        as_flavor_matrix(bad)


def test_dagger_uses_hermitian_conjugate():
    matrix = np.arange(9).reshape(3, 3) + 1j * np.eye(3)
    np.testing.assert_array_equal(dagger(matrix), matrix.conj().T)


def test_validate_density_matrix_accepts_mixed_state():
    rho = np.diag([0.2, 0.3, 0.5]).astype(complex)
    np.testing.assert_array_equal(validate_density_matrix(rho), rho)


@pytest.mark.parametrize(
    "rho,message",
    [
        (np.array([[1, 1, 0], [0, 0, 0], [0, 0, 0]], dtype=complex), "Hermitian"),
        (np.eye(3, dtype=complex), r"Tr\(rho\) != 1"),
        (np.diag([1.1, -0.1, 0.0]).astype(complex), "positive semidefinite"),
    ],
)
def test_validate_density_matrix_rejects_invalid_states(rho, message):
    with pytest.raises(ValueError, match=message):
        validate_density_matrix(rho)


def test_density_kernel_contraction_uses_trace_rho_kernel_convention():
    rho = flavor_projector("mu")
    coefficient = np.array(
        [
            [1.0, 0.5 + 0.2j, 0.0],
            [0.0, 2.0, 0.3j],
            [0.0, 0.0, 1.0],
        ],
        dtype=complex,
    )
    kernel = coefficient.conj().T @ coefficient

    assert contract_density_kernel(rho, kernel) == pytest.approx(
        kernel[1, 1].real
    )


def test_density_kernel_contraction_rejects_nonphysical_kernel():
    with pytest.raises(ValueError, match="not Hermitian"):
        contract_density_kernel(flavor_projector("e"), 1j * np.eye(3))
