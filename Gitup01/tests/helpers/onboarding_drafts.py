"""Synthetic science-free compiler fixtures, with explicit units and missing data."""
import numpy as np
from cevns_pyeft.experiments.generic_input import binding_contracts


def synthetic_draft(dataset_id='SyntheticCurve', *, missing=False):
    arrays={'energy':np.array([1.,2.,3.]),'curve':np.array([.5,1.,.5]),'edges':np.array([0.,1.,2.])}
    def resource(key,unit,axes,kind):
        value=arrays[key]
        return {'key':key,'unit':unit,'shape':list(value.shape),'dtype':str(value.dtype),'axes':axes,
            'meaning':'synthetic '+key,'role':'direct_input','source_refs':['synthetic'],
            'normalization':{'quantity_kind':kind,'runtime_authority':'array','included_factors':[],'runtime_factors':[]},
            'sha256_raw_c_order':'0'*64,'generation':None}
    specs={}
    for mid in ('constant_v1','tabulated_curve_v1'):
        c=binding_contracts()[mid]
        specs[mid]={'model_type':'synthetic','model_revision':'1','formula':c['formula'],'formula_purpose':'audit_only',
            'variables':{'x':'1','y':'1'},'parameter_refs':['amplitude'] if mid=='constant_v1' else [],
            'resource_refs':['energy','curve'] if mid=='tabulated_curve_v1' else [],'depends_on':[],
            'source_refs':['synthetic'],'locator':'authored synthetic fixture','meaning':'synthetic compiler test',
            'domain':'explicit finite table','boundary':'zero outside support','binding_status':'BOUND_UNVERIFIED',
            'implementation_contract':c['contract']}
    doc={'package':{'schema_version':'cevns-experiment-input/2','dataset_id':dataset_id,'experiment_slug':'Synthetic',
             'analysis_revision':'synthetic_1','scientific_claim':'no experimental or scientific claim','status':'DRAFT','human_approval':'NOT_REVIEWED'},
         'parameters':{'amplitude':{'value':None if missing else 2.,'unit':'1','role':'direct_input','meaning':'synthetic amplitude',
             'source_refs':['synthetic'],'consumers':['constant_v1'],'status':'MISSING' if missing else 'SYNTHETIC'}},
         'models':specs,'resources':{'archive':'experiment.resources.npz','sha256':'0'*64,'arrays':{
             'energy':resource('energy','MeV',[{'name':'energy','unit':'MeV','rule':'explicit grid'}],'coordinate'),
             'curve':resource('curve','1',[{'name':'energy','unit':'MeV','coordinate_ref':'energy'}],'table'),
             'edges':resource('edges','PE',[{'name':'edges','unit':'PE','rule':'bin edges'}],'coordinate')}},
         'observable':{'name':'synthetic bins','unit':'PE','edges_ref':'edges','bin_count':2},
         'assembly':{'profile':'specification_only','source':{},'target':{},'interaction':{},'detector':{},'statistics':{},'numerics':{}},
         'capabilities':{'signal':{'status':'BLOCKED','blockers':['synthetic specification only'],'evidence':[],'human_approval':'NOT_REVIEWED'}},
         'provenance':{'sources':{'synthetic':{'kind':'synthetic','version':'1','locator':'this fixture'}},
             'issues':[{'id':'missing_amplitude','status':'MISSING' if missing else 'CONFLICT','detail':'no experimental evidence, no scientific approval','blocks':['signal']}]}}
    return {'ir_version':'cevns-onboarding-draft/1','acquisition':{'mode':'synthetic','evidence_claims':[]},
            'requested_capabilities':['signal'],'document':doc},arrays
