"""Sec. 3.3: canonical CsI2021 Slow counts, convergence, figures and tables.

The public experiment registry remains the authoritative detector calculation.
An optional scoped cache reuses exact repeated cross-section calls; it does not
approximate coefficients, alter integration nodes, or modify runtime files.
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
from dataclasses import asdict, dataclass
import hashlib
import inspect
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

import matplotlib
if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from cevns_pyeft.foundation import constants as constants
from cevns_pyeft.experiments.registry import get_slow_count_function
from cevns_pyeft.experiments.coherent.sns import loadNeutrinoEmpiricalFluxSNS, sns_component_state
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import (
    A_TARGET, DEFAULT_ACCEPTANCE, PE_BINS_9, efficiency,
)
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates import counts as rate_counts
from cevns_pyeft.rates import differential as rate_differential
from cevns_pyeft.sources.state import NeutrinoState

SOURCES = ("mu", "e", "mub")
TARGETS = ("Cs133", "I127")
TARGET_KEYS = ("Cs133", "I")
SCENARIOS = ("SM", "FV_NP", "SMplusFV")
SOURCE_LABELS = (r"Prompt $\nu_\mu$", r"Delayed $\nu_e$", r"Delayed $\bar\nu_\mu$")
SOURCE_COLORS = ("#0072B2", "#D55E00", "#009E73")
OUTPUT_DIR = Path(__file__).resolve().parent / "7. csi2021_detector_figures"
MAIN_NAME = "fig_csi_07_detector_level_FV"
RECOIL_NAME = "fig_csi_07_supplement_true_recoil"
TABLE_NAME = "table_csi2021_event_count_comparison"
STYLE = {
    "font.family": "serif", "font.serif": ["DejaVu Serif"], "mathtext.fontset": "stix",
    "font.size": 9, "axes.labelsize": 10, "axes.titlesize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "axes.linewidth": .8,
    "lines.linewidth": 1.8, "pdf.fonttype": 42, "ps.fonttype": 42,
    "figure.facecolor": "white", "savefig.facecolor": "white",
}


@dataclass(frozen=True)
class DetectorConfig:
    coefficient_gev_minus2: float = 1e-5
    sin2theta_w: float = .23873
    significant_bin_events: float = 1.
    max_bin_relative_change: float = .01
    max_small_bin_absolute_change: float = .02
    max_total_relative_change: float = .002


@dataclass(frozen=True)
class Grid:
    n_er: int
    n_enu: int
    n_pe_bin: int
    pe_step: float

    @property
    def name(self):
        return f"er{self.n_er}_enu{self.n_enu}_pe{self.n_pe_bin}_step{self.pe_step:g}"


GRIDS = (
    Grid(32, 48, 24, 3.), Grid(64, 96, 48, 1.5),
    Grid(128, 192, 96, .75), Grid(256, 384, 192, .375),
    Grid(512, 768, 384, .1875),
)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze(value):
    if isinstance(value, np.ndarray):
        return (value.dtype.str, value.shape, value.tobytes())
    if isinstance(value, NeutrinoState):
        return ("state", value.particle_kind, freeze(np.asarray(value.rho)))
    if isinstance(value, dict):
        return tuple(sorted((repr(k), freeze(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(freeze(v) for v in value)
    return value


class ExactSlowCache:
    """Serial, scoped memoization; every cache miss calls the original API."""
    def __init__(self):
        self.responses = {}
        self.kernel = {}
        self.sigma = {}
        self.stats = {"kernel_hits": 0, "kernel_misses": 0, "sigma_hits": 0, "sigma_misses": 0}

    def identity(self, response):
        # Hold the objects so Python cannot reuse an id during this context.
        self.responses.setdefault(id(response), response)
        return id(response)

    def wrapper(self, original, cache, kind):
        defaults = {name: parameter.default for name, parameter in inspect.signature(original).parameters.items()
                    if parameter.default is not inspect.Parameter.empty}

        def cached(response, ER_keV, Enu_MeV, **kwargs):
            merged = dict(defaults); merged.update(kwargs)
            if merged.get("debug_units", False):
                return original(response, ER_keV, Enu_MeV, **kwargs)
            key = (self.identity(response), float(ER_keV), freeze(np.asarray(Enu_MeV)), freeze(merged))
            if key in cache:
                self.stats[kind + "_hits"] += 1
                return cache[key]
            self.stats[kind + "_misses"] += 1
            result = original(response, ER_keV, Enu_MeV, **kwargs)
            cache[key] = result
            return result
        return cached

    def __enter__(self):
        self.original_kernel = rate_differential.differential_flavor_kernel_nn
        self.original_sigma = rate_counts.differential_cross_section_nn
        self.kernel_patch = patch.object(rate_differential, "differential_flavor_kernel_nn",
            self.wrapper(self.original_kernel, self.kernel, "kernel"))
        self.sigma_patch = patch.object(rate_counts, "differential_cross_section_nn",
            self.wrapper(self.original_sigma, self.sigma, "sigma"))
        self.kernel_patch.start(); self.sigma_patch.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.sigma_patch.stop(); self.kernel_patch.stop()
        assert rate_counts.differential_cross_section_nn is self.original_sigma
        assert rate_differential.differential_flavor_kernel_nn is self.original_kernel


def benchmark(config):
    matrix = np.zeros((3, 3), complex)
    matrix[0, 1] = config.coefficient_gev_minus2
    matrix[1, 0] = matrix[0, 1].conjugate()
    return {(6, 1, "u"): matrix}


def relative_error(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(np.max(np.abs(a-b))) / max(float(np.max(np.abs(a))), float(np.max(np.abs(b))), 1e-300)


def source_hashes(root):
    paths = ["experiments/registry.py", "experiments/coherent/sns.py", "experiments/coherent/slow_counts_csi2021.py",
             "rates/counts.py", "rates/differential.py", "foundation/constants.py", "foundation/units.py",
             "sources/state.py", "theory/kinematics.py", "nuclear/response.py", "theory/li2026/amplitude.py",
             "theory/li2026/cross_section.py", "theory/li2026/flavor.py", "theory/li2026/left_to_ci.py",
             "theory/li2026/responses.py", "theory/li2026/lec.py", "theory/li2026/operators.py"]
    return {p: digest(root / "src/cevns_pyeft" / p) for p in paths}


def contract(config, grid, root):
    return {"algorithm": "canonical-slow-exact-memo-v1", "config": asdict(config), "grid": asdict(grid),
            "source_sha256": source_hashes(root),
            "response_json_sha256": digest(root / "data/responses/responses_all.json"),
            "numerical_code_sha256": hashlib.sha256((inspect.getsource(compute_grid)
                 + inspect.getsource(ExactSlowCache) + inspect.getsource(freeze)).encode()).hexdigest(),
            "numpy_version": np.__version__}


def validate_cache(config, root=ROOT):
    """Compare cached and uncached public Slow outputs, without changing grids."""
    public = get_slow_count_function("CsI2021")
    kwargs = dict(wc_triplets=benchmark(config), include_sm=True, sin2thetaW=config.sin2theta_w,
                  n_er=5, n_enu=8, n_pe_bin=4, pe_step=3.)
    start = time.perf_counter()
    direct = public(root / "data/responses/responses_all.json", **kwargs)
    with ExactSlowCache() as memo:
        cached = public(root / "data/responses/responses_all.json", **kwargs)
    for name in ("counts_per_bin", "counts_per_npe"):
        for key in (*SOURCES, "total"):
            np.testing.assert_array_equal(cached[name][key], direct[name][key])
    for source in SOURCES:
        for target in TARGETS:
            np.testing.assert_array_equal(cached["target_flavor_counts_per_bin"][source][target],
                                          direct["target_flavor_counts_per_bin"][source][target])
    return {"passed": True, "comparison": "bitwise equal public Slow outputs", "grid": kwargs | {"wc_triplets": "same FV benchmark"},
            "elapsed_seconds": time.perf_counter()-start, "stats": memo.stats}


def fold_saved_recoil(recoil, rate, grid, pe_edges):
    """Repeat canonical PE interpolation/bin integration using saved recoil yields."""
    pe_grid = np.arange(pe_edges[0], pe_edges[-1] + .5 * grid.pe_step, grid.pe_step)
    smear = np.stack([np.asarray(rate_differential.p_smearing_csi(pe_grid, float(t))) for t in recoil], axis=1)
    dndpe = np.trapezoid(smear * rate[None, :], recoil, axis=1)
    result = []
    for left, right in zip(pe_edges[:-1], pe_edges[1:]):
        nodes = np.linspace(left, right, grid.n_pe_bin)
        values = np.interp(nodes, pe_grid, dndpe, left=0., right=0.)
        result.append(np.trapezoid(values * efficiency(nodes), nodes))
    return np.asarray(result)


def compute_grid(config, grid, root=ROOT, memoize=True):
    root = Path(root).resolve()
    start = time.perf_counter()
    public = get_slow_count_function("CsI2021")
    response_json = root / "data/responses/responses_all.json"
    db = ResponseDB(response_json)
    flux = loadNeutrinoEmpiricalFluxSNS("CsI2021")
    mass = float(flux["basic"]["detectorMassKg"])
    weights = np.asarray([A_TARGET[t] for t in TARGETS]) / sum(A_TARGET.values())
    acceptance = np.asarray([DEFAULT_ACCEPTANCE[s] for s in SOURCES])
    raw = np.empty((3, 3, 2, 9))
    counts = np.empty((3, 3, 9)); density = np.empty_like(counts)
    public_total = np.empty((3, 9)); public_total_density = np.empty_like(public_total)
    recoil_grids = np.stack([rate_counts._er_grid(db.get(k), grid.n_er)[0] for k in TARGET_KEYS])
    recoil_events = np.empty((3, 3, 2, grid.n_er))
    independent_fold = np.empty_like(raw)
    kwargs = dict(sin2thetaW=config.sin2theta_w, c10_mass_mode="quark_mass_resolved",
                  n_er=grid.n_er, n_enu=grid.n_enu, n_pe_bin=grid.n_pe_bin, pe_step=grid.pe_step)
    memo = ExactSlowCache() if memoize else None
    with memo if memo is not None else nullcontext():
        for scenario_index, (scenario, wc, sm) in enumerate((
                ("SM", {}, True), ("FV_NP", benchmark(config), False),
                ("SMplusFV", benchmark(config), True))):
            print(f"  {grid.name}: {scenario} public Slow calculation", flush=True)
            prediction = public(response_json, wc_triplets=wc, include_sm=sm, **kwargs)
            pe_edges = np.asarray(prediction["pe_bins"])
            np.testing.assert_array_equal(pe_edges, PE_BINS_9)
            for si, source in enumerate(SOURCES):
                counts[scenario_index, si] = prediction["counts_per_bin"][source]
                density[scenario_index, si] = prediction["counts_per_npe"][source]
                for ti, (target, key) in enumerate(zip(TARGETS, TARGET_KEYS)):
                    raw[scenario_index, si, ti] = prediction["target_flavor_counts_per_bin"][source][target]
                    # Physical target yields before component time acceptance.
                    rate = rate_counts._rate_per_kg(db.get(key), flux, recoil_grids[ti], source, wc, sm,
                        config.sin2theta_w, "quark_mass_resolved", grid.n_enu, source_state=sns_component_state(source))
                    recoil_events[scenario_index, si, ti] = np.asarray(rate) * mass * weights[ti]
                    independent_fold[scenario_index, si, ti] = fold_saved_recoil(
                        recoil_grids[ti], recoil_events[scenario_index, si, ti], grid, pe_edges) * acceptance[si]
            public_total[scenario_index] = prediction["counts_per_bin"]["total"]
            public_total_density[scenario_index] = prediction["counts_per_npe"]["total"]
            print(f"  {scenario}: {float(public_total[scenario_index].sum()):.8f} events", flush=True)
    weighted = raw * weights[None, None, :, None] * acceptance[None, :, None, None]
    widths = np.diff(pe_edges)
    checks = {
        "source_sum_max_relative_error": relative_error(counts.sum(axis=1), public_total),
        "target_sum_max_relative_error": relative_error(weighted.sum(axis=2), counts),
        "counts_density_max_relative_error": relative_error(density * widths, counts),
        "total_density_max_relative_error": relative_error(public_total_density * widths, public_total),
        "saved_recoil_to_PE_fold_max_relative_error": relative_error(independent_fold, weighted),
        "FV_additivity_max_relative_error": relative_error(counts[2], counts[0] + counts[1]),
        "FV_additivity_target_max_relative_error": relative_error(weighted[2], weighted[0] + weighted[1]),
        "true_recoil_FV_additivity_max_relative_error": relative_error(recoil_events[2], recoil_events[0] + recoil_events[1]),
    }
    for name, error in checks.items():
        assert error < 1e-11, (grid.name, name, error)
    assert np.all(np.isfinite(counts)) and np.all(counts >= 0.)
    numbers = mass * weights / (np.asarray([133., 127.]) * 1.6605390666e-27)
    checks["equal_Cs_I_nucleus_numbers_relative_error"] = relative_error(numbers[0], numbers[1])
    fluence = flux["basic"]["NTimeIntegratedFlux_cm^-2"]
    explicit_fluence = flux["basic"]["r"] * flux["basic"]["N_POT"] / (4*np.pi*(100*flux["basic"]["baseline_m"])**2)
    checks["fluence_normalization_relative_error"] = relative_error(fluence, explicit_fluence)
    assert checks["equal_Cs_I_nucleus_numbers_relative_error"] < 1e-14
    assert checks["fluence_normalization_relative_error"] < 1e-14
    return dict(grid=asdict(grid), config=asdict(config), pe_edges=pe_edges, counts_per_bin=counts,
                counts_per_npe=density, public_total=public_total, public_total_density=public_total_density,
                target_flavor_raw=raw, target_flavor_weighted=weighted,
                recoil_grids_keV=recoil_grids, true_recoil_pre_time_acceptance=recoil_events,
                true_recoil_post_time_acceptance=recoil_events * acceptance[None, :, None, None],
                independently_folded_target_counts=independent_fold,
                mass_fractions=weights, time_acceptance=acceptance, target_numbers=numbers,
                fluence_per_source_cm_minus2=fluence, source_basic=flux["basic"], checks=checks,
                elapsed_seconds=time.perf_counter()-start, cache_stats=memo.stats if memo else {})


def save_grid(data, directory, numerical_contract):
    directory.mkdir(parents=True, exist_ok=True)
    array_keys = [key for key, value in data.items() if isinstance(value, np.ndarray)]
    np.savez_compressed(directory / "prediction.npz", **{key: data[key] for key in array_keys})
    info = {key: value for key, value in data.items() if key not in array_keys}
    info["contract"] = numerical_contract
    (directory / "metadata.json").write_text(json.dumps(info, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")


def load_grid(directory, numerical_contract):
    if not (directory / "metadata.json").is_file() or not (directory / "prediction.npz").is_file():
        return None
    info = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    if info["contract"] != numerical_contract:
        raise RuntimeError(f"Stale numerical cache: {directory}; use another output directory")
    with np.load(directory / "prediction.npz", allow_pickle=False) as arrays:
        info.update({key: arrays[key] for key in arrays.files})
    info.pop("contract")
    return info


def compare_grids(previous, current, config):
    # Test each physical source/target/bin, each source sum and inclusive bins.
    a = np.concatenate([previous["target_flavor_weighted"].reshape(3, -1),
                        previous["counts_per_bin"].reshape(3, -1), previous["public_total"]], axis=1)
    b = np.concatenate([current["target_flavor_weighted"].reshape(3, -1),
                        current["counts_per_bin"].reshape(3, -1), current["public_total"]], axis=1)
    significant = b >= config.significant_bin_events
    relative = float(np.max(np.abs(a[significant]-b[significant])/b[significant]))
    small = float(np.max(np.abs(a[~significant]-b[~significant]))) if np.any(~significant) else 0.
    total_a = previous["public_total"].sum(axis=1)
    total_b = current["public_total"].sum(axis=1)
    totals = np.abs(total_a-total_b) / np.maximum(np.abs(total_b), 1e-300)
    passed = (relative <= config.max_bin_relative_change and small <= config.max_small_bin_absolute_change
              and np.max(totals) <= config.max_total_relative_change)
    return {"previous_grid": previous["grid"], "current_grid": current["grid"],
            "max_significant_bin_relative_change": relative,
            "max_small_bin_absolute_change_events": small,
            "inclusive_total_relative_changes": dict(zip(SCENARIOS, totals.tolist())),
            "passed": bool(passed), "criterion": {
                "significant_bin_events": config.significant_bin_events,
                "max_bin_relative_change": config.max_bin_relative_change,
                "max_small_bin_absolute_change_events": config.max_small_bin_absolute_change,
                "max_total_relative_change": config.max_total_relative_change}}


def run_calculation(config=DetectorConfig(), output_dir=OUTPUT_DIR, max_levels=5):
    output_dir = Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    validation_path = output_dir / "exact_cache_validation.json"
    if validation_path.is_file():
        cache_check = json.loads(validation_path.read_text())
        if cache_check["source_sha256"] != source_hashes(ROOT):
            raise RuntimeError("Cached/uncached validation is stale")
    else:
        print("Checking exact memoization against uncached public Slow outputs...", flush=True)
        cache_check = validate_cache(config)
        cache_check["source_sha256"] = source_hashes(ROOT)
        validation_path.write_text(json.dumps(cache_check, indent=2)+"\n", encoding="utf-8")
        print("PASS: cached and uncached outputs are bitwise identical.", flush=True)
    runs = []; comparisons = []
    for level, grid in enumerate(GRIDS[:max_levels]):
        numerical_contract = contract(config, grid, ROOT)
        directory = output_dir / "grids" / grid.name
        data = load_grid(directory, numerical_contract)
        if data is None:
            print("Starting grid", grid.name, flush=True)
            data = compute_grid(config, grid)
            save_grid(data, directory, numerical_contract)
        else:
            print("Reusing validated numerical grid", grid.name, flush=True)
        runs.append(data)
        if len(runs) >= 2:
            comparison = compare_grids(runs[-2], runs[-1], config)
            comparisons.append(comparison)
            print(json.dumps(comparison), flush=True)
        progress = {"completed_grids": [r["grid"] for r in runs], "comparisons": comparisons,
                    "convergence_passed": bool(comparisons and comparisons[-1]["passed"]),
                    "selected_grid": data["grid"]}
        (output_dir / "convergence_report.json").write_text(json.dumps(progress, indent=2)+"\n", encoding="utf-8")
        # Always include the requested demo grid and at least two refinements.
        if level >= 2 and comparisons[-1]["passed"]:
            break
    return {"data": runs[-1], "runs": runs, "comparisons": comparisons,
            "convergence_passed": bool(comparisons and comparisons[-1]["passed"]),
            "cache_validation": cache_check}


def save_figure(fig, output, name):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(STYLE):
        for ext in ("pdf", "png"):
            path = output / f"{name}.{ext}"
            fig.savefig(path, dpi=400, bbox_inches="tight", pad_inches=.07)
            print("Saved:", path, flush=True)


def plot_detector(result):
    data = result["data"]; edges = data["pe_edges"]; widths = np.diff(edges)
    density = data["public_total_density"]
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 3, figsize=(10.4, 4.0))
        fig.subplots_adjust(left=.065, right=.985, bottom=.24, top=.72, wspace=.39)
        fig.suptitle("Detector-level predictions for COHERENT CsI-2021", x=.53, y=.985, fontsize=12)
        fig.text(.53, .91, r"$\hat{\mathcal{C}}^{6u}_{1,e\mu}=\hat{\mathcal{C}}^{6u*}_{1,\mu e}=10^{-5}\,\mathrm{GeV}^{-2}$",
                 ha="center", fontsize=10)
        ax=axes[0]
        for si, label, color, ls, lw in ((0,"SM","#777777","--",1.7),(1,"FV NP only","#CC79A7","-.",2.3),(2,"SM + FV NP","#111111","-",1.2)):
            ax.stairs(density[si], edges, baseline=None, label=label, color=color, ls=ls, lw=lw)
        ax.set_yscale("log"); ax.set_ylabel("Events / PE")
        ax.set_title("(a) SM and flavor-violating NP",loc="left",y=1.10,pad=4)
        ax.legend(frameon=False,fontsize=8,loc="upper right")
        ax=axes[1]
        delta=(data["counts_per_bin"][2]-data["counts_per_bin"][0])/widths
        for si,(label,color) in enumerate(zip(SOURCE_LABELS,SOURCE_COLORS)):
            ax.stairs(delta[si],edges,baseline=None,label=label,color=color,ls=("-","--","-.")[si])
        ax.set_yscale("log"); ax.set_ylabel(r"$\Delta N_i/\Delta n_{{\rm PE},i}$")
        ax.set_title("(b) Source-resolved excess",loc="left",y=1.10,pad=4)
        ax.legend(frameon=False,fontsize=8,loc="lower left")
        ax=axes[2]
        targets=data["target_flavor_weighted"][2].sum(axis=0)/widths
        ax.bar(edges[:-1],targets[0],width=widths,align="edge",color="#0072B2",alpha=.6,label=r"$^{133}\mathrm{Cs}$")
        ax.bar(edges[:-1],targets[1],width=widths,align="edge",bottom=targets[0],color="#E69F00",alpha=.6,label=r"$^{127}\mathrm{I}$")
        ax.stairs(density[2],edges,baseline=None,color="#111111",lw=1.1,label="SM + FV NP")
        ax.set_ylabel("Events / PE")
        ax.set_title("(c) Physical target contributions",loc="left",y=1.10,pad=4)
        ax.legend(frameon=False,fontsize=8,loc="upper right")
        for ax in axes:
            ax.set_xlim(0,60);ax.set_xticks([0,20,40,60])
            ax.set_xlabel(r"Reconstructed $n_{\rm PE}$")
            ax.tick_params(which="both",direction="in",top=True,right=True)
            ax.grid(axis="y",alpha=.2,lw=.5)
        fig.text(.53,.025,"Signal predictions only; current time-integrated SNS and antineutrino conventions",ha="center",fontsize=8)
        return fig


def plot_recoil(result):
    data=result["data"]
    grid=np.linspace(.1,float(np.max(data["recoil_grids_keV"])),350)
    by_source=np.empty((3,len(grid)))
    for si in range(3):
        by_source[si]=sum(np.interp(grid,data["recoil_grids_keV"][ti],data["true_recoil_pre_time_acceptance"][2,si,ti],left=0,right=0) for ti in range(2))
    with plt.rc_context(STYLE):
        fig,ax=plt.subplots(figsize=(6.3,4.3))
        for si,(label,color) in enumerate(zip(SOURCE_LABELS,SOURCE_COLORS)):
            ax.plot(grid,by_source[si],color=color,ls=("-","--","-.")[si],label=label)
        ax.plot(grid,by_source.sum(axis=0),color="#111111",lw=1.3,label="Total")
        ax.set_yscale("log");ax.set_xlim(0,grid[-1])
        ax.set_xlabel(r"True nuclear recoil $T_{\rm nr}$ [keV]")
        ax.set_ylabel(r"$dN/dT_{\rm nr}$ [events/keV]")
        ax.set_title("SM + FV NP: CsI2021 true recoil spectrum",fontsize=11)
        ax.legend(frameon=False,fontsize=9)
        ax.tick_params(which="both",direction="in",top=True,right=True)
        ax.text(.97,.06,"Before component time acceptance and PE response",ha="right",transform=ax.transAxes,fontsize=8)
        fig.tight_layout()
        return fig


def source_table(result):
    counts=result["data"]["counts_per_bin"].sum(axis=2)
    table=np.column_stack([counts.T,counts[2]-counts[0]])
    return np.vstack([table,table.sum(axis=0)])


def plot_table(result):
    values=source_table(result)
    with plt.rc_context(STYLE):
        fig,ax=plt.subplots(figsize=(7.7,2.5));ax.axis("off")
        ax.set_title("COHERENT CsI-2021: expected events in the nine PE bins",fontsize=11,pad=15)
        table=ax.table(cellText=[[f"{x:.3f}" for x in row] for row in values],
            rowLabels=[*SOURCE_LABELS,"Total"],colLabels=["SM","FV NP only","SM + FV NP",r"$\Delta N$"],
            loc="center",cellLoc="right",rowLoc="left",colWidths=[.18]*4)
        table.auto_set_font_size(False);table.set_fontsize(9);table.scale(1,1.6)
        for (row,col),cell in table.get_celld().items():
            cell.set_edgecolor("#cccccc");cell.set_linewidth(.5)
            if row in (0,4):cell.set_facecolor("#eeeeee")
        fig.tight_layout()
        return fig


def export(result,output=OUTPUT_DIR):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    data=result["data"]
    arrays={k:v for k,v in data.items() if isinstance(v,np.ndarray)}
    np.savez_compressed(output/"csi2021_detector_complete.npz",**arrays)
    rows=[]
    widths=np.diff(data["pe_edges"])
    for si,scenario in enumerate(SCENARIOS):
        for fi,source in enumerate(SOURCES):
            for ti,target in enumerate(TARGETS):
                for b in range(9):
                    rows.append((scenario,source,target,b,data["pe_edges"][b],data["pe_edges"][b+1],
                        data["target_flavor_raw"][si,fi,ti,b],data["target_flavor_weighted"][si,fi,ti,b],
                        data["target_flavor_weighted"][si,fi,ti,b]/widths[b]))
    import csv
    with (output/"source_target_bin_predictions.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.writer(f);writer.writerow(["scenario","source","target","bin","PE_low","PE_high","raw_full_mass_preacceptance_events","physical_weighted_accepted_events","physical_events_per_PE"]);writer.writerows(rows)
    table=source_table(result)
    with (output/(TABLE_NAME+".csv")).open("w",encoding="utf-8",newline="") as f:
        writer=csv.writer(f);writer.writerow(["source","SM","FV_NP","SMplusFV","DeltaN"])
        writer.writerows(zip([*SOURCES,"total"],*table.T))
    target_table=data["target_flavor_weighted"].sum(axis=(1,3)).T
    with (output/"target_total_comparison.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.writer(f);writer.writerow(["target","SM","FV_NP","SMplusFV"]);writer.writerows(zip(TARGETS,*target_table.T))
    md="| Source | SM | FV NP only | SM+FV NP | Delta N |\n|---|---:|---:|---:|---:|\n"
    for name,row in zip(["Prompt nu_mu","Delayed nu_e","Delayed anti-nu_mu","Total"],table):
        md+="| "+name+" | "+" | ".join(f"{x:.6f}" for x in row)+" |\n"
    (output/(TABLE_NAME+".md")).write_text(md,encoding="utf-8")
    tex=[r"\begin{tabular}{lrrrr}",r"\hline",r"Source & SM & FV NP & SM+FV NP & $\Delta N$ \\",r"\hline"]
    for name,row in zip([r"Prompt $\nu_\mu$",r"Delayed $\nu_e$",r"Delayed $\bar\nu_\mu$","Total"],table):
        tex.append(name+" & "+" & ".join(f"{x:.3f}" for x in row)+r" \\")
    tex.extend([r"\hline",r"\end{tabular}"])
    (output/(TABLE_NAME+".tex")).write_text("\n".join(tex)+"\n",encoding="utf-8")
    checks={"selected_grid":data["grid"],"convergence_passed":result["convergence_passed"],
            "algebra_and_unit_checks":data["checks"],"last_grid_comparison":result["comparisons"][-1] if result["comparisons"] else None,
            "exact_memoization_validated":result["cache_validation"]["passed"]}
    (output/"validation_summary.json").write_text(json.dumps(checks,indent=2)+"\n",encoding="utf-8")
    metadata={"config":data["config"],"grid":data["grid"],"scenarios":SCENARIOS,"sources":SOURCES,"targets":TARGETS,
        "source_basic":data["source_basic"],"mass_fractions":data["mass_fractions"].tolist(),"target_numbers":data["target_numbers"].tolist(),
        "time_acceptance":dict(zip(SOURCES,data["time_acceptance"].tolist())),"source_sha256":source_hashes(ROOT),
        "response_json_sha256":digest(ROOT/"data/responses/responses_all.json"),"generator_sha256":digest(__file__),
        "axes":{"counts_per_bin":["scenario","source","PE_bin"],"target_flavor_raw":["scenario","source","target","PE_bin"],
                "target_flavor_weighted":["scenario","source","target","PE_bin"],"true_recoil_pre_time_acceptance":["scenario","source","target","recoil_node"]},
        "raw_target_semantics":"hypothetical full detector mass pure-isotope yield before time acceptance; not the physical Cs/I contribution",
        "physical_target_semantics":"raw times A/(133+127) times the source time acceptance",
        "fluence_semantics":"POT-integrated cm^-2 MeV^-1; no extra exposure or seconds/day conversion",
        "antineutrino_convention":"mub is a mu-flavor antinu source state; interaction follows the current shared kernel, without a separately audited antineutrino dynamical change",
        "statistics":"signal-only expected events; no backgrounds, likelihood or fit", "checks":checks}
    (output/"metadata.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    caption=("Detector-level signal predictions for COHERENT CsI-2021 with the same flavor-violating vector benchmark as Sec. 3.2. "
        "Panel (a) compares SM, FV NP-only and SM+FV NP events per PE. Panel (b) shows source-resolved Delta N = N(SM+FV)-N(SM). "
        "Panel (c) shows the physical Cs133/I127 SM+FV contributions, including stoichiometric mass fractions and component time acceptances. "
        "All scenarios share the source, target, detector and numerical grid. Nine unequal PE-bin widths are retained. "
        "The anti-nu_mu contribution uses the current program convention. No backgrounds or experimental fit enter.")
    (output/(MAIN_NAME+"_caption.txt")).write_text(caption+"\n",encoding="utf-8")
    report=("# Sec. 3.3 detector-level FV benchmark\n\n"+md+"\n"
        f"Selected grid: {data['grid']}. Convergence passed: {result['convergence_passed']}.\n\n"
        "The initial (32,48,24) grid is retained as a demonstration reference. The final two grids are compared in convergence_report.json. "
        "The declared tolerances are 1% for physical source/target/bin contributions >=1 event, 0.02 event below that threshold, "
        "and 0.2% for each inclusive scenario total. This is a numerical grid check, not an experimental precision claim.\n\n"
        "The canonical get_slow_count_function('CsI2021') produces all PE predictions. Scoped exact memoization is checked against uncached "
        "public Slow results. Intermediate true recoils are independently folded back into PE and compared to physical target counts.\n\n"
        "Raw target arrays describe a full detector mass made of one isotope before time acceptance. Physical target contributions multiply "
        "133/260 or 127/260 and the source acceptance. Cs/I nucleus numbers are equal. POT already enters the SNS fluence, and detector mass "
        "enters once. True recoil arrays are saved both before and after the component time acceptance. The supplement shows the former.\n\n"
        "The dimension-six non-diagonal Wilson coefficient and its Hermitian partner are 1e-5 GeV^-2; sin^2(theta_W)=0.23873 matches Sec. 3.2. "
        "The detector default 0.2387 is explicitly overridden. The mub source follows the existing shared-kernel antineutrino convention; "
        "this run does not independently audit general EFT antineutrino dynamics. There is no likelihood or data fit.\n\n"
        "Reproduce from Gitup01 using the project Python environment:\n\n"
        "```powershell\npython -X utf8 -B \"论文图NoteBook/generate_csi2021_detector_figures.py\"\n```\n\n"
        "Reruns reuse only grid caches with matching physics/configuration/source fingerprints. Full results for every grid are retained under grids/.\n")
    (output/"NUMERICAL_REPORT.md").write_text(report,encoding="utf-8")
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=OUTPUT_DIR)
    parser.add_argument("--max-levels",type=int,default=5,choices=range(1,6))
    args=parser.parse_args()
    result=run_calculation(output_dir=args.output_dir,max_levels=args.max_levels)
    for function,name in ((plot_detector,MAIN_NAME),(plot_recoil,RECOIL_NAME),(plot_table,TABLE_NAME)):
        fig=function(result);save_figure(fig,args.output_dir,name);plt.close(fig)
    export(result,args.output_dir)
    print("Convergence passed:",result["convergence_passed"],flush=True)
    print(source_table(result),flush=True)


if __name__=="__main__":
    main()
