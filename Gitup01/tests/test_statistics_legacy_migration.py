from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from cevns_pyeft.foundation.constants import G_F
from cevns_pyeft.statistics import confidence as conf
from cevns_pyeft.statistics.datasets import ar2020_dataset, csi2017_dataset, csi2021_dataset
from cevns_pyeft.statistics.likelihoods import chi2_ar2020_bounded, chi2_ar2020_irls, chi2_csi2017, chi2_csi2021
from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable, observable, prediction_vector
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson

try:
    import scipy  # noqa: F401
except Exception:
    scipy = None

REF_DIR = Path("tests/reference/statistics_legacy")


def _reference():
    with (REF_DIR / "profile_reference.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def _cases():
    return np.load(REF_DIR / "fixed_prediction_cases.npz")


def _assert_profile_close(profile, expected, *, atol=1.0e-10):
    assert profile.chi2 == pytest.approx(expected["chi2"], abs=atol, rel=1.0e-12)
    assert profile.alpha == pytest.approx(expected["alpha"], abs=atol, rel=1.0e-12)
    assert profile.beta == pytest.approx(expected["beta"], abs=atol, rel=1.0e-12)
    assert profile.chi2_data == pytest.approx(expected["chi2_data"], abs=atol, rel=1.0e-12)
    assert profile.chi2_nuisance == pytest.approx(expected["chi2_nuisance"], abs=atol, rel=1.0e-12)


def test_reference_artifacts_are_from_frozen_source_files():
    metadata = json.loads((REF_DIR / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["source_git_commit"] is None
    assert "CEvNS-pyEFT-main" in metadata["source_root"]
    files = {row["relative_path"]: row for row in metadata["files"]}
    assert files["src/cevns_pyeft/statistics/cutoff_single.py"]["sha256"] == "40bd3ed819e05b4b577bc45714082b500b5f9ee3864afd38d109a38a572be451"
    assert files["src/cevns_pyeft/statistics/cutoff_multi.py"]["sha256"] == "e7393668ec432ab76062d2d00f19c561bdb8a2ea0628ae8fd553c961eca0ad81"
    assert files["src/cevns_pyeft/statistics/chi2_2d.py"]["sha256"] == "66aa4e557649d57789dbdd10abc9305e4182216a61079fd8572796969d61ab61"


def test_csi2021_likelihood_matches_legacy_fixed_cases():
    ref = _reference()["csi2021"]
    cases = _cases()
    ds = csi2021_dataset()
    raw = observable("reconstructed PE spectrum", "events/bin", ds.observable.bin_edges)
    for name in ("zero", "ones", "ramp", "background_width_scaled"):
        pred = prediction_vector(cases[f"csi2021_{name}"], raw)
        converted = convert_prediction_to_dataset_observable(pred, ds.observable)
        _assert_profile_close(chi2_csi2021(converted, ds), ref[name])


def test_csi2017_likelihood_matches_legacy_fixed_cases():
    ref = _reference()["csi2017"]
    cases = _cases()
    ds = csi2017_dataset()
    for name in ("zero", "ones", "legacy_spectrum", "observed"):
        pred = prediction_vector(cases[f"csi2017_{name}"], ds.observable)
        _assert_profile_close(chi2_csi2017(pred, ds), ref[name])


def test_ar2020_irls_and_bounded_match_legacy_fixed_cases():
    ref = _reference()["ar2020"]
    cases = _cases()
    ds = ar2020_dataset()
    for name in ("zero", "ones", "observed_minus_background", "ramp"):
        pred = prediction_vector(cases[f"ar2020_{name}"], ds.observable)
        _assert_profile_close(chi2_ar2020_irls(pred, ds), ref[name]["irls"], atol=1.0e-9)
        if not ref[name]["bounded"].get("available", True) or scipy is None:
            continue
        _assert_profile_close(chi2_ar2020_bounded(pred, ds), ref[name]["bounded"], atol=1.0e-7)


def test_observable_conversion_is_explicit_and_validated():
    ds = csi2021_dataset()
    raw = observable("reconstructed PE spectrum", "events/bin", ds.observable.bin_edges)
    counts = np.asarray([8.0, 4.0, 4.0, 4.0, 4.0, 8.0, 8.0, 8.0, 12.0])
    converted = convert_prediction_to_dataset_observable(prediction_vector(counts, raw), ds.observable)
    np.testing.assert_allclose(converted.values, counts / np.diff(ds.observable.bin_edges))
    bad = observable("reconstructed PE spectrum", "events/bin", [0.0, 1.0, 2.0])
    with pytest.raises(ValueError, match="bin edges"):
        convert_prediction_to_dataset_observable(prediction_vector([1.0, 2.0], bad), ds.observable)


def test_confidence_definitions_keep_46_and_461_separate():
    assert conf.confidence_definition("legacy_2d_90_flow_a").delta_chi2 == pytest.approx(4.61)
    assert conf.confidence_definition("legacy_2d_90_flow_b").delta_chi2 == pytest.approx(4.61)
    assert conf.confidence_definition("legacy_2d_90_rounded_api").delta_chi2 == pytest.approx(4.6)


def test_vector_nsi_mapping_uses_project_gf_and_hermitian_np_only_matrices():
    params = VectorNSIParameters(
        epsilon_ee_uV=1.0,
        epsilon_mumu_uV=2.0,
        epsilon_emu_uV=0.25 + 0.5j,
    )
    wilson = vector_nsi_to_np_wilson(params)
    u = wilson[(6, 1, "u")]
    assert u.shape == (3, 3)
    np.testing.assert_allclose(u, u.conj().T)
    assert u[0, 0].real == pytest.approx(-math.sqrt(2.0) * G_F)
    assert u[1, 1].real == pytest.approx(-2.0 * math.sqrt(2.0) * G_F)
    assert u[0, 1] == pytest.approx(-math.sqrt(2.0) * G_F * (0.25 + 0.5j))
    np.testing.assert_allclose(wilson[(6, 1, "d")], np.zeros((3, 3)))


