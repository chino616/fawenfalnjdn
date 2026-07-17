from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import numpy as np

from .basis import BasisElement, coeff_vector_from_triplets, li2026_left_basis_current
from .builder import KernelPayload, save_kernel
from .reconstruction import reconstruct_counts_from_kernel

from dataclasses import is_dataclass

DATASETS = ("CsI2021", "CsI2017", "Ar2020")
KERNEL_FILENAMES = {
    "CsI2021": "csi2021_fast_kernel.npz",
    "CsI2017": "csi2017_fast_kernel.npz",
    "Ar2020": "ar2020_fast_kernel.npz",
}


def _basis_from_jsonable(raw_basis: Sequence[Any]) -> list[BasisElement]:
    basis: list[BasisElement] = []
    for item in raw_basis:
        if isinstance(item, BasisElement):
            basis.append(item)
            continue
        triplet = item["triplet"]
        basis.append(
            BasisElement(
                index=int(item["index"]),
                name=str(item["name"]),
                label=str(item["label"]),
                triplet=(int(triplet[0]), int(triplet[1]), str(triplet[2])),
            )
        )
    return basis


def _jsonable_basis(basis: Sequence[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in basis:
        if is_dataclass(item):
            obj = asdict(item)
        else:
            obj = dict(item)
        obj["triplet"] = list(obj["triplet"])
        out.append(obj)
    return out


def _template_paths(path: str | Path) -> tuple[Path, Path]:
    p = Path(path)
    if p.suffix == ".npz":
        return p, p.with_suffix(".json")
    if p.suffix == ".json":
        return p.with_suffix(".npz"), p
    raise ValueError("fastscan template path must end with .npz or .json")


def validate_fastscan_template(kernel: Mapping[str, Any]) -> None:
    metadata = dict(kernel.get("metadata", {}))
    dataset = str(metadata.get("dataset", ""))
    if dataset not in DATASETS:
        raise ValueError(f"Unsupported dataset in template metadata: {dataset!r}")

    full = np.asarray(kernel["full_kernel"])
    diag = np.asarray(kernel["diag"])
    pair_re = np.asarray(kernel["pair_re"])
    pair_im = np.asarray(kernel["pair_im"])
    pair_index = np.asarray(kernel["pair_index"], dtype=int)
    pe_bins = np.asarray(kernel["pe_bins"], dtype=float)
    basis = list(kernel["basis"])
    targets = list(kernel["targets"])
    flavors = list(kernel["source_flavors"])
    channels = list(kernel["channels"])

    if full.ndim != 6:
        raise ValueError(f"full_kernel must be 6D, got shape {full.shape}")
    if full.shape[3] != full.shape[4]:
        raise ValueError(f"basis axes must be square, got shape {full.shape}")
    if len(targets) != full.shape[0]:
        raise ValueError("targets length does not match full_kernel axis 0")
    if len(flavors) != full.shape[1]:
        raise ValueError("source_flavors length does not match full_kernel axis 1")
    if len(channels) != full.shape[2]:
        raise ValueError("channels length does not match full_kernel axis 2")
    if len(basis) != full.shape[3]:
        raise ValueError("basis length does not match full_kernel basis axes")
    if pe_bins.size - 1 != full.shape[5]:
        raise ValueError("pe_bins length does not match full_kernel bin axis")
    if diag.shape[0] != len(basis):
        raise ValueError("diag axis 0 does not match basis length")
    if pair_index.ndim != 2 or pair_index.shape[1] != 2:
        raise ValueError("pair_index must have shape (N, 2)")
    if pair_re.shape != pair_im.shape:
        raise ValueError("pair_re and pair_im shapes differ")
    if pair_re.shape[0] != pair_index.shape[0]:
        raise ValueError("pair template count does not match pair_index")


def save_fastscan_template(path: str | Path, kernel: Mapping[str, Any]) -> Path:
    npz_path, _json_path = _template_paths(path)
    npz_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = dict(kernel["metadata"])
    metadata["basis"] = _jsonable_basis(kernel["basis"])
    metadata["targets"] = list(kernel["targets"])
    metadata["source_flavors"] = list(kernel["source_flavors"])
    metadata["channels"] = list(kernel["channels"])
    metadata["pe_bins"] = np.asarray(kernel["pe_bins"], dtype=float).tolist()
    metadata["kernel_shape"] = list(np.asarray(kernel["full_kernel"]).shape)
    metadata["diag_shape"] = list(np.asarray(kernel["diag"]).shape)
    metadata["pair_re_shape"] = list(np.asarray(kernel["pair_re"]).shape)
    metadata["pair_im_shape"] = list(np.asarray(kernel["pair_im"]).shape)
    metadata["pair_index_shape"] = list(np.asarray(kernel["pair_index"]).shape)

    payload = KernelPayload(
        metadata=metadata,
        full_kernel=np.asarray(kernel["full_kernel"]),
        diag=np.asarray(kernel["diag"]),
        pair_re=np.asarray(kernel["pair_re"]),
        pair_im=np.asarray(kernel["pair_im"]),
        pair_index=np.asarray(kernel["pair_index"], dtype=int),
    )
    save_kernel(npz_path, payload)
    return npz_path


def load_fastscan_template(path: str | Path) -> dict[str, Any]:
    npz_path, json_path = _template_paths(path)
    if not npz_path.exists():
        raise FileNotFoundError(npz_path)
    if not json_path.exists():
        raise FileNotFoundError(json_path)

    with np.load(npz_path, allow_pickle=False) as arrays:
        metadata = json.loads(json_path.read_text(encoding="utf-8"))
        kernel = {
            "metadata": metadata,
            "basis": _basis_from_jsonable(metadata["basis"]),
            "targets": list(metadata["targets"]),
            "source_flavors": list(metadata["source_flavors"]),
            "channels": list(metadata["channels"]),
            "pe_bins": np.asarray(arrays["pe_bins"], dtype=float),
            "full_kernel": np.asarray(arrays["full_kernel"]),
            "diag": np.asarray(arrays["diag"]),
            "pair_re": np.asarray(arrays["pair_re"]),
            "pair_im": np.asarray(arrays["pair_im"]),
            "pair_index": np.asarray(arrays["pair_index"], dtype=int),
            "kernel_axis_kind": "channel_resolved_full_li2026",
            "template_npz_path": str(npz_path),
            "template_json_path": str(json_path),
        }

    validate_fastscan_template(kernel)
    return kernel


def discover_fastscan_templates(data_dir: str | Path) -> list[Path]:
    found: list[Path] = []
    for npz_path in sorted(Path(data_dir).rglob("*.npz")):
        json_path = npz_path.with_suffix(".json")
        if not json_path.exists():
            continue
        try:
            metadata = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if metadata.get("dataset") in DATASETS:
            found.append(npz_path)
    return found


def build_fastscan_template(
    dataset: str,
    responses_json: str | Path,
    *,
    basis: Optional[Sequence[BasisElement]] = None,
    sin2thetaW: float = 0.2387,
    c10_mass_mode: str = "flavor",
    n_er: int = 21,
    n_enu: int = 120,
    n_pe_sub: int = 8,
    n_csi2017_er: int = 251,
    n_obs_sub: int = 8,
) -> dict[str, Any]:
    from cevns_pyeft.experiments.coherent.fast_kernel_ar2020 import build_fast_kernel_ar2020
    from cevns_pyeft.experiments.coherent.fast_kernel_csi2017 import build_fast_kernel_csi2017
    from cevns_pyeft.experiments.coherent.fast_kernel_csi2021 import build_fast_kernel_csi2021

    basis = list(basis or li2026_left_basis_current())
    if dataset == "CsI2021":
        return build_fast_kernel_csi2021(
            responses_json,
            basis=basis,
            sin2thetaW=sin2thetaW,
            c10_mass_mode=c10_mass_mode,
            n_er=n_er,
            n_enu=n_enu,
            n_pe_sub=n_pe_sub,
        )
    if dataset == "CsI2017":
        return build_fast_kernel_csi2017(
            responses_json,
            basis=basis,
            sin2thetaW=sin2thetaW,
            c10_mass_mode=c10_mass_mode,
            n_er=n_csi2017_er,
            n_enu=n_enu,
        )
    if dataset == "Ar2020":
        return build_fast_kernel_ar2020(
            responses_json,
            basis=basis,
            sin2thetaW=sin2thetaW,
            c10_mass_mode=c10_mass_mode,
            n_er=n_er,
            n_enu=n_enu,
            n_obs_sub=n_obs_sub,
        )
    raise ValueError(f"Unsupported dataset: {dataset!r}")


def reconstruct_saved_kernel(
    path: str | Path,
    wc_triplets: Optional[Mapping[tuple[int, int, str], complex]] = None,
    *,
    include_sm: bool = True,
    sin2thetaW: float = 0.2387,
) -> tuple[dict[str, Any], dict[str, Any]]:
    kernel = load_fastscan_template(path)
    coeff = coeff_vector_from_triplets(
        kernel["basis"],
        wc_triplets or {},
        include_sm=include_sm,
        sin2thetaW=sin2thetaW,
    )
    return kernel, reconstruct_counts_from_kernel(kernel, coeff)


def build_save_load_reconstruct(
    dataset: str,
    responses_json: str | Path,
    out_dir: str | Path,
    *,
    include_sm: bool = True,
    wc_triplets: Optional[Mapping[tuple[int, int, str], complex]] = None,
    sin2thetaW: float = 0.2387,
    c10_mass_mode: str = "flavor",
    n_er: int = 21,
    n_enu: int = 120,
    n_pe_sub: int = 8,
    n_csi2017_er: int = 251,
    n_obs_sub: int = 8,
) -> dict[str, Any]:
    kernel = build_fastscan_template(
        dataset,
        responses_json,
        sin2thetaW=sin2thetaW,
        c10_mass_mode=c10_mass_mode,
        n_er=n_er,
        n_enu=n_enu,
        n_pe_sub=n_pe_sub,
        n_csi2017_er=n_csi2017_er,
        n_obs_sub=n_obs_sub,
    )
    npz_path = Path(out_dir) / KERNEL_FILENAMES[dataset]
    save_fastscan_template(npz_path, kernel)
    loaded, prediction = reconstruct_saved_kernel(
        npz_path,
        wc_triplets,
        include_sm=include_sm,
        sin2thetaW=sin2thetaW,
    )
    return {
        "dataset": dataset,
        "npz_path": str(npz_path),
        "json_path": str(npz_path.with_suffix(".json")),
        "kernel": loaded,
        "prediction": prediction,
    }


def summarize_prediction(result: Mapping[str, Any]) -> dict[str, Any]:
    pred = result["prediction"]
    total = np.asarray(pred["counts_per_bin"]["total"], dtype=float)
    return {
        "dataset": str(result["dataset"]),
        "total_events": float(total.sum()),
        "n_bins": int(total.size),
        "kernel_shape": list(np.asarray(result["kernel"]["full_kernel"]).shape),
        "npz_path": str(result["npz_path"]),
        "json_path": str(result["json_path"]),
    }



def saved_kernel_main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build, save, load, and reconstruct CEvNS fast-scan kernels.")
    parser.add_argument("--responses", required=True, help="Path to Data/responses_all.json")
    parser.add_argument("--out-dir", default="saved_kernel_fast_outputs/kernels")
    parser.add_argument("--datasets", nargs="+", default=list(DATASETS), choices=list(DATASETS))
    parser.add_argument("--n-er", type=int, default=21)
    parser.add_argument("--n-enu", type=int, default=120)
    parser.add_argument("--n-pe-sub", type=int, default=8)
    parser.add_argument("--n-csi2017-er", type=int, default=251)
    parser.add_argument("--n-obs-sub", type=int, default=8)
    args = parser.parse_args(argv)

    rows = []
    for dataset in args.datasets:
        result = build_save_load_reconstruct(
            dataset,
            args.responses,
            args.out_dir,
            n_er=args.n_er,
            n_enu=args.n_enu,
            n_pe_sub=args.n_pe_sub,
            n_csi2017_er=args.n_csi2017_er,
            n_obs_sub=args.n_obs_sub,
        )
        rows.append(summarize_prediction(result))
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DATASETS",
    "KERNEL_FILENAMES",
    "validate_fastscan_template",
    "save_fastscan_template",
    "load_fastscan_template",
    "discover_fastscan_templates",
    "build_fastscan_template",
    "reconstruct_saved_kernel",
    "build_save_load_reconstruct",
    "summarize_prediction",
    "saved_kernel_main",
]
