# Tasks 02–10 连续执行进度

用户最新指示：每项完成后输出总结并继续，不在默认任务停点等待。
此指示不授予未确认物理的人工批准；缺失/冲突保留能力限制。若执行被额度或会话中断，
从此索引及对应任务报告核对文件、分支和实际测试后恢复，不重复已完成任务。

工作区：当前 `refactor/07-gitup01-20261104` 的 `Gitup01/`。
起始 HEAD：`520e1d0a33913a6793b326ed493f5b66e0004a0a`。不提交/推送。

| Task | 状态 | 权威报告/下一步 |
|---|---|---|
| 01 | 完成三文件提取；科学 PARTIAL | [Pilot 报告](CSI2021_ONBOARDING_PILOT_REPORT.md)，保留为历史报告。 |
| 02 | 完成 | [Schema 报告](EXPERIMENT_INPUT_SCHEMA_REPORT.md)；全局保护检查有保留并行文件造成的独立失败。 |
| 03 | 完成 | [模型绑定报告](PHYSICS_MODEL_BINDING_REPORT.md)；71/80 项分组测试通过。 |
| 04 | 完成 | [Loader 报告](EXPERIMENT_PACKAGE_LOADER_REPORT.md)；98 项合同与 16 项既有回归通过。 |
| 05 | 完成 | [运行迁移报告](CSI2021_PACKAGE_RUNTIME_MIGRATION_REPORT.md)；默认入口、旧格式和小网格 Fast 已验证。 |
| 06 | 完成 | [独立验证](CSI2021_STANDALONE_VALIDATION_REPORT.md)；I01–I10 通过，默认收敛未证明。 |
| 07 | 完成 | [来源报告](CSI2021_SCIENTIFIC_PROVENANCE_REPORT.md)；九问题/105字段，未闭合科学能力仍受限。 |
| 08 | 完成 | [通用生成器](GENERAL_ONBOARDING_GENERATOR_REPORT.md)；56项测试；历史待核对链接在最终验收通过。 |
| 09 | 完成 | [生命周期报告](DATASET_PACKAGE_LIFECYCLE_REPORT.md)；分发/安装/事务验证，全局保护与链接通过。 |
| 10 | 完成 | [项目总报告](PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md)；三实验默认两文件 Runtime、九份正式文件、sdist/wheel/外部cwd/隔离运行和拆装验收通过。 |

最终 checkpoint：Tasks02–10工程完成；Task10先Ar2020、再CsI2017，已完成三文件→现有Runtime→独立安装/回归。
最终35项合同、13项compiler、25项生命周期、12项legacy及独立安装通过；各组有重叠不累加。
科学DRAFT/PARTIAL、人工NOT_REVIEWED；官方likelihood、一般反中微子EFT与科学发布继续BLOCKED。
没有commit/push或切换分支。最终证据为outputs/onboarding/task10/results.json及项目总报告；不自动进入新任务。
用户明确要求保留原样的三个并行文件：coherent/csi2021_package.py、
coherent/csi2021_package_contract.json、tests/test_csi2021_input_package.py；不依赖其实现。
恢复时首先运行当前任务的只读校验；后续状态以任务报告实际命令与产物为准。
