# tools：显式执行的构建、审计和创建工具

这里的脚本由维护者从项目根目录运行，不由 `predict_experiment` 自动调用。物理算法仍在 `cevns_pyeft/`；把管理工具分开，可以看清每个操作读取或生成什么文件。

| 脚本 | 实际输入、操作和输出 |
|---|---|
| [validate_resource_manifest.py](validate_resource_manifest.py) | 用 `--root` 指定包含 data/ 的目录，结合 Catalog/definition 与资源清单检查 ID、路径、覆盖作用域和 SHA256；`--json-out` 可保存报告 |
| [validate_docs.py](validate_docs.py) | 只读检查 Markdown 本地文件链接；`--files` 精确检查受影响 README/文档，优先于 `--scope docs/all`；默认跳过 backup、outputs 与缓存，`--json-report` 保存结果；不自动改写内容 |
| [readme_maintenance.py](readme_maintenance.py) | `plan` 按 Git/快照生成目录分组影响清单；`snapshot` 保存当前文件基线；`sync/check --readmes` 同步/检查明确选定的 README 自动清单区，保留人工说明并备份；不删除文件或提交 Git |
| [update_skill_library.py](update_skill_library.py) | 默认/`--check` 只读核对 [Skill 总表](../cevns_pyeft/SKILLS.md)；`--write` 从 catalog 展示摘要和 WORKFLOW 实际引用刷新标记区，保留人工规则，备份旧文件并登记；不改保护哈希或 runtime |
| [scaffold_experiment.py](scaffold_experiment.py) | 按 `--root`、`--dataset-id`、`--module-name` 创建演示实验包与合同测试，拒绝已存在的目录/ID；不注册到内置 manifest |
| [build_wheel.py](build_wheel.py) | 离线、无依赖安装地构建 wheel，再安装到项目内独立 target；写 `outputs/release/` 的 wheel、日志和 `wheel.json` |
| [verify_wheel.py](verify_wheel.py) | 读取 `wheel.json` 的安装路径，在项目外 cwd 用 `python -I` 检查三实验预测，写 `outside_cwd.json/log` |
| [workflow_validation/](workflow_validation/README.md) | 工作流校验器直接读取的保护清单和历史路径例外 |

## 常用命令与实际副作用

```powershell
python tools/validate_resource_manifest.py --root .
python tools/validate_docs.py --scope docs
python tools/scaffold_experiment.py --dataset-id DemoReadme --module-name demo_readme --root outputs/scaffold-demo
```

第三条命令会在指定根下创建 `cevns_pyeft/experiments/demo_readme/` 的 `__init__.py`、`definition.py`、`execution.py`、`resources.yaml`、`capabilities.yaml`，以及 `tests/test_demo_readme_contract.py`。它是 synthetic 工程骨架；后续需实现模型、资源和能力，并先用 custom catalog 验证。

构建顺序是 `python tools/build_wheel.py`，然后 `python tools/verify_wheel.py`。后者当前在项目旁 `CONUS-Backup/_migration/wheel_outside_cwd` 创建外部工作目录；这个目录名是脚本的历史路径，不表示恢复 CONUS。当前副本内旧 `wheel.json` 指向旧位置，验证前需先在当前根重新构建。

## 管理与新增文件

所有工具和说明执行[文件与 README 联动规则](../workflows/_shared/policies/file-lifecycle.md)：文件变化和相应目录条目、命令及上级导航在同次任务中维护。检查本次受影响文档可运行 `python tools/validate_docs.py --files README.md tools/README.md`；该命令只报告失效链接，新增文件的用途覆盖、正文裸路径和消费者仍须按变更清单核对。

大批量维护的基线、目录分组、自动清单区和 Git 复查步骤见[维护流程](../workflows/cevns-pyeft/definitions/repository-maintenance/WORKFLOW.md)。报告默认不覆盖；`sync` 是显式写操作，会在 backup 创建改动前 README 副本并追加清单，计划与验收保持只读。

新的跨实验维护命令放 `tools/<动词_对象>.py`，提供明确参数、入口函数、退出码和报告位置；写清是否创建/覆盖文件。实际计算应导入包内函数，不在工具中复制 EFT 公式。只生成当前用户结果的示例放 `examples/`，仅作绘图的脚本放 `论文图NoteBook/`。

新增工具后在此登记命令和副作用；文件解析、身份或迁移工具应有成功与错误输入检查，参考 [test_manifest_and_migration_tools.py](../tests/test_manifest_and_migration_tools.py) 和 [test_runtime_migration_contracts.py](../tests/test_runtime_migration_contracts.py)。机器配置放明确目录并由消费者直接读取，不能隐藏在历史说明副本中。

---

[上一级](../README.md)

<!-- readme-inventory:start -->
**当前活动目录内容（自动维护区）**

备份、生成结果和历史/冻结证据不列入此区；用途见人工说明。

| 路径 | 类型 |
|---|---|
| [workflow_validation/](workflow_validation/README.md) | 目录 |
| [build_wheel.py](build_wheel.py) | 文件 |
| [readme_maintenance.py](readme_maintenance.py) | 文件 |
| [scaffold_experiment.py](scaffold_experiment.py) | 文件 |
| [update_skill_library.py](update_skill_library.py) | 文件 |
| [validate_docs.py](validate_docs.py) | 文件 |
| [validate_resource_manifest.py](validate_resource_manifest.py) | 文件 |
| [verify_wheel.py](verify_wheel.py) | 文件 |
<!-- readme-inventory:end -->
