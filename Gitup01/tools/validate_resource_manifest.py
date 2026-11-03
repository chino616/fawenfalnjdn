#!/usr/bin/env python3
"""Audit resource_manifest.json against definitions and ResourceCatalog semantics."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read resource manifest {path}: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("resources"), list):
        raise SystemExit(f"resource manifest must contain a resources list: {path}")
    return value


def audit(root: Path, manifest_path: Path, datasets: list[str] | None = None) -> dict[str, Any]:
    from cevns_pyeft.experiments.catalog import BUILTIN_CATALOG
    from cevns_pyeft.experiments.loader import ResourceCatalog, load_experiment
    from cevns_pyeft.foundation.resources import ALIASES, resolve_resource

    root = Path(root).resolve()

    manifest = _load_json(manifest_path)
    entries = manifest["resources"]
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    errors: list[str] = []
    warnings: list[str] = []
    for raw in entries:
        if not isinstance(raw, dict) or not raw.get("dataset_id") or not raw.get("resource_id"):
            errors.append(f"invalid resource entry: {raw!r}")
            continue
        key = (str(raw["dataset_id"]), str(raw["resource_id"]))
        if key in by_key:
            errors.append(f"duplicate manifest resource entry: {key!r}")
        by_key[key] = raw

    manifest_datasets = {key[0] for key in by_key}
    requested = tuple(datasets or sorted(manifest_datasets | set(BUILTIN_CATALOG.ids())))
    selected_list = []
    for name in requested:
        try:
            selected_list.append(BUILTIN_CATALOG.ensure_loadable(name))
        except KeyError as exc:
            errors.append(f"unknown or non-active requested dataset {name!r}: {exc}")
    selected = tuple(dict.fromkeys(selected_list))
    reports: list[dict[str, Any]] = []
    referenced: set[tuple[str, str]] = set()
    definitions = []

    if not root.is_absolute():
        errors.append("resource root must be an absolute path for isolated/wheel validation")
    if not (root / "data").is_dir():
        errors.append(f"resource root does not contain data/: {root}")

    for dataset_id in selected:
        try:
            definition = BUILTIN_CATALOG.definition(dataset_id)
        except Exception as exc:
            if dataset_id in manifest_datasets:
                errors.append(f"manifest references unknown or non-active dataset {dataset_id!r}: {exc}")
            continue
        definitions.append(definition)
        for ref in definition.resources:
            key = (definition.dataset_id, ref.id)
            referenced.add(key)
            entry = by_key.get(key)
            item: dict[str, Any] = {
                "dataset_id": definition.dataset_id,
                "resource_id": ref.id,
                "role": ref.role,
                "definition_path": ref.path,
                "canonical_path": entry.get("canonical_path") if entry else None,
                "external_resource_root": str(root),
                "expected_sha256": entry.get("sha256") if entry else None,
                "legacy_paths": list(entry.get("legacy_paths", [])) if entry else [],
                "statistics_lazy": ref.role == "statistics",
            }
            if entry is None:
                errors.append(f"definition resource missing from manifest: {key!r}")
                item["status"] = "missing_manifest_entry"
                reports.append(item)
                continue
            canonical = str(entry.get("canonical_path", ""))
            if canonical != ref.path:
                errors.append(f"definition/manifest canonical path mismatch for {key!r}: {ref.path!r} != {canonical!r}")
            canonical_abs = (root / canonical).resolve()
            try:
                resolved = ResourceCatalog(root).for_definition(definition).path_for(ref)
            except Exception as exc:
                errors.append(f"resource alias resolution failed for {key!r}: {exc}")
                resolved = canonical_abs
            item["canonical_exists"] = canonical_abs.is_file()
            item["resolved_path"] = str(resolved)
            item["resolved_legacy_path"] = str(resolved) if resolved != canonical_abs and resolved.is_file() else None
            item["alias_reason"] = (
                "canonical path present"
                if canonical_abs.is_file()
                else "canonical path absent; finite legacy alias resolved"
                if resolved.is_file()
                else "canonical path and legacy aliases absent"
            )
            item["resolved_exists"] = resolved.is_file()
            item["hash_match"] = False
            if not resolved.is_file():
                errors.append(f"missing resource for {key!r}: {resolved}")
            else:
                actual_hash = _sha256(resolved)
                item["actual_sha256"] = actual_hash
                item["hash_match"] = actual_hash == entry.get("sha256")
                if not item["hash_match"]:
                    errors.append(f"sha256 mismatch for {key!r}: {actual_hash} != {entry.get('sha256')}")
            alias_reports = []
            for legacy in item["legacy_paths"]:
                try:
                    legacy_abs = resolve_resource(root, legacy)
                except (OSError, ValueError) as exc:
                    errors.append(f"legacy alias resolution failed for {key!r}: {exc}")
                    continue
                alias_reports.append({
                    "legacy_path": legacy,
                    "resolved_path": str(legacy_abs),
                    "exists": legacy_abs.is_file(),
                    "same_resource": legacy_abs.is_file() and resolved.is_file() and _sha256(legacy_abs) == _sha256(resolved),
                    "alias_reason": "foundation.resources finite alias" if legacy in ALIASES else "manifest-declared alias",
                })
                if not legacy_abs.is_file():
                    warnings.append(f"legacy alias is not present for {key!r}: {legacy}")
                elif resolved.is_file() and _sha256(legacy_abs) != _sha256(resolved):
                    errors.append(f"legacy alias content differs for {key!r}: {legacy}")
            item["legacy_resolution"] = alias_reports
            item["status"] = "ok" if item["resolved_exists"] and item["hash_match"] else "blocked"
            reports.append(item)

        # Loading must resolve physical resources without touching statistics.
        try:
            prepared = load_experiment(definition.dataset_id, resources=ResourceCatalog(root))
            item = next((x for x in reports if x["dataset_id"] == definition.dataset_id), None)
            stat_ids = {ref.id for ref in definition.resources if ref.role == "statistics"}
            resolved_ids = set(prepared.resolved_resources)
            if stat_ids & resolved_ids:
                errors.append(f"statistics resource eagerly resolved for {definition.dataset_id}: {sorted(stat_ids & resolved_ids)}")
            if item is not None:
                item.setdefault("loader_check", {})["prediction_load_passed"] = True
                item["loader_check"]["statistics_deferred"] = not bool(stat_ids & resolved_ids)
        except Exception as exc:
            errors.append(f"load_experiment resource check failed for {definition.dataset_id}: {type(exc).__name__}: {exc}")

    # Every manifest resource should either be used by an active definition or be
    # explicitly reported as legacy/unknown instead of silently becoming active.
    considered = set(by_key) if datasets is None else {key for key in by_key if key[0] in selected}
    unknown_entries = sorted(considered - referenced)
    for key in unknown_entries:
        raw = by_key[key]
        errors.append(f"unknown or unused active manifest dataset/resource: {key!r}")
    ambiguous_ids: dict[str, set[str]] = defaultdict(set)
    for definition in definitions:
        for ref in definition.resources:
            ambiguous_ids[ref.id].add(ref.path)
    ambiguous_overrides = sorted(resource_id for resource_id, paths in ambiguous_ids.items() if len(paths) > 1)
    override_checks = []
    for resource_id in ambiguous_overrides:
        scoped = {
            (definition.dataset_id, ref.id): root / ref.path
            for definition in definitions for ref in definition.resources if ref.id == resource_id
        }
        try:
            ResourceCatalog(root, {resource_id: root / "unused"}).validate(definitions)
        except KeyError:
            unscoped_rejected = True
        else:
            unscoped_rejected = False
            errors.append(f"ambiguous unscoped override was accepted: {resource_id}")
        try:
            ResourceCatalog(root, scoped).validate(definitions)
            scoped_accepted = True
        except KeyError as exc:
            scoped_accepted = False
            errors.append(f"scoped overrides were rejected for {resource_id}: {exc}")
        override_checks.append({"resource_id": resource_id,
                               "unscoped_rejected": unscoped_rejected,
                               "scoped_accepted": scoped_accepted})
        warnings.append(f"resource ID {resource_id!r} requires (dataset_id, resource_id) overrides")

    # Check that every manifest top-level alias points to a known canonical path.
    alias_map = manifest.get("legacy_aliases", {})
    if isinstance(alias_map, dict):
        for legacy, canonical in alias_map.items():
            target = (root / str(canonical)).resolve()
            try:
                resolved = resolve_resource(root, legacy)
            except (OSError, ValueError) as exc:
                errors.append(f"top-level alias resolution failed: {legacy}: {exc}")
                continue
            if resolved.is_file() and target.is_file() and _sha256(resolved) != _sha256(target):
                errors.append(f"top-level alias hash mismatch: {legacy} -> {canonical}")

    return {
        "status": "PASS" if not errors else "BLOCKED",
        "root": str(root),
        "manifest": str(manifest_path.resolve()),
        "datasets": list(selected),
        "resources": reports,
        "unknown_or_unused_manifest_entries": [list(key) for key in unknown_entries],
        "ambiguous_override_resource_ids": ambiguous_overrides,
        "override_scope_checks": override_checks,
        "checks": {
            "definition_paths_reused": True,
            "resource_catalog_reused": True,
            "statistics_independent_and_deferred": all(item.get("statistics_lazy", False) or item.get("loader_check", {}).get("statistics_deferred", True) for item in reports),
            "cwd_independent_absolute_root": root.is_absolute(),
            "external_root_contract": (root / "data").is_dir(),
            "canonical_legacy_aliases_compared": True,
        },
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="directory containing data/")
    parser.add_argument("--dataset", action="append", dest="datasets", help="limit audit to one or more active dataset IDs")
    parser.add_argument("--manifest", type=Path, help="resource manifest path; defaults to ROOT/data/resource_manifest.json")
    parser.add_argument("--json-out", type=Path, help="write the JSON report to this path")
    args = parser.parse_args(argv)
    # Use this tool's source checkout (or the installed package), not the data root.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    root = args.root.resolve()
    manifest = (args.manifest if args.manifest is not None else root / "data" / "resource_manifest.json").resolve()
    result = audit(root, manifest, args.datasets)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
