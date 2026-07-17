from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from cevns_pyeft.rates.differential import _sm_left_dim6

Triplet = Tuple[int, int, str]


@dataclass(frozen=True)
class BasisElement:
    index: int
    name: str
    label: str
    triplet: Triplet


def li2026_left_basis() -> List[BasisElement]:
    raw: List[Tuple[str, Triplet, str]] = [('1', (5, 1, ''), 'C(5,1)'), ('2', (6, 1, 'u'), 'C(6,1)_u'), ('3', (6, 1, 'd'), 'C(6,1)_d'), ('4', (6, 2, 'u'), 'C(6,2)_u'), ('5', (6, 2, 'd'), 'C(6,2)_d'), ('6', (7, 1, 'u'), 'C(7,1)_u'), ('7', (7, 1, 'd'), 'C(7,1)_d'), ('8', (7, 2, 'u'), 'C(7,2)_u'), ('9', (7, 2, 'd'), 'C(7,2)_d'), ('10', (7, 3, 'u'), 'C(7,3)_u'), ('11', (7, 3, 'd'), 'C(7,3)_d'), ('12', (7, 4, 'u'), 'C(7,4)_u'), ('13', (7, 4, 'd'), 'C(7,4)_d'), ('14', (7, 5, 'u'), 'C(7,5)_u'), ('15', (7, 5, 'd'), 'C(7,5)_d'), ('16', (7, 6, ''), 'C(7,6)'), ('17', (7, 7, ''), 'C(7,7)'), ('18', (8, 1, 'u'), 'C(8,1)_u'), ('19', (8, 1, 'd'), 'C(8,1)_d'), ('20', (8, 2, 'u'), 'C(8,2)_u'), ('21', (8, 2, 'd'), 'C(8,2)_d'), ('22', (8, 9, ''), 'C(8,9)')]
    return [BasisElement(index=i, name=name, triplet=triplet, label=label) for i, (name, triplet, label) in enumerate(raw)]


def li2026_left_basis_current() -> List[BasisElement]:
    return li2026_left_basis()


def pair_index_for_basis(basis: Sequence[BasisElement]) -> np.ndarray:
    n = len(basis)
    return np.asarray([(a, b) for a in range(n) for b in range(a + 1, n)], dtype=int)


def coeff_vector_from_triplets(
    basis: Sequence[BasisElement],
    wc_triplets: Optional[Mapping[Triplet, complex]] = None,
    *,
    include_sm: bool = True,
    sin2thetaW: float = 0.2387,
) -> np.ndarray:
    merged: Dict[Triplet, complex] = dict(wc_triplets or {})
    if include_sm:
        for key, value in _sm_left_dim6(True, float(sin2thetaW)).items():
            merged[key] = complex(merged.get(key, 0.0 + 0j)) + complex(value)
    return np.asarray([complex(merged.get(be.triplet, 0.0 + 0j)) for be in basis], dtype=complex)


__all__ = [
    "Triplet",
    "BasisElement",
    "li2026_left_basis",
    "li2026_left_basis_current",
    "pair_index_for_basis",
    "coeff_vector_from_triplets",
]
