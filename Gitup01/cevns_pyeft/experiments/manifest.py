"""Runtime dataclass view of the single persistent dataset_registry.json.

The registry owns identity, lifecycle, version and file/dependency declarations.
This module preserves the existing Python manifest and Catalog API.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


VALID_STATUSES = ("active", "archived", "spec_only")


@dataclass(frozen=True)
class ExperimentManifestEntry:
    dataset_id: str
    definition: Any
    aliases: tuple[str, ...] = ()
    status: str = "active"
    capabilities: tuple[str, ...] = ()
    resource_manifest: str | None = None
    installed: bool = True

    def __post_init__(self) -> None:
        dataset_id = str(self.dataset_id).strip()
        if not dataset_id:
            raise ValueError("manifest dataset_id must be non-empty")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"unsupported manifest status {self.status!r}")
        if type(self.installed) is not bool or (not self.installed and self.status == "active"):
            raise ValueError("an uninstalled dataset cannot be active")
        aliases = tuple(str(alias).strip() for alias in self.aliases)
        if any(not alias for alias in aliases):
            raise ValueError(f"manifest aliases must be non-empty: {self.dataset_id!r}")
        if len(set((dataset_id, *aliases))) != len((dataset_id, *aliases)):
            raise ValueError(f"duplicate manifest dataset or alias: {dataset_id!r}")
        capabilities = tuple(str(capability).strip() for capability in self.capabilities)
        if any(not capability for capability in capabilities):
            raise ValueError(f"manifest capabilities must be non-empty: {dataset_id!r}")
        object.__setattr__(self, "dataset_id", dataset_id)
        object.__setattr__(self, "aliases", aliases)
        object.__setattr__(self, "capabilities", capabilities)
        if self.resource_manifest is not None:
            object.__setattr__(self, "resource_manifest", str(self.resource_manifest))


from pathlib import Path
from .registry_io import read_registry

# Identity and lifecycle have one authority: this installed registry resource.
# Ownership metadata in the same entries is consumed only by explicit management.
_REGISTRY = read_registry(Path(__file__).resolve().parents[2])
BUILTIN_MANIFEST = tuple(ExperimentManifestEntry(
    dataset_id=e['dataset_id'], definition=e['definition'], aliases=tuple(e.get('aliases',())),
    status=e['status'], capabilities=tuple(e.get('capabilities',())),
    resource_manifest=e.get('resource_manifest'), installed=e['installed'])
    for e in _REGISTRY['datasets'])


def manifest_entries(*, status: str | None = None) -> tuple[ExperimentManifestEntry, ...]:
    if status is not None and status not in VALID_STATUSES:
        raise ValueError(f"unsupported manifest status {status!r}")
    return tuple(entry for entry in BUILTIN_MANIFEST if status is None or entry.status == status)


__all__ = ["BUILTIN_MANIFEST", "ExperimentManifestEntry", "VALID_STATUSES", "manifest_entries"]
