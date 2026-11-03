"""Read-only schema and artifact checks for phase reports; never grants approval.

Requires jsonschema only in the QA environment. Does not import physics code.
Machine inputs use JSON syntax (a YAML 1.2 subset); Markdown phase reports contain
exactly one fenced "json phase-result" block.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[3]
SCHEMAS = Path("workflows/_shared/schemas")
BLOCK = re.compile(r"^```json phase-result\s*\n(.*?)^```\s*$", re.M | re.S)


def parse_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError(f"non-finite JSON value: {value}")

    return json.loads(text, object_pairs_hook=unique, parse_constant=nonfinite)


def read_record(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    if Path(path).suffix.lower() == ".md":
        blocks = BLOCK.findall(text)
        if len(blocks) != 1:
            raise ValueError("expected exactly one json phase-result block")
        text = blocks[0]
    return parse_json(text)


def load_schema(kind="phase", repo=REPO):
    name = "phase-result" if kind == "phase" else "physics-contract"
    schema = parse_json((Path(repo) / SCHEMAS / f"{name}.schema.yaml").read_text("utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def _safe_file(root, relative):
    path = Path(relative)
    if path.is_absolute() or path.drive or ".." in path.parts:
        raise ValueError(f"artifact must be a workspace-relative path: {relative}")
    if any(part.lower() == "backup" for part in path.parts):
        raise ValueError("backup is not an active phase artifact")
    root = Path(root).resolve()
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"artifact escapes workspace: {relative}")
    if not resolved.is_file():
        raise ValueError(f"artifact missing: {relative}")
    return resolved


def _verify_slow_reference(record, root):
    reference = record["handoff"]["slow_reference"]
    try:
        path = _safe_file(root, reference["report_ref"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            return ["slow_reference: report content changed"]
        slow = read_record(path)
        if not isinstance(slow, dict) or slow.get("phase") != "P07":
            return ["slow_reference: expected a P07 report"]
        errors = validate_record(slow, artifact_root=root)
        if errors:
            return ["slow_reference: invalid upstream record: " + error for error in errors]
        if slow["phase"] != "P07" or slow["machine_gate"] != "PASS":
            return ["slow_reference: requires a P07 machine PASS"]
        if record["workspace"] == "canonical":
            if slow["workspace"] != "canonical" or slow["human_gate"] != "APPROVED":
                return ["slow_reference: canonical Fast requires accepted canonical Slow"]
            if reference["approval_ref"] not in slow["approval_refs"]:
                return ["slow_reference: freeze approval reference does not match"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ["slow_reference: " + str(exc)]
    return []


def validate_record(record, *, kind="phase", artifact_root=None, repo=REPO):
    validator = Draft202012Validator(load_schema(kind, repo))
    errors = [
        f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(record), key=lambda e: str(list(e.absolute_path)))
    ]
    if errors or kind != "phase":
        return errors
    paths = [item["path"] for item in record["artifacts"]]
    if len(paths) != len(set(paths)):
        errors.append("artifacts: duplicate path")
    if record["machine_gate"] == "PASS":
        for check in record["checks"]:
            if check["result_ref"] not in paths:
                errors.append(f"checks: result_ref is not a recorded artifact: {check['result_ref']}")
    if record["phase"] == "P09" and "channels" in record["handoff"]:
        ids = [item["id"] for item in record["handoff"]["channels"]]
        if len(ids) != len(set(ids)):
            errors.append("channels: duplicate identity")
    if record["phase"] == "P10" and "capability_matrix" in record["handoff"]:
        ids = [item["id"] for item in record["handoff"]["capability_matrix"]]
        if len(ids) != len(set(ids)):
            errors.append("capability_matrix: duplicate identity")
    if artifact_root is not None:
        for item in record["artifacts"]:
            try:
                path = _safe_file(artifact_root, item["path"])
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual != item["sha256"]:
                    errors.append(f"artifacts: content changed: {item['path']}")
            except (OSError, ValueError, TypeError) as exc:
                errors.append("artifacts: " + str(exc))
        if record["phase"] == "P08" and record["machine_gate"] == "PASS":
            errors.extend(_verify_slow_reference(record, artifact_root))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, nargs="?")
    parser.add_argument("--kind", choices=("phase", "physics"), default="phase")
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--check-schemas", action="store_true")
    args = parser.parse_args()
    if args.record is None and not args.check_schemas:
        parser.error("provide a record or --check-schemas")
    if args.kind != "phase" and args.artifact_root is not None:
        parser.error("--artifact-root applies only to phase records")
    try:
        if args.check_schemas:
            for kind in ("phase", "physics"):
                load_schema(kind)
            print("PASS: JSON Schema 2020-12 declarations")
        if args.record is not None:
            record = read_record(args.record)
            errors = validate_record(record, kind=args.kind, artifact_root=args.artifact_root)
            for error in errors:
                print("ERROR:", error)
            if errors:
                return 1
            if args.kind == "physics" and record["contract_version"] < 4:
                print("LEGACY: structural compatibility only; no completion upgrade")
            print("PASS: record structure" + (" and artifact content" if args.artifact_root is not None else ""))
        print("Scope: no scientific validation, input-freshness proof or authentication of human approval.")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print("ERROR:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
