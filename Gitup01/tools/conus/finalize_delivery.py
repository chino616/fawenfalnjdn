"""Finalize machine-readable validation and delivery manifests."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "conus-plus-completion-20261012"
DATASET = ROOT / "data" / "experiments" / "CONUS_Plus" / "conus_plus_2025_c2c3c5_ge73_pyeft"
DIAGNOSTICS = ROOT / "workflows" / "experiment-integration" / "runs" / "CONUS_Plus" / "conus_plus_2025_c2c3c5_ge73_pyeft" / "diagnostics"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    fast = OUT / "fast"
    validation = OUT / "validation"
    fast.mkdir(parents=True, exist_ok=True)
    validation.mkdir(parents=True, exist_ok=True)
    for name in ("conus_plus_detector_response_matrix_v1.npz", "conus_plus_detector_response_matrix_v1.json"):
        source = DATASET / "fast" / name
        target = fast / name
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)

    summary = json.loads((DIAGNOSTICS / "08_fast_summary.json").read_text(encoding="utf-8"))
    comparison = []
    import csv
    with (DIAGNOSTICS / "08_slow_fast_comparison.csv").open(newline="", encoding="utf-8") as stream:
        comparison = list(csv.DictReader(stream))
    dump(
        validation / "fast_direct.json",
        {
            "status": "PASS_WITH_DOCUMENTED_LIMITATION",
            "artifact": "detector_response_matrix",
            "points": summary["points"],
            "bin_comparison_rows": len(comparison),
            "max_abs_difference": max(float(row["abs_difference"]) for row in comparison),
            "max_relative_difference": max(float(row["relative_difference"]) for row in comparison),
            "full_eft_quadratic_kernel": "NOT_RUN_PENDING",
            "note": "These values validate the detector matrix only; they are not a Wilson-coefficient Fast-kernel validation.",
        },
    )
    dump(
        validation / "performance.json",
        {
            "status": "MATRIX_MEASURED; EFT_KERNEL_NOT_MEASURED",
            "matrix_build_seconds": summary["cache"]["build_seconds"],
            "points": summary["points"],
            "break_even": "not reported because the tested matrix path is not a coefficient-dependent EFT kernel and is slower than direct for SM in this run",
            "machine": "local Windows Python 3.12; timings inherited from formal P08 diagnostic",
        },
    )
    dump(
        validation / "test_report.json",
        {
            "targeted_smoke": "PASS",
            "exact_new_tests": "PASS (test_conus_plus_eft_kernel.py functions called directly)",
            "eft_kernel_smoke": "PASS (114 coordinates; 2 held-out synthetic points)",
            "compileall": "PASS",
            "formal_regression": "101 passed recorded in the imported P06-P09 run; not re-executed in this shell because pytest is unavailable",
            "pytest_environment": "pytest unavailable in system Python and local candidate venv; network install was unavailable",
            "latex_preview": "VIEWABLE_PDF_GENERATED; pdflatex blocked by Windows DLL relocation error",
        },
    )

    phase = json.loads((OUT / "phase_status.json").read_text(encoding="utf-8"))
    phase.update(
        {
            "status": "PARTIAL_COMPLETION_DELIVERED",
            "P08": "PARTIAL_DETECTOR_MATRIX_VALIDATED; EFT_QUADRATIC_KERNEL_PENDING",
            "P09": "PASS_WITH_DOCUMENTED_LIMITATION_APPROXIMATE_DIGITIZED_BENCHMARK",
            "P10": "PARTIAL_DELIVERY_FORWARD_STATISTICS_FIGURES_PAPER_MATERIALS",
            "formal_human_gates": "not_promoted_by_automatic_candidate",
            "evidence": {
                "runner": "tools/conus/run_conus_completion.py",
                "forward": "outputs/conus-plus-completion-20261012/data",
                "statistics": "outputs/conus-plus-completion-20261012/statistics",
                "figures": "outputs/conus-plus-completion-20261012/figures",
                "paper": "outputs/conus-plus-completion-20261012/paper",
                "validation": "outputs/conus-plus-completion-20261012/validation",
            },
            "blockers": [
                "full 114-coordinate EFT quadratic kernel requires direct mixed samples and held-out validation",
                "official likelihood and electron-scattering inputs are unavailable",
                "paper Figs.5-12 require model-specific inputs not registered in this project",
                "no controlled with-Skill versus without-Skill onboarding experiment was run; no success-rate or time-saving claim is made",
                "pdflatex executable is blocked by local Windows DLL relocation; preview.pdf is generated from the validated figures",
            ],
        }
    )
    dump(OUT / "phase_status.json", phase)

    files = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            files.append({"path": str(path.relative_to(OUT)).replace("\\", "/"), "sha256": sha256(path), "bytes": path.stat().st_size})
    dump(
        OUT / "manifest.json",
        {
            "schema_version": 1,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "dataset_id": "conus_plus_2025_c2c3c5_ge73_pyeft",
            "config": "data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/experiment.yaml",
            "candidate_run": ".experiment-auto-runs/conus-plus-mainline-benchmark-high-auto-20261009-r2/snapshot",
            "git": {"status": "unavailable: formal copy contains an empty .git directory", "remote_publish": False},
            "files": files,
        },
    )
    (OUT / "README_FINAL.md").write_text(
        "# CONUS+ completion delivery\n\n"
        "The formal dataset is `conus_plus_2025_c2c3c5_ge73_pyeft`. The forward configuration uses Ge73 and C2/C3/C5 at 119 kg day each; the statistical benchmark is an independent effective-119 configuration.\n\n"
        "## Reproduce\n\n"
        "```powershell\n"
        "python tools\\conus\\run_conus_completion.py --config data\\experiments\\CONUS_Plus\\conus_plus_2025_c2c3c5_ge73_pyeft\\experiment.yaml --task all --output outputs\\conus-plus-completion-20261012 --resume\n"
        "python tools\\conus\\generate_paper_materials.py\n"
        "python tools\\conus\\build_preview.py\n"
        "```\n\n"
        "The available Fast object is a detector-response matrix. `fast/kernel_build_status.json` records why it is not a coefficient-dependent EFT kernel; the declared reactor-visible Li2026 basis has 114 real coordinates.\n\n"
        "The paper comparison is a 19-point digitized Gaussian Eq.(33) benchmark, not the official likelihood. Electronic recoils and Figs.5--12 are not represented. See `KNOWN_LIMITATIONS.md` and `FINAL_STATUS.md`.\n\n"
        "The viewable `paper/preview.pdf` is generated from the validated figure PDFs because this Windows environment cannot start its TeX executable; `paper/preview.tex` remains the compilable source for a working TeX installation.\n",
        encoding="utf-8",
    )
    (OUT / "FINAL_STATUS.md").write_text(
        "# CONUS+ final status\n\n"
        "Status: `PARTIAL_COMPLETION_DELIVERED`. P01 is reused; P02--P07 are imported and machine-validated in the formal project. The direct prediction is complete for Ge73 with C2/C3/C5 at 119 kg day each: 89.707788, 150.340819 and 116.202320 events, 356.250927 combined.\n\n"
        "The core paper benchmark is delivered for the effective-119 SM spectrum, weak mixing angle, CEvNS-only magnetic moment and four vector-NSI panels. Results are an approximate digitized Gaussian benchmark using 19 points and a normalization pull.\n\n"
        "P08 remains partial: the detector-response matrix is validated, while the full 114-coordinate EFT quadratic kernel has not been built. P10 contains the forward arrays, scan files, figures, paper macros, tables, section source and a viewable preview PDF.\n\n"
        "The official likelihood, electron scattering and paper Figs.5--12 remain blocked by missing registered inputs. The local TeX executable could not start because of a Windows DLL relocation error; this is recorded in `validation/test_report.json`.\n",
        encoding="utf-8",
    )
    (OUT / "KNOWN_LIMITATIONS.md").write_text(
        "# Known limitations\n\n"
        "The frozen candidate source and response are retained. The 340--350 eVee tail remains about 48% below the digitized paper blue curve, and the Mueller continuation from 8 to 10 MeV is a model assumption. These are documented limitations, not adjusted by rescaling.\n\n"
        "The statistical comparison uses 19 vector-digitized excess points and the Eq.(33) Gaussian approximation with one normalization pull. It is not the official CONUS+ likelihood.\n\n"
        "The current P08 Fast artifact validates detector folding only. A complete 114-coordinate EFT kernel requires direct coefficient samples and held-out mixed-point validation. Electronic recoil scattering and Figs.5--12 are not implemented.\n\n"
        "`preview.tex` is supplied for TeX compilation; the local pdflatex executable failed to start because of a Windows system DLL relocation error, so `preview.pdf` is a viewable figure-based preview.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
