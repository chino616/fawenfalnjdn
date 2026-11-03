"""Generate a consistent Cs133 R -> W -> K -> cross-section figure set.

Run with the project Python interpreter, or import the functions in a notebook.
Only this plotting layer writes outputs; the runtime theory and input tables
are used without modification.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cevns_pyeft.foundation import constants as constants
from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import (
    _build_total_left_hat,
    differential_cross_section_nn,
)
from cevns_pyeft.sources.state import pure_flavor_state
from cevns_pyeft.theory.kinematics import two_body_recoil_max_GeV
from cevns_pyeft.theory.li2026.amplitude import flavor_kernel_onebody_li2026
from cevns_pyeft.theory.li2026.lec import DEFAULT_LECS
from cevns_pyeft.theory.li2026.left_to_ci import left_to_ci
from cevns_pyeft.theory.li2026.responses import compute_R_matrices


@dataclass(frozen=True)
class FigureConfig:
    energy_mev: float = 30.0
    coefficient_gev_minus2: float = 1.0e-5
    sin2theta_w: float = 0.23873
    recoil_min_kev: float = 0.05
    recoil_max_kev: float = 13.0
    n_recoil: int = 160


# One mapping and one set of colors are shared by all three figures.
CHANNELS = (
    {"r": "MM", "w": "M", "label": r"$M$", "color": "#0072B2", "ls": "-"},
    {"r": "SSP", "w": "SigmaP", "label": r"$\Sigma'$", "color": "#D55E00", "ls": "--"},
    {"r": "DD", "w": "Delta", "label": r"$\Delta$", "color": "#009E73", "ls": "-."},
)
ALL_CHANNELS = {
    "MM": "M", "SSPP": "SigmaPP", "SSP": "SigmaP", "PhiPP": "PhiPP",
    "PhiPT": "PhiPT", "DD": "Delta", "MPhiPP": "MPhiPP", "SigmaPDelta": "SigmaPDelta",
}
SCENARIOS = ("SM", "NP", "SM+NP")
SCENARIO_STYLES = {
    "SM": dict(color="#777777", ls="--", lw=1.7),
    "NP": dict(color="#CC79A7", ls="-.", lw=2.4),
    "INT": dict(color="#E69F00", ls="--", lw=2.4),
    "SM+NP": dict(color="#111111", ls="-", lw=1.1),
}
STYLE = {
    "font.family": "serif", "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 9,
    "axes.labelsize": 10, "axes.titlesize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.linewidth": 0.8, "lines.linewidth": 1.8,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "figure.facecolor": "white", "savefig.facecolor": "white",
}
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "6. unified_R_W_K_figures"
FIGURE_NAMES = (
    "fig_unified_01_particle_R",
    "fig_unified_02_nuclear_W",
    "fig_unified_03_kernel_cross_sections",
)


def scaled_error(a, b):
    a, b = np.asarray(a), np.asarray(b)
    scale = max(float(np.max(np.abs(a))), float(np.max(np.abs(b))), 1e-300)
    return float(np.max(np.abs(a - b))) / scale


def pointwise_error(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(np.max(np.abs(a - b) / np.maximum(np.maximum(np.abs(a), np.abs(b)), 1e-300)))


def contract_responses(responses, nuclear_at_recoil):
    """Use all four nucleon pairs and the current engine's mixed-channel rule."""
    pieces = {}
    for rkey, wkey in ALL_CHANNELS.items():
        piece = np.einsum("abij,ij->ab", responses[rkey], nuclear_at_recoil[wkey], optimize=True)
        if wkey == "MPhiPP":
            piece = 0.5 * (piece + piece.conj().T)
        pieces[wkey] = piece
    return pieces, sum(pieces.values())


def calculate(config=FigureConfig(), root=PROJECT_ROOT):
    """Compute one common data set, including final-flavor-resolved kernels.

    NR coefficients have [final, initial] flavor axes. Selecting one final row
    before c_i^dagger c_j restricts the unobserved-final-flavor sum. This is a
    final-state diagnostic, not a change to the physical Wilson input.
    """
    root = Path(root).resolve()
    if config.n_recoil < 2 or config.energy_mev <= 0:
        raise ValueError("Positive energy and at least two recoil points are required")
    if not 0 < config.recoil_min_kev < config.recoil_max_kev:
        raise ValueError("Recoil range must be finite and strictly positive")
    if not all(np.isfinite(v) for v in asdict(config).values()):
        raise ValueError("All figure inputs must be finite")
    response_path = root / "data/responses/responses_all.json"
    target = ResponseDB(response_path).get("Cs133")
    energy = config.energy_mev * constants.MeV
    mass = 133 * constants.AMU_GEV
    endpoint = two_body_recoil_max_GeV(energy, mass) / constants.keV
    if config.recoil_max_kev >= endpoint:
        raise ValueError("Figure recoil range must stay below the elastic endpoint")
    recoil = np.linspace(config.recoil_min_kev, config.recoil_max_kev, config.n_recoil)
    qabs2 = 2 * mass * recoil * constants.keV
    qabs = np.sqrt(qabs2)
    y = (0.5 * qabs * float(target.basic["b"])) ** 2
    nuclear = {w: np.asarray([target.W_np(w, float(yy)) for yy in y], dtype=float)
               for w in ALL_CHANNELS.values()}
    coefficient = np.zeros((3, 3), dtype=complex)
    coefficient[0, 1] = config.coefficient_gev_minus2
    coefficient[1, 0] = coefficient[0, 1].conjugate()
    wc_np = {(6, 1, "u"): coefficient}
    cases = {"SM": ({}, True), "NP": (wc_np, False), "SM+NP": (wc_np, True)}
    left = {s: _build_total_left_hat(left_wcs=None, wc_triplets=wc, include_sm=sm,
                                    sin2thetaW=config.sin2theta_w)
            for s, (wc, sm) in cases.items()}
    n = len(recoil)
    particle = {s: {r: np.empty((n, 3, 3, 2, 2), complex) for r in ALL_CHANNELS} for s in SCENARIOS}
    pieces = {s: {w: np.empty((n, 3, 3), complex) for w in ALL_CHANNELS.values()} for s in SCENARIOS}
    kernel = {s: np.empty((n, 3, 3), complex) for s in SCENARIOS}
    final_kernel = {s: np.empty((n, 3, 3, 3), complex) for s in SCENARIOS}
    dsigma = {s: np.empty(n) for s in SCENARIOS}
    state_mu = pure_flavor_state("mu", particle_kind="nu")
    conversion = mass / (8 * np.pi * energy**2) * constants.GEV_INV2_TO_CM2 * constants.keV
    checks = {
        "manual_nucleon_contraction_max_scaled_error": 0.,
        "all_channel_sum_max_scaled_error": 0.,
        "final_flavor_sum_max_scaled_error": 0.,
        "final_projection_matches_projected_LEFT_max_scaled_error": 0.,
        "cross_section_unit_conversion_max_relative_error": 0.,
        "kernel_hermiticity_max_scaled_error": 0.,
    }
    for it, tkev in enumerate(recoil):
        t = float(tkev) * constants.keV
        w_at_t = {w: nuclear[w][it] for w in nuclear}
        for scenario, (wc, include_sm) in cases.items():
            ci = left_to_ci(left[scenario], E_nu=energy, q0=t, q2=t*t-qabs2[it],
                            qabs=qabs[it], qabs2=qabs2[it], mA=mass)
            ci_basis = {i: (ci.p[i], ci.n[i]) for i in range(1, 15)}
            kwargs = dict(E_nu=energy, qabs=qabs[it], qabs2=qabs2[it],
                          mA=mass, mN=DEFAULT_LECS.m_N, basis="np")
            responses = compute_R_matrices(ci_basis, **kwargs)
            manual_pieces, manual_total = contract_responses(responses, w_at_t)
            engine = flavor_kernel_onebody_li2026(target, E_nu_GeV=energy,
                       ER_keV=float(tkev), left_hat=left[scenario], basis="np")
            for rkey, wkey in ALL_CHANNELS.items():
                particle[scenario][rkey][it] = responses[rkey]
                engine_piece = engine.pieces.get(wkey, np.zeros((3, 3), complex))
                pieces[scenario][wkey][it] = engine_piece
                error = scaled_error(manual_pieces[wkey], engine_piece)
                assert error < 1e-12, (scenario, wkey, tkev, error)
                checks["manual_nucleon_contraction_max_scaled_error"] = max(
                    checks["manual_nucleon_contraction_max_scaled_error"], error)
            kernel[scenario][it] = engine.kernel
            error = scaled_error(manual_total, engine.kernel)
            assert error < 1e-12
            checks["all_channel_sum_max_scaled_error"] = max(checks["all_channel_sum_max_scaled_error"], error)
            error = scaled_error(engine.kernel, engine.kernel.conj().T)
            assert error < 1e-12
            checks["kernel_hermiticity_max_scaled_error"] = max(checks["kernel_hermiticity_max_scaled_error"], error)

            # Resolve the final flavor in every scenario, before forming bilinears.
            for final in range(3):
                projector = np.zeros((3, 3)); projector[final, final] = 1.
                selected = {i: (projector @ p, projector @ nn) for i, (p, nn) in ci_basis.items()}
                final_responses = compute_R_matrices(selected, **kwargs)
                _, final_kernel[scenario][it, final] = contract_responses(final_responses, w_at_t)
                if it in {0, n // 2, n - 1}:
                    selected_left = {key: projector @ value for key, value in left[scenario].items()}
                    selected_engine = flavor_kernel_onebody_li2026(
                        target, E_nu_GeV=energy, ER_keV=float(tkev), left_hat=selected_left, basis="np")
                    error = scaled_error(final_kernel[scenario][it, final], selected_engine.kernel)
                    assert error < 1e-12
                    checks["final_projection_matches_projected_LEFT_max_scaled_error"] = max(
                        checks["final_projection_matches_projected_LEFT_max_scaled_error"], error)
            error = scaled_error(final_kernel[scenario][it].sum(axis=0), engine.kernel)
            assert error < 1e-12
            checks["final_flavor_sum_max_scaled_error"] = max(checks["final_flavor_sum_max_scaled_error"], error)
            dsigma[scenario][it] = float(differential_cross_section_nn(
                target, ER_keV=float(tkev), Enu_MeV=config.energy_mev, rho=state_mu,
                wc_triplets=wc, include_sm=include_sm, sin2thetaW=config.sin2theta_w,
                basis="np").dsigma_cm2_per_keV)
            error = pointwise_error(dsigma[scenario][it], engine.kernel[1, 1].real * conversion)
            assert error < 1e-12
            checks["cross_section_unit_conversion_max_relative_error"] = max(
                checks["cross_section_unit_conversion_max_relative_error"], error)
    for container in (particle, pieces, kernel, final_kernel, dsigma):
        if isinstance(container["SM"], dict):
            container["INT"] = {key: container["SM+NP"][key] - container["SM"][key] - container["NP"][key]
                                for key in container["SM"]}
        else:
            container["INT"] = container["SM+NP"] - container["SM"] - container["NP"]

    # Observable transitions for the pure muon-neutrino input, not K[e,mu].
    transitions = {
        "SM_mu_to_mu": conversion * final_kernel["SM"][:, 1, 1, 1].real,
        "FC_NP_mu_to_e": conversion * final_kernel["NP"][:, 0, 1, 1].real,
        "total_mu_to_e": conversion * final_kernel["SM+NP"][:, 0, 1, 1].real,
        "total_mu_to_mu": conversion * final_kernel["SM+NP"][:, 1, 1, 1].real,
        "total_mu_to_tau": conversion * final_kernel["SM+NP"][:, 2, 1, 1].real,
    }
    by_response = {w: conversion * pieces["SM+NP"][w][:, 1, 1].real for w in ALL_CHANNELS.values()}
    checks["all_response_cross_sections_sum_max_relative_error"] = pointwise_error(sum(by_response.values()), dsigma["SM+NP"])
    checks["SM_mu_to_mu_matches_SM_inclusive_max_relative_error"] = pointwise_error(transitions["SM_mu_to_mu"], dsigma["SM"])
    checks["FC_mu_to_e_matches_NP_inclusive_max_relative_error"] = pointwise_error(transitions["FC_NP_mu_to_e"], dsigma["NP"])
    checks["SM_plus_FC_matches_total_max_relative_error"] = pointwise_error(
        transitions["SM_mu_to_mu"] + transitions["FC_NP_mu_to_e"], dsigma["SM+NP"])
    checks["total_mu_to_e_matches_FC_max_relative_error"] = pointwise_error(transitions["total_mu_to_e"], transitions["FC_NP_mu_to_e"])
    checks["total_mu_to_mu_matches_SM_max_relative_error"] = pointwise_error(transitions["total_mu_to_mu"], transitions["SM_mu_to_mu"])
    checks["total_mu_to_tau_max_abs_cm2_per_keV"] = float(np.max(np.abs(transitions["total_mu_to_tau"])))
    checks["pure_mu_interference_max_relative"] = float(np.max(np.abs(dsigma["INT"]) / np.maximum(
        np.abs(dsigma["SM+NP"]), np.abs(dsigma["SM"]) + np.abs(dsigma["NP"]))))
    checks["pure_mu_interference_max_abs_cm2_per_keV"] = float(np.max(np.abs(dsigma["INT"])))
    for key, value in checks.items():
        if key.endswith("error") or key.endswith("relative"):
            assert value < 1e-12, (key, value)
    assert checks["total_mu_to_tau_max_abs_cm2_per_keV"] == 0.
    assert all(np.all(np.isfinite(arr)) and np.all(arr > 0) for arr in (dsigma[s] for s in SCENARIOS))
    assert np.max(np.abs(kernel["SM"][:, 0, 1])) == 0
    assert np.max(np.abs(kernel["NP"][:, 0, 1])) == 0
    for rkey in ALL_CHANNELS:
        # Normalize vanishing diagonal interference against the actual response.
        assert np.max(np.abs(particle["INT"][rkey][:, 1, 1])) <= 1e-12 * max(
            float(np.max(np.abs(particle["SM+NP"][rkey]))), 1e-300)
    pn_equals_np = {ch["w"]: bool(np.array_equal(nuclear[ch["w"]][:, 0, 1], nuclear[ch["w"]][:, 1, 0])) for ch in CHANNELS}
    other_maxima = {w: float(np.max(np.abs(pieces["SM+NP"][w]))) for w in ALL_CHANNELS.values()
                    if w not in {ch["w"] for ch in CHANNELS}}
    metadata = {
        "config": asdict(config), "target": "Cs133", "mass_GeV": mass,
        "b_GeV_minus1": float(target.basic["b"]), "elastic_endpoint_keV": float(endpoint),
        "flavor_order": ["e", "mu", "tau"], "nucleon_order": ["p", "n"],
        "Wilson_axes": ["final", "initial"], "kernel_axes": ["incoming_beta", "incoming_beta_prime"],
        "final_kernel_axes": ["recoil", "resolved_final_flavor", "incoming_beta", "incoming_beta_prime"],
        "displayed_channels": CHANNELS, "all_implemented_channels": list(ALL_CHANNELS.values()),
        "pn_equals_np": pn_equals_np, "other_channel_max_abs_GeV_minus2": other_maxima,
        "R_and_K_units": "GeV^-2", "W_units": "dimensionless stored-table convention",
        "cross_section_units": "cm^2/keV", "no_extra_normalization_or_momentum_factors": True,
        "final_flavor_resolution": "P_alpha c_i applied before particle-response bilinears; all final projectors sum to identity",
        "cross_section_by_response_scenario": "SM+NP, pure incoming nu_mu",
        "checks": checks, "versions": {"numpy": np.__version__, "matplotlib": matplotlib.__version__},
        "response_json_sha256": hashlib.sha256(response_path.read_bytes()).hexdigest(),
    }
    source_files = ["foundation/constants.py", "foundation/units.py", "nuclear/response.py", "rates/differential.py",
                    "theory/kinematics.py", "theory/li2026/amplitude.py", "theory/li2026/responses.py",
                    "theory/li2026/left_to_ci.py", "theory/li2026/lec.py", "theory/li2026/operators.py", "theory/li2026/flavor.py"]
    metadata["source_sha256"] = {p: hashlib.sha256((root / "src/cevns_pyeft" / p).read_bytes()).hexdigest() for p in source_files}
    return dict(config=config, recoil=recoil, y=y, qabs=qabs, coefficient=coefficient,
                W=nuclear, R=particle, pieces=pieces, K=kernel, final_K=final_kernel,
                dsigma=dsigma, response_dsigma=by_response, transitions=transitions,
                metadata=metadata, checks=checks)


def finish_axes(axes, data):
    for ax in np.asarray(axes).flat:
        ax.set_xlim(0, data["config"].recoil_max_kev)
        ax.set_xticks([0, 4, 8, 12])
        ax.set_xlabel(r"Nuclear recoil energy $T_{\rm nr}$ [keV]")
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(which="both", direction="in", top=True, right=True)
        ax.grid(axis="y", which="major", color="#dddddd", lw=0.5, alpha=0.6)
        ax.set_axisbelow(True)


def header(fig, title, data):
    cfg = data["config"]
    fig.suptitle(title, x=0.54, y=0.985, fontsize=12)
    fig.text(0.54, 0.936, rf"$^{{133}}\mathrm{{Cs}}$, $E_\nu={cfg.energy_mev:g}\,\mathrm{{MeV}}$; $(p,n)$ basis", ha="center", fontsize=9)
    if cfg.coefficient_gev_minus2 == 0:
        coefficient = "0"
    else:
        mantissa, exponent = f"{cfg.coefficient_gev_minus2:.3e}".split("e")
        mantissa = float(mantissa)
        coefficient = ("" if mantissa == 1 else "-" if mantissa == -1
                       else f"{mantissa:g}" + r"\times") + rf"10^{{{int(exponent)}}}"
    fig.text(0.54, 0.899,
             r"$\hat{\mathcal{C}}^{6u}_{1,e\mu}=\hat{\mathcal{C}}^{6u*}_{1,\mu e}="
             + coefficient + r"\,\mathrm{GeV}^{-2}$", ha="center", fontsize=10)


def channel_lines(ax, x, arrays, key="w"):
    return [ax.plot(x, arrays[ch[key]], color=ch["color"], ls=ch["ls"], label=ch["label"])[0] for ch in CHANNELS]


def scenario_line(ax, x, y, scenario, label):
    return ax.plot(x, y, **SCENARIO_STYLES[scenario], label=label,
                   marker="o" if scenario == "SM+NP" else None, markevery=27,
                   markersize=3.2, markerfacecolor="white", markeredgewidth=0.8)[0]


def plot_particle(data):
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(2, 2, figsize=(7.8, 6.1))
        fig.subplots_adjust(left=.105, right=.98, bottom=.16, top=.755, wspace=.32, hspace=.52)
        header(fig, "Particle responses with flavor-changing vector interactions", data)
        handles = []
        for col, (a, b) in enumerate(((1, 1), (0, 1))):
            ax = axes[0, col]
            curves = {ch["r"]: data["R"]["SM+NP"][ch["r"]][:, a, b, 0, 0].real for ch in CHANNELS}
            handles = channel_lines(ax, data["recoil"], curves, key="r")
            ax.set_title((r"(a) $R^{pp}_{\mu\mu}$" if col == 0 else r"(b) $\mathrm{Re}\,R^{pp}_{e\mu}$"), loc="left", y=1.13, pad=4)
            ax.set_ylabel(r"Particle response [GeV$^{-2}$]")
            ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
            ax.margins(y=.13)
            ax.text(.96, .92, "SM + NP", transform=ax.transAxes, ha="right", fontsize=8)
        scenario_handles = []
        for col, (a, b) in enumerate(((1, 1), (0, 1))):
            ax = axes[1, col]
            for s in (*SCENARIOS[:2], "INT", "SM+NP"):
                if col == 0 and s == "INT":
                    continue
                line = scenario_line(ax, data["recoil"], data["R"][s]["MM"][:, a, b, 0, 0].real,
                                     s, {"INT": "SM–NP interference", "SM+NP": "SM + NP"}.get(s, s))
                if col == 1:
                    scenario_handles.append(line)
            ax.set_title((r"(c) $R^{pp}_{MM,\mu\mu}$ decomposition" if col == 0
                          else r"(d) $\mathrm{Re}\,R^{pp}_{MM,e\mu}$ decomposition"), loc="left", y=1.13, pad=4)
            ax.set_ylabel(r"Particle response [GeV$^{-2}$]")
            if col == 0:
                ax.set_yscale("log"); ax.set_ylim(8e-18, 4e-12)
                ax.text(.04, .48, "Interference = 0", transform=ax.transAxes, color=SCENARIO_STYLES["INT"]["color"], fontsize=8.5)
            else:
                ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
                ax.margins(y=.15)
                ax.text(.96, .91, r"SM $=$ NP $=0$", transform=ax.transAxes, ha="right", fontsize=8)
        finish_axes(axes, data)
        for ax in axes[0]:
            ax.set_xlabel("")
        fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.54, .87), ncol=3, frameon=False, handlelength=3.2, columnspacing=2.5)
        fig.legend(handles=scenario_handles, loc="lower center", bbox_to_anchor=(.54, .015), ncol=4, frameon=False, handlelength=3.1, columnspacing=1.4, fontsize=8.5)
        return fig


def plot_nuclear(data):
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 3, figsize=(8.6, 3.7))
        fig.subplots_adjust(left=.075, right=.985, bottom=.22, top=.73, wspace=.43)
        fig.suptitle(r"Nuclear response functions of $^{133}\mathrm{Cs}$", x=.53, y=.985, fontsize=12)
        fig.text(.53, .905, "Channel colors match the particle-response and kernel figures", ha="center", fontsize=9)
        pairs = [(0, 0, r"$pp$", "-", 1.8), (0, 1, r"$pn$", "--", 1.8), (1, 1, r"$nn$", ":", 2.3)]
        if not all(data["metadata"]["pn_equals_np"].values()):
            pairs.append((1, 0, r"$np$", "-.", 1.8))
        titles = (r"(a) $W_{MM}$", r"(b) $W_{\Sigma'\Sigma'}$", r"(c) $W_{\Delta\Delta}$")
        for ax, ch, title in zip(axes, CHANNELS, titles):
            for n1, n2, label, ls, lw in pairs:
                if (n1, n2) == (1, 0) and data["metadata"]["pn_equals_np"][ch["w"]]:
                    continue
                ax.plot(data["recoil"], data["W"][ch["w"]][:, n1, n2], color=ch["color"], ls=ls, lw=lw, label=label)
            ax.set_title(title, loc="left", y=1.10, pad=4, color=ch["color"])
            ax.set_ylabel(r"$W_X^{NN'}$ [dimensionless]")
            if ch["w"] == "M":
                ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
                ax.set_ylim(0, 7000)
            elif ch["w"] == "SigmaP":
                ax.set_yscale("symlog", linthresh=1e-6, linscale=.6)
                ax.set_ylim(-4e-3, 1.5); ax.set_yticks([-1e-3, -1e-5, 0, 1e-5, 1e-3, 1e-1])
                ax.axhline(0, color="#aaaaaa", lw=.6, zorder=0)
                ax.text(.96, .93, "signed log", transform=ax.transAxes, ha="right", fontsize=8)
            else:
                ax.set_yscale("log"); ax.set_ylim(4e-3, 5.)
                ax.text(.96, .93, "log scale", transform=ax.transAxes, ha="right", fontsize=8)
        finish_axes(axes, data)
        for ax in axes:
            ax.set_xlabel(r"$T_{\rm nr}$ [keV]")
        fig.legend(handles=[Line2D([0], [0], color="#333333", ls=ls, lw=lw, label=label) for _, _, label, ls, lw in pairs],
                   loc="lower center", bbox_to_anchor=(.53, .015), ncol=len(pairs), frameon=False, handlelength=3.3, columnspacing=2.6)
        return fig


def plot_kernel(data):
    """Four panels: K diagonal, K off-diagonal, response xs, resolved final xs."""
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(2, 2, figsize=(7.8, 6.3))
        fig.subplots_adjust(left=.105, right=.98, bottom=.19, top=.755, wspace=.34, hspace=.53)
        header(fig, "Response channels, flavor kernels and differential cross sections", data)
        handles = []
        for col, (a, b) in enumerate(((1, 1), (0, 1))):
            ax = axes[0, col]
            curves = {ch["w"]: data["pieces"]["SM+NP"][ch["w"]][:, a, b].real for ch in CHANNELS}
            handles = channel_lines(ax, data["recoil"], curves)
            ax.set_title((r"(a) $\mathsf{K}_{\mu\mu}^{(X)}$" if col == 0 else r"(b) $\mathrm{Re}\,\mathsf{K}_{e\mu}^{(X)}$"), loc="left", y=1.12, pad=4)
            ax.set_ylabel(r"Kernel [GeV$^{-2}$]")
            ax.text(.96, .92, "SM + NP", transform=ax.transAxes, ha="right", fontsize=8)
            if col == 0:
                ax.set_yscale("log"); ax.set_ylim(4e-15, 4e-8)
            else:
                ax.set_yscale("symlog", linthresh=1e-18, linscale=.5)
                ax.set_ylim(-1e-14, 5e-8); ax.set_yticks([-1e-15, 0, 1e-13, 1e-11, 1e-9])
                ax.axhline(0, color="#aaaaaa", lw=.6, zorder=0)
                ax.text(.96, .10, "signed log", transform=ax.transAxes, ha="right", fontsize=8)
        ax = axes[1, 0]
        channel_lines(ax, data["recoil"], data["response_dsigma"])
        ax.set_title(r"(c) Cross section by response", loc="left", y=1.12, pad=4)
        ax.set_yscale("log")
        ax.set_ylabel(r"$d\sigma^{(X)}/dT_{\rm nr}$ [cm$^2$/keV]")
        ax.text(.96, .90, r"SM + NP; incident $\nu_\mu$", transform=ax.transAxes, ha="right", fontsize=8)
        ax.margins(y=.16)
        ax = axes[1, 1]
        final_handles = [
            scenario_line(ax, data["recoil"], data["transitions"]["SM_mu_to_mu"], "SM", r"SM: $\nu_\mu\to\nu_\mu$"),
            scenario_line(ax, data["recoil"], data["transitions"]["FC_NP_mu_to_e"], "NP", r"FC NP: $\nu_\mu\to\nu_e$"),
            scenario_line(ax, data["recoil"], data["dsigma"]["SM+NP"], "SM+NP", r"Total: SM + FC NP"),
        ]
        ax.set_title(r"(d) Flavor-changing cross section", loc="left", y=1.12, pad=4)
        ax.set_yscale("log"); ax.margins(y=.18)
        ax.set_ylabel(r"$d\sigma/dT_{\rm nr}$ [cm$^2$/keV]")
        ax.text(.96, .10, "all implemented channels", transform=ax.transAxes, ha="right", fontsize=8)
        finish_axes(axes, data)
        for ax in axes[0]:
            ax.set_xlabel("")
        fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.54, .87), ncol=3, frameon=False, handlelength=3.2, columnspacing=2.5)
        fig.legend(handles=final_handles, loc="lower center", bbox_to_anchor=(.54, .015), ncol=3, frameon=False, handlelength=2.8, columnspacing=1.3, fontsize=8)
        return fig


def save_figure(fig, output_dir, basename):
    output_dir = Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(STYLE):
        for ext in ("pdf", "png"):
            path = output_dir / f"{basename}.{ext}"
            fig.savefig(path, dpi=400, bbox_inches="tight", pad_inches=.07)
            print("Saved:", path)


def export_data(data, output_dir=DEFAULT_OUTPUT):
    output_dir = Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    arrays = {"Tnr_keV": data["recoil"], "y": data["y"], "qabs_GeV": data["qabs"], "C6u1": data["coefficient"]}
    for group in ("R", "W", "pieces", "K", "final_K", "dsigma", "response_dsigma", "transitions"):
        def flatten(value, prefix):
            if isinstance(value, dict):
                for key, item in value.items():
                    flatten(item, prefix + "__" + key.replace("+", "plus"))
            else:
                arrays[prefix] = value
        flatten(data[group], group)
    np.savez_compressed(output_dir / "unified_response_data.npz", **arrays)

    def csv(name, columns):
        np.savetxt(output_dir / (name + ".csv"), np.column_stack(list(columns.values())),
                   delimiter=",", header=",".join(columns), comments="", fmt="%.16e")
    columns = {"Tnr_keV": data["recoil"]}
    for scenario in (*SCENARIOS, "INT"):
        for ch in CHANNELS:
            for label, (a, b) in (("mumu", (1, 1)), ("emu", (0, 1))):
                columns[f"R_{scenario.replace('+','plus')}_{ch['r']}_{label}_pp_GeVm2"] = data["R"][scenario][ch["r"]][:, a, b, 0, 0].real
    csv(FIGURE_NAMES[0], columns)
    columns = {"Tnr_keV": data["recoil"], "y": data["y"]}
    for ch in CHANNELS:
        for n1, n2, label in ((0, 0, "pp"), (0, 1, "pn"), (1, 0, "np"), (1, 1, "nn")):
            columns[f"W_{ch['w']}_{label}"] = data["W"][ch["w"]][:, n1, n2]
    csv(FIGURE_NAMES[1], columns)
    columns = {"Tnr_keV": data["recoil"]}
    for ch in CHANNELS:
        for label, (a, b) in (("mumu", (1, 1)), ("emu", (0, 1))):
            columns[f"K_{ch['w']}_{label}_GeVm2"] = data["pieces"]["SM+NP"][ch["w"]][:, a, b].real
        columns[f"dsigma_response_{ch['w']}_cm2_per_keV"] = data["response_dsigma"][ch["w"]]
    for key, value in data["transitions"].items():
        columns[f"dsigma_{key}_cm2_per_keV"] = value
    for key, value in data["dsigma"].items():
        columns[f"dsigma_{key.replace('+','plus')}_cm2_per_keV"] = value
    csv(FIGURE_NAMES[2], columns)
    captions = [
        "Particle responses in the pp nucleon entry for the common Cs133, 30 MeV, flavor-changing vector benchmark. "
        "Panels (a,b) compare M, Sigma-prime and Delta in the mu-mu and real e-mu entries of SM+NP. "
        "Panels (c,d) decompose R_MM into SM, FC NP, interference and total contributions. Panel (c) uses a log scale, "
        "with its vanishing interference indicated separately. Off-diagonal R describes incoming-flavor coherence and is not an exclusive transition cross section.",
        "Nuclear responses of Cs133 in the stored (p,n) basis. Panels (a-c) show M, Sigma-prime and Delta in the same "
        "channel colors as the R and K figures. Line styles distinguish pp, pn, nn, and np if independent. "
        "The Sigma-prime panel uses a symmetric-log scale (threshold 10^-6); the Delta panel uses a log scale. "
        "W has no neutrino-flavor or SM/NP indices. All nucleon pairs enter the full contractions.",
        "Kernel and cross-section correspondence for the common Cs133, 30 MeV benchmark with "
        "C_1,e-mu^(6u)=C_1,mu-e^(6u)*=10^-5 GeV^-2. Panels (a,b) show the diagonal mu-mu and real off-diagonal "
        "e-mu channel kernels; panel (b) uses a signed symmetric-log scale with threshold 10^-18 GeV^-2. "
        "Panel (c) converts each SM+NP channel kernel to its pure incident nu_mu cross-section contribution. "
        "Panel (d) resolves SM nu_mu->nu_mu and FC NP nu_mu->nu_e, together with the total over all implemented "
        "responses and all final flavors. Final flavors are selected before response bilinears. "
        "The two exclusive contributions add without linear interference for this benchmark.",
    ]
    cfg = data["config"]
    actual_inputs = (f"Common numerical inputs: E_nu={cfg.energy_mev:g} MeV; "
                     f"C6u1[e,mu]=C6u1[mu,e]*={cfg.coefficient_gev_minus2:g} GeV^-2; "
                     f"sin^2(theta_W)={cfg.sin2theta_w:g}; "
                     f"Tnr={cfg.recoil_min_kev:g}-{cfg.recoil_max_kev:g} keV; "
                     f"{cfg.n_recoil} identical nodes in all figures.")
    for name, caption in zip(FIGURE_NAMES, captions):
        caption = caption.replace("30 MeV", f"{cfg.energy_mev:g} MeV").replace(
            "10^-5 GeV^-2", f"{cfg.coefficient_gev_minus2:g} GeV^-2")
        (output_dir / (name + "_caption.txt")).write_text(caption + "\n\n" + actual_inputs + "\n", encoding="utf-8")
    metadata = dict(data["metadata"])
    metadata["generator_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output_dir / "unified_response_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "validation_summary.json").write_text(json.dumps(data["checks"], indent=2) + "\n", encoding="utf-8")
    readme = """# Unified Cs133 response figures

The generator is `../generate_unified_response_figures.py`. It is also called
from Section 12 of `../4. CEvNS_pyEFT_COHERENT_CsI2021_paper_figures - v2.ipynb`.
Run from Gitup01 with the project's Python environment:

```powershell
python -X utf8 -B "论文图NoteBook/generate_unified_response_figures.py"
```

Figure 1 has four R panels; Figure 2 has three W panels; Figure 3 has four
panels for K_mumu, Re K_emu, response-resolved cross sections and the resolved
SM mu->mu / FC NP mu->e / inclusive total. Blue, orange and green consistently
mean M, Sigma-prime and Delta. In Figure 2, line styles label nucleon pairs.

Final flavor is projected on the NR coefficient rows before bilinears. Three
recoil points also check this against projecting the LEFT rows before the
complete engine. The full final-flavor sum, all response channels, full nucleon
contractions and cross-section units are checked numerically. The cross-section
total always uses all implemented channels. No flux or detector folding enters.
W uses the current stored-table normalization without extra prefactors.

`unified_response_data.npz` contains complete complex R, W, channel K, total K,
final-flavor-resolved K, cross sections and transition arrays. The final_K axes
are (recoil, resolved final flavor, incoming beta, incoming beta-prime).
Separate CSV files contain plotted curves. Captions, source hashes, common
configuration and numeric checks accompany the figures. Old figure directories
and old notebook cells are retained.
"""
    (output_dir / "README.md").write_text(readme + "\n" + actual_inputs + "\n", encoding="utf-8")
    return output_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--n-recoil", type=int, default=160)
    parser.add_argument("--coefficient", type=float, default=1e-5)
    args = parser.parse_args()
    config = FigureConfig(n_recoil=args.n_recoil, coefficient_gev_minus2=args.coefficient)
    data = calculate(config)
    for plot, name in zip((plot_particle, plot_nuclear, plot_kernel), FIGURE_NAMES):
        fig = plot(data)
        save_figure(fig, args.output_dir, name)
        plt.close(fig)
    export_data(data, args.output_dir)
    print(json.dumps(data["checks"], indent=2))


if __name__ == "__main__":
    main()
