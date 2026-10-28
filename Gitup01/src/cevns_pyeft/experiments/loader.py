"""Resolve physical resources and construct one dataset execution instance."""
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
import hashlib
from .definition import digest, frozen_mapping
from .catalog import BUILTIN_CATALOG

@dataclass(frozen=True)
class ResourceCatalog:
    root: Path | str
    overrides: object = None

    def __post_init__(self):
        object.__setattr__(self, 'root', Path(self.root).resolve())
        object.__setattr__(self, 'overrides', MappingProxyType(dict(self.overrides or {})))

    def path_for(self, ref):
        path = Path(self.overrides.get(ref.id, self.root / ref.path))
        if not path.is_absolute():
            path = self.root / path
        return path.resolve()

    def resolve(self, ref):
        path = self.path_for(ref)
        if not path.is_file():
            raise FileNotFoundError(f'missing {ref.role} resource {ref.id!r}: {path}')
        return path.resolve()

@dataclass(frozen=True)
class PreparedExperiment:
    definition: object
    resource_catalog: ResourceCatalog
    resolved_resources: object
    executor: object
    model: object
    record: object
    physics_fingerprint: str
    analysis_fingerprint: str

    @property
    def dataset_id(self):
        return self.definition.dataset_id

    def describe(self):
        from .definition import plain
        return plain(self.record)

def load_experiment(dataset_id, *, resources=None, registry=None, definition=None):
    catalog = registry if registry is not None else BUILTIN_CATALOG
    canonical = catalog.canonical_id(dataset_id) if definition is None else dataset_id
    definition = definition or catalog.definition(canonical)
    if canonical != definition.dataset_id:
        raise ValueError('requested dataset and definition identity differ')
    if resources is None:
        resources = ResourceCatalog(Path(__file__).resolve().parents[3])
    elif not isinstance(resources, ResourceCatalog):
        resources = ResourceCatalog(resources)
    resolved, resource_record = {}, {}
    for ref in definition.resources:
        if ref.role == 'statistics':
            continue
        path = resources.resolve(ref)
        resolved[ref.id] = path
        resource_record[ref.id] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'semantic': ref.semantic}
    model, executor = definition.prepare(definition, MappingProxyType(resolved))
    from .definition import implementation_record
    implementation = implementation_record(definition)
    physics = {'implementation': implementation, 'physical': definition.describe()['physical'], 'observation': definition.describe()['observation'],
               'resources': {k:v['sha256'] for k,v in resource_record.items()}}
    # Statistics are lazy: neither resolving nor reading these files occurs here.
    analysis = {'dataset_id': definition.dataset_id, 'analysis_revision': definition.analysis_revision,
                'observation': definition.describe()['observation'], 'statistics': definition.describe()['statistics'],
                'statistics_resources': [(r.id,str(resources.path_for(r))) for r in definition.resources if r.role == 'statistics']}
    record = {'definition': definition.describe(), 'resources': resource_record, 'implementation': implementation,
              'physics_fingerprint': digest(physics), 'analysis_fingerprint': digest(analysis)}
    if hasattr(model,'describe'):
        record['actual_model'] = model.describe()
    return PreparedExperiment(definition, resources, MappingProxyType(resolved), executor, model,
                              frozen_mapping(record), digest(physics), digest(analysis))
