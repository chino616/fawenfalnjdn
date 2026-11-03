#!/usr/bin/env python3
"""Create a minimal custom-catalog experiment migration skeleton.

The scaffold intentionally does not modify the built-in manifest. A new
experiment starts in an isolated ``ExperimentCatalog(builtins=False)`` and is
promoted only after its Slow contract, resource audit, and validation pass.
"""
from __future__ import annotations

import argparse
import keyword
import re
import sys
from pathlib import Path

DATASET_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
MODULE_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _validate_name(value: str, pattern: re.Pattern[str], label: str) -> str:
    value = value.strip()
    if not pattern.fullmatch(value) or keyword.iskeyword(value):
        raise SystemExit(f"invalid {label} {value!r}; use ASCII letters, digits, and underscores")
    return value


def _definition(dataset_id: str, module_name: str) -> str:
    class_name = "".join(part.capitalize() for part in module_name.split("_")) + "Settings"
    return f'''"""Definition skeleton for the custom-catalog experiment {dataset_id}."""
from __future__ import annotations

from dataclasses import dataclass

from cevns_pyeft.experiments.definition import ExperimentDefinition, ObservationDefinition
from .execution import prepare


@dataclass(frozen=True)
class {class_name}:
    """Runnable default configuration for the migration contract.

    The generated executor is a deterministic Slow fixture, not a physics
    result. Replace the component values and executor with the approved
    experiment implementation before promotion to the built-in manifest.
    """

    implementation_modules: tuple[str, ...] = (
        "cevns_pyeft.experiments.{module_name}.execution",
    )


DEFINITION = ExperimentDefinition(
    dataset_id={dataset_id!r},
    experiment_slug={module_name!r},
    analysis_revision="draft_v1",
    run_refs=("replace_with_approved_run",),
    physical={class_name}(),
    observation=ObservationDefinition("replace observable", "replace unit", (0.0, 1.0)),
    resources=(),
    numerical_profiles={{"slow": {{}}}},
    prepare=prepare,
    statistics=None,
    capabilities={{
        "slow": "runnable deterministic migration fixture; replace with approved physics",
        "fast": "unsupported",
        "statistics": "unavailable until independently audited",
        "legacy": "unsupported",
    }},
    validation=("tests/test_{module_name}_contract.py",),
)
'''


def _execution(dataset_id: str) -> str:
    return f'''"""Runnable Slow migration fixture for {dataset_id}.

This module exists so the scaffold's contract tests exercise the real loader,
selection, prediction, statistics boundary, unsupported-Fast boundary, and
component fingerprint path. It intentionally produces a deterministic toy
prediction and must be replaced or extended with approved physics before the
experiment is promoted to the built-in manifest.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cevns_pyeft.contracts import Prediction
from cevns_pyeft.contracts.observation import Axis, Binning
from cevns_pyeft.experiments.definition import plain


@dataclass(frozen=True)
class DemoComponent:
    kind: str
    version: str = "fixture_v1"

    def describe(self):
        return {{"kind": self.kind, "version": self.version}}


@dataclass(frozen=True)
class DemoModel:
    source: DemoComponent
    interaction: DemoComponent
    observation: DemoComponent
    target: DemoComponent

    def describe(self):
        return plain(self)


class DemoExecutor:
    supports_state_parameters = False

    def describe_execution(self, model):
        return {{"strategy": "scaffold_slow_fixture_v1", "model": model.describe()}}

    def __call__(self, exp, point, backend, numerics, kernel):
        if backend != "slow":
            raise ValueError(f"{{exp.dataset_id}}: unsupported backend {{backend!r}}")
        if kernel is not None:
            raise ValueError("the scaffold Slow fixture does not consume a Fast kernel")
        edges = np.asarray(exp.definition.observation.edges, dtype=float)
        counts = np.ones(edges.size - 1, dtype=float)
        if not point.include_sm:
            counts *= 0.5
        binning = Binning((Axis(exp.definition.observation.name, exp.definition.observation.unit, edges),))
        components = {{("fixture", "target"): counts}}
        prediction = Prediction(
            counts,
            binning,
            components,
            normalization_record={{"fixture": True}},
            model_record={{"dataset_id": exp.dataset_id}},
            numerical_record=numerics,
        )
        return prediction, {{"detector": prediction}}, None, {{"strategy": "scaffold_slow_fixture_v1"}}


def prepare(definition, resources):
    return DemoModel(
        source=DemoComponent("source"),
        interaction=DemoComponent("interaction"),
        observation=DemoComponent("observation"),
        target=DemoComponent("target"),
    ), DemoExecutor()
'''


def _resources(dataset_id: str) -> str:
    return f'''# Resource declaration template for {dataset_id}.
# Paths are resolved relative to an explicit ResourceCatalog root.
dataset_id: {dataset_id}
resources: []
# Example:
# - id: detector_efficiency
#   path: data/experiments/<experiment_slug>/{dataset_id}/detector/efficiency.txt
#   role: physical
#   semantic: approved detector efficiency table
'''


def _capabilities(dataset_id: str) -> str:
    return f'''# Capability declaration template for {dataset_id}.
dataset_id: {dataset_id}
status: custom_catalog_only
slow:
  declared: true
  implemented: true
  implementation: deterministic migration fixture only; replace before promotion
fast:
  declared: false
  implemented: false
statistics:
  declared: false
  implemented: false
legacy:
  declared: false
  implemented: false
promotion_requirements:
  - custom catalog registration
  - explicit ResourceCatalog resolution
  - Slow prediction contract
  - observation axes, units, and bin-edge validation
  - explicit missing-statistics behavior
  - explicit unsupported-Fast behavior
'''


def _test(dataset_id: str, module_name: str) -> str:
    return f'''from __future__ import annotations

import pytest

from cevns_pyeft.experiments.catalog import ExperimentCatalog
from cevns_pyeft.experiments.definition import digest
from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
from cevns_pyeft.experiments.runtime import evaluate_experiment, predict_experiment, predict_selection
from cevns_pyeft.experiments.selection import AnalysisSelection
from cevns_pyeft.experiments.{module_name}.definition import DEFINITION
from cevns_pyeft.experiments.{module_name}.execution import DemoComponent


def test_{module_name}_can_start_in_custom_catalog():
    catalog = ExperimentCatalog(builtins=False).register(
        DEFINITION.dataset_id,
        DEFINITION,
        aliases=(DEFINITION.dataset_id.lower(),) if DEFINITION.dataset_id.lower() != DEFINITION.dataset_id else (),
        capabilities=("slow",),
    )
    assert catalog.ids() == ({dataset_id!r},)
    assert catalog.definition(DEFINITION.dataset_id).dataset_id == {dataset_id!r}
    assert catalog.status(DEFINITION.dataset_id) == "active"


def test_{module_name}_definition_has_identity_and_observation_contract():
    assert DEFINITION.dataset_id == {dataset_id!r}
    assert DEFINITION.observation.edges[0] < DEFINITION.observation.edges[-1]
    assert digest(DEFINITION.observation)
    resources = ResourceCatalog(".").for_definition(DEFINITION)
    assert resources.dataset_id == {dataset_id!r}


def _catalog():
    return ExperimentCatalog(builtins=False).register(
        DEFINITION.dataset_id,
        DEFINITION,
        aliases=(DEFINITION.dataset_id.lower(),) if DEFINITION.dataset_id.lower() != DEFINITION.dataset_id else (),
        capabilities=("slow",),
    )


def test_{module_name}_load_predict_and_selection_contract(tmp_path):
    catalog = _catalog()
    experiment = load_experiment(DEFINITION.dataset_id, resources=ResourceCatalog(tmp_path), registry=catalog)
    prediction = predict_experiment(experiment, backend="slow")
    assert prediction.dataset_id == DEFINITION.dataset_id
    assert prediction.counts.shape == (len(DEFINITION.observation.edges) - 1,)
    axis = prediction.combined_prediction.axes[0]
    assert (axis.name, axis.unit) == (DEFINITION.observation.name, DEFINITION.observation.unit)
    assert tuple(axis.edges) == DEFINITION.observation.edges
    assert prediction.physics_fingerprint == experiment.physics_fingerprint
    assert prediction.analysis_fingerprint == experiment.analysis_fingerprint

    selected = AnalysisSelection.from_mapping(
        {{"datasets": [{{"id": DEFINITION.dataset_id, "backend": "slow"}}]}},
        registry=catalog,
    )
    assert DEFINITION.dataset_id in predict_selection(selected, resources=ResourceCatalog(tmp_path), registry=catalog)
    disabled = AnalysisSelection.from_mapping(
        {{"datasets": [{{"id": DEFINITION.dataset_id, "enabled": False}}]}},
        registry=catalog,
    )
    assert predict_selection(disabled, resources=ResourceCatalog(tmp_path), registry=catalog) == {{}}


def test_{module_name}_statistics_and_fast_boundaries_are_explicit(tmp_path):
    catalog = _catalog()
    experiment = load_experiment(DEFINITION.dataset_id, resources=ResourceCatalog(tmp_path), registry=catalog)
    prediction = predict_experiment(experiment)
    with pytest.raises(ValueError, match="statistics unavailable"):
        evaluate_experiment(experiment, prediction)
    with pytest.raises(ValueError, match="unsupported backend"):
        predict_experiment(experiment, backend="fast")


def test_{module_name}_component_replacement_changes_identity_and_is_consumed(tmp_path):
    catalog = _catalog()
    baseline = load_experiment(DEFINITION.dataset_id, resources=ResourceCatalog(tmp_path), registry=catalog)
    changed = load_experiment(
        DEFINITION.dataset_id,
        resources=ResourceCatalog(tmp_path),
        registry=catalog,
        components={{"source": DemoComponent("source", "fixture_v2")}},
    )
    assert changed.physics_fingerprint != baseline.physics_fingerprint
    assert changed.describe()["actual_model"]["source"]["version"] == "fixture_v2"
    assert predict_experiment(changed).dataset_id == DEFINITION.dataset_id


def test_{module_name}_slow_and_statistics_boundaries_are_explicit(tmp_path):
    catalog = _catalog()
    experiment = load_experiment(DEFINITION.dataset_id, resources=ResourceCatalog(tmp_path), registry=catalog)
    assert DEFINITION.statistics is None
    assert "fast" not in DEFINITION.numerical_profiles
    assert predict_experiment(experiment).counts.size == len(DEFINITION.observation.edges) - 1
'''


def scaffold(root: Path, dataset_id: str, module_name: str) -> list[Path]:
    dataset_id = _validate_name(dataset_id, DATASET_RE, "dataset ID")
    module_name = _validate_name(module_name, MODULE_RE, "module name")
    from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
    if dataset_id in BUILTIN_CATALOG.all_ids():
        raise SystemExit(f"dataset ID already exists in the built-in catalog: {dataset_id}")
    package_dir = root / "cevns_pyeft" / "experiments" / module_name
    test_path = root / "tests" / f"test_{module_name}_contract.py"
    if package_dir.exists():
        raise SystemExit(f"target directory already exists: {package_dir}")
    if test_path.exists():
        raise SystemExit(f"target test already exists: {test_path}")
    package_dir.mkdir(parents=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    outputs = {
        package_dir / "__init__.py": f'''"""Custom-catalog scaffold for {dataset_id}."""\nfrom .definition import DEFINITION\n\n__all__ = ["DEFINITION"]\n''',
        package_dir / "definition.py": _definition(dataset_id, module_name),
        package_dir / "execution.py": _execution(dataset_id),
        package_dir / "resources.yaml": _resources(dataset_id),
        package_dir / "capabilities.yaml": _capabilities(dataset_id),
        test_path: _test(dataset_id, module_name),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    return list(outputs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--module-name", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    dataset_id = _validate_name(args.dataset_id, DATASET_RE, "dataset ID")
    module_name = _validate_name(args.module_name, MODULE_RE, "module name")
    root = args.root.resolve()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    paths = scaffold(root, dataset_id, module_name)
    print(f"created custom-catalog scaffold for {dataset_id}")
    for path in paths:
        print(path.relative_to(root))
    print("next: implement and test it with ExperimentCatalog(builtins=False); do not add it to the active manifest yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
