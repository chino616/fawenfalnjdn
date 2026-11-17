"""Solar ee NSI source, shared-amplitude, state-aware kernel and joint contracts."""
from dataclasses import replace
from pathlib import Path
import hashlib,json
import numpy as np
import pytest
from cevns_pyeft.contracts import IncidentStateBatch,TheoryPoint,StateParameters
from cevns_pyeft.contracts.modules import UnsupportedCapabilityError
from cevns_pyeft.experiments.solar_nsi import load_solar_nsi,INPUT_DIRECTORY
from cevns_pyeft.experiments.solar_singlebin import load_singlebin
from cevns_pyeft.experiments.runtime import predict_experiment,compile_experiment,evaluate_experiment
from cevns_pyeft.sources.solar_msw import SolarMSW,SolarDiagonalState
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point,monomials,couplings
from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
from cevns_pyeft.statistics.solar_nsi import SolarNSIJoint
ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def setup():
    experiments=[];kernels=[];shared=None
    for s in ['PandaX_paired','PandaX_US2','XENONnT']:
        e=load_solar_nsi(s,root=ROOT,interaction=shared);shared=e.model.interaction
        k=compile_experiment(e,numerics={'n_er':41,'n_enu':64});experiments.append(e);kernels.append(k)
    return tuple(experiments),tuple(kernels),SolarNSIJoint(tuple(experiments),tuple(kernels))


def test_actual_profile_and_derived_neutron_input():
    directory=ROOT/INPUT_DIRECTORY;card=json.loads((directory/'nsi.input.json').read_text(encoding='utf8'))
    for name,ref in card['files'].items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==ref['sha256']
        table=np.loadtxt(directory/name);raw=np.loadtxt(directory/ref['production_raw']);struct=np.loadtxt(directory/ref['structure_raw'])
        assert table.shape==(1000,4)
        np.testing.assert_allclose(table[:,1],10**raw[:,2],rtol=1e-14)
        rows=np.searchsorted(struct[:,0],raw[:,0]);np.testing.assert_allclose(table[:,2],struct[rows,1]-table[:,1],rtol=2e-14,atol=1e-12)
        np.testing.assert_array_equal(table[:,3],raw[:,8])


@pytest.mark.parametrize('uv,dv',[(-.5,0.),(0.,0.),(.5,0.),(-17.3,15.7)])
def test_pee_against_native_radial_integral_and_2x2_hamiltonian(setup,uv,dv):
    m=setup[0][0].model.state_model;p=m.profile;energy=np.array([.1,2.,5.,10.,15.])
    # Independent eigenvector construction, using a numerical 2x2 Hamiltonian
    # and the original1000 radial nodes; not the production quadrature code.
    factor=7.6324662e-14
    c13=np.cos(m.theta13)**2;s13=np.sin(m.theta13)**2;s12=np.sin(m.theta12)**2
    expected=[]
    for E in energy:
        potential=factor*(p[:,1]+uv*(2*p[:,1]+p[:,2])+dv*(p[:,1]+2*p[:,2]))
        A=2*E*1e6*c13*potential
        diag=-m.dm21*np.cos(2*m.theta12)+A;off=np.full_like(diag,m.dm21*np.sin(2*m.theta12))
        H=np.zeros((len(p),2,2));H[:,0,0]=diag;H[:,1,1]=-diag;H[:,0,1]=H[:,1,0]=off
        eigenvectors=np.linalg.eigh(H)[1]
        w1=abs(eigenvectors[:,0,0])**2;w2=abs(eigenvectors[:,0,1])**2
        probability=c13*c13*(w1*(1-s12)+w2*s12)+s13*s13
        expected.append(np.trapezoid(probability*p[:,3],p[:,0])/np.trapezoid(p[:,3],p[:,0]))
    np.testing.assert_allclose(m.pee(energy,uv,dv),expected,rtol=0,atol=2e-4)


def test_vacuum_limit_bounds_and_parameter_dependent_state(setup):
    m=setup[0][0].model.state_model
    vacuum=np.cos(m.theta13)**4*(1-.5*np.sin(2*m.theta12)**2)+np.sin(m.theta13)**4
    assert m.pee(np.array([0.]))[0]==pytest.approx(vacuum,abs=1e-14)
    u=np.linspace(-80,80,31);d=np.linspace(45,-45,31);values=m.pee(np.array([1.,5.,15.]),u,d)
    low,high=m.probability_bounds;assert np.all(values>=low-1e-14) and np.all(values<=high+1e-14)
    assert np.max(abs(m.pee(np.array([5.,15.]),-.5,0)-m.pee(np.array([5.,15.]),.5,0)))>.2
    fixed=replace(m,propagation='sm_fixed')
    np.testing.assert_array_equal(fixed.pee(np.array([5.,15.]),-.5,0),fixed.pee(np.array([5.,15.]),.5,0))
    state=m(np.array([5.,15.]),parameters=StateParameters({'epsilon_ee_uV':-.5,'epsilon_ee_dV':0.}))
    np.testing.assert_allclose(np.trace(state.rho,axis1=-2,axis2=-1),1.,rtol=0,atol=1e-14)
    assert state.parameter_dependencies==('epsilon_ee_uV','epsilon_ee_dV')


@pytest.mark.parametrize('uv,dv',[(0,0),(.3,-.1),(-17.3,15.7)])
def test_vectorized_nuclear_coefficients_match_original_scalar_api(setup,uv,dv):
    m=setup[0][1].model;i=m.interaction;energy=np.array([2.,7.,11.3,16.56,27.])
    for t in m.targets.isotopes:
        state=IncidentStateBatch(energy,np.diag([.31,.13,.56]),'nu','test')
        args=dict(target=t,energy_MeV=energy,recoil_keV=1.2,incident_state=state,parameters=nsi_point(uv,dv))
        np.testing.assert_allclose(i.dsigma_dT(**args).values_cm2_per_keV,i._legacy.dsigma_dT(**args).values_cm2_per_keV,rtol=2e-9,atol=2e-54)
        alternative=IncidentStateBatch(energy,np.diag([.31,.6,.09]),'nu','equivalent_mu_tau')
        np.testing.assert_array_equal(i.dsigma_dT(**args).values_cm2_per_keV,i.dsigma_dT(**dict(args,incident_state=alternative)).values_cm2_per_keV)


def test_old_sm_and_invalid_flavor_or_inconsistent_state_rejected(setup):
    old=load_singlebin('PandaX_US2',root=ROOT)
    with pytest.raises(ValueError,match='does not consume state parameters'):
        predict_experiment(old,parameters=nsi_point(.2,0),numerics={'n_er':5,'n_enu':5})
    with pytest.raises(UnsupportedCapabilityError):
        predict_experiment(old,parameters=replace(nsi_point(.2,0),state=StateParameters()),numerics={'n_er':5,'n_enu':5})
    e=setup[0][1]
    with pytest.raises(ValueError,match='same point'):
        predict_experiment(e,parameters=replace(nsi_point(.2,0),state=StateParameters({'epsilon_ee_uV':0.,'epsilon_ee_dV':0.})))
    with pytest.raises(UnsupportedCapabilityError):couplings(TheoryPoint({(6,1,'u'):np.eye(3)}))
    with pytest.raises(UnsupportedCapabilityError):couplings(TheoryPoint({(6,2,'u'):np.diag([1.,0.,0.])}))


def test_vectorial_diagonal_state_checks_every_energy():
    e=np.array([5.,10.]);rho=np.array([np.diag([.3,.3,.4]),np.diag([.4,.2,.4])],complex)
    valid=SolarDiagonalState(e,rho,'nu','test');assert not valid.rho.flags.writeable
    for change in ['negative','offdiagonal','trace','imaginary']:
        bad=rho.copy()
        if change=='negative':bad[1,0,0]=-.1;bad[1,1,1]=.7
        if change=='offdiagonal':bad[1,0,1]=.01
        if change=='trace':bad[1,0,0]=.5
        if change=='imaginary':bad[1,0,0]+=.01j
        with pytest.raises(ValueError):SolarDiagonalState(e,bad,'nu','invalid')


def test_three_samples_kernel_slow_and_joint_runtime_agree(setup):
    exps,kernels,joint=setup;point=nsi_point(.3,-.1);chi=0.
    for e,k in zip(exps,kernels):
        fast=predict_experiment(e,parameters=point,backend='fast',kernel=k,numerics=k.record['numerics'])
        slow=predict_experiment(e,parameters=point,numerics={'n_er':41,'n_enu':120})
        np.testing.assert_allclose(fast.counts,slow.counts,rtol=.002,atol=3e-4)
        chi+=evaluate_experiment(e,fast).chi2
    assert chi==pytest.approx(joint.chi2(.3,-.1),abs=1e-11)
    signals=joint.signals(.3,-.1);A=np.vstack([np.diag(signals/joint.sigma),np.diag(1/joint.pull)])
    residual=np.r_[(joint.D-signals)/joint.sigma,np.zeros(3)];a=np.linalg.lstsq(A,residual,rcond=None)[0]
    assert np.sum((A@a-residual)**2)==pytest.approx(chi,abs=1e-11)
    np.testing.assert_allclose(joint.sigma,[1.2985,27.975,3.9483],rtol=0,atol=1e-12)


def test_cache_round_trip_corruption_stale_and_explicit_state_rebind(setup,tmp_path):
    e=setup[0][1];k=setup[1][1];path=tmp_path/'kernel.npz';k.save(path);restored=SolarNSIKernel.load(path)
    np.testing.assert_array_equal(restored.values,k.values)
    fixed=load_solar_nsi('PandaX_US2',root=ROOT,propagation='sm_fixed')
    with pytest.raises(ValueError,match='stale/wrong'):
        predict_experiment(fixed,parameters=nsi_point(.3,-.1),backend='fast',kernel=k,numerics=k.record['numerics'])
    rebound=k.rebind_state(fixed)
    p=predict_experiment(fixed,parameters=nsi_point(.3,-.1),backend='fast',kernel=rebound,numerics=k.record['numerics'])
    assert p.counts[0]>0
    changed=replace(e,model=replace(e.model,exposure_tyr=2*e.model.exposure_tyr))
    with pytest.raises(ValueError,match='cannot rebind'):k.rebind_state(changed)
    with np.load(path,allow_pickle=False) as a:arrays={name:a[name] for name in a.files}
    arrays['values']=arrays['values'].copy()
    index=np.unravel_index(np.argmax(abs(arrays['values'])),arrays['values'].shape)
    arrays['values'][index]*=1.01;np.savez_compressed(path,**arrays)
    with pytest.raises(ValueError,match='corrupted'):SolarNSIKernel.load(path)


def test_full_msw_rate_is_not_a_fixed_state_quadratic(setup):
    e,k=setup[0][1],setup[1][1]
    fixed=load_solar_nsi('PandaX_US2',root=ROOT,propagation='sm_fixed');fk=k.rebind_state(fixed)
    def rate(exp,kernel,u):return predict_experiment(exp,parameters=nsi_point(u,0),backend='fast',kernel=kernel,numerics=kernel.record['numerics']).counts[0]
    for exp,kernel,should_be_quadratic in [(e,k,False),(fixed,fk,True)]:
        lo,center,hi=[rate(exp,kernel,u) for u in [-.5,0,.5]]
        polynomial=center+(hi-lo)/1.*.25+((hi+lo)/2-center)/(.5**2)*(.25**2)
        error=abs(polynomial-rate(exp,kernel,.25))
        assert error<1e-10 if should_be_quadratic else error>1e-3


def test_tail_profile_interval_and_certified_full_plane_bound(setup):
    joint=setup[2];u=np.array([0.,.3,-.5]);d=np.array([.178,-.1,.7])
    profile=joint.chi2(u,d,'profile_bounds')
    for mode in ['zero','unit','flat_sensitivity']:assert np.all(profile<=joint.chi2(u,d,mode)+1e-12)
    domain=joint.certified_domain();center=np.array(domain['center']);matrix=np.array(domain['transform'])
    angles=np.linspace(0,2*np.pi,17);z=1.01*np.array([np.cos(angles),np.sin(angles)]);p=center[:,None]+matrix@z
    assert np.all(joint.chi2(p[0],p[1])>domain['excluded_chi2_level'])
    # At a destructive-interference point the non-e flux must remain. There is
    # no basis for replacing the physical ee-only model by universal NSI.
    sm=joint.signals(0,0);s=joint.signals(0,.178)
    assert np.all(s>.6*sm)
