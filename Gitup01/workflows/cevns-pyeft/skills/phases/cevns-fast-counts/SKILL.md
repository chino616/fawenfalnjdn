---
name: cevns-fast-counts
description: Validate P08 accelerated representations against an approved Slow reference with explicit parameter domains, backend limits, cache dependencies and per-bin errors.
---

# P08 — 有适用范围的加速表示

遵循 [阶段交接合同](../../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)，
每种表示使用独立 [P08 表单](../../../../_shared/templates/phase/P08_FAST_COUNTS_TEMPLATE.md)；
当前后端见 [代码参考](../../../../_shared/references/phase/P08_FAST_COUNTS_CODE_REFERENCE.md)。

## 1. 判断是否需要以及能否开始

仅执行已请求的加速任务。原目标不要求 Fast 时记计划 NOT_REQUESTED。
正式实施须有当前 P07 PASS、有效人工 Slow 冻结和匹配的参数/输出范围。
缺前提只阻断对应 Fast；不得修改 Slow 以适应 Fast。

## 2. 定义数学表示及实现

分别记录：
- representation：reconstructed_spectrum_cumulative、detector_response_matrix、
  eft_quadratic_coefficient_kernel 或数学定义明确的 other_surrogate。
- backend：实际 compiler/executor 和存储格式；interface_kernel_v1 与 legacy 不能混同。
- 省去的计算、构建时固定输入、求值时允许变化的参数、单位/轴和有效域。
- 完整声明基底及次序、SM 常数/干涉/二次项、复数双线性与 flavor 约定。

允许明确的 declared_subspace，但该子空间内相关项必须完整，域外参数须拒绝，
不能称为完整 EFT；缺映射且无法定义完整子空间时该表示 BLOCKED。
当前 interface compiler 要求 operator_bilinear_v1、单观测轴、
固定且独立于扫描参数的入射态。rho(E) 或扫描态参数需要其他已验证表示或扩展。
cumulative 通常固定参数点；响应矩阵通常只加速探测器折叠，不能冒称全部物理已缓存。

展示本表示的范围、限制与精度，必要时取得 `APPROVE THIS FAST REPRESENTATION`。

## 3. 构建与缓存合同

可从同一物理积分的系数分解直接编译，并用冻结 Slow 验证；
不要求把 Slow 的单个数值数组反推为任意 EFT 的核。
按实际依赖记录 source/run、state、target/response、observation/selection、
binning、理论基底、数值设置、实现版本和内容哈希。
区分编译依赖与求值参数；由具体后端决定哪些变化可复用。
仅统计观测/误差变化不应无故使物理核失效；改变物理 nuisance 的实际依赖则必须重查。
旧格式不自动升级为新核。

## 4. 验证与交付

逐 bin、逐可分辨分量报告 Slow/Fast/绝对差/相对差/容差。
覆盖基准、非零参数、适用时复数与 flavor 混合、边界和多个组合点。
验证包含实虚干涉的重建、保存加载一致性、域外拒绝、实际依赖变化失效；
不只比较总计，不用全局比例修补。记录构建、单次求值和存储成本。

handoff：
`representation`、`backend`、`basis_scope`、`parameter_domain`、
`state_treatment`、`slow_reference`、`cache_dependencies`、`validation_summary`。
每个 capability_id 独立 P08 Gate 和结果接受，返回 Master；
P09 若使用本表示须引用其有效版本，不能借另一个 Fast 的 PASS。
