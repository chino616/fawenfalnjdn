"""Named unit conversions shared by theory and rate layers."""

from __future__ import annotations

from typing import TypeVar

from cevns_pyeft.foundation import constants as c


_DifferentialCrossSection = TypeVar("_DifferentialCrossSection")

# d/dE_keV = (d/dE_GeV) * dE_GeV/dE_keV.
CM2_PER_GEV_TO_CM2_PER_KEV = c.keV


def cm2_per_GeV_to_cm2_per_keV(
    value: _DifferentialCrossSection,
) -> _DifferentialCrossSection:
    """Convert a differential cross section from cm^2/GeV to cm^2/keV."""

    return value * CM2_PER_GEV_TO_CM2_PER_KEV


__all__ = [
    "CM2_PER_GEV_TO_CM2_PER_KEV",
    "cm2_per_GeV_to_cm2_per_keV",
]
