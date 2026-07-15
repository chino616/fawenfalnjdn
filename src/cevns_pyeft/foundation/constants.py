from __future__ import annotations

from collections import OrderedDict
from typing import Literal, Union
import math
import numpy as np

try:
    import scipy.constants
    pc = scipy.constants.physical_constants
except Exception:
    pc = {}
ArrayLike = Union[float, int, np.ndarray]
TeV = 1000.0
GeV = 1.0
MeV = 0.001
keV = 1e-06
eV = 1e-09
meV = 1e-12
HBARC_MEV_FM = 197.3269804
HBAR_MEV_S = 6.582119569e-22
HBARC_GEV_FM = HBARC_MEV_FM * MeV
HBAR_GEV_S = HBAR_MEV_S * MeV
C_M_S = 299792458.0
GEV_INV2_TO_MBARN = 0.3893793721
GEV_INV2_TO_CM2 = GEV_INV2_TO_MBARN * 1e-27
CM2_TO_GEV_INV2 = 1.0 / GEV_INV2_TO_CM2
INV_GEV_TO_FM = HBARC_GEV_FM
FM_TO_INV_GEV = 1.0 / INV_GEV_TO_FM
fm = FM_TO_INV_GEV
CM_TO_INV_GEV = 10000000000000.0 * FM_TO_INV_GEV
M_TO_INV_GEV = 1000000000000000.0 * FM_TO_INV_GEV
INV_GEV_TO_CM = 1.0 / CM_TO_INV_GEV
INV_GEV_TO_M = 1.0 / M_TO_INV_GEV
INV_GEV_TO_S = HBAR_GEV_S
S_TO_INV_GEV = 1.0 / INV_GEV_TO_S
SEC_PER_DAY = 86400.0
SEC_PER_YEAR = 365.25 * SEC_PER_DAY
DAY_TO_INV_GEV = SEC_PER_DAY * S_TO_INV_GEV
YEAR_TO_INV_GEV = SEC_PER_YEAR * S_TO_INV_GEV

def _pc_value(key: str, default: float) -> float:
    try:
        return float(pc[key][0])
    except Exception:
        return float(default)
G_F = _pc_value('Fermi coupling constant', 1.1663787e-05)
alpha_em = _pc_value('fine-structure constant', 1.0 / 137.035999084)
e_charge = math.sqrt(4.0 * math.pi * alpha_em)
e_em = e_charge
vev = 246.0 * GeV
m_W = 80.379 * GeV
m_Z = 91.1876 * GeV
Lambda_EW_match = m_W
Lambda_chi = 1.0 * GeV
mu_had = 1.0 * GeV
mu_2GeV = 2.0 * GeV
m_p = _pc_value('proton mass energy equivalent in MeV', 938.27208816) * MeV
m_n = _pc_value('neutron mass energy equivalent in MeV', 939.56542052) * MeV
m_N = 0.5 * (m_p + m_n)
m_pi_charged = _pc_value('charged pion mass energy equivalent in MeV', 139.57039) * MeV
m_pi0 = 134.9768 * MeV
m_mu = _pc_value('muon mass energy equivalent in MeV', 105.6583745) * MeV
m_e = _pc_value('electron mass energy equivalent in MeV', 0.51099895) * MeV
AMU_GEV = _pc_value('atomic mass constant energy equivalent in MeV', 931.49410372) * MeV
mu_p_magnetic = 2.79284734463
mu_n_magnetic = -1.91304273
g_A = 1.2754
Sigma_ud = 0.397
N_c = 3
C_F = (N_c ** 2 - 1.0) / (2.0 * N_c)
EnergyUnit = Literal['GeV', 'TeV', 'MeV', 'keV', 'eV', 'meV']
LengthUnit = Literal['GeV^-1', 'fm', 'cm', 'm']
TimeUnit = Literal['GeV^-1', 's', 'day', 'yr']
XsecUnit = Literal['GeV^-2', 'cm^2', 'barn', 'mb', 'ub', 'nb', 'pb', 'fb']
FluxUnit = Literal['cm^-2 GeV^-1', 'cm^-2 MeV^-1', 'cm^-2 keV^-1', 'nat']

def _asarray(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)

def to_energy_gev(x: ArrayLike, unit: EnergyUnit='GeV') -> np.ndarray:
    scale = {'TeV': TeV, 'GeV': GeV, 'MeV': MeV, 'keV': keV, 'eV': eV, 'meV': meV}[unit]
    return _asarray(x) * scale

def from_energy_gev(x_gev: ArrayLike, unit: EnergyUnit='GeV') -> np.ndarray:
    scale = {'TeV': TeV, 'GeV': GeV, 'MeV': MeV, 'keV': keV, 'eV': eV, 'meV': meV}[unit]
    return _asarray(x_gev) / scale

def to_length_invgev(x: ArrayLike, unit: LengthUnit='GeV^-1') -> np.ndarray:
    x = _asarray(x)
    if unit == 'GeV^-1':
        return x
    if unit == 'fm':
        return x * FM_TO_INV_GEV
    if unit == 'cm':
        return x * CM_TO_INV_GEV
    if unit == 'm':
        return x * M_TO_INV_GEV
    raise ValueError(f'Unknown length unit: {unit}')

def from_length_invgev(x_invgev: ArrayLike, unit: LengthUnit='GeV^-1') -> np.ndarray:
    x = _asarray(x_invgev)
    if unit == 'GeV^-1':
        return x
    if unit == 'fm':
        return x * INV_GEV_TO_FM
    if unit == 'cm':
        return x * INV_GEV_TO_CM
    if unit == 'm':
        return x * INV_GEV_TO_M
    raise ValueError(f'Unknown length unit: {unit}')

def to_time_invgev(x: ArrayLike, unit: TimeUnit='GeV^-1') -> np.ndarray:
    x = _asarray(x)
    if unit == 'GeV^-1':
        return x
    if unit == 's':
        return x * S_TO_INV_GEV
    if unit == 'day':
        return x * DAY_TO_INV_GEV
    if unit == 'yr':
        return x * YEAR_TO_INV_GEV
    raise ValueError(f'Unknown time unit: {unit}')

def from_time_invgev(x_invgev: ArrayLike, unit: TimeUnit='GeV^-1') -> np.ndarray:
    x = _asarray(x_invgev)
    if unit == 'GeV^-1':
        return x
    if unit == 's':
        return x * INV_GEV_TO_S
    if unit == 'day':
        return x * (INV_GEV_TO_S / SEC_PER_DAY)
    if unit == 'yr':
        return x * (INV_GEV_TO_S / SEC_PER_YEAR)
    raise ValueError(f'Unknown time unit: {unit}')

def to_xsec_gev_inv2(x: ArrayLike, unit: XsecUnit='GeV^-2') -> np.ndarray:
    x = _asarray(x)
    if unit == 'GeV^-2':
        return x
    if unit == 'cm^2':
        return x * CM2_TO_GEV_INV2
    factors_cm2 = {'barn': 1e-24, 'mb': 1e-27, 'ub': 1e-30, 'nb': 1e-33, 'pb': 1e-36, 'fb': 1e-39}
    if unit in factors_cm2:
        return x * factors_cm2[unit] * CM2_TO_GEV_INV2
    raise ValueError(f'Unknown xsec unit: {unit}')

def from_xsec_gev_inv2(x_gev_inv2: ArrayLike, unit: XsecUnit='GeV^-2') -> np.ndarray:
    x = _asarray(x_gev_inv2)
    if unit == 'GeV^-2':
        return x
    if unit == 'cm^2':
        return x * GEV_INV2_TO_CM2
    factors_cm2 = {'barn': 1e-24, 'mb': 1e-27, 'ub': 1e-30, 'nb': 1e-33, 'pb': 1e-36, 'fb': 1e-39}
    if unit in factors_cm2:
        return x * GEV_INV2_TO_CM2 / factors_cm2[unit]
    raise ValueError(f'Unknown xsec unit: {unit}')

def to_flux_natural(x: ArrayLike, unit: FluxUnit='cm^-2 GeV^-1') -> np.ndarray:
    x = _asarray(x)
    if unit == 'nat':
        return x
    if unit == 'cm^-2 GeV^-1':
        return x * GEV_INV2_TO_CM2
    if unit == 'cm^-2 MeV^-1':
        return x * (1000.0 * GEV_INV2_TO_CM2)
    if unit == 'cm^-2 keV^-1':
        return x * (1000000.0 * GEV_INV2_TO_CM2)
    raise ValueError(f'Unknown flux unit: {unit}')

def from_flux_natural(x_nat: ArrayLike, unit: FluxUnit='cm^-2 GeV^-1') -> np.ndarray:
    x = _asarray(x_nat)
    if unit == 'nat':
        return x
    if unit == 'cm^-2 GeV^-1':
        return x / GEV_INV2_TO_CM2
    if unit == 'cm^-2 MeV^-1':
        return x / (1000.0 * GEV_INV2_TO_CM2)
    if unit == 'cm^-2 keV^-1':
        return x / (1000000.0 * GEV_INV2_TO_CM2)
    raise ValueError(f'Unknown flux unit: {unit}')

def b_ho_invgev(A: int | float) -> float:
    A = float(A)
    b_fm = math.sqrt(41.467 / (45.0 * A ** (-1.0 / 3.0) - 25.0 * A ** (-2.0 / 3.0)))
    return b_fm * FM_TO_INV_GEV

def y_from_qb(q_gev: float, b_invgev: float) -> float:
    return (q_gev * b_invgev) ** 2 / 4.0
LECs_known = OrderedDict([('B0mu', 6200.0 * MeV ** 2), ('B0md', 13300.0 * MeV ** 2), ('L1', 1.355), ('L2', -1.535), ('L3', 0.6377), ('L4', -0.22), ('L5', 0.41 * MeV), ('L6', 0.49 * MeV), ('L7', -1.68 * MeV), ('L8', 0.88 * MeV), ('L9', 11.52 * MeV), ('L10', 24.05 * MeV), ('L11', -42.96 * MeV), ('L12', -36.75 * MeV), ('L13', -50.4 * MeV), ('L14', -0.306 * GeV)])
LECs_known_sigma = OrderedDict([('B0mu', 400.0 * MeV ** 2), ('B0md', 400.0 * MeV ** 2), ('L1', 0.014), ('L2', 0.01), ('L3', 0.0007), ('L4', 0.01), ('L5', 0.17 * MeV), ('L6', 0.8 * MeV), ('L7', 0.25 * MeV), ('L8', 0.2 * MeV), ('L9', 0.25 * MeV), ('L10', 0.48 * MeV), ('L11', 0.24 * MeV), ('L12', 0.36 * MeV), ('L13', 0.6 * MeV), ('L14', 0.028 * GeV)])
LECs_unknown_orders = OrderedDict([('g1pi', 'O(Lambda_chi)'), ('g2pi', 'O(Lambda_chi)'), ('g3pi', 'O(Lambda_chi)'), ('g4pi', 'O(Lambda_chi)'), ('g5pi', 'O(Lambda_chi)'), ('g6pi', 'O(1)'), ('g7pi', 'O(Lambda_chi**2)'), ('g8pi', 'O(Lambda_chi**2)'), ('g1', 'O(Lambda_chi)'), ('g2', 'O(Lambda_chi)'), ('g3', 'O(Lambda_chi)'), ('g4', 'O(Lambda_chi)'), ('g5', 'O(1)'), ('g6', 'O(1)'), ('g7', 'O(1)'), ('g8', 'O(1)'), ('g9', 'O(1)')])
LECs_unknown_NDA = OrderedDict([('g1pi', Lambda_chi), ('g2pi', Lambda_chi), ('g3pi', Lambda_chi), ('g4pi', Lambda_chi), ('g5pi', Lambda_chi), ('g6pi', 1.0), ('g7pi', Lambda_chi ** 2), ('g8pi', Lambda_chi ** 2), ('g1', Lambda_chi), ('g2', Lambda_chi), ('g3', Lambda_chi), ('g4', Lambda_chi), ('g5', 1.0), ('g6', 1.0), ('g7', 1.0), ('g8', 1.0), ('g9', 1.0)])
LECs = OrderedDict()
LECs.update(LECs_known)
LECs.update(LECs_unknown_NDA)
LECs_latex = {'B0mu': 'B_0 m_u', 'B0md': 'B_0 m_d', **{f'L{i}': f'L_{i}' for i in range(1, 15)}, **{f'g{i}pi': f'g^\\\\pi_{i}' for i in range(1, 9)}, **{f'g{i}': f'g_{i}' for i in range(1, 10)}}
LEFT_WCs_LNC = OrderedDict([('C1u(6)', 0.0), ('C1d(6)', 0.0), ('C2u(6)', 0.0), ('C2d(6)', 0.0), ('C1u(7)', 0.0), ('C1d(7)', 0.0), ('C2u(7)', 0.0), ('C2d(7)', 0.0), ('C1u(8)', 0.0), ('C1d(8)', 0.0), ('C2u(8)', 0.0), ('C2d(8)', 0.0), ('C3u(8)', 0.0), ('C3d(8)', 0.0), ('C4u(8)', 0.0), ('C4d(8)', 0.0), ('C5u(8)', 0.0), ('C5d(8)', 0.0), ('C6u(8)', 0.0), ('C6d(8)', 0.0), ('C7u(8)', 0.0), ('C7d(8)', 0.0), ('C8u(8)', 0.0), ('C8d(8)', 0.0), ('C9(8)', 0.0)])
LEFT_WCs_LNV = OrderedDict([('C1(5)', 0.0), ('C3u(7)', 0.0), ('C3d(7)', 0.0), ('C4u(7)', 0.0), ('C4d(7)', 0.0), ('C5u(7)', 0.0), ('C5d(7)', 0.0), ('C6(7)', 0.0), ('C7(7)', 0.0)])
LEFT_WCs = OrderedDict()
LEFT_WCs.update(LEFT_WCs_LNV)
LEFT_WCs.update(LEFT_WCs_LNC)
LEFT_WC_DIM = {**{k: 5 for k in LEFT_WCs if k.endswith('(5)')}, **{k: 6 for k in LEFT_WCs if k.endswith('(6)')}, **{k: 7 for k in LEFT_WCs if k.endswith('(7)')}, **{k: 8 for k in LEFT_WCs if k.endswith('(8)')}}
LEFT_WC_MASS_DIMENSION = {k: 4 - v for k, v in LEFT_WC_DIM.items()}
LEFT_WCs_latex = {name: f"\\hat{{C}}_{{{name.split('(')[0].replace('u', 'u').replace('d', 'd')}}}^{{({LEFT_WC_DIM[name]})}}" for name in LEFT_WCs}
LEFT_WCs_latex.update({'C1(5)': '\\hat{C}^{(5)}_1', 'C1u(6)': '\\hat{C}^{u,(6)}_1', 'C1d(6)': '\\hat{C}^{d,(6)}_1', 'C2u(6)': '\\hat{C}^{u,(6)}_2', 'C2d(6)': '\\hat{C}^{d,(6)}_2', 'C1u(7)': '\\hat{C}^{u,(7)}_1', 'C1d(7)': '\\hat{C}^{d,(7)}_1', 'C2u(7)': '\\hat{C}^{u,(7)}_2', 'C2d(7)': '\\hat{C}^{d,(7)}_2', 'C3u(7)': '\\hat{C}^{u,(7)}_3', 'C3d(7)': '\\hat{C}^{d,(7)}_3', 'C4u(7)': '\\hat{C}^{u,(7)}_4', 'C4d(7)': '\\hat{C}^{d,(7)}_4', 'C5u(7)': '\\hat{C}^{u,(7)}_5', 'C5d(7)': '\\hat{C}^{d,(7)}_5', 'C6(7)': '\\hat{C}^{(7)}_6', 'C7(7)': '\\hat{C}^{(7)}_7', 'C1u(8)': '\\hat{C}^{u,(8)}_1', 'C1d(8)': '\\hat{C}^{d,(8)}_1', 'C2u(8)': '\\hat{C}^{u,(8)}_2', 'C2d(8)': '\\hat{C}^{d,(8)}_2', 'C3u(8)': '\\hat{C}^{u,(8)}_3', 'C3d(8)': '\\hat{C}^{d,(8)}_3', 'C4u(8)': '\\hat{C}^{u,(8)}_4', 'C4d(8)': '\\hat{C}^{d,(8)}_4', 'C5u(8)': '\\hat{C}^{u,(8)}_5', 'C5d(8)': '\\hat{C}^{d,(8)}_5', 'C6u(8)': '\\hat{C}^{u,(8)}_6', 'C6d(8)': '\\hat{C}^{d,(8)}_6', 'C7u(8)': '\\hat{C}^{u,(8)}_7', 'C7d(8)': '\\hat{C}^{d,(8)}_7', 'C8u(8)': '\\hat{C}^{u,(8)}_8', 'C8d(8)': '\\hat{C}^{d,(8)}_8', 'C9(8)': '\\hat{C}^{(8)}_9'})
LEFT_QCD_RUNNING = {'C1(5)': 'none', 'C1u(6)': 'none', 'C1d(6)': 'none', 'C2u(6)': 'none', 'C2d(6)': 'none', 'C1u(7)': 'multiplicative: +2*C_F*alpha_s/(4*pi)', 'C1d(7)': 'multiplicative: +2*C_F*alpha_s/(4*pi)', 'C2u(7)': 'multiplicative: +2*C_F*alpha_s/(4*pi)', 'C2d(7)': 'multiplicative: +2*C_F*alpha_s/(4*pi)', 'C3u(7)': 'multiplicative: +2*C_F*alpha_s/(4*pi)', 'C3d(7)': 'multiplicative: +2*C_F*alpha_s/(4*pi)', 'C4u(7)': 'multiplicative: -6*C_F*alpha_s/(4*pi)', 'C4d(7)': 'multiplicative: -6*C_F*alpha_s/(4*pi)', 'C5u(7)': 'multiplicative: -6*C_F*alpha_s/(4*pi)', 'C5d(7)': 'multiplicative: -6*C_F*alpha_s/(4*pi)', 'C6(7)': 'none', 'C7(7)': 'none', 'C1u(8)': 'mixes with C5u(8)', 'C1d(8)': 'mixes with C5d(8)', 'C2u(8)': 'mixes with C6u(8)', 'C2d(8)': 'mixes with C6d(8)', 'C3u(8)': 'explicit QCD running not available in paper', 'C3d(8)': 'explicit QCD running not available in paper', 'C4u(8)': 'none', 'C4d(8)': 'none', 'C5u(8)': 'mixes with C1u(8)', 'C5d(8)': 'mixes with C1d(8)', 'C6u(8)': 'mixes with C2u(8)', 'C6d(8)': 'mixes with C2d(8)', 'C7u(8)': 'explicit QCD running not available in paper', 'C7d(8)': 'explicit QCD running not available in paper', 'C8u(8)': 'none', 'C8d(8)': 'none', 'C9(8)': 'explicit QCD running not available in paper'}
NR_operators = OrderedDict([(f'O{i}', 0.0) for i in range(1, 15)])
NR_coefficients_p = OrderedDict([(f'c{i},p', 0.0) for i in range(1, 15)])
NR_coefficients_n = OrderedDict([(f'c{i},n', 0.0) for i in range(1, 15)])
SMEFT_WCs = OrderedDict([('OLHB', 0.0), ('OLHW', 0.0), ('O5', 0.0), ('OH', 0.0), ('OHW', 0.0), ('OHB', 0.0), ('OHWB', 0.0), ('OHD', 0.0), ('OHl(1)', 0.0), ('OHl(3)', 0.0), ('OHq(1)', 0.0), ('OHq(3)', 0.0), ('OHu', 0.0), ('OHd', 0.0), ('OuB', 0.0), ('OuW', 0.0), ('OdB', 0.0), ('OdW', 0.0), ('Olq(1)', 0.0), ('Olq(3)', 0.0), ('Olu', 0.0), ('Old', 0.0), ('OQuLLH', 0.0), ('OdLQLH1', 0.0), ('OdLQLH2', 0.0), ('Ol2G2D', 0.0), ('Ol2q2G(1)', 0.0), ('Ol2q2G(2)', 0.0), ('Ol2q2G(3)', 0.0), ('Ol2q2G(4)', 0.0), ('Ol2u2G(1)', 0.0), ('Ol2u2G(2)', 0.0), ('Ol2d2G(1)', 0.0), ('Ol2d2G(2)', 0.0), ('Ol2q2D2(2)', 0.0), ('Ol2q2D2(4)', 0.0), ('Ol2u2D2(2)', 0.0), ('Ol2d2D2(2)', 0.0)])
SMEFT_WC_DIM = OrderedDict([('OLHB', 7), ('OLHW', 7), ('O5', 5), ('OH', 6), ('OHW', 6), ('OHB', 6), ('OHWB', 6), ('OHD', 6), ('OHl(1)', 6), ('OHl(3)', 6), ('OHq(1)', 6), ('OHq(3)', 6), ('OHu', 6), ('OHd', 6), ('OuB', 6), ('OuW', 6), ('OdB', 6), ('OdW', 6), ('Olq(1)', 6), ('Olq(3)', 6), ('Olu', 6), ('Old', 6), ('OQuLLH', 7), ('OdLQLH1', 7), ('OdLQLH2', 7), ('Ol2G2D', 8), ('Ol2q2G(1)', 8), ('Ol2q2G(2)', 8), ('Ol2q2G(3)', 8), ('Ol2q2G(4)', 8), ('Ol2u2G(1)', 8), ('Ol2u2G(2)', 8), ('Ol2d2G(1)', 8), ('Ol2d2G(2)', 8), ('Ol2q2D2(2)', 8), ('Ol2q2D2(4)', 8), ('Ol2u2D2(2)', 8), ('Ol2d2D2(2)', 8)])
SMEFT_WC_MASS_DIMENSION = {k: 4 - d for k, d in SMEFT_WC_DIM.items()}
SMEFT_WCs_latex = {'OLHB': 'C_{LHB}', 'OLHW': 'C_{LHW}', 'O5': 'C_{5}', 'OH': 'C_H', 'OHW': 'C_{HW}', 'OHB': 'C_{HB}', 'OHWB': 'C_{HWB}', 'OHD': 'C_{HD}', 'OHl(1)': 'C_{H\\ell}^{(1)}', 'OHl(3)': 'C_{H\\ell}^{(3)}', 'OHq(1)': 'C_{Hq}^{(1)}', 'OHq(3)': 'C_{Hq}^{(3)}', 'OHu': 'C_{Hu}', 'OHd': 'C_{Hd}', 'OuB': 'C_{uB}', 'OuW': 'C_{uW}', 'OdB': 'C_{dB}', 'OdW': 'C_{dW}', 'Olq(1)': 'C_{\\ell q}^{(1)}', 'Olq(3)': 'C_{\\ell q}^{(3)}', 'Olu': 'C_{\\ell u}', 'Old': 'C_{\\ell d}', 'OQuLLH': 'C_{QuLLH}', 'OdLQLH1': 'C_{dLQLH1}', 'OdLQLH2': 'C_{dLQLH2}', 'Ol2G2D': 'C_{\\ell^2 G^2 D}', 'Ol2q2G(1)': 'C_{\\ell^2 q^2 G}^{(1)}', 'Ol2q2G(2)': 'C_{\\ell^2 q^2 G}^{(2)}', 'Ol2q2G(3)': 'C_{\\ell^2 q^2 G}^{(3)}', 'Ol2q2G(4)': 'C_{\\ell^2 q^2 G}^{(4)}', 'Ol2u2G(1)': 'C_{\\ell^2 u^2 G}^{(1)}', 'Ol2u2G(2)': 'C_{\\ell^2 u^2 G}^{(2)}', 'Ol2d2G(1)': 'C_{\\ell^2 d^2 G}^{(1)}', 'Ol2d2G(2)': 'C_{\\ell^2 d^2 G}^{(2)}', 'Ol2q2D2(2)': 'C_{\\ell^2 q^2 D^2}^{(2)}', 'Ol2q2D2(4)': 'C_{\\ell^2 q^2 D^2}^{(4)}', 'Ol2u2D2(2)': 'C_{\\ell^2 u^2 D^2}^{(2)}', 'Ol2d2D2(2)': 'C_{\\ell^2 d^2 D^2}^{(2)}'}
SMEFT_TO_LEFT_TREE = OrderedDict([('C1(5)', {'deps': ['OLHB', 'OLHW'], 'formula': 'e_charge * vT**2 / (2 * LambdaEW**2) * (OLHB + OLHW)', 'eq': '(E.15)'}), ('C1u(6)', {'deps': ['Olq(1)', 'Olq(3)', 'Olu', 'Znu', 'ZuL', 'ZuR'], 'formula': '(LambdaEW**2 / MZ**2) * (gbarZ**2) * (Olq1 + Olq3 + Olu - 2*Znu*ZuL + Znu*ZuR)', 'eq': '(E.16)'}), ('C1d(6)', {'deps': ['Olq(1)', 'Olq(3)', 'Old', 'Znu', 'ZdL', 'ZdR'], 'formula': '(LambdaEW**2 / MZ**2) * (gbarZ**2) * (Olq1 - Olq3 + Old - 2*Znu*ZdL + Znu*ZdR)', 'eq': '(E.17)'}), ('C2u(6)', {'deps': ['Olq(1)', 'Olq(3)', 'Olu', 'Znu', 'ZuL', 'ZuR'], 'formula': '(LambdaEW**2 / MZ**2) * (gbarZ**2) * (Olu - Olq1 - Olq3 - 2*Znu*ZuR - Znu*ZuL)', 'eq': '(E.18)'}), ('C2d(6)', {'deps': ['Olq(1)', 'Olq(3)', 'Old', 'Znu', 'ZdL', 'ZdR'], 'formula': '(LambdaEW**2 / MZ**2) * (gbarZ**2) * (Old - Olq1 + Olq3 - 2*Znu*ZdR - Znu*ZdL)', 'eq': '(E.19)'}), ('C1u(7)', {'deps': ['OuW', 'OuB'], 'formula': 'sqrt(2) * delta * LambdaEW / (MZ * LambdaEW**2) * (cbar * OuW - sbar * OuB)', 'eq': '(E.20)'}), ('C1d(7)', {'deps': ['OdW', 'OdB'], 'formula': '-sqrt(2) * delta * LambdaEW / (MZ * LambdaEW**2) * (cbar * OdW + sbar * OdB)', 'eq': '(E.20)'}), ('C2u(7)', {'deps': ['OuW', 'OuB'], 'formula': 'sqrt(2) * delta * LambdaEW / (MZ * LambdaEW**2) * (sbar * OuB - cbar * OuW)', 'eq': '(E.21)'}), ('C2d(7)', {'deps': ['OdW', 'OdB'], 'formula': 'sqrt(2) * delta * LambdaEW / (MZ * LambdaEW**2) * (cbar * OdB + sbar * OdW)', 'eq': '(E.21)'}), ('C4u(7)', {'deps': ['OQuLLH'], 'formula': 'sqrt(2) * LambdaEW * vT / (sqrt(3) * LambdaEW**3) * OQuLLH', 'eq': '(E.22)'}), ('C4d(7)', {'deps': ['OdLQLH1'], 'formula': 'sqrt(2) * LambdaEW * vT / (sqrt(3) * LambdaEW**3) * OdLQLH1', 'eq': '(E.22)'}), ('C5u(7)', {'deps': ['OQuLLH'], 'formula': '-sqrt(2) * LambdaEW * vT / (sqrt(3) * LambdaEW**3) * OQuLLH', 'eq': '(E.23)'}), ('C5d(7)', {'deps': ['OdLQLH1'], 'formula': '-sqrt(2) * LambdaEW * vT / (2 * LambdaEW**3) * OdLQLH1', 'eq': '(E.23)'}), ('C3d(7)', {'deps': ['OdLQLH2'], 'formula': 'sqrt(2) * LambdaEW * vT / (2 * LambdaEW**3) * OdLQLH2', 'eq': '(E.24)'}), ('C1u(8)', {'deps': ['Ol2q2D2(2)', 'Ol2q2D2(4)', 'Ol2u2D2(2)'], 'formula': 'LambdaEW**4 * (Ol2q2D2_2 + Ol2q2D2_4 + Ol2u2D2_2) / LambdaEW**4', 'eq': '(E.25)'}), ('C1d(8)', {'deps': ['Ol2q2D2(2)', 'Ol2q2D2(4)', 'Ol2d2D2(2)'], 'formula': 'LambdaEW**4 * (Ol2q2D2_2 - Ol2q2D2_4 + Ol2d2D2_2) / LambdaEW**4', 'eq': '(E.26)'}), ('C2u(8)', {'deps': ['Ol2u2D2(2)', 'Ol2q2D2(2)', 'Ol2q2D2(4)'], 'formula': 'LambdaEW**4 * (Ol2u2D2_2 - Ol2q2D2_2 - Ol2q2D2_4) / LambdaEW**4', 'eq': '(E.27)'}), ('C2d(8)', {'deps': ['Ol2d2D2(2)', 'Ol2q2D2(2)', 'Ol2q2D2(4)'], 'formula': 'LambdaEW**4 * (Ol2d2D2_2 - Ol2q2D2_2 + Ol2q2D2_4) / LambdaEW**4', 'eq': '(E.28)'}), ('C3u(8)', {'deps': ['Ol2q2G(1)', 'Ol2q2G(3)', 'Ol2u2G(1)'], 'formula': 'LambdaEW**4 * (Ol2q2G_1 + Ol2q2G_3 + Ol2u2G_1) / LambdaEW**4', 'eq': '(E.29)'}), ('C3d(8)', {'deps': ['Ol2q2G(1)', 'Ol2q2G(3)', 'Ol2d2G(1)'], 'formula': 'LambdaEW**4 * (Ol2q2G_1 - Ol2q2G_3 + Ol2d2G_1) / LambdaEW**4', 'eq': '(E.30)'}), ('C4u(8)', {'deps': ['Ol2u2G(1)', 'Ol2q2G(1)', 'Ol2q2G(3)'], 'formula': 'LambdaEW**4 * (Ol2u2G_1 - Ol2q2G_1 - Ol2q2G_3) / LambdaEW**4', 'eq': '(E.31)'}), ('C4d(8)', {'deps': ['Ol2d2G(1)', 'Ol2q2G(1)', 'Ol2q2G(3)'], 'formula': 'LambdaEW**4 * (Ol2d2G_1 - Ol2q2G_1 + Ol2q2G_3) / LambdaEW**4', 'eq': '(E.32)'}), ('C5u(8)', {'deps': ['Ol2q2D2(1)', 'Ol2q2D2(3)', 'Ol2u2D2(1)'], 'formula': 'LambdaEW**4 * (Ol2q2D2_1 + Ol2q2D2_3 + Ol2u2D2_1) / LambdaEW**4', 'eq': '(E.33)'}), ('C5d(8)', {'deps': ['Ol2q2D2(1)', 'Ol2q2D2(3)', 'Ol2d2D2(1)'], 'formula': 'LambdaEW**4 * (Ol2q2D2_1 - Ol2q2D2_3 + Ol2d2D2_1) / LambdaEW**4', 'eq': '(E.34)'}), ('C6u(8)', {'deps': ['Ol2u2D2(1)', 'Ol2q2D2(1)', 'Ol2q2D2(3)'], 'formula': 'LambdaEW**4 * (Ol2u2D2_1 - Ol2q2D2_1 - Ol2q2D2_3) / LambdaEW**4', 'eq': '(E.35)'}), ('C6d(8)', {'deps': ['Ol2d2D2(1)', 'Ol2q2D2(1)', 'Ol2q2D2(3)'], 'formula': 'LambdaEW**4 * (Ol2d2D2_1 - Ol2q2D2_1 + Ol2q2D2_3) / LambdaEW**4', 'eq': '(E.36)'}), ('C7u(8)', {'deps': ['Ol2q2G(2)', 'Ol2q2G(4)', 'Ol2u2G(2)'], 'formula': 'LambdaEW**4 * (Ol2q2G_2 + Ol2q2G_4 + Ol2u2G_2) / LambdaEW**4', 'eq': '(E.37)'}), ('C7d(8)', {'deps': ['Ol2q2G(2)', 'Ol2q2G(4)', 'Ol2d2G(2)'], 'formula': 'LambdaEW**4 * (Ol2q2G_2 - Ol2q2G_4 + Ol2d2G_2) / LambdaEW**4', 'eq': '(E.38)'}), ('C8u(8)', {'deps': ['Ol2u2G(2)', 'Ol2q2G(2)', 'Ol2q2G(4)'], 'formula': 'LambdaEW**4 * (Ol2u2G_2 - Ol2q2G_2 - Ol2q2G_4) / LambdaEW**4', 'eq': '(E.39)'}), ('C8d(8)', {'deps': ['Ol2d2G(2)', 'Ol2q2G(2)', 'Ol2q2G(4)'], 'formula': 'LambdaEW**4 * (Ol2d2G_2 - Ol2q2G_2 + Ol2q2G_4) / LambdaEW**4', 'eq': '(E.40)'}), ('C9(8)', {'deps': ['Ol2G2D'], 'formula': 'LambdaEW**4 * Ol2G2D / LambdaEW**4', 'eq': '(E.41)'})])
NEUTRINO_FLAVORS = ('e', 'mu', 'tau')
NUCLEONS = ('p', 'n')
COHERENTLY_ENHANCED_LEFT = ('C1u(6)', 'C1d(6)', 'C1u(7)', 'C1d(7)', 'C1u(8)', 'C1d(8)', 'C5u(8)', 'C5d(8)', 'C3u(7)', 'C3d(7)', 'C4u(7)', 'C4d(7)', 'C5u(7)', 'C5d(7)', 'C6(7)', 'C7(7)', 'C9(8)')
SPIN_DEPENDENT_LEFT = ('C2u(6)', 'C2d(6)', 'C2u(7)', 'C2d(7)', 'C2u(8)', 'C2d(8)', 'C6u(8)', 'C6d(8)')
__all__ = ['ArrayLike', 'EnergyUnit', 'LengthUnit', 'TimeUnit', 'XsecUnit', 'FluxUnit', 'TeV', 'GeV', 'MeV', 'keV', 'eV', 'meV', 'fm', 'G_F', 'alpha_em', 'e_charge', 'vev', 'm_W', 'm_Z', 'Lambda_EW_match', 'Lambda_chi', 'mu_had', 'mu_2GeV', 'm_p', 'm_n', 'm_N', 'm_pi_charged', 'm_pi0', 'm_mu', 'm_e', 'mu_p_magnetic', 'mu_n_magnetic', 'g_A', 'Sigma_ud', 'N_c', 'C_F', 'LECs_known', 'LECs_known_sigma', 'LECs_unknown_orders', 'LECs_unknown_NDA', 'LECs', 'LECs_latex', 'LEFT_WCs_LNC', 'LEFT_WCs_LNV', 'LEFT_WCs', 'LEFT_WC_DIM', 'LEFT_WC_MASS_DIMENSION', 'LEFT_WCs_latex', 'LEFT_QCD_RUNNING', 'NR_operators', 'NR_coefficients_p', 'NR_coefficients_n', 'SMEFT_WCs', 'SMEFT_WC_DIM', 'SMEFT_WC_MASS_DIMENSION', 'SMEFT_WCs_latex', 'SMEFT_TO_LEFT_TREE', 'NEUTRINO_FLAVORS', 'NUCLEONS', 'COHERENTLY_ENHANCED_LEFT', 'SPIN_DEPENDENT_LEFT', 'HBARC_MEV_FM', 'HBAR_MEV_S', 'HBARC_GEV_FM', 'HBAR_GEV_S', 'C_M_S', 'GEV_INV2_TO_MBARN', 'GEV_INV2_TO_CM2', 'CM2_TO_GEV_INV2', 'INV_GEV_TO_FM', 'FM_TO_INV_GEV', 'CM_TO_INV_GEV', 'M_TO_INV_GEV', 'INV_GEV_TO_CM', 'INV_GEV_TO_M', 'INV_GEV_TO_S', 'S_TO_INV_GEV', 'SEC_PER_DAY', 'SEC_PER_YEAR', 'DAY_TO_INV_GEV', 'YEAR_TO_INV_GEV', 'to_energy_gev', 'from_energy_gev', 'to_length_invgev', 'from_length_invgev', 'to_time_invgev', 'from_time_invgev', 'to_xsec_gev_inv2', 'from_xsec_gev_inv2', 'to_flux_natural', 'from_flux_natural', 'b_ho_invgev', 'y_from_qb', 'AMU_GEV', 'e_em']
