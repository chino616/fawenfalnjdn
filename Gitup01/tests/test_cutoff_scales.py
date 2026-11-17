"""Independent analytic tests for the isolated cutoff statistics Part."""
import importlib.util
from pathlib import Path
import sys

import numpy as np
from numpy.polynomial import Polynomial as P
import pytest

PATH = Path(__file__).resolve().parents[1]/"examples/cutoff_scales/inference.py"
SPEC = importlib.util.spec_from_file_location("cutoff_scales_inference_tests", PATH)
infer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = infer
SPEC.loader.exec_module(infer)


@pytest.mark.parametrize("dimension", [5, 6, 7, 8])
def test_known_one_tev_coefficient_and_coupling_scaling(dimension):
    coefficient = 1000.**(4-dimension)
    assert infer.cutoff(coefficient, dimension) == pytest.approx(1000.)
    assert infer.cutoff(coefficient, dimension, 3.) == pytest.approx(1000.*3.**(1/(dimension-4)))


@pytest.mark.parametrize("coefficient", [0., -1., np.nan, np.inf])
def test_invalid_coefficient_is_not_a_finite_or_infinite_limit(coefficient):
    with pytest.raises(ValueError):
        infer.cutoff(coefficient, 6)


def test_two_known_islands_keep_sm_excluded_and_all_lambda_bands():
    fn = lambda x: (np.asarray(x)**2-4)**2
    result = infer.scan(fn, (-4., 4.), coefficient_scale=1e-6, dimension=6,
                        rational=(P([16., 0., -8., 0., 1.]), P([1.])), grid_size=257)
    level = result["confidence"]["90"]
    root_lo, root_hi = np.sqrt(4-np.sqrt(2.71)), np.sqrt(4+np.sqrt(2.71))
    np.testing.assert_allclose(level["intervals_x"], [[-root_hi, -root_lo], [root_lo, root_hi]], atol=1e-10)
    assert level["sm_status"] == "SM_EXCLUDED"
    assert level["sm_connected_GeV"] is None
    assert len(level["lambda_intervals"]) == 2
    assert level["positive_GeV"] == pytest.approx(level["negative_GeV"])
    assert level["global_GeV"] == pytest.approx((root_hi*1e-6)**-.5)


def test_zero_coefficient_endpoint_maps_to_unbounded_lambda():
    bands = infer.convert_intervals([[-.2, 0.], [1., 2.]], 1e-6, 6)
    assert [b["coefficient_sign"] for b in bands] == ["negative", "positive"]
    assert bands[0]["upper_unbounded"]
    assert bands[0]["lambda_max_GeV"] is None
    assert bands[1]["lambda_min_GeV"] == pytest.approx(1/np.sqrt(2e-6))
    assert bands[1]["lambda_max_GeV"] == pytest.approx(1000.)


def test_strict_sm_connected_does_not_select_nearest_interval():
    limits = infer.interval_limits([[1., 2.]], 1e-6, 6)
    assert limits["sm_status"] == "SM_EXCLUDED"
    assert limits["sm_connected_GeV"] is None


def test_flat_direction_has_no_numeric_bar_height():
    result = infer.scan(lambda x: np.asarray(x)*0+3., (-1., 1.),
                        coefficient_scale=1e-6, dimension=6, no_sensitivity=True)
    assert result["status"] == "NO_SENSITIVITY"
    assert result["confidence"]["90"]["global_GeV"] is None


def test_allowed_numerical_edge_is_rejected():
    with pytest.raises(ValueError, match="SEARCH_NOT_CLOSED"):
        infer.scan(lambda x: np.asarray(x)**2, (-1., 1.), coefficient_scale=1e-6, dimension=6)


def test_profile_and_rational_form_against_independent_augmented_lstsq():
    model = infer.Gaussian(np.array([14., 8., 5.]), np.array([2., 3., 1.]), .15,
                           np.array([1., 2., 1.5]), .25)
    coefficients = np.array([[8., 7., 5.], [2., -1., .5], [1., 2., 1.]])
    numerator, denominator = model.rational(coefficients)
    for x in (-3., -.7, 0., .3, 2.):
        signal = coefficients[0]+x*coefficients[1]+x*x*coefficients[2]
        design = np.vstack([np.column_stack([signal/model.sigma, model.background/model.sigma]),
                            np.diag([1/model.alpha_sigma, 1/model.beta_sigma])])
        rhs = np.r_[(model.observed-signal-model.background)/model.sigma, [0., 0.]]
        fit = np.linalg.lstsq(design, rhs, rcond=None)[0]
        expected = np.sum((design@fit-rhs)**2)
        assert model.profile(signal)[0] == pytest.approx(expected, abs=1e-11)
        assert numerator(x)/denominator(x) == pytest.approx(expected, abs=1e-10)


def test_rate_upper_bound_is_necessary_for_an_accepted_signal():
    model = infer.Gaussian(np.array([5., 8.]), np.array([2., 3.]), .12)
    level = 5.
    bound = model.rate_upper_bound(level)
    for scale in np.linspace(0., 8., 501):
        signal = np.array([3., 6.])*scale
        if model.profile(signal)[0] <= level:
            assert signal.sum() <= bound*(1+1e-12)
