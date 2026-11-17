"""Physical normalization, source scaling, response ownership and solar Runtime contracts."""
from copy import deepcopy
from pathlib import Path
import unittest
import numpy as np
from cevns_pyeft.experiments.package_loader import load_experiment_package,read_package
from cevns_pyeft.experiments.runtime import predict_experiment
from cevns_pyeft.experiments.catalog import ExperimentCatalog
from cevns_pyeft.experiments.loader import load_experiment
from cevns_pyeft.experiments.solar_input import profile_errors,resource_errors
from cevns_pyeft.contracts import TheoryPoint,IncidentStateBatch
from cevns_pyeft.sources.composable import ScaledSource
from cevns_pyeft.theory.sm_coherent import klein_nystrand_squared

ROOT=Path(__file__).resolve().parents[1]
X=ROOT/'data/experiments/XENONnT/XENONnT_2024_SolarB8'
P=ROOT/'data/experiments/PandaX4T/PandaX4T_2024_US2'


class SolarSMContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.experiment=load_experiment_package(X)
        cls.data,cls.arrays=read_package(X)

    def test_kn_zero_recoil_and_monotonic_low_momentum(self):
        interaction=self.experiment.model.interaction;target=self.experiment.model.targets.isotopes[0]
        a=interaction.mass_numbers[0]
        values=klein_nystrand_squared(np.array([0.,.1,1.,3.]),target.kinematic_mass_GeV,a,
            radius_fm=interaction.radius_fm,skin_fm=interaction.skin_fm,hbarc_GeV_fm=interaction.hbarc_GeV_fm)
        self.assertEqual(values[0],1.)
        self.assertTrue(np.all(values>0) and np.all(np.diff(values)<0))

    def test_zero_recoil_weak_charge_absolute_units(self):
        interaction=self.experiment.model.interaction;target=self.experiment.model.targets.isotopes[0]
        energy=np.array([5.,10.]);point=TheoryPoint(sin2thetaW=.25)
        rho=IncidentStateBatch(energy,np.diag([1.,0.,0.]),'nu','test')
        ds=interaction.dsigma_dT(target=target,energy_MeV=energy,recoil_keV=0.,incident_state=rho,parameters=point)
        # At s2w=1/4 the proton term vanishes exactly; dσ/dT=GF²*m*N²/(4π).
        neutron=interaction.mass_numbers[0]-54
        expected=interaction.fermi_GeV_minus2**2*target.kinematic_mass_GeV*neutron**2/(4*np.pi)*interaction.inverse_GeV2_to_cm2*1e-6
        np.testing.assert_allclose(ds.values_cm2_per_keV,[expected,expected],rtol=2e-15)
        rho2=IncidentStateBatch(energy,np.diag([0.,0.,1.]),'nu','test_tau')
        same=interaction.dsigma_dT(target=target,energy_MeV=energy,recoil_keV=0.,incident_state=rho2,parameters=point)
        np.testing.assert_array_equal(ds.values_cm2_per_keV,same.values_cm2_per_keV)

    def test_elastic_endpoint_and_sm_disable(self):
        m=self.experiment.model;target=m.targets.isotopes[0];e=np.array([10.])
        rho=IncidentStateBatch(e,np.eye(3)/3,'nu','test')
        recoil=m.interaction.kinematics.maximum_recoil_keV(target,10.)
        ds=m.interaction.dsigma_dT(target=target,energy_MeV=e,recoil_keV=recoil,incident_state=rho,parameters=TheoryPoint())
        self.assertLess(float(ds.values_cm2_per_keV[0]),1e-52)
        zero=m.interaction.dsigma_dT(target=target,energy_MeV=e,recoil_keV=.8,incident_state=rho,parameters=TheoryPoint(include_sm=False))
        np.testing.assert_array_equal(zero.values_cm2_per_keV,[0.])

    def test_response_probabilities_and_distinct_native_bins(self):
        m=self.experiment.model;o=m.observation[0]
        probs=o.bin_probabilities(target=m.targets.isotopes[0],recoil_keV=np.array([.4,.51,1.,2.,5.1]),binning=m.binning,component_id='solar_B8_all_flavors')
        np.testing.assert_array_equal(probs.values[[0,4]],np.zeros((2,3)))
        self.assertTrue(np.all(probs.values.sum(axis=1)<=1))
        self.assertEqual(probs.included_selections,('official_early_release_joint_selection',))
        self.assertFalse(np.array_equal(o.native_cs2_edges,m.observation[1].native_cs2_edges))
        self.assertEqual(m.binning.axes[0].unit,'1')

    def test_natural_target_inventory_and_bahcall_normalization(self):
        m=self.experiment.model
        self.assertEqual(len(m.targets.isotopes),9)
        self.assertAlmostEqual(sum(t.nucleus_mass_kg*t.number_of_nuclei for t in m.targets.isotopes),1000.,places=10)
        integral=np.trapezoid(self.arrays['source_shape_per_MeV'],self.arrays['source_energy_MeV'])
        self.assertAlmostEqual(float(integral),.999986544,places=9)

    def test_runtime_components_and_flux_linearity(self):
        base=self.experiment
        registry=ExperimentCatalog(builtins=False).register(base.dataset_id,base.definition)
        doubled=load_experiment(base.dataset_id,definition=base.definition,registry=registry,resources=base.resource_catalog,
             components={'source':ScaledSource(base.model.source,2.)})
        n={'n_er':51,'n_enu':60}
        first=predict_experiment(base,numerics=n);second=predict_experiment(doubled,numerics=n)
        np.testing.assert_allclose(second.counts,2*first.counts,rtol=3e-14)
        np.testing.assert_allclose(sum(p.counts for p in first.detector_predictions.values()),first.counts,rtol=1e-14)
        self.assertEqual(len(first.combined_prediction.components),18)
        self.assertNotEqual(first.physics_fingerprint,second.physics_fingerprint)

    def test_corrupt_probabilities_and_pandax_missing_response_cannot_be_promoted(self):
        arrays=dict(self.arrays);arrays['response_SR0']=np.full_like(arrays['response_SR0'],.5)
        self.assertTrue(any('accepted probabilities' in e for e in resource_errors(self.data,arrays)))
        data,_=read_package(P);self.assertEqual(data['observable']['unit'],'keVnr')
        self.assertEqual(data['capabilities']['electron_spectrum']['status'],'BLOCKED')
        bad=deepcopy(data);bad['capabilities']['electron_spectrum']['status']='PASS'
        self.assertTrue(any('electron response' in e for e in profile_errors(bad)))


if __name__=='__main__':unittest.main()
