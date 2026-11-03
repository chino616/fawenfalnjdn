from __future__ import annotations

from typing import Callable
from collections.abc import Mapping

from cevns_pyeft.experiments.catalog import (
    BUILTIN_CATALOG,
    ArchivedExperimentError,
    SpecOnlyExperimentError,
    list_archived_experiments,
    list_runtime_experiments,
    list_spec_only_experiments,
)
from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS
from cevns_pyeft.experiments.specs import list_spec_experiment_names, load_experiment_spec


def _legacy_loader(dataset_id: str) -> Callable[[], dict]:
    def load():
        BUILTIN_CATALOG.ensure_loadable(dataset_id)
        return loadNeutrinoEmpiricalFluxSNS(dataset_id)
    return load


# These are legacy callable adapters, not a second active-ID registry.
_LEGACY_MODULES = {"CsI2017": "csi2017", "CsI2021": "csi2021", "Ar2020": "ar2020"}

class _LegacyFunctions(Mapping):
    def __iter__(self):
        return (sid for sid in BUILTIN_CATALOG.ids() if sid in _LEGACY_MODULES)
    def __len__(self):return sum(1 for _ in self)
    def __getitem__(self, name):
        from importlib import import_module
        sid=BUILTIN_CATALOG.ensure_loadable(name)
        tag=_LEGACY_MODULES[sid]
        return getattr(import_module('.coherent.slow_counts_'+tag,__package__),'slow_counts_'+tag)

_LEGACY_SLOW_COUNT_FUNCTIONS = _LegacyFunctions()


class _ActiveLegacyView(Mapping):
    """Read-only compatibility view; lifecycle state comes from Catalog."""

    def __init__(self, *, slow=False):
        self.slow = slow

    def __iter__(self):
        return (key for key in BUILTIN_CATALOG.ids()
                if not self.slow or key in _LEGACY_SLOW_COUNT_FUNCTIONS)

    def __len__(self):
        return sum(1 for _ in self)

    def __getitem__(self, key):
        canonical = BUILTIN_CATALOG.ensure_loadable(key)
        if self.slow:
            return _LEGACY_SLOW_COUNT_FUNCTIONS[canonical]
        if canonical in _LEGACY_SLOW_COUNT_FUNCTIONS:
            return _legacy_loader(canonical)
        # A new runtime definition need not implement the SNS compatibility API.
        return lambda: BUILTIN_CATALOG.definition(canonical).describe()


EXPERIMENT_REGISTRY: Mapping[str, Callable[[], dict]] = _ActiveLegacyView()
EXPERIMENT_SLOW_COUNT_REGISTRY: Mapping[str, Callable] = _ActiveLegacyView(slow=True)


def _catalog_id_or_none(name: str) -> str | None:
    try:
        return BUILTIN_CATALOG.canonical_id(str(name).strip())
    except KeyError:
        return None


def get_experiment(name: str) -> dict:
    key = str(name).strip()
    canonical = _catalog_id_or_none(key)
    if canonical is not None:
        # Archived/spec-only IDs must fail explicitly instead of falling through
        # to a YAML spec and being mistaken for executable runtime definitions.
        BUILTIN_CATALOG.ensure_loadable(canonical)
        return EXPERIMENT_REGISTRY[canonical]()
    try:
        return load_experiment_spec(key).as_dict()
    except (KeyError, FileNotFoundError) as exc:
        raise KeyError(f"Unknown experiment {name!r}. Available: {list_experiments()}") from exc


def get_slow_count_function(name: str) -> Callable:
    key = str(name).strip()
    canonical = _catalog_id_or_none(key)
    if canonical is not None:
        BUILTIN_CATALOG.ensure_loadable(canonical)
    if canonical not in EXPERIMENT_SLOW_COUNT_REGISTRY:
        raise KeyError(
            f"Unknown slow-count experiment {name!r}. Available: {list(EXPERIMENT_SLOW_COUNT_REGISTRY)}"
        )
    return EXPERIMENT_SLOW_COUNT_REGISTRY[canonical]


def get_experiment_spec(name: str):
    return load_experiment_spec(name)


def list_experiments(*, include_specs: bool = True) -> tuple[str, ...]:
    """List runtime IDs, optionally followed by non-runtime YAML specs.

    The default remains ``include_specs=True`` for compatibility.  Callers that
    need an executable set should use ``include_specs=False`` or
    ``list_runtime_experiments()``.
    """
    names = list(BUILTIN_CATALOG.ids())
    if include_specs:
        for name in (*BUILTIN_CATALOG.spec_only_ids(), *list_spec_experiment_names()):
            if name not in names and name not in BUILTIN_CATALOG.archived_ids():
                names.append(name)
    return tuple(names)


def list_runtime_experiment_ids() -> tuple[str, ...]:
    return list_runtime_experiments()


def list_archived_experiment_ids() -> tuple[str, ...]:
    return list_archived_experiments()


def list_spec_only_experiment_ids() -> tuple[str, ...]:
    return tuple(dict.fromkeys((*list_spec_only_experiments(), *(
        name for name in list_spec_experiment_names() if name not in BUILTIN_CATALOG.ids() and name not in BUILTIN_CATALOG.archived_ids()
    ))))


__all__ = [
    "EXPERIMENT_REGISTRY",
    "EXPERIMENT_SLOW_COUNT_REGISTRY",
    "get_experiment",
    "get_experiment_spec",
    "get_slow_count_function",
    "list_archived_experiment_ids",
    "list_experiments",
    "list_runtime_experiment_ids",
    "list_spec_only_experiment_ids",
]
