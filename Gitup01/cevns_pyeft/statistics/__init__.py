from .confidence import *
from . import datasets as _datasets
from .likelihoods import *
from .observables import *
from .parameters import *
from .predictors import *
from .profiling import *
from .scans import *

# Keep the historical public names while loading dataset constants only when
# requested. Importing a generic profiler must work without experiment inputs.
__all__ = sorted({name for name in globals() if not name.startswith("_")} | set(_datasets.__all__))


def __getattr__(name):
    if name in _datasets.__all__:
        return getattr(_datasets, name)
    raise AttributeError(name)
