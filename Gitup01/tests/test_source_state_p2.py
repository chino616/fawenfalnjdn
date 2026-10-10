from __future__ import annotations

import math

import numpy as np
import pytest

from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import (
    differential_cross_section_nn,
    differential_flavor_kernel_nn,
)
from cevns_pyeft.sources.state import (
    NeutrinoState,
    coerce_neutrino_state,
    pure_flavor_density,
    pure_flavor_state,
    validate_density_matrices,
)
from cevns_pyeft.theory.li2026.flavor import (
    contract_density_kernel,
    contract_density_kernel_grid,
    contract_density_kernel_grid_reference,
    flavor_projector,
    zero_flavor_matrix,
)


RESPONSE_DB = ResponseDB("data/responses/responses_all.json")
CS133 = RESPONSE_DB.get("Cs133")
I127 = RESPONSE_DB.get("I")
ENERGIES_MEV = np.array([10.0, 30.0, 50.0])
ER_KEV = 0.5


def _random_density_matrix(rng: np.random.Generator) -> np.ndarray:
    raw = rng.standard_normal((3, 3)) + 1j * rng.standard_normal((3, 3))
    rho = raw @ raw.conj().T
    return rho / float(np.trace(rho).real)


def _coherent_density() -> np.ndarray:
    psi = np.array([1.0, 1.0j, 0.0], dtype=np.complex128)
    psi /= np.linalg.norm(psi)
    return np.outer(psi, psi.conj())


def _flavor_changing_coefficient() -> np.ndarray:
    coefficient = zero_flavor_matrix()
    coefficient[0, 1] = 1.0e-6 + 2.0e-7j
    coefficient[0, 2] = -4.0e-7 + 1.0e-7j
    return coefficient


def test_p2_csi_sns_states_keep_particle_identity_outside_flavor_index():
    prompt_mu = pure_flavor_state("mu", particle_kind="nu")
    delayed_e = pure_flavor_state("e", particle_kind="nu")
    delayed_mub = pure_flavor_state("mu", particle_kind="antinu")

    np.testing.assert_array_equal(prompt_mu.rho, flavor_projector("mu"))
    np.testing.assert_array_equal(delayed_e.rho, flavor_projector("e"))
    np.testing.assert_array_equal(delayed_mub.rho, prompt_mu.rho)
    assert prompt_mu.particle_kind == "nu"
    assert delayed_e.particle_kind == "nu"
    assert delayed_mub.particle_kind == "antinu"
    assert not prompt_mu.rho.flags.writeable


def test_p2_constant_density_broadcast_matches_explicit_energy_grid_for_cs133():
    constant_state = pure_flavor_state("e", particle_kind="nu")
    explicit_grid = np.broadcast_to(
        constant_state.rho,
        ENERGIES_MEV.shape + (3, 3),
    ).copy()
    grid_state = NeutrinoState(
        particle_kind="nu",
        rho=explicit_grid,
    )

    from_state = differential_cross_section_nn(
        CS133,
        ER_keV=ER_KEV,
        Enu_MeV=ENERGIES_MEV,
        rho=constant_state,
        include_sm=True,
    )
    from_raw_constant = differential_cross_section_nn(
        CS133,
        ER_keV=ER_KEV,
        Enu_MeV=ENERGIES_MEV,
        rho=pure_flavor_density("e"),
        particle_kind="nu",
        include_sm=True,
    )
    from_grid = differential_cross_section_nn(
        CS133,
        ER_keV=ER_KEV,
        Enu_MeV=ENERGIES_MEV,
        rho=grid_state,
        include_sm=True,
    )

    np.testing.assert_allclose(
        from_state.dsigma_cm2_per_keV,
        from_raw_constant.dsigma_cm2_per_keV,
        rtol=1.0e-14,
        atol=0.0,
    )
    np.testing.assert_allclose(
        from_state.dsigma_cm2_per_keV,
        from_grid.dsigma_cm2_per_keV,
        rtol=1.0e-14,
        atol=0.0,
    )
    assert from_state.particle_kind == "nu"


def test_p2_energy_dependent_density_contracts_each_cs133_kernel():
    rho_grid = np.stack(
        [
            flavor_projector("e"),
            flavor_projector("mu"),
            _coherent_density(),
        ]
    )
    state = NeutrinoState(particle_kind="nu", rho=rho_grid)
    coefficient = _flavor_changing_coefficient()
    flavor_result = differential_flavor_kernel_nn(
        CS133,
        ER_keV=ER_KEV,
        Enu_MeV=ENERGIES_MEV,
        wc_triplets={(6, 1, "u"): coefficient},
        include_sm=True,
    )
    result = differential_cross_section_nn(
        CS133,
        ER_keV=ER_KEV,
        Enu_MeV=ENERGIES_MEV,
        rho=state,
        wc_triplets={(6, 1, "u"): coefficient},
        include_sm=True,
    )
    expected = np.asarray(
        [
            contract_density_kernel(rho, kernel)
            for rho, kernel in zip(
                rho_grid,
                flavor_result.kernel_cm2_per_keV,
            )
        ]
    )

    assert result.dsigma_cm2_per_keV.shape == ENERGIES_MEV.shape
    np.testing.assert_allclose(
        result.dsigma_cm2_per_keV,
        expected,
        rtol=1.0e-14,
        atol=0.0,
    )
    assert flavor_result.amplitude_index == (2,)
    assert math.isclose(
        result.aas.total.real,
        contract_density_kernel(
            rho_grid[-1],
            flavor_result.amplitude.kernel,
        ),
        rel_tol=1.0e-14,
        abs_tol=0.0,
    )


def test_p2_public_density_kernel_grid_matches_reference():
    rng = np.random.default_rng(2026)
    kernels = []
    for _ in range(5):
        raw = rng.standard_normal((3, 3)) + 1j * rng.standard_normal((3, 3))
        kernels.append(raw.conj().T @ raw)
    kernel_grid = np.asarray(kernels, dtype=np.complex128) * 1.0e-40
    rho_constant = flavor_projector("mu")
    rho_grid = np.stack([_random_density_matrix(rng) for _ in range(5)])

    np.testing.assert_allclose(
        contract_density_kernel_grid(rho_constant, kernel_grid),
        contract_density_kernel_grid_reference(rho_constant, kernel_grid),
        rtol=1.0e-13,
        atol=0.0,
    )
    np.testing.assert_allclose(
        contract_density_kernel_grid(rho_grid, kernel_grid),
        contract_density_kernel_grid_reference(rho_grid, kernel_grid),
        rtol=1.0e-13,
        atol=0.0,
    )
    with pytest.raises(ValueError, match="rho energy shape"):
        contract_density_kernel_grid(rho_grid[:-1], kernel_grid)


def test_p2_snudd_style_rho_grid_preserves_sm_flavor_universality_for_i127():
    rng = np.random.default_rng(127)
    rho_grid = np.stack(
        [_random_density_matrix(rng) for _ in ENERGIES_MEV]
    )
    energy_dependent = differential_cross_section_nn(
        I127,
        ER_keV=ER_KEV,
        Enu_MeV=ENERGIES_MEV,
        rho=NeutrinoState("nu", rho_grid),
        include_sm=True,
    )
    pure_e = differential_cross_section_nn(
        I127,
        ER_keV=ER_KEV,
        Enu_MeV=ENERGIES_MEV,
        rho=pure_flavor_state("e"),
        include_sm=True,
    )

    np.testing.assert_allclose(
        energy_dependent.dsigma_cm2_per_keV,
        pure_e.dsigma_cm2_per_keV,
        rtol=1.0e-13,
        atol=0.0,
    )


def test_p2_density_grid_shape_and_each_energy_state_are_strict():
    wrong_shape = NeutrinoState(
        "nu",
        np.stack(
            [
                flavor_projector("e"),
                flavor_projector("mu"),
            ]
        ),
    )
    with pytest.raises(ValueError, match="energy shape"):
        differential_cross_section_nn(
            CS133,
            ER_keV=ER_KEV,
            Enu_MeV=ENERGIES_MEV,
            rho=wrong_shape,
            include_sm=True,
        )

    invalid_grid = np.stack(
        [
            flavor_projector("e"),
            np.diag([0.6, 0.6, -0.2]),
            flavor_projector("tau"),
        ]
    )
    with pytest.raises(ValueError, match=r"rho\(1,\).*positive semidefinite"):
        NeutrinoState("nu", invalid_grid)

    with pytest.raises(ValueError, match="shape"):
        validate_density_matrices(
            np.zeros((3, 3, 2)),
            energy_shape=ENERGIES_MEV.shape,
        )


def test_p2_raw_density_requires_particle_and_state_rejects_contradiction():
    with pytest.raises(ValueError, match="particle_kind is required"):
        coerce_neutrino_state(flavor_projector("e"))

    state = pure_flavor_state("mu", particle_kind="nu")
    with pytest.raises(ValueError, match="contradicts"):
        differential_cross_section_nn(
            CS133,
            ER_keV=ER_KEV,
            Enu_MeV=30.0,
            rho=state,
            particle_kind="antinu",
            include_sm=True,
        )

    with pytest.raises(ValueError, match="particle_kind"):
        NeutrinoState("nubar", flavor_projector("e"))


def test_p2_antinu_label_is_preserved_without_silent_kernel_physics_change():
    coefficient = _flavor_changing_coefficient()
    nu_state = pure_flavor_state("mu", particle_kind="nu")
    antinu_state = pure_flavor_state("mu", particle_kind="antinu")

    nu_result = differential_cross_section_nn(
        CS133,
        ER_keV=ER_KEV,
        Enu_MeV=30.0,
        rho=nu_state,
        wc_triplets={(6, 1, "u"): coefficient},
        include_sm=True,
    )
    antinu_result = differential_cross_section_nn(
        CS133,
        ER_keV=ER_KEV,
        Enu_MeV=30.0,
        rho=antinu_state,
        wc_triplets={(6, 1, "u"): coefficient},
        include_sm=True,
    )

    assert nu_result.particle_kind == "nu"
    assert antinu_result.particle_kind == "antinu"
    assert nu_result.dsigma_cm2_per_keV == pytest.approx(
        antinu_result.dsigma_cm2_per_keV,
        rel=0.0,
        abs=0.0,
    )
