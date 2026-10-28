# 靶核、截面与运动学接口

状态：DESIGN。关联：[源合同](03_SOURCE_AND_EXPOSURE_CONTRACTS.md) · [主链](06_PIPELINE_AND_ASSEMBLY.md)。

## 1. 靶核对象

```python
# DESIGN：字段示意，构造函数必须执行实际校验。
@dataclass(frozen=True)
class TargetIsotope:
    isotope_id: str
    kinematic_mass_GeV: float
    nucleus_mass_kg: float
    number_of_nuclei: float
    mass_convention: str
```

`TargetInventory` 保存材料、质量、组成输入及其 fraction convention，构造出上述核素元组。
核响应数据库的内部 key 由核响应适配器解析，例如 I127→I；不要要求通用积分器知道这些别名。

### 组成换算

若给质量分数：`n_A = M_kg * w_A / m_A_kg`。
若给数目分数：先结合各核素质量求出平均质量，再确定总核数与各分量核数。
不允许一个未标明含义的 `weight` 同时表示两者。

CsI 旧复现：质量分数为 133/260 和 127/260；核数换算采用 `A * 1.6605390666e-27 kg`；运动学质量采用 `A * AMU_GEV`。
这两个质量约定作为 legacy 配套参数记录，第一次重构不换成精确同位素质量。
核数应满足 Cs/I 等化学计量；质量因子只在此处形成一次。

### 原 raw 输出的特殊含义

当前 CsI2021 `target_flavor_counts_per_bin` 中每个目标的 raw 已使用整台质量，尚未乘相应质量分数和分量接受率。
新 `Prediction.components[(source_id,isotope_id)]` 表示实际材料贡献，应已经使用对应核数和声明的选择。
两者不能只改字段名就当成同一对象。旧包装器若继续返回历史 raw，必须由保存的每核/每目标选择前结果准确重构，或保留专用 legacy diagnostics；不得把新最终分量冒充旧 raw。

## 2. 核响应边界

继续复用当前 `ResponseDB/ResponseW`，通过 `Li2026LegacyInteraction` 中的适配器读取。
核响应内容记录 isotope、通道、基底、规范、数据哈希；源和探测器不应加载核响应数据。
已知核响应外部规范审核未闭合，保留其状态。不能仅因为适配器通过 shape 检查就宣称所有核模型可互换。
修改 W 的规范需要匹配振幅收缩约定，是联合合同变更，不是普通数表替换。

## 3. 相互作用最小能力

```python
# DESIGN：能量为一维向量，反冲为一个标量。
class InteractionModel(Protocol):
    kinematics: ElasticKinematics

    def dsigma_dT(
        self, *, target: TargetIsotope,
        energy_MeV: np.ndarray, recoil_keV: float,
        incident_state: IncidentStateBatch,
        parameters: TheoryPoint,
    ) -> DifferentialCrossSection: ...

    def describe(self) -> ModuleDescriptor: ...
```

`DifferentialCrossSection` 至少含 `values_cm2_per_keV`、对应能量、反冲和模型标识。
`values` 的 shape 为 `(n_E,)`，不得隐式 sum flavor/source。
核外的源注量、核数、分箱、效率、运行期均不属于此接口。
单位转换集中在适配器，核心 GeV^-3→cm²/GeV→cm²/keV 的关系使用当前明确转换函数。

正常物理参数下输出有限、实数且非负；显著负值应报错，不能在新物理接口中普遍用 `max(x,0)` 掩盖错误。legacy 兼容中的既有数值截断需单独记录。

## 4. 运动学与过程能力

`ElasticKinematics` 提供：

- `minimum_energy_MeV(target, recoil_keV)`；
- `maximum_recoil_keV(target, energy_MeV)`；
- 必要的 transfer/支撑检查。

单位转换后复用 `theory/kinematics.py` 的现有公式。接口声明的过程是当前近似下的弹性核散射。
截面和运动学必须使用同一目标质量约定；不能只替换其中一个的精确质量。
新模型需要不同末态或新的运动学变量时，应声明新 process contract；不能通过补几个可选参数伪装成原合同兼容。

## 5. TheoryPoint 与模型参数

`TheoryPoint` 包含本次 Wilson 矩阵和扫描量，并明确 NP-only/SM+NP 规则。
固定 LEC、核响应约定、c10_mass_mode 等属于模型配置或显式参数，所有消费者必须读取同一份解析后的值。
不要改写 `DEFAULT_LECS` 期待已绑定的默认参数和 Fast 同时更新。
目前源码签名中的部分标量注解与 flavor 矩阵运行约定不同；新合同按真实矩阵语义定义，并保留外部兼容行为或明确拒绝不支持输入。

现有 `differential_cross_section_nn` 可包装为 `Li2026LegacyInteraction`。如果必须暴露它当前未穿透的参数，则给当前模型内部增加显式传参链，并单独检验 Slow/Fast；不能只新增一个外层字段。

## 6. 粒子身份与可选 Fast

声明 `particle_treatment="legacy_shared_kernel"` 表示沿用当前 nu/antinu 处理，不等于一般反中微子支持。
用户要求改变这一物理处理时，另开模型版本及独立振幅基准。

`dsigma_dT` 是 Slow 能力。支持 EFT 系数核的模型另外暴露经过验证的系数表示或编译器接口。
没有此能力时，显式 Fast 请求报 `UnsupportedCapabilityError`；只有用户明确选择 `backend="auto"` 才允许返回 Slow，并在结果中记录实际后端及原因。

## 7. 验证

1. 旧截面与适配器在相同核素、能量、反冲、SM/NP 点逐点一致。
2. 密度矩阵能量对齐，常量态广播与显式能量态一致。
3. 核数随质量线性变化，Cs/I 等核数条件成立。
4. 源强变化不改变截面；靶质量变化只改变核数，不改变单核截面。
5. 单位转换的截面积分在不同单位表示下相同。
6. 超出运动学支持时为零；非法能量等输入按合同给出明确错误。

不能用 Helm 对所有 LEFT 算符的结果作为“完全等价”目标；不同核模型的适用范围需要分别声明。
