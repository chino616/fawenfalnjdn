"""Produce a reviewable diff and change list in a checkout without Git metadata."""
from pathlib import Path
import difflib
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]


def main():
    output = ROOT / "outputs/refactor"
    metadata = json.loads((ROOT / "tests/reference/interface_refactor_v1/metadata.json").read_text(encoding="utf-8"))
    changed, unchanged, removed, diff = [], [], [], []
    for original in sorted((output / "original").rglob("*")):
        if not original.is_file():
            continue
        relative = original.relative_to(output / "original")
        current = ROOT / relative
        if not current.is_file():
            removed.append(relative.as_posix())
            continue
        if original.read_bytes() != current.read_bytes():
            changed.append(relative.as_posix())
            diff.extend(difflib.unified_diff(original.read_text(encoding="utf-8").splitlines(keepends=True),
                current.read_text(encoding="utf-8").splitlines(keepends=True),
                fromfile="before/" + relative.as_posix(), tofile="after/" + relative.as_posix()))
        else:
            unchanged.append(relative.as_posix())
    new_files = [p for folder in ("src", "tests", "tools/refactor", "docs/interface_refactor")
        for p in sorted((ROOT / folder).rglob("*")) if p.is_file() and "__pycache__" not in p.parts
        and p.suffix in (".py", ".md", ".npz", ".json") and p.relative_to(ROOT).as_posix() not in metadata["hashes"]]
    for path in new_files:
        if path.suffix in (".py", ".md"):
            diff.extend(difflib.unified_diff([], path.read_text(encoding="utf-8").splitlines(keepends=True),
                fromfile="/dev/null", tofile="after/" + path.relative_to(ROOT).as_posix()))
    data_changes = [name for name, sha in metadata["hashes"].items() if name.startswith("data/")
                    and (not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha)]
    source_changes_without_original = [name for name, sha in metadata["hashes"].items()
        if name.startswith("src/") and (not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha)
        and name not in changed]
    manifest = {"modified": changed, "added": [p.relative_to(ROOT).as_posix() for p in new_files],
                "removed": removed, "unchanged_review_originals": unchanged,
                "experiment_data_changes": data_changes, "source_changes_without_review_original": source_changes_without_original}
    (output / "changes.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (output / "review.diff").write_text("".join(diff), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)
    if data_changes or source_changes_without_original or removed:
        raise SystemExit("Unexpected scope changes; inspect changes.json")


if __name__ == "__main__":
    main()
