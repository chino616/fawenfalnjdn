# 最小变更、归属与回滚

本次新增局部 adapter/绑定合同、两份测试与两份执行工具。共享变更只有两个包级延迟导入；登记/打包只补齐所需文件归属和合同 JSON。P10 Skill/参考明确持久 JSON 权威与既有语义工程 Gate。

完整 SHA256、所有观察到的同期修改与文件归属见 [change_and_rollback_manifest.json](../../../../../outputs/csi2021_package_execution_20261104/change_and_rollback_manifest.json)。三份正式输入、theory/nuclear 公式及冻结 reference 没有由本任务编辑。

| 文件 | 分类 | owning README | 原件备份 |
|---|---|---|---|
| cevns_pyeft/experiments/coherent/csi2021_package.py | ADDED | cevns_pyeft/experiments/README.md | None |
| cevns_pyeft/experiments/coherent/csi2021_package_contract.json | ADDED | cevns_pyeft/experiments/README.md | None |
| tests/test_csi2021_input_package.py | ADDED | tests/README.md | None |
| tests/test_csi2021_package_fast.py | ADDED | tests/README.md | None |
| tools/run_csi2021_package_phases.py | ADDED | tools/README.md | None |
| tools/verify_csi2021_package_release.py | ADDED | tools/README.md | None |
| cevns_pyeft/statistics/__init__.py | MODIFIED_OR_MIXED | cevns_pyeft/statistics/README.md | backup/20261104_csi2021_package_execution/cevns_pyeft/statistics/__init__.py |
| cevns_pyeft/detectors/__init__.py | MODIFIED_OR_MIXED | cevns_pyeft/detectors/README.md | backup/20261104_csi2021_package_execution/cevns_pyeft/detectors/__init__.py |
| cevns_pyeft/experiments/dataset_registry.json | MODIFIED_OR_MIXED | cevns_pyeft/experiments/README.md | backup/20261104_csi2021_package_execution/cevns_pyeft/experiments/dataset_registry.json |
| cevns_pyeft/experiments/DATASETS.md | MODIFIED_OR_MIXED | cevns_pyeft/experiments/README.md | backup/20261104_csi2021_package_execution/cevns_pyeft/experiments/DATASETS.md |
| pyproject.toml | MODIFIED_OR_MIXED | README.md | backup/20261104_csi2021_package_execution/pyproject.toml |
| workflows/cevns-pyeft/skills/phases/cevns-validation/SKILL.md | MODIFIED_OR_MIXED | workflows/cevns-pyeft/README.md | backup/20261104_csi2021_package_execution/workflows/cevns-pyeft/skills/phases/cevns-validation/SKILL.md |
| workflows/_shared/references/phase/P10_VALIDATION_RELEASE_CODE_REFERENCE.md | MODIFIED_OR_MIXED | workflows/_shared/README.md | backup/20261104_csi2021_package_execution/workflows/_shared/references/phase/P10_VALIDATION_RELEASE_CODE_REFERENCE.md |
| cevns_pyeft/experiments/README.md | MODIFIED_OR_MIXED | cevns_pyeft/experiments/README.md | backup/20261104_csi2021_package_execution/cevns_pyeft/experiments/README.md |
| cevns_pyeft/statistics/README.md | MODIFIED_OR_MIXED | cevns_pyeft/statistics/README.md | backup/20261104_csi2021_package_execution/cevns_pyeft/statistics/README.md |
| cevns_pyeft/detectors/README.md | MODIFIED_OR_MIXED | cevns_pyeft/detectors/README.md | None |
| data/experiments/COHERENT_CsI/CsI2021/README.md | MODIFIED_OR_MIXED | data/experiments/COHERENT_CsI/CsI2021/README.md | backup/20261104_csi2021_package_execution/data/experiments/COHERENT_CsI/CsI2021/README.md |
| docs/README.md | MODIFIED_OR_MIXED | docs/README.md | backup/20261104_csi2021_package_execution/docs/README.md |
| outputs/README.md | MODIFIED_OR_MIXED | outputs/README.md | backup/20261104_csi2021_package_execution/outputs/README.md |
| workflows/cevns-pyeft/README.md | MODIFIED_OR_MIXED | workflows/cevns-pyeft/README.md | backup/20261104_csi2021_package_execution/workflows/cevns-pyeft/README.md |
| tests/README.md | MODIFIED_OR_MIXED | tests/README.md | backup/20261104_csi2021_package_execution/tests/README.md |
| tools/README.md | MODIFIED_OR_MIXED | tools/README.md | backup/20261104_csi2021_package_execution/tools/README.md |

## 回滚方式

先核对 current SHA256；若已被后续修改，不直接覆盖。新增六个文件可在移除其消费者/登记后撤销。共享 __init__ 与 P10 两文档有本任务修改前备份，按清单逐文件恢复并重跑导入/回归。registry、pyproject 和 README 含同期改动，只撤销本任务增加的 adapter/contract/data ownership、package-data 一行和相应文档段落，不使用 git restore 或整体替换。

初始备份列表为 outputs/.../backups.json；后续 README 与 checkpoint 修订分别在本任务 backup 子目录登记，并追加 backup/BACKUP_MANIFEST.md。只查阅本任务恢复记录，没有用备份中的物理材料补齐正式输入。

## 版本和风险

长积分以不可变 wheel01/revision2 重现；wheel02 含更新后的局部适配器与同期共享模块，独立 package-only smoke/Fast/statistics 通过。当前工作树的兼容失败不能回写成这两份快照的结论。保守的模型审计元数据变化会使物理 fingerprint 失效；这是额外重算风险，不是允许错误复用。

同一目录的通用 reader/model_registry/package_loader/兼容入口由另一项连续工作修改，不是本任务新增的物理实现。其余观察变化在 manifest 中标为 concurrent；不把它们收入本任务代码归功或自动回滚。ZIP 的 current-source 部分供审查，先在新目录复现，不直接覆盖活动工作树。
