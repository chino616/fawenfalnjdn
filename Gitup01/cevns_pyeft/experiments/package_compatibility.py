"""Container conversions for historical APIs; physics comes from package models."""
from dataclasses import asdict
from pathlib import Path
import numpy as np


def legacy_fast_template(experiment, *, basis, numerics):
    from cevns_pyeft.kernels.compiler import compile_fast, pair_templates
    model = experiment.model
    settings = experiment.executor.settings(numerics)
    compiled = compile_fast(model, numerics=settings, basis_keys=tuple(b.triplet for b in basis))
    isotopes = model.targets.isotopes
    if tuple(t.isotope_id for t in isotopes) != ('Cs133', 'I127'):
        raise ValueError('this historical template view requires Cs133/I127 target axes')
    fractions = [t.number_of_nuclei*t.nucleus_mass_kg/model.targets.detector_mass_kg for t in isotopes]
    full = np.stack((compiled.full_kernel[0]/fractions[0], compiled.full_kernel[1]/fractions[1],
                     compiled.full_kernel.sum(axis=0)))
    diag, real, imag, index = pair_templates(full)
    targets, flavors = ['Cs133', 'I127', 'CsI'], ['mu', 'e', 'mub']
    channels = list(compiled.record['channels'])
    edges = model.binning.axes[0].edges
    metadata = {'model': 'package_interface_kernel_legacy_view_v1', 'dataset': experiment.dataset_id,
        'flavor_schema_version': 1, 'neutrino_flavor_order': ['e', 'mu', 'tau'],
        'wilson_flavor_axis': {'row': 'final', 'column': 'initial'}, 'operator_basis_size': len(basis),
        'coefficient_shape': [len(basis), 3, 3], 'lnc_lnv_interference': False,
        'basis': [asdict(b) for b in basis], 'targets': targets, 'source_flavors': flavors, 'channels': channels,
        'pe_bins': edges.tolist(), 'n_ER': settings.n_er, 'n_Enu': settings.n_enu,
        'n_PE_sub': settings.n_observed_bin, 'n_PE_bin': settings.n_observed_bin,
        'pe_step': settings.observed_step, 'ER_min_keV': settings.recoil_min_keV,
        'c10_mass_mode': model.interaction.c10_mass_mode, 'input_authority': 'YAML+NPZ',
        'experiment_physics_fingerprint': experiment.physics_fingerprint,
        'interface_dependency_fingerprint': compiled.record['dependency_fingerprint'],
        'kernel_shape': list(full.shape), 'diag_shape': list(diag.shape),
        'pair_re_shape': list(real.shape), 'pair_im_shape': list(imag.shape), 'pair_index_shape': list(index.shape)}
    return {'basis': list(basis), 'targets': targets, 'source_flavors': flavors, 'channels': channels,
        'pe_bins': edges.copy(), 'kernel_axis_kind': 'channel_resolved_full_li2026', 'metadata': metadata,
        'full_kernel': full, 'diag': diag, 'pair_re': real, 'pair_im': imag, 'pair_index': index}


def legacy_profile_counts(definition, responses_json, wc_triplets=None, *, include_sm=True,
        sin2thetaW=None, c10_mass_mode=None, numerics=None, model=None, efficiency_data_path=None):
    """Compatibility dictionary; old path arguments never supply missing data."""
    from pathlib import Path
    from cevns_pyeft.contracts import TheoryPoint
    from cevns_pyeft.experiments.loader import load_experiment
    from cevns_pyeft.rates.legacy_observables import predict_legacy_observable
    if responses_json is not None and Path(responses_json).name!='responses_all.json':
        raise ValueError('external response override requires explicit interaction component')
    if efficiency_data_path is not None and Path(efficiency_data_path).name not in ('COHERENT_eff.txt','CENNS10AnlAEfficiency.txt'):
        raise ValueError('external efficiency override requires explicit observation component')
    if c10_mass_mode is not None and c10_mass_mode!=definition.physical.c10_mass_mode:
        raise ValueError('theory mode differs from package binding')
    experiment=load_experiment(definition.dataset_id,definition=definition)
    ns=dict(definition.numerical_profiles['slow']);ns.update(numerics or {})
    ns=experiment.executor._settings(ns)
    point=TheoryPoint(dict(wc_triplets or {}),include_sm=include_sm,
                      sin2thetaW=definition.reproduction_sin2thetaW if sin2thetaW is None else sin2thetaW)
    result=predict_legacy_observable(experiment.model if model is None else model,point,ns,experiment.executor.profile)
    from cevns_pyeft.sources.sns import LEGACY_COMPONENT_IDS
    parts={flavor:sum((v for (source,_),v in result.components.items() if source==sid),np.zeros(result.binning.shape))
           for flavor,sid in LEGACY_COMPONENT_IDS.items()}
    parts['total']=parts['mu']+parts['e']+parts['mub']
    edges=result.binning.axes[0].edges
    output={'counts_per_bin':parts,'counts_per_npe':{k:v/np.diff(edges) for k,v in parts.items()},
            'pe_bins':edges.copy(),'dataset':definition.dataset_id}
    density=experiment.executor.profile.startswith('deterministic')
    raw=result.diagnostics['raw_target_density' if density else 'raw_target_counts']
    output['target_flavor_dndpe_grid' if density else 'target_flavor_counts_per_bin']={flavor:{target:v for (source,target),v in raw.items() if source==sid}
        for flavor,sid in LEGACY_COMPONENT_IDS.items()}
    if density:output['pe_grid']=result.diagnostics['pe_grid']
    return output


def legacy_profile_fast(definition, responses_json=None, *, basis=None, numerics=None, c10_mass_mode=None):
    from cevns_pyeft.experiments.loader import load_experiment
    from cevns_pyeft.kernels.basis import li2026_left_basis_current
    if c10_mass_mode is not None and c10_mass_mode!=definition.physical.c10_mass_mode:
        raise ValueError('theory mode differs from package binding')
    if responses_json is not None and Path(responses_json).name!='responses_all.json':
        raise ValueError('external response override requires explicit interaction component')
    exp=load_experiment(definition.dataset_id,definition=definition)
    ns=dict(definition.numerical_profiles['fast']);ns.update(numerics or {})
    return legacy_builder_from_package(exp,list(basis or li2026_left_basis_current()),exp.executor._settings(ns))


def legacy_builder_from_package(exp,basis,ns):
    """Keep historical builder arithmetic/rounding, with array-only resources.

    The public interface compiler remains the accurate package Fast path. This
    compatibility view intentionally retains the old conversion constant and
    channel Hermitian convention required by the pre-existing frozen arrays.
    """
    from cevns_pyeft.kernels.builder import (_build_target_static,_build_one_target_kernel,
        _target_static,_build_one_target_kernel_csi2017_ar,_make_payload,_trapz_weights,CHANNELS)
    from cevns_pyeft.rates.legacy_observables import recoil_grid,observed_gaussian_fold
    from cevns_pyeft.targets.materials import combine_equal_stoichiometry
    model=exp.model;obs=model.observation;edges=model.binning.axes[0].edges
    source=model.source.for_run(model.run);by_id={c.component_id:c for c in source.components}
    prompt=by_id['prompt_numu'].lines[0]
    flux={'basic':{'detectorMassKg':model.targets.detector_mass_kg},'measured':{
        'e':by_id['delayed_nue'].continuum,'mub':by_id['delayed_numubar'].continuum,
        'muLine':(prompt.energy_MeV,prompt.fluence_per_cm2)}}
    raw={}
    for target in model.targets.isotopes:
        responses=getattr(model.interaction,'responses',getattr(model.interaction,'_responses',{}))
        response=responses[target.isotope_id]
        if hasattr(obs,'response'):
            static=_build_target_static(None,target=target.isotope_id,pe_bins=edges,ER_min_keV=ns['recoil_min_keV'],
                n_ER=ns['n_er'],n_PE_sub=ns['n_pe_bin'],pe_step=ns['pe_step'],response=response,
                observation=obs,nucleus_mass_kg=target.nucleus_mass_kg)
            acceptance={label:obs.selection.acceptance(cid) for label,cid in [('mu','prompt_numu'),('e','delayed_nue'),('mub','delayed_numubar')]}
            _,value=_build_one_target_kernel(None,exp.dataset_id,target.isotope_id,basis,edges,ns['recoil_min_keV'],
                ns['n_er'],ns['n_enu'],ns['n_pe_bin'],ns['pe_step'],model.interaction.c10_mass_mode,acceptance,
                flux_obj=flux,static=static)
        else:
            profile=exp.executor.profile
            recoil=recoil_grid(model,target,ns,profile)
            if profile.startswith('deterministic'):
                pe=np.linspace(float(edges[0]),float(edges[-1]),int(ns['n_er']),dtype=float)
                recoil=pe/float(obs.pe_per_keV)
                fold=np.zeros((len(recoil),len(edges)-1))
                for ib,(left,right) in enumerate(zip(edges[:-1],edges[1:])):
                    xs=pe[(pe>=left-1e-12)&(pe<=right+1e-12)]
                    if len(xs)<2:continue
                    weights=_trapz_weights(xs)/float(obs.pe_per_keV)
                    for x,w in zip(xs,weights):fold[int(np.argmin(np.abs(pe-x))),ib]+=float(w)*float(obs.efficiency(float(x)))
            else:
                fold=observed_gaussian_fold(recoil,_trapz_weights(recoil),edges,obs.efficiency,obs,ns['n_pe_bin'])
            static=_target_static(response,target=target.isotope_id,er_grid_keV=recoil,fold_kernel=fold,nucleus_mass_kg=target.nucleus_mass_kg)
            value=_build_one_target_kernel_csi2017_ar(static=static,dataset=exp.dataset_id,basis_elements=basis,
                n_enu=ns['n_enu'],c10_mass_mode=model.interaction.c10_mass_mode,
                detector_mass_kg=model.targets.detector_mass_kg,flux=flux)
        raw[target.isotope_id]=value
    if set(raw)=={'Cs133','I127'}:
        targets=['Cs133','I127','CsI'];full=np.stack((raw['Cs133'],raw['I127'],combine_equal_stoichiometry(raw['Cs133'],raw['I127'])))
    else:targets=list(raw);full=np.stack(list(raw.values()))
    metadata={'model':'legacy_builder_package_arrays','dataset':exp.dataset_id,'targets':targets,
        'source_flavors':['e','mu','mub'],'channels':list(CHANNELS),'basis':[asdict(b) for b in basis],
        'pe_bins':edges.tolist(),'flavor_schema_version':1,'neutrino_flavor_order':['e','mu','tau'],
        'wilson_flavor_axis':{'row':'final','column':'initial'},'operator_basis_size':len(basis),
        'coefficient_shape':[len(basis),3,3],'lnc_lnv_interference':False,
        'n_ER':ns['n_er'],'n_Enu':ns['n_enu'],'n_PE_bin':ns.get('n_pe_bin'),
        'input_authority':'YAML+NPZ','compatibility_arithmetic':'legacy conversion/channel convention'}
    result=_make_payload(metadata=metadata,full_kernel=full);result['basis']=list(basis)
    return result
