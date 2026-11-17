"""Mean-yield approximation: change of variables, partition, and input identity."""
from pathlib import Path
import unittest

import numpy as np
from scipy.integrate import quad

from cevns_pyeft.experiments.catalog import ExperimentCatalog
from cevns_pyeft.experiments.loader import load_experiment
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.experiments.solar_mean_map import inverse_mean_edges, with_pandax_mean_map
from cevns_pyeft.sources.composable import ScaledSource

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/'data/experiments/PandaX4T/PandaX4T_2024_US2'


class SolarMeanMapTests(unittest.TestCase):
    def test_inverse_and_jacobian_preserve_analytic_bin_integrals(self):
        # Independent analytic model: Qy=2+T, n=2T+T², dn/dT=2+2T.
        edges = np.array([1., 2., 4., 7.])
        recoil = inverse_mean_edges([0., 3.], [2., 5.], edges)
        np.testing.assert_allclose(recoil, np.sqrt(1+edges)-1, rtol=1e-12)
        for a, b, na, nb in zip(recoil[:-1], recoil[1:], edges[:-1], edges[1:]):
            direct = (b*b-a*a)/2  # independent test density r(T)=T
            transformed = quad(lambda n: (np.sqrt(1+n)-1)/(2*np.sqrt(1+n)), na, nb)[0]
            self.assertAlmostEqual(direct, transformed, places=12)

    def test_nonmonotone_mapping_and_extrapolation_are_rejected(self):
        # Node values T*Qy increase, yet the derivative becomes negative inside.
        with self.assertRaisesRegex(ValueError, 'every segment'):
            inverse_mean_edges([1., 2.], [1., .6], [1., 1.1])
        with self.assertRaisesRegex(ValueError, 'outside verified'):
            inverse_mean_edges([.3, 3.], [5., 5.], [1., 8.])

    def test_runtime_partition_flux_scaling_and_distinct_approximation(self):
        base = load_experiment_package(PACKAGE)
        simplified = with_pandax_mean_map(base, qy_file=PACKAGE/'detector/pandax_qy_nominal.txt')
        self.assertEqual(base.model.mode, 'recoil_acceptance')
        self.assertEqual(base.definition.observation.unit, 'keVnr')
        self.assertEqual(simplified.definition.observation.unit, 'electron')
        self.assertNotEqual(base.physics_fingerprint, simplified.physics_fingerprint)
        self.assertEqual(len(simplified.record['resources']), 3)
        registry = ExperimentCatalog(builtins=False).register(simplified.dataset_id, simplified.definition)
        doubled = load_experiment(simplified.dataset_id, definition=simplified.definition,
            resources=simplified.resource_catalog, registry=registry,
            components={'source': ScaledSource(simplified.model.source, 2.)})
        n = {'n_er': 51, 'n_enu': 60}
        first = predict_experiment(simplified, numerics=n)
        second = predict_experiment(doubled, numerics=n)
        self.assertTrue(np.all(first.counts > 0))
        np.testing.assert_allclose(second.counts, 2*first.counts, rtol=3e-14)
        np.testing.assert_allclose(sum(first.combined_prediction.components.values()), first.counts, rtol=2e-14)
        d = first.combined_prediction.diagnostics
        self.assertAlmostEqual(d['accepted_domain_total_events'],
            first.counts.sum()+sum(d['outside_mean_window_events_low_high']), places=11)
        self.assertGreater(d['accepted_domain_total_events'], first.counts.sum())
        np.testing.assert_allclose(simplified.model.observation[0].recoil_edges[[0, -1]],
            [.6600837072119007, 1.1868926216472357], atol=1e-12)
        with self.assertRaises(TypeError):
            with_pandax_mean_map(simplified, qy_file=PACKAGE/'detector/pandax_qy_nominal.txt')


if __name__ == '__main__':
    unittest.main()
