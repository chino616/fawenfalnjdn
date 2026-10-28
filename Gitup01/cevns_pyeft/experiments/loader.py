from cevns_pyeft.foundation.paths import resource_root
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
    dataset_id: str | None = None

    def __post_init__(self):
        object.__setattr__(self,'root',Path(self.root).resolve())
        values={}
        for key,value in dict(self.overrides or {}).items():
            if not isinstance(key,str) and not (isinstance(key,tuple) and len(key)==2 and all(isinstance(x,str) for x in key)):
                raise TypeError('resource keys must be resource_id or (dataset_id,resource_id)')
            values[key]=Path(value)
        object.__setattr__(self,'overrides',MappingProxyType(values))

    def validate(self, definitions):
        available={(d.dataset_id,r.id):r for d in definitions for r in d.resources}
        ids={d.dataset_id.lower():d.dataset_id for d in definitions}
        for key in self.overrides:
            if isinstance(key,tuple):
                ds,rid=key;canonical=ids.get(ds.lower())
                if (canonical,rid) not in available:
                    raise KeyError(f'unknown or unused scoped resource override {key!r}')
            else:
                refs=[r for (ds,rid),r in available.items() if rid==key]
                if not refs:raise KeyError(f'unknown or unused resource override {key!r}')
                if len({r.path for r in refs})>1:
                    raise KeyError(f'ambiguous resource override {key!r}; use (dataset_id,resource_id)')

    def for_definition(self, definition, *, validated=False):
        from dataclasses import replace
        if not validated:self.validate((definition,))
        keys={r.id for r in definition.resources};values={}
        for key,value in self.overrides.items():
            if isinstance(key,str) and key in keys:values[key]=value
        for key,value in self.overrides.items():
            if isinstance(key,tuple) and key[0].lower()==definition.dataset_id.lower():values[key[1]]=value
        return replace(self,overrides=values,dataset_id=definition.dataset_id)

    def path_for(self, ref):
        path=Path(self.overrides.get(ref.id,ref.path))
        from cevns_pyeft.foundation.resources import resolve_resource
        return resolve_resource(self.root,path)

    def resolve(self, ref):
        path=self.path_for(ref)
        if not path.is_file():
            raise FileNotFoundError(f'{self.dataset_id}: missing {ref.role} resource {ref.id!r}: {path}; provide an external resource root for installed wheels')
        return path

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

def load_experiment(dataset_id, *, resources=None, registry=None, definition=None, components=None):
    catalog = registry if registry is not None else BUILTIN_CATALOG
    canonical = catalog.canonical_id(dataset_id) if definition is None else dataset_id
    definition = definition or catalog.definition(canonical)
    if canonical != definition.dataset_id:
        raise ValueError('requested dataset and definition identity differ')
    if resources is None:
        resources = ResourceCatalog(resource_root())
    elif not isinstance(resources, ResourceCatalog):
        resources = ResourceCatalog(resources)
    resources = resources.for_definition(definition)
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
    from .assembly import actual_assembly
    from .definition import snapshot
    if components:
        from dataclasses import replace,fields
        allowed={'source','interaction','observation','targets','run','target','nuclei_per_kg','exposures'} & {f.name for f in fields(model) if f.init}
        if set(components)-allowed:raise TypeError('unknown/unconsumed component slots: '+str(set(components)-allowed))
        model=replace(model,**components)
    model = snapshot(model)
    assembly = actual_assembly(model,executor)
    physics = {'actual_assembly':assembly, 'implementation': implementation, 'actual_assembly':assembly, 'physical': definition.describe()['physical'], 'observation': definition.describe()['observation'],
               'resources': {k:v['sha256'] for k,v in resource_record.items()}}
    # Statistics are lazy: neither resolving nor reading these files occurs here.
    analysis = {'dataset_id': definition.dataset_id, 'analysis_revision': definition.analysis_revision,
                'observation': definition.describe()['observation'], 'statistics': definition.describe()['statistics'],
                'statistics_resources': [(r.id,str(resources.path_for(r))) for r in definition.resources if r.role == 'statistics']}
    record = {'definition': definition.describe(), 'resources': resource_record, 'implementation': implementation, 'actual_assembly':assembly,
              'physics_fingerprint': digest(physics), 'analysis_fingerprint': digest(analysis)}
    if hasattr(model,'describe'):
        record['actual_model'] = model.describe()
    return PreparedExperiment(definition, resources, MappingProxyType(resolved), executor, model,
                              frozen_mapping(record), digest(physics), digest(analysis))
