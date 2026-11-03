"""Single source of truth for built-in experiment registration metadata.

The first migration stage deliberately keeps this as a small Python manifest.  It
can later be serialized without changing the public Catalog API.
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

    def __post_init__(self) -> None:
        dataset_id = str(self.dataset_id).strip()
        if not dataset_id:
            raise ValueError("manifest dataset_id must be non-empty")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"unsupported manifest status {self.status!r}")
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


# Keep the existing IDs, aliases, and definition modules exactly as they were.
BUILTIN_MANIFEST: tuple[ExperimentManifestEntry, ...] = (
    ExperimentManifestEntry(
        "CsI2021",
        "coherent.csi2021_definition",
        aliases=("csi2021",),
        capabilities=("slow", "fast", "statistics"),
        resource_manifest="data/resource_manifest.json",
    ),
    ExperimentManifestEntry(
        "CsI2017",
        "coherent.csi2017_definition",
        aliases=("csi2017",),
        capabilities=("slow", "fast", "statistics"),
        resource_manifest="data/resource_manifest.json",
    ),
    ExperimentManifestEntry(
        "Ar2020",
        "coherent.ar2020_definition",
        aliases=("ar2020",),
        capabilities=("slow", "fast", "statistics"),
        resource_manifest="data/resource_manifest.json",
    ),
)


def manifest_entries(*, status: str | None = None) -> tuple[ExperimentManifestEntry, ...]:
    if status is not None and status not in VALID_STATUSES:
        raise ValueError(f"unsupported manifest status {status!r}")
    return tuple(entry for entry in BUILTIN_MANIFEST if status is None or entry.status == status)


__all__ = ["BUILTIN_MANIFEST", "ExperimentManifestEntry", "VALID_STATUSES", "manifest_entries"]
