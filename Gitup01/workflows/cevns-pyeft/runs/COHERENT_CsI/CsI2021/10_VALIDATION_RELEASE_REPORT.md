# P10 — csi2021.package_execution_capability_audit

## 范围、输入与决定

CsI2021 / legacy_9bin_modular_v1；本次为既有物理的输入适配与执行审计。P01–P03 按用户指示继承，不重做 Onboarding。实施授权 W0001，未产生新物理批准。

数值输入 revision 2，执行实现 wheel 01；哈希与版本桥接见 [input_revision_2.json](../../../../../outputs/csi2021_package_execution_20261104/input_revision_2.json)。工作树同期发生通用 Loader 迁移，其当前结果单列，不能与固定版本混用。

## 实际实现与结果

P10 按能力汇总可追溯证据，不把前面 PASS 相加成为官方结论。
输入无损、内部理论/单位、探测器归一化、积分收敛、旧程序回归、论文 forward 和官方 likelihood
是不同证据层级。物理缺失保留，工程运行/打包/生命周期分别检验。

持久身份及文件归属由 dataset_registry.json 管理，manifest.py 提供 Python 视图，Catalog 查找活动身份。
本任务没有新增 dataset 或改变物理定义；loader/import/packaging 修复使用工程 Gate。
科学声明和 Slow/Fast 正式接受仍为 NOT_REVIEWED，不借连续执行授权伪造批准。

| 能力 | Machine Gate | Human Gate | 范围 |
| --- | --- | --- | --- |
| package_integrity | PASS | NOT_REVIEWED |  |
| P04_internal_legacy | PASS | NOT_REVIEWED |  |
| P05_internal_legacy | PASS | NOT_REVIEWED |  |
| P06_internal_legacy | PASS | NOT_REVIEWED |  |
| P07_internal_legacy | PASS | NOT_REVIEWED |  |
| P08_full22_engineering_equivalence | PASS | NOT_REVIEWED | 25 points on small grid |
| P08_formal_EFT_fast | BLOCKED | NOT_REVIEWED | current human Slow acceptance absent |
| P08_cumulative | NOT_RUN | NOT_REVIEWED |  |
| P09_legacy_approximate | PASS | NOT_REVIEWED |  |
| official_likelihood | BLOCKED | NOT_REVIEWED |  |
| externally_validated_nuclear_response | BLOCKED | NOT_REVIEWED |  |
| general_antineutrino_EFT | BLOCKED | NOT_REVIEWED |  |
| pinned_runtime_wheel | PASS | NOT_REVIEWED |  |
| current_adapter_wheel | PASS | NOT_REVIEWED |  |
| pinned_lifecycle_removal_recovery | PASS | NOT_REVIEWED |  |
| current_worktree_full_compatibility | BLOCKED | NOT_REVIEWED |  |
| final_external_scientific_claim | BLOCKED | NOT_REVIEWED |  |

固定实现的卸载/重装/反向回滚和 wheel 外部 cwd 均实际通过；当前同期迁移的三个兼容回归失败单列，故不报告当前全仓库发布通过。

复用/改动类别：REUSE + ADAPTER；共享变更仅为经失败测试证明的延迟导入边界修复。没有在本任务中修改理论/核响应/截面公式、物理输入或冻结参考。备份与归属见 [15_CHANGE_AND_ROLLBACK.md](15_CHANGE_AND_ROLLBACK.md)。

## 验证

| 检查 | 状态 | 命令 | 结果 |
| --- | --- | --- | --- |
| capability evidence audit | BLOCKED | python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P04 P05 P06 P07 P09 | [P10_results.json](../../../../../outputs/csi2021_package_execution_20261104/P10_results.json) |

技术检查说明所列内部/回归范围；论文与官方复现未完成。外部缺口不通过默认值补齐。

## 结构化交接记录

```json phase-result
{
  "schema_version": 1,
  "phase": "P10",
  "capability_id": "csi2021.package_execution_capability_audit",
  "workspace": "canonical",
  "plan_status": "BLOCKED",
  "machine_gate": "BLOCKED",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/00_EXECUTION_PLAN.md",
  "input_refs": [
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.input.yaml",
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.physics.md",
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.resources.npz"
  ],
  "input_fingerprint": "49aa23f62dd5ba7d2a2c0b964d44b14567a7f149b2c5507c418569eef386ddc8",
  "evidence_refs": [
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.input.yaml",
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.physics.md",
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.resources.npz",
    "outputs/csi2021_package_execution_20261104/P10_results.json",
    "outputs/csi2021_package_execution_20261104/test_results_summary.json",
    "outputs/csi2021_package_execution_20261104/revision_bridge_validation.json",
    "outputs/csi2021_package_execution_20261104/wheel_validation_01/wheel_result.json",
    "outputs/csi2021_package_execution_20261104/wheel_validation_02/wheel_result.json",
    "outputs/csi2021_package_execution_20261104/lifecycle_validation_01/lifecycle_result.json",
    "outputs/csi2021_package_execution_20261104/pinned_regression_01.xml",
    "outputs/csi2021_package_execution_20261104/regression_matrix_02.xml",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/04_THEORY_RESPONSE_REPORT.md",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/05_KINEMATICS_CROSS_SECTION_REPORT.md",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/06_DETECTOR_RESPONSE_REPORT.md",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/08_FAST_COUNTS_REPORT.md",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/09_STATISTICS_REPORT.md"
  ],
  "decision_refs": [],
  "approval_refs": [],
  "artifacts": [
    {
      "path": "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.input.yaml",
      "sha256": "7aa8ed1f59cada6db7e949fcba5dae5ea546989bb99480009fb172a1c25f992c",
      "role": "input"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.physics.md",
      "sha256": "beb4c4033b62312a19603f1b0bf46d1a0623cc20a76a805c13f828c777746291",
      "role": "input"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.resources.npz",
      "sha256": "25043e6f510f0ae643a532c53cec2c4b0dad1f2af7172247add5fdc99adc827a",
      "role": "input"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/P10_results.json",
      "sha256": "425ebc2e2a2bcc5b6f3bc3cb9cb1649526c816146d310fddda9e2386ba26f9a3",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/test_results_summary.json",
      "sha256": "3be568107e0168ac4c0470a7dc25f4b232fb668fb63d0f01d1d4b281eb3b9b63",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/revision_bridge_validation.json",
      "sha256": "6c00b6f15cd24dd0dfa58cc435dc50ca44cbb5dd9a6fac63a8437517bf381323",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/wheel_validation_01/wheel_result.json",
      "sha256": "6fd2b1b3193d5d442385b4aff6b5440f6aaa7b573e4bfc1f069bf46bb706a1f6",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/wheel_validation_02/wheel_result.json",
      "sha256": "32a8dd003b71bb519b4b356d07d3aec747e4a15c748e8bf9d4a5948d3c3434c2",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/lifecycle_validation_01/lifecycle_result.json",
      "sha256": "96fbf8c31de136e88e59cbbc879a2b49664235d310405d8cc8d8d8b845c20794",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/pinned_regression_01.xml",
      "sha256": "8088d24416ceede0ee0de947a80600868b291fd290201f97cfded2447f5748bc",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/regression_matrix_02.xml",
      "sha256": "ce83df753a638d30a24bbd6f1f2e742d3be73553495b06eeb395e6b2857bbedb",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/04_THEORY_RESPONSE_REPORT.md",
      "sha256": "73e7b51518bf67e8bb8668cb4929555daa96e1f8afd31177cb71e56fff2b4253",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/05_KINEMATICS_CROSS_SECTION_REPORT.md",
      "sha256": "7ca0b9cefaf4a8006f13a9892e6ece79daacceec4d1931def98bc5371e05ad5f",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/06_DETECTOR_RESPONSE_REPORT.md",
      "sha256": "83b5bbaffe3c2bed829b8c3b7e3b2c10b8bf6381f8ba26bba8a4a2393c979eaa",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md",
      "sha256": "955a0e349f71605c79ebe0711f743512ac1a716baee6e5f3dd386790ecc16958",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/08_FAST_COUNTS_REPORT.md",
      "sha256": "0ea3ef6413d513e5b1732a719128162dc0233fa6a46b11ff020eb76cd69abab9",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/09_STATISTICS_REPORT.md",
      "sha256": "f5a57931b446f4914a7be1679a52af2733d32d42858e453d1c78b6e43d502ce8",
      "role": "evidence"
    }
  ],
  "checks": [
    {
      "name": "capability evidence audit",
      "status": "BLOCKED",
      "command": "python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P04 P05 P06 P07 P09",
      "result_ref": "outputs/csi2021_package_execution_20261104/P10_results.json"
    }
  ],
  "handoff": {
    "delivery_scope": {
      "mode": "capability_change",
      "target": "existing CsI2021 package-driven P04-P10 execution audit",
      "completion": "partial"
    },
    "capability_matrix": [
      {
        "id": "package_integrity",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/package_to_runtime_mapping_final.json",
        "scope": ""
      },
      {
        "id": "P04_internal_legacy",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/04_THEORY_RESPONSE_REPORT.md",
        "scope": ""
      },
      {
        "id": "P05_internal_legacy",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/05_KINEMATICS_CROSS_SECTION_REPORT.md",
        "scope": ""
      },
      {
        "id": "P06_internal_legacy",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/06_DETECTOR_RESPONSE_REPORT.md",
        "scope": ""
      },
      {
        "id": "P07_internal_legacy",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md",
        "scope": ""
      },
      {
        "id": "P08_full22_engineering_equivalence",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/P08_results.json",
        "scope": "25 points on small grid"
      },
      {
        "id": "P08_formal_EFT_fast",
        "requested": true,
        "required_for_claim": false,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/08_FAST_COUNTS_REPORT.md",
        "scope": "current human Slow acceptance absent"
      },
      {
        "id": "P08_cumulative",
        "requested": false,
        "required_for_claim": false,
        "machine_gate": "NOT_RUN",
        "human_gate": "NOT_REVIEWED",
        "result_ref": null,
        "scope": ""
      },
      {
        "id": "P09_legacy_approximate",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/09_STATISTICS_REPORT.md",
        "scope": ""
      },
      {
        "id": "official_likelihood",
        "requested": true,
        "required_for_claim": false,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/P09_results.json",
        "scope": ""
      },
      {
        "id": "externally_validated_nuclear_response",
        "requested": true,
        "required_for_claim": false,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/P04_results.json",
        "scope": ""
      },
      {
        "id": "general_antineutrino_EFT",
        "requested": true,
        "required_for_claim": false,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/P04_results.json",
        "scope": ""
      },
      {
        "id": "pinned_runtime_wheel",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/wheel_validation_01/wheel_result.json",
        "scope": ""
      },
      {
        "id": "current_adapter_wheel",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/wheel_validation_02/wheel_result.json",
        "scope": ""
      },
      {
        "id": "pinned_lifecycle_removal_recovery",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "PASS",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/lifecycle_validation_01/lifecycle_result.json",
        "scope": ""
      },
      {
        "id": "current_worktree_full_compatibility",
        "requested": true,
        "required_for_claim": true,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "outputs/csi2021_package_execution_20261104/regression_matrix_02.xml",
        "scope": ""
      },
      {
        "id": "final_external_scientific_claim",
        "requested": true,
        "required_for_claim": false,
        "machine_gate": "BLOCKED",
        "human_gate": "NOT_REVIEWED",
        "result_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/12_SKILL_WORKFLOW_AUDIT.md",
        "scope": ""
      }
    ],
    "validation_levels": {
      "internal": "P04/P05/P06 + quadrature + full22 same-grid equivalence",
      "legacy": "explicit same-grid and protected-array regressions",
      "paper_forward": "MISSING",
      "official_likelihood": "BLOCKED"
    },
    "runtime_integration": {
      "pinned_wheel": "PASS",
      "updated_adapter_wheel": "PASS",
      "pinned_lifecycle": "PASS",
      "current_global_regression": "FAIL"
    },
    "final_claim": "Internally reproducible package-driven legacy calculation only; no official/scientific approval inferred",
    "limitations": [
      "官方旧九箱逐参数一手出处缺失，不能宣称 official reproduction。",
      "22 个内部 EFT key 的外部 Lagrangian/尺度及一般反中微子符号/螺旋度未闭合。",
      "核响应外部源表/生成流水线缺失，I127 M_nn(0) 残差原样保留。",
      "Michel 端点/节点掩码和 Gamma、quenching、efficiency 官方校准有效域尚未独立确认。",
      "observed residual/excess 与显式加入 background 的语义冲突保留；仅近似对角 Gaussian。",
      "当前结果没有官方 covariance/likelihood、置信区间、CL 或最终限制。",
      "人工科学状态 NOT_REVIEWED；连续工程执行授权不等于科学批准。",
      "收敛仅覆盖声明的 SM 点与 legacy 积分域；22 算符 Fast 比较使用小网格，不证明全参数域收敛。"
    ]
  }
}
```

## 返回 Master

Machine Gate 为 BLOCKED，Human Gate 为 NOT_REVIEWED。继续执行用户授权的工程检查；受阻科学能力保持原状态。实际下游依赖、限制和失效规则见 handoff。
