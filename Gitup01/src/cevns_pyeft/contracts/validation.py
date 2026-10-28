"""Small immutable-value and coordinate helpers shared by the contracts."""
from collections.abc import Mapping
from types import MappingProxyType
import numpy as np


def readonly(value, *, dtype=float):
    array = np.array(value, dtype=dtype, copy=True)
    if not np.all(np.isfinite(array)):
        raise ValueError("array contains non-finite values")
    array.setflags(write=False)
    return array


def freeze(value):
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, np.ndarray):
        return readonly(value, dtype=value.dtype)
    if isinstance(value, (tuple, list)):
        return tuple(freeze(item) for item in value)
    return value


def plain(value):
    if isinstance(value, Mapping):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return plain(value.tolist())
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, np.generic):
        return value.item()
    return value


def positive(value, name, *, zero=False):
    if not np.isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError(f"{name} must be finite and {'nonnegative' if zero else 'positive'}")


def coordinates(value, name, *, minimum_size=1):
    result = readonly(value)
    if result.ndim != 1 or result.size < minimum_size or np.any(np.diff(result) <= 0):
        raise ValueError(f"{name} must be a strictly increasing finite 1D grid")
    return result
