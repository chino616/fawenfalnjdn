"""Explicit namespaces, immutable scientific input records and finite JSON."""
from __future__ import annotations
from dataclasses import asdict, is_dataclass
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PART = "left_cutoff_scales"
SCHEMA = "left_cutoff_scales/1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def plain(obj):
    if is_dataclass(obj):
        return plain(asdict(obj))
    if isinstance(obj, dict):
        return {str(k): plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [plain(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return plain(obj.tolist())
    if isinstance(obj, np.generic):
        return plain(obj.item())
    if isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, float) and not np.isfinite(obj):
        raise ValueError("nonfinite number must be represented by an explicit status/open endpoint")
    return obj


def write_json(path, value):
    Path(path).write_text(json.dumps(plain(value), ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def new_run(path):
    path = Path(path).resolve()
    parent = (ROOT / "outputs/cutoff_scales").resolve()
    if path == parent or not path.is_relative_to(parent):
        raise ValueError("cutoff numerical outputs must stay under this mainline's outputs/cutoff_scales/<run_id>")
    if path.exists():
        raise FileExistsError("choose a new cutoff run; existing runs are immutable")
    path.mkdir(parents=True)
    return path
