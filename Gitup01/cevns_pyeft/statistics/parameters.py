from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

import numpy as np

from cevns_pyeft.foundation.constants import G_F
from cevns_pyeft.theory.li2026.flavor import FLAVOR_ORDER, FlavorMatrix, zero_flavor_matrix

Triplet = tuple[int, int, str]


@dataclass(frozen=True)
class VectorNSIParameters:
    epsilon_ee_uV: float = 0.0
    epsilon_ee_dV: float = 0.0
    epsilon_mumu_uV: float = 0.0
    epsilon_mumu_dV: float = 0.0
    epsilon_emu_uV: complex = 0.0
    epsilon_emu_dV: complex = 0.0
    epsilon_etau_uV: complex = 0.0
    epsilon_etau_dV: complex = 0.0
    epsilon_mutau_uV: complex = 0.0
    epsilon_mutau_dV: complex = 0.0
    epsilon_tautau_uV: float = 0.0
    epsilon_tautau_dV: float = 0.0


def _flavor_index(name: str) -> int:
    return FLAVOR_ORDER.index(name)


def _hermitian_epsilon_matrix(
    *,
    ee: complex = 0.0,
    mumu: complex = 0.0,
    tautau: complex = 0.0,
    emu: complex = 0.0,
    etau: complex = 0.0,
    mutau: complex = 0.0,
) -> FlavorMatrix:
    out = zero_flavor_matrix()
    out[_flavor_index("e"), _flavor_index("e")] = float(np.real(ee))
    out[_flavor_index("mu"), _flavor_index("mu")] = float(np.real(mumu))
    out[_flavor_index("tau"), _flavor_index("tau")] = float(np.real(tautau))
    pairs = {
        ("e", "mu"): complex(emu),
        ("e", "tau"): complex(etau),
        ("mu", "tau"): complex(mutau),
    }
    for (row, col), value in pairs.items():
        i = _flavor_index(row)
        j = _flavor_index(col)
        out[i, j] = value
        out[j, i] = np.conjugate(value)
    return out


def epsilon_matrix_to_np_wilson(epsilon: object) -> FlavorMatrix:
    matrix = np.asarray(epsilon, dtype=np.complex128)
    if matrix.shape != (3, 3):
        raise ValueError(f"epsilon matrix must have shape (3,3), got {matrix.shape}")
    if not np.allclose(matrix, matrix.conj().T, rtol=0.0, atol=1.0e-12):
        raise ValueError("vector NSI epsilon matrix must be Hermitian")
    return -math.sqrt(2.0) * float(G_F) * matrix


def vector_nsi_to_np_wilson(params: VectorNSIParameters) -> dict[Triplet, FlavorMatrix]:
    eps_u = _hermitian_epsilon_matrix(
        ee=params.epsilon_ee_uV,
        mumu=params.epsilon_mumu_uV,
        tautau=params.epsilon_tautau_uV,
        emu=params.epsilon_emu_uV,
        etau=params.epsilon_etau_uV,
        mutau=params.epsilon_mutau_uV,
    )
    eps_d = _hermitian_epsilon_matrix(
        ee=params.epsilon_ee_dV,
        mumu=params.epsilon_mumu_dV,
        tautau=params.epsilon_tautau_dV,
        emu=params.epsilon_emu_dV,
        etau=params.epsilon_etau_dV,
        mutau=params.epsilon_mutau_dV,
    )
    return {
        (6, 1, "u"): epsilon_matrix_to_np_wilson(eps_u),
        (6, 1, "d"): epsilon_matrix_to_np_wilson(eps_d),
    }


def merge_np_wilson(*parts: Mapping[Triplet, object]) -> dict[Triplet, FlavorMatrix]:
    out: dict[Triplet, FlavorMatrix] = {}
    for part in parts:
        for key, value in part.items():
            triplet = (int(key[0]), int(key[1]), str(key[2]))
            out[triplet] = np.asarray(value, dtype=np.complex128)
    return out


__all__ = [
    "Triplet",
    "VectorNSIParameters",
    "epsilon_matrix_to_np_wilson",
    "merge_np_wilson",
    "vector_nsi_to_np_wilson",
]


