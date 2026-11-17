"""Verify acquired files, actual ResponseDB reuse and generated provenance views.

These checks cover recorded files and implementation consistency. They do not
authenticate a scientific citation or establish unverified external authorship.
"""
from pathlib import Path
import hashlib
import importlib
import json
import sys

import numpy as np
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[5]
sys.path.insert(0, str(ROOT))


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify():
    sources = read(RUN / "P00_SOURCE_REGISTER.yaml")
    ledger = read(RUN / "P01_EVIDENCE_LEDGER.yaml")
    contract = read(RUN / "P03_PHYSICS_CONTRACT.yaml")
    claims = {claim["claim_id"]: claim for claim in ledger["claims"]}
    source_map = {entry["source_id"]: entry for entry in sources["sources"]}
    checks = []
    assert len(source_map) == len(sources["sources"])
    assert len(claims) == len(ledger["claims"])
    for entry in source_map.values():
        path = ROOT / entry["uri_or_path"]
        assert path.is_file(), entry["source_id"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry["source_id"]
        assert entry["citation"] and entry["verification_scope"]
    checks.append(dict(name="direct_source_files_and_fingerprints", count=len(source_map), result="PASS"))
    for name, kind in [("P01_EVIDENCE_LEDGER.yaml", "evidence-ledger"),
                       ("P03_PHYSICS_CONTRACT.yaml", "physics-contract")]:
        schema = read(ROOT / f"workflows/_shared/schemas/{kind}.schema.yaml")
        Draft202012Validator(schema).validate(read(RUN / name))
    checks.append(dict(name="P01_P03_schema", result="PASS"))
    visited = set()

    def visit(identifier, active):
        assert identifier in claims, identifier
        assert identifier not in active, "Evidence cycle " + identifier
        if identifier in visited:
            return
        for parent in claims[identifier]["input_claims"]:
            visit(parent, active | {identifier})
        visited.add(identifier)

    for claim in claims.values():
        assert claim["source_ids"], claim["claim_id"]
        for source_id in claim["source_ids"]:
            assert source_id in source_map, source_id
        assert claim["locator"] and claim["verification_scope"], claim["claim_id"]
        assert claim["verification_checks"], claim["claim_id"]
        visit(claim["claim_id"], set())
    for section in contract["sections"].values():
        for identifier, field in section["fields"].items():
            assert field["evidence_claims"] == [identifier]
            assert field["value"] == claims[identifier]["value"]
            assert field["unit"] == claims[identifier]["unit"]
    checks.append(dict(name="every_adopted_field_has_resolvable_evidence", count=len(claims), result="PASS"))
    response_module = importlib.import_module("cevns_pyeft.nuclear.response")
    raw_path = ROOT / "data/responses/responses_all.json"
    raw = read(raw_path)
    database = response_module.ResponseDB(raw_path)
    channel_count = 0
    with np.load(RUN / "data/nuclear_response_CsI.npz", allow_pickle=False) as extracted:
        assert len(extracted.files) == 16
        for nucleus, key in [("Cs133", "Cs133"), ("I127", "I")]:
            response = database.get(key)
            for channel, values in raw["nuclei"][key]["responses"].items():
                original = np.asarray(values, dtype=float)
                np.testing.assert_array_equal(extracted[nucleus + "_" + channel], original)
                for y in [0., .1, .5]:
                    expected = np.array([[np.polynomial.polynomial.polyval(y, coefficients)
                        for coefficients in row] for row in original]) * np.exp(-2 * y)
                    np.testing.assert_allclose(response.W_np(channel, y), expected, rtol=2e-13, atol=1e-10)
                channel_count += 1
    assert raw["meta"]["basis"] == "np" and "(p,n)" in raw["meta"]["note"]
    checks.append(dict(name="actual_ResponseDB_original_data_call_and_exact_arrays", arrays=channel_count,
        y_points=[0., .1, .5], result="PASS"))
    decisions = read(RUN / "DECISION_LOG.json")
    assert any(row["id"] == "D_LOCAL_RESPONSE" for row in decisions["decisions"])
    assert claims["C_RESOURCE_BINDING"]["value"]["path"] == "data/responses/responses_all.json"
    optional = claims["C_W_CONVERSION"]
    assert optional["status"] == "MISSING" and optional["adoption"] == "OPTIONAL_EXTERNAL_AUDIT"
    for field in ["C_W_Cs133_M", "C_W_I127_M"]:
        assert claims[field]["verification_checks"]["applicability"] == "USER_SELECTED_LOCAL_REUSE"
        assert claims[field]["verification_checks"]["external_upstream"] == "UNVERIFIED_OPTIONAL_AUDIT"
    for row in contract["report_spec"]["handoff"]:
        if row["capability"].startswith("P04") or row["capability"].startswith("P07"):
            assert "C_W_CONVERSION" not in row["required"]
    checks.append(dict(name="user_resource_selection_preserved_without_promoting_external_provenance", result="PASS"))
    with np.load(RUN / "data/analysis_inputs.npz", allow_pickle=False) as arrays:
        for identifier, key in [("C_OBS", "C_counts"), ("C_CONTROL", "AC_counts")]:
            np.testing.assert_array_equal(arrays[key], claims[identifier]["value"])
            assert arrays[key].shape == (9, 11)
        assert arrays["C_counts"].sum() == 1578
        assert arrays["AC_counts"].sum() == 1295
        assert abs(arrays["SS_counts"].sum() - claims["C_SS"]["value"]) < 1e-12
    official_eff = np.loadtxt(RUN / "sources/official/effCoefficients.txt")[0]
    np.testing.assert_array_equal(official_eff, claims["C_EFF"]["value"])
    assert official_eff[-1] != claims["C_EFF_LEGACY"]["value"]
    assert any(row["id"] == "G_BG" and row["status"] == "BLOCKED" for row in contract["report_spec"]["issues"])
    checks.append(dict(name="observations_units_and_legacy_nominal_differences_remain_explicit", result="PASS"))
    for formula in contract["report_spec"]["formulas"]:
        assert formula["sources"] and formula["locator"] and formula["symbols"]
        for identifier in formula["inputs"]:
            assert identifier in claims
        for identifier in formula["sources"]:
            assert identifier in source_map
    exporter = importlib.import_module("export_physics_docs")
    for path, body in exporter.render().items():
        assert path.read_text(encoding="utf-8") == body, "Stale output " + str(path)
    checks.append(dict(name="formula_input_mapping_and_same_source_generated_outputs", result="PASS"))
    result = dict(revision=sources["revision"], date="2026-11-06", machine_checks=checks,
        machine_status="PASS", sources=len(source_map), claims=len(claims), arrays=channel_count,
        scientific_status="DRAFT_PARTIAL; LOCAL_RESPONSE_REUSE_USER_SELECTED; BACKGROUND_AND_PAPER_EQUIVALENCE_GAPS_REMAIN",
        scope="File fingerprints, actual arrays, original ResponseDB numerical reading, source/evidence graph and deterministic rendering",
        outside_scope="Automatic authentication of external authorship, numerical citations and scientific applicability")
    return result


if __name__ == "__main__":
    result = verify()
    (RUN / "evidence/PROVENANCE_CHECKS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
