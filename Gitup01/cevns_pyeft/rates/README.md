# rates：对截面、源和探测器做数值积分

本目录把微观截面变成反冲产额或可观测箱贡献。CsI2021 的 `core.predict` 直接调用这里的 `recoil` 和 `folding`；旧实验和绘图入口还使用 `differential`、`counts`。

| 文件 | 实际责任与单位 |
|---|---|
| [differential.py](differential.py) | 将 Wilson/SM 输入、核响应和入射态接到 Li2026；公共能量边界使用 MeV/keV，输出 cm²/keV |
| [recoil.py](recoil.py) | `integrate_recoil_yield` 对连续谱做梯形积分、另加离散谱线；查询实际能量处的 rho，返回每核、每 keV 产额 |
| [folding.py](folding.py) | `legacy_density_fold`、`probability_fold` 与 Fast 使用的线性权重；区分响应概率和求积权重 |
| [legacy_observables.py](legacy_observables.py) | 包内 profile 共用的确定性 PE 和观测值相关 Gaussian 求积/折叠；保留 CsI2017 固定节点与原 bin-edge 插值，参数由 YAML/NPZ 装配 |
| [counts.py](counts.py) | 旧计数路径共用的反冲率/积分辅助，包含 `_rate_per_kg` |
| [mass_time.py](mass_time.py) | `segmented_recoil_rate` 用分段 Gauss–Legendre 求积，将每秒通量归一为 events/(kg day keVnr) |

在组合式路径中，源的 `for_run` 已经包含曝光；`recoil` 不再乘 POT，`folding` 不再乘真实核数，`core.predict` 最后施加核数。把这几个阶段分开，可以检查重复归一化，也可以让 Slow 与 Fast 使用相同的折叠约定。

## 管理与新增文件

新通用求积/折叠算法放对应模块，独立算法可另建文件。先明确输入是否含时间、质量、效率及输出单位，再由 `core` 或某实验 executor 显式选择。截面公式变化应回到 `theory/`，实验特有网格和参数放 definition/executor。

如果新增数值策略，需同时更新 `IntegrationSettings` 的合法值、能力检查和实际消费分支；仅增加一个配置键会被统一入口拒绝。检查运动学支撑、连续谱与谱线、箱边界、接受率一次性应用及三个实验回归；参考 [test_rates_differential_flavor.py](../../tests/test_rates_differential_flavor.py) 和 [test_refactor_csi2021_regression.py](../../tests/test_refactor_csi2021_regression.py)。

## 共享响应默认值

CsI淬火/Gamma微分率在未显式传参时读取detectors/legacy_parameters.py的原有默认值，避免通用率函数依赖某个dataset的专用文件。参数值、公式、积分端点与单位未改变；可拆装状态由实验Catalog和管理器负责。

---

[上一级](../README.md) · [项目总览](../../README.md)
