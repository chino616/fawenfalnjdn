from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Mapping, Optional, Tuple, Union
import math
import numpy as np

from cevns_pyeft.foundation import constants as c
from cevns_pyeft.foundation.units import cm2_per_GeV_to_cm2_per_keV
from cevns_pyeft.sources.state import (
    NeutrinoState,
    ParticleKind,
    coerce_neutrino_state,
)
from cevns_pyeft.theory.kinematics import (
    is_two_body_recoil_allowed,
    two_body_recoil_max_GeV,
    validate_recoil_energy_GeV,
)
from cevns_pyeft.theory.li2026.amplitude import (
    FlavorKernelResult,
    flavor_kernel_onebody_li2026,
)
from cevns_pyeft.theory.li2026.cross_section import (
    amplitude_kernel_to_dsigma_cm2_per_GeV,
)
from cevns_pyeft.theory.li2026.flavor import (
    DEFAULT_KERNEL_ATOL,
    DEFAULT_KERNEL_RTOL,
    FlavorMatrix,
    NeutrinoFlavor,
    contract_density_kernel_grid,
    identity_flavor_matrix,
    validate_density_matrix,
    zero_flavor_matrix,
)
from cevns_pyeft.theory.li2026.left_to_ci import C10MassMode, LeftKey
from cevns_pyeft.theory.li2026.operators import (
    canonicalize_wilson_coefficients,
    parse_operator_name,
)
from cevns_pyeft.theory.li2026.responses import Basis

ArrayLike = Union[float, int, np.ndarray]
SourceSpecies = Literal['all', 'e', 'mu', 'mub', 'mmb']

# Temporary import compatibility for rates/counts.py.  SourceSpecies is the
# canonical name; neutrino Hilbert-space flavor is NeutrinoFlavor.
Flavor = SourceSpecies

def _asarray(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)

def _scalar_or_array(arr: np.ndarray, like: ArrayLike):
    if np.isscalar(like):
        return float(np.asarray(arr).reshape(-1)[0])
    return arr

def if_positive(x: ArrayLike) -> ArrayLike:
    xx = _asarray(x)
    yy = np.where(xx > 0.0, xx, 0.0)
    return _scalar_or_array(yy, x)

def _trapz(y: np.ndarray, x: np.ndarray) -> float:
    if y.size == 0:
        return 0.0
    trapezoid = getattr(np, 'trapezoid', None)
    if trapezoid is not None:
        return float(trapezoid(y, x))
    return float(np.trapz(y, x))

def _parse_left_wc_key(name: str) -> Tuple[int, int, str]:
    """Backward-compatible strict wrapper around canonical name parsing."""

    return parse_operator_name(name)

def _build_wc_triplets(
    left_wcs: Optional[Mapping[str, FlavorMatrix]] = None,
    wc_triplets: Optional[Mapping[LeftKey, FlavorMatrix]] = None,
) -> Dict[LeftKey, FlavorMatrix]:
    return canonicalize_wilson_coefficients(
        left_wcs=left_wcs,
        wc_triplets=wc_triplets,
    )

def _sm_left_dim6(
    include_sm: bool,
    sin2thetaW: float,
) -> Dict[LeftKey, FlavorMatrix]:
    if not include_sm:
        return {}
    s2 = float(sin2thetaW)
    pref = -(1.0 / math.sqrt(2.0)) * float(c.G_F)
    scalar_coefficients = {
        (6, 1, 'u'): pref * (1.0 - 8.0 / 3.0 * s2),
        (6, 1, 'd'): -pref * (1.0 - 4.0 / 3.0 * s2),
        (6, 2, 'u'): -pref,
        (6, 2, 'd'): pref,
    }
    identity = identity_flavor_matrix()
    return {
        key: value * identity
        for key, value in scalar_coefficients.items()
    }

@dataclass(frozen=True)
class AASResult:
    pieces: np.ndarray
    total: complex
    y: float
    q2: float
    q: float
    ER: float
    Enu: float
    basis: Basis

    def as_dict(self) -> Dict[str, Any]:
        labels = ['M', 'SigmaPP', 'SigmaP', 'PhiPP', 'PhiPT', 'Delta', 'MPhiPP', 'SigmaPDelta']
        return {'pieces': {k: complex(v) for k, v in zip(labels, self.pieces)}, 'pieces_list': [complex(v) for v in self.pieces], 'total': complex(self.total), 'kinematics': {'ER_GeV': float(self.ER), 'Enu_GeV': float(self.Enu), 'q_GeV': float(self.q), 'q2_GeV2': float(self.q2), 'y': float(self.y)}, 'basis': self.basis}

def emax_muon_dar_mev() -> float:
    mmu = float(getattr(c, 'm_mu', 0.1056583745))
    me = float(getattr(c, 'm_e', 0.00051099895))
    mmu_mev = float(c.from_energy_gev(mmu, 'MeV'))
    me_mev = float(c.from_energy_gev(me, 'MeV'))
    return (mmu_mev * mmu_mev - me_mev * me_mev) / (2.0 * mmu_mev)

def enr_max_keV(A: int, *, Emax_MeV: Optional[float]=None) -> float:
    if Emax_MeV is None:
        Emax_MeV = emax_muon_dar_mev()
    mA_GeV = A * float(getattr(c, 'AMU_GEV', 0.93149410372))
    endpoint_GeV = two_body_recoil_max_GeV(
        float(Emax_MeV) * c.MeV,
        mA_GeV,
    )
    return endpoint_GeV / c.keV

def eee_quenching_csi(enr_keV: ArrayLike) -> ArrayLike:
    a = 0.0554628
    b = 4.30681
    c3 = -111.707
    d4 = 840.384
    x = _asarray(enr_keV)
    y = x * 0.001
    out = 1000.0 * (a * y + b * y ** 2 + c3 * y ** 3 + d4 * y ** 4)
    return _scalar_or_array(out, enr_keV)

def p_smearing_csi(pe: ArrayLike, enr_keV: float) -> ArrayLike:
    Eee = float(eee_quenching_csi(enr_keV))
    if not Eee > 0.0:
        xx = _asarray(pe)
        out = np.zeros_like(xx)
        return _scalar_or_array(out, pe)
    a = 0.0749 / Eee
    b = 9.56 * Eee
    k = 1.0 + b
    lam = a * (1.0 + b)
    xx = _asarray(pe)
    xx_pos = np.where(xx > 0.0, xx, 0.0)
    log_pdf = k * math.log(lam) - math.lgamma(k) + b * np.log(np.maximum(xx_pos, 1e-300)) - lam * xx_pos
    pdf = np.exp(log_pdf)
    pdf = np.where(xx > 0.0, pdf, 0.0)
    return _scalar_or_array(pdf, pe)

@dataclass(frozen=True)
class DSigmaResult:
    dsigma_cm2_per_keV: ArrayLike
    aas: AASResult
    particle_kind: ParticleKind


@dataclass(frozen=True)
class DSigmaFlavorKernelResult:
    """Differential cross-section kernel before selecting an incoming state.

    ``kernel_cm2_per_keV`` has shape ``(3, 3)`` for scalar ``Enu_MeV`` and
    ``Enu_MeV.shape + (3, 3)`` for an energy array.  ``amplitude`` retains
    the last physical-energy metadata, while ``amplitude_index`` identifies
    its energy-grid entry so an energy-dependent source state produces
    consistent diagnostics.
    """

    kernel_cm2_per_keV: np.ndarray
    amplitude: Optional[FlavorKernelResult]
    amplitude_index: Optional[Tuple[int, ...]]


_RESPONSE_LABELS = (
    'M',
    'SigmaPP',
    'SigmaP',
    'PhiPP',
    'PhiPT',
    'Delta',
    'MPhiPP',
    'SigmaPDelta',
)


def _build_total_left_hat(
    *,
    left_wcs: Optional[Mapping[str, FlavorMatrix]],
    wc_triplets: Optional[Mapping[LeftKey, FlavorMatrix]],
    include_sm: bool,
    sin2thetaW: Optional[float],
) -> Dict[LeftKey, FlavorMatrix]:
    left_hat = _build_wc_triplets(
        left_wcs=left_wcs,
        wc_triplets=wc_triplets,
    )
    if include_sm:
        s2 = float(sin2thetaW) if sin2thetaW is not None else 0.23873
        for key, sm_matrix in _sm_left_dim6(True, s2).items():
            left_hat[key] = (
                left_hat.get(key, zero_flavor_matrix())
                + sm_matrix
            )
    return canonicalize_wilson_coefficients(wc_triplets=left_hat)


def differential_flavor_kernel_nn(
    resp: Any,
    ER_keV: float,
    Enu_MeV: ArrayLike,
    *,
    basis: Basis = 'np',
    left_wcs: Optional[Mapping[str, FlavorMatrix]] = None,
    wc_triplets: Optional[Mapping[LeftKey, FlavorMatrix]] = None,
    include_sm: bool = False,
    debug_units: bool = False,
    sin2thetaW: Optional[float] = None,
    c10_mass_mode: C10MassMode = 'quark_mass_resolved',
) -> DSigmaFlavorKernelResult:
    """Return the differential CEvNS kernel in incoming-flavor space."""

    A = int(resp.basic.get('A'))
    mA_GeV = A * float(getattr(c, 'AMU_GEV', 0.93149410372))
    ER_GeV = validate_recoil_energy_GeV(float(ER_keV) * c.keV)
    Enu_arr = _asarray(Enu_MeV)
    out = np.zeros(Enu_arr.shape + (3, 3), dtype=np.complex128)
    amplitude_last: Optional[FlavorKernelResult] = None
    amplitude_index: Optional[Tuple[int, ...]] = None
    left_hat = _build_total_left_hat(
        left_wcs=left_wcs,
        wc_triplets=wc_triplets,
        include_sm=include_sm,
        sin2thetaW=sin2thetaW,
    )

    for idx, Enu1 in np.ndenumerate(Enu_arr):
        Enu_GeV = float(c.to_energy_gev(float(Enu1), 'MeV'))
        if not math.isfinite(Enu_GeV) or Enu_GeV < 0.0:
            raise ValueError("Enu_MeV entries must be non-negative and finite")
        if Enu_GeV == 0.0:
            # Rates grids may include the zero-flux integration endpoint.  The
            # strict Li2026 theory core itself rejects E_nu <= 0.
            continue
        if not is_two_body_recoil_allowed(Enu_GeV, ER_GeV, mA_GeV):
            continue

        amplitude = flavor_kernel_onebody_li2026(
            resp,
            E_nu_GeV=Enu_GeV,
            ER_keV=float(ER_keV),
            left_hat=left_hat,
            basis=basis,
            c10_mass_mode=c10_mass_mode,
        )
        amplitude_last = amplitude
        amplitude_index = idx
        qabs2 = 2.0 * mA_GeV * ER_GeV
        qabs = math.sqrt(max(qabs2, 0.0))
        b_ho = float(resp.basic.get('b'))
        y = (0.5 * qabs * b_ho) ** 2
        if debug_units:
            print('[units-check]')
            print(f'ER = {ER_GeV:.6e} GeV, Enu = {Enu_GeV:.6e} GeV')
            print(f'mA = {mA_GeV:.6e} GeV')
            print(
                f'qabs = {qabs:.6e} GeV, '
                f'q2 = {amplitude.q2:.6e} GeV^2, y = {y:.6e}'
            )
            print(f'basis = {basis}')
        kernel_cm2_per_GeV = amplitude_kernel_to_dsigma_cm2_per_GeV(
            amplitude.kernel,
            E_nu_GeV=Enu_GeV,
            m_A_GeV=mA_GeV,
        )
        out[idx] = cm2_per_GeV_to_cm2_per_keV(kernel_cm2_per_GeV)

    return DSigmaFlavorKernelResult(
        kernel_cm2_per_keV=out,
        amplitude=amplitude_last,
        amplitude_index=amplitude_index,
    )


def _aas_for_density(
    amplitude: FlavorKernelResult,
    rho: FlavorMatrix,
) -> AASResult:
    rho = validate_density_matrix(rho)
    pieces = np.asarray(
        [
            np.trace(
                rho
                @ amplitude.pieces.get(label, zero_flavor_matrix())
            )
            for label in _RESPONSE_LABELS
        ],
        dtype=np.complex128,
    )
    total = complex(np.trace(rho @ amplitude.kernel))
    return AASResult(
        pieces=pieces,
        total=total,
        y=float(amplitude.y),
        q2=float(amplitude.q2),
        q=float(amplitude.qabs),
        ER=float(amplitude.ER_keV) * 1e-06,
        Enu=float(amplitude.E_nu_GeV),
        basis=amplitude.basis,
    )


def _zero_aas_result(
    resp: Any,
    *,
    ER_keV: float,
    Enu_MeV: ArrayLike,
    basis: Basis,
) -> AASResult:
    A = int(resp.basic.get('A'))
    mA_GeV = A * float(getattr(c, 'AMU_GEV', 0.93149410372))
    Enu_arr = _asarray(Enu_MeV)
    Enu0_MeV = float(np.ravel(Enu_arr)[0]) if np.size(Enu_arr) > 0 else 0.0
    Enu0_GeV = float(c.to_energy_gev(Enu0_MeV, 'MeV'))
    ER_GeV = float(ER_keV) * 1e-06
    qabs2 = 2.0 * mA_GeV * ER_GeV
    qabs = math.sqrt(max(qabs2, 0.0))
    b_ho = float(resp.basic.get('b'))
    y = (0.5 * qabs * b_ho) ** 2
    q2 = ER_GeV * ER_GeV - qabs2
    return AASResult(
        pieces=np.zeros(len(_RESPONSE_LABELS), dtype=np.complex128),
        total=0.0 + 0.0j,
        y=float(y),
        q2=float(q2),
        q=float(qabs),
        ER=float(ER_GeV),
        Enu=float(Enu0_GeV),
        basis=basis,
    )


def differential_cross_section_nn(
    resp: Any,
    ER_keV: float,
    Enu_MeV: ArrayLike,
    *,
    rho: object,
    particle_kind: Optional[ParticleKind] = None,
    basis: Basis = 'np',
    left_wcs: Optional[Mapping[str, FlavorMatrix]] = None,
    wc_triplets: Optional[Mapping[LeftKey, FlavorMatrix]] = None,
    include_sm: bool = False,
    debug_units: bool = False,
    sin2thetaW: Optional[float] = None,
    c10_mass_mode: C10MassMode = 'quark_mass_resolved',
) -> DSigmaResult:
    """Contract a Flavor kernel with a canonical neutrino source state.

    rho may be a NeutrinoState or a raw constant/energy-dependent density
    array.  Raw arrays require an explicit particle_kind.  P2 records the
    particle label without changing the existing antineutrino interaction
    convention; sign/helicity changes require a separate audit.
    """

    state = coerce_neutrino_state(
        rho,
        particle_kind=particle_kind,
    )
    energy_shape = _asarray(Enu_MeV).shape
    rho_grid = state.density_for_energy_shape(energy_shape)
    flavor_result = differential_flavor_kernel_nn(
        resp,
        ER_keV=ER_keV,
        Enu_MeV=Enu_MeV,
        basis=basis,
        left_wcs=left_wcs,
        wc_triplets=wc_triplets,
        include_sm=include_sm,
        debug_units=debug_units,
        sin2thetaW=sin2thetaW,
        c10_mass_mode=c10_mass_mode,
    )
    contracted = contract_density_kernel_grid(
        rho_grid,
        flavor_result.kernel_cm2_per_keV,
    )
    dsigma = _scalar_or_array(np.asarray(contracted), Enu_MeV)

    if flavor_result.amplitude is None:
        aas = _zero_aas_result(
            resp,
            ER_keV=ER_keV,
            Enu_MeV=Enu_MeV,
            basis=basis,
        )
    else:
        if flavor_result.amplitude_index is None:
            raise RuntimeError(
                "amplitude metadata is missing its neutrino-energy index"
            )
        if rho_grid.shape == (3, 3):
            rho_for_aas = rho_grid
        else:
            rho_for_aas = rho_grid[flavor_result.amplitude_index]
        aas = _aas_for_density(
            flavor_result.amplitude,
            rho_for_aas,
        )

    return DSigmaResult(
        dsigma_cm2_per_keV=dsigma,
        aas=aas,
        particle_kind=state.particle_kind,
    )

__all__ = [
    "ArrayLike",
    "Basis",
    "SourceSpecies",
    "NeutrinoFlavor",
    "ParticleKind",
    "NeutrinoState",
    "Flavor",
    "_asarray",
    "_scalar_or_array",
    "_trapz",
    "AASResult",
    "DSigmaFlavorKernelResult",
    "DSigmaResult",
    "_parse_left_wc_key",
    "_build_wc_triplets",
    "_sm_left_dim6",
    "emax_muon_dar_mev",
    "enr_max_keV",
    "eee_quenching_csi",
    "p_smearing_csi",
    "differential_flavor_kernel_nn",
    "differential_cross_section_nn",
]
