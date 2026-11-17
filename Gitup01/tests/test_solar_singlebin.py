"""Independent physical checks, data isolation and statistical identity guards."""
from dataclasses import replace
from pathlib import Path
import json
import subprocess
import sys
from unittest.mock import patch
import numpy as np
import pytest
from scipy.optimize import minimize_scalar

from cevns_pyeft.contracts import IncidentStateBatch, TheoryPoint
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
from cevns_pyeft.experiments.solar_singlebin import load_singlebin, INPUT_DIRECTORY, SAMPLES
from cevns_pyeft.statistics.solar_singlebin import profile

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def models():
    return {sample:load_singlebin(sample, root=ROOT) for sample in SAMPLES}


@pytest.mark.parametrize('signal,observed,sigma', [(0.,3.5,1.3),(2.4,3.5,1.3),(44.3,75.,28.),(11.2,10.7,3.95),(200.,75.,28.)])
def test_analytic_pull_matches_independent_optimizer(signal, observed, sigma):
    objective = lambda a: ((observed-(1+a)*signal)/sigma)**2+(a/.12)**2
    numeric = minimize_scalar(objective, bracket=(-1.,0.,1.)) if signal==0 else minimize_scalar(objective)
    actual = profile(signal, observed, sigma)
    assert actual.chi2 == pytest.approx(numeric.fun, rel=1e-11, abs=1e-13)
    assert actual.alpha == pytest.approx(numeric.x, abs=1e-7)
    assert actual.chi2 == pytest.approx(actual.chi2_data+actual.chi2_nuisance)


def test_reference_arithmetic_is_not_a_forward_prediction():
    result = sum(profile(*row).chi2 for row in [(2.4,3.5,1.3),(44.3,75.,28.),(11.2,10.7,3.95)])
    assert result == pytest.approx(1.857171830289251, abs=1e-13)


@pytest.mark.parametrize('args', [(-1.,3.,1.),(2.,3.,0.),(2.,float('nan'),1.),(2.,3.,1.,0.)])
def test_invalid_statistical_inputs_rejected(args):
    with pytest.raises(ValueError):
        profile(*args)


def test_natural_xe_counts_use_full_denominator_and_no_renormalization(models):
    e = models['PandaX_US2']
    original = np.loadtxt(ROOT/INPUT_DIRECTORY/'xe_isotopes.txt')
    mean = original[:,1]@original[:,2]
    for target in e.model.targets.isotopes:
        row = original[original[:,0]==int(target.isotope_id[2:])][0]
        assert target.number_of_nuclei == pytest.approx(1e6*6.02214076e23*row[2]/mean,rel=1e-14)
    assert e.model.targets.composition_record['original_number_fraction_coverage'] == pytest.approx(.998158)
    assert e.model.targets.detector_mass_kg < 1000.


def test_quadratic_vectorization_matches_original_api_and_endpoint(models):
    interaction=models['PandaX_US2'].model.interaction
    for target in models['PandaX_US2'].model.targets.isotopes:
        for recoil in (.3,1.23,2.7):
            energy=np.array([2.,7.,11.3,16.56,27.])
            state=IncidentStateBatch(energy,np.diag([1.,0.,0.]),'nu','independent_test')
            args=dict(target=target,energy_MeV=energy,recoil_keV=recoil,incident_state=state,parameters=TheoryPoint(sin2thetaW=.23857))
            actual=interaction.dsigma_dT(**args).values_cm2_per_keV
            expected=interaction._legacy.dsigma_dT(**args).values_cm2_per_keV
            np.testing.assert_allclose(actual,expected,rtol=3e-11,atol=2e-54)
        energy=np.array([16.56]);state=IncidentStateBatch(energy,np.eye(3)/3,'nu','endpoint')
        recoil=interaction.kinematics.maximum_recoil_keV(target,energy[0])
        args=dict(target=target,energy_MeV=energy,recoil_keV=recoil,incident_state=state,parameters=TheoryPoint(sin2thetaW=.23857))
        endpoint=interaction.dsigma_dT(**args).values_cm2_per_keV
        assert np.all(np.isfinite(endpoint)) and np.all(endpoint>=0)
        # The old scalar API can reject its own roundoff-sized negative kernel
        # at the exact even-Xe endpoint. Compare that API strictly inside support;
        # retain the exact endpoint nonnegativity check without changing its core.
        args['recoil_keV']=recoil*(1-1e-5)
        np.testing.assert_allclose(interaction.dsigma_dT(**args).values_cm2_per_keV,
                                   interaction._legacy.dsigma_dT(**args).values_cm2_per_keV,rtol=1e-8,atol=2e-54)
    with pytest.raises(UnsupportedCapabilityError):
        interaction.validate(models['PandaX_US2'].model.targets,TheoryPoint(wc_triplets={(6,1,'u'):np.eye(3)}))


def test_total_efficiency_independent_reextraction_agrees_with_us2_original():
    original=np.loadtxt(ROOT/'data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_us2_acceptance_2407.10892v3.txt')
    fresh=np.loadtxt(ROOT/INPUT_DIRECTORY/'pandax_us2_total.txt')
    assert fresh.shape==original.shape==(99,2)
    np.testing.assert_allclose(fresh,original,rtol=3e-8,atol=1e-9)


def test_no_legacy_inputs_are_read_by_singlebin_runtime():
    old=ROOT/'data/experiments'
    original=Path.open
    def guarded(path,*args,**kwargs):
        if Path(path).resolve().is_relative_to(old):
            raise AssertionError('singlebin tried reading old multibin data: '+str(path))
        return original(path,*args,**kwargs)
    with patch.object(Path,'open',guarded):
        e=load_singlebin('PandaX_US2',root=ROOT)
        p=predict_experiment(e,numerics={'n_er':9,'n_enu':10})
        assert p.counts.shape==(1,)
        assert p.counts[0]>40  # original Ne mapping retained only about 26; no extra ROI window
        assert evaluate_experiment(e,p).chi2>=0
    paths={p.resolve() for p in e.resolved_resources.values()}
    assert all(not path.is_relative_to(old) for path in paths)


def test_xenon_tail_is_bounded_and_partial_likelihood_rejected(models):
    e=models['XENONnT'];obs=e.model.observation
    assert 2.76<obs.verified_upper<2.78
    with pytest.raises(ValueError,match='no implicit extrapolation'):
        obs.known_acceptance(np.array([3.]))
    p=predict_experiment(e,numerics={'n_er':11,'n_enu':20})
    d=p.combined_prediction.diagnostics
    assert not d['coverage_complete']
    assert d['full_interval_events'][1]>d['full_interval_events'][0]>0
    with pytest.raises(ValueError,match='partial acceptance'):
        evaluate_experiment(e,p)
    flat=load_singlebin('XENONnT',root=ROOT,tail_mode='flat_sensitivity')
    pf=predict_experiment(flat,numerics={'n_er':11,'n_enu':20})
    expected=d['verified_domain_events']+obs.efficiency[-1]*d['unknown_tail_max_events_epsilon_le_1']
    assert pf.counts[0]==pytest.approx(expected,rel=1e-13)
    assert flat.analysis_fingerprint!=e.analysis_fingerprint
    assert pf.combined_prediction.diagnostics['claim']=='project_flat_tail_sensitivity'
    assert evaluate_experiment(flat,pf).chi2>=0


def test_multibin_runtime_does_not_read_singlebin_inputs_and_mixed_statistics_rejected(models):
    from cevns_pyeft.experiments.package_loader import load_experiment_package
    from cevns_pyeft.experiments.solar_mean_map import with_pandax_mean_map
    from cevns_pyeft.experiments.solar_nuclear import with_solar_nuclear_response
    original=Path.open
    def guarded(path,*args,**kwargs):
        if Path(path).resolve().is_relative_to(ROOT/INPUT_DIRECTORY):
            raise AssertionError('multibin tried reading singlebin data')
        return original(path,*args,**kwargs)
    with patch.object(Path,'open',guarded):
        directory=ROOT/'data/experiments/PandaX4T/PandaX4T_2024_US2'
        multi=with_solar_nuclear_response(with_pandax_mean_map(load_experiment_package(directory),
                    qy_file=directory/'detector/pandax_qy_nominal.txt'),response_file=ROOT/'data/responses/responses_all.json')
        prediction=predict_experiment(multi,numerics={'n_er':9,'n_enu':10})
        assert prediction.counts.shape==(8,)
    with pytest.raises(ValueError,match='identity mismatch'):
        evaluate_experiment(models['PandaX_US2'],prediction)
    single=predict_experiment(models['PandaX_US2'],numerics={'n_er':9,'n_enu':10})
    with pytest.raises(ValueError,match='identity mismatch'):
        evaluate_experiment(multi,single)


def test_both_explicit_entry_points_and_compatibility_gateway_have_separate_help():
    single=subprocess.run([sys.executable,'-B','tools/run_solar_b8_sm_benchmark.py','--analysis','singlebin','--help'],cwd=ROOT,capture_output=True,text=True)
    multi=subprocess.run([sys.executable,'-B','tools/run_solar_b8_multibin_benchmark.py','--help'],cwd=ROOT,capture_output=True,text=True)
    assert single.returncode==multi.returncode==0
    assert '--xenon-tail' in single.stdout and '--xenon-tail' not in multi.stdout
    assert '--sample' in single.stdout


def test_wrong_analysis_output_root_rejected_before_creating_any_file():
    wrong_single=ROOT/'outputs/solar_b8_sm/should_not_create_singlebin_test'
    wrong_multi=ROOT/'outputs/solar_b8_singlebin/should_not_create_multibin_test'
    for script,destination in [('tools/run_solar_b8_singlebin_benchmark.py',wrong_single),
                               ('tools/run_solar_b8_multibin_benchmark.py',wrong_multi)]:
        assert not destination.exists()
        for output_arguments in [ ['--output',str(destination)], ['--output='+str(destination)] ]:
            result=subprocess.run([sys.executable,'-B',script,*output_arguments],cwd=ROOT,capture_output=True,text=True)
            assert result.returncode!=0 and 'separate from' in result.stderr
            assert not destination.exists()
