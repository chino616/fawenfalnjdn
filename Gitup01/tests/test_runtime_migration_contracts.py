"""Lifecycle and tool integration checks against the real local resources."""
from dataclasses import replace
from pathlib import Path

import pytest

from cevns_pyeft.experiments.catalog import (
    ArchivedExperimentError, BUILTIN_CATALOG, ExperimentCatalog, SpecOnlyExperimentError,
)
from cevns_pyeft.experiments.loader import load_experiment

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_definition_cannot_bypass_lifecycle_and_custom_aliases_work():
    base = BUILTIN_CATALOG.definition("CsI2021")
    catalog = ExperimentCatalog(builtins=False)
    for name, status in [("Archived", "archived"), ("Spec", "spec_only")]:
        catalog.register(name, replace(base, dataset_id=name), status=status)
    catalog.register("Live", replace(base, dataset_id="Live"), aliases=("live",))
    assert load_experiment("live", registry=catalog, resources=ROOT,
                           definition=catalog.definition("Live")).dataset_id == "Live"
    for name, error in [("Archived", ArchivedExperimentError), ("Spec", SpecOnlyExperimentError)]:
        with pytest.raises(error):
            load_experiment(name, registry=catalog, resources=ROOT,
                            definition=catalog.manifest_entry(name).definition)
    catalog.unregister("live")
    assert catalog.ids() == ()
    with pytest.raises(KeyError):
        catalog.canonical_id("live")


def test_manifest_definition_id_alias_and_default_set_are_preserved():
    from cevns_pyeft.experiments.manifest import BUILTIN_MANIFEST
    assert BUILTIN_CATALOG.ids() == ("CsI2021", "CsI2017", "Ar2020")
    assert BUILTIN_CATALOG.archived_ids() == BUILTIN_CATALOG.spec_only_ids() == ()
    for entry in BUILTIN_MANIFEST:
        assert BUILTIN_CATALOG.definition(entry.aliases[0]).dataset_id == entry.dataset_id
    with pytest.raises(RuntimeError, match="manifest-owned"):
        BUILTIN_CATALOG.unregister("CsI2021")


@pytest.mark.parametrize("status,error", [("archived", ArchivedExperimentError),
                                         ("spec_only", SpecOnlyExperimentError)])
def test_legacy_views_follow_catalog_without_a_second_active_set(monkeypatch, status, error):
    from cevns_pyeft.experiments.registry import (
        EXPERIMENT_REGISTRY, EXPERIMENT_SLOW_COUNT_REGISTRY, get_experiment,
        get_slow_count_function, list_experiments,
    )
    saved_loader = EXPERIMENT_REGISTRY["CsI2021"]
    monkeypatch.setitem(BUILTIN_CATALOG._statuses, "CsI2021", status)
    assert "CsI2021" not in tuple(EXPERIMENT_REGISTRY)
    assert "CsI2021" not in tuple(EXPERIMENT_SLOW_COUNT_REGISTRY)
    assert list_experiments(include_specs=False) == BUILTIN_CATALOG.ids()
    for action in [lambda: get_experiment("csi2021"),
                   lambda: get_slow_count_function("CsI2021"), saved_loader]:
        with pytest.raises(error):
            action()
    assert isinstance(get_experiment("Ar2020"), dict)


def test_all_resource_hashes_and_override_scopes_are_audited():
    from tools.validate_resource_manifest import audit
    result = audit(ROOT, ROOT / "data/resource_manifest.json")
    assert result["status"] == "PASS", result["errors"]
    assert result["unknown_or_unused_manifest_entries"] == []
    assert result["ambiguous_override_resource_ids"] == ["efficiency"]
    assert result["override_scope_checks"] == [
        {"resource_id": "efficiency", "unscoped_rejected": True, "scoped_accepted": True}
    ]
    assert all(item["hash_match"] for item in result["resources"])


def test_resource_audit_unknown_id_unused_entry_and_alias_conflict_block(tmp_path):
    import json
    from tools.validate_resource_manifest import audit
    manifest = ROOT / "data/resource_manifest.json"
    assert audit(ROOT, manifest, ["misspelled"]) ["status"] == "BLOCKED"
    doc = json.loads(manifest.read_text())
    doc["resources"].append({**doc["resources"][0], "resource_id": "unused"})
    broken = tmp_path / "manifest.json"
    broken.write_text(json.dumps(doc))
    assert audit(ROOT, broken, ["CsI2021"])["status"] == "BLOCKED"
    # A conflicting legacy alias must be reported, never silently preferred.
    old = tmp_path / "data/datafiles/COHERENT_eff.txt"
    new = tmp_path / "data/experiments/COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt"
    old.parent.mkdir(parents=True); new.parent.mkdir(parents=True)
    old.write_text("1 2"); new.write_text("1 3")
    result = audit(tmp_path, manifest, ["CsI2017"])
    assert result["status"] == "BLOCKED"
    assert any("conflicting" in error for error in result["errors"])


def test_audit_cli_uses_own_package_with_external_data_root(tmp_path):
    import json, os, subprocess, sys
    result = subprocess.run([
        sys.executable, "-I", str(ROOT / "tools/validate_resource_manifest.py"),
        "--root", str(ROOT), "--dataset", "csi2021",
    ], cwd=tmp_path, capture_output=True, text=True,
        env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
    assert result.returncode == 0, result.stderr + result.stdout
    assert json.loads(result.stdout)["datasets"] == ["CsI2021"]


def test_scaffold_cli_runs_isolated_contract_and_rejects_collisions(tmp_path):
    import os, subprocess, sys
    fixture = tmp_path / "new-project"
    tool = ROOT / "tools/scaffold_experiment.py"
    command = [sys.executable, "-I", str(tool), "--root", str(fixture),
               "--dataset-id", "fixture_demo", "--module-name", "fixture_demo"]
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "fixture_demo" not in BUILTIN_CATALOG.all_ids()
    runner = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "import cevns_pyeft.experiments as experiments; "
        "experiments.__path__.append(sys.argv[2]); "
        "import pytest; raise SystemExit(pytest.main([sys.argv[3], '-q', '-p', 'no:cacheprovider', '--basetemp=' + sys.argv[4]]))"
    )
    result = subprocess.run([
        sys.executable, "-I", "-c", runner, str(ROOT),
        str(fixture / "cevns_pyeft/experiments"),
        str(fixture / "tests/test_fixture_demo_contract.py"), str(tmp_path / "generated-test-temp"),
    ], cwd=tmp_path, capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "6 passed" in result.stdout
    assert subprocess.run(command, cwd=tmp_path, capture_output=True, env=env).returncode != 0
    for dataset, module in [("CsI2021", "other"), ("Escape", "../escape"), ("Demo", "class")]:
        bad = command[:];bad[-3] = dataset;bad[-1] = module
        assert subprocess.run(bad, cwd=tmp_path, capture_output=True, env=env).returncode != 0


@pytest.mark.parametrize("status,error", [("archived", ArchivedExperimentError),
                                         ("spec_only", SpecOnlyExperimentError)])
def test_engine_compatibility_exports_reject_inactive_ids(monkeypatch, status, error):
    from cevns_pyeft.core import engine
    monkeypatch.setitem(BUILTIN_CATALOG._statuses, "CsI2021", status)
    with pytest.raises(error):
        engine.slow_counts_csi2021("never-read.json")
    with pytest.raises(error):
        engine.build_fast_kernel_csi2021("never-read.json")


def test_archive_real_builtin_keeps_other_experiments_predicting_and_evaluating(monkeypatch):
    import numpy as np
    from cevns_pyeft.experiments.registry import get_experiment, list_experiments
    from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
    from cevns_pyeft.experiments.selection import AnalysisSelection
    baseline = {}
    for dataset in ("CsI2017", "Ar2020"):
        exp = load_experiment(dataset, resources=ROOT)
        numerics = {"n_enu": 8} if dataset == "CsI2017" else {"n_er": 4, "n_enu": 8, "n_pe_bin": 3}
        prediction = predict_experiment(exp, numerics=numerics)
        baseline[dataset] = (prediction.counts, evaluate_experiment(exp, prediction).chi2, numerics)
    monkeypatch.setitem(BUILTIN_CATALOG._statuses, "CsI2021", "archived")
    assert list_experiments(include_specs=False) == ("CsI2017", "Ar2020")
    assert "CsI2021" not in list_experiments(include_specs=True)
    for action in [lambda: get_experiment("CsI2021"),
                   lambda: AnalysisSelection.from_mapping({"datasets": [{"id": "CsI2021", "enabled": False}]})]:
        with pytest.raises(ArchivedExperimentError):
            action()
    for dataset, (counts, chi2, numerics) in baseline.items():
        assert isinstance(get_experiment(dataset), dict)
        exp = load_experiment(dataset, resources=ROOT)
        prediction = predict_experiment(exp, numerics=numerics)
        np.testing.assert_array_equal(prediction.counts, counts)
        assert evaluate_experiment(exp, prediction).chi2 == chi2
