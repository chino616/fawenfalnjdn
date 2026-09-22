import os
from pathlib import Path
import sys

import numpy as np
import pytest

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.propagation import (
    PropagationState,
    propagation_state_from_density,
    validate_energy_grid_GeV,
    wilson_np_to_vector_nsi,
)
from cevns_pyeft.propagation.backends.snudd import SNuDDSolarDensityBackend
from cevns_pyeft.theory.li2026.flavor import flavor_projector, zero_flavor_matrix


def _real_snudd_density_calculator():
    checkout = Path(
        os.environ.get("CEVNS_PYEFT_SNUDD_CHECKOUT", r"F:\Work\SNuDD-main\SNuDD-main")
    )
    if "snudd" not in sys.modules:
        if checkout.joinpath("snudd", "__init__.py").is_file():
            sys.path.insert(0, str(checkout))

    try:
        from snudd import models
        from snudd.nsi.nsi_probabilities import DensityMatrixCalculator
    except ModuleNotFoundError as exc:
        pytest.skip(f"real SNuDD package or checkout is not available: {exc}")

    return DensityMatrixCalculator(models.SM(), adiabatic_check=False)


def test_propagation_state_validates_energy_shape_and_density_grid():
    energy = np.array([0.001, 0.01, 0.02])
    rho = np.stack([flavor_projector("e"), flavor_projector("mu"), flavor_projector("tau")])

    state = propagation_state_from_density(energy, rho)

    assert isinstance(state, PropagationState)
    np.testing.assert_array_equal(state.energy_GeV, energy)
    np.testing.assert_array_equal(state.rho, rho)
    assert state.basis == ("e", "mu", "tau")
    assert state.unit == "dimensionless"


@pytest.mark.parametrize(
    "energy,message",
    [
        ([[0.001, 0.002]], "one-dimensional"),
        ([0.001, np.inf], "finite"),
        ([0.001, -0.002], "non-negative"),
    ],
)
def test_validate_energy_grid_gev_rejects_invalid_inputs(energy, message):
    with pytest.raises(ValueError, match=message):
        validate_energy_grid_GeV(energy)


def test_propagation_state_rejects_invalid_density_matrices():
    with pytest.raises(ValueError, match=r"Tr\(rho\) != 1"):
        propagation_state_from_density([0.01], np.zeros((1, 3, 3)))

    bad = np.diag([0.6, 0.6, -0.2])
    with pytest.raises(ValueError, match="positive semidefinite"):
        propagation_state_from_density([0.01], bad)


class FakeSnuddCalculator:
    def __init__(self):
        self.calls = []

    def density(self, E_nus, nu):
        self.calls.append((E_nus.copy(), nu))
        return np.broadcast_to(flavor_projector("e"), E_nus.shape + (3, 3))


def test_snudd_backend_uses_gev_energy_and_returns_only_propagation_state():
    calculator = FakeSnuddCalculator()
    backend = SNuDDSolarDensityBackend(calculator)
    energy = np.array([0.002, 0.005])

    state = backend.density(energy, nu="B8")

    np.testing.assert_array_equal(calculator.calls[0][0], energy)
    assert calculator.calls[0][1] == "B8"
    np.testing.assert_array_equal(state.rho, np.broadcast_to(flavor_projector("e"), (2, 3, 3)))
    assert not hasattr(state, "rate")
    assert not hasattr(state, "target")
    assert not hasattr(state, "spectrum")


def test_snudd_backend_rejects_invalid_backend_density():
    class BadCalculator:
        def density(self, E_nus, nu):
            return np.zeros(E_nus.shape + (3, 3))

    backend = SNuDDSolarDensityBackend(BadCalculator())
    with pytest.raises(ValueError, match=r"Tr\(rho\) != 1"):
        backend.density([0.01], nu="pp")


def test_real_snudd_density_calculator_end_to_end_if_available():
    calculator = _real_snudd_density_calculator()
    backend = SNuDDSolarDensityBackend(calculator)
    energy = np.array([0.005, 0.01])

    state = backend.density(energy, nu="8B")
    direct = calculator.density(energy, "8B")

    np.testing.assert_array_equal(state.energy_GeV, energy)
    np.testing.assert_allclose(state.rho, direct, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(
        np.trace(state.rho, axis1=-2, axis2=-1),
        np.ones(energy.shape, dtype=np.complex128),
        rtol=1.0e-12,
        atol=1.0e-12,
    )
    assert np.all(np.linalg.eigvalsh(state.rho) >= -1.0e-12)
    probabilities = np.diagonal(state.rho, axis1=-2, axis2=-1).real
    assert np.all((probabilities >= -1.0e-12) & (probabilities <= 1.0 + 1.0e-12))


def test_wilson_np_to_vector_nsi_uses_only_np_c6q1_matrices():
    c6u1 = zero_flavor_matrix()
    c6d1 = zero_flavor_matrix()
    c6u1[0, 1] = 1.0e-8
    c6d1[1, 0] = -2.0e-8

    nsi = wilson_np_to_vector_nsi(
        wc_triplets={(6, 1, "u"): c6u1, (6, 1, "d"): c6d1},
        wilson_content="np_only",
    )
    prefactor = -1.0 / (np.sqrt(2.0) * float(c.G_F))

    np.testing.assert_allclose(nsi["u"], prefactor * c6u1)
    np.testing.assert_allclose(nsi["d"], prefactor * c6d1)


def test_wilson_np_to_vector_nsi_rejects_sm_plus_np_and_unsupported_coefficients():
    with pytest.raises(ValueError, match="np_only"):
        wilson_np_to_vector_nsi(wilson_content="sm_plus_np")

    unsupported = zero_flavor_matrix()
    unsupported[0, 1] = 1.0e-8
    with pytest.raises(ValueError, match="Unsupported propagation NSI"):
        wilson_np_to_vector_nsi(wc_triplets={(6, 2, "u"): unsupported})
