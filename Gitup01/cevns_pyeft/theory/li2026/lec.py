from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from cevns_pyeft.foundation import constants as c

MEV_TO_GEV = 0.001

@dataclass(frozen=True)
class Li2026LECs:
    """Low-energy constants for the current Li2026 proof convention.

    Units: L1-L4 and g5-g9 are dimensionless; B0_m_u/B0_m_d are
    GeV^2; L5-L14, g1-g4, sigma terms, and masses are in GeV.
    """

    g_A: float = float(c.g_A)
    Sigma_ud: float = float(c.Sigma_ud)
    B0_m_u: float = float(c.LECs_known["B0mu"])
    B0_m_d: float = float(c.LECs_known["B0md"])
    L1: float = float(c.LECs_known["L1"])
    L2: float = float(c.LECs_known["L2"])
    L3: float = float(c.LECs_known["L3"])
    L4: float = float(c.LECs_known["L4"])
    L5: float = float(c.LECs_known["L5"])
    L6: float = float(c.LECs_known["L6"])
    L7: float = float(c.LECs_known["L7"])
    L8: float = float(c.LECs_known["L8"])
    L9: float = float(c.LECs_known["L9"])
    L10: float = float(c.LECs_known["L10"])
    L11: float = float(c.LECs_known["L11"])
    L12: float = float(c.LECs_known["L12"])
    L13: float = float(c.LECs_known["L13"])
    L14: float = float(c.LECs_known["L14"])
    sigma_u_p: float = 18.5 * MEV_TO_GEV
    sigma_d_p: float = 36.0 * MEV_TO_GEV
    sigma_u_n: float = 16.7 * MEV_TO_GEV
    sigma_d_n: float = 39.7 * MEV_TO_GEV
    g1: float = float(c.Lambda_chi)
    g2: float = float(c.Lambda_chi)
    g3: float = float(c.Lambda_chi)
    g4: float = float(c.Lambda_chi)
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
