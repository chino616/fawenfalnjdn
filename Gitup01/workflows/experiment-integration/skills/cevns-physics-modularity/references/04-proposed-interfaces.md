# 04 建议的模块接口与渐进重构

**全文为 PROPOSED 设计，不是当前可 import 的 API。** 不要求一次创建所有文件；先在已授权的替换场景中抽离最小职责。
目前实际存在的 NeutrinoState、PropagationState、ResponseDB、共享截面继续作为适配基础。

## 1. 模块化应满足的可替换条件

每个接口定义输入输出变量、单位、轴、粒子类别、物理支撑、默认假设、异常、参数和 provenance。
“通用”需要 source/target/detector 通过参数或 provider 输入，不能在核心内导入某个实验。
同一物理公式只保留一个可测试 owner；实验 adapter 仅实现材料/源的专有模型或单位桥接。
源谱本身可有专用实现，通用接口不能预设一定是 e/mu/mub、一定含 prompt 线、一定是 PE。

| 设计层 | 应保存 | 不应保存 |
| --- | --- | --- |
| 数据/参数 | 数值、单位、来源、校准版本、运行期 | 自动改变其它层的隐式全局开关 |
| 纯物理 provider | 有边界的公式或数表求值 | I/O 路由、最终事件归一化、绘图修正 |
| 积分与编排 | 源/靶/探测器求和、单位桥接、求积 | 再复制 Michel/LEC/R/效率公式 |
| 加速/缓存 | 已说明数学含义的中间对象 | 未记录物理依赖的通用“kernel” |
| 统计 | 数据语义、背景、系统误差、推断 | 隐式调整 signal normalization |

## 2. 建议的内部单位与轴

建议新通用积分边界统一 E_GeV、T_GeV、q_GeV、q2_GeV2。
source differential flux/fluence 每 GeV；cross section cm²/GeV；detector x 保留声明的物理单位。
这只是新接口方案，不要求直接改变旧公开 MeV/keV API。

旧 rates 截面适配示意：

```python
# PROPOSED adapter sketch，变量来自实际 provider。
E_MeV = E_GeV * 1e3
T_keV = T_GeV * 1e6
# 旧 API 给 cm²/keV，转回新约定 cm²/GeV 要乘 1e6。
dsigma_cm2_per_GeV = legacy_dsigma_cm2_per_keV * 1e6
```

连续源 cm^-2 MeV^-1 转 cm^-2 GeV^-1 要乘 1e3；谱线权重 cm^-2 不变。
响应密度 P(x|T) 单位 x^-1，bin acceptance 无量纲；dT 权重是 GeV，不是再次乘 1e-6 的 keV。
各 adapter 的往返换算应使用同一物理测试点验证，而不是只比较单位字符串。

建议保留 `(detector, run, source, isotope, bin)` 分量元数据；维数可省略单例轴，但不能丢失含义。
flavor 矩阵轴固定最后两个维度，源/能量/靶轴单独命名。`A` 质量数、`target` 轴、`J` 核自旋不能混用。

## 3. SourceComponent 与 SourceProvider

下列是契约示意，不需要照抄成特定类层次：

```python
@dataclass(frozen=True)
class SourceComponentSpec:
    component_id: str
    particle_kind: str
    time_basis: str              # per_second / time_integrated
    support_GeV: tuple[float, float]
    includes_time_or_pot: bool
    normalization_description: str
    provenance: str

class SourceProvider(Protocol):
    def components(self): ...
    def continuum(self, component_id, energy_GeV, *, time=None): ...
    def lines(self, component_id, *, time=None): ...
    def breakpoints_GeV(self, component_id): ...
```

每条 line 返回 energy_GeV、integrated_weight、unit/source_id；lines 可以为空。
time_integrated 时权重 cm^-2；per_second 时权重 cm^-2 s^-1。不能把是否有时间轴靠数组形状猜出来。
SourceProvider 不知道 target mass、EFT、response/bin；时间积分后 source 已含曝光因子必须在 spec 明示。
组件 ID 可为 prompt_mu、solar_B8、reactor_core_1_nubar_e；其 flavor/particle 由状态接口定义。

## 4. IncidentStateProvider 与传播

```python
class IncidentStateProvider(Protocol):
    def state(self, component_id, energy_GeV, *, time=None,
              propagation_parameters=None): ...
```

输出带实际 energy_GeV、basis、particle_kind 的 rho，适配现有 PropagationState/NeutrinoState。
常量态对任意子网格广播；能量态在请求的真实网格上返回正确 rho，而不是只接受一个 shape。
line 的 energy 也通过这个接口求值。先抽取实际数组再调用当前截面，不把旧整网格态原样用于掩码后的子网格。
状态 provider 可以依赖传播参数，但不依赖靶或探测器；检测和传播的 Wilson 关联由上层模型管理。

## 5. TargetInventory 与 Exposure

建议每核素存 isotope_id、response_key、Z/N/J、nucleus_mass_GeV、nucleus_mass_kg、fraction_convention、fraction。
以明确的同位素质量把 number_fraction 转成 mass_fraction；验证质量单位和核数。

```python
class TargetInventory(Protocol):
    def isotopes(self, detector_id): ...
    def nuclei_per_kg(self, detector_id, isotope_id): ...

class ExposureProvider(Protocol):
    def active_mass_kg(self, detector_id, run_id): ...
    def time_factor(self, detector_id, run_id, source_time_basis): ...
```

time_factor 返回数值和单位的显式记录。对于 time_integrated fluence，返回 1（无量纲）；不能返回单位 s 的运行时间再乘。
对 per_second flux，返回秒数或进入真正的时间积分。质量只在这一层声明，不再藏进 source metadata。
一个运行期的 accepted exposure 与 time efficiency 可能不是简单相乘，要根据合同避免重复 dead-time 修正。

## 6. WilsonModel、HadronicMatching 与 NuclearResponseProvider

- WilsonModel：把用户模型参数转成有量纲、basis 固定的 LEFT 矩阵；NP-only 输入清楚标记。
- SM coefficient provider：在检测振幅前合并，与 Fast coefficient builder 共用。
- HadronicMatching：C→ci，显式依赖 lecs、q0/q²/qabs² 与截断阶数，不加载实验源。
- ParticleResponseProvider：ci+kinematics→R，各 sector 保持正交；Slow 与 Fast 共用公式构造。
- NuclearResponseProvider：isotope/channel/q 或 y→W，带 basis、normalization、current truncation 和来源标识。

建议换模型用 provider 选择，不把 JSON 内部换一套规范而沿用旧标签。
SMEFT/RG 如新增，应作为 WilsonModel 上游的独立转换，不塞进事件积分器。
form_factors.py 与 left_to_ci 的关系要按实际实现决定，不能为“看起来模块化”而增加一条没有物理依据的调用。

## 7. KinematicsProvider 与 CrossSectionProvider

```python
class KinematicsProvider(Protocol):
    def recoil_max(self, energy_GeV, target): ...
    def energy_min(self, recoil_GeV, target): ...
    def transfer(self, energy_GeV, recoil_GeV, target): ...

class CrossSectionProvider(Protocol):
    def kernel(self, target, energy_GeV, recoil_GeV, *,
               wilson, particle_kind, theory_options): ...
```

kernel 输出 cm²/GeV 的入射 flavor 矩阵，或由独立 contraction 给标量；两者不可混用返回类型。
新的 particle_kind 参数只有在实际实现 ν/反ν振幅时才宣称支持；否则显式报告限制。
transfer 返回 q0/q2/qabs/qabs2 及 exact/approx convention，所有响应和 pole 消费同一对象。
Helm provider 与 full-response provider 分开声明适用 EFT 空间，禁止暗中互相乘 form factor。

## 8. DetectorResponseProvider、Selection 与 Binning

```python
class DetectorResponseProvider(Protocol):
    def mean(self, isotope_id, recoil_GeV, detector_id): ...
    def density(self, x_reco, isotope_id, recoil_GeV, detector_id): ...
    def efficiency(self, x_reco, detector_id): ...
    def bin_acceptance(self, bin_edges, isotope_id, recoil_GeV,
                       detector_id): ...
```

不是每个模型都必须暴露 mean/density：已有 probability-per-bin matrix 时可直接实现 bin_acceptance，
但必须说明已含哪些因子。bin_acceptance 只表示探测器概率，不应暗含 source、nuclei、质量或 dT。
分量选择 a_s 独立于 detector density；依赖 E/t/T 时增加选择函数并留在正确积分内。
bin spec 保存 observable_name/unit/edges/discrete_or_continuous，事件函数输出同一 spec。

## 9. 通用 Slow 的建议求值顺序

```text
for detector, run:
  读取 target inventory / exposure / bin spec
  for source_component, isotope:
    构造覆盖实际源支撑及谱线的 T 网格
    for T:
      E_min = kinematics.energy_min(T, target)
      在各连续谱支撑与 E_min 的交集求积分
        同一 E 子网格求 source(E)、rho(E)、cross_section(E,T)
      每条线单独求 state(Eline)、cross_section(Eline,T) 与支撑
      得到 per-nucleus true recoil yield
    detector.bin_acceptance(T) 只做一次或使用已验证响应矩阵
    ∫dT 后乘 nuclei_per_kg × active_mass × 未含时间因子
    保存每源/每靶分量
  最后汇总 total 并输出 bin observable
```

也允许先乘核数再积分或在有效条件下交换积分顺序，但归一化 ledger 和输出单位保持一致。
只在确有性能收益且满足准确度时预计算响应矩阵；不必为了设计完整而强迫所有实验使用同一种数值表示。

## 10. Fast 共享的底层表达式

当前 builder 把 responses_R 重写成系数空间公式，是核心漂移风险。
建议后续采用能在标量系数、flavor 矩阵或 basis transfer 上求同一双线性的公共表达式，
或从统一的 amplitude bilinear evaluator 导出 h；不要要求每加一个算符手抄两套物理公式。
实施这种抽取前，先覆盖复相位、混合通道、sector、Hermitian 化与现有逐箱回归。

探测器响应矩阵可与源无关；振幅 h 可与 source/detector 无关；已积分 H 则含其实际积分过的输入。
把不同缓存分开，改变源时只失效源积分及其下游，避免无谓重算核结构或 detector matrix。

## 11. 建议文件布局与迁移顺序

以下目录是 PROPOSED，不代表已经创建：

```text
sources/components.py           连续谱/谱线及 source spec
sources/state.py                复用现有状态，并按需要增加显式网格桥接
targets/inventory.py             同位素与 nuclei/kg
experiments/<family>/source.py   专有源物理或数表
experiments/<family>/detector_response.py
experiments/<family>/slow_counts.py  仅组装已选择的 providers
rates/integration.py            source/state/cross-section 的通用能量积分
rates/folding.py                反冲谱与 detector acceptance 的积分
kernels/<representation>.py     按数学对象分缓存与重建
statistics/...                 继续与 forward model 分离
```

渐进顺序：

1. 固定当前逐源逐靶逐箱输出、单位、归一化和已知限制。
2. 先分离静态数据与真正的配置消费，不改变公式。
3. 抽 source support/continuous/lines，消除积分器的 mu/e/mub 和 μ 端点绑定。
4. 抽 detector provider，显式透传，消除 counts 中已绑定默认函数的隐式影响。
5. 抽真反冲谱求值，再抽 fold/bin，保留旧入口做兼容 wrapper。
6. 在测试保护下统一 Slow/Fast 物理表达式，增加内容依赖缓存元数据。
7. 最后让 registry/spec/predictor 通过真实能力路由，而非仅按名字复制旧行为。

每一步只落地当前授权与物理合同要求的部分，给出前后数值、受影响实验和仍未完成的能力。
不把“已写好模块接口设计”报告成“运行代码已完成模块化”。
