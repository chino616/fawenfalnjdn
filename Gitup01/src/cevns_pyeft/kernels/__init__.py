"""Fast-kernel basis, builders, reconstruction, and storage helpers."""

from .basis import *  # noqa: F401,F403

_LAZY_EXPORTS = {
    "build_matrixized_kernel": ("cevns_pyeft.kernels.builder", "build_matrixized_kernel"),
    "save_kernel": ("cevns_pyeft.kernels.builder", "save_kernel"),
    "reconstruct_counts_from_kernel": ("cevns_pyeft.kernels.reconstruction", "reconstruct_counts_from_kernel"),
    "reconstruct_real_events_from_full_kernel": ("cevns_pyeft.kernels.reconstruction", "reconstruct_real_events_from_full_kernel"),
    "reconstruct_real_events_from_pair_templates": ("cevns_pyeft.kernels.reconstruction", "reconstruct_real_events_from_pair_templates"),
    "build_fastscan_template": ("cevns_pyeft.kernels.storage", "build_fastscan_template"),
    "save_fastscan_template": ("cevns_pyeft.kernels.storage", "save_fastscan_template"),
    "load_fastscan_template": ("cevns_pyeft.kernels.storage", "load_fastscan_template"),
    "discover_fastscan_templates": ("cevns_pyeft.kernels.storage", "discover_fastscan_templates"),
    "reconstruct_saved_kernel": ("cevns_pyeft.kernels.storage", "reconstruct_saved_kernel"),
}


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(name)
    import importlib

    module_name, attr_name = _LAZY_EXPORTS[name]
    value = getattr(importlib.import_module(module_name), attr_name)
    globals()[name] = value
    return value
