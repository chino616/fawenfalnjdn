from __future__ import annotations

from pathlib import Path

from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
from cevns_pyeft.experiments.manifest import BUILTIN_MANIFEST, VALID_STATUSES

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_catalog_and_registry_have_one_active_id_set():
    assert tuple(entry.dataset_id for entry in BUILTIN_MANIFEST if entry.status == "active") == BUILTIN_CATALOG.ids()
    assert set(entry.status for entry in BUILTIN_MANIFEST) <= set(VALID_STATUSES)


def test_resource_validator_reuses_catalog_and_passes_csi2021():
    from tools.validate_resource_manifest import audit

    result = audit(ROOT, ROOT / "data" / "resource_manifest.json", ["CsI2021"])
    assert result["status"] == "PASS"
    assert result["checks"]["resource_catalog_reused"] is True
    assert result["checks"]["statistics_independent_and_deferred"] is True
