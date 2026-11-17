# PandaX4T_2024_US2：数据、正式输入与来源

<!-- solar-nuclear-v31:start -->

## 当前SM onboarding：v3.1 原子核Response

[完整新版本：实际核表/代码/数据来源/逐箱结果](<../../../../docs/experiments/PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v3.1.md>) · [历史KN v3.0](<../../../../docs/experiments/PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v3.0.md>)。原包与旧结果保留；当前计算需显式使用核表入口，完整缺口见新版本。

<!-- solar-nuclear-v31:end -->

2026-11-09。当时说明统一为[onboarding v3.0完整整合版](<../../../../docs/experiments/PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v3.0.md>)；[两实验总文档](<../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>)。

| 实际内容 | 使用方式/性质 |
|---|---|
| [experiment.input.yaml](<experiment.input.yaml>) | 正式标量/模型合同权威 |
| [experiment.resources.npz](<experiment.resources.npz>) | 9个正式数值数组；标准Runtime读取 |
| detector/、statistics/、reference/及根目录原表 | 14份辅助数值；来源、轴、shape、采用/候选身份见v3.0第9章 |
| [完整机器可读来源清单](<../../../../outputs/solar_b8_onboarding_v3/20261109_layout_r1/NUMERICAL_INVENTORY.json>) | 每文件/正式键的哈希、单位、范围、代表值、原文定位、转换和当前用途 |
| experiment.physics.md / experiment.physics.summary.md | 原Compiler包内派生说明保留；该历史包派生说明对应docs中的v3.0；当前SM阅读v3.1，不将旧模板通用“未绑定”文字当作当前执行事实 |


SM简化Ne八箱采用nominal Qy与正式总接受度，固定SSM通量、c=1。后验拟合谱缩放仅作参考，未独立校准Response。原真实反冲投影与完整Ne箱Response缺口保留；259日CSV不冒充2024完整事件原件。

原始表、正式包与旧数值结果字节未变；旧onboarding保留原位。没有恢复旧七份遗留辅助表的读取。

**2026-11-10新增、已实际计算：PandaX SM简化平均映射八箱谱。** 采用R01 PDF p5式(11)–(13)、p6式(15)，nominal Qy来自R02 PDF p5 Fig.4下图；Total(US2)已含ROI且只乘一次，忽略分辨率。直接积分（项目c_i=1基线）为**25.851676事例**，SSM通量固定为5.46×10⁶。R02 PDF p6 Fig.5后验拟合谱乘5.46/8.4的历史参考为**48.654331事例**；它仍带实验拟合响应参数，不是同一基准响应下独立校准的SM预测，不作为验证。

[结果、逐步物理及标准文献引用](<../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/REPORT.md>) · [真正计算的八箱表](<../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/events_by_bin.tsv>) · [来源/方法参数卡](<../../../benchmarks/pandax_us2_simplified_v1/benchmark.input.json>)
