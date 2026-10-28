"""Li2026 operator coefficients using the same response-polynomial owner as Slow."""
import math
import numpy as np
from cevns_pyeft.foundation import constants as c
from cevns_pyeft.theory.kinematics import is_two_body_recoil_allowed
from .left_to_ci import left_to_ci
from .lec import DEFAULT_LECS
from .flavor import zero_flavor_matrix
from .operators import get_operator_spec
from .responses import RKinematics, coefficient_responses_R

CHANNELS = ('M', 'SigmaPP', 'SigmaP', 'PhiPP', 'PhiPT', 'Delta', 'MPhiPP', 'SigmaPDelta')
_CI_KEYS = (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14)


def _left_operator_template(key):
    matrix = zero_flavor_matrix()
    index = (0, 1) if get_operator_spec(key).lepton_number == 'LNV' else (0, 0)
    matrix[index] = 1
    return matrix, index


def operator_ci_units(basis_keys, *, E_nu_GeV: float, q0_GeV: float, q2_GeV2: float, qabs_GeV: float, qabs2_GeV2: float, mA_GeV: float, c10_mass_mode: str) -> np.ndarray:
    B = len(basis_keys)
    out = np.zeros((B, 15, 2), dtype=complex)
    for a, key in enumerate(basis_keys):
        template, flavor_index = _left_operator_template(key)
        ci_obj = left_to_ci({key: template}, E_nu=float(E_nu_GeV), q0=float(q0_GeV), q2=float(q2_GeV2), qabs=float(qabs_GeV), qabs2=float(qabs2_GeV2), mA=float(mA_GeV), c10_mass_mode=str(c10_mass_mode), lecs=DEFAULT_LECS)
        for i in _CI_KEYS:
            out[a, i, 0] = complex(ci_obj.p.get(i, zero_flavor_matrix())[flavor_index])
            out[a, i, 1] = complex(ci_obj.n.get(i, zero_flavor_matrix())[flavor_index])
    return out



def amplitude_coefficients_by_channel(*, E_nu_GeV, qabs_GeV, mA_GeV, mN_GeV, ci, W_slice, hermitianize=True):
    kin = RKinematics(Enu=E_nu_GeV, qabs=qabs_GeV, m_A=mA_GeV, m_N=mN_GeV)
    out = np.zeros((len(CHANNELS), ci.shape[0], ci.shape[0]), complex)
    for tau in (0, 1):
        for taup in (0, 1):
            values = coefficient_responses_R(ci, kin, tau=tau, taup=taup)
            for index, channel in enumerate(CHANNELS):
                out[index] += W_slice[index, tau, taup] * values[channel]
    if hermitianize:
        out = .5 * (out + out.swapaxes(-1, -2).conj())
    return out


def differential_coefficients(resp, target, energy_MeV, recoil_keV, basis_keys, *, c10_mass_mode):
    """cm²/keV coefficients H[channel,operator_i,operator_j] for each energy."""
    output = np.zeros((len(energy_MeV), len(CHANNELS), len(basis_keys), len(basis_keys)), complex)
    q0 = float(recoil_keV) * 1e-6
    mass = target.kinematic_mass_GeV
    qabs2 = 2 * mass * q0
    qabs = math.sqrt(qabs2)
    q2 = q0*q0 - qabs2
    y = (.5 * qabs * float(resp.basic['b']))**2
    weights = np.array([resp.W_np(name, y) if name in resp.responses else np.zeros((2, 2)) for name in CHANNELS])
    for index, energy in enumerate(energy_MeV):
        e = float(energy) * 1e-3
        if not is_two_body_recoil_allowed(e, q0, mass):
            continue
        ci = operator_ci_units(basis_keys, E_nu_GeV=e, q0_GeV=q0, q2_GeV2=q2, qabs_GeV=qabs,
                               qabs2_GeV2=qabs2, mA_GeV=mass, c10_mass_mode=c10_mass_mode)
        amplitude = amplitude_coefficients_by_channel(E_nu_GeV=e, qabs_GeV=qabs, mA_GeV=mass,
                              mN_GeV=DEFAULT_LECS.m_N, ci=ci, W_slice=weights)
        output[index] = amplitude * ((mass/(8*math.pi*e*e)) * c.GEV_INV2_TO_CM2) * c.keV
    return output
