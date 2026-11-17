# XENONnT 2024 Solar 8B — Response onboarding v2.0 精简版（新版本）

版本日期：2026-11-06。[详细版 v2](<experiment.physics.v2.md>) · [用户资料 v2](<EXPERIMENT_USER_INPUT.v2.md>) · [标准参考文献](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md>) · [旧版原位入口](<../../../../../../../.experiment-auto-runs/cevns-threephase-20261105-high01/snapshot/docs/experiments/XENONnT/datasets/XENONnT_SolarB8/EXPERIMENT_USER_INPUT.md>)

用户已指定使用完整探测器 Response；信号由真实反冲谱与含选择的重建概率核卷积，不使用作者逐箱 c_i。核响应模块与探测器响应分别登记。完整 response 已含的效率、涨落、增益和迁移不重复施加。

| 项目 | v2 当前内容与出处 |
|---|---|
| Source | Bahcall 官网完整四列谱形 [[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-4)；绝对通量参考值与误差单独来自 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) Sec.III |
| Target | NIST 九种天然 Xe 数丰度/原子质量 [[9]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-9)；不使用纯 Xe131，原子与裸核质量区分 |
| Detector | 完整 response 合同；已补齐两 run 的完整 7×7×46×81 更新版本概率模板，2024 适用性未证明 |
| D/B | 37 个官方事件、各 run 81 箱 D；原图 B 与 2026 版本 B 分开 |
| Runtime | 未新增 binding、未拟合；既有三个 COHERENT 输入与算法不变 |

XENONnT：完整后续 Response 和 B 已能回读，2024 原版响应/后续校准追溯适用性尚未证明；run 曝光、响应支撑外贡献、nuisance prior/covariance 和官方推断校准仍需对应版本证据。

数据文件与严格来源逐项列于 [详细版第 9 节](<experiment.physics.v2.md>)，科学缺失不以任意 response 形状或 c_i 补齐。
