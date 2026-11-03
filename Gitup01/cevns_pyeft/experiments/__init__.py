"""Lazy public exports, preserving historical star-import names."""
from importlib import import_module

_EXPORTS = {
    "TargetComponent": "base", "ExperimentConfig": "base", "_data_path": "base", "_num": "base", "_table": "base", "_interp_eff": "base",
    "EXPERIMENT_REGISTRY": "registry", "EXPERIMENT_SLOW_COUNT_REGISTRY": "registry", "get_experiment": "registry", "get_experiment_spec": "registry", "get_slow_count_function": "registry", "list_experiments": "registry",
    "list_runtime_experiment_ids": "registry", "list_archived_experiment_ids": "registry", "list_spec_only_experiment_ids": "registry",
    "ExperimentSpec": "specs", "REQUIRED_EXPERIMENT_SPEC_FIELDS": "specs", "discover_experiment_spec_paths": "specs", "experiment_data_root": "specs", "list_spec_experiment_names": "specs", "load_experiment_spec": "specs", "parse_yaml_scalar": "specs", "read_simple_yaml": "specs", "required_input_fields": "specs", "resolve_experiment_spec_path": "specs", "validate_experiment_spec_data": "specs",
    "ExperimentCatalog": "catalog", "BUILTIN_CATALOG": "catalog", "ArchivedExperimentError": "catalog", "SpecOnlyExperimentError": "catalog", "list_runtime_experiments": "catalog", "list_archived_experiments": "catalog", "list_spec_only_experiments": "catalog",
    "ExperimentManifestEntry": "manifest", "BUILTIN_MANIFEST": "manifest",
    "load_experiment": "loader", "predict_experiment": "runtime", "evaluate_experiment": "runtime", "compile_experiment": "runtime",
}
__all__ = list(_EXPORTS)

def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module("." + _EXPORTS[name], __name__), name)
    globals()[name] = value
    return value
