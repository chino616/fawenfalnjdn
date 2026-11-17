# PandaX-4T 2024 US2 — Response onboarding v2.0 精简版（新版本）

版本日期：2026-11-06。[详细版 v2](<experiment.physics.v2.md>) · [用户资料 v2](<EXPERIMENT_USER_INPUT.v2.md>) · [标准参考文献](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md>) · [旧版原位入口](<../../../../../../../.experiment-auto-runs/cevns-threephase-20261105-high01/snapshot/docs/experiments/PandaX_4T/datasets/PandaX4T_SolarB8_Run0_Run1/EXPERIMENT_USER_INPUT.md>)

用户已指定使用完整探测器 Response；信号由真实反冲谱与含选择的重建概率核卷积，不使用作者逐箱 c_i。核响应模块与探测器响应分别登记。完整 response 已含的效率、涨落、增益和迁移不重复施加。

| 项目 | v2 当前内容与出处 |
|---|---|
| Source | Bahcall 官网完整四列谱形 [[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-4)；绝对通量参考值与误差单独来自 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) Sec.III |
| Target | NIST 九种天然 Xe 数丰度/原子质量 [[9]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-9)；不使用纯 Xe131，原子与裸核质量区分 |
| Detector | 完整 response 合同；Qy 三表与通用响应论文 Table II 的校准参数已补充，US2 sub-keV 核仍缺 |
| D/B | 332 事件八箱；原实验/再分析 B 分别保留；后续官方 CSV 做逐箱核对 |
| Runtime | 未新增 binding、未拟合；既有三个 COHERENT 输入与算法不变 |

PandaX：仍缺 US2 sub-keV、run-dependent 完整响应核/WS 参数及选取合同，缺二维 prefit B/精确 width edges/统计相关性。本次已取得的通用校准参数和 Qy 不自动填补这些缺口。

数据文件与严格来源逐项列于 [详细版第 9 节](<experiment.physics.v2.md>)，科学缺失不以任意 response 形状或 c_i 补齐。
