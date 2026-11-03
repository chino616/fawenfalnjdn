# tools：显式执行的构建、审计和创建工具

这里的脚本由维护者从项目根目录运行，不由 `predict_experiment` 自动调用。物理算法仍在 `cevns_pyeft/`；把管理工具分开，可以看清每个操作读取或生成什么文件。

| 脚本 | 实际输入、操作和输出 |
|---|---|
| [validate_resource_manifest.py](validate_resource_manifest.py) | 用 `--root` 指定包含 data/ 的目录，结合 Catalog/definition 与资源清单检查 ID、路径、覆盖作用域和 SHA256；`--json-out` 可保存报告 |
| [validate_docs.py](validate_docs.py) | 检查 Markdown 本地文件链接；`--scope docs/all` 选择范围，`--json-report` 输出报告；不执行物理计算 |
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

新的跨实验维护命令放 `tools/<动词_对象>.py`，提供明确参数、入口函数、退出码和报告位置；写清是否创建/覆盖文件。实际计算应导入包内函数，不在工具中复制 EFT 公式。只生成当前用户结果的示例放 `examples/`，仅作绘图的脚本放 `论文图NoteBook/`。

新增工具后在此登记命令和副作用；文件解析、身份或迁移工具应有成功与错误输入检查，参考 [test_manifest_and_migration_tools.py](../tests/test_manifest_and_migration_tools.py) 和 [test_runtime_migration_contracts.py](../tests/test_runtime_migration_contracts.py)。机器配置放明确目录并由消费者直接读取，不能隐藏在历史说明副本中。

---

[上一级](../README.md)
