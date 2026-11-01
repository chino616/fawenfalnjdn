from __future__ import annotations

from cevns_pyeft.experiments.registry import list_experiments
from cevns_pyeft.experiments.specs import (
    discover_experiment_spec_paths,
    load_experiment_spec,
)


def test_bundled_experiment_specs_are_discoverable():
    names = list_experiments()
    assert "CsI2021" in names
    assert {
        load_experiment_spec(path).dataset_name
        for path in discover_experiment_spec_paths()
    } == {"CsI2017", "CsI2021"}


def test_flat_and_nested_experiment_specs_are_discoverable(tmp_path):
    data_root = tmp_path / "data" / "experiments"
    flat = data_root / "FlatDataset" / "experiment.yaml"
    nested = data_root / "ReadableExperiment" / "nested_dataset" / "experiment.yaml"
    flat.parent.mkdir(parents=True)
    nested.parent.mkdir(parents=True)
    flat.write_text(
        "dataset_name: FlatDataset\nsource_type: stopped_pion\ntarget_mode: flat_target\n",
        encoding="utf-8",
    )
    nested.write_text(
        "dataset_name: nested_dataset\nsource_type: reactor\ntarget_mode: Ge73_only\n",
        encoding="utf-8",
    )

    discovered = discover_experiment_spec_paths(tmp_path)

    assert discovered == (flat, nested)
    assert load_experiment_spec("FlatDataset", tmp_path).path == flat.resolve()
    assert load_experiment_spec("nested_dataset", tmp_path).path == nested.resolve()
