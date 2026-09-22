#!/usr/bin/env python3
"""Generate CsI Slow reference arrays only after explicit approval.

The default mode is intentionally non-writing.  Gate L requires authoritative
Slow reference arrays, but those arrays must not be created or updated as an
incidental side effect of diagnostics or tests.
"""

from __future__ import annotations

import argparse
import hashlib
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
APPROVAL_PHRASE = "I approve updating CsI Slow reference arrays"
Dataset = Literal["CsI2017", "CsI2021"]
DATASETS: tuple[Dataset, ...] = ("CsI2017", "CsI2021")
REFERENCE_PATHS: dict[Dataset, Path] = {
    "CsI2017": REPO_ROOT / "tests" / "reference_CsI2017" / "slow_reference.npy",
    "CsI2021": REPO_ROOT / "tests" / "reference_CsI2021" / "slow_reference.npy",
}


def _selected_datasets(raw: str) -> tuple[Dataset, ...]:
    if raw == "all":
        return DATASETS
    if raw not in DATASETS:
        raise ValueError(f"Unknown CsI dataset {raw!r}")
    return (raw,)  # type: ignore[return-value]


def compute_slow_reference(dataset: Dataset) -> tuple[np.ndarray, dict[str, Any]]:
    """Return the direct Slow total counts and generation metadata."""

    if dataset == "CsI2017":
        from cevns_pyeft.experiments.coherent.slow_counts_csi2017 import (
            slow_counts_csi2017,
        )

        out = slow_counts_csi2017(RESPONSES_JSON)
        settings = {"n_enu": 120, "direct_slow_defaults": True}
    elif dataset == "CsI2021":
        from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import (
            slow_counts_csi2021,
        )

        out = slow_counts_csi2021(RESPONSES_JSON)
        settings = {
            "n_er": 21,
            "n_enu": 120,
            "n_pe_bin": 8,
            "pe_step": 3.0,
            "direct_slow_defaults": True,
        }
    else:
        raise ValueError(f"Unknown CsI dataset {dataset!r}")

    counts = np.asarray(out["counts_per_bin"]["total"], dtype=np.float64)
    metadata = {
        "dataset": dataset,
        "reference_kind": "authoritative_slow_counts",
        "gate": "L",
        "source": "direct Slow calculation",
        "responses_json": str(RESPONSES_JSON.relative_to(REPO_ROOT)),
        "settings": settings,
        "shape": list(counts.shape),
        "sum": float(np.sum(counts)),
        "sha256": hashlib.sha256(np.ascontiguousarray(counts).view(np.uint8)).hexdigest(),
    }
    return counts, metadata


def write_reference_array(path: Path, counts: np.ndarray, metadata: dict[str, Any]) -> None:
    """Write the reference array and a JSON sidecar in one explicit operation."""

    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, np.asarray(counts, dtype=np.float64))
    path.with_suffix(".json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare or explicitly write authoritative CsI Slow references."
    )
    parser.add_argument("--dataset", default="all", choices=("all",) + DATASETS)
    parser.add_argument(
        "--no-compute",
        action="store_true",
        help="Only print target paths and guard status; do not run Slow integration.",
    )
    parser.add_argument(
        "--write-reference-arrays",
        action="store_true",
        help="Write tests/reference_CsI*/slow_reference.npy and JSON sidecars.",
    )
    parser.add_argument(
        "--acknowledge-reference-update",
        default="",
        help=f"Required exact phrase when writing: {APPROVAL_PHRASE!r}.",
    )
    args = parser.parse_args(argv)

    selected = _selected_datasets(str(args.dataset))
    if args.write_reference_arrays and args.acknowledge_reference_update != APPROVAL_PHRASE:
        raise SystemExit(
            "Refusing to write CsI Slow reference arrays without the exact "
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

        counts, metadata = compute_slow_reference(dataset)
        record = dict(metadata)
        record["reference_path"] = str(path.relative_to(REPO_ROOT))
        if args.write_reference_arrays:
            write_reference_array(path, counts, metadata)
            record["status"] = "REFERENCE_WRITTEN"
        else:
            record["status"] = "DRY_RUN_NO_REFERENCE_WRITTEN"
        records.append(record)

    print(json.dumps(records, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
