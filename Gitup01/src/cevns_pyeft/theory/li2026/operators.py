"""Canonical metadata for the 22 active Li2026 LEFT operators."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral
import re
from types import MappingProxyType
from typing import Dict, Literal, Mapping, Optional, Tuple

import numpy as np

from cevns_pyeft.theory.li2026.flavor import FlavorMatrix, as_flavor_matrix

LeftKey = Tuple[int, int, str]
LeptonNumberSector = Literal["LNC", "LNV"]


@dataclass(frozen=True)
class OperatorSpec:
    """Physics metadata for one LEFT operator structure."""

    key: LeftKey
    name: str
    dimension: int
    lepton_number: LeptonNumberSector
    unit_power_GeV: int
    lnv_diagonal_must_vanish: bool = False

    def __post_init__(self) -> None:
        if self.dimension != self.key[0]:
            raise ValueError(
                f"Operator {self.name} dimension {self.dimension} does not match key {self.key}"
            )
        expected_power = 4 - self.dimension
        if self.unit_power_GeV != expected_power:
            raise ValueError(
                f"Operator {self.name} must have GeV power {expected_power}, "
                f"got {self.unit_power_GeV}"
            )
        if self.lepton_number not in ("LNC", "LNV"):
            raise ValueError(f"Unknown lepton-number sector: {self.lepton_number}")
        if self.lnv_diagonal_must_vanish and self.lepton_number != "LNV":
            raise ValueError("Only LNV operators may require a vanishing diagonal")


def _spec(
    key: LeftKey,
    name: str,
    lepton_number: LeptonNumberSector,
) -> OperatorSpec:
    dimension = key[0]
    return OperatorSpec(
        key=key,
        name=name,
        dimension=dimension,
        lepton_number=lepton_number,
        unit_power_GeV=4 - dimension,
        lnv_diagonal_must_vanish=lepton_number == "LNV",
    )


LI2026_OPERATOR_SPECS = (
    _spec((5, 1, ""), "C5_1", "LNV"),
    _spec((6, 1, "u"), "C6u1", "LNC"),
    _spec((6, 1, "d"), "C6d1", "LNC"),
    _spec((6, 2, "u"), "C6u2", "LNC"),
    _spec((6, 2, "d"), "C6d2", "LNC"),
    _spec((7, 1, "u"), "C7u1", "LNC"),
    _spec((7, 1, "d"), "C7d1", "LNC"),
    _spec((7, 2, "u"), "C7u2", "LNC"),
    _spec((7, 2, "d"), "C7d2", "LNC"),
    _spec((7, 3, "u"), "C7u3", "LNV"),
    _spec((7, 3, "d"), "C7d3", "LNV"),
    _spec((7, 4, "u"), "C7u4", "LNV"),
    _spec((7, 4, "d"), "C7d4", "LNV"),
    _spec((7, 5, "u"), "C7u5", "LNV"),
    _spec((7, 5, "d"), "C7d5", "LNV"),
    _spec((7, 6, ""), "C7_6", "LNV"),
    _spec((7, 7, ""), "C7_7", "LNV"),
    _spec((8, 1, "u"), "C8u1", "LNC"),
    _spec((8, 1, "d"), "C8d1", "LNC"),
    _spec((8, 2, "u"), "C8u2", "LNC"),
    _spec((8, 2, "d"), "C8d2", "LNC"),
    _spec((8, 9, ""), "C8_9", "LNC"),
)

OPERATOR_SPECS_BY_KEY: Mapping[LeftKey, OperatorSpec] = MappingProxyType(
    {spec.key: spec for spec in LI2026_OPERATOR_SPECS}
)


def get_operator_spec(key: LeftKey) -> OperatorSpec:
    """Return metadata for a supported Li2026 LEFT operator."""

    try:
        return OPERATOR_SPECS_BY_KEY[key]
    except KeyError as exc:
        raise KeyError(f"Unknown Li2026 LEFT operator key: {key}") from exc


def validate_operator_coefficient(
    key: LeftKey,
    value: object,
    *,
    atol: float = 1e-10,
) -> FlavorMatrix:
    """Validate matrix shape/finiteness and explicit LNV diagonal constraints."""

    spec = get_operator_spec(key)
    matrix = as_flavor_matrix(value, name=f"LEFT coefficient {key}")
    if spec.lnv_diagonal_must_vanish and np.any(np.abs(np.diag(matrix)) > atol):
        raise ValueError(f"LNV coefficient {key} must have a vanishing diagonal")
    return matrix


def parse_operator_name(name: str) -> LeftKey:
    """Parse and validate a canonical string such as ``C1u(6)``."""

    if not isinstance(name, str):
        raise TypeError(f"LEFT operator name must be a string, got {type(name).__name__}")
    match = re.fullmatch(r"C(\d+)([ud])?\((\d+)\)", name)
    if match is None:
        raise ValueError(f"Cannot parse Li2026 LEFT operator name: {name!r}")
    key = (int(match.group(3)), int(match.group(1)), match.group(2) or "")
    get_operator_spec(key)
    return key


def validate_operator_key(key: object) -> LeftKey:
    """Validate the shape, types, and metadata membership of a triplet key."""

    if not isinstance(key, tuple) or len(key) != 3:
        raise ValueError(
            "Li2026 LEFT operator key must be a "
            f"(dimension, index, quark_flavor) tuple, got {key!r}"
        )
    dimension, index, quark_flavor = key
    if (
        isinstance(dimension, bool)
        or not isinstance(dimension, Integral)
        or isinstance(index, bool)
        or not isinstance(index, Integral)
        or not isinstance(quark_flavor, str)
    ):
        raise TypeError(
            "Li2026 LEFT operator key must have types (int, int, str), "
            f"got {key!r}"
        )
    canonical_key = (int(dimension), int(index), quark_flavor)
    get_operator_spec(canonical_key)
    return canonical_key


def canonicalize_wilson_coefficients(
    *,
    left_wcs: Optional[Mapping[str, object]] = None,
    wc_triplets: Optional[Mapping[LeftKey, object]] = None,
) -> Dict[LeftKey, FlavorMatrix]:
    """Return one validated Li2026 Wilson mapping.

    Every supplied key and value is validated before physics evaluation.
    Supplying the same operator through both string and triplet interfaces (or
    through two string aliases) is rejected instead of relying on overwrite
    order.
    """

    canonical: Dict[LeftKey, FlavorMatrix] = {}
    origins: Dict[LeftKey, str] = {}

    def add(key: LeftKey, value: object, *, origin: str) -> None:
        if key in canonical:
            raise ValueError(
                f"Duplicate Li2026 LEFT operator {key}: "
                f"supplied by {origins[key]} and {origin}"
            )
        canonical[key] = validate_operator_coefficient(key, value)
        origins[key] = origin

    if wc_triplets is not None:
        for raw_key, value in wc_triplets.items():
            key = validate_operator_key(raw_key)
            add(key, value, origin=f"wc_triplets[{raw_key!r}]")

    if left_wcs is not None:
        for name, value in left_wcs.items():
            key = parse_operator_name(name)
            add(key, value, origin=f"left_wcs[{name!r}]")

    return canonical


__all__ = [
    "LeftKey",
    "LeptonNumberSector",
    "OperatorSpec",
    "LI2026_OPERATOR_SPECS",
    "OPERATOR_SPECS_BY_KEY",
    "get_operator_spec",
    "validate_operator_coefficient",
    "parse_operator_name",
    "validate_operator_key",
    "canonicalize_wilson_coefficients",
]
