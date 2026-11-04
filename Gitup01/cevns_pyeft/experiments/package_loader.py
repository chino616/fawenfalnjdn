"""Two-machine-file adapter into the existing catalog/loader/runtime lifecycle."""
from dataclasses import dataclass, replace
from pathlib import Path
import hashlib
import zipfile
import numpy as np

from .definition import (ExperimentDefinition, ObservationDefinition, StatisticsDefinition,
                         ResourceRef, SNSRun, digest)
from .input_package import strict_json, read_arrays, validate_document, validate_arrays
from .model_registry import BindingSession


def read_package(package_path):
    path = Path(package_path).resolve()
    if path.name == 'experiment.input.yaml':
        path = path.parent
    input_path = path/'experiment.input.yaml'
    try:
        data = strict_json(input_path.read_text(encoding='utf-8'))
        errors = validate_document(data)
        if errors:
            raise ValueError('; '.join(errors))
        generic = data['package']['schema_version'] == 'cevns-experiment-input/2'
        if not generic:
            engine = data['engine_compatibility']
            if engine['core_api_version'] != 1 or any(v != '1' for v in engine['contract_versions'].values()):
                raise ValueError('unsupported engine API/component contract version')
        archive = path/data['resources']['archive']
        if archive.resolve().parent != path or archive.is_absolute() and data['resources']['archive'].startswith(('/', '\\')):
            raise ValueError('archive must be an internal relative file')
        raw = archive.read_bytes()
        arrays = read_arrays(raw, data['resources']['arrays'])
        if generic:
            from .generic_input import validate_resources
            errors = validate_resources(data, arrays, raw)
        else:
            errors = validate_arrays(data, arrays, raw)
        if errors:
            raise ValueError('; '.join(errors))
        if not generic:
            BindingSession(data, arrays)
        for value in arrays.values():
            value.setflags(write=False)
        return data, arrays
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        raise ValueError(f'{input_path}: package input/resource validation: {error}') from error


def physics_projection(data):
    return {key: {field: p[field] for field in ('value', 'unit', 'role')}
            for key, p in data['parameters'].items()
            if p['role'] not in ('reference_only', 'unused_snapshot') and not key.startswith('statistics.')}


@dataclass(frozen=True)
class PackageSettings:
    run: SNSRun
    mass_kg: float
    targets: tuple
    atomic_mass_kg: float
    quenching: tuple
    gamma_a: float
    gamma_b: float
    efficiency: tuple
    acceptance: tuple
    c10_mass_mode: str
    input_parameters: object
    implementation_modules: tuple


def _settings(data):
    p = {k: v['value'] for k, v in data['parameters'].items()}
    run = SNSRun(p['target.detector_mass'], p['source.baseline_m'], p['source.total_pot'],
        p['source.yield_per_pot'], (p['source.tabulation_min'], p['source.tabulation_max']),
        (p['source.mask_min'], p['source.mask_max']), p['source.tabulation_nodes'], p['source.interpolation'])
    modules = ('cevns_pyeft.experiments.package_loader', 'cevns_pyeft.experiments.package_components',
        'cevns_pyeft.experiments.model_registry', 'cevns_pyeft.nuclear.response',
        'cevns_pyeft.rates.differential', 'cevns_pyeft.rates.recoil', 'cevns_pyeft.rates.folding',
        'cevns_pyeft.core.predict', 'cevns_pyeft.theory.li2026.amplitude',
        'cevns_pyeft.theory.li2026.left_to_ci', 'cevns_pyeft.theory.li2026.responses',
        'cevns_pyeft.theory.li2026.coefficients', 'cevns_pyeft.detectors.csi2021')
    return PackageSettings(run, p['target.detector_mass'],
        tuple((i, data['target']['response_keys'][i], p[f'target.{i}.A']) for i in data['target']['isotope_order']),
        p['target.atomic_mass_kg'], tuple(p[f'detector.quenching_q{i}'] for i in range(1, 5)),
        p['detector.gamma_a'], p['detector.gamma_b'], tuple(p[f'detector.efficiency_{k}'] for k in 'abcd'),
        tuple((c['legacy_label'], p['detector.acceptance_' + c['legacy_label']]) for c in data['source']['components']),
        data['interaction']['c10_mass_mode'], physics_projection(data), modules)


def _require(data, capability):
    cap = data['capabilities'][capability]
    if cap['readiness'] in ('BLOCKED', 'NOT_SUPPORTED'):
        raise ValueError(f"{data['package']['dataset_id']}: capability {capability} {cap['readiness']}: {cap['blocker_refs']}")


def _assemble(definition, data, arrays):
    from cevns_pyeft.contracts.source import POTExposure, DetectorFluence, EnergySupport
    from cevns_pyeft.sources.composable import CallableFluenceComponent
    from cevns_pyeft.contracts.observation import Axis, Binning
    from cevns_pyeft.core.model import ExperimentModel
    from cevns_pyeft.detectors.csi2021 import CsI2021Observation, CsIGammaResponse, CsI2021Efficiency, CsI2021EfficiencyParams
    from cevns_pyeft.detectors.selection import LegacyComponentAcceptance
    from .package_components import ArraySource, ZeroContinuum
    _require(data, 'legacy_prediction')
    _require(data, 'package_backed_prediction')
    s, physical = BindingSession(data, arrays), definition.physical
    p = s.value
    run = POTExposure(physical.run.total_pot, definition.dataset_id)
    support = EnergySupport((p('source.integration_min'), p('source.integration_max')),
        (p('source.tabulation_min'), p('source.tabulation_max')), interpolation_id='package_linear',
        convention_id='legacy_sns_56MeV_node_mask_muon_DAR_quadrature')
    parts = []
    for c in data['source']['components']:
        continuum = ZeroContinuum() if c['continuum_ref'] is None else s.execute('sns_michel_tabulation_legacy_v1', resource=c['continuum_ref'])
        lines = (s.execute(c['line_model_ref']),) if c['line_model_ref'] else ()
        parts.append(CallableFluenceComponent(c['component_id'], c['particle_kind'], support,
            continuum, s.execute('sns_fixed_state_v1', component=c), lines))
    fluence = DetectorFluence(tuple(parts), run.run_id, {'geometry_included': True,
        'included_factors': ['POT', 'yield', 'geometry'], 'extra_runtime_factors': [],
        'authority': 'materialized NPZ continuum and validated derived prompt'})
    hashes = {k: v['sha256_raw_c_order'] for k, v in data['resources']['arrays'].items() if k.startswith(('source_', 'state_'))}
    source = ArraySource(fluence, physical.run.baseline_m, physical.run.yield_per_pot,
                        p('source.total_pot'), p('source.baseline_m'), p('source.yield_per_pot'), hashes)
    targets = s.execute('csi_target_inventory_v1')
    original = _settings(data)
    if (physical.run.energy_tabulation, physical.run.node_support, physical.run.num_points, physical.run.interpolation) != (
        original.run.energy_tabulation, original.run.node_support, original.run.num_points, original.run.interpolation):
        raise ValueError('source tabulation override requires explicit resource regeneration')
    if physical.mass_kg != original.mass_kg or physical.atomic_mass_kg != original.atomic_mass_kg:
        # An explicit dataclasses.replace scenario; the stored package remains immutable.
        from cevns_pyeft.targets.materials import inventory_from_mass_fractions
        parts = tuple(replace(t, nucleus_mass_kg=t.nucleus_mass_kg * physical.atomic_mass_kg/original.atomic_mass_kg,
                              number_of_nuclei=0) for t in targets.isotopes)
        targets = inventory_from_mass_fractions(physical.mass_kg, parts,
            [p(f'target.{t.isotope_id}.mass_fraction') for t in parts])
    if physical.targets != original.targets or physical.c10_mass_mode != original.c10_mass_mode:
        raise ValueError('target recipe/theory mode change requires another explicit package binding')
    interaction = s.execute('li2026_dsigma_v1')
    observation = CsI2021Observation(
        LegacyComponentAcceptance({c['component_id']: dict(physical.acceptance)[c['legacy_label']] for c in data['source']['components']}),
        CsIGammaResponse(physical.quenching, physical.gamma_a, physical.gamma_b),
        CsI2021Efficiency(CsI2021EfficiencyParams(*physical.efficiency)))
    obs = definition.observation
    return ExperimentModel(source, run, targets, interaction, observation,
        Binning((Axis(obs.name, obs.unit, obs.edges),)), model_id=data['prediction']['runtime_model_id'])


@dataclass(frozen=True)
class PackagePreparation:
    def __call__(self, definition, resources):
        path = resources['package_input']
        data, arrays = read_package(path)
        if resources['package_arrays'].resolve() != (path.parent/data['resources']['archive']).resolve():
            raise ValueError('NPZ override must be the archive declared by the input package')
        if data['package']['dataset_id'] != definition.dataset_id:
            raise ValueError('package/definition dataset identity mismatch')
        model = _assemble(definition, data, arrays)
        return model, PackageExecutor(data['prediction']['numerical_strategy'],
            data['parameters']['numerics.recoil_min_keV']['value'],
            data['parameters']['interaction.include_sm']['value'], data['parameters']['interaction.sin2thetaW']['value'],
            data['capabilities']['fast']['readiness'] not in ('BLOCKED', 'NOT_SUPPORTED'))

    def physics_resource_identity(self, definition, resolved):
        data, _ = read_package(resolved['package_input'])
        return {'package_input': digest({'parameters': physics_projection(data),
                    'models': {k: v['model_revision'] for k, v in data['models'].items() if k != data['statistics']['model_ref']}}),
                'package_arrays': digest({k: v['sha256_raw_c_order'] for k, v in data['resources']['arrays'].items()
                                         if not k.startswith('statistics_')})}


@dataclass(frozen=True)
class PackageExecutor:
    strategy: str
    recoil_min_keV: float
    include_sm: bool
    sin2thetaW: float
    fast_allowed: bool

    def default_point(self):
        from cevns_pyeft.contracts import TheoryPoint
        return TheoryPoint(include_sm=self.include_sm, sin2thetaW=self.sin2thetaW)

    def settings(self, ns):
        from cevns_pyeft.contracts import IntegrationSettings
        return IntegrationSettings(n_er=ns['n_er'], n_enu=ns['n_enu'], n_observed_bin=ns['n_pe_bin'],
            observed_step=ns['pe_step'], recoil_min_keV=self.recoil_min_keV, strategy=self.strategy)

    def describe_execution(self, model):
        return {'strategy': self.strategy, 'model': model.describe(), 'recoil_min_keV': self.recoil_min_keV,
                'default_theory': {'include_sm': self.include_sm, 'sin2thetaW': self.sin2thetaW}, 'fast_allowed': self.fast_allowed}

    def __call__(self, exp, point, backend, ns, kernel):
        from cevns_pyeft.core.predict import predict
        if backend == 'fast' and not self.fast_allowed:
            raise ValueError('package Fast is BLOCKED/NOT_SUPPORTED')
        result = predict(exp.model, parameters=point, numerics=self.settings(ns), backend=backend, compiled=kernel)
        return result, {'detector': result}, None, {'strategy': self.strategy, 'input_authority': 'YAML+NPZ'}

    def compile(self, exp, ns):
        from cevns_pyeft.kernels.compiler import compile_fast
        if not self.fast_allowed:
            raise ValueError('package Fast is BLOCKED/NOT_SUPPORTED')
        return compile_fast(exp.model, numerics=self.settings(ns))


def definition_from_package(package_path, *, resource_prefix=''):
    data, arrays = read_package(package_path)
    if data['package']['schema_version'] == 'cevns-experiment-input/2':
        from .package_profiles import definition_from_generic
        return definition_from_generic(data, arrays, resource_prefix)
    package = data['package']
    p = {k: v['value'] for k, v in data['parameters'].items()}
    prefix = Path(resource_prefix)
    resources = (ResourceRef('package_input', (prefix/'experiment.input.yaml').as_posix()),
                 ResourceRef('package_arrays', (prefix/data['resources']['archive']).as_posix()))
    profiles = {'slow': {'n_er': p['numerics.n_er'], 'n_enu': p['numerics.n_enu'],
                         'n_pe_bin': p['numerics.n_observed_bin'], 'pe_step': p['numerics.observed_step']}}
    # Merely constructing a Fast-compatible model is not package-Fast evidence.
    if data['capabilities']['fast']['package_runtime_validation'] == 'PASS':
        profiles['fast'] = dict(profiles['slow'])
    stat = data['statistics']
    statistics = None
    if data['capabilities']['legacy_approximate_statistics']['readiness'] not in ('BLOCKED', 'NOT_SUPPORTED'):
        statistics = StatisticsDefinition('cevns_pyeft.experiments.package_loader:evaluate_package_statistics',
            p['statistics.sigma_alpha'], p['statistics.sigma_beta'],
            observed=tuple(arrays[stat['observed_ref']]), background=tuple(arrays[stat['background_ref']]),
            uncertainty=tuple(np.maximum(arrays[stat['uncertainty_ref']], p['statistics.sigma_floor'])),
            kind='gaussian_two_pull', observable_unit=data['observable']['statistics_unit'],
            status='legacy approximate statistics; unresolved data semantics')
    return ExperimentDefinition(package['dataset_id'], package['experiment_slug'], package['analysis_revision'],
        (package['dataset_id'],), _settings(data), ObservationDefinition(data['observable']['name'], data['observable']['unit'],
        tuple(arrays[data['observable']['edges_ref']])), resources, profiles, PackagePreparation(),
        statistics=statistics, reproduction_sin2thetaW=p['interaction.sin2thetaW'],
        capabilities={'slow': 'package-backed legacy prediction', 'statistics': 'legacy approximate Gaussian',
                      'official_likelihood': 'BLOCKED', 'general_antineutrino_EFT': 'BLOCKED'},
        validation=('tests/test_experiment_package_loader.py',))


def evaluate_package_statistics(exp, prediction):
    from cevns_pyeft.statistics.profiling import profile_gaussian_two_pull
    stat = exp.definition.statistics
    counts = prediction.counts / np.diff(exp.definition.observation.edges)
    return profile_gaussian_two_pull(counts, stat.observed, stat.background, stat.uncertainty,
        sigma_alpha=stat.signal_sigma, sigma_beta=stat.background_sigma)


def load_experiment_package(package_path, *, validate=True):
    if validate is not True:
        raise ValueError('runtime package validation cannot be disabled')
    path = Path(package_path).resolve()
    directory = path.parent if path.name == 'experiment.input.yaml' else path
    definition = definition_from_package(directory)
    from .catalog import ExperimentCatalog
    from .loader import load_experiment, ResourceCatalog
    catalog = ExperimentCatalog(builtins=False).register(definition.dataset_id, definition)
    return load_experiment(definition.dataset_id, registry=catalog, resources=ResourceCatalog(directory))
