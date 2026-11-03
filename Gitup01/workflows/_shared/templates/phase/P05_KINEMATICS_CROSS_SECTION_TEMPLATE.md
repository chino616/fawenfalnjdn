# P05｜运动学与微分截面

使用 [P05 Skill](../../../cevns-pyeft/skills/phases/cevns-kinematics-cross-section/SKILL.md)、
[执行合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)、
[代码参考](../../references/phase/P05_KINEMATICS_CROSS_SECTION_CODE_REFERENCE.md)。
输入 P04 的模型约定，输出 P07 可消费的截面合同。

## A. 用户提供的定义

| 内容 | 定义、数值/单位与来源 |
|---|---|
| 散射过程与目标模型；P04 引用 | ____ |
| Eν、T 的物理意义、单位、输入范围 | ____ |
| 逐同位素核质量及其约定 | ____ |
| T_max、Eν_min 与支撑条件 | ____ |
| 允许域内截面公式及近似范围 | ____ |
| 入射态、flavor 轴、末态求和、ν/反ν | ____ |
| 域外/非法输入行为；零点奇异性与 cutoff | ____ |
| 独立端点、截面或积分参考点 | ____ |

## B. AI 接口与实现

| 职责 | 实际文件::symbol | 输入/输出、单位、shape、错误行为 | 复用判断 |
|---|---|---|---|
| 运动学 | ____ | ____ | ____ |
| InteractionModel.dsigma_dT | ____ | ____ | ____ |
| 单位与状态坐标桥接 | ____ | ____ | ____ |

记录 P04、运动学和相空间是否使用同一核质量；单位转换 owner：____。
需要新增的物理决定、扩展和受影响回归：____。
本层不加入源归一化、曝光、核数或效率。

## C. 检查与交接

检查端点及逆关系、端点两侧、非法输入、T=0/小反冲的模型行为、
单位 Jacobian、状态坐标、适用的 SM/EFT/复数点与拒绝域。
至少一个端点可独立复算，记录计算条件和结果。
handoff：process_and_mass、kinematics、cross_section_api、units_and_axes、
support_and_limits、benchmark。用 [阶段报告](PHASE_REPORT_TEMPLATE.md) 返回 Master。
