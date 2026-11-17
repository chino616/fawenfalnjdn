# XENONnT_2024_SolarB8：数据、正式输入与来源

<!-- solar-nuclear-v31:start -->

## 当前SM onboarding：v3.1 原子核Response

[完整新版本：实际核表/代码/数据来源/逐箱结果](<../../../../docs/experiments/XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v3.1.md>) · [历史KN v3.0](<../../../../docs/experiments/XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v3.0.md>)。原包与旧结果保留；当前计算需显式使用核表入口，完整缺口见新版本。

<!-- solar-nuclear-v31:end -->

2026-11-09。当时说明统一为[onboarding v3.0完整整合版](<../../../../docs/experiments/XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v3.0.md>)；[两实验总文档](<../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>)。

| 实际内容 | 使用方式/性质 |
|---|---|
| [experiment.input.yaml](<experiment.input.yaml>) | 正式标量/模型合同权威 |
| [experiment.resources.npz](<experiment.resources.npz>) | 17个正式数值数组；标准Runtime读取 |
| detector/、statistics/、reference/及根目录原表 | 31份辅助数值；来源、轴、shape、采用/候选身份见v3.0第9章 |
| [完整机器可读来源清单](<../../../../outputs/solar_b8_onboarding_v3/20261109_layout_r1/NUMERICAL_INVENTORY.json>) | 每文件/正式键的哈希、单位、范围、代表值、原文定位、转换和当前用途 |
| experiment.physics.md / experiment.physics.summary.md | 原Compiler包内派生说明保留；该历史包派生说明对应docs中的v3.0；当前SM阅读v3.1，不将旧模板通用“未绑定”文字当作当前执行事实 |


当前信号使用R17早期YBe基底和正式中位产额；R08的2026模板只是候选。官方观测、名义背景、图线拟合参考分别标注。

原始表、正式包与旧数值结果字节未变；旧onboarding保留原位。没有恢复旧七份遗留辅助表的读取。
