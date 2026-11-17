# PandaX-4T 2024 US2 onboarding v2.1 精简草稿

**2026-11-06，DRAFT / PARTIAL。**

[详细主文](<experiment.physics.v2.1.md>) · [来源登记](<../../../../../../重构/20261106_Onboarding_provenance_revision/P00_SOURCE_REGISTER.yaml>) · [逐项证据](<../../../../../../重构/20261106_Onboarding_provenance_revision/PandaX4T_P01_EVIDENCE_LEDGER.yaml>) · [配置草稿](<../../../../../../重构/20261106_Onboarding_provenance_revision/PandaX4T_P03_PHYSICS_CONTRACT.yaml>)

<a id="toc"></a>

## 目录

- [目标与方法](#identity)
- [已有数值与出处](#inputs)
- [本轮补充和反馈](#revision)
- [下一步依赖](#handoff)

<a id="identity"></a>

## 目标与方法

本次以2411.11749v1 Fig.1/2/4为比较目标，采用一维电子数/S2观测谱。真实反冲谱与落入各观测箱的概率P_i(T)卷积。原生二维/四维likelihood作为附加能力单独登记。物理含义与来源见主文第5节。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>)

[返回目录](#toc)

<a id="inputs"></a>

## 已有数值与出处

| 输入 | 本轮实际数值/文件 | 直接出处与主文 |
|---|---|---|
| Detector | Qy原节点、总接受度、10个通用校准参数，2024核MISSING | [第5节同章数值和标准书目](<experiment.physics.v2.1.md#s5>) |
| 统计输入 | Run0/1 selection误差0.11/0.17，model误差0.17/0.16 | [第8节逐箱数据与原文约束](<experiment.physics.v2.1.md#s8>) |
| 一维benchmark误差 | 信号0.22、Cathode0.31、MD0.23 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |
| 下一步依赖 | 完整响应和统计形状/约束按能力列出 | [第10节输入交接](<experiment.physics.v2.1.md#s10>) |

[返回目录](#toc)

<a id="revision"></a>

## 本轮补充和反馈

本轮累计补充20个数值文件，主文逐章展示具体参数、数组与直接来源。用户确认本地暂无其他PandaX响应文件，并要求从实验文章提取。XENONnT 2024 Fig.1的三条接受度和两条SM真实反冲谱已进一步提取，完整矩阵为何不能由这些边际曲线唯一反演的说明见主文第5节。

继续追查实验的官方早期数据发布后，已取得YBe Qy/Ly各三表、单能响应基底及原始背景/信号参考模板，按官方重铸插值法整理名义一维响应。有据的早期响应数值现在已存在。精确复现的剩余核验是与2024 CEvNS原分析的等价性和重铸误差，来源[17]及实际数组见主文。

此前把原生多维拟合的附加输入合入本次一维目标，范围过宽。本版将一维P_i(T)的必要输入与原生多维likelihood依赖分开。

[返回目录](#toc)

<a id="handoff"></a>

## 下一步依赖

| 能力 | 实际状态 | 具体所需材料 |
|---|---|---|
| 一维重建谱 | PandaX八箱P_i(T) MISSING | 一维概率核或可生成它的校准模型，按第5节核对版本 |
| 一维benchmark统计 | D/B参考谱与归一化误差已有 | 前向响应与Fig.2通量扫描参数化核对 |
| 原生多维likelihood | 附加能力有独立缺口 | 原版多维形状、binning与校准约束 |
| Fig.4核物理 | 外部来源及匹配待核 | 核系数源表、归一化及算符对应 |

完整待补项与记录见 [下一步输入交接](<../../../../../../重构/20261106_Onboarding_provenance_revision/P02_MISSING_AND_HANDOFF.md>)。

[返回目录](#toc)
