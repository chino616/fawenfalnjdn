"""Dataset-neutral package v2 validation/rendering; no runtime imports or defaults."""
from pathlib import Path
import hashlib
import json
import numpy as np

from .input_package import strict_json, fingerprint, dependency_fingerprint, derived_value, _cycles, validate_arrays

VERSION = 'cevns-experiment-input/2'


def schema():
    return strict_json(Path(__file__).with_name('generic_input.schema.json').read_text('utf8'))


def validate(data):
    from jsonschema import Draft202012Validator
    errors = [f'schema {"/".join(map(str,e.absolute_path))}: {e.message}'
              for e in Draft202012Validator(schema()).iter_errors(data)]
    if errors:
        return errors
    def check(ok, text):
        if not ok: errors.append(text)
    params, models, arrays = data['parameters'], data['models'], data['resources']['arrays']
    sources = data['provenance']['sources']
    bindings = binding_contracts()
    errors += _cycles({k:m['depends_on'] for k,m in models.items()})
    errors += _cycles({k:p.get('derivation', {}).get('input_refs', []) for k,p in params.items()})
    for mid, model in models.items():
        check(mid in bindings or model['binding_status'] == 'SPECIFICATION_ONLY', 'unregistered model: '+mid)
        check(all(k in params for k in model['parameter_refs']), 'model parameter refs: '+mid)
        check(all(k in arrays for k in model['resource_refs']), 'model resource refs: '+mid)
        check(all(k in models for k in model['depends_on']), 'model dependency refs: '+mid)
        check(all(mid in params[k]['consumers'] for k in model['parameter_refs'] if k in params),
              'model/parameter reverse ref: '+mid)
        check(all(s in sources for s in model['source_refs']), 'model provenance: '+mid)
        if mid in bindings:
            check(model['implementation_contract'] == bindings[mid]['contract'], 'implementation contract mismatch: '+mid)
            check(model['formula'] == bindings[mid]['formula'], 'registered model formula mismatch: '+mid)
        check(model['formula_purpose'] == 'audit_only', 'executable formula forbidden')
    inactive = ('reference_only','unused_snapshot')
    for pid, p in params.items():
        if p['value'] is not None:
            check((type(p['value']) is bool)==(p['unit']=='boolean'),'boolean/numeric unit: '+pid)
        check(all(s in sources for s in p['source_refs']), 'parameter source refs: '+pid)
        check(bool(p['consumers']) == (p['role'] not in inactive), 'parameter consumer role: '+pid)
        for consumer in p['consumers']:
            check(consumer in models and pid in models[consumer]['parameter_refs'], 'parameter/model reverse ref: '+pid)
        if p['value'] is None:
            check(p['status'] in ('MISSING','CONFLICT') and data['package']['status'] == 'DRAFT', 'missing value promoted: '+pid)
        if p['role']=='derived':
            d=p.get('derivation',{})
            try:
                refs=d['input_refs'];value=derived_value(d['formula_id'],[params[k]['value'] for k in refs])
                check(np.isclose(p['value'],value,rtol=1e-14,atol=0), 'derived value mismatch: '+pid)
                check(d['dependency_fingerprint']==dependency_fingerprint(data,refs,formula_id=d['formula_id']), 'stale derived: '+pid)
            except (KeyError,TypeError,ValueError,ZeroDivisionError) as e:errors.append('derivation '+pid+': '+str(e))
        check(('derivation' in p)==(p['role']=='derived'),'parameter derivation role: '+pid)
    for key, meta in arrays.items():
        check(len(meta['axes'])==len(meta['shape']), 'array axis rank: '+key)
        check(all(s in sources for s in meta['source_refs']), 'array provenance: '+key)
        norm=meta['normalization']
        check(not set(norm['included_factors']) & set(norm['runtime_factors']), 'duplicate normalization: '+key)
        for index,axis in enumerate(meta['axes']):
            if 'values' in axis: check(len(axis['values'])==meta['shape'][index], 'axis label length: '+key)
            for field,extra in [('coordinate_ref',0),('edges_ref',1)]:
                if field in axis:
                    ref=arrays.get(axis[field]);check(ref is not None,'missing axis coordinate: '+key)
                    if ref:check(ref['shape']==[meta['shape'][index]+extra] and ref['unit']==axis['unit'],'axis shape/unit: '+key)
        generation=meta.get('generation')
        check(bool(generation)==(meta['role']=='materialized_derived_resource'),'materialization role: '+key)
        if generation:
            try:check(generation['dependency_fingerprint']==dependency_fingerprint(data,generation['parameter_refs'],generation['model_refs'],generation['resource_refs']),'stale materialized resource: '+key)
            except KeyError as e:errors.append('generation ref: '+str(e))
    errors += _cycles({k:(m.get('generation') or {}).get('resource_refs',[]) for k,m in arrays.items()})
    for name,cap in data['capabilities'].items():
        check(cap['human_approval']=='NOT_REVIEWED','unearned human approval: '+name)
        if cap['status']=='BLOCKED':check(bool(cap['blockers']),'blocked capability without reason: '+name)
        if cap['status']=='PASS':check(bool(cap['evidence']),'capability PASS without evidence: '+name)
    check(not (data['package']['status']=='RELEASED' and data['package']['human_approval']!='APPROVED'),'release requires human decision')
    observable=data['observable']
    check(observable['edges_ref'] in arrays,'missing observable edges')
    if observable['edges_ref'] in arrays:
        check(arrays[observable['edges_ref']]['unit']==observable['unit'],'observable axis unit')
    if data['assembly']['profile'] != 'specification_only':
        try:errors += profile_errors(data)
        except (KeyError,TypeError,ValueError,AttributeError) as error:
            errors.append('invalid assembly structure: '+str(error))
    return errors


def profile_errors(data):
    """Closed contracts for code-owned executable profiles, without runtime imports."""
    errors=[]
    cfg=data['assembly'];params=data['parameters'];arrays=data['resources']['arrays'];models=data['models']
    def require(ok, message):
        if not ok:errors.append('assembly: '+message)
    def fields(obj, required, optional=()):
        if not isinstance(obj,dict):
            require(False,'expected object');return False
        require(set(required)<=obj.keys(),'missing fields '+str(sorted(set(required)-obj.keys())))
        require(obj.keys()<=set(required)|set(optional),'unknown fields '+str(sorted(obj.keys()-set(required)-set(optional))))
        return set(required)<=obj.keys()
    def parameter(ref, unit, consumer):
        record=params.get(ref) if isinstance(ref,str) else None
        require(record is not None,'unknown parameter ref '+str(ref))
        if record is not None:
            require(record['unit']==unit,'parameter unit '+ref+' expected '+unit)
            require(record['value'] is not None and record['role'] not in ('reference_only','unused_snapshot'),
                    'inactive/missing parameter '+ref)
            require(consumer in record['consumers'],'unbound parameter '+ref)
    def resource(ref,unit,consumer):
        record=arrays.get(ref) if isinstance(ref,str) else None
        require(record is not None,'unknown array ref '+str(ref))
        if record is not None:
            require(record['unit']==unit,'array unit '+ref+' expected '+unit)
            require(ref in models.get(consumer,{}).get('resource_refs',[]),'unbound array '+ref)
        return record
    profile=cfg['profile'];source='integrated_fluence_components_v1';target='explicit_target_inventory_v1'
    nuclear='nuclear_polynomial_arrays_v1';interaction='li2026_package_interaction_v1';eff='legacy_efficiency_curve_v1'
    expected={source,target,nuclear,interaction,eff,profile}
    stats=cfg['statistics']
    if stats:expected.add(stats.get('model_id',''))
    require(set(models)==expected,'profile model set differs: '+str(sorted(set(models)^expected)))
    require(set(arrays)=={ref for model in models.values() for ref in model['resource_refs']},
            'profile contains unconsumed or undeclared arrays')
    require(all(m['binding_status'] in ('BOUND_AND_TESTED','BOUND_UNVERIFIED') for m in models.values()),
            'SPECIFICATION_ONLY/REFERENCE_ONLY/BLOCKED model cannot execute')
    require({'signal','fast','legacy_statistics'}<=data['capabilities'].keys(),'missing capability states')
    s=cfg['source']
    if fields(s,('energy_ref','components','integration_min_ref','integration_max_ref','baseline_ref','pot_ref','yield_ref')):
        energy=resource(s['energy_ref'],'MeV',source)
        if energy:require(len(energy['shape'])==1,'source energy rank')
        def generated(record,ref,dependencies):
            if record:
                generation=record.get('generation') or {}
                required={k for k in params if k.startswith('source.') and 'line_' not in k}|{'constants.m_mu'}
                require(required<=set(generation.get('parameter_refs',[])) and source in generation.get('model_refs',[]) and
                        set(generation.get('resource_refs',[]))==set(dependencies),'incomplete source generation dependencies '+str(ref))
        generated(energy,s['energy_ref'],())
        for key,unit in [('integration_min','MeV'),('integration_max','MeV'),('baseline','m'),('pot','POT'),('yield','neutrinos/species/POT')]:
            parameter(s[key+'_ref'],unit,source)
        require(isinstance(s['components'],list) and bool(s['components']),'source components must be nonempty')
        ids=[]
        for component in s['components'] if isinstance(s['components'],list) else []:
            if not fields(component,('id','legacy_label','particle_kind','rho_ref','continuum_ref','lines')):continue
            ids.append(component['id'])
            require(component['particle_kind'] in ('nu','antinu'),'invalid particle kind')
            rho=resource(component['rho_ref'],'1',source)
            if rho:require(rho['shape']==[3,3] and rho.get('semantic')=='density_matrix','fixed flavor density contract')
            if component['continuum_ref'] is not None:
                continuum=resource(component['continuum_ref'],'cm^-2 MeV^-1',source)
                if continuum and energy:require(continuum['shape']==energy['shape'],'continuum shape')
                generated(continuum,component['continuum_ref'],(s['energy_ref'],))
            require(isinstance(component['lines'],list),'source lines must be a list')
            for line in component['lines'] if isinstance(component['lines'],list) else []:
                if fields(line,('id','energy_ref','fluence_ref')):
                    parameter(line['energy_ref'],'MeV',source);parameter(line['fluence_ref'],'cm^-2',source)
        require(len(ids)==len(set(ids)),'duplicate source component IDs')
    for key,unit in [('tabulation_min','MeV'),('tabulation_max','MeV'),('mask_min','MeV'),('mask_max','MeV'),
                     ('tabulation_nodes','1'),('interpolation','boolean')]:parameter('source.'+key,unit,source)
    t=cfg['target']
    if fields(t,('mass_ref','isotopes')):
        parameter(t['mass_ref'],'kg',target);parameter('target.atomic_mass_kg','kg',target)
        require(isinstance(t['isotopes'],list) and bool(t['isotopes']),'target isotopes must be nonempty')
        ids=[]
        for isotope in t['isotopes'] if isinstance(t['isotopes'],list) else []:
            if not fields(isotope,('id','responses')):continue
            sid=isotope['id'];ids.append(sid)
            for name,unit in [('A','1'),('mass_GeV','GeV'),('mass_kg','kg'),('mass_fraction','1'),('nuclei','nuclei')]:
                parameter('target.'+sid+'.'+name,unit,target)
            parameter('target.'+sid+'.b','GeV^-1',nuclear);parameter('nuclear.'+sid+'.exp_factor','1',nuclear)
            channels=('M','SigmaPP','SigmaP','PhiPP','PhiPT','Delta','MPhiPP')
            if fields(isotope['responses'],channels):
                for ref in isotope['responses'].values():resource(ref,'1',nuclear)
        require(len(ids)==len(set(ids)),'duplicate target isotope IDs')
    i=cfg['interaction']
    if fields(i,('model_id','c10_mass_mode')):
        require(i['model_id']==interaction,'interaction model differs')
        require(i['c10_mass_mode'] in ('quark_mass_resolved','legacy_equal_light_quark_mass'),'unregistered c10 mass mode')
    parameter('interaction.include_sm','boolean',interaction);parameter('interaction.sin2thetaW','1',interaction)
    d=cfg['detector']
    detector_parameters={'pe_per_keV':'PE/keV','slow_pe_nodes':'1'} if profile=='deterministic_pe_legacy_v1' else {
        'mean_linear':'PE/keV','mean_quadratic':'PE/keV^2','sigma_coefficient':'PE^0.5'}
    required=('profile','efficiency_energy_ref','efficiency_values_ref','efficiency_low_ref','efficiency_threshold_ref',
              *(k+'_ref' for k in detector_parameters))
    if fields(d,required):
        require(d['profile']==profile,'detector profile differs')
        resource(d['efficiency_energy_ref'],'PE',eff);resource(d['efficiency_values_ref'],'1',eff)
        parameter(d['efficiency_low_ref'],'1',eff)
        if d['efficiency_threshold_ref'] is not None:parameter(d['efficiency_threshold_ref'],'PE',eff)
        for key,unit in detector_parameters.items():parameter(d[key+'_ref'],unit,profile)
    if profile=='observed_gaussian_legacy_v1':parameter('numerics.recoil_min_keV','keV',profile)
    n=cfg['numerics']
    if fields(n,('slow','fast')):
        for backend,keys in [('slow',('n_enu',) if profile=='deterministic_pe_legacy_v1' else ('n_er','n_enu','n_pe_bin')),
                             ('fast',('n_er','n_enu') if profile=='deterministic_pe_legacy_v1' else ('n_er','n_enu','n_obs_sub'))]:
            if fields(n[backend],keys):
                for ref in n[backend].values():parameter(ref,'1',profile)
    resource(data['observable']['edges_ref'],'PE',profile)
    require(data['observable']['unit']=='PE','legacy profile observable unit')
    if stats:
        mid=stats.get('model_id')
        if mid=='gaussian_one_pull_legacy_v1':
            refs=('observed','uncertainty','lower','upper','spectrum');scalars=('sigma_alpha',)
        elif mid=='asymmetric_irls_legacy_v1':
            refs=('observed','background','lower','upper');scalars=('sigma_alpha','sigma_beta')
        else:require(False,'unregistered statistics model');return errors
        if fields(stats,('model_id','observable_unit',*(r+'_ref' for r in refs+scalars))):
            require(stats['observable_unit']=='counts/bin','statistics mapping unit')
            for name in refs:
                record=resource(stats[name+'_ref'],'counts/bin',mid)
                if record:require(record['shape']==[data['observable']['bin_count']],'statistics bin shape')
            for name in scalars:parameter(stats[name+'_ref'],'1',mid)
    return errors


def validate_resources(data, arrays, raw):
    # Reuse hash/shape/dtype/coordinate/observable checks, with generic metadata.
    errors=validate_arrays(data,arrays,raw)
    for key,meta in data['resources']['arrays'].items():
        if key in arrays and meta.get('semantic')=='density_matrix':
            # File-contract checks stay NumPy-only: catalog description must not
            # import the runtime theory package. ArrayState validates again with
            # the existing common state contract when an experiment is prepared.
            rho=arrays[key]
            if rho.shape!=(3,3) or not np.allclose(rho,rho.conj().T,rtol=0,atol=1e-10) or not np.isclose(np.trace(rho),1,rtol=0,atol=1e-10):
                errors.append(key+': invalid fixed density matrix shape/Hermiticity/trace')
            elif np.min(np.linalg.eigvalsh(rho)) < -1e-10:
                errors.append(key+': density matrix is not positive semidefinite')
    return errors


def binding_contracts():
    return strict_json(Path(__file__).with_name('component_bindings.json').read_text('utf8'))


def render(data, arrays):
    def cell(v):return str(v).replace('|','&#124;').replace('\n',' ')
    def table(head,rows):
        return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join('---' for _ in head)+' |']+
                         ['| '+' | '.join(cell(x) for x in row)+' |' for row in rows])
    p=data['package']
    lines=['# '+p['dataset_id']+' — Physics Input','',p['scientific_claim'],'',
        'Status: '+p['status']+'; human: '+p['human_approval']+'. YAML/NPZ are machine authority; this document is a deterministic view.','',
        '## Parameters','',table(['ID','Value','Unit','Role','Meaning','Consumers','Sources','State'],
            [(k,v['value'],v['unit'],v['role'],v['meaning'],v['consumers'],v['source_refs'],v['status']) for k,v in data['parameters'].items()]),'',
        '## Models and audit equations','']
    for mid,m in data['models'].items():
        lines += ['### '+mid,'',m['meaning'],'','```text',m['formula'],'```','',
                  table(['Variable','Unit'],m['variables'].items()),'',
                  'Inputs: '+str(m['parameter_refs'])+'; resources: '+str(m['resource_refs'])+'; dependencies: '+str(m['depends_on']),
                  'Contract: '+m['implementation_contract']+'; binding: '+m['binding_status']+'; domain: '+m['domain']+'; boundary: '+m['boundary'],
                  'Sources: '+str(m['source_refs'])+'; '+m['locator'],'']
    lines += ['## Resources','',table(['Key','Unit','Shape','Dtype','Axes','Normalization','Meaning','Sources'],
        [(k,v['unit'],v['shape'],v['dtype'],v['axes'],v['normalization'],v['meaning'],v['source_refs']) for k,v in data['resources']['arrays'].items()]),'',
        '## Assembly and normalization','', '```json',json.dumps(data['assembly'],ensure_ascii=False,indent=2),'```','',
        '## Capabilities','',table(['Capability','State','Evidence','Blockers','Human'],
            [(k,v['status'],v['evidence'],v['blockers'],v['human_approval']) for k,v in data['capabilities'].items()]),'',
        '## Provenance, missing and conflicts','',table(['Source','Record'],data['provenance']['sources'].items()),'',
        table(['Issue','State','Description','Blocks'],[(i['id'],i['status'],i['detail'],i['blocks']) for i in data['provenance']['issues']]),'',
        'Archive SHA256: `'+data['resources']['sha256']+'`. No equation text is executable.','']
    return '\n'.join(lines)
