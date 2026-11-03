# P08｜加速表示与适用范围

每种表示单独填写。见 [P08 Skill](../../../cevns-pyeft/skills/phases/cevns-fast-counts/SKILL.md)、
[执行合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)、
[当前 Fast 路径](../../references/phase/P08_FAST_COUNTS_CODE_REFERENCE.md)。

## A. 用户加速目标

| 内容 | 本次要求 |
|---|---|
| 扫描参数、范围、预计调用量 | ____ |
| 逐箱误差目标；近零箱规则 | ____ |
| 构建时间、单次评价和存储要求 | ____ |
| 所需分量和输出轴 | ____ |

未请求时记录 NOT_REQUESTED；请求但缺 Slow 冻结时记录对应阻断。

## B. AI 数学、实现与缓存合同

| handoff 字段 | 应填内容 |
|---|---|
| representation | cumulative / response matrix / EFT quadratic kernel / 有明确定义的其他 surrogate；使用 Skill 的完整标识 |
| backend | 真实实现与格式，如 interface_kernel_v1 或具体 legacy 后端 |
| basis_scope | full_model / declared_subspace / not_applicable；实际基底、顺序、单位与 SM/干涉/复数项 |
| parameter_domain | 构建固定项、允许扫描项、域外拒绝；省去和仍需执行的计算 |
| state_treatment | fixed_parameter_independent / energy_dependent / parameter_dependent / not_applicable；实现依据 |
| slow_reference | report_ref、sha256、approval_ref；对应当前有效 P07 冻结 |
| cache_dependencies | 内容/实现/数值指纹、重建条件、可复用变化及存储加载规则 |
| validation_summary | 验证点、逐箱误差、性能与限制；实现前保持草稿 |

interface_kernel_v1 当前要求 fixed_parameter_independent 状态和一维观测。
限定基底子空间须完整保留该域全部相关项并拒绝域外参数，不得冒称全 EFT。
统计观测/误差与物理编译依赖分开；改变实际物理 nuisance 仍按依赖处理。

## C. 对照与交接

| 参数点/源/核素/bin | Slow | Fast | 绝对差 | 相对差 | 容差与结论 |
|---|---|---|---|---|---|
| ____ | ____ | ____ | ____ | ____ | ____ |

覆盖基准、非零/组合/边界点及适用的复数和 flavor 混合。
检查保存加载、缓存失效、域外拒绝、构建成本和单次评价。
每个 capability_id 独立记录 [阶段报告](PHASE_REPORT_TEMPLATE.md) 和人工接受，返回 Master。
