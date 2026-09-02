from __future__ import annotations

import numpy as np
import pytest
import json

from cevns_pyeft.kernels.basis import coeff_tensor_from_triplets, coeff_vector_from_triplets, li2026_left_basis
from cevns_pyeft.kernels.builder import _build_ci_units, _kernel_to_diag_pair_templates
from cevns_pyeft.kernels.reconstruction import (
    coefficient_bilinear,
    coefficient_bilinear_reference,
    reconstruct_from_full_kernel,
    reconstruct_from_full_kernel_flavor,
    reconstruct_from_pair_templates_flavor,
    source_densities_for_fast_flavors,
)
from cevns_pyeft.kernels.storage import (
    StaleKernelError,
    load_fastscan_template,
    save_fastscan_template,
    validate_fastscan_template,
)
from cevns_pyeft.theory.li2026.flavor import identity_flavor_matrix, zero_flavor_matrix


def _minimal_kernel_metadata() -> dict[str, object]:
    basis = li2026_left_basis()[:2]
    return {
        "metadata": {
            "dataset": "CsI2021",
            "flavor_schema_version": 1,
            "neutrino_flavor_order": ["e", "mu", "tau"],
            "wilson_flavor_axis": {"row": "final", "column": "initial"},
            "operator_basis_size": 2,
            "coefficient_shape": [2, 3, 3],
            "lnc_lnv_interference": False,
        },
        "basis": basis,
        "targets": ["CsI"],
        "source_flavors": ["mu", "e", "mub"],
        "channels": ["M"],
        "pe_bins": np.array([0.0, 1.0, 3.0]),
        "full_kernel": np.zeros((1, 3, 1, 2, 2, 2), dtype=np.complex128),
        "diag": np.zeros((2, 1, 3, 1, 2), dtype=float),
        "pair_re": np.zeros((1, 1, 3, 1, 2), dtype=float),
        "pair_im": np.zeros((1, 1, 3, 1, 2), dtype=float),
        "pair_index": np.array([[0, 1]], dtype=int),
    }


def test_coeff_tensor_from_triplets_keeps_basis_22_and_flavor_shape():
    basis = li2026_left_basis()
    matrix = zero_flavor_matrix()
    matrix[0, 1] = 2.0 + 0.5j
    coeffs = coeff_tensor_from_triplets(
        basis,
        {(6, 1, "u"): matrix},
        include_sm=False,
    )
    assert coeffs.shape == (22, 3, 3)
    assert coeffs[basis.index(next(be for be in basis if be.triplet == (6, 1, "u"))), 0, 1] == 2.0 + 0.5j

    with pytest.raises(ValueError, match="shape"):
        coeff_tensor_from_triplets(basis, {(6, 1, "u"): 1.0}, include_sm=False)


def test_legacy_scalar_coeff_vector_keeps_sm_identity_path():
    basis = li2026_left_basis()
    coeffs = coeff_vector_from_triplets(basis, {}, include_sm=True)

    assert coeffs.shape == (22,)
    assert np.all(np.isfinite(coeffs.real))
    assert np.all(np.isfinite(coeffs.imag))
    assert np.count_nonzero(coeffs) == 4


def test_coefficient_bilinear_matches_reference_and_orientation():
    coeffs = np.zeros((2, 3, 3), dtype=np.complex128)
    coeffs[0, 0, 1] = 3.0 + 4.0j
    coeffs[1, 0, 0] = 2.0

    rho_mu = np.diag([0.0, 1.0, 0.0]).astype(np.complex128)
    rho_e = np.diag([1.0, 0.0, 0.0]).astype(np.complex128)

    optimized = coefficient_bilinear(coeffs, rho_mu)
    reference = coefficient_bilinear_reference(coeffs, rho_mu)
    np.testing.assert_allclose(optimized, reference, rtol=1.0e-13, atol=0.0)
    assert optimized[0, 0] == pytest.approx(25.0, rel=1.0e-13, abs=0.0)
    assert coefficient_bilinear(coeffs, rho_e)[0, 0] == pytest.approx(0.0, abs=0.0)


def test_fast_builder_operator_templates_satisfy_strict_lnc_and_lnv_validation():
    basis = li2026_left_basis()
    ci = _build_ci_units(
        basis,
        E_nu_GeV=0.03,
        q0_GeV=1.0e-6,
        q2_GeV2=-1.0e-4,
        qabs_GeV=0.01,
        qabs2_GeV2=1.0e-4,
        mA_GeV=120.0,
        c10_mass_mode="quark_mass_resolved",
    )
    assert ci.shape == (22, 15, 2)
    assert np.any(np.abs(ci) > 0.0)


def test_flavor_full_kernel_reduces_to_scalar_for_identity_coefficients():
    rng = np.random.default_rng(123)
    raw = rng.normal(size=(3, 1, 2, 2, 4))
    hermitian = raw.astype(np.complex128)
    hermitian[:, :, 1, 0, :] = hermitian[:, :, 0, 1, :]
    scalar_coeffs = np.array([1.5 - 0.25j, -0.75 + 0.5j])
    flavor_coeffs = np.asarray([value * identity_flavor_matrix() for value in scalar_coeffs])
    rhos = source_densities_for_fast_flavors(["mu", "e", "mub"])

    scalar = reconstruct_from_full_kernel(hermitian, scalar_coeffs)
    flavor = reconstruct_from_full_kernel_flavor(hermitian, flavor_coeffs, rhos)
    np.testing.assert_allclose(flavor, scalar, rtol=1.0e-13, atol=1.0e-13)


def test_flavor_pair_templates_match_full_kernel():
    full = np.zeros((1, 3, 1, 2, 2, 2), dtype=np.complex128)
    full[:, :, :, 0, 0, :] = 1.0
    full[:, :, :, 1, 1, :] = 2.0
    full[:, :, :, 0, 1, :] = 0.25 + 0.75j
    full[:, :, :, 1, 0, :] = 0.25 - 0.75j
    diag, pair_re, pair_im, pair_index = _kernel_to_diag_pair_templates(full)

    coeffs = np.zeros((2, 3, 3), dtype=np.complex128)
    coeffs[0] = identity_flavor_matrix()
    coeffs[1] = 2.0 * identity_flavor_matrix()
    rhos = source_densities_for_fast_flavors(["mu", "e", "mub"])

    from_full = reconstruct_from_full_kernel_flavor(full, coeffs, rhos)
    from_pairs = reconstruct_from_pair_templates_flavor(
        diag=diag,
        pair_re=pair_re,
        pair_im=pair_im,
        pair_index=pair_index,
        coeffs=coeffs,
        source_rhos=rhos,
    )
    np.testing.assert_allclose(from_pairs, np.real(from_full), rtol=1.0e-13, atol=0.0)


def test_fast_template_requires_flavor_schema_version():
    kernel = _minimal_kernel_metadata()
    validate_fastscan_template(kernel)
    stale = dict(kernel)
    stale["metadata"] = dict(kernel["metadata"])
    del stale["metadata"]["flavor_schema_version"]
    with pytest.raises(StaleKernelError):
        validate_fastscan_template(stale)


def test_fast_template_save_load_roundtrip_preserves_flavor_schema(tmp_path):
    kernel = _minimal_kernel_metadata()
    full = np.asarray(kernel["full_kernel"], dtype=np.complex128)
    full[:, :, :, 0, 0, :] = 1.0
    full[:, :, :, 1, 1, :] = 2.0
    full[:, :, :, 0, 1, :] = 0.25 + 0.5j
    full[:, :, :, 1, 0, :] = 0.25 - 0.5j
    kernel["full_kernel"] = full

    path = save_fastscan_template(tmp_path / "kernel.npz", kernel)
    loaded = load_fastscan_template(path)

    assert loaded["metadata"]["flavor_schema_version"] == 1
    assert loaded["metadata"]["coefficient_shape"] == [2, 3, 3]
    assert loaded["metadata"]["wilson_flavor_axis"] == {
        "row": "final",
        "column": "initial",
    }
    np.testing.assert_allclose(loaded["full_kernel"], full)
    np.testing.assert_array_equal(loaded["pe_bins"], kernel["pe_bins"])


def test_fast_template_load_rejects_stale_saved_metadata(tmp_path):
    kernel = _minimal_kernel_metadata()
    path = save_fastscan_template(tmp_path / "kernel.npz", kernel)
    json_path = path.with_suffix(".json")
    metadata = json.loads(json_path.read_text(encoding="utf-8"))
    del metadata["flavor_schema_version"]
    json_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(StaleKernelError):
        load_fastscan_template(path)
