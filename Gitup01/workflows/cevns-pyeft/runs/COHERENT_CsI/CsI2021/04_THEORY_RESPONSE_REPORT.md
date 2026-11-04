# P04 — csi2021.package_full_theory_internal

## 范围、输入与决定

CsI2021 / legacy_9bin_modular_v1；本次为既有物理的输入适配与执行审计。P01–P03 按用户指示继承，不重做 Onboarding。实施授权 W0001，未产生新物理批准。

数值输入 revision 2，执行实现 wheel 01；哈希与版本桥接见 [input_revision_2.json](../../../../../outputs/csi2021_package_execution_20261104/input_revision_2.json)。工作树同期发生通用 Loader 迁移，其当前结果单列，不能与固定版本混用。

## 实际实现与结果

中微子核散射的强度由 Wilson 味矩阵经过 LEFT→核子 matching，再与核响应收缩得到。
系数矩阵的行是末态味、列是入射味；末态求和后得到入射味空间的 Hermitian 核 K，
给定入射密度矩阵 rho 的强度为 Re Tr(rho K)。SM 的单位矩阵只是一个对角点，
完整代码保留复数、非对角味以及 LNC/LNV 的既有约定。

核响应使用物理 (p,n) 顺序，W_ab(y)=exp(exp_factor*y) sum_k a_abk*y^k，
y=(|q|b/2)^2；b 使用 GeV^-1。Cs133、I127 各七通道来自 NPZ，不能再乘 Helm。
引擎第八项 SigmaPDelta 为零；不能把零项说成输入缺失已补全。M+c1 只占完整理论的一个子空间。

14 个数组、56 个 y 点比对的最大绝对差为 0.0。I127 M_nn(0) 审计：`{"actual": 5475.961194368475, "N_squared": 5476, "residual": -0.03880563152506511, "status": "retained original table"}`。

复用/改动类别：REUSE + ADAPTER；共享变更仅为经失败测试证明的延迟导入边界修复。没有在本任务中修改理论/核响应/截面公式、物理输入或冻结参考。备份与归属见 [15_CHANGE_AND_ROLLBACK.md](15_CHANGE_AND_ROLLBACK.md)。

## 验证

| 检查 | 状态 | 命令 | 结果 |
| --- | --- | --- | --- |
| 14 responses and operator contracts | PASS | python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P04 | [P04_results.json](../../../../../outputs/csi2021_package_execution_20261104/P04_results.json) |

技术检查说明所列内部/回归范围；论文与官方复现未完成。外部缺口不通过默认值补齐。

## 结构化交接记录

```json phase-result
{
  "schema_version": 1,
  "phase": "P04",
  "capability_id": "csi2021.package_full_theory_internal",
  "workspace": "canonical",
  "plan_status": "READY",
  "machine_gate": "PASS",
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
    "outputs/csi2021_package_execution_20261104/P04_results.json",
    "outputs/csi2021_package_execution_20261104/adapter_29_green.xml",
    "outputs/csi2021_package_execution_20261104/package_to_runtime_mapping_final.json"
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
      "path": "outputs/csi2021_package_execution_20261104/P04_results.json",
      "sha256": "ac081f67dfed566d08f8a9f69cb714b65b6e7daf892bd8320875e91648403def",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/adapter_29_green.xml",
      "sha256": "17635647f4a1d12d1d4a43f19aacd615266de6f2b6fa0d0369c5a25c7bc3059e",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/package_to_runtime_mapping_final.json",
      "sha256": "4f5a92d0a8e0e1f963a6ee24669ab73054953ab3293a3842d596d33e55d3a565",
      "role": "evidence"
    }
  ],
  "checks": [
    {
      "name": "14 responses and operator contracts",
      "status": "PASS",
      "command": "python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P04",
      "result_ref": "outputs/csi2021_package_execution_20261104/P04_results.json"
    }
  ],
  "handoff": {
    "theory_scope": "22 internal Li2026 LEFT keys; SM plus LNC/LNV, legacy_shared_kernel",
    "coefficient_convention": "GeV^(4-d); np table label is physical (p,n); rows final flavor, columns initial flavor",
    "nuclear_responses": {
      "source": "NPZ nuclear_Cs133_* / nuclear_I127_*",
      "channels": [
        "M",
        "SigmaPP",
        "SigmaP",
        "PhiPP",
        "PhiPT",
        "Delta",
        "MPhiPP"
      ],
      "grid_y": [
        0,
        0.1,
        0.5,
        1
      ],
      "normalization": "exp(exp_factor*y) polynomial, no extra Helm"
    },
    "coverage": "all supplied seven channels; SigmaPDelta identically zero in existing amplitude",
    "runtime_binding": "CsIPackage.responses -> PackedInteraction._responses -> Li2026LegacyInteraction",
    "external_evidence_limits": [
      "官方旧九箱逐参数一手出处缺失，不能宣称 official reproduction。",
      "22 个内部 EFT key 的外部 Lagrangian/尺度及一般反中微子符号/螺旋度未闭合。",
      "核响应外部源表/生成流水线缺失，I127 M_nn(0) 残差原样保留。",
      "Michel 端点/节点掩码和 Gamma、quenching、efficiency 官方校准有效域尚未独立确认。"
    ]
  }
}
```

## 返回 Master

Machine Gate 为 PASS，Human Gate 为 NOT_REVIEWED。继续执行用户授权的工程检查；受阻科学能力保持原状态。实际下游依赖、限制和失效规则见 handoff。
