"""Explicit numerical replay of verified response kernels for 1D inference.

Production package loading remains separate. Where Windows denies YAML/NPZ
reads, these analysis-only routes never pretend that a native load succeeded.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.contracts import TheoryPoint
from cevns_pyeft.foundation.constants import G_F
from cevns_pyeft.kernels.compiler import reconstruct_channels
from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
from cevns_pyeft.rates.differential import _sm_left_dim6
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson

BASIS = ((6, 1, "u"), (6, 1, "d"), (6, 2, "u"), (6, 2, "d"))
TERRESTRIAL_PARAMETERS = tuple("epsilon_" + flavor + "_" + quark + "V"
    for flavor in ["ee", "mumu", "emu", "etau", "mutau", "tautau"] for quark in ["u", "d"])
CONUS_PARAMETERS = tuple("epsilon_" + f + "_" + q + "V" for f in ["ee", "emu", "etau"] for q in ["u", "d"])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def coefficients(angle, parameter=None, value=0.):
    sm = _sm_left_dim6(True, angle)
    npart = {} if parameter is None else vector_nsi_to_np_wilson(VectorNSIParameters(**{parameter: value}))
    return np.array([sm[k] + npart.get(k, np.zeros((3, 3), complex)) for k in BASIS])


@dataclass
class GaussianChannel:
    name: str
    observed: np.ndarray
    sigma: np.ndarray
    alpha_sigma: float
    background: np.ndarray | None = None
    beta_sigma: float | None = None

    def profile(self, signal):
        s = np.asarray(signal, dtype=float)
        if s.shape[-1] != len(self.observed) or not np.isfinite(s).all():
            raise ValueError("signal axes or finiteness mismatch")
        tol = 1e-10 * max(1., float(np.max(abs(s))))
        if np.min(s) < -tol: raise ValueError("negative physical prediction")
        w = 1 / self.sigma**2
        b = 0. if self.background is None else self.background
        residual = self.observed - s - b
        aa = np.sum(s*s*w, axis=-1) + 1/self.alpha_sigma**2
        ra = np.sum(s*residual*w, axis=-1)
        if self.background is None:
            alpha = ra/aa
            beta = np.zeros_like(alpha)
        else:
            ab = np.sum(s*b*w, axis=-1)
            bb = float(np.sum(b*b*w) + 1/self.beta_sigma**2)
            rb = np.sum(b*residual*w, axis=-1)
            alpha = (ra*bb-rb*ab)/(aa*bb-ab*ab)
            beta = (rb*aa-ra*ab)/(aa*bb-ab*ab)
        r = self.observed-(1+alpha[..., None])*s
        if self.background is not None: r = r-(1+beta[..., None])*b
        data = np.sum(r*r*w, axis=-1)
        penalty = (alpha/self.alpha_sigma)**2
        if self.background is not None: penalty += (beta/self.beta_sigma)**2
        return data+penalty, alpha, beta, data, penalty

    def rate_upper_bound(self, chi2_level):
        """Cauchy projection bound; necessary condition for chi2<=level."""
        b = 0. if self.background is None else float(self.background.sum())
        net = float(self.observed.sum()) - b
        variance = float(self.sigma @ self.sigma)
        if self.background is not None: variance += (self.beta_sigma*b)**2
        denominator = 1-chi2_level*self.alpha_sigma**2
        if denominator <= 0: raise ValueError("normalization-pull saturation prevents finite rate bound")
        return (net+np.sqrt(chi2_level*(self.alpha_sigma**2*net**2+denominator*variance)))/denominator


class FrozenBilinearRoute:
    def __init__(self, name, full, rhos, channel, angle, record):
        self.name, self.full, self.rhos, self.channel, self.angle, self.record = name, full, rhos, channel, angle, record
        if full.shape[3:5] != (4, 4) or rhos.shape != (full.shape[1], 3, 3): raise ValueError("operator/source axes differ")
        self.holdouts = []

    def predict(self, value=0., parameter=None):
        angle = float(value) if parameter == "sin2thetaW" else self.angle
        c = coefficients(angle, None if parameter in [None, "sin2thetaW"] else parameter, value)
        channels = reconstruct_channels(self.full, c, self.rhos)
        s = channels.sum(axis=(0, 1, 2))
        tol = 1e-10 * max(float(np.max(abs(s))), 1.)
        if np.any(s < -tol): raise ValueError("kernel yields negative physical signal")
        return np.maximum(s, 0.)

    def polynomial(self, parameter):
        """An exact quadratic in one fixed-state coupling/weak-angle parameter."""
        v0, vp, vm = [self.predict(x, parameter) for x in [0., 1., -1.]]
        p = np.array([v0, (vp-vm)/2, (vp+vm)/2-v0])
        for x in [-.317, .023, .193, .511, 1.7]:
            exact = self.predict(x, parameter)
            result = p[0]+x*(p[1]+x*p[2])
            delta = float(np.max(abs(result-exact)))
            if delta > 1e-8 + 2e-11*float(np.max(abs(exact))): raise ValueError("polynomial holdout failed")
            self.holdouts.append({"parameter": parameter, "point": x, "max_abs_events": delta})
        return p


class SolarRoute:
    SAMPLES = ("PandaX_paired", "PandaX_US2", "XENONnT")

    def __init__(self, directory):
        from extensions.solar_rho_snudd.scan import ScanSource
        self.directory = Path(directory)
        self.result = read(self.directory/"NSI_RESULTS.json")
        self.kernels = [SolarNSIKernel.load(self.directory/"kernels"/(s+".npz")) for s in self.SAMPLES]
        self.energy = self.kernels[0].energy
        self.weights = self.kernels[0].energy_weights
        if any(not np.array_equal(k.energy, self.energy) for k in self.kernels): raise ValueError("solar energy axes differ")
        self.angle = self.kernels[0].record["sin2thetaW"]
        self.source = ScanSource(self.directory/"propagation_source", threads=4)
        self.templates = np.stack([k.values.sum(axis=0) for k in self.kernels])
        data = read(ROOT/"data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json")["samples"]
        self.D = np.array([data[s]["D"] for s in self.SAMPLES])
        self.sigma = np.array([data[s]["sigma_stat"] for s in self.SAMPLES])
        self.pulls = np.array([data[s]["pull_sigma"] for s in self.SAMPLES])
        # Original physical endpoint efficiency, not inferred from a target event count.
        dep = self.kernels[-1].record["physical_dependencies"]
        self.tail_efficiency = self._find_tail_efficiency(dep)
        self.sm_blocks = np.einsum("sbme,e->sbm", self.templates, self.weights)[:, :, 0]
        self.SM = self.sm_blocks[:, 0] + self.tail_efficiency*self.sm_blocks[:, 1]
        np.testing.assert_allclose(self.SM, self.result["SM"]["signal_events"], rtol=1e-13, atol=2e-12)
        self._scalar_cache = {}

    def _find_tail_efficiency(self, dep):
        # The official total-acceptance table is already pinned by the singlebin card.
        card = read(ROOT/"data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json")
        for record in card["files"].values():
            if isinstance(record, dict) and "path" in record and "xenon" in record["path"].lower() and "accept" in record["path"].lower():
                p = ROOT/record["path"]
                if not p.exists(): p = ROOT/"data/benchmarks/solar_b8_singlebin_2601_19883"/record["path"]
                if p.exists(): return float(np.loadtxt(p)[-1, 1])
        # Public loader is supported for solar and records the exact observation table.
        from cevns_pyeft.experiments.solar_singlebin import load_singlebin
        e = load_singlebin("XENONnT", root=ROOT)
        return float(e.model.observation.efficiency[-1])

    def ee_signals(self, value, parameter):
        x = np.asarray(value, float)
        u = x if parameter == "epsilon_ee_uV" else np.zeros_like(x)
        d = x if parameter == "epsilon_ee_dV" else np.zeros_like(x)
        scalar = x.ndim == 0
        key = (parameter, float(x)) if scalar else None
        if scalar and key in self._scalar_cache: return self._scalar_cache[key]
        uf, df = u.ravel(), d.ravel()
        result = np.empty((len(uf), 3))
        for first in range(0, len(uf), 192):
            uu, dd = uf[first:first+192], df[first:first+192]
            pee = self.source.pee(self.energy, uu, dd)
            monomials = np.stack([uu, dd, uu**2, uu*dd, dd**2], axis=-1)
            blocks = self.sm_blocks + np.einsum("pe,sbme,pm,e->psb", pee, self.templates[:, :, 1:, :], monomials, self.weights, optimize=True)
            result[first:first+len(uu)] = blocks[:, :, 0]+self.tail_efficiency*blocks[:, :, 1]
        if np.min(result) < -1e-8: raise ValueError("negative solar physical signal")
        result = result.reshape((*x.shape, 3))
        if scalar: self._scalar_cache[key] = result
        return result

    def electron_coefficients(self):
        return np.stack([k.integrated_electron_coefficients(self.tail_efficiency if i == 2 else 0.) for i, k in enumerate(self.kernels)])

    def weak_signals(self, value):
        # Exact matching identity for every incoming flavor: eu=-4/3 ds, ed=+2/3 ds.
        delta = np.asarray(value, float) - self.angle
        u, d = -4*delta/3, 2*delta/3
        basis = np.stack([np.ones_like(u), u, d, u*u, u*d, d*d], axis=-1)
        return basis @ self.electron_coefficients().T

    def profile(self, signals, indices=None, *, retain_pulls=True):
        indices = np.arange(3) if indices is None else np.array(indices)
        s = np.asarray(signals)[..., indices]
        D, sigma = self.D[indices], self.sigma[indices]
        if retain_pulls:
            alpha = self.pulls[indices]**2*s*(D-s)/(sigma*sigma+self.pulls[indices]**2*s*s)
        else:
            alpha = np.zeros_like(s)
        data = np.sum(((D-(1+alpha)*s)/sigma)**2, axis=-1)
        penalty = np.sum((alpha/self.pulls[indices])**2, axis=-1)
        return data+penalty


def load_routes(output):
    """Open adopted numerical artifacts and verify original SM regressions."""
    output = Path(output)
    summary_path = ROOT/"outputs/paper2601_chi2_corrected_20261111/SUMMARY.json"
    summary = read(summary_path)
    files = {summary_path.relative_to(ROOT).as_posix(): sha(summary_path)}
    routes = {}
    for name in ["CsI2021", "Ar2020", "CONUS_plus"]:
        row = summary["SM"][name]
        ch = GaussianChannel(name, np.array(row["observed"]), np.array(row["sigma"]), row["sigma_alpha"],
                             None if row["background"] is None else np.array(row["background"]), row["sigma_beta"])
        if name == "CONUS_plus":
            p = ROOT/"outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_operator_kernel_161_641.npz"
            with np.load(p, allow_pickle=False) as a:
                full = a["full_kernel"].copy()
                record = json.loads(str(a["metadata"]))["record"]
            rho = np.diag([1., 0., 0.])[None, ...]
            angle = .23857
        else:
            p = ROOT/"outputs/paper2601_chi2_corrected_20261111"/(name+"_kernel.npz")
            with np.load(p, allow_pickle=False) as a: full = a["full_kernel"].copy()
            recpath = p.with_name(name+"_kernel_record.json")
            record = read(recpath); files[recpath.relative_to(ROOT).as_posix()] = sha(recpath)
            rho = np.array([np.diag([0., 1., 0.]), np.diag([1., 0., 0.]), np.diag([0., 1., 0.])])
            angle = .2387
        files[p.relative_to(ROOT).as_posix()] = sha(p)
        route = FrozenBilinearRoute(name, full, rho, ch, angle, record)
        signal = route.predict()
        np.testing.assert_allclose(signal, row["signal"], atol=1e-9, rtol=1e-12)
        if abs(float(ch.profile(signal)[0])-row["chi2"]) > 1e-10: raise ValueError("SM likelihood regression differs")
        np.savez_compressed(output/"inputs"/(name+"_fixed_model.npz"), full_kernel=full, rhos=rho,
            observed=ch.observed, sigma=ch.sigma, background=np.zeros_like(ch.observed) if ch.background is None else ch.background)
        routes[name] = route
    source_dir = ROOT/"outputs/external/solar_rho_snudd/20261112_fig4_run2"
    solar = SolarRoute(source_dir)
    files[(source_dir/"NSI_RESULTS.json").relative_to(ROOT).as_posix()] = sha(source_dir/"NSI_RESULTS.json")
    for k in solar.SAMPLES:
        p = source_dir/"kernels"/(k+".npz"); files[p.relative_to(ROOT).as_posix()] = sha(p)
    for p in [source_dir/"propagation_source/source.npz", source_dir/"propagation_source/manifest.json"]:
        files[p.relative_to(ROOT).as_posix()] = sha(p)
    # Existing audited source identities remain distinct from fresh native loader execution.
    current_sources = read(ROOT/"outputs/paper2601_fast_audit_20261111/SOURCE_MANIFEST.json")
    for item in current_sources:
        if sha(ROOT/item["path"]) != item["sha256"]: raise ValueError("audited Fast source changed: "+item["path"])
        files[item["path"]] = item["sha256"]
    for path, h in read(source_dir/"SOURCE_FINGERPRINTS.json").items():
        if sha(ROOT/path) != h: raise ValueError("solar source changed: "+path)
        files[path] = h
    return routes, solar, files
