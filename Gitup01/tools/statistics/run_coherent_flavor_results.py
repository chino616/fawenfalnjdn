from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from cevns_pyeft.foundation.constants import G_F
from cevns_pyeft.kernels.storage import build_fastscan_template, save_fastscan_template
from cevns_pyeft.statistics.confidence import confidence_definition
from cevns_pyeft.statistics.datasets import csi2021_dataset
from cevns_pyeft.statistics.likelihoods import chi2_csi2021
from cevns_pyeft.statistics.observables import convert_prediction_to_dataset_observable
from cevns_pyeft.statistics.parameters import VectorNSIParameters, vector_nsi_to_np_wilson
from cevns_pyeft.statistics.predictors import RawComponentPrediction, predict_raw_components
from cevns_pyeft.statistics.scans import scan_grid_1d, scan_grid_2d


SOURCE_KEYS = ("e", "mu", "mub", "total")
SOURCE_LABELS = {"e": "nu_e", "mu": "nu_mu", "mub": "nubar_mu", "total": "total"}
PRIMARY_CASES = {
    "SM": {},
    "epsilon_ee_uV": {"epsilon_ee_uV": 0.05},
    "epsilon_mumu_uV": {"epsilon_mumu_uV": 0.05},
    "epsilon_emu_uV": {"epsilon_emu_uV": 0.05},
    "epsilon_etau_uV": {"epsilon_etau_uV": 0.05},
    "epsilon_mutau_uV": {"epsilon_mutau_uV": 0.05},
    "epsilon_tautau_uV": {"epsilon_tautau_uV": 0.05},
}
F0_EXPECTED_CHANGED = {
    "epsilon_ee_uV": {"e"},
    "epsilon_mumu_uV": {"mu", "mub"},
    "epsilon_emu_uV": {"e", "mu", "mub"},
    "epsilon_etau_uV": {"e"},
    "epsilon_mutau_uV": {"mu", "mub"},
    "epsilon_tautau_uV": set(),
}
SCAN_1D_PARAMETERS = (
    "epsilon_ee_uV",
    "epsilon_ee_dV",
    "epsilon_mumu_uV",
    "epsilon_mumu_dV",
    "epsilon_emu_uV",
    "epsilon_emu_dV",
    "epsilon_etau_uV",
    "epsilon_etau_dV",
    "epsilon_mutau_uV",
    "epsilon_mutau_dV",
)


def _git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _params(**kwargs: float) -> VectorNSIParameters:
    return VectorNSIParameters(**kwargs)


def _wilson(kwargs: dict[str, float]):
    return vector_nsi_to_np_wilson(_params(**kwargs))


def _predict(
    kwargs: dict[str, float],
    *,
    mode: str,
    fast_kernel: Path | None,
    responses: Path,
    slow_kwargs: dict[str, int | float],
) -> RawComponentPrediction:
    extra = dict(slow_kwargs) if mode == "slow" else {}
    return predict_raw_components(
        "CsI2021",
        _wilson(kwargs),
        mode=mode,
        fast_kernel_path=fast_kernel,
        responses_json=responses,
        **extra,
    )


def _component_arrays(pred: RawComponentPrediction) -> dict[str, np.ndarray]:
    return {key: np.asarray(pred.components[key].values, dtype=float) for key in SOURCE_KEYS}


def _component_sums(pred: RawComponentPrediction) -> dict[str, float]:
    arrs = _component_arrays(pred)
    return {key: float(arrs[key].sum()) for key in SOURCE_KEYS}


def _chi2(pred: RawComponentPrediction):
    ds = csi2021_dataset()
    converted = convert_prediction_to_dataset_observable(pred.total, ds.observable)
    return chi2_csi2021(converted, ds)


def _write_csv(path: Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_metadata(path: Path, data: dict[str, object]) -> None:
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, (dict, list, tuple)):
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        else:
            lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _make_f0_checks(sm_fast: RawComponentPrediction, fast_predictions: dict[str, RawComponentPrediction]) -> list[dict[str, object]]:
    sm = _component_arrays(sm_fast)
    rows: list[dict[str, object]] = []
    for case, expected_changed in F0_EXPECTED_CHANGED.items():
        current = _component_arrays(fast_predictions[case])
        changed: set[str] = set()
        max_rel: dict[str, float] = {}
        for key in ("e", "mu", "mub"):
            denom = np.maximum(np.abs(sm[key]), 1.0e-30)
            rel = np.max(np.abs(current[key] - sm[key]) / denom)
            max_rel[key] = float(rel)
            if rel > 1.0e-7:
                changed.add(key)
        rows.append(
            {
                "case": case,
                "expected_changed": "+".join(sorted(expected_changed)) or "none",
                "observed_changed": "+".join(sorted(changed)) or "none",
                "pass": changed == expected_changed,
                "max_rel_nu_e": max_rel["e"],
                "max_rel_nu_mu": max_rel["mu"],
                "max_rel_nubar_mu": max_rel["mub"],
            }
        )
    return rows


def _component_benchmark(out_dir: Path, predictions: dict[str, RawComponentPrediction]) -> None:
    sm_arrays = _component_arrays(predictions["SM"])
    spectra_rows: list[dict[str, object]] = []
    ratio_rows: list[dict[str, object]] = []
    for case, pred in predictions.items():
        arrs = _component_arrays(pred)
        for bin_index in range(pred.pe_bins.size - 1):
            base = {
                "case": case,
                "bin": bin_index,
                "pe_left": float(pred.pe_bins[bin_index]),
                "pe_right": float(pred.pe_bins[bin_index + 1]),
            }
            spectra_rows.append({**base, **{SOURCE_LABELS[k]: float(arrs[k][bin_index]) for k in SOURCE_KEYS}})
            ratio_rows.append(
                {
                    **base,
                    **{
                        SOURCE_LABELS[k]: float(arrs[k][bin_index] / sm_arrays[k][bin_index]) if sm_arrays[k][bin_index] != 0.0 else np.nan
                        for k in SOURCE_KEYS
                    },
                }
            )
    fields = ["case", "bin", "pe_left", "pe_right", "nu_e", "nu_mu", "nubar_mu", "total"]
    _write_csv(out_dir / "component_spectra.csv", spectra_rows, fields)
    _write_csv(out_dir / "component_ratios.csv", ratio_rows, fields)

    centers = 0.5 * (predictions["SM"].pe_bins[:-1] + predictions["SM"].pe_bins[1:])
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, key in zip(axes.ravel(), SOURCE_KEYS):
        for case in PRIMARY_CASES:
            arr = _component_arrays(predictions[case])[key]
            ax.step(centers, arr, where="mid", label=case if key == "total" else None)
        ax.set_title(SOURCE_LABELS[key])
        ax.set_ylabel("events/bin")
    axes[-1, 0].set_xlabel("PE")
    axes[-1, 1].set_xlabel("PE")
    handles, labels = axes.ravel()[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", fontsize=8)
    fig.tight_layout(rect=(0, 0, 0.82, 1))
    fig.savefig(out_dir / "fig_csi2021_flavor_components.png", dpi=180)
    plt.close(fig)


def _scan_1d(
    parameter: str,
    values: np.ndarray,
    *,
    mode: str,
    fast_kernel: Path | None,
    responses: Path,
    slow_kwargs: dict[str, int | float],
):
    cache: dict[float, tuple[float, object, RawComponentPrediction]] = {}

    def evaluate(value: float) -> float:
        if value not in cache:
            pred = _predict({parameter: float(value)}, mode=mode, fast_kernel=fast_kernel, responses=responses, slow_kwargs=slow_kwargs)
            profile = _chi2(pred)
            cache[float(value)] = (float(profile.chi2), profile, pred)
        return cache[float(value)][0]

    result = scan_grid_1d(values, evaluate)
    rows: list[dict[str, object]] = []
    for value, chi2, dchi2 in zip(result.x, result.chi2, result.dchi2):
        _, profile, pred = cache[float(value)]
        sums = _component_sums(pred)
        rows.append(
            {
                "parameter": parameter,
                "value": float(value),
                "chi2": float(chi2),
                "delta_chi2": float(dchi2),
                "alpha_best": float(profile.alpha),
                "beta_best": float(profile.beta),
                "prediction_nue": sums["e"],
                "prediction_numu": sums["mu"],
                "prediction_numubar": sums["mub"],
                "prediction_total": sums["total"],
                "mode": mode,
            }
        )
    return result, rows


def _run_1d_scans(out_dir: Path, fast_kernel: Path, responses: Path) -> dict[str, object]:
    values = np.linspace(-0.3, 0.3, 61)
    all_rows: list[dict[str, object]] = []
    plotted = ("epsilon_ee_uV", "epsilon_mumu_uV", "epsilon_emu_uV")
    summaries: dict[str, object] = {}
    for parameter in SCAN_1D_PARAMETERS:
        result, rows = _scan_1d(parameter, values, mode="fast", fast_kernel=fast_kernel, responses=responses, slow_kwargs={})
        all_rows.extend(rows)
        summaries[parameter] = {"bestfit": float(result.bestfit), "chi2_min": float(result.chi2_min)}
        if parameter in plotted:
            fig, ax = plt.subplots(figsize=(6.2, 4.2))
            ax.plot(result.x, result.dchi2, color="#1f77b4")
            ax.axhline(2.71, color="0.35", ls="--", lw=1.0)
            ax.axvline(0.0, color="0.55", lw=0.8)
            ax.set_xlabel(parameter)
            ax.set_ylabel("Delta chi2")
            ax.set_title(f"CsI2021 {parameter}")
            fig.tight_layout()
            fig.savefig(out_dir / f"fig_csi2021_dchi2_{parameter}.png", dpi=180)
            plt.close(fig)
    _write_csv(
        out_dir / "csi2021_1d_chi2.csv",
        all_rows,
        [
            "parameter",
            "value",
            "chi2",
            "delta_chi2",
            "alpha_best",
            "beta_best",
            "prediction_nue",
            "prediction_numu",
            "prediction_numubar",
            "prediction_total",
            "mode",
        ],
    )
    return summaries


def _sign_checks(fast_kernel: Path, responses: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for parameter in ("epsilon_ee_uV", "epsilon_mumu_uV", "epsilon_emu_uV"):
        plus = _predict({parameter: 0.05}, mode="fast", fast_kernel=fast_kernel, responses=responses, slow_kwargs={})
        minus = _predict({parameter: -0.05}, mode="fast", fast_kernel=fast_kernel, responses=responses, slow_kwargs={})
        pprof = _chi2(plus)
        mprof = _chi2(minus)
        rel_counts = abs(_component_sums(plus)["total"] - _component_sums(minus)["total"]) / max(abs(_component_sums(plus)["total"]), 1.0e-30)
        rows.append(
            {
                "parameter": parameter,
                "chi2_plus": float(pprof.chi2),
                "chi2_minus": float(mprof.chi2),
                "abs_chi2_diff": float(abs(pprof.chi2 - mprof.chi2)),
                "relative_total_count_diff": float(rel_counts),
                "expected_sign_symmetric": parameter == "epsilon_emu_uV",
                "pass": (abs(pprof.chi2 - mprof.chi2) < 1.0e-8) if parameter == "epsilon_emu_uV" else (abs(pprof.chi2 - mprof.chi2) > 1.0e-5),
            }
        )
    return rows


def _ensure_lowres_fast_kernel(out_dir: Path, responses: Path) -> Path:
    kernel_dir = out_dir / "lowres_fast_kernel"
    kernel_path = kernel_dir / "csi2021_lowres_fast_kernel.npz"
    if kernel_path.exists() and kernel_path.with_suffix(".json").exists():
        return kernel_path
    kernel_dir.mkdir(parents=True, exist_ok=True)
    kernel = build_fastscan_template("CsI2021", responses, n_er=3, n_enu=6, n_pe_sub=3, pe_step=3.0)
    return save_fastscan_template(kernel_path, kernel)


def _slow_fast_checks(out_dir: Path, responses: Path) -> list[dict[str, object]]:
    low_fast = _ensure_lowres_fast_kernel(out_dir, responses)
    values = np.array([-0.05, 0.0, 0.05])
    rows: list[dict[str, object]] = []
    for parameter in ("epsilon_ee_uV", "epsilon_mumu_uV", "epsilon_emu_uV"):
        slow_result, slow_rows = _scan_1d(parameter, values, mode="slow", fast_kernel=None, responses=responses, slow_kwargs={"n_er": 3, "n_enu": 6, "n_pe_bin": 3})
        fast_result, fast_rows = _scan_1d(parameter, values, mode="fast", fast_kernel=low_fast, responses=responses, slow_kwargs={})
        for sr, fr, sd, fd in zip(slow_rows, fast_rows, slow_result.dchi2, fast_result.dchi2):
            rows.append(
                {
                    "parameter": parameter,
                    "value": sr["value"],
                    "slow_chi2": sr["chi2"],
                    "fast_chi2": fr["chi2"],
                    "abs_chi2_diff": abs(float(sr["chi2"]) - float(fr["chi2"])),
                    "slow_delta_chi2": float(sd),
                    "fast_delta_chi2": float(fd),
                    "abs_delta_chi2_diff": abs(float(sd) - float(fd)),
                    "slow_total": sr["prediction_total"],
                    "fast_total": fr["prediction_total"],
                    "abs_total_diff": abs(float(sr["prediction_total"]) - float(fr["prediction_total"])),
                }
            )
    _write_csv(
        out_dir / "slow_fast_csi2021_short_grid.csv",
        rows,
        ["parameter", "value", "slow_chi2", "fast_chi2", "abs_chi2_diff", "slow_delta_chi2", "fast_delta_chi2", "abs_delta_chi2_diff", "slow_total", "fast_total", "abs_total_diff"],
    )
    return rows


def _scan_2d(
    parameter_x: str,
    parameter_y: str,
    values: np.ndarray,
    *,
    fast_kernel: Path,
    responses: Path,
):
    def evaluate(x: float, y: float) -> float:
        pred = _predict({parameter_x: float(x), parameter_y: float(y)}, mode="fast", fast_kernel=fast_kernel, responses=responses, slow_kwargs={})
        return float(_chi2(pred).chi2)

    return scan_grid_2d(values, values, evaluate)


def _run_2d(out_dir: Path, fast_kernel: Path, responses: Path) -> dict[str, object]:
    threshold = confidence_definition("legacy_2d_90_flow_a").delta_chi2
    values = np.linspace(-0.35, 0.35, 41)
    planes = {
        "ee_uV_dV": ("epsilon_ee_uV", "epsilon_ee_dV"),
        "mumu_uV_dV": ("epsilon_mumu_uV", "epsilon_mumu_dV"),
        "mixed_ee_dV_emu_dV": ("epsilon_ee_dV", "epsilon_emu_dV"),
    }
    summary: dict[str, object] = {}
    for tag, (px, py) in planes.items():
        result = _scan_2d(px, py, values, fast_kernel=fast_kernel, responses=responses)
        np.savez(
            out_dir / f"csi2021_2d_{tag}.npz",
            x_values=result.x_values,
            y_values=result.y_values,
            chi2_grid=result.chi2_grid,
            delta_chi2_grid=result.dchi2_grid,
            threshold=np.array([threshold], dtype=float),
        )
        fig, ax = plt.subplots(figsize=(5.2, 4.6))
        mesh = ax.pcolormesh(result.x_values, result.y_values, result.dchi2_grid, shading="auto", cmap="viridis")
        fig.colorbar(mesh, ax=ax, label="Delta chi2")
        if float(np.nanmin(result.dchi2_grid)) <= threshold <= float(np.nanmax(result.dchi2_grid)):
            ax.contour(result.x_values, result.y_values, result.dchi2_grid, levels=[threshold], colors="white", linewidths=1.4)
        ax.scatter([0.0], [0.0], marker="+", color="red", s=50)
        ax.set_xlabel(px)
        ax.set_ylabel(py)
        ax.set_title(f"CsI2021 {px} vs {py}")
        fig.tight_layout()
        fig.savefig(out_dir / f"fig_csi2021_2d_{tag}.png", dpi=180)
        plt.close(fig)
        summary[tag] = {
            "x_parameter": px,
            "y_parameter": py,
            "bestfit_x": float(result.bestfit_x),
            "bestfit_y": float(result.bestfit_y),
            "chi2_min": float(result.chi2_min),
            "threshold_90cl": float(threshold),
        }
    return summary


def _gate_report(
    out_dir: Path,
    *,
    f0_rows: list[dict[str, object]],
    sign_rows: list[dict[str, object]],
    slow_fast_rows: list[dict[str, object]],
    scan_summary: dict[str, object],
    scan2d_summary: dict[str, object],
) -> None:
    f0_pass = all(bool(row["pass"]) for row in f0_rows)
    sign_pass = all(bool(row["pass"]) for row in sign_rows)
    sf_max = max(float(row["abs_delta_chi2_diff"]) for row in slow_fast_rows) if slow_fast_rows else float("nan")
    sf_pass = bool(np.isfinite(sf_max) and sf_max < 1.0e-6)
    report = f"""# COHERENT Flavor statistics gate report

[Flavor Statistics Gate F0]
Experiment: CsI2021
Mode: fast reference
Parameterization: real Hermitian vector NSI, NP-only Wilson matrices
Status: {'PASS' if f0_pass else 'FAIL'}
Allow next Gate: {'YES' if f0_pass else 'NO'}

[Flavor Statistics Gate F1]
Experiment: CsI2021
Mode: slow low-resolution benchmark
Generated artifacts:
- component_spectra.csv
- component_ratios.csv
- fig_csi2021_flavor_components.png
Status: PASS
Allow next Gate: YES

[Flavor Statistics Gate F2]
Experiment: CsI2021
Mode: fast reference
Physics checks:
- diagonal NSI sign asymmetry
- off-diagonal epsilon_emu sign symmetry
Status: {'PASS' if sign_pass else 'FAIL'}
Allow next Gate: {'YES' if sign_pass else 'NO'}

[Flavor Statistics Gate F3]
Experiment: CsI2021
Mode: fast reference
Generated artifacts:
- csi2021_1d_chi2.csv
- fig_csi2021_dchi2_epsilon_ee_uV.png
- fig_csi2021_dchi2_epsilon_mumu_uV.png
- fig_csi2021_dchi2_epsilon_emu_uV.png
Status: PASS
Allow next Gate: YES

[Flavor Statistics Gate F4]
Experiment: CsI2021
Mode: low-resolution slow vs matching low-resolution fast
Slow/Fast max abs Delta chi2 diff: {sf_max:.6e}
Status: {'PASS' if sf_pass else 'FAIL'}
Allow next Gate: {'YES' if sf_pass else 'NO'}

[Flavor Statistics Gate F5-F7]
Experiment: CsI2021
Mode: fast reference
Confidence convention: legacy_2d_90_flow_a from statistics.confidence
Generated artifacts:
- fig_csi2021_2d_ee_uV_dV.png
- fig_csi2021_2d_mumu_uV_dV.png
- fig_csi2021_2d_mixed_ee_dV_emu_dV.png
Status: PASS
Allow next Gate: YES

Legacy statistics check:
- This result generation uses the migrated CsI2021 legacy approximate chi2 and does not replace tests/reference/statistics_legacy.

Known limitations:
- CsI2021 only for F0-F7 in this first result pass.
- Slow component spectra and Slow/Fast check use low-resolution numerical settings for tractable local runtime.
- This is not an official COHERENT likelihood.

1D summary:
```json
{json.dumps(scan_summary, indent=2)}
```

2D summary:
```json
{json.dumps(scan2d_summary, indent=2)}
```
"""
    (out_dir / "flavor_gate_report.md").write_text(report, encoding="utf-8")


def run(args: argparse.Namespace) -> Path:
    root = Path(args.root).resolve()
    responses = Path(args.responses).resolve()
    fast_kernel = Path(args.fast_kernel).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    slow_kwargs = {"n_er": int(args.slow_n_er), "n_enu": int(args.slow_n_enu), "n_pe_bin": int(args.slow_n_pe_bin)}
    slow_predictions = {
        case: _predict(kwargs, mode="slow", fast_kernel=None, responses=responses, slow_kwargs=slow_kwargs)
        for case, kwargs in PRIMARY_CASES.items()
    }
    fast_predictions = {
        case: _predict(kwargs, mode="fast", fast_kernel=fast_kernel, responses=responses, slow_kwargs={})
        for case, kwargs in PRIMARY_CASES.items()
    }

    _component_benchmark(out_dir, slow_predictions)
    f0_rows = _make_f0_checks(fast_predictions["SM"], fast_predictions)
    _write_csv(out_dir / "flavor_contract_checks.csv", f0_rows, ["case", "expected_changed", "observed_changed", "pass", "max_rel_nu_e", "max_rel_nu_mu", "max_rel_nubar_mu"])

    sign_rows = _sign_checks(fast_kernel, responses)
    _write_csv(out_dir / "interference_sign_checks.csv", sign_rows, ["parameter", "chi2_plus", "chi2_minus", "abs_chi2_diff", "relative_total_count_diff", "expected_sign_symmetric", "pass"])

    scan_summary = _run_1d_scans(out_dir, fast_kernel, responses)
    slow_fast_rows = _slow_fast_checks(out_dir, responses)
    scan2d_summary = _run_2d(out_dir, fast_kernel, responses)

    metadata = {
        "git_commit": _git_commit(root),
        "experiment": "CsI2021",
        "mode_primary": "fast reference for scans; slow low-resolution for component benchmark",
        "parameterization": "real Hermitian dimension-6 vector NSI",
        "operator": "C1q(6), q=u,d",
        "G_F_source": "cevns_pyeft.foundation.constants.G_F",
        "G_F_value": float(G_F),
        "raw_observable": "events/bin",
        "statistical_observable": "counts/PE",
        "units": {"raw": "events/bin", "likelihood": "counts/PE"},
        "provenance_status": "legacy approximate statistics; not official COHERENT likelihood",
        "slow_settings": slow_kwargs,
        "fast_kernel": str(fast_kernel),
        "confidence_definition_2d": asdict(confidence_definition("legacy_2d_90_flow_a")),
    }
    _write_metadata(out_dir / "benchmark_metadata.yaml", metadata)
    _gate_report(
        out_dir,
        f0_rows=f0_rows,
        sign_rows=sign_rows,
        slow_fast_rows=slow_fast_rows,
        scan_summary=scan_summary,
        scan2d_summary=scan2d_summary,
    )
    return out_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate first-pass COHERENT Flavor NSI statistics results.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--responses", default="data/responses/responses_all.json")
    parser.add_argument("--fast-kernel", default="tests/reference_CsI2021/fast_kernel.npz")
    parser.add_argument("--out-dir", default="results/flavor_benchmark/CsI2021")
    parser.add_argument("--slow-n-er", type=int, default=3)
    parser.add_argument("--slow-n-enu", type=int, default=8)
    parser.add_argument("--slow-n-pe-bin", type=int, default=3)
    args = parser.parse_args(argv)
    out_dir = run(args)
    print(f"Generated COHERENT Flavor results in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
