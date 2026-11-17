"""Analysis coordinates and the published CsI scintillation-fit domain."""
import numpy as np

from cevns_pyeft.rates.differential import (
    eee_quenching_csi,
    enr_max_keV,
    emax_muon_dar_mev,
    p_smearing_csi,
)
from cevns_pyeft.rates.counts import _trapz_weights

PE_EDGES = np.array([0, 8, 12, 16, 20, 24, 32, 40, 48, 60.], dtype=float)
TIME_EDGES = np.array([0, .125, .25, .375, .5, .625, .75, .875, 1, 2, 4, 6.])
PE_EDGES.flags.writeable = False
TIME_EDGES.flags.writeable = False
QF_DOMAIN_KEV = (2., 70.)
QF_SOURCE_URL = 'https://arxiv.org/html/2111.02477v2#S8'
QF_SOURCE_LOCATOR = 'Section 8, Fitting approach and Eq. (8.1)'


def validate_qf_recoil(recoil_keV):
    """Require the stated 2--70 keVnr fit domain before evaluating the fit."""
    recoil = np.asarray(recoil_keV, dtype=float)
    if not np.isfinite(recoil).all():
        raise ValueError('QF recoil energies must be finite')
    if np.any(recoil < QF_DOMAIN_KEV[0]) or np.any(recoil > QF_DOMAIN_KEV[1]):
        raise ValueError('CsI QF fit is supported only on 2--70 keVnr (0.002--0.070 MeVnr)')
    return recoil


def calibrated_scintillation_response(recoil_keV):
    validate_qf_recoil(recoil_keV)
    return eee_quenching_csi(recoil_keV)


def calibrated_smearing(pe, recoil_keV):
    validate_qf_recoil(recoil_keV)
    return p_smearing_csi(pe, recoil_keV)


def calibrated_recoil_grid(response, count):
    if isinstance(count, bool) or int(count) != count or count < 2:
        raise ValueError('Recoil grid requires an integer count >= 2')
    maximum = enr_max_keV(int(response.basic['A']), Emax_MeV=emax_muon_dar_mev())
    if maximum > QF_DOMAIN_KEV[1]:
        raise ValueError('Signal recoil support exceeds the published QF fit domain')
    grid = np.linspace(QF_DOMAIN_KEV[0], maximum, int(count))
    validate_qf_recoil(grid)
    return grid, _trapz_weights(grid)
