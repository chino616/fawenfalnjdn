# CsI2021 P04–P10 输入包执行审计

本目录是本次唯一 canonical 阶段/Gate 记录，数值结果在 [outputs](../../../../../outputs/csi2021_package_execution_20261104/README.md)。
输入与代码按版本固定；科学状态为 DRAFT/PARTIAL、人工 NOT_REVIEWED。

| 文件 | 内容 |
|---|---|
| [最终执行报告](11_FINAL_EXECUTION_REPORT.md) | 版本、数值、测试、逐能力 PASS/BLOCKED/NOT_RUN |
| [当前进度](00_MIGRATION_PROGRESS.md) | 可恢复 checkpoint，非批准权威 |
| [执行计划](00_EXECUTION_PLAN.md) / [实施清单](00_IMPLEMENTATION_MANIFEST.yaml) / [授权](AUTHORIZATION_LOG.yaml) | 用户授权范围、DAG、输入/实现依赖 |
| [P04 理论与核响应](04_THEORY_RESPONSE_REPORT.md) | 七响应、22 算符、flavor 与来源边界 |
| [P05 运动学与截面](05_KINEMATICS_CROSS_SECTION_REPORT.md) | 动量、质量、支撑和单位 |
| [P06 探测器响应](06_DETECTOR_RESPONSE_REPORT.md) | Gamma/quenching/效率/选择及窗口损失 |
| [P07 Slow](07_SLOW_COUNTS_REPORT.md) | 直接积分、十组网格、收敛与技术 reference |
| [P08 Fast](08_FAST_COUNTS_REPORT.md) | full22 工程候选、固定态与正式 Gate 限制 |
| [P09 近似统计](09_STATISTICS_REPORT.md) | 一次箱宽转换、双 pull、独立解 |
| [P10 验证与发布](10_VALIDATION_RELEASE_REPORT.md) | 能力矩阵、wheel、生命周期、当前兼容失败 |
| [Skill 问题审计](12_SKILL_WORKFLOW_AUDIT.md) | 流程/实现/输入/版本问题与最小修正 |
| [逐项 Runtime 映射](13_PACKAGE_RUNTIME_MAPPING.md) | 全 17 模型、105 参数、23 数组 |
| [复现命令](14_REPRODUCE.md) | 固定 wheel、外部 cwd、测试和新目录复现 |
| [变更和回滚](15_CHANGE_AND_ROLLBACK.md) | 本任务/同期变更归属、备份、精确回滚范围 |
| [逐条验收](16_REQUIREMENTS_AUDIT.md) | 任务要求与实际证据对应 |

Machine P07 PASS 不等于人工 Slow 接受，P08 正式 Gate 保留 BLOCKED。
普通工程验证可以完成，不补造外部科学来源或批准。
