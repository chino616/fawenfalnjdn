# P07｜直接积分与 Slow 冻结

见 [P07 Skill](../../../cevns-pyeft/skills/phases/cevns-slow-counts/SKILL.md)、
[执行合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)、
[当前积分路径](../../references/phase/P07_SLOW_COUNTS_CODE_REFERENCE.md)。

## A. 用户目标

| 内容 | 定义、单位与来源 |
|---|---|
| dataset、模型/参数点及需覆盖的参数域 | ____ |
| 输出：真实反冲产额/重建谱/events per bin | ____ |
| 各轴与需要保留的源/核素/探测器分量 | ____ |
| Eν、T、观测量积分范围 | ____ |
| 逐箱绝对/相对精度及依据 | ____ |
| 外部参考、对应条件及精度；无则注明缺失 | ____ |

## B. AI 归一化台账

| 因子 | 物理含义、单位 | owner/symbol | 已包含什么；本次还乘什么 |
|---|---|---|---|
| 连续通量/注量 | ____ | ____ | ____ |
| 线谱积分注量 | ____ | ____ | 不乘连续谱能量宽度：____ |
| 微分截面 | ____ | ____ | ____ |
| 核数/每 kg 率/质量 | ____ | ____ | ____ |
| 活时间/已积分运行归一化 | ____ | ____ | ____ |
| 响应与选择 | ____ | ____ | P06 已含选择：____ |
| bin 积分 | ____ | ____ | ____ |

实际采用的单一路线、单位推导与 decision refs：____。
P06 若不适用于本次真实反冲输出，写明原因和受限声明；不伪造已折叠计数。

## C. AI 计算与收敛

实际 definition/model/executor、函数和数值策略：____。
输出合同、分量和总计的关系、兼容 raw 数组的区别：____。

| 改变的积分维度/域 | 原设置→加密设置 | 最大逐箱绝对/相对差 | 预定容差 | 结论 |
|---|---|---|---|---|
| Eν/线谱与阈值 | ____ | ____ | ____ | ____ |
| T/端点与尾部 | ____ | ____ | ____ | ____ |
| 重建量/bin 求积（如适用） | ____ | ____ | ____ | ____ |

缩放、支撑、分量和、有限性/总计非负性与适用参数点：____。
外部比较等级及缺口：____。小网格 smoke 不作为冻结依据。

## D. 冻结

handoff：normalization_ledger、output_contract、numerics_and_convergence、
reference_comparison、freeze_scope。
freeze_scope 包括实际输入/代码/参数域、网格、容差、结果文件指纹和证据等级。
用 [阶段报告](PHASE_REPORT_TEMPLATE.md) 展示逐箱与总计，记录用户对当前版本的
`APPROVE SLOW AS AUTHORITATIVE REFERENCE`。返回 Master 后按目标进入 P08、P09 或 P10。
