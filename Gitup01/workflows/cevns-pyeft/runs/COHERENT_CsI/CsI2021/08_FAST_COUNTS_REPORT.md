# P08 — csi2021.package_full22_EFT_candidate

## 范围、输入与决定

CsI2021 / legacy_9bin_modular_v1；本次为既有物理的输入适配与执行审计。P01–P03 按用户指示继承，不重做 Onboarding。实施授权 W0001，未产生新物理批准。

数值输入 revision 2，执行实现 wheel 01；哈希与版本桥接见 [input_revision_2.json](../../../../../outputs/csi2021_package_execution_20261104/input_revision_2.json)。工作树同期发生通用 Loader 迁移，其当前结果单列，不能与固定版本混用。

## 实际实现与结果

Fast 将相同前向积分中与 Wilson 系数无关的部分编译成系数双线性核。
核的轴为 (target,source,response,operator_i,operator_j,bin)，
系数轴为 (operator,final flavor,initial flavor)，与固定 rho 收缩后重建事件数。
full 和 pair 表示保留实、虚干涉；加速的是重复参数求值，物理公式和归一化不变。

本次候选包含全部 22 个内部算符、七个输入响应及引擎零响应，用 SM、逐算符和混合复数点比较。
固定、与扫描参数无关的入射态是当前 compiler 前提；rho(E) 及扫描态不在已支持域。
工程等价检查可以保存候选，但正式 P08 仍需当前 P07 的人工 Slow 冻结。

| point | max abs source/isotope/bin | max relative |
| --- | --- | --- |
| SM | 3.197442310920451e-14 | 1.86678558415767e-15 |
| C5_1 | 2.842170943040401e-14 | 2.0534641425670414e-15 |
| C6u1 | 1.9539925233402755e-14 | 2.0760355554835446e-15 |
| C6d1 | 4.263256414560601e-14 | 2.2012989804560242e-15 |
| C6u2 | 2.4868995751603507e-14 | 1.778951231737277e-15 |
| C6d2 | 2.842170943040401e-14 | 1.915795046436969e-15 |
| C7u1 | 2.1316282072803006e-14 | 1.0985648092088843e-15 |
| C7d1 | 4.973799150320701e-14 | 1.605171188944706e-15 |
| C7u2 | 2.4868995751603507e-14 | 1.8667844947082874e-15 |
| C7d2 | 2.1316282072803006e-14 | 1.9157963661915057e-15 |
| C7u3 | 2.842170943040401e-14 | 2.2401427008177877e-15 |
| C7d3 | 3.197442310920451e-14 | 1.7789540217912143e-15 |
| C7u4 | 3.197442310920451e-14 | 1.915455280330766e-15 |
| C7d4 | 3.552713678800501e-14 | 2.202336091677728e-15 |
| C7u5 | 3.197442310920451e-14 | 2.2401426966563985e-15 |
| C7d5 | 3.552713678800501e-14 | 2.052639263421057e-15 |
| C7_6 | 2.4868995751603507e-14 | 2.317919611920617e-15 |
| C7_7 | 3.197442310920451e-14 | 1.8667855777382168e-15 |
| C8u1 | 3.552713678800501e-14 | 1.547748426324578e-15 |
| C8d1 | 2.6645352591003757e-14 | 2.464407475846425e-15 |
| C8u2 | 3.197442310920451e-14 | 1.7788011034740703e-15 |
| C8d2 | 2.842170943040401e-14 | 2.0534176345816357e-15 |
| C8_9 | 3.730349362740526e-14 | 5.870713636404765e-15 |
| mixed_with_SM | 6.394884621840902e-14 | 2.158764695874383e-15 |
| mixed_without_SM | 1.4210854715202004e-14 | 1.1976721523750433e-15 |

保存的核为工程候选；不将 small-grid 等价证据称为正式或全参数域 Fast validated。候选文件 131763 bytes；25 点 Slow+Fast+pair 的整组耗时为 29.436 s。构建时间与单次 Fast 专用基准未独立计时（NOT_MEASURED），不据此给速度提升倍数。

复用/改动类别：REUSE + ADAPTER；共享变更仅为经失败测试证明的延迟导入边界修复。没有在本任务中修改理论/核响应/截面公式、物理输入或冻结参考。备份与归属见 [15_CHANGE_AND_ROLLBACK.md](15_CHANGE_AND_ROLLBACK.md)。

## 验证

| 检查 | 状态 | 命令 | 结果 |
| --- | --- | --- | --- |
| full22 same-grid engineering equivalence | PASS | python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P08 | [P08_results.json](../../../../../outputs/csi2021_package_execution_20261104/P08_results.json) |
| current-version human Slow acceptance | BLOCKED | python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P08 | [P08_results.json](../../../../../outputs/csi2021_package_execution_20261104/P08_results.json) |

技术检查说明所列内部/回归范围；论文与官方复现未完成。外部缺口不通过默认值补齐。

## 结构化交接记录

```json phase-result
{
  "schema_version": 1,
  "phase": "P08",
  "capability_id": "csi2021.package_full22_EFT_candidate",
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
    "outputs/csi2021_package_execution_20261104/P08_results.json",
    "outputs/csi2021_package_execution_20261104/P08_candidate_comparisons.npz",
    "outputs/csi2021_package_execution_20261104/wheel_validation_01/external_case/candidate_full22_kernel.npz",
    "outputs/csi2021_package_execution_20261104/package_fast_tests.xml",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md"
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
      "path": "outputs/csi2021_package_execution_20261104/P08_results.json",
      "sha256": "a2353e89ce04219dd2e7932f433510c50fd38dc7b1f604228db7b93ae41d6a58",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/P08_candidate_comparisons.npz",
      "sha256": "b5fa0e01501be15a10aa1fab1f321174d0787bfbeb830d4ce28a213a14256a42",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/wheel_validation_01/external_case/candidate_full22_kernel.npz",
      "sha256": "62ce422646c42abe80038b35375ac1df739448b2e7b5f93c5e049c124ae30183",
      "role": "evidence"
    },
    {
      "path": "outputs/csi2021_package_execution_20261104/package_fast_tests.xml",
      "sha256": "6024fe2c734297790100025e4f63d0d041c6a90422da91fd673a03334c60d52a",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md",
      "sha256": "955a0e349f71605c79ebe0711f743512ac1a716baee6e5f3dd386790ecc16958",
      "role": "evidence"
    }
  ],
  "checks": [
    {
      "name": "full22 same-grid engineering equivalence",
      "status": "PASS",
      "command": "python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P08",
      "result_ref": "outputs/csi2021_package_execution_20261104/P08_results.json"
    },
    {
      "name": "current-version human Slow acceptance",
      "status": "BLOCKED",
      "command": "python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P08",
      "result_ref": "outputs/csi2021_package_execution_20261104/P08_results.json"
    }
  ],
  "handoff": {
    "representation": "eft_quadratic_coefficient_kernel",
    "backend": "interface_kernel_v1",
    "basis_scope": "full_model",
    "parameter_domain": "22 internal keys; complex LNC/LNV points at declared small grid; parameter-wide convergence not established",
    "state_treatment": "fixed_parameter_independent",
    "slow_reference": {
      "report_ref": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md",
      "sha256": "955a0e349f71605c79ebe0711f743512ac1a716baee6e5f3dd386790ecc16958",
      "approval_ref": "NOT_REVIEWED"
    },
    "cache_dependencies": "source/run/state/target/response/observation/selection/axis/basis/numerics/implementation content; statistical observations excluded",
    "validation_summary": {
      "engineering": "PASS",
      "points": 25,
      "formal_blocker": "P07 current-version human Slow freeze is NOT_REVIEWED; no formal P08 acceptance inferred",
      "cumulative": "NOT_REQUESTED / NOT_RUN"
    }
  }
}
```

## 返回 Master

Machine Gate 为 BLOCKED，Human Gate 为 NOT_REVIEWED。继续执行用户授权的工程检查；受阻科学能力保持原状态。实际下游依赖、限制和失效规则见 handoff。
