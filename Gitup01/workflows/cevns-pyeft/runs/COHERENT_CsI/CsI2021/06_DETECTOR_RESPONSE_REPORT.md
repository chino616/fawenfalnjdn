# P06 — csi2021.package_gamma_density_internal

## 范围、输入与决定

CsI2021 / legacy_9bin_modular_v1；本次为既有物理的输入适配与执行审计。P01–P03 按用户指示继承，不重做 Onboarding。实施授权 W0001，未产生新物理批准。

数值输入 revision 2，执行实现 wheel 01；哈希与版本桥接见 [input_revision_2.json](../../../../../outputs/csi2021_package_execution_20261104/input_revision_2.json)。工作树同期发生通用 Loader 迁移，其当前结果单列，不能与固定版本混用。

## 实际实现与结果

真实反冲 T 先通过 quenching 得到电子等效能量 Eee，再生成重建 PE 密度。
令 u=T[keV]/1000，Eee[keV]=1000(q1*u+q2*u²+q3*u³+q4*u⁴)。
Gamma 的 shape k=1+gamma_b*Eee，rate lambda=(gamma_a/Eee)*k；
R(x|T)=lambda^k*x^(k-1)*exp(-lambda*x)/Gamma(k)，x>0，单位 PE^-1。

效率为 max(a/(1+exp(-b(x-c)))+d,0)，接受率单独按源分量施加。
本次 P07 保留 legacy sampled-density 顺序：响应→T 积分→非负裁剪→PE 插值→效率→bin 积分→接受率。
诊断接口给出的 P_b(T) 已含效率/接受率，其箱和至多为一；不把分析窗内结果强行归一为一。

| T [keVnr] | int R dx | accepted analysis-window probability |
| --- | --- | --- |
| 1.0 | 1.0000000000000002 | 1.8612811780937906e-07 |
| 5.0 | 1.0000000000000104 | 0.024843772417792672 |
| 10.0 | 0.9999999999999991 | 0.3912423994442084 |
| 30.0 | 0.9999999999999977 | 0.9644697591078597 |

[响应与效率图](../../../../../outputs/csi2021_package_execution_20261104/P06_response.png)；已视觉检查标签、图例、坐标和边界。

复用/改动类别：REUSE + ADAPTER；共享变更仅为经失败测试证明的延迟导入边界修复。没有在本任务中修改理论/核响应/截面公式、物理输入或冻结参考。备份与归属见 [15_CHANGE_AND_ROLLBACK.md](15_CHANGE_AND_ROLLBACK.md)。

## 验证

| 检查 | 状态 | 命令 | 结果 |
| --- | --- | --- | --- |
| Gamma normalization and accepted window probabilities | PASS | python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P06 | [P06_results.json](../../../../../outputs/csi2021_package_execution_20261104/P06_results.json) |

技术检查说明所列内部/回归范围；论文与官方复现未完成。外部缺口不通过默认值补齐。

## 结构化交接记录

```json phase-result
{
  "schema_version": 1,
  "phase": "P06",
  "capability_id": "csi2021.package_gamma_density_internal",
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
    "outputs/csi2021_package_execution_20261104/P06_results.json",
    "outputs/csi2021_package_execution_20261104/P06_response.png",
    "outputs/csi2021_package_execution_20261104/P06_response.pdf",
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
      "path": "outputs/csi2021_package_execution_20261104/P06_results.json",
      "sha256": "4f4898166d98f58c8ec7c01df5a359b92a4d98916223396a039323fe6ec9f361",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/P06_response.png",
      "sha256": "a6f62e1c41d20be8d10c36854cae461bf98fdf1498782027e67e871ef930d08e",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/P06_response.pdf",
      "sha256": "0eb520a02091c55fd1d2dc000a0ab6e66e7b9cbc6dfdaf96f2dcacb90a7070da",
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
      "name": "Gamma normalization and accepted window probabilities",
      "status": "PASS",
      "command": "python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P06",
      "result_ref": "outputs/csi2021_package_execution_20261104/P06_results.json"
    }
  ],
  "handoff": {
    "representation": "conditional_density",
    "unit": "PE^-1",
    "normalization": "integral_one",
    "included_selections": [],
    "axes": "true recoil keV -> reconstructed PE density; nine ordered intervals from NPZ ten PE edges",
    "response_definition": "CsIGammaResponse, shape-rate Gamma; explicit YAML quenching and gamma parameters",
    "selection_ownership": "density has no selection; legacy_density_fold applies efficiency, core.predict applies component acceptance once",
    "validity_domain": "positive Eee and x>0; numerical samples 1/5/10/30 keVnr, official calibration range MISSING"
  }
}
```

## 返回 Master

Machine Gate 为 PASS，Human Gate 为 NOT_REVIEWED。继续执行用户授权的工程检查；受阻科学能力保持原状态。实际下游依赖、限制和失效规则见 handoff。
