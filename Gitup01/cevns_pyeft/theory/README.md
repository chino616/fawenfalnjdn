# theory：相互作用公式与运动学

<!-- solar-singlebin-v321:start -->

## 太阳⁸B：单 bin独立能力

[li2026/sm_quadratic.py](li2026/sm_quadratic.py)为SM-only薄适配：委托既有Li2026LegacyInteraction取得三个合法能量点，精确重组E²dσ/dT二次式。无探测器/太阳模块依赖，不抄写匹配公式、核表或额外KN因子。核表与原共享核心未改；新适配与旧API逐点比较、端点及既有COHERENT冻结回归分别检验。

<!-- solar-singlebin-v321:end -->

本层负责截面中的物理公式，不施加源通量、探测器质量、曝光或效率。内置 COHERENT 装配使用 `li2026.adapter.Li2026LegacyInteraction`；`helm/` 提供另一套低层 Helm 计算接口，没有作为默认后端自动替换进去。

## Li2026 的真实调用链

```text
rates/differential.py：整理 Wilson 输入、注入所请求的 SM 系数
  → li2026/cross_section.py：运动学支撑、相空间因子和 cm² 换算
  → li2026/amplitude.py：构建味空间核
      → left_to_ci.py：LEFT → 核子系数
      → responses.py：粒子响应 R
      → nuclear/response.py：核响应 W
  → 与 rho 收缩；公共 rates 接口换算为 cm²/keV
```

[kinematics.py](kinematics.py) 管理两体端点和最低入射能；[li2026/](li2026/) 还包含算符规则、味矩阵校验、LEC 与形状因子；[helm/](helm/) 用 Helm 形状因子和弱荷矩阵构造截面核。

## 为什么这样拆分

LEFT 匹配、粒子响应与核表来源有不同职责。`li2026/responses.py::_response_polynomials` 是 Slow 味矩阵和 Fast 系数响应共同使用的公式入口，避免两份多项式各自演化。核表数值由外部 `data/responses/` 管理。

## 管理与新增文件

现有理论的扩展放对应子包；独立理论可创建新的子包和 `__init__.py`，提供 `InteractionModel` 适配器并由实验 `prepare`/`components` 明确装配。不要只新增公式文件就修改所有实验的默认理论。

新增算符需一起核对 `operators.py` 的合法性/味规则、`left_to_ci.py` 匹配、R 响应、系数表示和 Fast 能力；某一路径未实现时应明确拒绝。检查单位、密度矩阵、运动学支撑、干涉项、Fast–Slow 及三个实验的冻结回归。相关理论论文见 [通用 CEvNS 文献](../../docs/references/General_CEvNS/README.md)，共享 nu/antinu 核的限制仍需保留。

---

[上一级](../README.md) · [项目总览](../../README.md)

<!-- solar-b8-sm-20261107:start -->

## Solar B8 SM profile

[sm_coherent.py](sm_coherent.py)提供2411.11749v1式(1)–(3)的纯SM/KN共享模块，参数来自正式包；原EFT与Helm实现不变。

<!-- solar-b8-sm-20261107:end -->

<!-- solar-vector-20261108:start -->

## Solar B8 vector benchmark

[light_vector.py](light_vector.py)在既有StandardModelKN核上加入味普适轻矢量V/B−L弱荷与干涉，采用JCAP05(2025)012式(2.6),(2.10)。不接受一般LEFT系数；测试点与物理适用性见主报告。

<!-- solar-vector-20261108:end -->

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

li2026/ee_vector_nsi.py负责Eq95实数ee-uV/dV，委托原Li2026核Response振幅，保留其他味SM散射。

[完整新onboarding：实际输入、标准引文、物理与程序](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->
