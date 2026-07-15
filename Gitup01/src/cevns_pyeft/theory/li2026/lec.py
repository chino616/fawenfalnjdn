from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from cevns_pyeft.foundation import constants as c

MEV_TO_GEV = 0.001

@dataclass(frozen=True)
class Li2026LECs:
    g_A: float = float(c.g_A)
    Sigma_ud: float = float(c.Sigma_ud)
    L1: float = 1.355
    L2: float = -1.535
    L3: float = 0.6377
    L4: float = -0.22
    L5: float = 0.41 * MEV_TO_GEV
    L6: float = 0.49 * MEV_TO_GEV
    L7: float = -1.68 * MEV_TO_GEV
    L8: float = 0.88 * MEV_TO_GEV
    L9: float = 11.52 * MEV_TO_GEV
    L10: float = 24.05 * MEV_TO_GEV
    L11: float = -42.96 * MEV_TO_GEV
    L12: float = -36.75 * MEV_TO_GEV
    L13: float = -50.4 * MEV_TO_GEV
    L14: float = -0.306
    sigma_u_p: float = 16.3 * MEV_TO_GEV
    sigma_d_p: float = 30.6 * MEV_TO_GEV
    sigma_u_n: float = 14.5 * MEV_TO_GEV
    sigma_d_n: float = 34.5 * MEV_TO_GEV
    g1: float = 1.0
    g2: float = 1.0
    g3: float = 1.0
    g4: float = 1.0
    g5: float = 1.0
    g6: float = 1.0
    g7: float = 1.0
    g8: float = 1.0
    g9: float = 1.0
    m_u: float = 2.16 * MEV_TO_GEV
    m_d: float = 4.67 * MEV_TO_GEV
    m_pi: float = float(c.m_pi_charged)
    m_N: float = float(c.m_N)
DEFAULT_LECS = Li2026LECs()

def as_dict(lecs: Li2026LECs=DEFAULT_LECS) -> Dict[str, float]:
    return lecs.__dict__.copy()

__all__ = [
    "MEV_TO_GEV",
    "Li2026LECs",
    "DEFAULT_LECS",
    "as_dict",
]
