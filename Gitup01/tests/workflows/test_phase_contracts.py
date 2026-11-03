"""Adversarial phase-record examples; all approvals and physics inputs are synthetic."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("phase_contract_validator", REPO / "workflows/cevns-pyeft/qa/validate_phase_contract.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

HASH = "0" * 64


def result(phase, handoff):
    return {
        "schema_version": 1, "phase": phase, "capability_id": "synthetic." + phase,
        "workspace": "canonical", "plan_status": "READY",
        "machine_gate": "PASS", "human_gate": "NOT_REVIEWED",
        "scope_ref": "synthetic-scope", "input_refs": ["synthetic-input"],
        "input_fingerprint": HASH, "evidence_refs": ["synthetic-evidence"],
        "decision_refs": ["synthetic-decision"], "approval_refs": [],
        "artifacts": [{"path": "result.json", "sha256": HASH, "role": "diagnostic"}],
        "checks": [{"name": "synthetic-check", "status": "PASS", "command": "synthetic command", "result_ref": "result.json"}],
        "handoff": copy.deepcopy(handoff),
    }


def slow():
    return result("P07", {
        "normalization_ledger": "integrated fluence times per-nucleus yield times actual nuclei",
        "output_contract": "events/bin; explicit source and target components",
        "numerics_and_convergence": "independent quadrature refinements",
        "reference_comparison": "internal convergence only; external reference missing",
        "freeze_scope": "synthetic parameter and integration domain",
    })


def fast():
    return result("P08", {
        "representation": "eft_quadratic_coefficient_kernel", "backend": "interface_kernel_v1",
        "basis_scope": "declared_subspace", "parameter_domain": "two complex coefficients; all relevant interference retained",
        "state_treatment": "fixed_parameter_independent",
        "slow_reference": {"report_ref": "slow.json", "sha256": HASH, "approval_ref": "synthetic-freeze"},
        "cache_dependencies": "source/run/target/observation/implementation; excludes observed data",
        "validation_summary": "per-source isotope and bin; complex and boundary cases",
    })


def detector():
    return result("P06", {
        "representation": "bin_probability", "unit": "1", "normalization": "sum_at_most_one",
        "included_selections": ["trigger"], "axes": "true recoil, reconstructed bins",
        "response_definition": "accepted probabilities with row sum 0.6",
        "selection_ownership": "trigger already in matrix", "validity_domain": "synthetic calibration domain",
    })


def statistics():
    return result("P09", {
        "channels": [{"id": "on_off", "representation": "binned_counts", "processing": "raw",
                      "design": "on_off", "likelihood": "poisson", "requires_covariance": False}],
        "prediction_binding": "accepted Slow directly",
        "required_inputs": {"available": True, "sources": ["official-on-off-counts-and-exposure-ratio"], "missing": []},
        "nuisance_model": "explicit background rate and constraints",
        "inference": "likelihood evaluation only", "claim_level": "internal",
        "benchmark": "analytic toy likelihood",
    })


def release():
    return result("P10", {
        "delivery_scope": {"mode": "dataset_onboarding", "target": "Slow forward only", "completion": "complete"},
        "capability_matrix": [
            {"id": "slow", "requested": True, "required_for_claim": True,
             "machine_gate": "PASS", "human_gate": "APPROVED", "result_ref": "slow.json"},
            {"id": "fast", "requested": False, "required_for_claim": False,
             "machine_gate": "NOT_RUN", "human_gate": "NOT_REVIEWED", "result_ref": None},
        ],
        "validation_levels": "internal numerical consistency only",
        "runtime_integration": "custom catalog load/predict checked",
        "final_claim": "validated forward prediction within declared scope", "limitations": ["no official likelihood"],
    })


class PhaseContractTests(unittest.TestCase):
    def assertValid(self, record, **kwargs):
        self.assertEqual(validator.validate_record(record, **kwargs), [])

    def assertInvalid(self, record, **kwargs):
        self.assertTrue(validator.validate_record(record, **kwargs))

    def test_schema_and_actual_draft_templates(self):
        for kind in ("phase", "physics"):
            validator.load_schema(kind)
        phase = validator.read_record(REPO / "workflows/_shared/templates/phase/PHASE_REPORT_TEMPLATE.md")
        self.assertValid(phase)
        contract = validator.read_record(REPO / "workflows/_shared/templates/onboarding/PHYSICS_CONTRACT_TEMPLATE.yaml")
        self.assertValid(contract, kind="physics")

    def test_draft_can_defer_details_but_pass_cannot(self):
        record = slow()
        record.update(plan_status="DRAFT", machine_gate="NOT_RUN", input_refs=[], input_fingerprint=None,
                      evidence_refs=[], artifacts=[], checks=[], handoff={})
        self.assertValid(record)
        record["machine_gate"] = "PASS"
        self.assertInvalid(record)

    def test_not_requested_is_not_a_machine_pass(self):
        record = fast()
        record.update(plan_status="NOT_REQUESTED", machine_gate="NOT_RUN", human_gate="NOT_REVIEWED", handoff={})
        self.assertValid(record)
        record["machine_gate"] = "PASS"
        self.assertInvalid(record)

    def test_candidate_cannot_self_approve(self):
        record = slow()
        record["workspace"] = "isolated_candidate"
        self.assertValid(record)
        record.update(human_gate="APPROVED", approval_refs=["synthetic-freeze"])
        self.assertInvalid(record)

    def test_accepted_result_requires_decision_and_acceptance_refs(self):
        record = slow()
        record["human_gate"] = "APPROVED"
        self.assertInvalid(record)
        record["approval_refs"] = ["synthetic-freeze"]
        self.assertValid(record)
        record["decision_refs"] = []
        self.assertInvalid(record)

    def test_accepted_probabilities_preserve_loss(self):
        record = detector()
        self.assertValid(record)
        record["handoff"]["normalization"] = "integral_one"
        self.assertInvalid(record)
        record["handoff"]["normalization"] = "sum_at_most_one"
        record["handoff"]["unit"] = "PE^-1"
        self.assertInvalid(record)

    def test_density_and_probability_contracts_are_distinct(self):
        record = detector()
        record["handoff"].update(representation="conditional_density", unit="PE^-1", normalization="integral_one",
                                 included_selections=[], selection_ownership="applied after conditional density")
        self.assertValid(record)
        record["handoff"]["normalization"] = "sum_at_most_one"
        self.assertInvalid(record)

    def test_duplicate_selection_is_rejected(self):
        record = detector()
        record["handoff"]["included_selections"] = ["trigger", "trigger"]
        self.assertInvalid(record)

    def test_interface_fast_rejects_energy_or_parameter_dependent_state(self):
        self.assertValid(fast())
        for mode in ("energy_dependent", "parameter_dependent"):
            record = fast()
            record["handoff"]["state_treatment"] = mode
            self.assertInvalid(record)

    def test_declared_subspace_requires_basis_and_frozen_slow(self):
        record = fast()
        self.assertValid(record)
        record["handoff"]["basis_scope"] = "not_applicable"
        self.assertInvalid(record)
        record = fast()
        record["handoff"]["slow_reference"]["approval_ref"] = None
        self.assertInvalid(record)
        record["workspace"] = "isolated_candidate"
        self.assertValid(record)

    def test_poisson_does_not_require_unneeded_covariance(self):
        self.assertValid(statistics())
        record = statistics()
        record["handoff"]["channels"][0]["requires_covariance"] = True
        self.assertInvalid(record)

    def test_background_subtracted_data_cannot_be_raw_poisson(self):
        record = statistics()
        channel = record["handoff"]["channels"][0]
        channel.update(processing="background_subtracted", design="single_sample")
        self.assertInvalid(record)
        channel.update(likelihood="gaussian", requires_covariance=True, covariance_ref="approved-covariance")
        self.assertValid(record)

    def test_missing_official_inputs_do_not_pass(self):
        record = statistics()
        record["handoff"]["claim_level"] = "official_likelihood"
        record["handoff"]["required_inputs"].update(available=False, missing=["official-background-template"])
        self.assertInvalid(record)

    def test_channel_identity_is_unique(self):
        record = statistics()
        record["handoff"]["channels"] *= 2
        self.assertInvalid(record)

    def test_optional_fast_does_not_block_slow_delivery(self):
        self.assertValid(release())

    def test_unrequested_capability_cannot_be_reported_as_current_pass(self):
        record = release()
        record["handoff"]["capability_matrix"][1]["machine_gate"] = "PASS"
        self.assertInvalid(record)

    def test_required_fast_blocker_prevents_complete_claim(self):
        record = release()
        fast_row = record["handoff"]["capability_matrix"][1]
        fast_row.update(requested=True, required_for_claim=True, machine_gate="BLOCKED")
        self.assertInvalid(record)
        record["handoff"]["delivery_scope"]["completion"] = "partial"
        self.assertValid(record)

    def test_machine_pass_requires_successful_traceable_checks(self):
        record = slow()
        record["checks"][0]["status"] = "BLOCKED"
        self.assertInvalid(record)
        record["checks"][0].update(status="PASS", result_ref="unrecorded.json")
        self.assertInvalid(record)

    def test_artifact_hash_changes_and_path_escape_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            artifact = root / "result.json"
            artifact.write_text("synthetic result", encoding="utf-8")
            record = slow()
            record["artifacts"][0]["sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
            self.assertValid(record, artifact_root=root)
            artifact.write_text("changed", encoding="utf-8")
            self.assertInvalid(record, artifact_root=root)
            record["artifacts"][0]["path"] = "../result.json"
            self.assertInvalid(record, artifact_root=root)

    def test_fast_upstream_freeze_is_checked_by_content(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            artifact = root / "result.json"
            artifact.write_text("synthetic diagnostic", encoding="utf-8")
            record = fast()
            record["artifacts"][0]["sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
            predecessor = slow()
            predecessor.update(human_gate="APPROVED", approval_refs=["synthetic-freeze"])
            predecessor["artifacts"][0]["sha256"] = record["artifacts"][0]["sha256"]
            slow_path = root / "slow.json"
            slow_path.write_text(json.dumps(predecessor), encoding="utf-8")
            record["handoff"]["slow_reference"]["sha256"] = hashlib.sha256(slow_path.read_bytes()).hexdigest()
            self.assertValid(record, artifact_root=root)
            record["handoff"]["slow_reference"]["approval_ref"] = "wrong-freeze"
            self.assertInvalid(record, artifact_root=root)
            record["handoff"]["slow_reference"]["approval_ref"] = "synthetic-freeze"
            slow_path.write_text(json.dumps({**predecessor, "human_gate": "NOT_REVIEWED"}), encoding="utf-8")
            self.assertInvalid(record, artifact_root=root)
            record["handoff"]["slow_reference"]["sha256"] = hashlib.sha256(slow_path.read_bytes()).hexdigest()
            self.assertInvalid(record, artifact_root=root)

    def test_version_four_approval_cannot_have_empty_contract(self):
        record = {"contract_version": 4, "dataset_id": "synthetic", "sections": {
            "theory_response": {"decision_status": "APPROVED", "fields": {}}}}
        self.assertInvalid(record, kind="physics")
        record["sections"]["theory_response"].update(
            fields={"model": "synthetic model"}, decision_refs=["synthetic-decision"], evidence_refs=["synthetic-source"])
        self.assertValid(record, kind="physics")

    def test_unchanged_slow_report_cannot_hide_changed_result_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            own = root / "result.json"
            upstream_output = root / "slow-result.json"
            own.write_text("synthetic fast check", encoding="utf-8")
            upstream_output.write_text("synthetic frozen bins", encoding="utf-8")
            predecessor = slow()
            predecessor.update(human_gate="APPROVED", approval_refs=["synthetic-freeze"])
            predecessor["artifacts"][0].update(
                path="slow-result.json", sha256=hashlib.sha256(upstream_output.read_bytes()).hexdigest())
            predecessor["checks"][0]["result_ref"] = "slow-result.json"
            report = root / "slow.json"
            report.write_text(json.dumps(predecessor), encoding="utf-8")
            record = fast()
            record["artifacts"][0]["sha256"] = hashlib.sha256(own.read_bytes()).hexdigest()
            record["handoff"]["slow_reference"]["sha256"] = hashlib.sha256(report.read_bytes()).hexdigest()
            self.assertValid(record, artifact_root=root)
            upstream_output.write_text("different bins", encoding="utf-8")
            self.assertInvalid(record, artifact_root=root)

    def test_legacy_contract_keeps_compatibility_without_upgrade(self):
        legacy = {"contract_version": 3, "dataset_id": None, "sections": {
            "theory_response": {"decision_status": "DRAFT", "fields": {}}}}
        self.assertValid(legacy, kind="physics")
        self.assertEqual(legacy["contract_version"], 3)

    def test_duplicate_json_keys_and_report_blocks_fail(self):
        with self.assertRaises(ValueError):
            validator.parse_json('{"phase":"P07","phase":"P08"}')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.md"
            block = "```json phase-result\n{}\n```\n"
            path.write_text(block + block, encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.read_record(path)


class PhaseReferenceAuditTests(unittest.TestCase):
    def test_missing_symbol_in_shared_phase_reference_is_detected(self):
        path = REPO / "workflows/cevns-pyeft/skills/engineering/cevns-physics-modularity/scripts/audit_references.py"
        spec = importlib.util.spec_from_file_location("phase_reference_auditor", path)
        auditor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auditor)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            skill = root / "skill"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text("", encoding="utf-8")
            for name in auditor.REQUIRED_REFERENCES:
                (skill / "references" / name).write_text("", encoding="utf-8")
            refs = root / "workflows/_shared/references/phase"
            refs.mkdir(parents=True)
            (refs / "P07.md").write_text("cevns_pyeft/example.py::missing", encoding="utf-8")
            (root / "cevns_pyeft").mkdir()
            (root / "cevns_pyeft/example.py").write_text("def existing(): pass\n", encoding="utf-8")
            errors = auditor.audit(root, skill)
            self.assertTrue(any("missing symbol" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
