# P07｜Slow authoritative counts：可填写模板

对应 [cevns-slow-counts Skill](../../skills/cevns-slow-counts/SKILL.md)。P01–P06 所需的 Machine 与 Human Gate 通过后才能实施。用户填写希望计算的输出、参考结果及资料；AI 负责积分接口、归一化台账和收敛验证。真实函数链和小网格收敛演示见 [P07 Slow 代码参考](P07_SLOW_COUNTS_CODE_REFERENCE.md)。

## A. 用户填写：权威直接计算目标

| 字段 | 请填写；值 + 单位 + 来源定位 |
| --- | --- |
| dataset_id；计算的模型/参数点 | ____；SM/EFT 参数及 flavor 约定：____ |
| 目标输出 | □ 真实反冲谱 □ 重建谱 □ events/bin；单位 ____；输出轴及顺序 ____ |
| 需要保留的分量 | 源 ____；同位素 ____；探测器 ____；总和规则 ____ |
| 每台探测器的 bin | 观测量/单位 ____；edges ____；窗外事件处理 ____ |
| 积分域 | `Eν` ____；真反冲 `T` ____；重建量 `x` ____；物理边界来源 ____ |
| 可比较的外部结果 | 表/图/旧程序数组 ____；条件、参数、误差/精度 ____；无则写“缺失” |
| 数值精度需求 | 逐 bin/总计容差 ____；依据 ____；仅研究用途可写目标容差 |

## B. AI 填写：归一化台账（写代码前必须核对）

| 因子 | 物理定义及单位 | 文件.symbol / owner | 已含在哪个因子？ |
| --- | --- | --- | --- |
| differential flux 或 fluence | ____ | ____ | ____ |
| `dσ/dT` | ____ | ____ | ____ |
| 每 kg 靶核数及同位素权重 | ____ | ____ | ____ |
| 靶质量或 kg·day 曝光 | ____ | ____ | ____ |
| 时间因子 | 每秒通量需按活时间积分；时间积分注量不再乘活时间：____ | ____ | ____ |
| 探测器响应与效率 | ____ | ____ | ____ |
| bin 积分 | ____ | ____ | ____ |

直接计算链：`source(Eν) × dσ/dT(Eν,T) → dN/dT → R(x|T) × ε → ∫bin dx → events/bin`。写明各积分和源/靶/探测器求和顺序：____。Slow 不读取 Fast kernel、cumulative cache，也不用整体比例因子修补结果。

## C. AI 填写：函数与输出契约

| 函数职责 | 候选或新增文件.symbol | 输入→输出、shape、单位 | 复用判断及证据 |
| --- | --- | --- | --- |
| 真实反冲率 | ____ | ____ | ____ |
| 探测器折叠及逐箱积分 | ____ | ____ | ____ |
| 源/靶/探测器编排 | ____ | ____ | ____ |
| 分量与总计输出 | ____ | ____ | ____ |

分类：`REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED`。实验专有层应只编排，避免复制共享截面或核响应。

## D. 验证与冻结

- [ ] 逐 bin、逐分量、逐探测器及总计保存；总计可由分量和独立复算。
- [ ] 保存真实谱、重建谱、网格、求积容差、单位和归一化检查点。
- [ ] 收敛、运动学支撑、有限性、按质量/曝光缩放及适用的复系数点已检查。
- [ ] 外部参考的来源和比较等级明确：内部一致性 / 旧程序回归 / 论文 forward 复现。
- Machine Gate P07：`NOT_RUN / PASS / BLOCKED`；数值结果和诊断路径：____。
- Human Slow Freeze：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；批准的版本/参数点/容差：____。未批准前 P08 不得开始。

**CsI2021 结构参考**：`rates.counts.bin_events_csi` 对响应和 bin 积分，`slow_counts_csi2021.slow_counts_csi2021` 编排源与靶，并输出 `counts_per_bin`、`counts_per_npe`、`target_flavor_counts_per_bin`。新实验要定义自己的输出键和形状；SNS、Cs/I、PE 与 9 bin 不可移植。

