"""Joint inference must preserve physical scales and joint nuisance profiling."""
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar

HERE = Path(__file__).resolve().parents[1]/"examples/cutoff_scales"
sys.path.insert(0, str(HERE))
from inference import Gaussian
from run_joint import CombinedObjective, block_least_squares


class Quadratic:
    def __init__(self, scale, center, offset):
        self.coefficient_scale, self.center, self.offset = scale, center, offset
        self.no_sensitivity = False

    def __call__(self, x):
        return (np.asarray(x)*self.coefficient_scale-self.center)**2+self.offset

    def domain(self, threshold):
        self.last_threshold = threshold
        radius = np.sqrt(float(self(0.))+threshold-self.offset)
        return ((self.center-radius)/self.coefficient_scale,
                (self.center+radius)/self.coefficient_scale), {"total_level": float(self(0.))+threshold}


def test_physical_scale_and_minimum_offset():
    a, b = Quadratic(.3, -1., 7.), Quadratic(2., 3., 11.)
    joint = CombinedObjective([a, b], .7)
    c = np.linspace(-5, 5, 21)
    np.testing.assert_allclose(joint(c/.7), (c+1)**2+(c-3)**2+18)
    opt = minimize_scalar(joint)
    np.testing.assert_allclose(opt.x*.7, 1., atol=1e-7)
    np.testing.assert_allclose(opt.fun, 26.)
    # Summed component Delta functions have minimum 8, rather than zero.
    np.testing.assert_allclose(joint(opt.x)-a.offset-b.offset, 8.)
    domain, proof = joint.domain()
    level = float(joint(0.))+3.84
    np.testing.assert_allclose(float(a(0.))+a.last_threshold, level)
    np.testing.assert_allclose(float(b(0.))+b.last_threshold, level)
    assert domain[0] < 0 < domain[1]
    assert proof["total_level"] == level


def test_joint_eight_pull_block_solve():
    rng = np.random.default_rng(19883)
    rows = []
    for i, n in enumerate([19, 9, 12, 1, 1, 1]):
        signal = rng.uniform(3, 20, n)
        background = rng.uniform(0, 4, n) if i in (1, 2) else None
        data = signal+(0 if background is None else background)+rng.normal(0, 2, n)
        channel = Gaussian(data, np.full(n, 2.), .12, background, .35 if background is not None else None)
        rows.append((str(i), channel, signal))
    block, pulls = block_least_squares(rows)
    expected = sum(float(ch.profile(s)[0]) for _, ch, s in rows)
    np.testing.assert_allclose(block, expected, atol=1e-11)
    assert len(pulls) == 8
