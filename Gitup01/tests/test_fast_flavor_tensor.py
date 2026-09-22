from __future__ import annotations

import numpy as np
import pytest
import json
import runpy
from pathlib import Path

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
    build_fastscan_template,
    StaleKernelError,
    load_fastscan_template,
    reconstruct_saved_kernel,
    save_fastscan_template,
    validate_fastscan_template,
)
from cevns_pyeft.experiments.specs import read_simple_yaml
from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import slow_counts_csi2017
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import slow_counts_csi2021
from cevns_pyeft.theory.li2026.flavor import identity_flavor_matrix, zero_flavor_matrix


RESPONSES_JSON = "data/responses/responses_all.json"
REFERENCE_FAST_GENERATOR = Path("tools/experiment_integration/generate_csi_fast_references.py")
REFERENCE_FAST = {
    "CsI2017": Path("tests/reference_CsI2017/fast_kernel.npz"),
    "CsI2021": Path("tests/reference_CsI2021/fast_kernel.npz"),
}
REFERENCE_SLOW = {
    "CsI2017": Path("tests/reference_CsI2017/slow_reference.npy"),
    "CsI2021": Path("tests/reference_CsI2021/slow_reference.npy"),
}
EXPERIMENT_SPECS = {
    "CsI2017": Path("data/experiments/CsI2017/experiment.yaml"),
    "CsI2021": Path("data/experiments/CsI2021/experiment.yaml"),
}


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


def test_csi_fast_reference_generator_defaults_to_nonwriting_guard():
    namespace = runpy.run_path(str(REFERENCE_FAST_GENERATOR))
    assert namespace["APPROVAL_PHRASE"] == "I approve updating CsI Fast reference kernels"
    assert namespace["FAST_SLOW_RTOL"] == 1.0e-9
    assert namespace["FAST_SLOW_ATOL"] == 2.0e-8
    assert namespace["REFERENCE_PATHS"]["CsI2017"].as_posix().endswith(
        "tests/reference_CsI2017/fast_kernel.npz"
    )
    assert namespace["REFERENCE_PATHS"]["CsI2021"].as_posix().endswith(
        "tests/reference_CsI2021/fast_kernel.npz"
    )

    main = namespace["main"]
    before = {
        str(path): path.exists()
        for path in namespace["REFERENCE_PATHS"].values()
    }
    assert main(["--dataset", "CsI2017", "--no-compute"]) == 0
    assert main(["--dataset", "CsI2021", "--no-compute"]) == 0
    after = {
        str(path): path.exists()
        for path in namespace["REFERENCE_PATHS"].values()
    }
    assert after == before


def test_csi_fast_reference_generator_rejects_write_without_exact_acknowledgement():
    namespace = runpy.run_path(str(REFERENCE_FAST_GENERATOR))
    main = namespace["main"]
    before = {
        str(path): path.exists()
        for path in namespace["REFERENCE_PATHS"].values()
    }

    with pytest.raises(SystemExit, match="exact acknowledgement phrase"):
        main(
            [
                "--dataset",
                "CsI2017",
                "--no-compute",
                "--write-reference-kernels",
                "--acknowledge-reference-update",
                "I approve updating CsI Slow reference arrays",
            ]
        )

    after = {
        str(path): path.exists()
        for path in namespace["REFERENCE_PATHS"].values()
    }
    assert after == before


def test_csi_fast_reference_generator_no_compute_stays_nonwriting_with_acknowledgement():
    namespace = runpy.run_path(str(REFERENCE_FAST_GENERATOR))
    main = namespace["main"]
    before = {
        str(path): path.exists()
        for path in namespace["REFERENCE_PATHS"].values()
    }

    assert (
        main(
            [
                "--dataset",
                "CsI2017",
                "--no-compute",
                "--write-reference-kernels",
                "--acknowledge-reference-update",
                namespace["APPROVAL_PHRASE"],
            ]
        )
        == 0
    )

    after = {
        str(path): path.exists()
        for path in namespace["REFERENCE_PATHS"].values()
    }
    assert after == before


def test_csi_fast_reference_generator_alignment_metadata_is_strict():
    namespace = runpy.run_path(str(REFERENCE_FAST_GENERATOR))
    alignment = namespace["fast_slow_alignment_metadata"](
        np.array([1.0, 2.0, 3.0]),
        np.array([1.0, 2.0, 3.0 + 1.0e-8]),
    )
    assert alignment["fast_slow_allclose"] is True
    assert alignment["max_abs_bin_delta_vs_slow_reference"] == pytest.approx(1.0e-8)
    assert alignment["worst_bin_index"] == 2

    failed = namespace["fast_slow_alignment_metadata"](
        np.array([1.0, 2.0, 3.0 + 1.0e-4]),
        np.array([1.0, 2.0, 3.0]),
    )
    assert failed["fast_slow_allclose"] is False
    assert failed["worst_bin_tolerance_ratio"] > 1.0

    with pytest.raises(ValueError, match="shape mismatch"):
        namespace["fast_slow_alignment_metadata"](
            np.array([1.0, 2.0]),
            np.array([1.0]),
        )


def test_csi_authoritative_fast_references_reproduce_slow_gate_l_counts():
    missing = [
        str(path)
        for path in REFERENCE_FAST.values()
        if not path.exists() or not path.with_suffix(".json").exists()
    ]
    if missing:
        pytest.skip("P4 pending authoritative CsI Flavor Fast references: " + ", ".join(missing))

    for dataset, fast_path in REFERENCE_FAST.items():
        slow_reference = np.load(REFERENCE_SLOW[dataset])
        loaded, prediction = reconstruct_saved_kernel(fast_path)
        predicted = np.asarray(prediction["counts_per_bin"]["total"], dtype=float)

        assert loaded["metadata"]["flavor_schema_version"] == 1
        assert loaded["metadata"]["coefficient_shape"] == [22, 3, 3]
        assert loaded["metadata"]["reference_kind"] == "authoritative_flavor_fast_kernel"
        assert loaded["metadata"]["gate"] == "P4_FAST"
        assert loaded["metadata"]["slow_reference_path"] == str(REFERENCE_SLOW[dataset]).replace("\\", "/")
        assert loaded["metadata"]["fast_slow_allclose"] is True
        np.testing.assert_allclose(predicted, slow_reference, rtol=1.0e-9, atol=2.0e-8)


def test_csi_fast_yaml_cannot_pass_without_authoritative_fast_references():
    for dataset, fast_path in REFERENCE_FAST.items():
        data = read_simple_yaml(EXPERIMENT_SPECS[dataset])
        fast_validated = data["phase_boundaries"]["fast_validated"]
        sidecar_path = fast_path.with_suffix(".json")

        if not fast_validated:
            assert data["callables"]["fast_counts"] == "BLOCKED_UNTIL_P4_FLAVOR_CONTRACT"
            continue

        assert fast_path.exists()
        assert sidecar_path.exists()
        metadata = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert metadata["flavor_schema_version"] == 1
        assert metadata["coefficient_shape"] == [22, 3, 3]
        assert metadata["reference_kind"] == "authoritative_flavor_fast_kernel"
        assert metadata["gate"] == "P4_FAST"
        assert metadata["fast_slow_allclose"] is True
        assert metadata["dataset"] == dataset


def test_csi2017_fast_saved_kernel_reconstructs_lightweight_slow_counts(tmp_path):
    slow = slow_counts_csi2017(RESPONSES_JSON, n_enu=6)["counts_per_bin"]["total"]
    kernel = build_fastscan_template(
        "CsI2017",
        RESPONSES_JSON,
        n_enu=6,
        n_csi2017_er=251,
    )
    path = save_fastscan_template(tmp_path / "csi2017_fast_kernel.npz", kernel)
    loaded, prediction = reconstruct_saved_kernel(path)

    assert loaded["metadata"]["flavor_schema_version"] == 1
    assert loaded["metadata"]["coefficient_shape"] == [22, 3, 3]
    np.testing.assert_allclose(
        prediction["counts_per_bin"]["total"],
        slow,
        rtol=1.0e-9,
        atol=2.0e-8,
    )


def test_csi2021_fast_saved_kernel_reconstructs_lightweight_slow_counts(tmp_path):
    slow = slow_counts_csi2021(
        RESPONSES_JSON,
        n_er=3,
        n_enu=6,
        n_pe_bin=3,
        pe_step=3.0,
    )["counts_per_bin"]["total"]
    kernel = build_fastscan_template(
        "CsI2021",
        RESPONSES_JSON,
        n_er=3,
        n_enu=6,
        n_pe_sub=3,
        pe_step=3.0,
    )
    path = save_fastscan_template(tmp_path / "csi2021_fast_kernel.npz", kernel)
    loaded, prediction = reconstruct_saved_kernel(path)

    assert loaded["metadata"]["flavor_schema_version"] == 1
    assert loaded["metadata"]["coefficient_shape"] == [22, 3, 3]
    assert loaded["metadata"]["pe_step"] == 3.0
    assert loaded["metadata"]["detector_fold_contract"] == "Slow PE interpolation grid"
    np.testing.assert_allclose(
        prediction["counts_per_bin"]["total"],
        slow,
        rtol=1.0e-9,
        atol=2.0e-8,
    )
