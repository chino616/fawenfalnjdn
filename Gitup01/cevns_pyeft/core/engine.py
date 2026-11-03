"""Compatibility re-exports for the phase-1 split modules.

This minimal copy does not include the original monolithic fast-kernel,
statistics, plotting, or Streamlit application code. It keeps the old
``cevns_pyeft.core.engine`` import path for the split physics and rate APIs.
"""

from cevns_pyeft.foundation.constants import *  # noqa: F401,F403
from cevns_pyeft.nuclear.response import *  # noqa: F401,F403
from cevns_pyeft.theory.li2026.form_factors import *  # noqa: F401,F403
from cevns_pyeft.theory.li2026.lec import *  # noqa: F401,F403
from cevns_pyeft.theory.li2026.left_to_ci import *  # noqa: F401,F403
from cevns_pyeft.theory.li2026.responses import *  # noqa: F401,F403
from cevns_pyeft.theory.li2026.amplitude import *  # noqa: F401,F403
from cevns_pyeft.theory.li2026.cross_section import *  # noqa: F401,F403
from cevns_pyeft.experiments.base import *  # noqa: F401,F403
from cevns_pyeft.experiments.registry import *  # noqa: F401,F403
from cevns_pyeft.experiments.specs import *  # noqa: F401,F403
from cevns_pyeft.experiments.coherent.sns import *  # noqa: F401,F403
from importlib import import_module as _import_dataset_module
from cevns_pyeft.experiments.registry import _LEGACY_MODULES as _legacy_modules
from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG as _dataset_catalog
for _sid, _tag in _legacy_modules.items():
    if _sid not in _dataset_catalog.ids():
        continue
    for _stem in ('slow_counts_', 'fast_kernel_'):
        _module = _import_dataset_module('cevns_pyeft.experiments.coherent.'+_stem+_tag)
        for _name in _module.__all__:
            globals()[_name] = getattr(_module, _name)

from cevns_pyeft.rates.differential import *  # noqa: F401,F403
from cevns_pyeft.rates.counts import *  # noqa: F401,F403
from cevns_pyeft.kernels.basis import *  # noqa: F401,F403
from cevns_pyeft.kernels.builder import *  # noqa: F401,F403
from cevns_pyeft.kernels.reconstruction import *  # noqa: F401,F403
from cevns_pyeft.kernels.storage import *  # noqa: F401,F403



# Preserve historical call signatures while enforcing manifest lifecycle at the
# public compatibility boundary. Numerical implementations remain unchanged.
def _lifecycle_adapter(function, dataset_id):
    from functools import wraps

    @wraps(function)
    def checked(*args, **kwargs):
        from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
        BUILTIN_CATALOG.ensure_loadable(dataset_id)
        return function(*args, **kwargs)
    return checked


def _install_lifecycle_adapters():
    from cevns_pyeft.experiments.registry import _LEGACY_SLOW_COUNT_FUNCTIONS

    for dataset_id, function in _LEGACY_SLOW_COUNT_FUNCTIONS.items():
        name = function.__name__
        globals()[name] = _lifecycle_adapter(function, dataset_id)
        fast_name = "build_fast_kernel_" + name.removeprefix("slow_counts_")
        globals()[fast_name] = _lifecycle_adapter(globals()[fast_name], dataset_id)


_install_lifecycle_adapters()
