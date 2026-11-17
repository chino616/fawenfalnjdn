# CsI2021时间分析：唯一当前进度索引

本索引不授予物理批准；父目录索引仅属旧9箱包。当前无r3已通过阶段，不继承旧PASS。

```json
{
  "schema_version": 1,
  "revision": 2,
  "previous_revision": 1,
  "updated_at": "2026-11-18",
  "workflow_status": "ACTIVE",
  "task_scope": "existing_dataset",
  "workspace_kind": "canonical",
  "execution_mode": "stepwise",
  "presentation_format": "migration_blocks_v1",
  "experiment_name": "COHERENT CsI2021 time-resolved",
  "experiment_slug": "COHERENT_CsI",
  "dataset_id": "CsI2021",
  "analysis_id": "CsI2021_time_9x11",
  "scientific_claim_ref": {
    "path": "P03_PHYSICS_CONTRACT.yaml",
    "decision_ref": "D_RESTART_20261118",
    "scientific_acceptance": "NOT_REVIEWED"
  },
  "checkpoint": {
    "phase_id": "onboarding",
    "phase_name": "材料/证据与H3配置审阅",
    "skill": "cevns-onboarding",
    "step_id": "onboarding.step3.scientific_claim",
    "next_action": "H3 review: same9x11 SM/RESPONSE one-body scope; adopt a fluence convention only after review; continue Eq75 audit before implementation",
    "resume_requires": [
      "H3 actual physics review",
      "required phase pre-code contract acceptance"
    ]
  },
  "gates": {
    "P01": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P02": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P03": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P04": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P05": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P06": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P07": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P08": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P09": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    },
    "P10": {
      "machine": "NOT_RUN",
      "human": "NOT_REVIEWED",
      "report_ref": null
    }
  },
  "active_blockers": [
    "G_EQ75",
    "G_FLUENCE_SCOPE"
  ],
  "pending_decisions": [
    "fluence scope and precision claim"
  ],
  "authorization_refs": {
    "scope": "D_RESTART_20261118",
    "write": "W0001"
  },
  "artifact_refs": {
    "source_register": "P00_SOURCE_REGISTER.yaml",
    "evidence_ledger": "P01_EVIDENCE_LEDGER.yaml",
    "missing_and_conflicts": "P02_MISSING_AND_CONFLICTS.md",
    "physics_contract": "P03_PHYSICS_CONTRACT.yaml",
    "decision_log": "DECISION_LOG.json",
    "authorization_log": "AUTHORIZATION_LOG.yaml",
    "implementation_manifest": "00_IMPLEMENTATION_MANIFEST.yaml",
    "phase_reports": {},
    "input_inventory": "evidence/INPUT_FILE_REVIEW_20261118.json"
  },
  "stale_artifacts": [
    "20261107/20261117 diagnostics are historical references, not r3 accepted predictions"
  ],
  "handoff": {
    "state": "NONE"
  },
  "source_fingerprints": [
    {
      "path": "docs/references/COHERENT/2110.07730v2.pdf",
      "sha256": "03b4bd7aa10653ecb86743c4d4a90abb0251ac3d0e5087b5202a621567bd81a7",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf",
      "sha256": "7f4aec67a7a5323a84d6db0379d973de46e4a782c6c8f3cd43e31c262c6b5753",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "docs/references/COHERENT/2211.11905v2.pdf",
      "sha256": "071225342b004f4e97001d6c200066b216f0af1af226f4b4aafa43512304a2b1",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "docs/references/COHERENT/2202.11002v3.pdf",
      "sha256": "dd87860c25f0bde41cc65a3acebdc9e04c8ed0f47e61095801f4b9672364b6a9",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "docs/references/COHERENT/2111.02477v2.pdf",
      "sha256": "22194a7f022dcd5918ad03db5b64e475449980b201fdafd7a5a1c7ac15330605",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/snsFlux2D.root",
      "sha256": "1af0639911bb9219b66cbfa617057cd145d180c2ac8bc791c3008f1d666206ae",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnC.txt",
      "sha256": "b78333f0cc0c4182f913cecd91d55968e43a620683e9f51e0ceb1c1db596326f",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnAC.txt",
      "sha256": "fba5c06334521531eda353771b5297b44a70566b0d755e23b174c716abec9468",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/brnPE.txt",
      "sha256": "0000b042b8d0d28b90370eb70d1409db1d8c510fcf2b3e636370b0d4443ac0b0",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/brnTrec.txt",
      "sha256": "6f279d835242a868dfc048abaa42b8c400bf961036de7bc7e64636efdd46466f",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/ninPE.txt",
      "sha256": "41cae0376003cc2dcd028a3913e7c16395471f612b56d311f80e2a6071c9950c",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/ninTrec.txt",
      "sha256": "2bb034d648b312f4ee329ae95078dc748ff3f83b999c411b08f86d82ddf8e151",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt",
      "sha256": "f1e58e6b8ec4db53da3be21fe44ebc4621e9b248b920be09759b1000dada8c51",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt",
      "sha256": "ea6b8f34b296bf6e99f2a4ac504030d99155daba3e3c252f51c87d2470319d13",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "data/responses/responses_all.json",
      "sha256": "cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Elastic/Cs133_GCN5082.txt",
      "sha256": "da46cf5c93b499f74a9e29d3e932ed4a81108fe23e1a527c5e9df7d6692a5c23",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Elastic/I127_GCN5082.txt",
      "sha256": "393e743c02fe818528de5ede53479b688e36eea03547c2ed6f47c1012fbe2f4b",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Mu2e_NRET/v2/mathematica/mu2elib_v2.wl",
      "sha256": "5e5f1e646c9399c25f4ae72cd8f7dd1976ac87234d41ac5759242740783137ca",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt",
      "sha256": "77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/PDG2024_pi_charged.pdf",
      "sha256": "f7c2e47de06d0e28f637441067aa144ca5a9e76cec2055060f95e39cae57bfae",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json",
      "sha256": "08a6a2a70d32c5af28928641a64e303a80d9d7d025d562d2532f2761564c5186",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py",
      "sha256": "6691472df0a3264d4ba95fa9f356bf6afbd1c411c14e9807b3700cff638e139e",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/slow_counts_csi2021.py",
      "sha256": "73d793e61dfa190af26ca01b1381ba4b019da07b0b95f25a5a09a99f595773c9",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/sns.py",
      "sha256": "9ea97baf50e46a158680b556f9fe514502fd8ca7386d8e9ea36ed07681e7a764",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py",
      "sha256": "535de210f4ebde240e8b3f230a24c0e472a71ae7ad3ff836c1abf1787a1cbc28",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/analysis_inputs.py",
      "sha256": "931da0b2339f2fe1fda07eea2751784c9f6269db2afbcb26ecf4a85adade119d",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json",
      "sha256": "674060128a0bd83da468009dbafffc171eded8cf662753a42fe70434ef6f666a",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py",
      "sha256": "4761eeed0f193a0424ea19b591c3ac3e9c39f91df688da45d3966d630c1f13ed",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/README.md",
      "sha256": "cd00a92446882a91a94c816af2103f06e342d22458a2d170320b58092d61d3d9",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/HANDOFF_PROMPT.md",
      "sha256": "88f55d6d3767fb3d25b9a6660c97a4bc483a25ed167d8c0e32eaa85ed9dc19c1",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/20261117_CsI2021_ROOTTime_%E6%A0%B8%E5%BF%83%E4%BB%A3%E7%A0%81%E4%B8%8E%E4%B8%BB%E7%BA%BF%E8%BF%81%E7%A7%BB%E4%BA%A4%E6%8E%A5%E5%8C%85.zip",
      "sha256": "53796f8c1c7df7148a1acce915d7a1210ac67206f5bd0819d63a7ec259bad511",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "examples/COHERENT_CsI/time_resolved_common/timing_diagnostics.py",
      "sha256": "e9c21f40f2ad78befe857866238377e2e6c74b5555f54116b134a31edec09503",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py",
      "sha256": "0078b45a5344290860f9fd881abed3953a8ff2a474f34986d6905565b666cc8e",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "docs/references/General_CEvNS/2601.19883v2.pdf",
      "sha256": "e72ae8b8d7642027b9723ce9758b2477d7322c802b53cef67f561191289d90cd",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "cevns_pyeft/theory/li2026/amplitude.py",
      "sha256": "40a2bbfcb60716da67ff3d5182d5af6dd075bcd7dfccf9a49b9b3b0a8a9b7aed",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "cevns_pyeft/theory/li2026/responses.py",
      "sha256": "5edb06d4dd7409d0bac8245f9bf25b24f81f9e473e37f5e4f311492e9542f01b",
      "affects": [
        "onboarding input review"
      ]
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/restart_records.py",
      "sha256": "ac7be6768550e274f196ad92dfcb81c7c446a2e855dc93414c515371cc60d972",
      "affects": [
        "onboarding input review"
      ]
    }
  ]
}
```
