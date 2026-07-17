from __future__ import annotations

from cevns_pyeft.experiments.registry import get_experiment, get_experiment_spec, list_experiments
from cevns_pyeft.experiments.specs import discover_experiment_spec_paths, required_input_fields


def test_bundled_experiment_specs_are_discoverable():
    names = list_experiments()
    assert "CsI2021" in names
    assert "conus_plus_2025_reproduction" in names
    assert "conus_plus_2025_first_observation" in names
    assert "conus_legacy_mathematica_2026_01_08" in names
    assert len(discover_experiment_spec_paths()) >= 3


def test_load_conus_reproduction_spec():
    spec = get_experiment_spec("conus_plus_2025_reproduction")
    assert spec.dataset_name == "conus_plus_2025_reproduction"
    assert spec.source_type == "reactor"
    assert spec.target_mode == "natural_germanium"
    assert spec.data["analysis_window_evee"] == [160, 800]
    assert spec.data["fission_fractions"]["U235"] == 0.53


def test_registry_returns_spec_dict_for_data_driven_experiment():
    data = get_experiment("conus_legacy_mathematica_2026_01_08")
    assert data["source_type"] == "reactor"
    assert data["target_mode"] == "Ge73_only"
    assert data["_spec_path"].endswith("experiment.yaml")


def test_publication_spec_marks_required_inputs_without_failing_load():
    spec = get_experiment_spec("conus_plus_2025_first_observation")
    assert spec.data["spec_status"] == "incomplete_for_exact_publication_reproduction"
    assert required_input_fields(spec.data) == ()
