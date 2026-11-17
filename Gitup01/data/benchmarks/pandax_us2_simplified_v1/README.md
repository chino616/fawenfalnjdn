# PandaX US2：SM简化平均映射参数卡 v1

2026-11-10；用户指定“请你根据简化方法处理”。

[benchmark.input.json](benchmark.input.json)逐项记录公式、原文位置、数据身份、处理约定、Qy曲线选择、c=1基线、条件有效校准、输入哈希与标准参考文献。复用既有正式包，未新建实验注册。

- [运行工具](../../../tools/run_pandax_us2_simplified_benchmark.py)：标准Runtime→共享SM反冲积分→逆Qy箱界积分。
- [实际输出与图](../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/README.md)。
- [当前onboarding v3.0](../../../docs/experiments/PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v3.0.md)。
- [上级benchmark目录](../README.md)。

原始c_i未取得。重建值以实验Fig.5纯信号及8.4×10⁶拟合通量为条件锚点；校准闭合不是独立验证。

SSM口径更正：直接计算固定5.46×10⁶；卡内effective_calibration是历史后验拟合谱缩放参考，未独立验证Response。当前说明见[角色核对](../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/SSM_REFERENCE_ROLE_AUDIT.json)。
