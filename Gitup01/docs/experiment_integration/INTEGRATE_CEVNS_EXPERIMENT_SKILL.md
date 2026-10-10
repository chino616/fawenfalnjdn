---
name: integrate-cevns-experiment
description: >
  将任意 CEvNS 实验拆解为中微子通量、靶核组成、曝光、真实核反冲谱、
  探测器响应、效率、分析分箱和预期事例数，并以统一接口接入 CEvNS-pyEFT。
  适用于 SNS、反应堆、太阳中微子、加速器连续源和自定义表格通量。
---

# 1. 目标

对每个实验建立同一条物理链：

\[
\text{Flux}
\rightarrow
\text{Target inventory}
\rightarrow
\frac{d\sigma}{dT}
\rightarrow
\frac{dN}{dT}
\rightarrow
R(x\mid T)
\rightarrow
\epsilon(x)
\rightarrow
N_i.
\]

其中：

- \(E_\nu\)：中微子能量；
- \(T\)：真实核反冲能；
- \(x\)：实验实际拟合的重建观测量；
- \(R(x\mid T)\)：探测器响应核；
- \(\epsilon\)：探测效率；
- \(N_i\)：第 \(i\) 个分析 bin 的预期事例数。

实验模块不得复制 LEFT matching、核子 form factors、粒子响应、核响应、振幅平方或微分截面。

# 2. 必须提供的输入

每个数据集必须有一份实验物理规格，至少冻结：

```text
dataset identity
source and flux components
flux formula or data table
flux normalization and time basis
target isotopes and abundances
exposure
detector observable
quenching / yield
resolution or stochastic response
efficiency domain and data
analysis window and bin edges
numerical integration ranges
SM validation target
provenance for every numeric input
```

若 forward model 的必需输入仍为 `REQUIRES_INPUT`、`TBD` 或 `UNRESOLVED`，Codex 必须停止 publication 模式实现并报告缺项。

# 3. 代码分层

```text
theory
  LEFT coefficients -> ci -> particle responses -> amplitude -> dσ/dT

experiments
  source + target + exposure + detector response + bins

rates
  flux × dσ/dT -> dR/dT -> response folding -> expected counts

statistics
  observed data + backgrounds + covariance/likelihood
```

不得让实验文件定义第二套散射理论，也不得让通用 counts 引擎硬编码某个实验。

# 4. 通量接口

## 4.1 统一对象

```python
@dataclass(frozen=True)
class FluxComponent:
    name: str
    flavor: str
    production_component: str | None
    kind: Literal["continuous", "line"]
    time_basis: Literal["per_second", "integrated"]
    energy_min_mev: float
    energy_max_mev: float
    output_unit: str
```

- SNS 可使用 `prompt_numu`、`delayed_nue`、`delayed_numubar`；
- 反应堆只有一个味道 `nuebar`，但生产分量可为 `U235`、`U238`、`Pu239`、`Pu241`；
- 太阳源可使用 `pp`、`Be7_line`、`B8` 等分量。

## 4.2 连续通量

必须返回：

\[
\frac{d\Phi_c}{dE_\nu}.
\]

数据表必须声明：

```text
energy grid meaning: centers or edges
energy unit
spectrum unit
interpolation
out-of-range behavior
normalization convention
```

## 4.3 单能线

单能线必须单独保存线能量和积分权重，不得用窄 Gaussian 或粗网格伪造 Dirac delta。

## 4.4 时间基准

- `integrated`：单位通常为 `cm^-2 MeV^-1`，不能再次乘运行时间；
- `per_second`：单位通常为 `cm^-2 s^-1 MeV^-1`，必须乘 live time。

程序必须拒绝重复时间归一化。

## 4.5 通量归一化互斥

反应堆通量只允许以下之一：

```text
fixed detector-site total flux
```

或：

```text
thermal power + fission energies + baseline
```

不得同时用于归一化。未被选中的量只能作为一致性检查。

# 5. 靶核库存

所有材料都必须转换为每千克探测器中的同位素核数：

```python
@dataclass(frozen=True)
class IsotopeComponent:
    isotope: str
    response_key: str
    atomic_number: int
    mass_number: int
    number_fraction: float
```

统一输出：

```python
TargetInventory.nuclei_per_kg[isotope]
```

要求：

- 化合物通过化学计量和摩尔质量计算；
- 天然元素逐同位素计算；
- 单同位素近似必须显式命名，例如 `Ge73_only`；
- `response_key` 必须能在 nuclear-response 数据库中找到；
- 同位素丰度之和必须为 1，允许数值容差。

# 6. 曝光

```python
@dataclass(frozen=True)
class ExposureSpec:
    mass_kg: float | None = None
    live_time_s: float | None = None
    exposure_kg_day: float | None = None
```

只允许：

```text
mass_kg + live_time_s
```

或：

```text
exposure_kg_day
```

两者不能同时使用。若使用 kg·day，则通量仍是每秒量时，统一 counts 引擎负责 day-to-second 换算一次。

# 7. 真实核反冲谱

对靶核 \(a\) 和通量分量 \(c\)：

\[
\frac{dN_{ac}}{dT}
=
\mathcal E_a
\int_{E_{\nu,\min}(T)}^{E_{\nu,\max}}
 dE_\nu\,
\frac{d\Phi_c}{dE_\nu}
\frac{d\sigma_{ac}}{dT}.
\]

使用精确运动学：

\[
E_{\nu,\min}(T)=
\frac{T+\sqrt{T^2+2m_aT}}{2},
\qquad
T_{\max}(E_\nu)=
\frac{2E_\nu^2}{m_a+2E_\nu}.
\]

实验模块通过统一接口调用截面：

```python
differential_cross_section(
    isotope=isotope,
    flavor=flavor,
    recoil_kev=recoil_kev,
    enu_mev=enu_mev,
    theory_parameters=theory_parameters,
)
```

输出单位必须固定并测试，推荐 `cm^2/keVnr`。

# 8. 探测器响应

观测量不得统一假定为 PE。必须定义：

```python
@dataclass(frozen=True)
class ObservableSpec:
    name: str
    unit: str
```

响应拆成三层。

## 8.1 平均映射

\[
\bar x(T).
\]

例如 CsI 的 light yield × quenching，或 Ge 的 Lindhard ionization yield。

## 8.2 随机涨落/分辨率

\[
R(x\mid T),
\qquad
\int_{-\infty}^{+\infty}R(x\mid T)\,dx=1.
\]

支持：

```text
delta
poisson
gamma
gaussian
tabulated_matrix
custom
```

不得在分析窗口内重新归一化响应核。

## 8.3 效率

必须明确效率作用域：

```python
EfficiencySpec(
    domain="true_recoil"
           | "mean_observable"
           | "reconstructed_observable"
)
```

效率表必须定义插值、低端和高端外推行为。

# 9. 分箱

bin 必须定义在实验实际拟合的观测量上：

```python
@dataclass(frozen=True)
class BinningSpec:
    observable_name: str
    unit: str
    edges: np.ndarray
```

验证：

```python
assert edges.ndim == 1
assert len(edges) >= 2
assert np.all(np.diff(edges) > 0)
```

第 \(i\) 个 bin：

\[
N_{aci}
=
\int_{x_i}^{x_{i+1}}dx\,
\epsilon(x)
\int dT\,
R(x\mid T)
\frac{dN_{ac}}{dT}.
\]

# 10. 输出契约

```python
@dataclass
class BinnedPrediction:
    bin_edges: np.ndarray

    # target × source_component × bin
    counts_by_target_source: np.ndarray
    target_names: tuple[str, ...]
    source_names: tuple[str, ...]

    counts_by_target: np.ndarray
    counts_by_source: np.ndarray
    counts_total: np.ndarray
    total_events: float

    diagnostics: dict
    provenance: dict
```

必须满足：

```python
assert counts_total.shape == (len(bin_edges) - 1,)
assert np.all(counts_total >= 0)
assert np.allclose(
    counts_total,
    counts_by_target_source.sum(axis=(0, 1)),
)
```

多探测器实验在最外层增加 detector 轴：

```text
detector × target × source_component × bin
```

# 11. 慢速与快速实现

每个数据集先创建慢速物理基准：

```text
slow_counts_<dataset>.py
slow_counts_<dataset>_check.ipynb
```

慢速实现：

- 直接执行完整积分；
- 不依赖预计算 EFT kernel；
- 保留 detector/target/source/bin 分量；
- 使用小网格 notebook 做人工检查；
- 使用正式测试做回归。

快速实现可以缓存：

- 运动学 mask；
- 与 EFT 参数无关的通量积分部分；
- detector response matrix；
- cumulative bin integrals。

但必须与慢速实现逐 bin 比较。

# 12. 数据来源与文件契约

每个数据文件必须在相邻 README 中标记来源类型：

```text
official_table
supplementary_material
author_repository
digitized_figure
legacy_code
user_supplied
synthetic_test_only
```

必须记录：

```text
publication / DOI / arXiv
figure/table/equation identifier
units
column meanings
interpolation
transformations applied
checksum
```

不得把数字化曲线称为官方表格，不得把占位模板称为数据。

# 13. Codex 执行顺序

1. 读取本 Skill；
2. 读取具体实验 MD；
3. 运行数据验证脚本；
4. 列出所有 `REQUIRES_INPUT`；
5. publication 模式若有核心缺项则停止；
6. 先实现通量、靶核、响应的独立测试；
7. 再实现慢速 counts；
8. 保存标准模型 reference；
9. 再实现 fast 路径；
10. 注册实验；
11. 运行 pytest 与检查 notebook。

# 14. 每个新实验至少创建

```text
experiments/datasets/<dataset>.py
experiments/datasets/slow_counts_<dataset>.py
experiments/datasets/slow_counts_<dataset>_check.ipynb
data/experiments/<dataset>.yaml
tests/test_<dataset>_flux.py
tests/test_<dataset>_target.py
tests/test_<dataset>_response.py
tests/test_<dataset>_counts.py
tests/reference/<dataset>_sm_counts.npz
```

# 15. 禁止事项

- 不得在实验文件中重写截面；
- 不得混用不同年份或不同站点的数据；
- 不得重复乘时间、质量、通量或每千克核数；
- 不得把 keVnr、keVee、eVee、PE 混用；
- 不得猜测 efficiency 的作用变量；
- 不得默认天然材料只有一个同位素；
- 不得把观测最佳拟合值用作 forward model 的人工归一化；
- 不得通过更新 reference 掩盖数值差异；
- 不得在缺少官方数据时声称复现完整 likelihood。

# 16. 完成标准

只有同时满足以下条件才算接入完成：

- 通量积分和单位通过测试；
- 靶核库存通过测试；
- 每个同位素调用正确核响应；
- 真实反冲谱可单独输出；
- 探测器响应核归一；
- efficiency 作用域明确；
- bin edges 与规格一致；
- 所有分量轴被保留；
- slow 与 fast 在约定容差内一致；
- 标准模型基准通过；
- 所有数据文件有来源和校验和；
- registry 只做名称到构造函数的映射。
