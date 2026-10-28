# 源、运行期与入射态接口

状态：DESIGN。依赖：[02](02_ARCHITECTURE_AND_DECISIONS.md)。接口审阅：[09](09_MODULE_INTERFACE_REVIEW.md)。

## 1. 最小公开边界

建议在 `contracts/source.py` 定义源合同，在 `sources/` 放实际模型。

```python
# DESIGN：符号为待实现接口；省略具体类型导入和运行时校验。
class SourceModel(Protocol):
    def for_run(self, run: RunExposure) -> DetectorFluence: ...
    def describe(self) -> ModuleDescriptor: ...

class FluenceComponent(Protocol):
    component_id: str
    particle_kind: str
    support: EnergySupport
    lines: tuple[FluenceLine, ...]

    def continuum(self, energy_MeV: np.ndarray) -> np.ndarray: ...
    def state_at(self, energy_MeV: np.ndarray, *,
                 parameters: StateParameters) -> IncidentStateBatch: ...
```

`DetectorFluence` 包含组件元组、运行期标识、源归一化记录与来源记录。没有探测器质量字段。
组件 ID 可为 `prompt_numu`、`delayed_nue`、`reactor_core_1`；它不是味指标，也不能用于决定有无谱线。
旧接口的 `mu/e/mub` 在 legacy adapter 中映射到稳定 ID，旧输出包装器再映射回来。

## 2. 能量向量与状态合同

新数值边界统一使用一维能量数组 `(n_E,)`；谱线使用长度为 1 的查询数组。用户级便利函数可包装标量，但不向核心传播多种不明确 shape。

`IncidentStateBatch` 至少包含：

| 字段 | 约束 |
|---|---|
| `energy_MeV` | 与本次请求的真实能量值一致，不仅是长度相同 |
| `rho` | `(n_E,3,3)`；基底固定为 `(e,mu,tau)` |
| `particle_kind` | `nu` 或 `antinu`；不由 source ID 猜测 |
| `state_model_id` | 状态/传播模型标识 |
| `parameter_dependencies` | 是否依赖当前理论点、传播参数、时间或路径 |

逐能量校验 Hermitian、PSD、trace=1，并使用明确的数值容差。
常量态通过 provider 广播；能量依赖态在请求网格求值或按已记录规则插值。
采用非负凸权重线性插值可以保持密度矩阵的 PSD 和 trace；不能默认高阶样条保留这些性质。
不覆盖域的状态查询须报错或执行显式的物理外推策略，不能取第一个矩阵代替。

当前 `NeutrinoState` 可复用其校验逻辑；当前 `PropagationState` 已携带能量网格，可通过适配器对接。
中性数学校验最终可移动到独立于 Li2026 的位置，并保留旧 import re-export；不在初始阶段强制搬动所有 flavor 文件。

`StateParameters` 由当前 TheoryPoint 中明确声明的传播/入射态参数映射生成；常量态使用空参数对象。积分器每次查询都传入本次参数，不能在创建源时冻结一个会随扫描改变的状态。物理模型负责定义传播参数与检测参数的关联，接口不擅自假定二者相同。

## 3. 连续谱、谱线与支撑

`continuum(E)` 返回 `cm^-2 MeV^-1`，shape 为 `(n_E,)`，非负且有限。
`FluenceLine` 包含 `line_id`、`energy_MeV`、`fluence_per_cm2`；它的权重是积分量，不是某个任意窄峰的峰高。
允许无连续谱、无谱线、多条谱线；完全空源需明确作为零源测试对象，而非资料缺失的默认补零。
每条谱线在其自身能量执行运动学支撑和入射态查询。

`EnergySupport` 至少区分：

- `integration_domain_MeV`：本数值版本采用的积分区间。
- `tabulation_domain_MeV`：数表覆盖区间，可为空。
- `physical_domain_MeV`：有证据支持的物理支撑；未独立确认时不得假填。
- `breakpoints_MeV`：需要数值分段的阈值或拼接点。
- `outside_policy`、`interpolation_id`、`convention_id`。

旧 SNS 的表格网格、56 MeV 节点筛选和 μ 衰变积分端点分别记录。适配时保留原计算路径，不将 56 MeV 写成理想 Michel 谱的物理端点，也不重新归一化尾部来使积分“看起来更正确”。
新通用积分器从组件读取积分区间，不再调用 `emax_muon_dar_mev()` 来决定所有源的能区。
源 adapter 可以内部调用该物理函数以生成 SNS 的已声明支撑。

## 4. 运行期和归一化

原始输入用互斥的归一化类型表达：

| 类型 | 源输入 | `for_run` 的工作 |
|---|---|---|
| `PerPOTSource` + `POTExposure` | 每 POT 的源产额与几何信息 | 乘该运行期 POT，得到探测器位置积分注量 |
| `DifferentialFlux` + `LiveTimeExposure` | 每秒探测器位置通量或可计算的时变通量 | 对实际运行时间积分 |
| `IntegratedFluenceInput` + `IntegratedRunReference` | 已包含指定运行期的绝对注量 | 检查运行期及来源，不重复积分 |

源模型不兼容某种运行期类型时，抛出 `IncompatibleNormalizationError`。
禁止构造同时要求乘 POT 和活时间的含混默认运行期。
更复杂的运行期分段可以逐段构造 fluence 再相加，不强行使用单一平均源。

源归一化记录至少包括：几何已包含与否、运行期因子、输入/输出单位、资源哈希、所用参数。若数据已是探测器位置绝对谱，就不再施加几何衰减。
全运行期的 dead time 归属 `LiveTimeExposure` 时，后续选择模型不得重复施加同一损失；逐事件时间选择另外处理。

## 5. 适配现有 SNS

`sources/sns.py::SNSLegacySource` 的首版行为：

1. 调用或复用 `experiments/coherent/sns.py` 的谱和归一化公式。
2. 把 `measured.e/mub` 转为连续组件，把 `muLine` 转为一个谱线组件。
3. 保留现有 200 节点线性插值与实际积分端点。
4. 通过既有 `sns_component_state` 生成相同的入射态约定。
5. 不把 `basic.detectorMassKg` 传给新积分器；质量来自靶核清单。
6. 记录 legacy antinu 约定，不能从标签推断已经实现反粒子振幅转换。

第一版包装现有 loader 不等于它已经支持任意外部参数。对外公开的参数必须确实被 loader/函数消费。
如果旧 loader 只能按 dataset 名取全局常量，先抽出一个接收显式不可变 SNS 参数的纯构造函数；旧 loader 委托它。禁止临时改写 `SNS_DATASETS` 再改回来。

## 6. 不确定度与传播

谱形/源强不确定度作为模型参数和依赖声明；源模块不执行 profile。
传播输出可以通过 `state_at` 组合进组件，但传播计算本身独立于靶核和探测器响应。
检测和传播参数有物理关联时，由理论模型配置声明；不能擅自复制 SM 项到已有 SM 的传播 Hamiltonian。
如果状态依赖扫描参数，`prepare`/`predict` 必须接收实际参数依赖或拒绝缓存复用，不能把初始状态冻结后继续扫描。

## 7. 必需错误和验证

- 未知归一化模式、单位缺失、重复组件 ID：拒绝构造。
- 负谱线权重、非有限谱值、不覆盖查询的能量态：给出组件 ID 和坐标。
- 空/多谱线测试；任意组件名称测试；对每条线单独验证运动学。
- 仅源强倍增时所有相关分量线性倍增，核数和观测记录不变。
- 相同物理输入从 flux→fluence 与直接 fluence 两条输入路径得到相同结果。
- 两个源实例不同参数交替求值，结果与各自单独求值一致，证明无全局状态污染。

相同算法的源码复写不能充当唯一物理基准；源积分需有解析或独立数值检查。
