"""Closed solar-profile file contract; NumPy-only and no runtime model imports."""
import numpy as np

PROFILE='solar_b8_sm_v1'
SOURCE='solar_b8_flux_v1'
TARGET='explicit_target_inventory_v1'
NUCLEAR='klein_nystrand_v1'
INTERACTION='coherent_sm_kn_v1'


def profile_errors(data):
    errors=[];cfg=data['assembly'];params=data['parameters'];arrays=data['resources']['arrays'];models=data['models']
    def check(ok,text):
        if not ok:errors.append('solar assembly: '+text)
    def fields(obj,keys):check(set(obj)==set(keys),'unexpected/missing fields '+str(sorted(set(obj)^set(keys))))
    fields(cfg['source'],['energy_ref','shape_ref'])
    fields(cfg['target'],['mass_number_ref','atomic_mass_ref','number_fraction_ref','exposures_ref'])
    fields(cfg['interaction'],['model_id'])
    fields(cfg['detector'],['mode','model_id','run_ids'])
    fields(cfg['numerics'],['slow']);fields(cfg['numerics']['slow'],['n_er','n_enu'])
    check(not cfg['statistics'],'no inference model declared by SM forward profile')
    mode=cfg['detector']['mode'];check(mode in ('xenon_basis','recoil_acceptance'),'unknown detector mode')
    detector='xenon_mono_basis_v1' if mode=='xenon_basis' else 'recoil_efficiency_projection_v1'
    expected={SOURCE,TARGET,NUCLEAR,INTERACTION,detector,PROFILE}
    check(set(models)==expected,'exact component model set differs')
    check(cfg['interaction']['model_id']==INTERACTION and cfg['detector']['model_id']==detector,'component identities differ')
    check(all(m['binding_status'] in ('BOUND_AND_TESTED','BOUND_UNVERIFIED') for m in models.values()),'nonexecutable component binding')
    check(set(arrays)=={ref for m in models.values() for ref in m['resource_refs']},'unconsumed/undeclared array')
    units={'source.total_flux':'cm^-2 s^-1','target.anchor_mass_kg':'kg','target.Z':'1','constants.avogadro':'mol^-1',
           'constants.amu_GeV':'GeV/u','constants.electron_mass_GeV':'GeV','constants.G_F':'GeV^-2',
           'constants.hbarc_GeV_fm':'GeV fm','constants.GeV_inverse2_to_cm2':'cm^2 GeV^2',
           'constants.seconds_per_year':'s/yr','nuclear.radius_fm':'fm','nuclear.skin_fm':'fm',
           'interaction.sin2thetaW':'1','interaction.include_sm':'boolean','numerics.n_er':'1','numerics.n_enu':'1'}
    check(set(params)==set(units),'unconsumed/undeclared parameter')
    for key,unit in units.items():
        p=params.get(key,{})
        check(p.get('value') is not None and p.get('unit')==unit and p.get('role') not in ('reference_only','unused_snapshot'),'parameter '+key)
    check(params['target.Z']['value']==54,'this natural-xenon profile requires Z=54')
    check(0<=params['interaction.sin2thetaW']['value']<=1,'weak angle outside [0,1]')
    for key in set(units)-{'interaction.sin2thetaW','interaction.include_sm'}:
        check(params[key]['value']>0,'positive parameter required: '+key)
    for key in ('numerics.n_er','numerics.n_enu'):
        check(type(params[key]['value']) is int and params[key]['value']>=2,'integer quadrature count: '+key)
    check(cfg['numerics']['slow']=={'n_er':'numerics.n_er','n_enu':'numerics.n_enu'},'numerical reference mapping')
    check(cfg['source']=={'energy_ref':'source_energy_MeV','shape_ref':'source_shape_per_MeV'},'source references')
    check(cfg['target']=={'mass_number_ref':'target_mass_number','atomic_mass_ref':'target_atomic_mass_u',
                         'number_fraction_ref':'target_number_fraction','exposures_ref':'run_exposures_tyr'},'target references')
    for key,unit in [('source_energy_MeV','MeV'),('source_shape_per_MeV','MeV^-1'),('target_mass_number','1'),
                     ('target_atomic_mass_u','u'),('target_number_fraction','1'),('run_exposures_tyr','t yr')]:
        check(key in arrays and arrays[key]['unit']==unit,'array unit/ref '+key)
    runs=cfg['detector']['run_ids']
    check(runs==(['SR0','SR1'] if mode=='xenon_basis' else ['US2']),'run identity/order')
    check(arrays['run_exposures_tyr']['shape']==[len(runs)],'exposure run shape')
    check(data['capabilities']['signal']['status'] in ('PARTIAL','PASS'),'signal unavailable')
    check(all(data['capabilities'][name]['status'] in ('BLOCKED','NOT_APPLICABLE','NOT_RUN') for name in ('fast','legacy_statistics')),'unsupported inference/Fast enabled')
    if mode=='xenon_basis':
        check(data['observable']['unit']=='1' and data['observable']['bin_count']==3,'run-specific cS2 ordinal axis required')
        for key,shape in [('response_SR0',[16,10,10,3]),('response_SR1',[16,10,10,3]),
                          ('response_energy_keV',[16]),('response_Ly',[10]),('response_Qy',[10]),
                          ('yield_energy_keV',[501]),('yield_Ly_median',[501]),('yield_Qy_median',[501]),
                          ('cs2_edges_SR0',[4]),('cs2_edges_SR1',[4])]:
            check(key in arrays and arrays[key]['shape']==shape,'response shape/ref '+key)
    else:
        check(data['observable']['unit']=='keVnr','PandaX diagnostic must be true recoil')
        check(data['capabilities']['electron_spectrum']['status']=='BLOCKED','missing electron response cannot be promoted')
    return errors


def resource_errors(data,arrays):
    errors=[]
    def check(ok,text):
        if not ok:errors.append('solar resources: '+text)
    e=arrays['source_energy_MeV'];shape=arrays['source_shape_per_MeV']
    check(e.ndim==1 and shape.shape==e.shape and len(e)>2 and np.all(np.diff(e)>0) and np.all(shape>=0),'invalid nonnegative source table')
    f=arrays['target_number_fraction'];a=arrays['target_mass_number'];m=arrays['target_atomic_mass_u']
    check(a.shape==m.shape==f.shape==(9,) and np.isclose(f.sum(),1,rtol=0,atol=1e-12) and np.all(f>0),'natural Xe isotope inventory')
    check(np.array_equal(a,[124,126,128,129,130,131,132,134,136]),'natural Xe mass-number order')
    check(np.all(arrays['run_exposures_tyr']>0),'exposure must be positive')
    if data['assembly']['detector']['mode']=='xenon_basis':
        for run in ['SR0','SR1']:
            probabilities=arrays['response_'+run]
            check(np.all(probabilities>=0) and np.all(probabilities.sum(axis=-1)<=1+1e-10),'accepted probabilities '+run)
            check(np.all(np.diff(arrays['cs2_edges_'+run])>0),'native cS2 edges '+run)
        for key in ['response_energy_keV','response_Ly','response_Qy','yield_energy_keV']:
            check(np.all(np.diff(arrays[key])>0),'response coordinate '+key)
    else:
        check(np.all(np.diff(arrays['efficiency_energy_keV'])>0) and np.all((arrays['efficiency']>=0)&(arrays['efficiency']<=1)),'efficiency coordinate/probability')
    return errors
