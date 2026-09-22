from __future__ import annotations

import csv
import inspect
import json
import runpy
from pathlib import Path

import numpy as np
import pytest

from cevns_pyeft.experiments.specs import read_simple_yaml
from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import (
    CSI2017_BINS_25,
    CSI2017_WIDTHS_25,
    slow_counts_csi2017,
)
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import (
    PE_BINS_9,
    PE_WIDTHS_9,
    slow_counts_csi2021,
)
from cevns_pyeft.experiments.coherent.slow_counts_ar2020 import slow_counts_ar2020
from cevns_pyeft.theory.li2026.flavor import zero_flavor_matrix


RESPONSES_JSON = Path("data/responses/responses_all.json")
RUNS_DIR = Path("workflows/experiment-integration/runs")
REFERENCE_FAST_SPLIT = Path("tests/reference_fast_split")
REFERENCE_GENERATOR = Path("tools/experiment_integration/generate_csi_slow_references.py")
REFERENCE_SLOW = {
    "CsI2017": Path("tests/reference_CsI2017/slow_reference.npy"),
    "CsI2021": Path("tests/reference_CsI2021/slow_reference.npy"),
}
EXPERIMENT_SPECS = {
    "CsI2017": Path("data/experiments/CsI2017/experiment.yaml"),
    "CsI2021": Path("data/experiments/CsI2021/experiment.yaml"),
}


def _assert_counts_contract(out: dict, *, shape: tuple[int, ...], widths: np.ndarray) -> None:
    counts = out["counts_per_bin"]
    total = np.asarray(counts["total"], dtype=float)
    assert total.shape == shape
    assert np.all(np.isfinite(total))
    assert np.all(total >= 0.0)
    np.testing.assert_allclose(
        total,
        np.asarray(counts["mu"]) + np.asarray(counts["e"]) + np.asarray(counts["mub"]),
        rtol=1.0e-12,
        atol=0.0,
    )
    for key, value in counts.items():
        arr = np.asarray(value, dtype=float)
        assert arr.shape == shape
        assert np.all(np.isfinite(arr))
        assert np.all(arr >= 0.0)
        np.testing.assert_allclose(
            out["counts_per_npe"][key],
            arr / widths,
            rtol=1.0e-12,
            atol=0.0,
        )


def test_csi2017_slow_direct_counts_contract_and_regression_total():
    out = slow_counts_csi2017(RESPONSES_JSON, n_enu=6)
    _assert_counts_contract(out, shape=(25,), widths=CSI2017_WIDTHS_25)
    np.testing.assert_allclose(out["pe_bins"], CSI2017_BINS_25, rtol=0.0, atol=0.0)
    assert float(np.sum(out["counts_per_bin"]["total"])) == np.float64(144.97689163030518)


def test_csi2021_slow_direct_counts_contract_and_regression_total():
    out = slow_counts_csi2021(
        RESPONSES_JSON,
        n_er=5,
        n_enu=12,
        n_pe_bin=3,
    )
    _assert_counts_contract(out, shape=(9,), widths=PE_WIDTHS_9)
    np.testing.assert_allclose(out["pe_bins"], PE_BINS_9, rtol=0.0, atol=0.0)
    assert float(np.sum(out["counts_per_bin"]["total"])) == np.float64(381.8912488750059)


def test_csi_slow_zero_without_sm_or_np_coefficients():
    csi2017 = slow_counts_csi2017(RESPONSES_JSON, include_sm=False, n_enu=6)
    csi2021 = slow_counts_csi2021(
        RESPONSES_JSON,
        include_sm=False,
        n_er=3,
        n_enu=6,
        n_pe_bin=3,
    )
    np.testing.assert_array_equal(csi2017["counts_per_bin"]["total"], np.zeros(25))
    np.testing.assert_array_equal(csi2021["counts_per_bin"]["total"], np.zeros(9))


def test_csi_slow_accepts_explicit_flavor_matrix_wilson_coefficients():
    coeff = zero_flavor_matrix()
    coeff[0, 1] = 1.0e-8 + 2.0e-9j
    out = slow_counts_csi2021(
        RESPONSES_JSON,
        wc_triplets={(6, 1, "u"): coeff},
        n_er=3,
        n_enu=6,
        n_pe_bin=3,
    )
    total = np.asarray(out["counts_per_bin"]["total"], dtype=float)
    assert total.shape == (9,)
    assert np.all(np.isfinite(total))
    assert np.all(total >= 0.0)


def test_ar2020_shared_counts_exact_support_nonregression():
    out = slow_counts_ar2020(
        RESPONSES_JSON,
        include_sm=True,
        n_er=3,
        n_enu=6,
        n_pe_bin=3,
    )
    total = np.asarray(out["counts_per_bin"]["total"], dtype=float)
    assert total.shape == (12,)
    assert np.all(np.isfinite(total))
    assert np.all(total >= 0.0)
    assert float(np.sum(total)) == np.float64(23.203475634474284)


def test_csi_phase7_stale_fast_diagnostic_is_not_gate_l_reference():
    for dataset, stem, dominant_component, expected_total_delta in (
        ("CsI2017", "csi2017", "mu", 0.7867905882172579),
        ("CsI2021", "csi2021", "mub", -0.13227960865830823),
    ):
        metadata = json.loads(
            (REFERENCE_FAST_SPLIT / f"{stem}_metadata.json").read_text(
                encoding="utf-8"
            )
        )
        assert "flavor_schema_version" not in metadata

        path = RUNS_DIR / dataset / "artifacts" / "slow_vs_stale_fast_split_components.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = {row["component"]: row for row in csv.DictReader(handle)}

        assert set(rows) == {"mu", "e", "mub", "total"}
        assert rows[dominant_component]["diagnosis"]
        assert float(rows["total"]["delta"]) == np.float64(expected_total_delta)
        assert dominant_component in rows["total"]["diagnosis"]


def test_csi_slow_reference_generator_defaults_to_nonwriting_guard():
    namespace = runpy.run_path(str(REFERENCE_GENERATOR))
    assert namespace["APPROVAL_PHRASE"] == "I approve updating CsI Slow reference arrays"
    assert namespace["REFERENCE_PATHS"]["CsI2017"].as_posix().endswith(
        "tests/reference_CsI2017/slow_reference.npy"
    )
    assert namespace["REFERENCE_PATHS"]["CsI2021"].as_posix().endswith(
        "tests/reference_CsI2021/slow_reference.npy"
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


def test_csi_gate_l_yaml_matches_authoritative_slow_reference_availability():
    for dataset, reference_path in REFERENCE_SLOW.items():
        data = read_simple_yaml(EXPERIMENT_SPECS[dataset])
        sidecar_path = reference_path.with_suffix(".json")
        if reference_path.exists() and sidecar_path.exists():
            assert data["spec_status"] in {"slow_validated", "fast_validated"}
            assert data["provenance"]["phase"] in {"SLOW_VALIDATED", "FAST_VALIDATED"}
            assert data["planned_data_files"]["slow_reference"] == str(reference_path).replace("\\", "/")
            assert data["planned_data_files"]["slow_reference_metadata"] == str(sidecar_path).replace("\\", "/")
            assert data["callables"]["slow_counts"].startswith("cevns_pyeft.experiments.coherent.slow_counts_csi")
            assert data["phase_boundaries"]["slow_validated"] is True
            if data["phase_boundaries"]["fast_validated"]:
                fast_reference = Path(data["planned_data_files"]["fast_reference"])
                fast_sidecar = Path(data["planned_data_files"]["fast_reference_metadata"])
                assert fast_reference.exists()
                assert fast_sidecar.exists()
            continue

        assert data["spec_status"] == "detector_response_validated_slow_pending"
        assert data["provenance"]["phase"] == "DETECTOR_RESPONSE_VALIDATED"
        assert data["callables"]["slow_counts"].startswith("PENDING_PHASE_7:")
        assert data["phase_boundaries"]["slow_validated"] is False
        assert data["phase_boundaries"]["fast_validated"] is False


def test_csi_gate_l_saved_slow_references_reproduce_direct_defaults():
    missing = [
        str(path)
        for path in REFERENCE_SLOW.values()
        if not path.exists() or not path.with_suffix(".json").exists()
    ]
    if missing:
        pytest.skip("Gate L pending authoritative CsI Slow references: " + ", ".join(missing))

    namespace = runpy.run_path(str(REFERENCE_GENERATOR))
    compute_slow_reference = namespace["compute_slow_reference"]
    for dataset, reference_path in REFERENCE_SLOW.items():
        reference = np.load(reference_path)
        computed, metadata = compute_slow_reference(dataset)
        sidecar = json.loads(reference_path.with_suffix(".json").read_text(encoding="utf-8"))

        np.testing.assert_allclose(computed, reference, rtol=1.0e-12, atol=1.0e-12)
        assert sidecar["reference_kind"] == "authoritative_slow_counts"
        assert sidecar["gate"] == "L"
        assert sidecar["dataset"] == dataset
        assert sidecar["shape"] == list(reference.shape)
        assert sidecar["sha256"] == metadata["sha256"]


def test_csi2021_slow_rejects_automatic_pe_grid_coarser_than_bin_width():
    with pytest.raises(ValueError, match="pe_step"):
        slow_counts_csi2021(
            RESPONSES_JSON,
            n_er=3,
            n_enu=6,
            n_pe_bin=3,
            pe_step=20.0,
        )


def test_csi_slow_modules_do_not_depend_on_fast_or_statistics_layers():
    import cevns_pyeft.experiments.coherent.slow_counts_csi2017 as csi2017
    import cevns_pyeft.experiments.coherent.slow_counts_csi2021 as csi2021
    import cevns_pyeft.rates.counts as counts

    source = "\n".join(
        inspect.getsource(module)
        for module in (csi2017, csi2021, counts)
    ).lower()
    for forbidden in ("fast_kernel", "reference_fast_split", "statistics", "likelihood"):
        assert forbidden not in source
