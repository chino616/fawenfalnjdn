from __future__ import annotations

import numpy as np
import pytest

from cevns_pyeft.kernels.reconstruction import reconstruct_counts_from_kernel
from cevns_pyeft.statistics.likelihoods import chi2_csi2021
from cevns_pyeft.statistics.datasets import csi2021_dataset
from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
from cevns_pyeft.statistics.predictors import predict_raw_components

FAST_KERNEL = "tests/reference_CsI2021/fast_kernel.npz"


def _params(**kwargs):
    return vector_nsi_to_np_wilson(VectorNSIParameters(**kwargs))


def _prediction(**kwargs):
    return predict_raw_components("CsI2021", _params(**kwargs), mode="fast", fast_kernel_path=FAST_KERNEL)


def _arrays(pred):
    return {key: np.asarray(pred.components[key].values, dtype=float) for key in ("e", "mu", "mub", "total")}


def _changed_components(case, sm):
    out = set()
    now = _arrays(case)
    base = _arrays(sm)
    for key in ("e", "mu", "mub"):
        rel = np.max(np.abs(now[key] - base[key]) / np.maximum(np.abs(base[key]), 1.0e-30))
        if rel > 1.0e-7:
            out.add(key)
    return out


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({"epsilon_ee_uV": 0.05}, {"e"}),
        ({"epsilon_mumu_uV": 0.05}, {"mu", "mub"}),
        ({"epsilon_emu_uV": 0.05}, {"e", "mu", "mub"}),
        ({"epsilon_etau_uV": 0.05}, {"e"}),
        ({"epsilon_mutau_uV": 0.05}, {"mu", "mub"}),
        ({"epsilon_tautau_uV": 0.05}, set()),
    ],
)
def test_flavor_source_contract(kwargs, expected):
    sm = _prediction()
    assert _changed_components(_prediction(**kwargs), sm) == expected


def test_predictor_exposes_source_components_and_total_sum_rule():
    pred = _prediction(epsilon_emu_uV=0.05)
    arr = _arrays(pred)
    np.testing.assert_allclose(arr["total"], arr["e"] + arr["mu"] + arr["mub"], rtol=1.0e-13, atol=1.0e-13)
    assert pred.components["e"].metadata["source_component"] == "nu_e"
    assert pred.components["mu"].metadata["source_component"] == "nu_mu"
    assert pred.components["mub"].metadata["source_component"] == "nubar_mu"


def _chi2(pred):
    ds = csi2021_dataset()
    return chi2_csi2021(convert_prediction_to_dataset_observable(pred.total, ds.observable), ds).chi2


def test_diagonal_nsi_is_not_sign_symmetric_but_offdiagonal_is():
    ee_plus = _chi2(_prediction(epsilon_ee_uV=0.05))
    ee_minus = _chi2(_prediction(epsilon_ee_uV=-0.05))
    assert abs(ee_plus - ee_minus) > 1.0e-5

    emu_plus = _chi2(_prediction(epsilon_emu_uV=0.05))
    emu_minus = _chi2(_prediction(epsilon_emu_uV=-0.05))
    assert emu_plus == pytest.approx(emu_minus, rel=0.0, abs=1.0e-10)

def test_fast_reconstruction_accepts_single_target_layout():
    full_kernel = np.zeros((1, 3, 2, 1, 1, 4), dtype=complex)
    full_kernel[0, 0, :, 0, 0, :] = [[1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0]]
    full_kernel[0, 1, :, 0, 0, :] = [[2.0, 3.0, 4.0, 5.0], [20.0, 30.0, 40.0, 50.0]]
    full_kernel[0, 2, :, 0, 0, :] = [[3.0, 4.0, 5.0, 6.0], [30.0, 40.0, 50.0, 60.0]]
    kernel = {
        "full_kernel": full_kernel,
        "targets": ["Ar40"],
        "source_flavors": ["mu", "e", "mub"],
        "pe_bins": np.arange(5, dtype=float),
    }

    out = reconstruct_counts_from_kernel(kernel, np.array([1.0 + 0.0j]))
    counts = out["counts_per_bin"]

    np.testing.assert_allclose(counts["mu"], [11.0, 22.0, 33.0, 44.0])
    np.testing.assert_allclose(counts["e"], [22.0, 33.0, 44.0, 55.0])
    np.testing.assert_allclose(counts["mub"], [33.0, 44.0, 55.0, 66.0])
    np.testing.assert_allclose(counts["total"], counts["mu"] + counts["e"] + counts["mub"])

