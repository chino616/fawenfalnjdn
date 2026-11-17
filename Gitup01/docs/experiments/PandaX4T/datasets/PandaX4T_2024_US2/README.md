# PandaX4T_2024_US2：onboarding版本

<!-- solar-nuclear-v31:start -->

## 当前SM onboarding：v3.1 原子核Response

[完整新版本：实际核表/代码/数据来源/逐箱结果](<experiment.physics.v3.1.md>) · [历史KN v3.0](<experiment.physics.v3.0.md>)。原包与旧结果保留；当前计算需显式使用核表入口，完整缺口见新版本。

<!-- solar-nuclear-v31:end -->

**历史统一阅读版本：v3.0，2026-11-09。** 详细版已整合Qy/Response、观测/背景、来源、SM与V/B−L结果及下一步依赖，不需要拼接旧版。

| 历史v3.0入口 | 用途 |
|---|---|
| [详细版v3.0](<experiment.physics.v3.0.md>) | 完整实验专属物理、实际数据、逐项来源、结果和交接 |
| [精简版v3.0](<experiment.physics.summary.v3.0.md>) | 快速阅读 |
| [用户资料v3.0](<EXPERIMENT_USER_INPUT.v3.0.md>) | 用户已确定的范围与补充项 |
| [两实验完整总文档](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>) | 单文件连续阅读PandaX与XENONnT |
| [主线进度](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/00_MIGRATION_PROGRESS.md>) | 实际Gate/科学接受保留 |
| [机器输入](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) · [完整数组](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) | 标准Runtime实际读取的YAML/NPZ |

PandaX原真实反冲诊断保留，SM简化Ne八箱已新增；完整US2 Ne响应仍MISSING。

**2026-11-10新增、已实际计算：PandaX SM简化平均映射八箱谱。** 采用R01 PDF p5式(11)–(13)、p6式(15)，nominal Qy来自R02 PDF p5 Fig.4下图；Total(US2)已含ROI且只乘一次，忽略分辨率。直接积分（项目c_i=1基线）为**25.851676事例**，SSM通量固定为5.46×10⁶。R02 PDF p6 Fig.5后验拟合谱乘5.46/8.4的历史参考为**48.654331事例**；它仍带实验拟合响应参数，不是同一基准响应下独立校准的SM预测，不作为验证。

[结果、逐步物理及标准文献引用](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/REPORT.md>) · [真正计算的八箱表](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/events_by_bin.tsv>) · [来源/方法参数卡](<../../../../../data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json>)

## 旧版历史（原位保留）

| 历史版本 | 当时主要内容 | 保留文件 |
|---|---|---|
| v2 | 最初Response方案 | [详细版](<experiment.physics.v2.md>) · [精简版](<experiment.physics.summary.v2.md>) · [用户资料](<EXPERIMENT_USER_INPUT.v2.md>) |
| v2.1 | 原文输入和来源修订 | [详细版](<experiment.physics.v2.1.md>) · [精简版](<experiment.physics.summary.v2.1.md>) · [用户资料](<EXPERIMENT_USER_INPUT.v2.1.md>) |
| v2.2 | SM执行补充 | [详细版](<experiment.physics.v2.2.md>) · [精简版](<experiment.physics.summary.v2.2.md>) · [用户资料](<EXPERIMENT_USER_INPUT.v2.2.md>) |
| v2.3 | V/B−L执行补充 | [详细版](<experiment.physics.v2.3.md>) · [精简版](<experiment.physics.summary.v2.3.md>) · [用户资料](<EXPERIMENT_USER_INPUT.v2.3.md>) |

旧版状态按其生成时间保留，当前SM能力以v3.1及其实际运行记录为准。
