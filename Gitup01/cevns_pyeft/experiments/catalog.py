"""Lazy experiment catalog backed by one manifest and explicit lifecycle states."""
from __future__ import annotations

from dataclasses import replace
from importlib import import_module
from typing import Any

from .manifest import BUILTIN_MANIFEST, VALID_STATUSES, ExperimentManifestEntry


class ExperimentStatusError(KeyError):
    """Base error for IDs known to the catalog but not runtime-loadable."""

    def __init__(self, dataset_id: str, status: str) -> None:
        self.dataset_id = dataset_id
        self.status = status
        super().__init__(f"experiment {dataset_id!r} is registered as {status}; it is not runtime-loadable")


class ArchivedExperimentError(ExperimentStatusError):
    def __init__(self, dataset_id: str) -> None:
        super().__init__(dataset_id, "archived")


class UninstalledExperimentError(ExperimentStatusError):
    def __init__(self, dataset_id):
        super().__init__(dataset_id, "uninstalled")


class SpecOnlyExperimentError(ExperimentStatusError):
    def __init__(self, dataset_id: str) -> None:
        super().__init__(dataset_id, "spec_only")


class ExperimentCatalog:
    """Resolve active definitions while retaining archived/spec-only identities.

    ``builtins=False`` is the supported migration path for a new experiment.
    Custom entries may be active, archived, or spec-only without touching the
    process-global built-in catalog.
    """

    def __init__(self, *, builtins: bool = True):
        self._entries: dict[str, Any] = {}
        self._aliases: dict[str, str] = {}
        self._statuses: dict[str, str] = {}
        self._capabilities: dict[str, tuple[str, ...]] = {}
        self._resource_manifests: dict[str, str | None] = {}
        self._installed = {}
        self._builtins = bool(builtins)
        if builtins:
            for entry in BUILTIN_MANIFEST:
                self.register(
                    entry.dataset_id,
                    entry.definition,
                    aliases=entry.aliases,
                    status=entry.status,
                    capabilities=entry.capabilities,
                    resource_manifest=entry.resource_manifest,
                    installed=entry.installed,
                )

    def register(
        self,
        dataset_id: str,
        definition: Any,
        *,
        aliases: tuple[str, ...] = (),
        status: str = "active",
        capabilities: tuple[str, ...] = (),
        resource_manifest: str | None = None,
        installed: bool = True,
    ) -> "ExperimentCatalog":
        entry = ExperimentManifestEntry(
            str(dataset_id), definition, tuple(aliases), status, tuple(capabilities), resource_manifest, installed
        )
        names = (entry.dataset_id, *entry.aliases)
        if any(name in self._aliases for name in names):
            raise ValueError(f"duplicate dataset or alias: {names}")
        self._entries[entry.dataset_id] = entry.definition
        self._statuses[entry.dataset_id] = entry.status
        self._installed[entry.dataset_id] = entry.installed
        self._capabilities[entry.dataset_id] = entry.capabilities
        self._resource_manifests[entry.dataset_id] = entry.resource_manifest
        self._aliases.update({name: entry.dataset_id for name in names})
        return self

    def unregister(self, dataset_id: str) -> "ExperimentCatalog":
        """Remove a custom entry; built-ins require manifest status changes instead."""
        key = self.canonical_id(dataset_id)
        if self._builtins:
            raise RuntimeError("built-in catalog entries are manifest-owned; use status in manifest")
        self._entries.pop(key, None)
        self._statuses.pop(key, None)
        self._installed.pop(key, None)
        self._capabilities.pop(key, None)
        self._resource_manifests.pop(key, None)
        self._aliases = {alias: value for alias, value in self._aliases.items() if value != key}
        return self

    def canonical_id(self, name: str) -> str:
        raw = str(name).strip()
        try:
            return self._aliases[raw]
        except KeyError as exc:
            raise KeyError(f"unknown dataset {name!r}; available: {self.ids()}") from exc

    def status(self, name: str) -> str:
        return self._statuses[self.canonical_id(name)]

    def manifest_entry(self, name: str) -> ExperimentManifestEntry:
        key = self.canonical_id(name)
        return ExperimentManifestEntry(
            key,
            self._entries[key],
            aliases=tuple(alias for alias, value in self._aliases.items() if value == key and alias != key),
            status=self._statuses[key],
            capabilities=self._capabilities[key],
            resource_manifest=self._resource_manifests[key],
            installed=self._installed[key],
        )

    def ensure_loadable(self, name: str) -> str:
        key = self.canonical_id(name)
        status = self._statuses[key]
        if not self._installed[key]:
            raise UninstalledExperimentError(key)
        if status == "archived":
            raise ArchivedExperimentError(key)
        if status == "spec_only":
            raise SpecOnlyExperimentError(key)
        return key

    def ids(self) -> tuple[str, ...]:
        return tuple(key for key in self._entries if self._statuses[key] == "active" and self._installed[key])

    def archived_ids(self) -> tuple[str, ...]:
        return tuple(key for key in self._entries if self._statuses[key] == "archived")

    def spec_only_ids(self) -> tuple[str, ...]:
        return tuple(key for key in self._entries if self._statuses[key] == "spec_only")

    def all_ids(self) -> tuple[str, ...]:
        return tuple(self._entries)

    def capabilities(self, name: str) -> tuple[str, ...]:
        return self._capabilities[self.canonical_id(name)]

    def definition(self, name: str):
        key = self.ensure_loadable(name)
        entry = self._entries[key]
        value = import_module("." + entry, __package__).DEFINITION if isinstance(entry, str) else entry
        if value.dataset_id != key:
            raise ValueError(f"registered identity {key!r} differs from definition {value.dataset_id!r}")
        return value

    def describe(self):
        return {key: self.definition(key).describe() for key in self.ids()}


BUILTIN_CATALOG = ExperimentCatalog()


def list_runtime_experiments() -> tuple[str, ...]:
    return BUILTIN_CATALOG.ids()


def list_archived_experiments() -> tuple[str, ...]:
    return BUILTIN_CATALOG.archived_ids()


def list_spec_only_experiments() -> tuple[str, ...]:
    return BUILTIN_CATALOG.spec_only_ids()


__all__ = [
    "ArchivedExperimentError",
    "BUILTIN_CATALOG",
    "ExperimentCatalog",
    "ExperimentStatusError",
    "SpecOnlyExperimentError",
    "UninstalledExperimentError",
    "list_archived_experiments",
    "list_runtime_experiments",
    "list_spec_only_experiments",
]
