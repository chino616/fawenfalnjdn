"""Exact compiled ee-only evaluation of exported SNuDD source arrays.

This is a numerical representation of the declared upstream two-flavor model,
not a fit/interpolation of probabilities. All nonzero original radial weights
and the actual query energy values are used at every NSI point. fastmath=False.
"""
from pathlib import Path
import math
import numpy as np
import numba
from cevns_pyeft.statistics.solar_nsi import SolarNSIJoint
from .protocol import CARD, PIN, read, sha, energy_grid


@numba.njit(parallel=True, cache=True, fastmath=False)
def average_cosine(energy, u, d, alpha, ratio, weights, cosine, sine):
    out = np.empty((len(u), len(energy)))
    for task in numba.prange(len(u)*len(energy)):
        i, j = task//len(energy), task%len(energy)
        p, n = 2*u[i]+d[i], u[i]+2*d[i]
        total = 0.
        for r in range(len(weights)):
            q = cosine-energy[j]*alpha[r]*(1+p+ratio[r]*n)
            total += weights[r]*q/math.sqrt(q*q+sine*sine)
        out[i, j] = total
    return out


class ScanSource:
    """Immutable source identity and a lossless full-rho reconstruction."""
    def __init__(self, directory, *, fixed_sm=False, threads=4):
        directory = Path(directory)
        self.record = read(directory / 'manifest.json')
        if (self.record['schema'] != 'snudd_ee_exact_source_arrays/1' or self.record['software_commit'] != PIN
                or self.record['input_card_sha256'] != sha(CARD)
                or self.record['source_npz_sha256'] != sha(directory / 'source.npz')):
            raise ValueError('stale/corrupt/wrong-source propagation representation')
        with np.load(directory / 'source.npz', allow_pickle=False) as a:
            self.arrays = {k: a[k].copy() for k in a.files}
        for a in self.arrays.values():
            if not np.all(np.isfinite(a)):
                raise ValueError('nonfinite source input')
            a.setflags(write=False)
        self.active = self.arrays['radial_weights'] != 0.
        if len(self.active) != 1000 or np.any(self.arrays['radial_weights'] < 0) or abs(self.arrays['radial_weights'].sum()-1) > 1e-13:
            raise ValueError('wrong upstream quadrature')
        self.fixed_sm = fixed_sm
        self.propagation = 'SNuDD_fixed_SM_probability' if fixed_sm else 'SNuDD_exact_ee_quadrature'
        numba.set_num_threads(min(threads, numba.config.NUMBA_NUM_THREADS))

    @property
    def probability_bounds(self):
        c, s = float(self.arrays['c13_squared']), float(self.arrays['s13_squared'])
        cos2 = float(self.arrays['cos2theta12'])
        return s*s+.5*c*c*(1-abs(cos2)), s*s+.5*c*c*(1+abs(cos2))

    def cos_average(self, energy, eu=0., ed=0.):
        energy = energy_grid(energy)
        u, d = np.broadcast_arrays(np.asarray(eu, float), np.asarray(ed, float))
        if not np.all(np.isfinite(u)) or not np.all(np.isfinite(d)):
            raise ValueError('real finite NSI required')
        if self.fixed_sm:
            u, d = np.zeros_like(u), np.zeros_like(d)
        a, ix = self.arrays, self.active
        result = average_cosine(energy, u.ravel(), d.ravel(), a['alpha_per_MeV'][ix], a['neutron_electron_ratio'][ix],
                                a['radial_weights'][ix], float(a['cos2theta12']), float(a['sin2theta12']))
        if np.any(abs(result) > 1+1e-12):
            raise ValueError('probability average out of physical range')
        return result.reshape((*u.shape, len(energy)))

    def pee(self, energy, eu=0., ed=0., *, radial_order=None):
        if radial_order is not None:
            raise ValueError('upstream1000-node rule is fixed')
        c, s = float(self.arrays['c13_squared']), float(self.arrays['s13_squared'])
        return .5*c*c*(1+float(self.arrays['cos2theta12'])*self.cos_average(energy, eu, ed))+s*s

    def rho(self, energy, eu=0., ed=0.):
        avg = self.cos_average(energy, eu, ed)
        c, s = float(self.arrays['c13_squared']), float(self.arrays['s13_squared'])
        populations = np.stack([.5*c*(1+avg), .5*c*(1-avg), np.full_like(avg, s)], axis=-1)
        U = self.arrays['U_PMNS']
        return np.einsum('ai,...i,bi->...ab', U, populations, U.conj())


class ScanJoint(SolarNSIJoint):
    """Same three-pull statistics with a separately validated source representation.

PreparedExperiment and Runtime stay unchanged. The analysis-only source evaluator
is compared to their full-rho provider before any parameter inference is allowed.
"""
    def __init__(self, experiments, kernels, source):
        super().__init__(experiments, kernels)
        if source.record['input_card_sha256'] != experiments[0].definition.physical.external_card_sha256:
            raise ValueError('source representation and actual Runtime model differ')
        self.runtime_state = self.state
        self.state = source
