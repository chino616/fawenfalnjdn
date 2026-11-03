# software：代码、数据与工具怎样组织

本目录解释工程结构，供维护者定位修改入口。工程事实以当前源码和配置为准，文档应指出具体消费者，不能只按理想分层描述。

| 文档 | 实际实现入口 |
|---|---|
| [LAYOUT.md](LAYOUT.md) | flat 布局：唯一活动包为根 `cevns_pyeft/`，数据和产物独立 |
| [runtime-architecture.md](runtime-architecture.md) | `load_experiment → PreparedExperiment → executor → ExperimentPrediction → evaluate_experiment` |
| [experiment-catalog.md](experiment-catalog.md) | `manifest.py` 的活动身份，Catalog 的延迟导入和生命周期检查，旧兼容分派 |
| [resource-management.md](resource-management.md) | `ResourceCatalog`、有限路径别名、作用域和资源清单 |
| [packaging.md](packaging.md) | `pyproject.toml` 的包发现、外置数据、构建与隔离导入 |

## 为什么单独维护

“数据文件放在哪里”和“物理公式是什么”改变时需要不同检查。这里说明入口和依赖关系，例如新增目录不等于注册插件、配置不能覆盖未消费的参数、统计变化为何不重编物理核。

## 管理与新增文件

新的跨模块工程说明放 `<主题>.md`，列出实际文件/函数、输入输出、依赖方、创建/迁移步骤和验证办法。仅某个实验的默认值放 experiments 文档；操作示例放 user-guide；一次运行的构建/审计结果放 outputs。

改动 Catalog、资源解析或打包边界时同步本页和对应说明，并用实际实现核对，不只修改架构图。新增页面从本 README 链接，路径使用相对项目文件位置，避免依赖作者机器的绝对路径。

---

[上一级](../README.md) · [项目总览](../../README.md)
