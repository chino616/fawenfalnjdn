from dataclasses import dataclass
from typing import Protocol
import numpy as np
from .validation import coordinates, readonly


@dataclass(frozen=True)
class Axis:
    name: str
    unit: str
    edges: np.ndarray
    clock: str | None = None

    def __post_init__(self):
        if not self.name or not self.unit:
            raise ValueError("axis name and unit are required")
        if self.unit in ("s", "ms", "us", "ns") and not self.clock:
            raise ValueError("time axis requires a clock definition")
        object.__setattr__(self, "edges", coordinates(self.edges, "axis edges", minimum_size=2))


@dataclass(frozen=True)
class Binning:
    axes: tuple[Axis, ...]

    def __post_init__(self):
        axes = tuple(self.axes)
        if not axes or len({axis.name for axis in axes}) != len(axes):
            raise ValueError("binning requires distinct named axes")
        object.__setattr__(self, "axes", axes)

    @property
    def shape(self):
        return tuple(axis.edges.size - 1 for axis in self.axes)


@dataclass(frozen=True)
class BinProbabilities:
    recoil_keV: np.ndarray
    binning: Binning
    values: np.ndarray
    included_selections: tuple[str, ...] = ()

    def __post_init__(self):
        recoil = coordinates(self.recoil_keV, "probability recoil")
        values = readonly(self.values)
        if values.shape != (recoil.size,) + self.binning.shape:
            raise ValueError("bin probability axes do not match values")
        if np.any(values < 0) or np.any(values.reshape(recoil.size, -1).sum(axis=1) > 1 + 1e-10):
            raise ValueError("mutually exclusive bin probabilities must sum to at most one")
        if len(set(self.included_selections)) != len(self.included_selections):
            raise ValueError("a selection was applied more than once")
        object.__setattr__(self, "recoil_keV", recoil)
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "included_selections", tuple(self.included_selections))


class ObservationModel(Protocol):
    axis_name: str
    axis_unit: str

    def bin_probabilities(self, *, target, recoil_keV, binning, component_id) -> BinProbabilities: ...
    def describe(self): ...
