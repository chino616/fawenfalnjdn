from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import math
import re
import numpy as np

Number = Union[int, float]
CoeffList = List[Number]
CoeffMat2 = List[List[CoeffList]]
ResponseEntry = Union[CoeffList, CoeffMat2]

def _poly_eval(coeffs: CoeffList, y: float) -> float:
    v = 0.0
    for c in reversed(coeffs):
        v = v * y + float(c)
    return v

def _is_coeffmat2(x: Any) -> bool:
    if not isinstance(x, list) or len(x) != 2:
        return False
    if any((not isinstance(row, list) or len(row) != 2 for row in x)):
        return False
    return all((isinstance(x[i][j], list) for i in range(2) for j in range(2)))

def y_from_qb(q: float, b: float) -> float:
    return (0.5 * q * b) ** 2

def np_to_iso_matrix(W_np: List[List[float]]) -> List[List[float]]:
    M = [[1.0, 1.0], [1.0, -1.0]]
    tmp00 = W_np[0][0] * M[0][0] + W_np[0][1] * M[1][0]
    tmp01 = W_np[0][0] * M[0][1] + W_np[0][1] * M[1][1]
    tmp10 = W_np[1][0] * M[0][0] + W_np[1][1] * M[1][0]
    tmp11 = W_np[1][0] * M[0][1] + W_np[1][1] * M[1][1]
    W00 = M[0][0] * tmp00 + M[1][0] * tmp10
    W01 = M[0][0] * tmp01 + M[1][0] * tmp11
    W10 = M[0][1] * tmp00 + M[1][1] * tmp10
    W11 = M[0][1] * tmp01 + M[1][1] * tmp11
    return [[W00, W01], [W10, W11]]

def bilinear(W: List[List[float]], a0: float, a1: float) -> float:
    return a0 * (W[0][0] * a0 + W[0][1] * a1) + a1 * (W[1][0] * a0 + W[1][1] * a1)

@dataclass(frozen=True)
class ResponseW:
    name: str
    basic: Dict[str, Any]
    exp_factor: float
    responses: Dict[str, ResponseEntry]

    def keys(self) -> List[str]:
        return sorted(self.responses.keys())

    def get_basic(self, key: str, default: Any=None) -> Any:
        return self.basic.get(key, default)

    def W_np(self, key: str, y: float) -> Union[float, List[List[float]]]:
        if key not in self.responses:
            raise KeyError(f"[{self.name}] Unknown response '{key}'. Available: {self.keys()}")
        entry = self.responses[key]
        e = math.exp(self.exp_factor * y)
        if _is_coeffmat2(entry):
            m = entry
            return [[_poly_eval(m[0][0], y) * e, _poly_eval(m[0][1], y) * e], [_poly_eval(m[1][0], y) * e, _poly_eval(m[1][1], y) * e]]
        else:
            coeffs = entry
            return _poly_eval(coeffs, y) * e

    def W_iso(self, key: str, y: float) -> Union[float, List[List[float]]]:
        W = self.W_np(key, y)
        if isinstance(W, list):
            return np_to_iso_matrix(W)
        return W

    def W_np_from_q(self, key: str, q: float, b: Optional[float]=None) -> Union[float, List[List[float]]]:
        if b is None:
            if 'b' not in self.basic:
                raise KeyError(f"[{self.name}] basic['b'] not found; please pass b explicitly.")
            b = float(self.basic['b'])
        return self.W_np(key, y_from_qb(q, b))

    def contract_np(self, key: str, y: float, an: float, ap: float) -> float:
        W = self.W_np(key, y)
        if not isinstance(W, list):
            raise TypeError(f"[{self.name}] Response '{key}' is scalar in JSON; cannot do 2x2 contraction.")
        return bilinear(W, ap, an)

    def contract_iso(self, key: str, y: float, a0: float, a1: float) -> float:
        W = self.W_iso(key, y)
        if not isinstance(W, list):
            raise TypeError(f"[{self.name}] Response '{key}' is scalar in JSON; cannot do 2x2 contraction.")
        return bilinear(W, a0, a1)

class ResponseDB:

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        obj = json.loads(self.path.read_text(encoding='utf-8'))
        if 'nuclei' not in obj or not isinstance(obj['nuclei'], dict):
            raise ValueError("JSON format error: top-level must contain dict field 'nuclei'.")
        self.meta: Dict[str, Any] = obj.get('meta', {})
        self._raw_nuclei: Dict[str, Any] = obj['nuclei']
        self._cache: Dict[str, ResponseW] = {}

    def nuclei(self) -> List[str]:
        return sorted(self._raw_nuclei.keys())

    def find(self, pattern: str, ignore_case: bool=True) -> List[str]:
        flags = re.IGNORECASE if ignore_case else 0
        try:
            rx = re.compile(pattern, flags)
            return [k for k in self.nuclei() if rx.search(k)]
        except re.error:
            p = pattern.lower() if ignore_case else pattern
            return [k for k in self.nuclei() if (k.lower().find(p) >= 0 if ignore_case else k.find(p) >= 0)]

    def get(self, name: str) -> ResponseW:
        if name in self._cache:
            return self._cache[name]
        if name not in self._raw_nuclei:
            raise KeyError(f"Unknown nucleus '{name}'. Available (first 20): {self.nuclei()[:20]}")
        item = self._raw_nuclei[name]
        if not isinstance(item, dict):
            raise ValueError(f"Bad nucleus entry type for '{name}' (expected dict).")
        basic = item.get('basic', {})
        exp_factor = float(item.get('exp_factor', -2.0))
        responses = item.get('responses', {})
        rw = ResponseW(name=name, basic=basic, exp_factor=exp_factor, responses=responses)
        self._cache[name] = rw
        return rw

    def get_by_symbol_A(self, symbol: str, A: int) -> ResponseW:
        candidates = [f'{symbol}{A}', f'{symbol}-{A}', f'{symbol}_{A}']
        for c in candidates:
            if c in self._raw_nuclei:
                return self.get(c)
        raise KeyError(f'Cannot find nucleus for symbol={symbol}, A={A}. Tried {candidates}.')

    def describe(self, name: str) -> Dict[str, Any]:
        r = self.get(name)
        return {'name': r.name, 'basic': r.basic, 'exp_factor': r.exp_factor, 'response_keys': r.keys()}

__all__ = [
    "Number",
    "CoeffList",
    "CoeffMat2",
    "ResponseEntry",
    "_poly_eval",
    "_is_coeffmat2",
    "y_from_qb",
    "np_to_iso_matrix",
    "bilinear",
    "ResponseW",
    "ResponseDB",
]
