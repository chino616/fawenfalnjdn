from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

from cevns_pyeft.nuclear.response import ResponseDB
from cevns_pyeft.rates.differential import _sm_left_dim6
from cevns_pyeft.theory.li2026.amplitude import amplitude_squared_onebody_li2026


RUN_DIR = Path("workflows/experiment-integration/runs/conus_plus_ge73_pheno")
RESPONSES_JSON = Path("data/responses/responses_all.json")
EXPECTED_CHANNELS = {"Delta", "M", "MPhiPP", "PhiPP", "PhiPT", "SigmaP", "SigmaPDelta", "SigmaPP"}


def test_ge73_response_metadata_and_channels():
    resp = ResponseDB(RESPONSES_JSON).get("Ge73")
    assert resp.basic["A"] == 73
    assert resp.basic["Z"] == 32
    assert resp.basic["N"] == 41
    assert set(resp.keys()) == EXPECTED_CHANNELS


def test_shared_li2026_amplitude_sm_is_finite_nonnegative():
    resp = ResponseDB(RESPONSES_JSON).get("Ge73")
    left_hat = _sm_left_dim6(True, 0.23873)
    amp = amplitude_squared_onebody_li2026(
        resp,
        E_nu_GeV=0.005,
        ER_keV=0.5,
        left_hat=left_hat,
        basis="np",
        c10_mass_mode="flavor",
    )
    assert math.isfinite(amp.amp2)
    assert amp.amp2 >= 0.0
    assert amp.basis == "np"
    assert set(amp.pieces) == EXPECTED_CHANNELS


def test_phase4_diagnostic_artifacts_are_finite():
    grid_path = RUN_DIR / "artifacts" / "nuclear_response_grid.csv"
    bench_path = RUN_DIR / "artifacts" / "theory_response_benchmarks.csv"
    figure_path = RUN_DIR / "figures" / "nuclear_response_channels.png"
    assert grid_path.exists()
    assert bench_path.exists()
    assert figure_path.exists()
    assert figure_path.stat().st_size > 0

    with grid_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["target"] for row in rows} == {"Ge73"}
    assert {row["basis_i"] for row in rows} <= {"p", "n", "scalar"}
    assert {row["basis_j"] for row in rows} <= {"p", "n", "scalar"}
    assert all(math.isfinite(float(row["value"])) for row in rows)

    with bench_path.open(encoding="utf-8", newline="") as handle:
        bench = list(csv.DictReader(handle))
    assert bench
    assert all(row["finite"] == "True" for row in bench)
    assert all(row["nonnegative"] == "True" for row in bench)
    assert np.all([float(row["amplitude_squared"]) >= 0.0 for row in bench])
