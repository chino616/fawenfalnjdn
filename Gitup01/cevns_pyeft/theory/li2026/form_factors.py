from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal

from cevns_pyeft.foundation import constants as uc

Quark = Literal['u', 'd', 's']
Nucleon = Literal['p', 'n']
Q2Unit = Literal['GeV^2', 'MeV^2', 'keV^2']

def to_q2_gev2(q2: float, unit: Q2Unit='GeV^2') -> float:
    if unit == 'GeV^2':
        return float(q2)
    if unit == 'MeV^2':
        return float(q2) * 1e-06
    if unit == 'keV^2':
        return float(q2) * 1e-12
    raise ValueError(f'Unknown Q2 unit: {unit}')

@dataclass(frozen=True)
class FormFactors:
    q2: float
    MN: float
    m_pi0: float
    m_eta: float
    mu_mag_p: float
    mu_mag_n: float
    mu_mag_s: float
    f1_slope: Dict[Quark, float]
    gA: float
    delta_u: float
    delta_d: float
    delta_s: float
    m_u: float
    m_d: float
    m_s: float

    @staticmethod
    def build(q2: float, q2_unit: Q2Unit='GeV^2') -> 'FormFactors':
        q2g = to_q2_gev2(q2, q2_unit)
        MN = (float(getattr(uc, 'm_p', 0.93827208816)) + float(getattr(uc, 'm_n', 0.93956542052))) / 2.0
        m_pi0 = float(getattr(uc, 'm_pi0', 0.1349768))
        m_eta = 0.547862
        mu_mag_p = 2.793
        mu_mag_n = -1.913
        mu_mag_s = -0.064
        f1_slope: Dict[Quark, float] = {'u': 5.57, 'd': 2.84, 's': -0.018}
        gA = 1.2723
        delta_u = round((0.521 + gA) / 2.0, 3)
        delta_d = round((0.521 - gA) / 2.0, 3)
        delta_s = -0.031
        m_u = 0.0022
        m_d = 0.0047
        m_s = 0.096
        return FormFactors(q2=q2g, MN=MN, m_pi0=m_pi0, m_eta=m_eta, mu_mag_p=mu_mag_p, mu_mag_n=mu_mag_n, mu_mag_s=mu_mag_s, f1_slope=f1_slope, gA=gA, delta_u=delta_u, delta_d=delta_d, delta_s=delta_s, m_u=m_u, m_d=m_d, m_s=m_s)

    def _pion_pole(self) -> float:
        return 1.0 / (self.m_pi0 * self.m_pi0 + self.q2)

    def _eta_pole(self) -> float:
        return 1.0 / (self.m_eta * self.m_eta + self.q2)

    def F1(self, q: Quark, n: Nucleon) -> float:
        if n == 'p':
            return {'u': 2.0, 'd': 1.0, 's': 0.0}[q]
        else:
            return {'u': 1.0, 'd': 2.0, 's': 0.0}[q]

    def QSF1(self, q: Quark, n: Nucleon) -> float:
        return self.F1(q, n) + self.f1_slope[q] * self.q2

    def F2(self, q: Quark, n: Nucleon) -> float:
        mup, mun, mus = (self.mu_mag_p, self.mu_mag_n, self.mu_mag_s)
        if q == 's':
            return mus
        if n == 'p':
            if q == 'u':
                return 2.0 * (mup - 1.0) + mun + mus
            if q == 'd':
                return 2.0 * mun + (mup - 1.0) + mus
        else:
            if q == 'u':
                return 2.0 * mun + (mup - 1.0) + mus
            if q == 'd':
                return 2.0 * (mup - 1.0) + mun + mus
        raise ValueError(f'Bad (q,n)=({q},{n})')

    def FA(self, q: Quark, n: Nucleon) -> float:
        if q == 's':
            return self.delta_s
        if n == 'p':
            return self.delta_u if q == 'u' else self.delta_d
        else:
            return self.delta_d if q == 'u' else self.delta_u

    def FPp(self, q: Quark, n: Nucleon) -> float:
        a_eta = 2.0 * (self.delta_u + self.delta_d - 2.0 * self.delta_s) / 3.0
        pp = self._pion_pole()
        ep = self._eta_pole()
        if n == 'p':
            if q == 'u':
                return +2.0 * self.gA * self.MN ** 2 * pp + a_eta * self.MN ** 2 * ep
            if q == 'd':
                return -2.0 * self.gA * self.MN ** 2 * pp + a_eta * self.MN ** 2 * ep
            if q == 's':
                return -2.0 * a_eta * self.MN ** 2 * ep
        else:
            if q == 'd':
                return +2.0 * self.gA * self.MN ** 2 * pp + a_eta * self.MN ** 2 * ep
            if q == 'u':
                return -2.0 * self.gA * self.MN ** 2 * pp + a_eta * self.MN ** 2 * ep
            if q == 's':
                return -2.0 * a_eta * self.MN ** 2 * ep
        raise ValueError(f'Bad (q,n)=({q},{n})')

    def FS(self, q: Quark, n: Nucleon) -> float:
        sigma = {('u', 'p'): 0.017, ('d', 'p'): 0.032, ('s', 'p'): 0.0413, ('u', 'n'): 0.015, ('d', 'n'): 0.036, ('s', 'n'): 0.0413}
        return sigma[q, n]

    def FP(self, q: Quark, n: Nucleon) -> float:
        # B0_mq_GeV2 stores B0*m_q combinations, not B0 itself.
        B0_mq_GeV2 = {'u': 0.0061, 'd': 0.0133, 's': 0.268}
        pp = self._pion_pole()
        ep = self._eta_pole()
        tmp = self.delta_u + self.delta_d - 2.0 * self.delta_s
        if n == 'p':
            a_pi = +self.gA * B0_mq_GeV2[q] / self.MN if q == 'u' else -self.gA * B0_mq_GeV2[q] / self.MN if q == 'd' else 0.0
        else:
            a_pi = +self.gA * B0_mq_GeV2[q] / self.MN if q == 'd' else -self.gA * B0_mq_GeV2[q] / self.MN if q == 'u' else 0.0
        if q == 's':
            a_eta = -2.0 * B0_mq_GeV2[q] * tmp / (3.0 * self.MN)
        else:
            a_eta = +B0_mq_GeV2[q] * tmp / (3.0 * self.MN)
        return self.MN ** 2 * pp * a_pi + self.MN ** 2 * ep * a_eta

    def FT0(self, q: Quark, n: Nucleon) -> float:
        gT = {'u': 0.794, 'd': -0.204, 's': 0.00032}
        mq = {'u': self.m_u, 'd': self.m_d, 's': self.m_s}
        if n == 'p':
            return mq[q] * gT[q]
        else:
            if q == 'u':
                return self.m_u * gT['d']
            if q == 'd':
                return self.m_d * gT['u']
            return self.m_s * gT['s']

    def FT1(self, q: Quark, n: Nucleon) -> float:
        BT10p = {'u': 3.0, 'd': 0.24, 's': 0.0}
        mq = {'u': self.m_u, 'd': self.m_d, 's': self.m_s}
        if n == 'p':
            return -mq[q] * BT10p[q]
        else:
            if q == 'u':
                return -self.m_u * BT10p['d']
            if q == 'd':
                return -self.m_d * BT10p['u']
            return -self.m_s * BT10p['s']

    def FG(self, n: Nucleon) -> float:
        mG = 0.848
        return -2.0 * mG / 27.0

    def FGt(self, n: Nucleon) -> float:
        mu, md, ms = (self.m_u, self.m_d, self.m_s)
        mtilde = 1.0 / (1.0 / mu + 1.0 / md + 1.0 / ms)
        a_gt_pi = -mtilde * self.MN * self.gA * (1.0 / mu - 1.0 / md) / 2.0
        a_gt_eta = -mtilde * self.MN * (self.delta_u + self.delta_d - 2.0 * self.delta_s) * (1.0 / mu + 1.0 / md - 2.0 / ms) / 6.0
        if n == 'p':
            b_gt = -mtilde * self.MN * (self.delta_u / mu + self.delta_d / md + self.delta_s / ms)
            sign_pi = +1.0
        else:
            b_gt = -mtilde * self.MN * (self.delta_d / mu + self.delta_u / md + self.delta_s / ms)
            sign_pi = -1.0
        return -self.q2 * self._pion_pole() * (sign_pi * a_gt_pi) - self.q2 * self._eta_pole() * a_gt_eta + b_gt

def build_form_factors(q2: float, q2_unit: Q2Unit='GeV^2') -> FormFactors:
    return FormFactors.build(q2, q2_unit=q2_unit)

__all__ = [
    "Quark",
    "Nucleon",
    "Q2Unit",
    "to_q2_gev2",
    "FormFactors",
    "build_form_factors",
]
