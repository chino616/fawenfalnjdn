# CsI2021_time_9x11 onboarding（r3重启）

2026-11-18按用户请求重新走物理流程。三个旧计算入口已从examples移除；当前尚无新计数入口。

[当前进度](00_MIGRATION_PROGRESS.md) · [阶段计划](00_EXECUTION_PLAN.md) · [实施依赖](00_IMPLEMENTATION_MANIFEST.yaml) · [实际授权](AUTHORIZATION_LOG.yaml)

[P00来源](P00_SOURCE_REGISTER.yaml) · [P01证据](P01_EVIDENCE_LEDGER.yaml) · [P02缺失/冲突](P02_MISSING_AND_CONFLICTS.md) · [P03配置](P03_PHYSICS_CONTRACT.yaml) · [实际决定](DECISION_LOG.json)

[详细草稿](../../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/experiment.physics.md) · [精简草稿](../../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/experiment.physics.summary.md) · [用户审阅件](../../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/EXPERIMENT_USER_INPUT.md)

## 生成与检查

prepare_records.py重建原始数值记录后，依次应用timing_diagnostics_records.py（历史诊断）和restart_records.py（当前审阅状态）；export_physics_docs.py从同一P00/P01/P03生成四份文档。

```powershell
python -X utf8 -B export_physics_docs.py
python -X utf8 -B export_physics_docs.py --check
```

本轮Compiler/Renderer运行包交接为NOT_RUN，见阶段计划；不能用当前草稿导出替代新YAML/NPZ编译验收。当前共享公式不变，新P07等待必要合同。

## 证据与历史归属

data/和sources/为实际数值及原材料；evidence/保留原核验及本轮INPUT_FILE_REVIEW_20261118.json。旧sm_benchmark_20261107、nsi_benchmark_20261108及outputs/20261117结果仅作版本明确的历史参考。revisions/20261118_before_restart保存重启前记录。

撤下入口与清理清单：[清理记录](<../../../../../../../重构/20261118_CsI2021_onboarding_restart/README.md>)。

[上一级旧9箱执行记录](../README.md)
