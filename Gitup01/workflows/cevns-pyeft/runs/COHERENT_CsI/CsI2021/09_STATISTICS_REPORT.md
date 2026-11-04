# P09 — csi2021.package_legacy_approximate_gaussian

## 范围、输入与决定

CsI2021 / legacy_9bin_modular_v1；本次为既有物理的输入适配与执行审计。P01–P03 按用户指示继承，不重做 Onboarding。实施授权 W0001，未产生新物理批准。

数值输入 revision 2，执行实现 wheel 01；哈希与版本桥接见 [input_revision_2.json](../../../../../outputs/csi2021_package_execution_20261104/input_revision_2.json)。工作树同期发生通用 Loader 迁移，其当前结果单列，不能与固定版本混用。

## 实际实现与结果

P09 在给定预测上计算旧九箱的近似目标函数。先且仅先除一次 PE 箱宽：S_b=N_b/DeltaPE_b。
采用 χ²=sum_b[(D_b-(1+alpha)S_b-(1+beta)B_b)/sigma_b]²
+(alpha/sigma_alpha)²+(beta/sigma_beta)²。alpha、beta 是无界零均值 Gaussian pulls，
用 2×2 线性正规方程解析 profile；本次以独立矩阵解和 Asimov 零点复核。
包适配器拒绝非正 uncertainty；底层 profiler 对有限 sigma 采用 10^-12 floor。
若线性求解器报奇异，旧接口返回 alpha=beta=0、success=False 和 singular profile matrix，不能把该返回当成功拟合。

该实现保留 residual/excess 与显式 background 叠加的历史语义冲突，只说明 approximate Gaussian
数值可复算。没有官方 covariance/likelihood，不计算或宣称官方 CL、置信区间或最终限制。
使用 Slow 预测，不要求 P08 先通过。

| Slow profile | chi2 | alpha | beta | success |
| --- | --- | --- | --- | --- |
| finer | 4.229729115743852 | -0.032147768672757975 | -0.02296067715937478 | True |

数值模型所需输入齐全；官方统计语义缺失/冲突另列为 BLOCKED，不用 required_inputs=[] 掩盖官方能力。

复用/改动类别：REUSE + ADAPTER；共享变更仅为经失败测试证明的延迟导入边界修复。没有在本任务中修改理论/核响应/截面公式、物理输入或冻结参考。备份与归属见 [15_CHANGE_AND_ROLLBACK.md](15_CHANGE_AND_ROLLBACK.md)。

## 验证

| 检查 | 状态 | 命令 | 结果 |
| --- | --- | --- | --- |
| Gaussian independent matrix solution and Asimov zero | PASS | python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P09 | [P09_results.json](../../../../../outputs/csi2021_package_execution_20261104/P09_results.json) |
| sigma floor, guards and injected solver failure semantics | PASS | python -B outputs/csi2021_package_execution_20261104/P09_edge_diagnostics.py | [P09_edge_diagnostics.json](../../../../../outputs/csi2021_package_execution_20261104/P09_edge_diagnostics.json) |

技术检查说明所列内部/回归范围；论文与官方复现未完成。外部缺口不通过默认值补齐。

## 结构化交接记录

```json phase-result
{
  "schema_version": 1,
  "phase": "P09",
  "capability_id": "csi2021.package_legacy_approximate_gaussian",
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
  "input_fingerprint": "420e2bb16be9e99654632cea7479b84641cb2bcf3eab2aae57fc412e324e0b9e",
  "evidence_refs": [
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.input.yaml",
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.physics.md",
    "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.resources.npz",
    "outputs/csi2021_package_execution_20261104/P09_results.json",
    "outputs/csi2021_package_execution_20261104/P09_observables.csv",
    "outputs/csi2021_package_execution_20261104/P09_edge_diagnostics.json",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md",
    "outputs/csi2021_package_execution_20261104/current_adapter_05.xml"
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
      "path": "outputs/csi2021_package_execution_20261104/P09_results.json",
      "sha256": "0bacd20327a0190379a39445eb7b6597c0c81555bc0f2e9f85e1bac7d20ce652",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/P09_observables.csv",
      "sha256": "ef013e452b539975f3e120b49b693f62c7454388e8ee465f62e75cff4cb8f0e1",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/P09_edge_diagnostics.json",
      "sha256": "05eaf71edd97a5adfc22c614c1965196a3ff5baee35f654611cbe36e9e214826",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md",
      "sha256": "955a0e349f71605c79ebe0711f743512ac1a716baee6e5f3dd386790ecc16958",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/current_adapter_05.xml",
      "sha256": "6ef5280d1c3efca4e44c61fe9e0a1272894fc326f183e71059681b1e481aefee",
      "role": "evidence"
    }
  ],
  "checks": [
    {
      "name": "Gaussian independent matrix solution and Asimov zero",
      "status": "PASS",
      "command": "python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P09",
      "result_ref": "outputs/csi2021_package_execution_20261104/P09_results.json"
    },
    {
      "name": "sigma floor, guards and injected solver failure semantics",
      "status": "PASS",
      "command": "python -B outputs/csi2021_package_execution_20261104/P09_edge_diagnostics.py",
      "result_ref": "outputs/csi2021_package_execution_20261104/P09_edge_diagnostics.json"
    }
  ],
  "handoff": {
    "channels": [
      {
        "id": "legacy_9bin",
        "representation": "binned_density",
        "processing": "other",
        "design": "single_sample",
        "likelihood": "gaussian",
        "requires_covariance": false,
        "processing_detail": "legacy residual/excess and explicit background conflict retained"
      }
    ],
    "prediction_binding": {
      "backend": "Slow",
      "profile": "finer",
      "bin_width_conversion_count": 1,
      "upstream": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md"
    },
    "required_inputs": {
      "available": true,
      "sources": [
        "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.input.yaml",
        "outputs/csi2021_package_execution_20261104/input_revision_2/experiment.resources.npz"
      ],
      "missing": []
    },
    "nuisance_model": "alpha/beta, zero-mean Gaussian priors, unbounded analytic 2x2 profile; sigma_floor=1e-12",
    "inference": "objective evaluation only; no intervals/CL/limits",
    "claim_level": "approximate",
    "benchmark": {
      "independent_chi2": 4.229729115743853,
      "asimov_zero": 1.3601051815662173e-32
    }
  }
}
```

## 返回 Master

Machine Gate 为 PASS，Human Gate 为 NOT_REVIEWED。继续执行用户授权的工程检查；受阻科学能力保持原状态。实际下游依赖、限制和失效规则见 handoff。
