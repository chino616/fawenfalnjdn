"""Explicit legacy acquisition adapter; output always uses the common compiler.

Run one active dataset at a time, before retiring its old definition. This tool
does not discover papers, scan backups, approve science, or activate datasets.
"""
from pathlib import Path
import argparse
import ast
from dataclasses import asdict
import hashlib
import json
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
from cevns_pyeft.experiments.loader import load_experiment
from cevns_pyeft.experiments.input_package import dependency_fingerprint
from cevns_pyeft.experiments.generic_input import binding_contracts
from cevns_pyeft.experiments.package_compiler import write_package


def acquire(dataset_id, root):
    definition=BUILTIN_CATALOG.definition(dataset_id)
    physical=definition.physical
    if type(definition.prepare).__module__.endswith(('package_profiles','package_loader')):
        raise ValueError('dataset already package-backed; use its IR/three-file compiler check')
    model=load_experiment(dataset_id,resources=root).model
    profile='deterministic_pe_legacy_v1' if hasattr(physical,'pe_per_keV') else 'observed_gaussian_legacy_v1'
    source_mid='integrated_fluence_components_v1';target_mid='explicit_target_inventory_v1'
    nuclear_mid='nuclear_polynomial_arrays_v1';interaction_mid='li2026_package_interaction_v1'
    eff_mid='legacy_efficiency_curve_v1'
    stat_mid='gaussian_one_pull_legacy_v1' if definition.statistics.kind=='gaussian_one_pull' else 'asymmetric_irls_legacy_v1'
    params,arrays,metadata,models={},{},{},{}
    contracts=binding_contracts()
    for mid in [source_mid,target_mid,nuclear_mid,interaction_mid,eff_mid,profile,stat_mid]:
        contract=contracts[mid]
        models[mid]={'model_type':mid,'model_revision':'1','formula':contract['formula'],'formula_purpose':'audit_only',
            'variables':{},'parameter_refs':[],'resource_refs':[],'depends_on':[], 'source_refs':['legacy'],
            'locator':'current registered definition + existing numerical consumers','meaning':'preserve current '+mid,
            'domain':'legacy sampled domain only; official validity not independently confirmed',
            'boundary':'preserve existing interpolation, support and clipping; no scientific correction',
            'binding_status':'BOUND_UNVERIFIED','implementation_contract':contract['contract']}
    def scalar(key,value,unit,mid,role='direct_input',derivation=None):
        if isinstance(value,np.generic):value=value.item()
        params[key]={'value':value,'unit':unit,'role':role,'meaning':key+'; legacy-code-derived',
            'source_refs':['legacy'],'consumers':[] if role in ('reference_only','unused_snapshot') else [mid],
            'status':'PROJECT_DERIVED' if role=='derived' else 'LEGACY_ONLY'}
        if derivation:params[key]['derivation']=derivation
        if params[key]['consumers']:models[mid]['parameter_refs'].append(key)
        return key
    def derived(key,value,unit,mid,formula,refs):
        return scalar(key,value,unit,mid,'derived',{'formula_id':formula,'input_refs':refs,'dependency_fingerprint':'0'*64})
    def resource(key,value,unit,axes,mid,kind='table',included=()):
        arrays[key]=np.array(value,copy=True)
        metadata[key]={'key':key,'shape':list(arrays[key].shape),'dtype':str(arrays[key].dtype),
            'unit':unit,'axes':axes,'meaning':key+'; legacy data snapshot','source_refs':['legacy'],
            'role':'direct_input','normalization':{'quantity_kind':kind,'runtime_authority':'array',
            'included_factors':list(included),'runtime_factors':[]},'sha256_raw_c_order':'0'*64,'generation':None}
        models[mid]['resource_refs'].append(key)
        return key
    run=physical.run
    for key,value,unit in [('baseline_m',run.baseline_m,'m'),('total_pot',run.total_pot,'POT'),
        ('yield_per_pot',run.yield_per_pot,'neutrinos/species/POT'),('tabulation_min',run.energy_tabulation[0],'MeV'),
        ('tabulation_max',run.energy_tabulation[1],'MeV'),('mask_min',run.node_support[0],'MeV'),
        ('mask_max',run.node_support[1],'MeV'),('tabulation_nodes',run.num_points,'1'),('interpolation',run.interpolation,'boolean')]:
        scalar('source.'+key,value,unit,source_mid,'runtime_control' if key.startswith(('tabulation','mask','interpolation')) else 'direct_input')
    scalar('target.run_mass_metadata',run.mass_metadata_kg,'kg',target_mid,'reference_only')
    scalar('target.detector_mass',physical.mass_kg,'kg',target_mid)
    from cevns_pyeft.foundation import constants
    from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
    from importlib import import_module
    matching=import_module('cevns_pyeft.theory.li2026.left_to_ci')
    tree=ast.parse(Path(matching.__file__).read_text('utf8'))
    used={node.attr for node in ast.walk(tree) if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='lecs'}
    for key in ['G_F','alpha_em','m_mu','m_e','m_pi_charged','AMU_GEV','GEV_INV2_TO_CM2']:
        unit={'G_F':'GeV^-2','alpha_em':'1','GEV_INV2_TO_CM2':'cm^2/GeV^-2'}.get(key,'GeV')
        scalar('constants.'+key,getattr(constants,key),unit,interaction_mid)
    # LEC units come from existing field definitions, not experimental inference.
    energy_lecs={'L5','L6','L7','L8','L9','L10','L11','L12','L13','L14','sigma_u_p','sigma_d_p','sigma_u_n','sigma_d_n','g1','g2','g3','g4','m_u','m_d','m_pi','m_N'}
    for key,value in asdict(DEFAULT_LECS).items():
        scalar('lecs.'+key,value,'GeV^2' if key.startswith('B0_m_') else ('GeV' if key in energy_lecs else '1'),
               interaction_mid,'direct_input' if key in used else 'unused_snapshot')
    scalar('target.atomic_mass_kg',getattr(physical,'atomic_mass_kg',1.6605390666e-27),'kg',target_mid)
    fluence=model.source.for_run(model.run)
    scalar('source.integration_min',fluence.components[0].support.integration_domain_MeV[0],'MeV',source_mid,'runtime_control')
    derived('source.integration_max',fluence.components[0].support.integration_domain_MeV[1],'MeV',source_mid,
            'muon_dar_endpoint.v1',['constants.m_mu','constants.m_e'])
    energy=np.linspace(*run.energy_tabulation,run.num_points)
    resource('source_energy_MeV',energy,'MeV',[{'name':'energy','unit':'MeV','rule':'declared tabulation'}],source_mid,'coordinate')
    components=[]
    for index,c in enumerate(fluence.components):
        rho_key=resource('rho_'+str(index),c.fixed_state_for_fast().rho,'1',
            [{'name':'flavor_row','unit':'1','values':['e','mu','tau']},{'name':'flavor_column','unit':'1','values':['e','mu','tau']}],source_mid,'density')
        metadata[rho_key]['semantic']='density_matrix'
        continuum_key=None
        lines=[]
        if c.lines:
            for line in c.lines:
                e=derived('source.line_energy',line.energy_MeV,'MeV',source_mid,'pion_line_energy.v1',['constants.m_pi_charged','constants.m_mu'])
                f=derived('source.line_fluence',line.fluence_per_cm2,'cm^-2',source_mid,'spherical_fluence.v1',['source.yield_per_pot','source.total_pot','source.baseline_m'])
                lines.append({'id':line.line_id,'energy_ref':e,'fluence_ref':f})
        else:
            continuum_key=resource('source_fluence_'+str(index),c.continuum(energy),'cm^-2 MeV^-1',
                [{'name':'energy','unit':'MeV','coordinate_ref':'source_energy_MeV'}],source_mid,'integrated_detector_fluence_density',('POT','yield','geometry'))
        components.append({'id':c.component_id,'legacy_label':('mu','e','mub')[index],
            'particle_kind':c.particle_kind,'rho_ref':rho_key,'continuum_ref':continuum_key,'lines':lines})
    from cevns_pyeft.nuclear.response import ResponseDB
    response_ref=next(r for r in definition.resources if r.id=='responses')
    db=ResponseDB(root/response_ref.path)
    isotopes=[]
    for target in model.targets.isotopes:
        isotope=target.isotope_id
        response=model.interaction._responses[isotope]
        prefix='target.'+isotope+'.'
        scalar(prefix+'A',int(response.basic['A']),'1',target_mid)
        scalar(prefix+'b',float(response.basic['b']),'GeV^-1',nuclear_mid)
        scalar('nuclear.'+isotope+'.exp_factor',response.exp_factor,'1',nuclear_mid)
        derived(prefix+'mass_GeV',target.kinematic_mass_GeV,'GeV',target_mid,'product.v1',[prefix+'A','constants.AMU_GEV'])
        derived(prefix+'mass_kg',target.nucleus_mass_kg,'kg',target_mid,'product.v1',[prefix+'A','target.atomic_mass_kg'])
        fraction=target.number_of_nuclei*target.nucleus_mass_kg/physical.mass_kg
        derived(prefix+'mass_fraction',fraction,'1',target_mid,'mass_fraction.v1',
            [prefix+'A']+[f'target.{part.isotope_id}.A' for part in model.targets.isotopes])
        derived(prefix+'nuclei',target.number_of_nuclei,'nuclei',target_mid,'nucleus_inventory.v1',['target.detector_mass',prefix+'mass_fraction',prefix+'mass_kg'])
        responses={}
        for channel in ('M','SigmaPP','SigmaP','PhiPP','PhiPT','Delta','MPhiPP'):
            key='nuclear_'+isotope+'_'+channel
            responses[channel]=resource(key,response.responses[channel],'1',
                [{'name':'nucleon_left','unit':'1','values':['p','n']},{'name':'nucleon_right','unit':'1','values':['p','n']},
                 {'name':'polynomial_power','unit':'1','rule':'ascending coefficient power'}],nuclear_mid)
        isotopes.append({'id':isotope,'responses':responses})
    from cevns_pyeft.experiments.base import _table
    eff_ref=next(r for r in definition.resources if r.id=='efficiency')
    table=_table(root/eff_ref.path,max(physical.efficiency_columns)+1)
    x,y=table[:,physical.efficiency_columns[0]],table[:,physical.efficiency_columns[1]]
    order=np.argsort(x);x,y=x[order],y[order];keep=np.r_[True,np.diff(x)>0];x,y=x[keep],y[keep]
    resource('efficiency_energy',x,'PE',[{'name':'PE','unit':'PE','rule':'legacy sorted/deduplicated'}],eff_mid,'coordinate')
    resource('efficiency_values',y,'1',[{'name':'PE','unit':'PE','coordinate_ref':'efficiency_energy'}],eff_mid)
    scalar('detector.efficiency_low',physical.efficiency_low,'1',eff_mid)
    detector={'profile':profile,'efficiency_energy_ref':'efficiency_energy','efficiency_values_ref':'efficiency_values',
              'efficiency_low_ref':'detector.efficiency_low','efficiency_threshold_ref':None}
    for key in (['pe_per_keV','slow_pe_nodes','efficiency_threshold'] if profile.startswith('deterministic') else ['mean_linear','mean_quadratic','sigma_coefficient']):
        mid=eff_mid if key=='efficiency_threshold' else profile
        unit={'pe_per_keV':'PE/keV','slow_pe_nodes':'1','efficiency_threshold':'PE','mean_linear':'PE/keV','mean_quadratic':'PE/keV^2','sigma_coefficient':'PE^0.5'}[key]
        ref=scalar('detector.'+key,getattr(physical,key),unit,mid,'runtime_control' if key=='slow_pe_nodes' else 'direct_input')
        detector[key+'_ref']=ref
    resource('observable_edges',definition.observation.edges,'PE',[{'name':'edges','unit':'PE','rule':'exact legacy edges'}],profile,'coordinate')
    from cevns_pyeft.experiments.coherent.statistics_binding import dataset
    from cevns_pyeft.experiments.loader import ResourceCatalog
    stat=dataset(definition,ResourceCatalog(root))
    stats={'model_id':stat_mid,'observable_unit':stat.observable.unit}
    for field in ['observed','background','uncertainty','lower','upper']:
        value=getattr(stat,field)
        if value is not None and len(value):
            key='statistics_'+field
            stats[field+'_ref']=resource(key,value,stat.observable.unit,[{'name':'bin','unit':'PE','edges_ref':'observable_edges'}],stat_mid)
    stats['sigma_alpha_ref']=scalar('statistics.sigma_alpha',definition.statistics.signal_sigma,'1',stat_mid)
    if definition.statistics.background_sigma is not None:
        stats['sigma_beta_ref']=scalar('statistics.sigma_beta',definition.statistics.background_sigma,'1',stat_mid)
    scalar('interaction.include_sm',True,'boolean',interaction_mid)
    scalar('interaction.sin2thetaW',definition.reproduction_sin2thetaW,'1',interaction_mid)
    numerics={}
    for backend,values in definition.numerical_profiles.items():
        numerics[backend]={key:scalar('numerics.'+backend+'.'+key,value,'1',profile,'runtime_control') for key,value in values.items()}
    if profile=='observed_gaussian_legacy_v1':
        scalar('numerics.recoil_min_keV',.1,'keV',profile,'runtime_control')
    package={'schema_version':'cevns-experiment-input/2','dataset_id':dataset_id,'experiment_slug':definition.experiment_slug,
        'analysis_revision':definition.analysis_revision,'scientific_claim':'legacy implementation compatibility only; no new scientific confirmation',
        'status':'DRAFT','human_approval':'NOT_REVIEWED'}
    source={'energy_ref':'source_energy_MeV','components':components,'integration_min_ref':'source.integration_min',
            'integration_max_ref':'source.integration_max','baseline_ref':'source.baseline_m','pot_ref':'source.total_pot','yield_ref':'source.yield_per_pot'}
    doc={'package':package,'parameters':params,'models':models,'resources':{'archive':'experiment.resources.npz','sha256':'0'*64,'arrays':metadata},
        'observable':{'name':definition.observation.name,'unit':definition.observation.unit,'edges_ref':'observable_edges','bin_count':len(definition.observation.edges)-1},
        'assembly':{'profile':profile,'source':source,'target':{'isotopes':isotopes,'mass_ref':'target.detector_mass'},
            'interaction':{'model_id':interaction_mid,'c10_mass_mode':physical.c10_mass_mode},'detector':detector,'statistics':stats,'numerics':numerics},
        'capabilities':{name:{'status':'NOT_RUN' if name in ('signal','fast','legacy_statistics') else 'BLOCKED',
            'evidence':[],'blockers':[] if name in ('signal','fast','legacy_statistics') else ['scientific source/convention review incomplete'],
            'human_approval':'NOT_REVIEWED'} for name in ['signal','fast','legacy_statistics','official_likelihood','general_antineutrino_EFT','scientific_release']},
        'provenance':{'sources':{'legacy':{'kind':'legacy_implementation','version':definition.analysis_revision,
            'definition_source_sha256':hashlib.sha256((root/'cevns_pyeft/experiments'/Path(definition.prepare.__module__.removeprefix('cevns_pyeft.experiments.').replace('.','/')).with_suffix('.py')).read_bytes()).hexdigest(),
            'locator':'current registered definition, response JSON, declared detector/statistical files; not official primary confirmation'}},
            'issues':[{'id':'science_review','status':'MISSING','detail':'external nuclear source, antinu convention, official statistics and detector validity not fully reviewed','blocks':['scientific_release','official_likelihood']}]}}
    for key,p in params.items():
        if p['role']=='derived':
            d=p['derivation'];d['dependency_fingerprint']=dependency_fingerprint(doc,d['input_refs'],formula_id=d['formula_id'])
    for key,meta in metadata.items():meta['sha256_raw_c_order']=hashlib.sha256(arrays[key].tobytes()).hexdigest()
    for key,meta in metadata.items():
        if key.startswith('source_'):
            meta['role']='materialized_derived_resource'
            refs=[k for k in params if k.startswith('source.') and 'line_' not in k]+['constants.m_mu']
            generation={'parameter_refs':refs,'model_refs':[source_mid],'resource_refs':[] if key=='source_energy_MeV' else ['source_energy_MeV']}
            generation['dependency_fingerprint']=dependency_fingerprint(doc,**generation)
            meta['generation']=generation
    models[profile]['depends_on']=[source_mid,target_mid,interaction_mid,eff_mid]
    models[interaction_mid]['depends_on']=[nuclear_mid]
    models[stat_mid]['depends_on']=[profile]
    units={source_mid:{'E':'MeV','fluence':'cm^-2 MeV^-1','line_weight':'cm^-2'},
        target_mid:{'nuclei':'nuclei','mass_i':'kg','detector_mass':'kg'},
        nuclear_mid:{'W':'1','y':'1','coeff':'1','b':'GeV^-1'},
        interaction_mid:{'dsigma':'cm^2/keV','rho':'1','K':'GeV^-2','mass':'GeV','E':'GeV'},
        eff_mid:{'x':'PE','y':'1'}, profile:{'T':'keV','PE':'PE','density':'events/PE','counts':'events/bin'},
        stat_mid:{'signal':'counts/bin','data':'counts/bin','chi2':'1','alpha':'1','beta':'1'}}
    for mid,variables in units.items():models[mid]['variables']=variables
    return {'ir_version':'cevns-onboarding-draft/1','acquisition':{'mode':'legacy_migration','evidence_claims':[]},
            'requested_capabilities':['signal','fast','legacy_statistics'],'document':doc},arrays


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--dataset',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    BUILTIN_CATALOG.ensure_loadable(args.dataset)
    draft,arrays=acquire(args.dataset,root)
    audit=root/'outputs/onboarding/task10'/args.dataset;audit.mkdir(parents=True,exist_ok=True)
    (audit/'draft.json').write_text(json.dumps(draft,indent=2),encoding='utf8');np.savez(audit/'declared_arrays.npz',**arrays)
    report=write_package(draft,arrays,args.output)
    (audit/'compilation.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
