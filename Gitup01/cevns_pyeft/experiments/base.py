from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re
import numpy as np


@dataclass(frozen=True)
class TargetComponent:
    name: str
    response_key: str
    weight: float = 1.0


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    dataset: str
    detector_mass_kg: float


def _asarray(x):
    return np.asarray(x, dtype=float)


def _scalar_or_array(arr: np.ndarray, like):
    if np.isscalar(like):
        return float(np.asarray(arr).reshape(-1)[0])
    return arr


def _data_path(responses_json: str | Path, rel: str | Path) -> Path:
    from cevns_pyeft.foundation.paths import resource_root
    from cevns_pyeft.foundation.resources import resolve_resource
    p=Path(rel)
    if p.is_absolute():return p
    response=Path(responses_json).resolve()
    root=response.parent.parent.parent if response.parent.name=='responses' and response.parent.parent.name=='data' else resource_root()
    return resolve_resource(root,p)


def _num(x: str) -> float:
    return float(str(x).replace('D', 'e').replace('d', 'e').replace('*^', 'e').replace('*10^', 'e'))


def _table(path: str | Path, ncol: int) -> np.ndarray:
    rows = []
    for raw in Path(path).read_text(encoding='utf-8', errors='ignore').splitlines():
        parts = re.split(r'[\s,]+', raw.strip())
        if len(parts) >= ncol:
            try:
                rows.append([_num(v) for v in parts[:ncol]])
            except Exception:
                pass
    arr = np.asarray(rows, dtype=float)
    if arr.ndim != 2 or arr.shape[0] < 2:
        raise ValueError(f'Could not read numeric table: {path}')
    return arr


def _interp_eff(path: str | Path, x_col: int, y_col: int, *, low: float, threshold: Optional[float] = None):
    tab = _table(path, max(x_col, y_col) + 1)
    x, y = tab[:, x_col], tab[:, y_col]
    order = np.argsort(x)
    x, y = x[order], y[order]
    keep = np.r_[True, np.diff(x) > 0]
    x, y = x[keep], y[keep]

    def eff(v):
        a = _asarray(v)
        out = np.interp(a, x, y, left=low, right=float(y[-1]))
        if threshold is not None:
            out = np.where(a > threshold, out, low)
        return _scalar_or_array(np.where(np.isfinite(a), out, 0.0), v)
    return eff


__all__ = [
    "TargetComponent",
    "ExperimentConfig",
    "_data_path",
    "_num",
    "_table",
    "_interp_eff",
]

