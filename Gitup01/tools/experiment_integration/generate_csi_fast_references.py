#!/usr/bin/env python3
"""Generate CsI Flavor Fast references only after explicit approval.

The default mode is intentionally non-writing.  P4 needs authoritative saved
Fast kernels, but stale scalar Fast split files must not be promoted or updated
as a side effect of diagnostics.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Literal, Sequence

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

RESPONSES_JSON = REPO_ROOT / "data" / "responses" / "responses_all.json"
APPROVAL_PHRASE = "I approve updating CsI Fast reference kernels"
FAST_SLOW_RTOL = 1.0e-9
FAST_SLOW_ATOL = 2.0e-8
Dataset = Literal["CsI2017", "CsI2021"]
DATASETS: tuple[Dataset, ...] = ("CsI2017", "CsI2021")
REFERENCE_PATHS: dict[Dataset, Path] = {
    "CsI2017": REPO_ROOT / "tests" / "reference_CsI2017" / "fast_kernel.npz",
    "CsI2021": REPO_ROOT / "tests" / "reference_CsI2021" / "fast_kernel.npz",
}
SLOW_REFERENCE_PATHS: dict[Dataset, Path] = {
    "CsI2017": REPO_ROOT / "tests" / "reference_CsI2017" / "slow_reference.npy",
    "CsI2021": REPO_ROOT / "tests" / "reference_CsI2021" / "slow_reference.npy",
}


def _selected_datasets(raw: str) -> tuple[Dataset, ...]:
    if raw == "all":
        return DATASETS
    if raw not in DATASETS:
        raise ValueError(f"Unknown CsI dataset {raw!r}")
    return (raw,)  # type: ignore[return-value]


def fast_slow_alignment_metadata(
    predicted: np.ndarray,
    slow_reference: np.ndarray,
    *,
    rtol: float = FAST_SLOW_RTOL,
    atol: float = FAST_SLOW_ATOL,
) -> dict[str, Any]:
    """Return strict Fast-vs-Slow alignment diagnostics for bin counts."""

    fast = np.asarray(predicted, dtype=np.float64)
    slow = np.asarray(slow_reference, dtype=np.float64)
    if fast.shape != slow.shape:
        raise ValueError(f"Fast/Slow reference shape mismatch: {fast.shape} != {slow.shape}")
    delta = fast - slow
    abs_delta = np.abs(delta)
    tolerance = float(atol) + float(rtol) * np.abs(slow)
    if np.any(tolerance <= 0.0):
        raise ValueError("Fast/Slow tolerance must be positive")
    worst_bin = int(np.argmax(abs_delta / tolerance)) if abs_delta.size else 0
    passed = bool(np.allclose(fast, slow, rtol=float(rtol), atol=float(atol)))
    return {
        "fast_slow_rtol": float(rtol),
        "fast_slow_atol": float(atol),
        "fast_slow_allclose": passed,
        "slow_total_events": float(slow.sum()),
        "fast_total_events": float(fast.sum()),
        "total_delta_vs_slow_reference": float(delta.sum()),
        "max_abs_bin_delta_vs_slow_reference": float(abs_delta.max(initial=0.0)),
        "worst_bin_index": worst_bin,
        "worst_bin_abs_delta": float(abs_delta[worst_bin]) if abs_delta.size else 0.0,
        "worst_bin_tolerance": float(tolerance[worst_bin]) if tolerance.size else float(atol),
        "worst_bin_tolerance_ratio": float(abs_delta[worst_bin] / tolerance[worst_bin]) if abs_delta.size else 0.0,
    }


def compute_fast_reference(dataset: Dataset) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a Flavor Fast kernel payload and reconstruction metadata."""

    from cevns_pyeft.kernels.storage import build_fastscan_template, summarize_prediction
    from cevns_pyeft.kernels.basis import coeff_tensor_from_triplets, li2026_left_basis_current
    from cevns_pyeft.kernels.reconstruction import reconstruct_counts_from_kernel

    basis = li2026_left_basis_current()

    if dataset == "CsI2017":
        kernel = build_fastscan_template(
            dataset,
            RESPONSES_JSON,
            basis=basis,
            n_enu=120,
            n_csi2017_er=251,
        )
    elif dataset == "CsI2021":
        kernel = build_fastscan_template(
            dataset,
            RESPONSES_JSON,
            basis=basis,
            n_er=21,
            n_enu=120,
            n_pe_sub=8,
            pe_step=3.0,
        )
    else:
        raise ValueError(f"Unknown CsI dataset {dataset!r}")

    coeffs = coeff_tensor_from_triplets(basis, {}, include_sm=True)
    prediction = reconstruct_counts_from_kernel(kernel, coeffs)
    total = np.asarray(prediction["counts_per_bin"]["total"], dtype=np.float64)
    slow_reference_path = SLOW_REFERENCE_PATHS[dataset]
    if not slow_reference_path.exists():
        raise FileNotFoundError(slow_reference_path)
    slow_reference = np.load(slow_reference_path)
    alignment = fast_slow_alignment_metadata(total, slow_reference)
    if not alignment["fast_slow_allclose"]:
        raise ValueError(
            "Refusing to prepare CsI Fast reference because it does not reproduce "
            f"the Gate L Slow reference: {alignment}"
        )
    metadata = summarize_prediction(
        {
            "dataset": dataset,
            "npz_path": REFERENCE_PATHS[dataset].relative_to(REPO_ROOT).as_posix(),
            "json_path": REFERENCE_PATHS[dataset].with_suffix(".json").relative_to(REPO_ROOT).as_posix(),
            "kernel": kernel,
            "prediction": prediction,
        }
    )
    metadata.update(
        reference_kind="authoritative_flavor_fast_kernel",
        gate="P4_FAST",
        slow_reference_path=slow_reference_path.relative_to(REPO_ROOT).as_posix(),
        reconstructed_total_events=float(total.sum()),
        **alignment,
    )
    kernel["metadata"] = {**dict(kernel["metadata"]), **metadata}
    return kernel, metadata


def write_fast_reference(path: Path, kernel: dict[str, Any]) -> Path:
    from cevns_pyeft.kernels.storage import save_fastscan_template

    path.parent.mkdir(parents=True, exist_ok=True)
    return save_fastscan_template(path, kernel)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare or explicitly write authoritative CsI Flavor Fast references."
    )
    parser.add_argument("--dataset", default="all", choices=("all",) + DATASETS)
    parser.add_argument(
        "--no-compute",
        action="store_true",
        help="Only print target paths and guard status; do not build Fast kernels.",
    )
    parser.add_argument(
        "--write-reference-kernels",
        action="store_true",
        help="Write tests/reference_CsI*/fast_kernel.npz and JSON sidecars.",
    )
    parser.add_argument(
        "--acknowledge-reference-update",
        default="",
        help=f"Required exact phrase when writing: {APPROVAL_PHRASE!r}.",
    )
    args = parser.parse_args(argv)

    selected = _selected_datasets(str(args.dataset))
    if args.write_reference_kernels and args.acknowledge_reference_update != APPROVAL_PHRASE:
        raise SystemExit(
            "Refusing to write CsI Fast reference kernels without the exact "
            f"acknowledgement phrase: {APPROVAL_PHRASE!r}"
        )

    records: list[dict[str, Any]] = []
    for dataset in selected:
        path = REFERENCE_PATHS[dataset]
        if args.no_compute:
            records.append(
                {
                    "dataset": dataset,
                    "status": "NO_COMPUTE_NO_REFERENCE_WRITTEN",
                    "reference_path": str(path.relative_to(REPO_ROOT)),
                    "requires_write_flag": True,
                    "requires_acknowledgement": APPROVAL_PHRASE,
                }
            )
            continue

        kernel, metadata = compute_fast_reference(dataset)
        record = dict(metadata)
        record["reference_path"] = path.relative_to(REPO_ROOT).as_posix()
        if args.write_reference_kernels:
            write_fast_reference(path, kernel)
            record["status"] = "REFERENCE_WRITTEN"
        else:
            record["status"] = "DRY_RUN_NO_REFERENCE_WRITTEN"
        records.append(record)

    print(json.dumps(records, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
