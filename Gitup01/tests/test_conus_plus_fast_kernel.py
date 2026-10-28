from pathlib import Path

import numpy as np
import pytest

from cevns_pyeft.experiments.conus_plus.fast_kernel import (
    StaleConusResponseMatrixError,
    build_detector_response_matrix,
    fast_counts_conus_plus_response_matrix,
    load_detector_response_matrix,
    save_detector_response_matrix,
    validate_detector_response_matrix,
)
from cevns_pyeft.experiments.conus_plus.slow_counts import (
    slow_counts_conus_plus,
)


RESPONSES = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "responses"
    / "responses_all.json"
)


def test_response_matrix_contract_shape_units_and_metadata():
    cache = build_detector_response_matrix(n_recoil=18)
    validate_detector_response_matrix(cache)

    assert cache["weighted_folding_kg_day_kev"].shape == (3, 18, 19)
    assert cache["metadata"]["fast_type"] == "detector_response_matrix"
    assert cache["metadata"]["unit"] == "kg_day_keVnr"
    assert cache["metadata"]["exposures_kg_day"] == [119.0, 119.0, 119.0]
    assert (
        cache["metadata"]["eft_quadratic_coefficient_kernel"]
        == "not_included"
    )
    assert len(cache["metadata"]["cache_key_sha256"]) == 64


@pytest.mark.parametrize("complex_point", [False, True])
def test_response_matrix_fast_matches_slow_per_bin(complex_point):
    coefficient = np.zeros((3, 3), dtype=np.complex128)
    coefficient[0, 1] = 1.0e-6 + 2.0e-7j
    wc = {(6, 1, "u"): coefficient} if complex_point else {}
    cache = build_detector_response_matrix(n_recoil=18)

    slow = slow_counts_conus_plus(
        RESPONSES,
        wc,
        n_recoil=18,
        n_energy=4,
    )
    fast = fast_counts_conus_plus_response_matrix(
        cache,
        RESPONSES,
        wc,
        n_energy=4,
    )
    np.testing.assert_allclose(
        fast["counts_per_detector_component_bin"],
        slow["counts_per_detector_component_bin"],
        rtol=3.0e-14,
        atol=2.0e-14,
    )


def test_response_matrix_save_load_round_trip(tmp_path):
    cache = build_detector_response_matrix(n_recoil=12)
    npz_path, json_path = save_detector_response_matrix(
        tmp_path / "conus_plus_detector_response_matrix_v1.npz",
        cache,
    )
    loaded = load_detector_response_matrix(npz_path)

    assert npz_path.exists() and json_path.exists()
    assert loaded["metadata"] == cache["metadata"]
    np.testing.assert_array_equal(
        loaded["weighted_folding_kg_day_kev"],
        cache["weighted_folding_kg_day_kev"],
    )


def test_response_contract_change_invalidates_cache():
    cache = build_detector_response_matrix(n_recoil=12)
    cache["metadata"] = dict(cache["metadata"])
    cache["metadata"]["detector_response_contract"] = dict(
        cache["metadata"]["detector_response_contract"]
    )
    cache["metadata"]["detector_response_contract"]["lindhard_k"] = 0.163
    with pytest.raises(StaleConusResponseMatrixError, match="metadata"):
        validate_detector_response_matrix(cache)


def test_exposure_change_changes_cache_key():
    baseline = build_detector_response_matrix(n_recoil=12)
    changed = build_detector_response_matrix(
        n_recoil=12,
        exposures_kg_day=np.array([120.0, 119.0, 119.0]),
    )

    assert (
        baseline["metadata"]["cache_key_sha256"]
        != changed["metadata"]["cache_key_sha256"]
    )
