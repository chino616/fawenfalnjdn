"""Explicit mainline Runtime adapter, with no modification of the core package.

Source is the only replaced physics: independent external state provider is
bound both to the source component (Slow) and state_model (energy-resolved Fast).
New Definition/PreparedExperiment identities register its actual dependencies.
"""
from dataclasses import dataclass, replace
from pathlib import Path
from cevns_pyeft.contracts.modules import ModuleDescriptor
from cevns_pyeft.experiments.catalog import ExperimentCatalog
from cevns_pyeft.experiments.definition import ResourceRef
from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
from cevns_pyeft.experiments.solar_singlebin import load_singlebin, SingleBinModel
from cevns_pyeft.experiments.solar_nsi import NSIModel, NSIExecutor, EXTRA_DEPENDENCIES
from cevns_pyeft.theory.li2026.ee_vector_nsi import ElectronVectorNSI
from .protocol import ROOT, CARD, read, sha
from .state import ExternalSolarState


@dataclass(frozen=True)
class ExternalSettings:
    base: object
    external_card_sha256: str
    cache_root: str
    tail_mode: str
    implementation_modules: tuple


@dataclass(frozen=True)
class Preparation:
    base_definition: object

    def __call__(self, definition, resources):
        card = read(resources['external_snudd_card'])
        if sha(resources['external_snudd_card']) != definition.physical.external_card_sha256:
            raise ValueError('external source definition/card changed')
        for name, expected in card['upstream_files'].items():
            if sha(ROOT / '.externals/SNuDD' / name) != expected:
                raise ValueError('upstream pinned source/data changed: '+name)
        model, _ = self.base_definition.prepare(self.base_definition, resources)
        state = ExternalSolarState(Path(definition.physical.cache_root), definition.physical.external_card_sha256)
        component = replace(model.source.components_per_second[0], state_provider=state)
        source = replace(model.source, components_per_second=(component,), descriptor=ModuleDescriptor('source', 'B8_external_snudd_day',
            parameters={'flux_cm2_s': card['normalization']['flux_stays_cm2_s'], 'shape': 'original829-point Bahcall spectrum',
                        'state': state.describe().as_dict()}, resources={'external_card_sha256': sha(CARD)}))
        values = {f: getattr(model, f) for f in SingleBinModel.__dataclass_fields__}
        values.update(source=source, interaction=ElectronVectorNSI(resources['nuclear_response'], tuple(t.isotope_id for t in model.targets.isotopes)))
        weak_angle = read(ROOT / card['baseline_card'])['physics']['sin2thetaW']
        return NSIModel(**values, state_model=state, tail_mode=definition.physical.tail_mode), NSIExecutor(weak_angle)


def load_snudd(sample, *, cache_root=None, tail_mode='flat_sensitivity', interaction=None):
    """Explicit optional entry. The original load_solar_nsi signature is unchanged."""
    if tail_mode not in ['flat_sensitivity', 'zero', 'unit', 'bounded']:
        raise ValueError('choose an explicit supported X-tail treatment')
    card = read(CARD)
    if sha(ROOT / card['baseline_card']) != card['baseline_card_sha256']:
        raise ValueError('baseline NSI/statistical inputs changed')
    base = load_singlebin(sample, root=ROOT)
    modules = tuple(dict.fromkeys((*base.definition.physical.implementation_modules, *EXTRA_DEPENDENCIES,
        'extensions.solar_rho_snudd.protocol', 'extensions.solar_rho_snudd.state', 'extensions.solar_rho_snudd.experiment')))
    cache = Path(cache_root or ROOT / 'outputs/external/solar_rho_snudd/cache').resolve()
    settings = ExternalSettings(base.definition.physical, sha(CARD), str(cache), tail_mode, modules)
    dataset = base.dataset_id+'__external_snudd_day_'+tail_mode
    refs = tuple(replace(ref, path=str(ROOT / 'data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json'))
                 if ref.id == 'fitted_yields' else ref for ref in base.definition.resources)
    refs += (ResourceRef('external_snudd_card', str(CARD), semantic='actual pinned SNuDD propagation/input choices'),)
    refs += tuple(ResourceRef('snudd_raw_'+str(i), str(ROOT / '.externals/SNuDD' / name),
                   semantic='read-only fixed software/data dependency: '+name) for i, name in enumerate(card['upstream_files']))
    refs += tuple(ResourceRef('snudd_producer_'+str(i), str(ROOT / name), semantic='external file producer implementation')
                  for i, name in enumerate(card['producer_files']))
    definition = replace(base.definition, dataset_id=dataset, analysis_revision='solar_external_snudd_v3.4_'+tail_mode,
        physical=settings, resources=refs, prepare=Preparation(base.definition),
        numerical_profiles={'slow': {'n_er': 801, 'n_enu': 480}, 'fast': {'n_er': 801, 'n_enu': 144}},
        capabilities={'analysis': 'solar_ee_vector_nsi_external_snudd_day', 'source': 'isolated full-rho file provider; current ee-equivalent rate projection',
                      'statistics': 'same three independent Eq88 fitted-yield pulls asv3.3', 'kernel': 'new independent energy-resolved kernel, no reuse of old physical fingerprint'},
        validation=('tests/test_solar_snudd.py',))
    catalog = ExperimentCatalog(builtins=False).register(dataset, definition)
    return load_experiment(dataset, definition=definition, registry=catalog, resources=ResourceCatalog(ROOT),
                           components={'interaction': interaction} if interaction is not None else None)
