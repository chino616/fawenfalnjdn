# user-guide：直接对应公共接口的使用方法

本目录回答用户“怎样调用现有功能”。它不保存执行状态；实际参数校验由 `cevns_pyeft` 完成。

| 文档 | 对应调用或约束 |
|---|---|
| [USAGE.md](USAGE.md) | `ResourceCatalog`、`load_experiment`、prediction/evaluation、selection 和组件覆盖 |
| [COMPONENTS.md](COMPONENTS.md) | `ExperimentModel` 与合同；CsI2021 组件替换、raw 与物理分量区别 |
| [FAST_AND_CACHE.md](FAST_AND_CACHE.md) | `compile_fast`、`CompiledKernel.predict`、保存加载、依赖指纹与固定态限制 |
| [capability-matrix.md](capability-matrix.md) | 三个实验各自支持的 Slow/Fast/统计能力，避免把统一接口理解为算法相同 |
| [parameter-ownership.md](parameter-ownership.md) | 默认值属于哪份 definition，哪些变化影响预测、核或统计 |
| [workflow-operation.md](workflow-operation.md) | 如何使用现有协作流程；与物理运行 API 分开 |

## 为什么与软件/物理说明分开

这里按用户操作组织：例如要更换源，应看到 `components={"source": ...}`、被消费的位置及能力限制；目录管理和实现归属另见 software，公式/单位的科学依据另见 physics。

## 管理与新增文件

新的已有功能教程放 `<主题>.md`，说明适用实验、前置条件、最小调用、返回对象/单位和失败边界，并链接实现与现有测试。用 `TheoryPoint` 扫描参数、用 definition/components 改实例、用 selection 选实验，这三类操作不要混写。

代码示例先在声明的环境/目录验证；小网格标明仅为接口演示。功能发生变化时同步对应指南、能力矩阵和示例，不通过文档宣称尚未实现的后端。新增页面后在本 README 登记，并检查本地链接。

---

[上一级](../README.md) · [项目总览](../../README.md)
