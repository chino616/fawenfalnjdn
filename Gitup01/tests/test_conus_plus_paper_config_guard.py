from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "experiment_integration" / "conus_paper_config_guard.py"


def _load_guard_module():
    spec = importlib.util.spec_from_file_location("conus_paper_config_guard", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_paper_config_guard_separates_effective_and_actual_exposure():
    guard = _load_guard_module()
    summary = guard.build_summary()

    assert summary["status"] == "PASS"
    assert summary["no_duplicate_exposure_factor"] is True
    assert summary["common_119day_rounds_to_paper_integers"] is True
    assert summary["hybrid_effective_total"] == pytest.approx(150.3408190683323)
    assert summary["hybrid_actual_total"] == pytest.approx(323.65254471154014)
    assert summary["live_time_difference_total"] == pytest.approx(12.325438457790668)
    assert summary["remaining_shape_or_input_difference_total"] == pytest.approx(9.66647516739431)


def test_unit_exposure_reconstructs_actual_bin_without_duplicate_factor():
    guard = _load_guard_module()
    unit = guard.build_summary()["unit_exposure_check"]

    assert unit["passes"] is True
    assert unit["rate_per_kg_day_bin"] == pytest.approx(0.17304559367894155)
    assert unit["effective_from_rate"] == pytest.approx(20.592425647794045)
    assert unit["actual_combined_from_rate"] == pytest.approx(56.483812232743304)
    assert unit["actual_combined_reference"] == pytest.approx(56.483812232743304)


def test_guard_writes_machine_readable_outputs(tmp_path):
    guard = _load_guard_module()
    paths = guard.write_outputs(tmp_path)

    for value in paths.values():
        assert Path(value).exists()

    report = Path(paths["markdown"]).read_text(encoding="utf-8")
    assert "not a duplicate exposure factor" in report
    assert "actual C2+C3+C5" in report
    assert "effective-detector Fig. 1" in report
