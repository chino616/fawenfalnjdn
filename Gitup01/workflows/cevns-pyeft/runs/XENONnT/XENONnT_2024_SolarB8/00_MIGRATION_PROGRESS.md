# 主线进度：XENONnT_2024_SolarB8

已更新v3.5完整ρ与Tr(ρK) onboarding；新要求的运行实现和重算待做。旧结果保留，不将旧投影实现称为新版trace。

```json
{
  "schema_version": 1,
  "revision": 16,
  "previous_revision": 15,
  "updated_at": "2026-11-12",
  "workflow_status": "ACTIVE",
  "task_scope": "existing_dataset",
  "workspace_kind": "canonical",
  "execution_mode": "stepwise",
  "experiment_name": "XENONnT 2024",
  "experiment_slug": "XENONnT",
  "dataset_id": "XENONnT_2024_SolarB8",
  "checkpoint": {
    "phase_id": "P07",
    "phase_name": "full rho trace implementation pending",
    "skill": "cevns-experiment",
    "step_id": "phase.P07.implementation_pending",
    "next_action": "implement documented full-rho trace; then validate counts and statistics; current round is documentation first",
    "resume_requires": []
  },
  "gates": {
    "P04": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_sm_theory.md",
      "capability": "solar_b8.sm_theory",
      "decision_refs": [
        "D0001"
      ]
    },
    "P05": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P05_sm_cross_section.md",
      "capability": "solar_b8.sm_cross_section",
      "decision_refs": [
        "D0001"
      ]
    },
    "P06": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P06_accepted_response.md",
      "capability": "solar_b8.accepted_response",
      "decision_refs": [
        "D0001"
      ]
    },
    "P07": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_sm_forward.md",
      "capability": "solar_b8.sm_forward",
      "decision_refs": [
        "D0001"
      ]
    },
    "P01": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P01_dataset.md",
      "capability": "dataset",
      "decision_refs": [
        "D0001"
      ]
    },
    "P02": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P02_target_exposure.md",
      "capability": "target_exposure",
      "decision_refs": [
        "D0001"
      ]
    },
    "P03": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P03_source.md",
      "capability": "source",
      "decision_refs": [
        "D0001"
      ]
    },
    "P10": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_sm_delivery.md",
      "capability": "solar_b8.sm_delivery",
      "decision_refs": [
        "D0001"
      ]
    },
    "P04_vector": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_vector_benchmark.md",
      "capability": "solar_b8.vector.p04",
      "decision_refs": [
        "D0002"
      ]
    },
    "P05_vector": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P05_vector_benchmark.md",
      "capability": "solar_b8.vector.p05",
      "decision_refs": [
        "D0002"
      ]
    },
    "P07_vector": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_vector_benchmark.md",
      "capability": "solar_b8.vector.p07",
      "decision_refs": [
        "D0002"
      ]
    },
    "P10_vector": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_vector_benchmark.md",
      "capability": "solar_b8.vector.p10",
      "decision_refs": [
        "D0002"
      ]
    },
    "P04_nuclear": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_P05_P07_P10_nuclear_response.md",
      "capability": "solar_b8.local_nuclear_SM.P04",
      "decision_refs": [
        "D0004"
      ]
    },
    "P05_nuclear": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_P05_P07_P10_nuclear_response.md",
      "capability": "solar_b8.local_nuclear_SM.P05",
      "decision_refs": [
        "D0004"
      ]
    },
    "P07_nuclear": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_P05_P07_P10_nuclear_response.md",
      "capability": "solar_b8.local_nuclear_SM.P07",
      "decision_refs": [
        "D0004"
      ]
    },
    "P10_nuclear": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_P05_P07_P10_nuclear_response.md",
      "capability": "solar_b8.local_nuclear_SM.P10",
      "decision_refs": [
        "D0004"
      ]
    },
    "P06_singlebin": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P06_singlebin2601.md",
      "capability": "solar_b8.singlebin2601.P06",
      "decision_refs": [
        "D0005"
      ]
    },
    "P07_singlebin": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_singlebin2601.md",
      "capability": "solar_b8.singlebin2601.P07",
      "decision_refs": [
        "D0005"
      ]
    },
    "P09_singlebin": {
      "machine": "BLOCKED",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P09_singlebin2601.md",
      "capability": "solar_b8.singlebin2601.P09",
      "decision_refs": [
        "D0005"
      ]
    },
    "P10_singlebin": {
      "machine": "BLOCKED",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_singlebin2601.md",
      "capability": "solar_b8.singlebin2601.P10",
      "decision_refs": [
        "D0005"
      ]
    },
    "P03_solar_nsi": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P03_solar_nsi2601.md",
      "capability": "solar_b8.ee_vector_nsi2601.P03",
      "decision_refs": [
        "D0006"
      ]
    },
    "P04_solar_nsi": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_solar_nsi2601.md",
      "capability": "solar_b8.ee_vector_nsi2601.P04",
      "decision_refs": [
        "D0006"
      ]
    },
    "P05_solar_nsi": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P05_solar_nsi2601.md",
      "capability": "solar_b8.ee_vector_nsi2601.P05",
      "decision_refs": [
        "D0006"
      ]
    },
    "P06_solar_nsi": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P06_solar_nsi2601.md",
      "capability": "solar_b8.ee_vector_nsi2601.P06",
      "decision_refs": [
        "D0006"
      ]
    },
    "P07_solar_nsi": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_solar_nsi2601.md",
      "capability": "solar_b8.ee_vector_nsi2601.P07",
      "decision_refs": [
        "D0006"
      ]
    },
    "P08_solar_nsi": {
      "machine": "BLOCKED",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P08_solar_nsi2601.md",
      "capability": "solar_b8.ee_vector_nsi2601.P08",
      "decision_refs": [
        "D0006"
      ]
    },
    "P09_solar_nsi": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P09_solar_nsi2601.md",
      "capability": "solar_b8.ee_vector_nsi2601.P09",
      "decision_refs": [
        "D0006"
      ]
    },
    "P10_solar_nsi": {
      "machine": "BLOCKED",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_solar_nsi2601.md",
      "capability": "solar_b8.ee_vector_nsi2601.P10",
      "decision_refs": [
        "D0006"
      ]
    },
    "external_snudd_integration": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_snudd_source.md",
      "decision_refs": [
        "D0007"
      ]
    },
    "external_snudd_full_fig4": {
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "report_ref": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_snudd_full_inference.md",
      "decision_refs": [
        "D0008"
      ]
    },
    "full_rho_trace": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md",
      "decision_refs": [
        "D0009"
      ]
    }
  },
  "active_blockers": [
    "external nuclear author-source certification only: upstream release/normalization unresolved",
    "full natural Xe coverage only: Xe124/Xe126 tables missing",
    "strict paper equivalence only: R01 used KN and author c_i/nuisance points unavailable",
    "strict original-2024 detector equivalence only: early recasting model scope retained"
  ],
  "authorization_refs": {
    "scope": "D0001",
    "write": "W0001",
    "vector_scope": "D0002",
    "vector_write": "W0002",
    "nuclear_scope": "D0004",
    "nuclear_write": "W0004",
    "singlebin_scope": "D0005",
    "singlebin_write": "W0005",
    "solar_nsi_scope": "D0006",
    "solar_nsi_write": "W0006",
    "snudd_source_scope": "D0007",
    "snudd_source_write": "W0007",
    "snudd_full_scope": "D0008",
    "snudd_full_write": "W0008",
    "full_trace_method": "D0009",
    "full_trace_onboarding_write": "W0009"
  },
  "artifact_refs": {
    "source_register": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P00_SOURCE_REGISTER.yaml",
    "evidence_ledger": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P01_EVIDENCE_LEDGER.yaml",
    "physics_contract": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P03_PHYSICS_CONTRACT.yaml",
    "decision_log": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P04_DECISION_LOG.yaml",
    "authorization_log": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/AUTHORIZATION_LOG.yaml",
    "implementation_manifest": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/00_IMPLEMENTATION_MANIFEST.yaml",
    "phase_reports": {
      "P04": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_sm_theory.md",
      "P05": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P05_sm_cross_section.md",
      "P06": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P06_accepted_response.md",
      "P07": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_sm_forward.md",
      "P01": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P01_dataset.md",
      "P02": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P02_target_exposure.md",
      "P03": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P03_source.md",
      "P10": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_sm_delivery.md",
      "P04_vector": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_vector_benchmark.md",
      "P05_vector": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P05_vector_benchmark.md",
      "P07_vector": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_vector_benchmark.md",
      "P10_vector": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_vector_benchmark.md"
    },
    "onboarding_v3": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/ONBOARDING_V3_INDEX.json",
    "onboarding_current": "docs/experiments/XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v3.1.md",
    "nuclear_evidence": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/NUCLEAR_BRANCH.json",
    "nuclear_result": "outputs/solar_b8_sm/20261110_nuclear_response_run2/XENONnT_2024_SolarB8/RESULT.json",
    "singlebin_branch": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SINGLEBIN_BRANCH.json",
    "singlebin_onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md",
    "solar_nsi_branch": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SOLAR_NSI_BRANCH.json",
    "solar_nsi_onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md",
    "snudd_source_branch": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SNUDD_SOURCE_BRANCH.json",
    "snudd_onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_EXTERNAL_ONBOARDING.v3.4.md",
    "snudd_full_branch": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SNUDD_FIG4_BRANCH.json",
    "snudd_full_report": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md",
    "full_trace_onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md",
    "full_trace_contract": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_CONTRACT.v3.5.json",
    "full_trace_branch": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SNUDD_FULL_TRACE_BRANCH.json"
  },
  "requested_unfinished_capabilities": [],
  "human_result_acceptance": "NOT_REVIEWED",
  "previous_checkpoint": {
    "phase_id": "P10",
    "phase_name": "V/B-L fixed-point benchmark delivery",
    "skill": "cevns-experiment",
    "step_id": "vector_forward.result_review",
    "next_action": "review benchmark and retained public response limitations",
    "resume_requires": []
  },
  "parallel_analyses": {
    "multibin_2411_11749": {
      "checkpoint": {
        "phase_id": "P10",
        "phase_name": "actual nuclear Response SM forward review",
        "skill": "cevns-experiment",
        "step_id": "nuclear_response.result_review",
        "next_action": "review actual nuclear-table prediction and separately tracked coverage/source/response limitations",
        "resume_requires": []
      },
      "onboarding": "docs/experiments/XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v3.1.md",
      "status": "retained as-is, original gates and results"
    },
    "singlebin_2601_19883": {
      "analysis_id": "singlebin_2601_19883",
      "status": "PARTIAL_XENON_ACCEPTANCE_TAIL",
      "date": "2026-11-11",
      "decision_ref": "D0005",
      "write_ref": "W0005",
      "samples": [
        "XENONnT"
      ],
      "input_card": "data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json",
      "input_card_sha256": "50c510dbe07d4f41b5c38ce897d1610efcfcc389e107d621009fc57334a0d316",
      "statistics_input": "data/benchmarks/solar_b8_singlebin_2601_19883/fitted_yields.json",
      "source_register_and_evidence": "data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json /references,/extraction,/files",
      "onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md",
      "calculation_entry": "tools/run_solar_b8_singlebin_benchmark.py",
      "results": {
        "XENONnT": "outputs/solar_b8_singlebin/20261111_response_run2/XENONnT/SM_RESULT.json"
      },
      "physics_fingerprints": {
        "XENONnT": "f54732cd010dffd66fe93d6f98e58c78eb2a289abdb972a21949e7a60da75a24"
      },
      "human_result_acceptance": "NOT_REVIEWED",
      "old_multibin": "separate, retained; no resources reused by detector/statistics",
      "blockers": [
        "full X2024 acceptance from last native point to 3keV missing"
      ],
      "common_limitations": [
        "Xe124/Xe126 missing, no renormalization",
        "external nuclear-table source certification unresolved; direct local reuse authorized"
      ],
      "phase_reports": {
        "P06": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P06_singlebin2601.md",
        "P07": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_singlebin2601.md",
        "P09": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P09_singlebin2601.md",
        "P10": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_singlebin2601.md"
      }
    },
    "solar_ee_vector_nsi": {
      "analysis_id": "solar_ee_vector_nsi",
      "version": "3.3",
      "date": "2026-11-12",
      "status": "MAINLINE_NSI_COMPUTED; EXACT_PAPER_GREEN_REPRODUCTION_NOT_ESTABLISHED",
      "decision_ref": "D0006",
      "write_ref": "W0006",
      "samples": [
        "PandaX_paired",
        "PandaX_US2",
        "XENONnT"
      ],
      "input_card": "data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json",
      "input_card_sha256": "ee6d5d5e0844e01692ca5612e778e2785db41dcab9172bb89d0955b01830f256",
      "statistics_input": "data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json",
      "onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md",
      "calculation_entry": "tools/run_solar_b8_nsi_benchmark.py",
      "result": "outputs/solar_b8_nsi/20261112_fig4_run2/NSI_RESULTS.json",
      "comparison": "outputs/solar_b8_nsi/20261112_fig4_run2/PAPER_COMPARISON.json",
      "qa": "outputs/solar_b8_nsi/20261112_fig4_run2/QA.json",
      "model_fingerprints": {
        "PandaX_paired": {
          "physics_fingerprint": "27eb17f0337bde4985d930e473854515d5d2af6d08afbefc346adf6d17e73468",
          "analysis_fingerprint": "e518019bc00f9fb331c53050457dcf2697241650bc7cca9ceced3d6e9782daf4",
          "kernel_sha256": "e4bf43a6413a1ad9d30be16e00c7b59017863b6cd35b187a51326121c2b30a83",
          "K_shape": [
            7,
            2,
            6,
            144
          ]
        },
        "PandaX_US2": {
          "physics_fingerprint": "21f6cf90be35a977d3be65cd0b038d5844c896db0e6c5e74bf586dc7ea87373b",
          "analysis_fingerprint": "008501583b32eacc508ccc9e21b7c0a8aa491e352901265748e925c748669e8f",
          "kernel_sha256": "96524561929f2a6a33c088fa3cb658e46dc5476ffb3deb8d0bc2bea214d36aea",
          "K_shape": [
            7,
            2,
            6,
            144
          ]
        },
        "XENONnT": {
          "physics_fingerprint": "ac7e035d82bbbbfc6b16d395c9748edde5b4d969b667af2d56cd6f4339b03ed7",
          "analysis_fingerprint": "8a0c9b1a339c69317dfc9647d86b924a5ac944824e8b688a1e895edf4c476ea7",
          "kernel_sha256": "c6028135a42cbf62b7dd440e51e937480bd9ac927ab461f53818c049fb59306f",
          "K_shape": [
            7,
            2,
            6,
            144
          ]
        }
      },
      "actual_source_snapshot": "outputs/solar_b8_nsi/20261112_fig4_run2/source",
      "analysis_source_fingerprints": "outputs/solar_b8_nsi/20261112_fig4_run2/ANALYSIS_SOURCE_FINGERPRINTS.json",
      "scientific_result_acceptance": "NOT_REVIEWED",
      "exact_paper_reproduction": "NOT_ESTABLISHED",
      "limitations": [
        "two-flavor adiabatic model, theta13_m=vacuum, no Earth regeneration",
        "X tail is explicit project assumption; zero/unit and bounded profile controls kept separate",
        "B16 structure is pinned secondary transcription; neutron density uses baryon mass1u approximation",
        "paper exact oscillation/profile/SM input card not published; project choice explicitly sourced",
        "seven directly adopted nuclear tables; Xe124/126 missing, no renormalization; external nuclear author release unverified"
      ],
      "phase_reports": {
        "P03": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P03_solar_nsi2601.md",
        "P04": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P04_solar_nsi2601.md",
        "P05": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P05_solar_nsi2601.md",
        "P06": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P06_solar_nsi2601.md",
        "P07": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_solar_nsi2601.md",
        "P08": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P08_solar_nsi2601.md",
        "P09": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P09_solar_nsi2601.md",
        "P10": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_solar_nsi2601.md"
      }
    },
    "external_solar_rho_snudd": {
      "analysis_id": "external_solar_rho_snudd",
      "parent_analysis": "solar_ee_vector_nsi",
      "version": "3.4",
      "date": "2026-11-12",
      "status": "INSTALLED_EXTERNAL_SOURCE_BOUND_TO_MAINLINE_RUNTIME; POINT_BENCHMARK_VERIFIED",
      "decision_ref": "D0007",
      "write_ref": "W0007",
      "scientific_result_acceptance": "NOT_REVIEWED",
      "onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_EXTERNAL_ONBOARDING.v3.4.md",
      "source_card": "extensions/solar_rho_snudd/snudd.input.json",
      "source_card_sha256": "942ae3f85b40b07b87ad271d1a0b943440a89d6d1f294c850ef4a720652861b9",
      "entry": "tools/run_solar_b8_snudd_benchmark.py",
      "loader": "extensions.solar_rho_snudd.experiment.load_snudd",
      "results": "outputs/external/solar_rho_snudd/20261112_run1/RESULTS.json",
      "qa": "outputs/external/solar_rho_snudd/20261112_run1/QA.json",
      "software_commit": "11622ded104994959a649d85e263c2d9f933ea74",
      "primary_old_branch": "solar_ee_vector_nsi (retained)",
      "default_global_activation": false,
      "capability": {
        "installation": "PASS",
        "rho_export": "PASS",
        "standard_runtime": "PASS",
        "actual_Slow_Fast": "PASS",
        "new_full_Fig4": "COMPUTED; EXACT_PAPER_REPRODUCTION_NOT_ESTABLISHED",
        "human": "NOT_REVIEWED"
      },
      "phase_reports": {
        "P03": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P03_snudd_source.md",
        "P07": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P07_snudd_source.md",
        "P08": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P08_snudd_source.md",
        "P09": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P09_snudd_source.md",
        "P10": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_snudd_source.md"
      },
      "full_inference_extension": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SNUDD_FIG4_BRANCH.json"
    },
    "external_snudd_full_fig4": {
      "analysis_id": "external_snudd_full_fig4",
      "parent_analysis": "solar_ee_vector_nsi",
      "parent_source": "external_solar_rho_snudd",
      "version": "3.4.1",
      "date": "2026-11-12",
      "status": "FULL_SOLAR_FIG4_STATISTICAL_CALCULATION_COMPLETE; EXACT_PAPER_REPRODUCTION_NOT_ESTABLISHED",
      "machine": "PASS",
      "human": "NOT_REVIEWED",
      "write_ref": "W0008",
      "decision_ref": "D0008",
      "report": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md",
      "results": "outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json",
      "entry": "tools/run_solar_b8_snudd_inference.py",
      "source_card_sha256": "942ae3f85b40b07b87ad271d1a0b943440a89d6d1f294c850ef4a720652861b9",
      "qa": "outputs/external/solar_rho_snudd/20261112_fig4_run2/QA.json",
      "exact_paper_reproduction": "NOT_ESTABLISHED",
      "default_global_activation": false,
      "phase_reports": {
        "P09": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P09_snudd_full_inference.md",
        "P10": "workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/phases/P10_snudd_full_inference.md"
      }
    },
    "snudd_full_rho_trace_contract": {
      "analysis_id": "snudd_full_rho_trace_contract",
      "version": "3.5",
      "status": "ONBOARDING_UPDATED_RUNTIME_PENDING",
      "write_ref": "W0009",
      "decision_ref": "D0009",
      "onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md",
      "contract": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_CONTRACT.v3.5.json",
      "availability_audit": "outputs/external/solar_rho_snudd/20261112_trace_onboarding/RHO_INPUT_AUDIT.json",
      "implementation_audit": "outputs/external/solar_rho_snudd/20261112_trace_onboarding/IMPLEMENTATION_AUDIT.json",
      "runtime_full_trace": "NOT_IMPLEMENTED",
      "full_trace_statistics": "NOT_RUN",
      "old_numerical_results_preserved": true,
      "human_result_review": "NOT_REVIEWED"
    }
  },
  "current_analysis": "solar_ee_vector_nsi",
  "current_source_variant": "external_solar_rho_snudd",
  "current_statistical_variant": "external_snudd_full_fig4",
  "current_onboarding": "docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md",
  "required_scattering_contraction": "full_rho_trace_K",
  "pending_implementation": "snudd_full_rho_trace_contract"
}
```
