# CsI2021 核心函数结构参考

本文件从当前 CsI2021 实现提取**调用关系、职责和可复用接口**，供新实验的 Phase 0 实施清单参考。具体数值和资料来源见[按用户模板填写的 CsI2021 示例](../onboarding/EXPERIMENT_USER_INPUT_CsI2021_EXAMPLE.md)。这里不复制完整源码；CsI 的 SNS 源、PE 响应、9 个 bin 和旧统计数据均不是新实验默认值。

## 从资料到计数的最小链

```text
experiment spec：dataset、输出轴、bin edges、目标物理声明
  ├─ target：同位素/核响应 key、每 kg 靶核数、曝光归一化
  ├─ source component s：Φ_s(Eν)、ν/反ν标签、ρ_s(Eν)
  ├─ shared theory：Wilson 矩阵 → 核响应 → K_a(Eν,T)
  ├─ cross section：Tr[ρ_s(Eν) K_a(Eν,T)]，单位和运动学支撑
  ├─ detector：T → 重建量 x，迁移核 R_d(x|T)，效率 ε_d(x或T)
  └─ Slow：按 s、同位素 a、探测器 d 积分 → 每 bin 计数 → 总和
       ├─ Fast（仅在 Slow 冻结后）：选加速表示、保留有效性元数据、逐 bin 对照
       └─ Statistics（有可用观测数据时）：将预测轴/单位映射到已批准的数据语义
```

源若给时间积分注量，就不再乘活时间；源若给每秒通量，才由曝光合同确定时间因子。这个决定来自新实验的资料，而非 CsI 函数默认值。

## CsI2021 对应的真实函数与复用判断

| 阶段 | 当前项目中的函数或文件 | 核心职责 | 新实验的初步处理 |
| --- | --- | --- | --- |
| P01 | `experiments.specs.load_experiment_spec`；`data/experiments/CsI2021/experiment.yaml` | 读取 dataset 身份、轴和配置；不做物理积分。 | **REUSE/CONFIG_ONLY**：复用装载入口，写新实验配置；先核对 schema 能否表达。 |
| P02 | `nuclear.response.ResponseDB.get`；`slow_counts_csi2021.combine_equal_stoichiometry` | 选择核响应，按靶组成汇总。 | ResponseDB **候选 REUSE**；CsI 等化学计量汇总公式只作结构参考，新靶需自己的组成规则。 |
| P03 | `coherent.sns.loadNeutrinoEmpiricalFluxSNS`、`sns_component_state`；`sources.state.NeutrinoState` | 逐源分量提供注量和入射 flavor 状态。 | `NeutrinoState` **候选 REUSE**；SNS 通量及 `mu/e/mub` 映射是 **CsI/SNS 专用**，新源通常需 CONFIG_ONLY 或 ADAPTER。 |
| P04–P05 | `rates.differential.differential_flavor_kernel_nn`、`differential_cross_section_nn` | 共享理论、核响应和运动学支撑，计算 `Tr(ρK)` 后的差分截面。 | **候选 REUSE**；必须核对模型、Response key、单位、flavor 与 ν/反ν 约定。 |
| P06 | `rates.differential.eee_quenching_csi`、`p_smearing_csi`；`slow_counts_csi2021.efficiency_csi2021` | 映射真实反冲到 PE，并实施迁移、效率。 | **接口结构可参考**；这些函数的物理参数和 PE 语义是 CsI 专用，新探测器按材料选择配置或 ADAPTER。 |
| P07 | `rates.counts.bin_events_csi`；`slow_counts_csi2021.slow_counts_csi2021` | 对源和靶调用共享截面，积分真实反冲、探测器响应及 bin，保存分量和总计。 | **保留积分结构**；为新实验写最薄计数编排，避免复制 CsI 的源选择、PE 网格和化学计量常量。 |
| P08 | `fast_kernel_csi2021.build_fast_kernel_csi2021`；`kernels.reconstruction.reconstruct_from_full_kernel_flavor` | 从已验证 Slow 目标构造并重建 Fast 表示。 | flavor 双线性重建是**候选 REUSE**；现有 builder 的 SNS 分量、CsI 靶/PE 和 dataset 限制不能直接用于新实验。 |
| P09 | `statistics.datasets.csi2021_dataset`；`likelihoods.chi2_csi2021` | 旧程序 residual 数据与 Gaussian 双 pull χ²。 | **REFERENCE_ONLY**；新实验先确认观测数据语义及官方/近似统计范围。 |
| P10 | `experiments.registry` 与验证报告 | 暴露已实现能力并记录结论。 | 注册模式可复用；只暴露已通过相应机器与物理 Gate 的能力。 |

这些分类是**CsI2021 结构给出的初步判断**，不是新实验的已批准实施清单。每个 `REUSE` 必须在 Phase 0 指明实际文件、symbol、输入输出形状/单位、物理适用域和回归检查；未核对时记为候选，不计作已完成迁移。

## P07：需要保留的计算契约

1. 对每个源分量记录 `flux/fluence`、`particle_kind`、入射密度矩阵 `ρ_s(Eν)`；对每个靶同位素选择正确核响应。
2. 共享截面先处理运动学支撑和 flavor 收缩，再与该源分量的谱相乘；对 `Eν`、真实反冲和每个观测 bin 积分。
3. 只在约定的所有源/靶/探测器因子均施加后汇总 `total`；同时保留分量计数、单位和归一化台账。
4. 直接积分结果独立于 P08 缓存；网格收敛、纯 flavor/混合态、ν/反ν 适用域和逐 bin 输出都要核对。

CsI2021 的 `slow_counts_csi2021` 是上述结构的一个实现。其 prompt μ 线、两条 Michel 连续谱、Cs/I 混合、PE 展宽和接受率是具体实验细节。

## P08：复用前的判定

| Fast 类型 | 可复用的结构 | 关键有效性条件 |
| --- | --- | --- |
| 重建谱 cumulative | 从已验证重建谱积分为累计量，再做 bin edge 差。 | 缓存固定的源谱、flavor 状态、探测器模型、曝光与参数点；这些输入改变时重建。 |
| 探测器响应矩阵 | 真实反冲到重建 bin 的线性映射。 | 只有响应不依赖待扫描物理参数时才能复用；源/flavor 计算仍由 P07 合同约束。 |
| EFT 二次 kernel | 保留基底、源分量、flavor 矩阵约定和 bin 轴，通过系数双线性重建。 | 基底完整、kernel 与 P07 同一物理模型；固定 `ρ_s` 与能量依赖 `ρ_s(Eν)` 不能混用。逐源、逐 bin、多个参数点对照 Slow。 |

当前通用 builder 的源分量固定为 SNS 的 `e/mu/mub`，存储校验只接受项目中已列出的数据集；新实验不能仅改 `dataset` 字符串就宣称 Fast 已复用。ν/反ν 在当前 `NeutrinoState` 接口中有标签，但相互作用 kernel 的反中微子审计仍是独立物理条件。

## Phase 0 应填的逐函数复用表

| 所需计算 | 候选文件/symbol | 分类 | 适用性证据：模型、单位、轴、flavor | 缺口与最小动作 | 验证基准 |
| --- | --- | --- | --- | --- | --- |
| 示例：差分截面 | `rates.differential.differential_cross_section_nn` | 候选 `REUSE` | 待比对新实验所需的理论、单位和 ν/反ν 约定 | 必要时只写单位/靶适配器；物理不符则 `BLOCKED` | 共享测试 + 新实验参考点 |
| 示例：逐箱计数 | `rates.counts.bin_events_csi` | `ADAPTER` 或重新编排 | 积分次序可参考；CsI/SNS/PE 细节不能继承 | 写新实验的最薄 Slow 编排 | 逐源/逐靶收敛与外部参考 |

新实验填写此表后，才能决定具体哪些函数直接调用、哪些只借用结构、哪些必须新增。
