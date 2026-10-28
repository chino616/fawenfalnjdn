from dataclasses import dataclass, field
from typing import Mapping
import numpy as np
from .validation import freeze, positive


@dataclass(frozen=True)
class TargetIsotope:
    isotope_id: str
    kinematic_mass_GeV: float
    nucleus_mass_kg: float
    number_of_nuclei: float
    mass_convention: str = "explicit"

    def __post_init__(self):
        if not self.isotope_id:
            raise ValueError("isotope_id is required")
        for name in ("kinematic_mass_GeV", "nucleus_mass_kg"):
            positive(getattr(self, name), name)
        positive(self.number_of_nuclei, "number_of_nuclei", zero=True)


@dataclass(frozen=True)
class TargetInventory:
    isotopes: tuple[TargetIsotope, ...]
    detector_mass_kg: float
    composition_record: Mapping = field(default_factory=dict)

    def __post_init__(self):
        parts = tuple(self.isotopes)
        if not parts or len({part.isotope_id for part in parts}) != len(parts):
            raise ValueError("target isotopes must be nonempty with unique IDs")
        positive(self.detector_mass_kg, "detector_mass_kg", zero=True)
        mass = sum(part.nucleus_mass_kg * part.number_of_nuclei for part in parts)
        if not np.isclose(mass, self.detector_mass_kg, rtol=1e-12, atol=0):
            raise ValueError("inventory nucleus counts do not account for detector mass")
        object.__setattr__(self, "isotopes", parts)
        object.__setattr__(self, "composition_record", freeze(self.composition_record))
