"""Mass-time normalization and named detector adaptation for CONUS+."""
import numpy as np
from cevns_pyeft.contracts import Prediction
from cevns_pyeft.contracts.observation import Axis,Binning

class ConusExecutor:
    def __init__(self, definition, resources):
        obs=definition.observation
        if (obs.name,obs.unit,obs.detector_ids)!=('ionization_energy','eVee',tuple(e.detector_id for e in definition.physical.exposures)):
            raise ValueError('CONUS executor requires its eVee axis and named exposure detector order')
        self.definition, self.resources = definition, resources
        self.source_dir = {'kopeikin':resources['kopeikin'],'mueller':resources['mueller']}

    def compile(self,exp,ns):
        from .fast_kernel import build_detector_response_matrix
        return build_detector_response_matrix(n_recoil=ns['n_recoil'],settings=exp.definition.physical,
            edges_evee=exp.definition.observation.edges)

    def __call__(self,exp,point,backend,ns,kernel):
        from .slow_counts import slow_counts_conus_plus
        from .fast_kernel import fast_counts_conus_plus_response_matrix,validate_detector_response_matrix
        definition = exp.definition
        settings = definition.physical
        common = dict(settings=settings,source_data_dir=self.source_dir,include_sm=point.include_sm,
            sin2theta_w=point.sin2thetaW,c10_mass_mode=settings.c10_mass_mode)
        if backend=='slow':
            if kernel is not None:
                raise ValueError('Slow does not consume response matrix')
            raw = slow_counts_conus_plus(self.resources['responses'],point.wc_triplets,bin_edges_evee=definition.observation.edges,**ns,**common)
        else:
            kernel = self.compile(exp,ns) if kernel is None else kernel
            validate_detector_response_matrix(kernel,settings=settings,edges_evee=definition.observation.edges)
            if kernel['metadata']['recoil_quadrature']['n_recoil'] != ns['n_recoil'] or not np.array_equal(kernel['exposures_kg_day'],[x.kg_day for x in settings.exposures]):
                raise ValueError('response matrix numerical settings or exposure mismatch')
            raw = fast_counts_conus_plus_response_matrix(kernel,self.resources['responses'],point.wc_triplets,
                n_energy=ns['n_energy'],edges_evee=definition.observation.edges,**common)
        obs = definition.observation
        bins = Binning((Axis(obs.name,obs.unit,obs.edges),))
        norm = {'route':'per_second_flux_x_nuclei_per_kg_x_seconds_per_day_x_kg_day',
                'nuclei_per_kg':settings.nuclei_per_kg,'seconds_per_day':settings.seconds_per_day,
                'exposures_kg_day':{e.detector_id:e.kg_day for e in settings.exposures}}
        def pack(counts):
            parts = {(component,settings.response_key):counts[i] for i,component in enumerate(settings.source.components)}
            return Prediction(np.sum(counts,axis=0),bins,parts,norm,
                {'dataset_id':definition.dataset_id,'physics_fingerprint':exp.physics_fingerprint},ns)
        components = raw['counts_per_detector_component_bin']
        detectors = {name:pack(components[i]) for i,name in enumerate(obs.detector_ids)}
        combined = pack(np.sum(components,axis=0))
        return combined,detectors,raw,{'strategy':definition.capabilities[backend], 'aggregation':'sum named detectors in identical eVee bins'}

def prepare_conus(definition,resources):
    executor = ConusExecutor(definition,resources)
    return definition.physical,executor


def evaluate(exp,prediction):
    from .statistics import profile_paper_eq33
    s = exp.definition.statistics
    actual = tuple(e.kg_day for e in exp.definition.physical.exposures)
    if actual != s.required_exposures:
        raise ValueError('CONUS digitized statistics require effective119 C3-like exposures (0,119,0); default 357 kg day forward prediction has no bound observations')
    if prediction.record['execution']['aggregation'] != 'sum named detectors in identical eVee bins':
        raise ValueError('CONUS observation aggregation mismatch')
    ref = next(r for r in exp.definition.resources if r.id=='observations')
    rows = np.genfromtxt(exp.resource_catalog.resolve(ref),delimiter=',',names=True)
    return profile_paper_eq33(prediction.counts,rows['observed_excess_per_kg_10eVee'],rows['sigma_used_half_span'],sigma_alpha=s.signal_sigma)
