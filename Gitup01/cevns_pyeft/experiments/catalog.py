"""A lightweight lazy catalog; listing reads no experimental resources."""
from importlib import import_module

class ExperimentCatalog:
    def __init__(self, *, builtins=True):
        self._entries, self._aliases = {}, {}
        if builtins:
            for dataset, module in (
                ('CsI2021', 'coherent.csi2021_definition'),
                ('CsI2017', 'coherent.csi2017_definition'),
                ('Ar2020', 'coherent.ar2020_definition'),
                ('conus_plus_2025_c2c3c5_ge73_pyeft', 'conus_plus.definition')):
                self.register(dataset, module, aliases=(dataset.lower(),) if dataset.lower() != dataset else ())

    def register(self, dataset_id, definition, *, aliases=()):
        names = (dataset_id, *aliases)
        if len(set(names)) != len(names) or any(x in self._aliases for x in names):
            raise ValueError(f'duplicate dataset or alias: {names}')
        self._entries[dataset_id] = definition
        self._aliases.update({x: dataset_id for x in names})
        return self

    def canonical_id(self, name):
        try:
            return self._aliases[name]
        except KeyError as exc:
            raise KeyError(f'unknown dataset {name!r}; available: {self.ids()}') from exc

    def ids(self):
        return tuple(self._entries)

    def definition(self, name):
        key = self.canonical_id(name)
        entry = self._entries[key]
        value = import_module('.' + entry, __package__).DEFINITION if isinstance(entry, str) else entry
        if value.dataset_id != key:
            raise ValueError(f'registered identity {key!r} differs from definition {value.dataset_id!r}')
        return value

    def describe(self):
        return {key: self.definition(key).describe() for key in self.ids()}

BUILTIN_CATALOG = ExperimentCatalog()
