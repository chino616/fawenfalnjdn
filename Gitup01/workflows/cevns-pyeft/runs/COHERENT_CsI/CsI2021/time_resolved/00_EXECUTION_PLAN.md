# CsI2021_time_9x11 — Phase0实施计划草稿

**r3-onboarding-restart-20261118。当前处于材料/配置审阅；本文件不是阶段通过或新公式批准。**

用户明确要求撤下三个入口并重新onboarding。对象沿用同一CsI2021时间分析；父目录legacy9bin阶段记录保持独立。原RESPONSE直接复用选择保留。

## 本轮目标与边界

先建立源、靶、模块选择、探测器、观测与折叠的可审核合同；再执行SM一体流99箱信号前向。+75ns仅为待核时钟的诊断，0ns保持当前候选；不做likelihood拟合或新Fast，不把两体流缺失误差用非M占比替代。

## 实际复用与阻断

| 组件 | 分类 | 现有接口/资源 | 本轮要求 |
|---|---|---|---|
| 源 | CONFIG_ONLY/DRAFT | CallableFluenceComponent、解析DAR谱、ROOT时间边缘 | 明确η对应完整支撑还是参考窗 |
| 靶 | REUSE | csi_target_inventory，14.6kg，Cs133/I127 | 重新核对核数与质量单位 |
| Interaction | BLOCKED | Li2026LegacyInteraction | 原文式75/82与装配逐项对应 |
| 核结构 | REUSE/PARTIAL | ResponseDB及原JSON | 保留用户原表复用选择；基底/归一/外部对应分开核验 |
| 运动学/截面 | BLOCKED | elastic_neutrino_nucleus_v1及现相空间接口 | P04接受后P05核查 |
| 探测器 | REUSE/CONFIG_ONLY | CsIGammaResponse、CsI2021Efficiency、CsITimeEfficiency | P06核验函数/单位/域/施加顺序 |
| 99箱观测 | ADAPTER_CANDIDATE | 原C/AC数据；现有通用Slow单PE轴 | 不能声称已注册原生二维likelihood；先审折叠合同 |
| 预测 | BLOCKED | public predict(backend=slow) | 审核后只建立一个阶段入口 |

## 阶段顺序与验证

| 阶段 | 计划状态 | 负责内容 |
|---|---|---|
| P01 | READY | same CsI2021_time_9x11 identity, data semantics and bin-edge provenance |
| P02 | READY | Cs/I stoichiometry,14.6kg, nuclei count and POT normalization ownership |
| P03 | DRAFT | DAR spectra/lines, eta scope, ROOT marginal and clock; H3 normalization decision pending |
| P04 | BLOCKED | independent interaction/nuclear selections; source Eq75 prefactors, basis/spin normalization and interference |
| P05 | BLOCKED | units/kinematic support/phase space following accepted P04 contract |
| P06 | DRAFT | QF domain, Gamma, efficiency, binning/time selection; can review inputs independently |
| P07 | BLOCKED | single workflow-owned Slow only after current P01-P06 dependencies accepted |
| P08 | NOT_REQUESTED | no new Fast representation |
| P09 | NOT_REQUESTED | no likelihood fit or parameter tuning |
| P10 | DRAFT | separate internal checks, regression, paper-forward and scientific limitations |

每个实际阶段执行：证据/依赖核对→物理方案→必要的人工审核→实现→机器验收→结果审阅→权威记录→进度更新。阶段报告只在实际执行后写入，未执行不填PASS；新公式或归一化未审前不启动P07。

候选数值标准：同网格绝对差≤1e−9 events；独立细化逐源/核素/箱采用0.01 event +0.5%组合判据，进入P07前确认。Shared theory若确需修正，应先完成理论决定并执行CsI2017/CsI2021/Ar2020回归；不改冻结参考或放宽容差。

## 当前需要审阅的具体物理配置

1. Interaction=SM；Nuclear=用户选定原RESPONSE。两者独立登记，不用KN替代原表。
2. η=POT×每POT每味产额/(4πL²)。full_support是按总注量解释的候选；reference_window必须说明η为0–6μs注量的依据，旧/q结果仅作对照。
3. 一体流范围明确；两体流与圈修正尚未实现、误差尚未量化。
4. 默认0ns；+75ns不作为已确定官方onset。BRN/NIN原表与先验归一解释分列，不当作同一模板。
5. 9PE×11time边界、T≥2keVnr候选及QF域限制明确；若改变低反冲截断，须先审其校准依据。

## 写入授权与恢复

原始用户指令见AUTHORIZATION_LOG.yaml。该记录仅记录真实自然语言任务授权，不伪造APPROVE WRITE回复，也不表示物理接受。清理及P00–P03/计划草稿在授权范围内；共享物理公式、注册与数据包不在当前实施范围。
旧文件备份与三份撤下入口的SHA见[清理清单](<../../../../../../../重构/20261118_CsI2021_onboarding_restart/CLEANUP_MANIFEST.json>)。旧结果保留为历史诊断，不恢复为r3当前批准。

## Compiler/Renderer交接

本轮IR与机器运行包尚未编译。H3及必要合同接受后，使用统一cevns-onboarding-draft/1与tools/compile_experiment_package.py生成YAML/NPZ/详细和精简Physics MD；缺绑定或二维能力时明确阻断，不能伪造model ID。
