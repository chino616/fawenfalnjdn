"""Actual nuclear table -> shared SM amplitude -> solar Runtime contracts."""
from dataclasses import replace
from pathlib import Path
import unittest
import numpy as np

from cevns_pyeft.contracts import IncidentStateBatch, TheoryPoint
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.experiments.solar_mean_map import with_pandax_mean_map
from cevns_pyeft.experiments.solar_nuclear import with_solar_nuclear_response, XE_KEYS
from cevns_pyeft.foundation import constants as c
from cevns_pyeft.rates.differential import differential_cross_section_nn, _sm_left_dim6
from cevns_pyeft.theory.li2026.left_to_ci import left_to_ci

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/'data/experiments/PandaX4T/PandaX4T_2024_US2'
TABLE = ROOT/'data/responses/responses_all.json'


class SolarNuclearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load_experiment_package(PACKAGE)
        cls.mean = with_pandax_mean_map(cls.base, qy_file=PACKAGE/'detector/pandax_qy_nominal.txt')
        cls.exp = with_solar_nuclear_response(cls.mean, response_file=TABLE)

    def test_actual_resource_bound_and_counts_not_renormalized(self):
        self.assertIn('nuclear_response', self.exp.record['resources'])
        self.assertNotEqual(self.mean.physics_fingerprint, self.exp.physics_fingerprint)
        targets = self.exp.model.targets
        self.assertEqual(tuple(t.isotope_id for t in targets.isotopes), XE_KEYS)
        old = {t.isotope_id: t for t in self.base.model.targets.isotopes}
        for t in targets.isotopes:
            self.assertEqual(t.number_of_nuclei, old[t.isotope_id].number_of_nuclei)
            self.assertEqual(t.kinematic_mass_GeV, int(t.isotope_id[2:])*c.AMU_GEV)
        self.assertLess(targets.detector_mass_kg, 1000.)
        self.assertEqual(self.exp.model.anchor_mass_kg, 1000.)
        self.assertEqual(self.exp.model.source.describe(), self.mean.model.source.describe())
        self.assertEqual(len(self.exp.model.observation[0].charge_yield), 36)

    def test_sm_matching_has_only_energy_independent_nonzero_coefficients(self):
        # Establish the reason that a quadratic identity is valid for this scope.
        left = _sm_left_dim6(True, .23857)
        low = left_to_ci(left, E_nu=.012, q0=1e-6, qabs=.015, mA=122.)
        high = left_to_ci(left, E_nu=.031, q0=1e-6, qabs=.015, mA=122.)
        for pn in ('p', 'n'):
            for i in range(1, 15):
                np.testing.assert_array_equal(getattr(low, pn)[i], getattr(high, pn)[i])
                if i not in (1, 2, 5, 6, 7):
                    np.testing.assert_array_equal(getattr(low, pn)[i], np.zeros((3, 3)))

    def test_vectorized_cross_sections_match_original_shared_amplitude(self):
        m = self.exp.model
        for t in m.targets.isotopes:
            for recoil in (0., .13, .8, 1.18, 2.7):
                energies = np.array([2., 7., 11.3, 16.56, 27.])
                state = IncidentStateBatch(energies, np.diag([1., 0., 0.]), 'nu', 'test')
                point = TheoryPoint(sin2thetaW=.23857)
                actual = m.interaction.dsigma_dT(target=t, energy_MeV=energies,
                    recoil_keV=recoil, incident_state=state, parameters=point).values_cm2_per_keV
                expected = differential_cross_section_nn(m.interaction._responses[t.isotope_id],
                    recoil, energies, rho=state.rho, particle_kind='nu', include_sm=True,
                    sin2thetaW=point.sin2thetaW).dsigma_cm2_per_keV
                np.testing.assert_allclose(actual, expected, rtol=3e-11, atol=2e-54)

    def test_m_zero_recoil_absolute_contraction_and_units(self):
        t = self.exp.model.targets.isotopes[3]
        interaction = self.exp.model.interaction
        energy = np.array([5., 10.])
        state = IncidentStateBatch(energy, np.eye(3)/3, 'nu', 'test')
        point = TheoryPoint(sin2thetaW=.23857)
        pieces = interaction.channel_dsigma(target=t, energy_MeV=energy, recoil_keV=0.,
            incident_state=state, parameters=point)
        resp = interaction._responses[t.isotope_id]
        W = np.asarray(resp.W_np('M', 0.))
        # Independent M contraction, without invoking compute_R or amplitude.py.
        cp = c.G_F/np.sqrt(2)*np.array([-(1-4*point.sin2thetaW), 1.])
        expected = t.kinematic_mass_GeV/(2*np.pi)*(cp@W@cp)*c.GEV_INV2_TO_CM2*1e-6
        np.testing.assert_allclose(pieces['M'], expected, rtol=4e-14)
        self.assertEqual(np.asarray(resp.responses['M']).shape, (2, 2, 11))

    def test_support_wrong_mass_and_bsm_are_rejected(self):
        m = self.exp.model; t = m.targets.isotopes[0]
        e = np.array([1., 2.])
        state = IncidentStateBatch(e, np.eye(3)/3, 'nu', 'test')
        kwargs = dict(target=t, energy_MeV=e, recoil_keV=2., incident_state=state)
        actual = m.interaction.dsigma_dT(**kwargs, parameters=TheoryPoint()).values_cm2_per_keV
        np.testing.assert_array_equal(actual, [0., 0.])
        with self.assertRaisesRegex(ValueError, r'A\*amu'):
            m.interaction.dsigma_dT(**dict(kwargs, target=replace(t, kinematic_mass_GeV=123.)),
                                   parameters=TheoryPoint())
        with self.assertRaises(UnsupportedCapabilityError):
            m.interaction.dsigma_dT(**kwargs, parameters=TheoryPoint(wc_triplets={(6, 1, 'u'):np.eye(3)}))
        with self.assertRaisesRegex(ValueError, 'available Xe'):
            with_solar_nuclear_response(self.mean, response_file=TABLE, isotope_keys=('Xe124',))
        zero = m.interaction.dsigma_dT(**kwargs, parameters=TheoryPoint(include_sm=False))
        np.testing.assert_array_equal(zero.values_cm2_per_keV, [0., 0.])

    def test_exact_endpoint_roundoff_preserves_nonzero_spin_pieces(self):
        m = self.exp.model
        e = np.array([16.56])
        state = IncidentStateBatch(e, np.eye(3)/3, 'nu', 'endpoint')
        for t in m.targets.isotopes:
            endpoint = m.interaction.kinematics.maximum_recoil_keV(t, e[0])
            pieces = m.interaction.channel_dsigma(target=t, energy_MeV=e, recoil_keV=endpoint,
                incident_state=state, parameters=TheoryPoint(sin2thetaW=.23857))
            np.testing.assert_array_equal(pieces['M'], [0.])
            if t.isotope_id in ('Xe129', 'Xe131'):
                self.assertGreater(pieces['SigmaP'][0], 0.)
            ds = m.interaction.dsigma_dT(target=t, energy_MeV=e, recoil_keV=endpoint,
                incident_state=state, parameters=TheoryPoint(sin2thetaW=.23857))
            self.assertTrue(np.isfinite(ds.values_cm2_per_keV).all())

    def test_runtime_partition_and_matched_kn_control(self):
        result = predict_experiment(self.exp, numerics={'n_er':31, 'n_enu':60})
        self.assertTrue(np.all(result.counts > 0))
        np.testing.assert_allclose(sum(result.combined_prediction.components.values()), result.counts, rtol=1e-14)
        d = result.combined_prediction.diagnostics
        self.assertAlmostEqual(d['accepted_domain_total_events'], result.counts.sum()+
            sum(d['outside_mean_window_events_low_high']), places=11)
        control = with_solar_nuclear_response(self.mean, response_file=TABLE, nuclear_model='kn_control')
        self.assertEqual(control.model.targets, self.exp.model.targets)
        self.assertNotEqual(control.physics_fingerprint, self.exp.physics_fingerprint)
        self.assertEqual(self.exp.model.interaction.describe().model_id, 'solar_sm_nuclear_table_v1')


if __name__ == '__main__':
    unittest.main()
