"""Explicit pilot/1 -> canonical/1 metadata migration for the CsI2021 fixture.

This is a migration adapter, not the general compiler from Task 08. It neither
loads an experiment nor writes files. All 105 numeric values and NPZ bytes stay
unchanged; roles follow the audited legacy consumers listed below.
"""
from copy import deepcopy

from cevns_pyeft.experiments.input_package import SCHEMA_VERSION, dependency_fingerprint


VARIABLE_UNITS = {
    'sns_fluence_legacy_v1': dict(F='cm^-2',r='neutrinos/species/POT',N_POT='POT',L_m='m',L_cm='cm'),
    'sns_michel_tabulation_legacy_v1': dict(E='MeV',m_mu='MeV',E_j='MeV',F='cm^-2',phi_l='cm^-2 MeV^-1',f_l='MeV^-1',mask='1'),
    'sns_prompt_line_v1': dict(E0='GeV',m_pi='GeV',m_mu='GeV',F='cm^-2',delta='inverse_energy'),
    'sns_fixed_state_v1': dict(rho_e='1',rho_mu='1',flavor_order='not_scalar'),
    'csi_target_inventory_v1': dict(w_i='1',A_i='1',u_kg='kg',u_GeV='GeV',Mdet='kg',m_i_kg='kg',m_i_GeV='GeV',N_i='nuclei'),
    'li2026_sm_left_v1': dict(P='GeV^-2',G_F='GeV^-2',s2='1',I3='1',C_BSM='GeV^(4-d)'),
    'li2026_matching_v1': {'c_i^N':'GeV^-2|GeV^-3','C_o':'GeV^(4-d)','M_io^N':'GeV^(d-6)|GeV^(d-7)','Ebar':'GeV','q0':'GeV','q2':'GeV^2','LECs':'not_scalar'},
    'elastic_kinematics_v1': dict(T='GeV',E='GeV',mA='GeV',q0='GeV',qabs='GeV',q2='GeV^2',b='GeV^-1',y='1'),
    'nuclear_np_polynomial_v1': {'W_X':'1','w_X,ab,k':'1','e_i':'1','y':'1','k':'1'},
    'li2026_R_W_kernel_v1': {'B_ij':'GeV^(p_i+p_j)','S_ij':'GeV^(p_i+p_j)','A_ij':'GeV^(p_i+p_j)','c_i^a':'GeV^-2|GeV^-3','R_X':'GeV^-2','W_X':'1','K':'GeV^-2','V':'GeV^-2'},
    'li2026_dsigma_v1': dict(rho='1',K='GeV^-2',mA='GeV',E='GeV',GEV_INV2_TO_CM2='cm^2/GeV^-2',T_keV='keV'),
    'csi_quenching_legacy_v1': dict(T_keV='keVnr',t='MeVnr',Eee_keV='keVee',q1='1',q2='MeV^-1',q3='MeV^-2',q4='MeV^-3'),
    'legacy_csi_gamma': dict(Eee='keVee',a0='keVee/PE',b0='keVee^-1',a='PE^-1',b='1',k='1',**{'lambda':'PE^-1'},x='PE',p='PE^-1',mean='PE',variance='PE^2'),
    'csi2021_logistic_legacy': dict(x='PE',a='1',b='PE^-1',c='PE',d='1',epsilon='1'),
    'legacy_component_acceptance': dict(acceptance_l='1',N_pre='events/nucleus/bin',N_i='nuclei',N_b='events/bin'),
    'legacy_csi2021_v1': {'Y_li':'events/nucleus/keV','phi_l':'cm^-2 MeV^-1','dsigma_li':'cm^2/keV','F_line':'cm^-2','T':'keVnr','x_j':'PE','m_i_kg':'kg/nucleus','h_li':'events/kg/PE','N_pre_li,b':'events/nucleus/bin','N_i':'nuclei','N_b':'events/bin','Trapz':'not_scalar'},
    'gaussian_two_pull_legacy_v1': dict(N_b='events/bin',edge='PE',s_b='counts/PE',observed_b='counts/PE',background_b='counts/PE',sigma_b='counts/PE',alpha='1',beta='1',sigma_alpha='1',sigma_beta='1',chi2='1'),
}
OUTPUT_UNITS = dict(zip(VARIABLE_UNITS, ('cm^-2','cm^-2 MeV^-1','not_scalar','not_scalar','not_scalar',
    'GeV^(4-d)','not_scalar','not_scalar','1','GeV^-2','cm^2/keV','keVee','PE^-1','1','events/bin','events/bin','1')))


def migrate_pilot(pilot):
    if pilot['package']['schema_version'] != 'cevns-experiment-input-pilot/1':
        raise ValueError('migration input must be pilot/1; canonical packages are not migrated twice')
    data = deepcopy(pilot)
    p = data['parameters']
    models = data['models']
    for key, item in p.items():
        item.update(role='direct_input', consumers=[], editable=True, affects_fingerprint=True,
                    fingerprint_scope='physical', legacy_fingerprint_effect='actual legacy consumer plus implementation/assembly fingerprints',
                    package_consumption_status='NOT_RUN',derivation=None)

    def consume(pid, mid, slot, source_ref, symbol, stage='runtime'):
        p[pid]['consumers'].append(dict(model_id=mid,slot=slot,stage=stage,
                                       code_evidence=[dict(source_ref=source_ref,symbol=symbol)]))

    for name in ('baseline_m','total_pot','yield_per_pot'):
        consume('source.'+name,'sns_fluence_legacy_v1',name,'source','_n_time_integrated_flux_cm2', 'resource_generation')
    for name in ('tabulation_min','tabulation_max','mask_min','mask_max','tabulation_nodes','interpolation'):
        p['source.'+name].update(role='runtime_control',fingerprint_scope='materialization')
        consume('source.'+name,'sns_michel_tabulation_legacy_v1',name,'source','build_neutrino_empirical_flux_sns','resource_generation')
    consume('constants.m_mu','sns_michel_tabulation_legacy_v1','muon_mass','source','_michel_nue_spectrum; _michel_numubar_spectrum','resource_generation')
    consume('source.fluence_per_species','sns_michel_tabulation_legacy_v1','fluence','source','build_neutrino_empirical_flux_sns','resource_generation')
    for pid, slot in (('source.fluence_per_species','fluence'),('source.prompt_energy','energy'),
                      ('constants.m_pi_charged','pion_mass'),('constants.m_mu','muon_mass')):
        consume(pid,'sns_prompt_line_v1',slot,'source','build_neutrino_empirical_flux_sns:muLine',
                'derivation' if pid.startswith('constants.') else 'runtime')
    for key in ('source.integration_min','source.integration_max'):
        consume(key,'legacy_csi2021_v1','energy_min' if key.endswith('min') else 'energy_max','recoil','integrate_recoil_yield')
    p['source.integration_min'].update(role='runtime_control',fingerprint_scope='numerics')
    for pid, slot in (('target.detector_mass','detector_mass'),('target.atomic_mass_kg','atomic_mass'),('constants.AMU_GEV','amu')):
        consume(pid,'csi_target_inventory_v1',slot,'assembly','assemble_csi2021')
    inactive = {'target.run_mass_metadata'}
    for isotope in ('Cs133','I127'):
        for field in ('Z','N','J','T','isotopic_fraction'):
            inactive.add('target.'+isotope+'.'+field)
        prefix='target.'+isotope+'.'
        for field,slot in (('A','mass_number'),('mass_fraction','mass_fraction'),('mass_kg','mass_kg'),('mass_GeV','mass_GeV')):
            consume(prefix+field,'csi_target_inventory_v1',slot,'assembly','assemble_csi2021; inventory_from_mass_fractions')
        consume(prefix+'mass_GeV','elastic_kinematics_v1','mass_GeV','kinematics','two_body_recoil_max_GeV; minimum_neutrino_energy_GeV')
        consume(prefix+'mass_GeV','li2026_dsigma_v1','mass_GeV','differential','differential_flavor_kernel_nn')
        consume(prefix+'mass_kg','legacy_csi2021_v1','isotope_mass_kg','folding','legacy_density_fold')
        consume(prefix+'nuclei','legacy_component_acceptance','nuclei','prediction','predict: final * target.number_of_nuclei')
        consume(prefix+'b','nuclear_np_polynomial_v1','oscillator_length','amplitude','flavor_kernel_onebody_li2026:y')
        consume('nuclear.'+isotope+'.exp_factor','nuclear_np_polynomial_v1','exp_factor','response_reader','ResponseW.W_np')
    for name in ('Sigma_ud','L9','L10','m_u','m_d'):
        inactive.add('lecs.'+name)
    for key in inactive:
        p[key].update(role='unused_snapshot' if key.startswith('lecs.') else 'reference_only',
                      consumers=[], editable=False,affects_fingerprint=False,fingerprint_scope='none',
                      legacy_fingerprint_effect='legacy whole-code/resource/model metadata may invalidate fingerprints; no numerical consumer')
    for key in p:
        if key.startswith('lecs.') and key not in inactive:
            consume(key,'li2026_matching_v1',key.split('.')[-1],'matching','left_to_ci')
    consume('lecs.m_N','li2026_R_W_kernel_v1','m_N','amplitude','compute_R_matrices:mN=lecs.m_N')
    consume('constants.alpha_em','li2026_matching_v1','alpha_em','matching','left_to_ci:alpha')
    for pid,slot in (('interaction.include_sm','include_sm'),('interaction.sin2thetaW','sin2thetaW'),('constants.G_F','G_F')):
        consume(pid,'li2026_sm_left_v1',slot,'differential','_sm_left_dim6')
    consume('constants.GEV_INV2_TO_CM2','li2026_dsigma_v1','conversion','cross_section','amplitude_kernel_to_dsigma_cm2_per_GeV')
    for index in range(1,5):
        consume('detector.quenching_q'+str(index),'csi_quenching_legacy_v1','q'+str(index),'differential','eee_quenching_csi')
    for key, slot in (('gamma_a','a0'),('gamma_b','b0')):
        consume('detector.'+key,'legacy_csi_gamma',slot,'differential','p_smearing_csi')
    for name in ('a','b','c','d'):
        consume('detector.efficiency_'+name,'csi2021_logistic_legacy',name,'detector','efficiency_csi2021')
    for name in ('mu','e','mub'):
        consume('detector.acceptance_'+name,'legacy_component_acceptance',name,'prediction','predict: observation.selection.acceptance')
    for key in p:
        if key.startswith('numerics.'):
            consume(key,'legacy_csi2021_v1',key.split('.')[-1],'prediction','predict; integrate_recoil_yield; legacy_density_fold')
            p[key].update(role='runtime_control',fingerprint_scope='numerics')
        if key.startswith('statistics.'):
            consume(key,'gaussian_two_pull_legacy_v1',key.split('.')[-1],'profiling','profile_gaussian_two_pull')
            p[key]['fingerprint_scope']='analysis'

    derivations = {
        'source.fluence_per_species': ('spherical_fluence.v1',['source.yield_per_pot','source.total_pot','source.baseline_m']),
        'source.prompt_energy': ('pion_line_energy.v1',['constants.m_pi_charged','constants.m_mu']),
        'source.integration_max': ('muon_dar_endpoint.v1',['constants.m_mu','constants.m_e']),
        'lecs.m_pi': ('identity.v1',['constants.m_pi_charged']),
    }
    # The electron mass is consumed by the endpoint derivation, not by matching.
    consume('constants.m_e','legacy_csi2021_v1','electron_mass','differential','emax_muon_dar_mev','derivation')
    for isotope in ('Cs133','I127'):
        prefix='target.'+isotope+'.'
        derivations[prefix+'mass_fraction']=('mass_fraction.v1',[prefix+'A','target.Cs133.A','target.I127.A'])
        derivations[prefix+'mass_GeV']=('product.v1',[prefix+'A','constants.AMU_GEV'])
        derivations[prefix+'mass_kg']=('product.v1',[prefix+'A','target.atomic_mass_kg'])
        derivations[prefix+'nuclei']=('nucleus_inventory.v1',['target.detector_mass',prefix+'mass_fraction',prefix+'mass_kg'])
    for key,(formula,refs) in derivations.items():
        p[key].update(role='derived',editable=False,
                      derivation=dict(formula_id=formula,formula=pilot['parameters'][key]['derivation'] or 'identity alias of input',
                                      input_refs=refs,read_only=True,dependency_fingerprint=dependency_fingerprint(data,refs,formula_id=formula)))
    # Audit completeness: no scalar is allowed to disappear into a name heuristic.
    missing=[key for key,item in p.items() if not item['consumers'] and item['role'] not in ('unused_snapshot','reference_only')]
    if missing:
        raise ValueError('unclassified actual consumers: '+str(missing))
    for key,model in models.items():
        model['parameter_refs']=[pid for pid,item in p.items() if any(c['model_id']==key for c in item['consumers'])]
        model.update(model_revision='1',formula_purpose='audit_only',contract=dict(
            binding_status='NOT_IMPLEMENTED',variable_units=VARIABLE_UNITS[key],output_unit=OUTPUT_UNITS[key],
            domain=dict(status='LEGACY_CODE_DERIVED',description=model['domain'],bounds=[]),
            normalization=dict(description=model['normalization'],additional_runtime_factors=[]),
            boundary=dict(policy_id=key+'.boundary.v1',description=model['boundary_behavior'])))
    models['sns_fluence_legacy_v1']['contract']['domain']['bounds']=[dict(variable='L_m',unit='m',lower=0,upper=None,lower_inclusive=False,upper_inclusive=False,parameter_ref='source.baseline_m')]
    models['legacy_csi_gamma']['contract']['domain']['bounds']=[dict(variable='Eee',unit='keVee',lower=0,upper=None,lower_inclusive=False,upper_inclusive=False,parameter_ref=None),dict(variable='x',unit='PE',lower=0,upper=None,lower_inclusive=False,upper_inclusive=False,parameter_ref=None)]

    resources=data['resources']['arrays']
    for key,item in resources.items():
        for axis in item['axes']:
            coordinate=axis.get('coordinate_ref') or axis.get('edges_ref')
            axis['unit']=resources[coordinate]['unit'] if coordinate else '1'
        if key.startswith('nuclear_'):
            kind,mid,slot='nuclear_coefficient','nuclear_np_polynomial_v1','coefficient'
        elif key.startswith('state_rho_'):
            kind,mid,slot='density_matrix','sns_fixed_state_v1','density'
        elif key.startswith('statistics_'):
            kind,mid,slot='statistic_density','gaussian_two_pull_legacy_v1',key.removeprefix('statistics_')
        elif key=='observable_pe_edges':
            kind,mid,slot='coordinate','legacy_csi2021_v1','edges'
        elif key=='source_energy_MeV':
            kind,mid,slot='coordinate','sns_michel_tabulation_legacy_v1','energy'
        else:
            kind,mid,slot='integrated_detector_fluence_density','sns_michel_tabulation_legacy_v1','continuum'
        item.update(role='direct_input',generation=None,consumers=[dict(model_id=mid,slot=slot)],
                    normalization=dict(description=item['normalization'],quantity_kind=kind,
                                       included_factors=['POT','yield','geometry'] if key.startswith('source_fluence_') else [],
                                       runtime_factors=[],runtime_authority='array'))
    resources['observable_pe_edges']['consumers'].append(dict(model_id='gaussian_two_pull_legacy_v1',slot='edges'))
    coordinate_refs=['source.tabulation_min','source.tabulation_max','source.tabulation_nodes']
    fluence_refs=[key for key in p if key.startswith('source.') and key not in ('source.prompt_energy','source.integration_min','source.integration_max')]+['constants.m_mu']
    for key in ('source_energy_MeV','source_fluence_e','source_fluence_mub'):
        refs=coordinate_refs if key=='source_energy_MeV' else fluence_refs
        mids=['sns_michel_tabulation_legacy_v1'] if key=='source_energy_MeV' else ['sns_michel_tabulation_legacy_v1','sns_fluence_legacy_v1']
        rrefs=[] if key=='source_energy_MeV' else ['source_energy_MeV']
        resources[key].update(role='materialized_derived_resource',generation=dict(parameter_refs=refs,model_refs=mids,resource_refs=rrefs,
            dependency_fingerprint=dependency_fingerprint(data,refs,mids,rrefs),method='current legacy SNS tabulation, no precision/order change'))
    data['source']['normalization']=dict(route='materialized_continuum_derived_prompt',continuum_authority='npz',
        prompt_weight_ref='source.fluence_per_species',runtime_continuum_factors=[],included_factors=['POT','yield','geometry'],
        notes=pilot['source']['normalization'])
    capability={
        'legacy_prediction':('AVAILABLE','LEGACY_ONLY','INTERNAL_REGRESSION_PASSED',[],'已有旧引擎预测，未获官方物理确认。'),
        'package_backed_prediction':('NOT_IMPLEMENTED','NOT_IMPLEMENTED','NOT_RUN',['pilot_runtime'],'Task 04–06 尚未完成。'),
        'fast':('AVAILABLE','LEGACY_ONLY','INTERFACE_EXISTS',['pilot_runtime'],'已有 interface_kernel_v1；package-only Fast 未测试。'),
        'legacy_approximate_statistics':('AVAILABLE','LEGACY_ONLY','INTERNAL_REGRESSION_PASSED',['statistics_semantics'],'旧 Gaussian 双 pull 可执行；数据语义限制保留。'),
        'official_likelihood':('NOT_IMPLEMENTED','BLOCKED','NOT_RUN',['official_experiment_sources','statistics_semantics'],'官方 likelihood 和数据语义待证据。'),
        'general_antineutrino_EFT':('RESTRICTED','BLOCKED','NOT_RUN',['antineutrino_kernel'],'共享 nu/antinu 核不能宣称一般 EFT 审核完成。'),
        'scientific_release':('NOT_IMPLEMENTED','BLOCKED','NOT_RUN',['official_experiment_sources','eft_primary_conventions','nuclear_source_audit','antineutrino_kernel','statistics_semantics','source_endpoint','detector_validity'],'DRAFT/PARTIAL；技术 PASS 不授予科学接受。'),
    }
    data['capabilities']={key:dict(engine_support=engine,readiness=readiness,legacy_evidence=evidence,
        package_runtime_validation='NOT_RUN',scientific_validation='BLOCKED' if readiness=='BLOCKED' else 'DRAFT',
        human_approval='NOT_REVIEWED',blocker_refs=blockers,notes=notes)
        for key,(engine,readiness,evidence,blockers,notes) in capability.items()}
    data['package']['schema_version']=SCHEMA_VERSION
    data['engine_compatibility']=dict(engine_id='CEvNS-pyEFT',core_api_version=1,
        contract_versions=dict(source='1',interaction='1',observation='1'),binding_task='Task03',status='DECLARED_NOT_BOUND')
    data['legacy_spec']=dict(path='experiment.yaml',status='legacy_compatibility',package_authority='experiment.input.yaml',
        runtime_authority='existing_python_definition',retirement_task='Task09',conflicts=[
            'historical fast_validated is not package-only Fast validation',
            'historical statistics blocked means authoritative provenance missing, not absence of executable legacy Gaussian',
            'old phase/reference/run paths remain historical and cannot grant current human approval'])
    data['provenance']['migration']=dict(from_version=pilot['package']['schema_version'],to_version=SCHEMA_VERSION,
        numeric_values_changed=False,npz_bytes_changed=False,
        machine_authority_decision='normalized continuum NPZ is runtime authority; upstream scalars are generation inputs; prompt F and target quantities are verified read-only derivations')
    data['provenance']['standards']['schema']='cevns_pyeft/experiments/input_package.schema.json; JSON-compatible YAML 1.2'
    data['provenance']['standards']['actual_schema_check']='Draft202012Validator plus input_package semantic/resource/derived/MD checks; no model binding or Runtime loading'
    return data
