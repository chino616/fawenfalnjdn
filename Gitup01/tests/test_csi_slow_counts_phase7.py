from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np

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


def test_csi2021_slow_rejects_automatic_pe_grid_coarser_than_bin_width():
    import pytest

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
