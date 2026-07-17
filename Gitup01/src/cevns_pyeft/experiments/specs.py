from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REQUIRED_EXPERIMENT_SPEC_FIELDS = ("dataset_name", "source_type", "target_mode")


@dataclass(frozen=True)
class ExperimentSpec:
    dataset_name: str
    source_type: str
    target_mode: str
    path: Path
    data: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        out = dict(self.data)
        out["_spec_path"] = str(self.path)
        return out


def repo_root_from_module() -> Path:
    return Path(__file__).resolve().parents[3]


def experiment_data_root(root: str | Path | None = None) -> Path:
    base = Path(root) if root is not None else repo_root_from_module()
    return base / "data" / "experiments"


def discover_experiment_spec_paths(root: str | Path | None = None) -> tuple[Path, ...]:
    data_root = experiment_data_root(root)
    if not data_root.exists():
        return ()
    return tuple(sorted(data_root.glob("*/experiment.yaml")))


def list_spec_experiment_names(root: str | Path | None = None) -> tuple[str, ...]:
    names: list[str] = []
    for path in discover_experiment_spec_paths(root):
        data = read_simple_yaml(path)
        name = str(data.get("dataset_name") or path.parent.name).strip()
        if name:
            names.append(name)
    return tuple(names)


def load_experiment_spec(name_or_path: str | Path, root: str | Path | None = None) -> ExperimentSpec:
    path = resolve_experiment_spec_path(name_or_path, root)
    data = read_simple_yaml(path)
    validate_experiment_spec_data(data, path)
    return ExperimentSpec(
        dataset_name=str(data["dataset_name"]),
        source_type=str(data["source_type"]),
        target_mode=str(data["target_mode"]),
        path=path,
        data=data,
    )


def resolve_experiment_spec_path(name_or_path: str | Path, root: str | Path | None = None) -> Path:
    raw = Path(name_or_path)
    if raw.suffix.lower() in {".yaml", ".yml"} or raw.is_absolute():
        path = raw if raw.is_absolute() else Path.cwd() / raw
        if path.exists():
            return path.resolve()
        raise FileNotFoundError(path)

    key = str(name_or_path).strip()
    for path in discover_experiment_spec_paths(root):
        data = read_simple_yaml(path)
        if key in {path.parent.name, str(data.get("dataset_name", "")).strip()}:
            return path.resolve()
    available = list_spec_experiment_names(root)
    raise KeyError(f"Unknown experiment spec {name_or_path!r}. Available specs: {list(available)}")


def validate_experiment_spec_data(data: dict[str, Any], path: str | Path | None = None) -> None:
    missing = [field for field in REQUIRED_EXPERIMENT_SPEC_FIELDS if field not in data or data[field] in ("", None)]
    if missing:
        where = f" in {path}" if path is not None else ""
        raise ValueError(f"Missing required experiment spec fields{where}: {missing}")


def read_simple_yaml(path: str | Path) -> dict[str, Any]:
    """Read the small YAML subset used by bundled experiment specs.

    This avoids adding a PyYAML dependency to the split-minimal package. It
    supports top-level key/value pairs, one-level nested maps, inline lists,
    quoted strings, booleans, nulls, and numeric scalars.
    """
    result: dict[str, Any] = {}
    current_map_key: str | None = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if indent == 0:
            if value == "":
                result[key] = {}
                current_map_key = key
            else:
                result[key] = parse_yaml_scalar(value)
                current_map_key = None
        elif current_map_key is not None and isinstance(result.get(current_map_key), dict):
            result[current_map_key][key] = parse_yaml_scalar(value)
    return result


def parse_yaml_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "None", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_yaml_scalar(part.strip()) for part in inner.split(",")]
    try:
        if any(mark in value for mark in (".", "e", "E")):
            return float(value)
        return int(value)
    except ValueError:
        return value


def required_input_fields(data: dict[str, Any]) -> tuple[str, ...]:
    found: list[str] = []
    for key, value in walk_items(data):
        if isinstance(value, str) and "REQUIRES_INPUT" in value:
            found.append(key)
        elif value in ("", None):
            found.append(key)
    return tuple(found)


def walk_items(data: dict[str, Any], prefix: str = "") -> Iterable[tuple[str, Any]]:
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            yield from walk_items(value, name)
        else:
            yield name, value


__all__ = [
    "ExperimentSpec",
    "REQUIRED_EXPERIMENT_SPEC_FIELDS",
    "discover_experiment_spec_paths",
    "experiment_data_root",
    "list_spec_experiment_names",
    "load_experiment_spec",
    "parse_yaml_scalar",
    "read_simple_yaml",
    "required_input_fields",
    "resolve_experiment_spec_path",
    "validate_experiment_spec_data",
]
