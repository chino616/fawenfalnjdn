# 四实验实际能力

工程范围：四个已有精确 ID；原科学状态保持不变。
统一入口不会把不同折叠策略或统计样本强制改成同一种。

| dataset_id | 定义权威文件 | Slow | Fast | 统计 | 物理必需资源 |
|---|---|---|---|---|---|
| CsI2021 | coherent/csi2021_definition.py | ExperimentModel + 原 gamma/效率/接受率 | interface_kernel_v1，完整/成对表示及依赖指纹 | 原近似 Gaussian；events/bin → counts/PE 一次 | responses_all.json |
| CsI2017 | coherent/csi2017_definition.py | 固定251点确定性PE映射、Jacobian、14.6kg | legacy_compat channel_resolved_full_li2026；保留自身PE网格规则，新增实例绑定 | 原近似 Gaussian；统计时才加载四个text资源 | responses + COHERENT_eff.txt |
| Ar2020 | coherent/ar2020_definition.py | 原 sigma(observed) Gaussian、12箱、24kg | legacy_compat channel_resolved_full_li2026；新增实例绑定 | 原近似非对称误差 IRLS；保留历史观测单位约定 | responses + CENNS10AnlAEfficiency.txt |
| conus_plus_2025_c2c3c5_ge73_pyeft | conus_plus/definition.py | 分段Gauss积分、Ge73、kg·day、C2/C3/C5有名分项 | detector_response_matrix；理论率仍逐点积分 | 默认357kg·day预测无绑定观测；effective119 + 显式观测CSV可评价一次19箱合计 | responses + Kopeikin/Mueller CSV |

各定义文件以 `src/cevns_pyeft/experiments/` 为前缀。

| 状态 | CsI2021 | CsI2017 | Ar2020 | CONUS+ |
|---|---|---|---|---|
| definition_centralized | 已实现 | 已实现 | 已实现 | 已实现 |
| unified_loading_verified | 已验证 | 已验证 | 已验证 | 已验证 |
| component_inputs_consumed | 已验证 | 已验证 | 已验证 | 已验证 |
| slow_regression_verified | 独立旧基线 | 独立旧基线 | 独立旧基线 | 独立旧基线、探测器/分量/能区/箱 |
| fast_status | 新合同及原兼容保护 | legacy_compat，独立旧Fast回归 | legacy_compat，独立旧Fast回归 | 响应矩阵及持久化验证；完整EFT核未新增 |
| statistics_status | 现有近似 | 现有近似 | 现有近似 | 条件支持；默认资源位置缺CSV，须显式提供 |
| selection_verified | 已验证 | 已验证 | 已验证 | 已验证 |
| release_verified | wheel+外部cwd | wheel+外部cwd | wheel+外部cwd | wheel+外部cwd |

统计能力不等于官方 likelihood。CONUS+ 当前 CSV 实际在既有交付输出中；
不从 workflow 自动导入，也不把同一19点观测分配给三个探测器。
实际命令、测试数量与逐项误差以 MIGRATION_REPORT.md 和 JSON 证据为准。
