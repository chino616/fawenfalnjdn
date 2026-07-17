"""COHERENT experiment definitions."""

from .sns import *  # noqa: F401,F403
from .slow_counts_csi2017 import *  # noqa: F401,F403
from .slow_counts_csi2021 import *  # noqa: F401,F403
from .slow_counts_ar2020 import *  # noqa: F401,F403

_LAZY_EXPORTS = {
    "build_fast_kernel_csi2017": ("cevns_pyeft.experiments.coherent.fast_kernel_csi2017", "build_fast_kernel_csi2017"),
    "build_fast_kernel_csi2021": ("cevns_pyeft.experiments.coherent.fast_kernel_csi2021", "build_fast_kernel_csi2021"),
    "build_fast_kernel_ar2020": ("cevns_pyeft.experiments.coherent.fast_kernel_ar2020", "build_fast_kernel_ar2020"),
}


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(name)
    import importlib

    module_name, attr_name = _LAZY_EXPORTS[name]
    value = getattr(importlib.import_module(module_name), attr_name)
    globals()[name] = value
    return value
