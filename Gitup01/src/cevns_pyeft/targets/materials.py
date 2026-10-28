from dataclasses import replace
import numpy as np
from cevns_pyeft.contracts.target import TargetInventory, TargetIsotope
from cevns_pyeft.foundation.constants import AMU_GEV


def _fractions(isotopes, fractions):
    parts = tuple(isotopes)
    values = np.asarray(fractions, dtype=float)
    if values.shape != (len(parts),) or not np.all(np.isfinite(values)) or np.any(values < 0) or not np.isclose(values.sum(), 1, rtol=0, atol=1e-12):
        raise ValueError("composition fractions must be nonnegative, match isotopes and sum to one")
    return parts, values


def inventory_from_mass_fractions(detector_mass_kg, isotopes, fractions):
    parts, values = _fractions(isotopes, fractions)
    return TargetInventory(tuple(replace(part, number_of_nuclei=detector_mass_kg * fraction / part.nucleus_mass_kg)
                                 for part, fraction in zip(parts, values)), detector_mass_kg,
                           {"fraction_convention": "mass", "fractions": dict(zip((p.isotope_id for p in parts), values))})


def inventory_from_number_fractions(detector_mass_kg, isotopes, fractions):
    parts, values = _fractions(isotopes, fractions)
    mean_mass = sum(part.nucleus_mass_kg * fraction for part, fraction in zip(parts, values))
    return TargetInventory(tuple(replace(part, number_of_nuclei=detector_mass_kg * fraction / mean_mass)
                                 for part, fraction in zip(parts, values)), detector_mass_kg,
                           {"fraction_convention": "number", "fractions": dict(zip((p.isotope_id for p in parts), values))})


def csi_target_inventory(detector_mass_kg=14.57):
    parts = tuple(TargetIsotope(name, a * AMU_GEV, a * 1.6605390666e-27, 0,
                               "legacy_A_times_amu") for name, a in (("Cs133", 133), ("I127", 127)))
    return inventory_from_mass_fractions(detector_mass_kg, parts, (133 / 260, 127 / 260))
