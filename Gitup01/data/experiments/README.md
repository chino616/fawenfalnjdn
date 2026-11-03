# data/experiments：按实验身份保存输入

这里与 `cevns_pyeft/experiments/` 分工：本目录拥有数据文件，代码目录拥有定义和算法。`load_experiment` 只读取 definition 明确声明的资源，不因目录名或 YAML 自动启用实验。

| 现有位置 | 实际消费者 |
|---|---|
| [COHERENT_CsI/CsI2017](COHERENT_CsI/CsI2017/README.md) | `csi2017_definition.py` 绑定效率、四份原始统计表及 `observation_schema.json`；统计表由 `statistics.tables.csi2017_tables` 读取 |
| [COHERENT_CsI/CsI2021](COHERENT_CsI/CsI2021/README.md) | 保存 spec/provenance；当前九箱观测及误差在 `csi2021_definition.py` 中定义 |
| [COHERENT_Ar/Ar2020](COHERENT_Ar/Ar2020/) | `ar2020_definition.py` 读取 detector 效率表；十二箱统计数组在定义中保存 |
| `external/` | 当前无活动定义因该目录存在而被注册；其存在不构成运行能力 |

`experiments.specs` 可发现和读取 `experiment.yaml`，这属于说明接口；活动 runtime 仍由 Catalog/manifest 决定。

## 新文件如何进入一次预测

```text
data/experiments/<实验族>/<dataset_id>/<职责>/文件
  → definition.resources 中的 ResourceRef
  → ResourceCatalog 解析并记录内容
  → prepare/resolved_resources 或统计 loader
  → 预测或统计评价
```

新 dataset 采用独立身份目录；detector 输入放 `detector/`，观测/误差/坐标映射放 `statistics/`，来源说明与文件相邻维护。该布局用于明确归属；读取行为由资源绑定决定，不依赖自动扫描所有子目录。

创建文件后同步 [resource_manifest.json](../resource_manifest.json) 的 ID、路径、哈希与坐标合同，并测试缺文件、错单位/错坐标和资源覆盖。真实新实验的接入需先通过[工作流入口](../../workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md)确认范围；创建数据目录本身不替代这一步。

---

[上一级](../README.md) · [项目总览](../../README.md)
