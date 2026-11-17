"""Known-zero likelihood with far, narrow branches guards the reported defect."""
from pathlib import Path
import importlib.util
import sys
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('_joint_minimum_regression', ROOT/'examples/paper2601_chi2/run_benchmark.py')
benchmark = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = benchmark
spec.loader.exec_module(benchmark)


def channel(name, slope, observed, sigma=20., pull=.1):
    # S=1+(u+slope*d)^2, an exactly nonnegative count model.
    coefficients = np.array([[1.], [0.], [0.], [1.], [2*slope], [slope*slope]])
    return benchmark.Channel(name, coefficients, np.array([observed]), np.array([sigma]), pull)


def test_narrow_far_branches_recover_known_zero_chi2():
    first, second = channel('first', 1., 25.), channel('second', 1.001, 36.)
    objective = lambda u, d: first.chi2(u, d)+second.chi2(u, d)
    # The exact four solutions have u+d=+-sqrt(24), u+1.001d=+-sqrt(35).
    # Every exact solution lies beyond |epsilon|=100; coincident bounded minima
    # therefore cannot justify stopping the search on the plotted box.
    result = benchmark.fit_plane_minimum(objective, [first, second])
    u, d = result['best_fit']['coordinates']
    assert result['minimum_search_verified']
    assert result['best_fit']['chi2'] < 1e-7
    assert max(abs(u), abs(d)) > 100.
    assert 1+(u+d)**2 == pytest.approx(25., abs=1e-4)
    assert 1+(u+1.001*d)**2 == pytest.approx(36., abs=1e-4)
    geometry = result['search_geometry']
    total_events = 2+(u+d)**2+(u+1.001*d)**2
    assert total_events <= geometry['total_signal_upper_bound_for_any_chi2_better_than_SM']


def test_no_finite_improvement_domain_is_not_silently_assumed():
    first, second = channel('first', 1., 100., sigma=1., pull=1.), channel('second', 2., 100., sigma=1., pull=1.)
    objective = lambda u, d: first.chi2(u, d)+second.chi2(u, d)
    with pytest.raises(ValueError, match='no finite search-domain bound proved'):
        benchmark.fit_plane_minimum(objective, [first, second])
