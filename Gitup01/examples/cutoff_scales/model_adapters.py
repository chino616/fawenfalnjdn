"""Read-only, explicitly scoped adapters for adopted mainline numerical models."""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cevns_pyeft.foundation.constants import G_F
from cevns_pyeft.kernels.compiler import reconstruct_channels
from cevns_pyeft.kernels.solar_nsi import SolarNSIKernel
from cevns_pyeft.rates.differential import _sm_left_dim6
from common import read, sha
from inference import Gaussian, sum_rational

BASIS = ((6, 1, "u"), (6, 1, "d"), (6, 2, "u"), (6, 2, "d"))
REFERENCE = "outputs/paper2601_chi2_corrected_20261111"
SOLAR = "outputs/external/solar_rho_snudd/20261112_fig4_run2"
GROUND_GROUPS = {"CONUS_plus": ("CONUS_plus",), "CsI2021_9PE": ("CsI2021_9PE",),
                 "Ar2020_average": ("Ar2020_average",),
                 "CsI2021_9PE+Ar2020_average": ("CsI2021_9PE", "Ar2020_average")}
SOLAR_SAMPLES = ("PandaX_paired", "PandaX_US2", "XENONnT")
SOLAR_GROUPS = {**{name: (i,) for i, name in enumerate(SOLAR_SAMPLES)}, "Solar_three_singlebins": (0, 1, 2)}


def metadata_basis(record):
    return tuple(tuple(k) for k in record.get("basis_keys", record.get("dependencies", {}).get("basis_keys", BASIS)))


@dataclass
class Ground:
    name: str
    full: np.ndarray
    rhos: np.ndarray
    channel: Gaussian
    angle: float
    basis: tuple = BASIS

    def tensor(self, operator=None, coefficient=0., flavor=None):
        values = _sm_left_dim6(True, self.angle)
        result = np.array([values.get(k, np.zeros((3, 3), complex)) for k in self.basis])
        if operator is not None:
            matrix = np.diag([1., 0., 0.]) if flavor is None else np.asarray(flavor)
            result[self.basis.index(tuple(operator))] += coefficient*matrix
        return result

    def predict(self, operator=None, coefficient=0., *, flavor=None, representation="full"):
        return reconstruct_channels(self.full, self.tensor(operator, coefficient, flavor), self.rhos,
                                    representation=representation).sum(axis=(0, 1, 2))

    def polynomial(self, operator, flavor=None):
        sm = self.tensor()
        unit = np.zeros_like(sm)
        unit[self.basis.index(tuple(operator))] = np.diag([1., 0., 0.]) if flavor is None else flavor
        bilinear = lambda a, b: np.einsum("sab,ifb,jfa->sij", self.rhos, a.conj(), b, optimize=True)
        contract = lambda b: np.einsum("tshijb,sij->tshb", self.full, b, optimize=True).real.sum(axis=(0, 1, 2))
        return np.array([contract(bilinear(sm, sm)), contract(bilinear(sm, unit)+bilinear(unit, sm)), contract(bilinear(unit, unit))])


def load_ground():
    result, files = {}, {}
    summary = read(f"{REFERENCE}/SUMMARY.json")
    files[f"{REFERENCE}/SUMMARY.json"] = sha(ROOT/f"{REFERENCE}/SUMMARY.json")
    for name, source_name in (("CsI2021_9PE", "CsI2021"), ("Ar2020_average", "Ar2020"), ("CONUS_plus", "CONUS_plus")):
        row = summary["SM"][source_name]
        channel = Gaussian(np.array(row["observed"]), np.array(row["sigma"]), row["sigma_alpha"],
                           None if row["background"] is None else np.array(row["background"]), row["sigma_beta"])
        if name == "CONUS_plus":
            rel = "outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_operator_kernel_161_641.npz"
            with np.load(ROOT/rel, allow_pickle=False) as arr:
                full = arr["full_kernel"].copy()
                record = json.loads(str(arr["metadata"]))["record"]
            rhos, angle = np.diag([1., 0., 0.])[None, ...], .23857
        else:
            rel = f"{REFERENCE}/{source_name}_kernel.npz"
            with np.load(ROOT/rel, allow_pickle=False) as arr:
                full = arr["full_kernel"].copy()
            recpath = f"{REFERENCE}/{source_name}_kernel_record.json"
            record = read(recpath); files[recpath] = sha(ROOT/recpath)
            rhos = np.array([np.diag([0., 1., 0.]), np.diag([1., 0., 0.]), np.diag([0., 1., 0.])])
            angle = .2387
        if metadata_basis(record) != BASIS or full.shape[3:5] != (4, 4):
            raise ValueError("adopted ground basis mismatch")
        files[rel] = sha(ROOT/rel)
        route = Ground(name, full, rhos, channel, angle)
        np.testing.assert_allclose(route.predict(), row["signal"], rtol=1e-12, atol=1e-9)
        np.testing.assert_allclose(channel.profile(route.predict())[0], row["chi2"], rtol=0, atol=1e-10)
        result[name] = route
    return result, files


class GroundObjective:
    def __init__(self, routes, operator, *, flavor=None):
        self.routes, self.operator = routes, tuple(operator)
        physical = [r.polynomial(operator, flavor) for r in routes]
        quadratic = sum(float(p[2].sum()) for p in physical)
        signal = sum(float(p[0].sum()) for p in physical)
        linear = max(float(np.max(abs(p[1]))) for p in physical)
        self.no_sensitivity = quadratic == 0 and linear == 0
        self.coefficient_scale = np.sqrt(max(signal, 1.)/quadratic) if quadratic > 0 else 1.
        self.polynomials = [p*np.array([1., self.coefficient_scale, self.coefficient_scale**2])[:, None] for p in physical]
        self.rational = sum_rational([r.channel.rational(p) for r, p in zip(routes, self.polynomials)])
        self.name = "+".join(r.name for r in routes)

    def signals(self, x):
        x = np.asarray(x)
        return [p[0]+x[..., None]*(p[1]+x[..., None]*p[2]) for p in self.polynomials]

    def __call__(self, x):
        return sum(r.channel.profile(s)[0] for r, s in zip(self.routes, self.signals(x)))

    def domain(self, threshold=3.84):
        if self.no_sensitivity:
            return (-1., 1.), {"proof": "all linear and quadratic arrays exactly zero"}
        level = float(self(0.))+threshold
        lower, upper, rows = -np.inf, np.inf, []
        for route, p in zip(self.routes, self.polynomials):
            a, b, q = p.sum(axis=1)
            if q == 0 and b == 0:
                continue
            rate = route.channel.rate_upper_bound(level)
            if q <= 0:
                raise ValueError("positive quadratic needed for certified ground rate bound")
            center = -b/(2*q)
            radius = np.sqrt((rate-a+b*b/(4*q))/q)
            lo, hi = center-radius, center+radius
            lower, upper = max(lower, lo), min(upper, hi)
            rows.append({"component": route.name, "total_chi2_level": level, "necessary_rate_upper": rate,
                         "necessary_interval_x": [lo, hi]})
        if not np.isfinite([lower, upper]).all() or not lower < 0 < upper:
            raise ValueError("failed to enclose the SM-referenced confidence domain")
        width = upper-lower
        return (lower-.01*width, upper+.01*width), {"proof": "intersection of necessary rate inequalities; chi2_min <= chi2_SM", "components": rows}


class Solar:
    def __init__(self, *, threads=4):
        from extensions.solar_rho_snudd.scan import ScanSource
        directory = ROOT/SOLAR
        self.source = ScanSource(directory/"propagation_source", threads=threads)
        self.kernels = [SolarNSIKernel.load(directory/"kernels"/(s+".npz")) for s in SOLAR_SAMPLES]
        self.energy, self.weights = self.kernels[0].energy, self.kernels[0].energy_weights
        if any(not np.array_equal(k.energy, self.energy) for k in self.kernels):
            raise ValueError("solar energy axes mismatch")
        card = read("data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json")
        self.tail_efficiency = None
        for record in card["files"].values():
            if isinstance(record, dict) and "path" in record and "xenon" in record["path"].lower() and "accept" in record["path"].lower():
                path = ROOT/record["path"]
                if not path.exists():
                    path = ROOT/"data/benchmarks/solar_b8_singlebin_2601_19883"/record["path"]
                if path.is_file():
                    self.tail_efficiency = float(np.loadtxt(path)[-1, 1]); break
        if self.tail_efficiency is None:
            from cevns_pyeft.experiments.solar_singlebin import load_singlebin
            self.tail_efficiency = float(load_singlebin("XENONnT", root=ROOT).model.observation.efficiency[-1])
        self.templates = np.stack([k.values.sum(axis=0)[0]+(self.tail_efficiency if i == 2 else 0.)*k.values.sum(axis=0)[1] for i, k in enumerate(self.kernels)])
        self.sm = np.einsum("se,e->s", self.templates[:, 0, :], self.weights)
        expected = read(f"{SOLAR}/NSI_RESULTS.json")["SM"]["signal_events"]
        np.testing.assert_allclose(self.sm, expected, rtol=1e-12, atol=2e-10)
        data = read("data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json")["samples"]
        self.channels = [Gaussian(np.array([data[s]["D"]]), np.array([data[s]["sigma_stat"]]), data[s]["pull_sigma"]) for s in SOLAR_SAMPLES]
        self.files = {f"{SOLAR}/kernels/{s}.npz": sha(directory/"kernels"/(s+".npz")) for s in SOLAR_SAMPLES}
        for rel in (f"{SOLAR}/NSI_RESULTS.json", f"{SOLAR}/propagation_source/source.npz", f"{SOLAR}/propagation_source/manifest.json",
                    "data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json", "data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json"):
            self.files[rel] = sha(ROOT/rel)

    @lru_cache(maxsize=65536)
    def scalar_signals(self, x, quark):
        return self.signals(np.array([x]), quark)[0]

    def signals(self, x, quark):
        x = np.asarray(x, float)
        if x.ndim == 0:
            return self.scalar_signals(float(x), quark)
        flat = x.ravel()
        out = np.empty((len(flat), 3))
        li, qi = (1, 3) if quark == "u" else (2, 5)
        for first in range(0, len(flat), 256):
            v = flat[first:first+256]
            # c=sqrt(2)GF*x, so epsilon=-x. Update the state at every point.
            eps = -v
            u, d = (eps, np.zeros_like(eps)) if quark == "u" else (np.zeros_like(eps), eps)
            pee = self.source.pee(self.energy, u, d)
            correction = self.templates[:, li, :][None, :, :]*eps[:, None, None]+self.templates[:, qi, :][None, :, :]*eps[:, None, None]**2
            out[first:first+len(v)] = self.sm+np.einsum("pe,pse,e->ps", pee, correction, self.weights, optimize=True)
        return out.reshape((*x.shape, 3))


class SolarObjective:
    def __init__(self, solar, indices, quark):
        self.solar, self.indices, self.quark = solar, tuple(indices), quark
        self.coefficient_scale = np.sqrt(2)*G_F
        self.no_sensitivity, self.rational = False, None

    def __call__(self, x):
        signals = self.solar.signals(x, self.quark)
        return sum(self.solar.channels[i].profile(signals[..., i, None])[0] for i in self.indices)

    def domain(self, threshold=3.84):
        level = float(self(0.))+threshold
        pmin, pmax = self.solar.source.probability_bounds
        li, qi = (1, 3) if self.quark == "u" else (2, 5)
        radii, rows = [], []
        for i in self.indices:
            spectrum = self.solar.templates[i]
            q = float(spectrum[qi] @ self.solar.weights)
            a = float(abs(spectrum[li]) @ self.solar.weights)
            if q <= 0 or pmin <= 0:
                raise ValueError("no positive solar quadratic/probability tail proof")
            upper = self.solar.channels[i].rate_upper_bound(level)
            constant = self.solar.sm[i]-upper
            radius = (pmax*a+np.sqrt((pmax*a)**2-4*pmin*q*constant))/(2*pmin*q)
            radii.append(float(radius))
            rows.append({"sample": SOLAR_SAMPLES[i], "rate_upper": upper, "Pee_bounds": [pmin, pmax],
                         "quadratic_integral": q, "absolute_linear_integral": a, "excluded_tail_beyond_abs_x": radius})
        radius = min(radii)*1.02
        return (-radius, radius), {"proof": "S(x)>=S_SM-Pmax*integral|L|*|x|+Pmin*integral Q*x^2; necessary Gaussian rate upper bound", "components": rows}


def validate_gaussian_and_polynomials(routes):
    from cevns_pyeft.statistics.profiling import profile_gaussian_one_pull, profile_gaussian_two_pull
    rows = []
    for name, route in routes.items():
        for operator in route.basis:
            objective = GroundObjective([route], operator)
            for x in (-2.13, -.193, 0., .417, 3.27):
                c = x*objective.coefficient_scale
                polynomial = objective.signals(x)[0]
                full = route.predict(operator, c)
                pair = route.predict(operator, c, representation="pair")
                np.testing.assert_allclose(polynomial, full, atol=2e-9, rtol=2e-11)
                np.testing.assert_allclose(pair, full, atol=2e-9, rtol=2e-11)
                ch = route.channel
                native = (profile_gaussian_one_pull(full, ch.observed, ch.sigma, sigma_alpha=ch.alpha_sigma)
                          if ch.background is None else profile_gaussian_two_pull(full, ch.observed, ch.background, ch.sigma,
                              sigma_alpha=ch.alpha_sigma, sigma_beta=ch.beta_sigma))
                evaluated = float(objective(x))
                np.testing.assert_allclose(evaluated, native.chi2, atol=2e-10, rtol=2e-12)
                # Independent nuisance solve using an augmented least-squares design.
                cols = [full/ch.sigma]
                if ch.background is not None:
                    cols.append(ch.background/ch.sigma)
                design = np.vstack([np.column_stack(cols), np.diag([1/ch.alpha_sigma]+([] if ch.background is None else [1/ch.beta_sigma]))])
                rhs = np.r_[(ch.observed-full-(0 if ch.background is None else ch.background))/ch.sigma, np.zeros(len(cols))]
                pulls = np.linalg.lstsq(design, rhs, rcond=None)[0]
                cost = float(np.sum((rhs-design@pulls)**2))
                np.testing.assert_allclose(cost, evaluated, atol=2e-9, rtol=2e-11)
                n, d = objective.rational
                np.testing.assert_allclose(n(x)/d(x), evaluated, atol=2e-8, rtol=2e-10)
                rows.append({"analysis": name, "operator": list(operator), "x": x,
                             "polynomial_full_max_abs_events": float(np.max(abs(polynomial-full))),
                             "full_pair_max_abs_events": float(np.max(abs(pair-full))),
                             "native_profile_difference": float(evaluated-native.chi2),
                             "independent_augmented_least_squares_difference": cost-evaluated})
    return rows
