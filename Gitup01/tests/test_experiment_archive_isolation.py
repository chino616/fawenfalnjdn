from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import json

import pytest

from cevns_pyeft.experiments.catalog import (
    ArchivedExperimentError,
    BUILTIN_CATALOG,
    ExperimentCatalog,
    SpecOnlyExperimentError,
)
from cevns_pyeft.experiments.loader import load_experiment
from cevns_pyeft.experiments.selection import AnalysisSelection
from cevns_pyeft.experiments.registry import list_experiments

ROOT = Path(__file__).resolve().parents[1]


def _status_catalog() -> ExperimentCatalog:
    base = BUILTIN_CATALOG.definition("CsI2021")
    return (
        ExperimentCatalog(builtins=False)
        .register("ActiveDemo", replace(base, dataset_id="ActiveDemo"), aliases=("active-demo",))
        .register("ArchivedDemo", replace(base, dataset_id="ArchivedDemo"), status="archived")
        .register("SpecDemo", replace(base, dataset_id="SpecDemo"), status="spec_only")
    )


def test_archive_and_spec_only_are_isolated_from_runtime_ids():
    catalog = _status_catalog()
    assert catalog.ids() == ("ActiveDemo",)
    assert catalog.archived_ids() == ("ArchivedDemo",)
    assert catalog.spec_only_ids() == ("SpecDemo",)
    assert catalog.canonical_id("active-demo") == "ActiveDemo"
    with pytest.raises(ArchivedExperimentError):
        catalog.definition("ArchivedDemo")
    with pytest.raises(SpecOnlyExperimentError):
        catalog.definition("SpecDemo")


def test_archived_and_spec_only_cannot_enter_selection_or_loader():
    catalog = _status_catalog()
    with pytest.raises(ArchivedExperimentError):
        AnalysisSelection.from_mapping({"datasets": [{"id": "ArchivedDemo"}]}, registry=catalog)
    with pytest.raises(SpecOnlyExperimentError):
        AnalysisSelection.from_mapping({"datasets": [{"id": "SpecDemo"}]}, registry=catalog)
    with pytest.raises(ArchivedExperimentError):
        load_experiment("ArchivedDemo", registry=catalog, definition=catalog.manifest_entry("ArchivedDemo").definition)


def test_global_legacy_views_only_expose_active_manifest_entries():
    assert list_experiments(include_specs=False) == BUILTIN_CATALOG.ids()
    assert not any(name in list_experiments(include_specs=False) for name in ("ArchivedDemo", "SpecDemo"))
    assert all(BUILTIN_CATALOG.status(name) == "active" for name in list_experiments(include_specs=False))


def test_statistics_and_resource_manifest_do_not_reintroduce_archived_ids():
    from cevns_pyeft.statistics.datasets import load_dataset

    with pytest.raises(ValueError):
        load_dataset("ArchivedDemo")
    manifest = json.loads((ROOT / "data" / "resource_manifest.json").read_text(encoding="utf-8"))
    assert {entry["dataset_id"] for entry in manifest["resources"]} <= set(BUILTIN_CATALOG.ids())


@pytest.mark.parametrize(
    ("status", "error_type"),
    (("archived", ArchivedExperimentError), ("spec_only", SpecOnlyExperimentError)),
)
def test_legacy_statistics_entrypoints_honor_builtin_lifecycle_status(monkeypatch, status, error_type):
    """Legacy fixed-name APIs must not bypass Catalog lifecycle state."""
    from cevns_pyeft.statistics.datasets import csi2021_dataset, load_dataset
    from cevns_pyeft.statistics.predictors import predict_raw_components

    # The built-in manifest is intentionally all-active in this snapshot. A
    # scoped status mutation lets this test exercise the real built-in ID and
    # prove the legacy API boundary without changing production manifest data.
    monkeypatch.setitem(BUILTIN_CATALOG._statuses, "CsI2021", status)
    with pytest.raises(error_type):
        load_dataset("CsI2021")
    with pytest.raises(error_type):
        csi2021_dataset()
    with pytest.raises(error_type):
        predict_raw_components("CsI2021")


def test_legacy_predictor_honors_custom_catalog_status_before_backend_dispatch():
    from cevns_pyeft.statistics.predictors import predict_raw_components

    catalog = (
        ExperimentCatalog(builtins=False)
        .register(
            "ArchivedDemo",
            replace(BUILTIN_CATALOG.definition("CsI2021"), dataset_id="ArchivedDemo"),
            status="archived",
        )
    )
    with pytest.raises(ArchivedExperimentError):
        predict_raw_components("ArchivedDemo", registry=catalog)
