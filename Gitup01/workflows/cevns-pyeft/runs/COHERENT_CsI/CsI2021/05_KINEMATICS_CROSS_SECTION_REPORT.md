# P05 — csi2021.package_cross_section_internal

## 范围、输入与决定

CsI2021 / legacy_9bin_modular_v1；本次为既有物理的输入适配与执行审计。P01–P03 按用户指示继承，不重做 Onboarding。实施授权 W0001，未产生新物理批准。

数值输入 revision 2，执行实现 wheel 01；哈希与版本桥接见 [input_revision_2.json](../../../../../outputs/csi2021_package_execution_20261104/input_revision_2.json)。工作树同期发生通用 Loader 迁移，其当前结果单列，不能与固定版本混用。

## 实际实现与结果

P05 把 P04 的散射强度变成每个核的微分截面，不乘源注量、核数或效率。
所有量用 GeV 时，Tmax=2E²/(m+2E)，Emin=(T+sqrt(T²+2mT))/2；
实际入口用 E[MeV]、T[keV]、m[GeV]，结果 cm²/keV，Jacobian 为 10^-6。

这里 q0=T，qabs²=2mT，signed q2=q0²-qabs²；它们是程序当前采用的动量约定，
必须区分 qabs² 与带符号 Lorentz 不变量。核响应只使用空间动量得到 y=qabs²*b²/4。
空间动量采用既有非相对论近似，未保留精确 |q|² 中的 T² 项；精确弹性端点不意味着允许域内振幅也完全相对论精确。
合法但域外反冲返回零；负反冲、非有限量或不合法能量坐标拒绝。T=0 的一般 EFT
可能有低能奇异项，不能把 SM 的有限零点推广到所有算符。

| 核素/源 | Tmax(30 MeV) [keV] | qabs² @ 1 keV [GeV²] | signed q² [GeV²] |
| --- | --- | --- | --- |
| Cs133/prompt_numu | 14.522135130310854 | 0.00024777743158951995 | -0.00024777743058951995 |
| Cs133/delayed_nue | 14.522135130310854 | 0.00024777743158951995 | -0.00024777743058951995 |
| Cs133/delayed_numubar | 14.522135130310854 | 0.00024777743158951995 | -0.00024777743058951995 |
| I127/prompt_numu | 15.207872458075334 | 0.00023659950234487998 | -0.00023659950134488 |
| I127/delayed_nue | 15.207872458075334 | 0.00023659950234487998 | -0.00023659950134488 |
| I127/delayed_numubar | 15.207872458075334 | 0.00023659950234487998 | -0.00023659950134488 |

复用/改动类别：REUSE + ADAPTER；共享变更仅为经失败测试证明的延迟导入边界修复。没有在本任务中修改理论/核响应/截面公式、物理输入或冻结参考。备份与归属见 [15_CHANGE_AND_ROLLBACK.md](15_CHANGE_AND_ROLLBACK.md)。

## 验证

| 检查 | 状态 | 命令 | 结果 |
| --- | --- | --- | --- |
| six component/isotope kinematic and units checks | PASS | python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P05 | [P05_results.json](../../../../../outputs/csi2021_package_execution_20261104/P05_results.json) |

技术检查说明所列内部/回归范围；论文与官方复现未完成。外部缺口不通过默认值补齐。

## 结构化交接记录

```json phase-result
{
  "schema_version": 1,
  "phase": "P05",
  "capability_id": "csi2021.package_cross_section_internal",
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
    "outputs/csi2021_package_execution_20261104/P05_results.json",
    "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/04_THEORY_RESPONSE_REPORT.md",
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
      "path": "outputs/csi2021_package_execution_20261104/P05_results.json",
      "sha256": "e4ba438eb3c3cf7cc3bbe00be08f6ec98ec761d044300c2556865c902712f5db",
      "role": "evidence"
    },
    {
      "path": "workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/04_THEORY_RESPONSE_REPORT.md",
      "sha256": "73e7b51518bf67e8bb8668cb4929555daa96e1f8afd31177cb71e56fff2b4253",
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
      "name": "six component/isotope kinematic and units checks",
      "status": "PASS",
      "command": "python -B tools/run_csi2021_package_phases.py --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel --package outputs/csi2021_package_execution_20261104/input_revision_2 --phases P05",
      "result_ref": "outputs/csi2021_package_execution_20261104/P05_results.json"
    }
  ],
  "handoff": {
    "process_and_mass": "elastic CEvNS, Cs133/I127 mass A*AMU_GEV from package with fixed-engine validation",
    "kinematics": "exact ElasticKinematics endpoints; amplitude uses NR qabs2=2*m*T and signed q2=T*T-qabs2, not the exact spatial expression 2*m*T+T*T",
    "cross_section_api": "same P04 PackedInteraction.dsigma_dT(target,energy_MeV,recoil_keV,incident_state,parameters)",
    "units_and_axes": "positive E[MeV] vector -> DifferentialCrossSection cm^2/keV, same energy coordinates",
    "support_and_limits": "T=0, endpoint and outside tested for SM; negative/nonfinite refused; general antinu audit remains open",
    "benchmark": {
      "source": "outputs/csi2021_package_execution_20261104/P05_results.json",
      "independent": "phase-space/Jacobian contraction and endpoint inverse"
    }
  }
}
```

## 返回 Master

Machine Gate 为 PASS，Human Gate 为 NOT_REVIEWED。继续执行用户授权的工程检查；受阻科学能力保持原状态。实际下游依赖、限制和失效规则见 handoff。
