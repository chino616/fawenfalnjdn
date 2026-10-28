"""Dataset-independent orchestration, with no experiment-name formula routing."""
from dataclasses import dataclass, field
from types import MappingProxyType
from collections.abc import Mapping
from .definition import frozen_mapping

@dataclass(frozen=True)
class ExperimentPrediction:
    dataset_id: str
    analysis_revision: str
    analysis_fingerprint: str
    physics_fingerprint: str
    combined_prediction: object
    detector_predictions: Mapping
    backend: str
    record: Mapping
    legacy_result: object = field(default=None, repr=False)

    def __post_init__(self):
        object.__setattr__(self, 'detector_predictions', MappingProxyType(dict(self.detector_predictions)))
        object.__setattr__(self, 'record', frozen_mapping(self.record))

    @property
    def counts(self):
        return self.combined_prediction.counts

def predict_experiment(experiment, *, parameters=None, backend='slow', numerics=None, kernel=None):
    from cevns_pyeft.contracts import TheoryPoint
    definition = experiment.definition
    validate_snapshot(experiment)
    fallback = None
    if backend == 'auto':
        backend = 'fast' if kernel is not None and 'fast' in definition.numerical_profiles else 'slow'
        fallback = 'no supplied fast cache; use slow strategy' if backend == 'slow' else None
    if backend not in definition.numerical_profiles:
        raise ValueError(f'{definition.dataset_id}: unsupported backend {backend!r}')
    actual = resolve_numerics(definition, backend, numerics)
    point = TheoryPoint(sin2thetaW=definition.reproduction_sin2thetaW) if parameters is None else parameters
    if not isinstance(point, TheoryPoint):
        raise TypeError('parameters must be TheoryPoint or None')
    if point.state.values and not getattr(experiment.executor, 'supports_state_parameters', False):
        raise ValueError('executor does not consume state parameters')
    combined, detectors, raw, execution = experiment.executor(experiment, point, backend, actual, kernel)
    import numpy as np
    obs = definition.observation
    axes = combined.axes
    if len(axes) != 1 or (axes[0].name,axes[0].unit) != (obs.name,obs.unit) or not np.array_equal(axes[0].edges,obs.edges):
        raise ValueError('executor returned an incompatible observation')
    if tuple(detectors) != obs.detector_ids:
        raise ValueError('executor detector identities differ from definition')
    if obs.aggregation != 'sum_identical_bins':
        raise ValueError('unsupported detector aggregation')
    for part in detectors.values():
        if len(part.axes) != 1 or (part.axes[0].name,part.axes[0].unit) != (obs.name,obs.unit) or not np.array_equal(part.axes[0].edges,obs.edges):
            raise ValueError('detector prediction observation mismatch')
    if not np.allclose(sum(p.counts for p in detectors.values()),combined.counts,rtol=1e-12,atol=1e-14):
        raise ValueError('combined prediction does not equal named detector sum')
    from cevns_pyeft.contracts.validation import plain as contract_plain
    return ExperimentPrediction(definition.dataset_id, definition.analysis_revision, experiment.analysis_fingerprint,
        experiment.physics_fingerprint, combined, detectors, backend,
        {'numerics': actual, 'execution': execution, 'auto_reason': fallback,
         'sin2thetaW': point.sin2thetaW, 'reproduction_defaults_used': parameters is None,
         'theory_point': {'wc_triplets':contract_plain(point.wc_triplets),'include_sm':point.include_sm,'sin2thetaW':point.sin2thetaW,'state':contract_plain(point.state.values)}}, raw)

def evaluate_experiment(experiment, prediction):
    import numpy as np
    from importlib import import_module
    if (prediction.dataset_id, prediction.analysis_revision, prediction.analysis_fingerprint) != (
            experiment.dataset_id, experiment.definition.analysis_revision, experiment.analysis_fingerprint):
        raise ValueError('prediction dataset / analysis / observation identity mismatch')
    if prediction.physics_fingerprint != experiment.physics_fingerprint:
        raise ValueError('prediction physical definition identity mismatch')
    obs = experiment.definition.observation
    axes = prediction.combined_prediction.axes
    if len(axes) != 1 or (axes[0].name, axes[0].unit) != (obs.name, obs.unit) or not np.array_equal(axes[0].edges, obs.edges):
        raise ValueError('prediction observation axes mismatch')
    stat = experiment.definition.statistics
    if stat is None:
        raise ValueError(f'{experiment.dataset_id}: statistics unavailable')
    from .definition import digest
    if stat.bound_observation != digest(obs):
        raise ValueError('statistical observation mapping changed; bind explicitly mapped data before evaluation')
    module, name = stat.evaluator.rsplit(':',1)
    profile = getattr(import_module(module), name)(experiment, prediction)
    import hashlib
    from .definition import digest, plain
    resources = {}
    for ref in experiment.definition.resources:
        if ref.role == 'statistics':
            path = experiment.resource_catalog.resolve(ref)
            resources[ref.id] = {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    statistical_inputs = {'definition':plain(stat),'content':{k:v['sha256'] for k,v in resources.items()}}
    return ExperimentEvaluation(profile, frozen_mapping({'dataset_id':experiment.dataset_id,
        'analysis_fingerprint':experiment.analysis_fingerprint,'statistics_fingerprint':digest(statistical_inputs),
        'statistics':plain(stat),'resources':resources}))

def predict_selection(selection, *, resources=None, registry=None, parameters=None):
    from .loader import load_experiment
    from .selection import AnalysisSelection
    from .definition import plain
    selection = AnalysisSelection.from_mapping({'datasets':[plain(item) for item in selection.datasets]},registry=registry)
    results = {}
    for item in selection.datasets:
        if not item.enabled:
            continue
        exp = load_experiment(item.id, resources=resources, registry=registry)
        results[item.id] = predict_experiment(exp, parameters=parameters, backend=item.backend, numerics=item.numerics)
    return results


def resolve_numerics(definition, backend, numerics=None):
    actual = dict(definition.numerical_profiles[backend])
    supplied = dict(numerics or {})
    unknown = set(supplied) - set(actual)
    if unknown:
        raise TypeError(f'{definition.dataset_id}/{backend}: unconsumed numerical settings {sorted(unknown)}')
    actual.update(supplied)
    for key, value in actual.items():
        if key.startswith('n_') and (isinstance(value, bool) or not isinstance(value, int) or value < 2):
            raise ValueError(f'{key} must be an integer >= 2')
        if key == 'pe_step' and (not isinstance(value, (int,float)) or not 0 < value < float('inf')):
            raise ValueError('pe_step must be finite and positive')
    return actual


def compile_experiment(experiment, *, numerics=None):
    """Compile the actual representation declared by the experiment executor."""
    validate_snapshot(experiment)
    if 'fast' not in experiment.definition.numerical_profiles:
        raise ValueError(f'{experiment.dataset_id}: unsupported backend fast')
    if not hasattr(experiment.executor,'compile'):
        raise ValueError(f'{experiment.dataset_id}: no Fast compiler bound')
    ns=resolve_numerics(experiment.definition,'fast',numerics)
    return experiment.executor.compile(experiment,ns)


def validate_snapshot(experiment):
    definition = experiment.definition
    import hashlib
    from .definition import implementation_record
    if implementation_record(definition) != dict(experiment.record['implementation']):
        raise ValueError('implementation changed; reload experiment')
    for resource_id, path in experiment.resolved_resources.items():
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != experiment.record['resources'][resource_id]['sha256']:
            raise ValueError(f'physical resource {resource_id!r} changed; reload experiment')


@dataclass(frozen=True)
class ExperimentEvaluation:
    profile: object
    record: Mapping

    def __getattr__(self,name):
        # Keep the convenient .chi2/.alpha/etc access of the existing profiler.
        return getattr(self.profile,name)
