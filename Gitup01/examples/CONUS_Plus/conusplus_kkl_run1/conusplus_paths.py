"""Repository-local paths for the two distinct CONUS+ benchmark methods.

This module only locates files and verifies input identity. It does not change
the source, detector, interaction, numerical quadrature or statistical model.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / "pyproject.toml").is_file() and (p / "cevns_pyeft").is_dir())
sys.path.insert(0, str(ROOT))
DATASET = "conusplus_kkl_run1"
EXAMPLES = Path(__file__).resolve().parent


class Layout:
    def __init__(self, method):
        if method not in ("sm", "nsi"):
            raise ValueError("method must be sm or nsi")
        self.method = method
        self.root = ROOT
        self.tag = f"{method}_response_20261106"
        self.code = EXAMPLES / f"{method}_response"
        self.canonical_output = ROOT / "outputs/CONUS_Plus" / DATASET / self.tag
        self.canonical_review = ROOT / "workflows/cevns-pyeft/runs/CONUS_Plus" / DATASET / "benchmarks" / self.tag
        self.canonical_data = ROOT / "data/benchmarks/CONUS_Plus" / DATASET / self.tag
        self.canonical_document = ROOT / "docs/experiments/CONUS_Plus/datasets" / DATASET / "benchmarks" / self.tag
        self.output = Path(os.environ.get("CEVNS_CONUS_OUTPUT", self.canonical_output)).resolve()
        self.review = Path(os.environ.get("CEVNS_CONUS_REVIEW", self.canonical_review)).resolve()
        self.data = Path(os.environ.get("CEVNS_CONUS_RUN_DATA", self.canonical_data)).resolve()
        self.document = Path(os.environ.get("CEVNS_CONUS_DOCUMENT", self.canonical_document)).resolve()
        self.report = self.document / f"{method.upper()}_BENCHMARK.md"
        self.sm_output = ROOT / "outputs/CONUS_Plus" / DATASET / "sm_response_20261106"

    def path(self, value):
        """Resolve the original run's explicit logical paths by responsibility."""
        value = Path(value)
        if value.is_absolute():
            return value
        parts = value.parts
        if not parts:
            return self.code
        head, tail = parts[0], Path(*parts[1:])
        if head == "snapshot":
            return ROOT / tail
        if head == "outputs":
            return self.output / tail
        if head == "review":
            if tail.name in ("SM_BENCHMARK_REPORT_V1.md", "NSI_BENCHMARK_REPORT_V1.md"):
                return self.report
            return self.review / tail
        if head == "data":
            if len(parts) > 1 and parts[1] == "sm_reference":
                return self.sm_output / Path(*parts[2:])
            return self.data / tail
        return self.code / value

    def verify_inputs(self):
        """Verify the adopted current resources; old manifests remain evidence."""
        path = EXAMPLES / "LOCAL_INPUTS.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        errors = []
        for name, expected in record["files"].items():
            target = (ROOT / name).resolve()
            if not target.is_relative_to(ROOT):
                raise ValueError("Input path escapes Gitup01: " + name)
            actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
            if actual != expected:
                errors.append(name)
        if errors:
            raise ValueError("Adopted benchmark input changed; review and start a new version: " + repr(errors))
        return {"files_checked": len(record["files"]), "status": "PASS"}

    def require_writable_run(self):
        """A new calculation uses a fresh output selected by the public runner."""
        if not os.environ.get("CEVNS_CONUS_OUTPUT") or self.output == self.canonical_output:
            raise ValueError("Preserve the latest result. Use run_benchmark.py --method "
                             + self.method + " --output-dir outputs/<NEW_DIRECTORY>")
        for path in (self.output, self.review, self.data, self.document):
            if not path.is_relative_to(ROOT / "outputs"):
                raise ValueError("A repeat run must stay in Gitup01/outputs: " + str(path))
            path.mkdir(parents=True, exist_ok=True)

    def _old_origin(self):
        origins = json.loads((EXAMPLES / "MIGRATION_ORIGINS.json").read_text(encoding="utf-8"))
        return Path(origins[self.method]["original_directory"]), origins

    def map_original(self, path):
        """Translate a recorded old address without opening the old directory."""
        path = Path(path)
        original, origins = self._old_origin()
        for method in ("sm", "nsi"):
            old = Path(origins[method]["original_directory"])
            if path.is_relative_to(old):
                layout = self if method == self.method else Layout(method)
                return layout.path(path.relative_to(old))
        old_root = Path(origins["source_project"])
        if path.is_relative_to(old_root):
            return ROOT / path.relative_to(old_root)
        return path

    def normalize_document(self, path, original_relative=None):
        """Rewrite only local navigation in a migrated/generated report."""
        path = Path(path)
        original, _ = self._old_origin()
        if original_relative is None:
            if path == self.report:
                original_relative = f"review/{self.method.upper()}_BENCHMARK_REPORT_V1.md"
            elif path.is_relative_to(self.review):
                original_relative = "review/" + path.relative_to(self.review).as_posix()
            elif path.is_relative_to(self.output):
                original_relative = "outputs/" + path.relative_to(self.output).as_posix()
            elif path.is_relative_to(self.data):
                original_relative = "data/" + path.relative_to(self.data).as_posix()
            else:
                return
        old_file = original / original_relative
        content = path.read_text(encoding="utf-8-sig")

        def replacement(match):
            raw = match.group(1).strip().strip("<>")
            if re.match(r"^(?:https?:|mailto:|data:|#)", raw):
                return match.group(0)
            target, marker, fragment = raw.partition("#")
            current = (path.parent / unquote(target)).resolve()
            if current.exists() and "snapshot/" not in target.replace("\\", "/"):
                return match.group(0)
            resolved = self.map_original((old_file.parent / unquote(target)).resolve())
            relative = os.path.relpath(resolved, path.parent).replace("\\", "/")
            return "](<" + relative + ("#" + fragment if marker else "") + ">)"

        content = re.sub(r"\]\((<[^>\n]+>|[^)\n]+)\)", replacement, content)
        path.write_text(content, encoding="utf-8")

    def normalize_generated_documents(self):
        for base in (self.review, self.document, self.output):
            for path in base.rglob("*.md"):
                self.normalize_document(path)
