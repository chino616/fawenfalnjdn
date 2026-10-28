# 计算主链与实验组装

状态：DESIGN。合同见 [03](03_SOURCE_AND_EXPOSURE_CONTRACTS.md)、[04](04_TARGET_AND_INTERACTION_CONTRACTS.md)、[05](05_OBSERVATION_AND_PREDICTION_CONTRACTS.md)。

## 1. 用户级调用

```python
# DESIGN：API 目标，不是当前可以直接运行的代码。
analysis = ExperimentModel(
    source=SNSLegacySource(baseline_m=19.3, yield_per_pot=0.0848),
    run=POTExposure(total_pot=3.198e23),
    targets=CsITargetInventory(detector_mass_kg=14.57),
    interaction=Li2026LegacyInteraction(nuclear_responses=response_db),
    observation=ObservationModel(
        response=CsIGammaResponse(),
        efficiency=CsI2021Efficiency(),
        selection=LegacyComponentAcceptance(mu=0.997, e=0.848, mub=0.848),
    ),
    binning=Binning.pe(PE_BINS_9),
)
result = predict(analysis, parameters=point, numerics=settings, backend="slow")
```

CsI2021 工厂保存这些实验选择；`predict` 不包含 `if dataset == "CsI2021"` 来选择物理公式。
运行期曝光只存在于 source.for_run 的输入；探测器质量只经 TargetInventory 生成核数。
来源/效率/目标常量可来自明确的配置，但解析后应写入实际模型记录。

## 2. 公共调用签名

```python
def predict(model: ExperimentModel, *, parameters: TheoryPoint,
            numerics: IntegrationSettings, backend: str = "slow") -> Prediction: ...

def validate_compatibility(model: ExperimentModel, *, parameters: TheoryPoint,
                          numerics: IntegrationSettings, backend: str) -> ValidationReport: ...
```

`backend` 只接受已经实现的枚举值。显式 Fast 不支持时拒绝；只有显式 auto 允许按记录退回 Slow。
不要通过不受约束的 `**kwargs` 将所有设置透传到每个底层函数。
未知参数和未消费字段在组装时报告，禁止“配置写了但程序没用”。

## 3. Slow 主链步骤

以下伪代码描述责任，实际函数需使用类型化对象和模块合同。

```python
validate_compatibility(model, parameters=parameters, numerics=numerics, backend="slow")
fluence = model.source.for_run(model.run)
parts = {}
for component in fluence.components:
    for target in model.targets.isotopes:
        recoil_yield = integrate_recoil_yield(
            component=component, target=target,
            interaction=model.interaction,
            parameters=parameters, numerics=numerics,
        )
        per_nucleus_bins = fold_observation(
            recoil_yield, component=component, target=target,
            observation=model.observation,
            binning=model.binning, numerics=numerics,
        )
        parts[(component.component_id, target.isotope_id)] = (
            target.number_of_nuclei * per_nucleus_bins
        )
prediction = assemble_prediction(parts, model, parameters, numerics)
```

最后乘核数与先生成实际反冲事件谱再折叠在线性响应下等价。实现固定一种顺序；诊断对象明确是否已经乘核数。
暂不让完整 ExperimentModel 流入 integrate/fold；显式参数使依赖可审计。

## 4. 入射能积分

对每个反冲 T：

1. 由 interaction.kinematics 计算 E_min。
2. 与 component.support.integration_domain 取交集。
3. 按当前数值 profile 获取能量子网格与积分权重；legacy 先保留旧掩码+trapz 行为。
4. 在实际子网格调用 continuum 与 state_at；向后者传入由当前 TheoryPoint 解析的 StateParameters，验证坐标对齐。
5. 调用 dsigma_dT 并积分连续部分。
6. 单独遍历 lines，在自身能量求状态和截面，施加运动学支撑。
7. 输出 RecoilYield，单位为每核 keV^-1；没有质量、效率或接受率。

不对未知源自动使用 0–52.8 MeV，不强制保留 muLine 字段，不以源名字判定连续/离散谱。
能量积分区间没有足够节点时按明确策略处理。旧 profile 和新收敛算法的处理差别记录在数值版本中。

## 5. 分离计算也改善可读性和性能

当前 `bin_events_csi` 对多个 PE 节点反复调用 `empirical_dNdPE_response_csi`，每次都重新计算与 PE 无关的反冲谱。
新主链将 Y(T) 作为明确结果后，同一输入的能量积分可复用，再施加多个 PE/时间观测。
先实现数学与离散约定相同的提取，之后才做矢量化、并行或缓存。不要把数值重排误差混入第一阶段接口回归。

## 6. 新旧实现共存

使用 `dataclasses.replace` 或等价的显式构造：

```python
alternative = replace(analysis, source=another_source)
old_prediction = predict(analysis, parameters=point, numerics=settings)
new_prediction = predict(alternative, parameters=point, numerics=settings)
```

组件参数与资源只读；不同实例不会改写对方的全局默认。
源替换可能要求同时替换 run 或 observation，例如新 source ID 不在旧接受率表中。应由兼容性报告指出具体缺口，而不是自动补名字或值。
本包的可替换性只承诺满足同一合同和物理能力条件的组合；不承诺任意新物理都可以无改动接入。

## 7. 旧入口兼容

`slow_counts_csi2021` 在新链验证后：

- 保留已有函数名、参数、默认值、返回键和 PE 分箱。
- 将参数映射到工厂、TheoryPoint、legacy numerics。
- 调用新主链，明确转换到旧字典结构。
- 保留 legacy raw 的特殊语义，参见 04；不要把新分量直接复制进去。
- 旧 `core.engine` import 路径继续可用。

在新链成熟前可继续让旧入口走原实现，测试使用独立新入口比较，避免边改边丢失基准。
公共 API 切换后，回归基准来自变更前冻结数据或独立旧版本环境，不能只比较两个都指向新函数的包装器。

## 8. 配置与资源

建议 `make_csi2021_model` 是唯一默认组装点。配置文件调用该工厂覆盖明确允许的字段；不同时在多个模块维护相同可变默认。
`ResolvedModelRecord` 序列化实际选中的组件、参数、运行期、轴及数据内容哈希。指纹详见 10。
计算内层不读文件；资源在构造/prepare 阶段加载，避免每个 E/T 点重复 I/O。
数据位置使用显式资源根或经验证的包资源机制，不从当前 cwd 猜路径。既有安装方式保持兼容，打包验证见 R6。
