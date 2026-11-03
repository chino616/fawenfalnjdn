# experiment-input：共同规范中的实验输入格式

本目录提供[共同输入规范](../../INPUT_STANDARD.md)引用的实验配置与命名表格格式。它们供接入和检查文件时使用；每种格式的适用范围与实际读取器应一起核对。

| 文件 | 实际声明内容 |
|---|---|
| [experiment.schema.json](experiment.schema.json) | 实验说明最少需要 `dataset_name`、`source_type`、`target_mode`；另外描述 source 类型和部分可选字段 |
| [csv_contracts.json](csv_contracts.json) | reactor spectrum、efficiency、bin edges、isotopes 的列名、递增/范围/分数和等约定 |

## 与实际代码的边界

[experiments/specs.py](../../../../cevns_pyeft/experiments/specs.py) 用自己的小型 YAML 解析器和 `validate_experiment_spec_data` 检查必需字段，没有加载这里的 JSON Schema。`load_experiment` 也不因新增 schema 自动获得新输入格式。

当前 CsI2017 的实际坐标绑定由 [statistics/tables.py](../../../../cevns_pyeft/statistics/tables.py) 读取该数据集的 `observation_schema.json` 完成；资源完整性由 [validate_resource_manifest.py](../../../../tools/validate_resource_manifest.py) 检查。两者职责不同，不能把声明文件存在理解为所有科学语义已验证。

`csv_contracts.json` 是命名格式约定表，不是 JSON Schema。其 `energy_evee` 等列只约束选择该 profile 的数据；PE、其他观测量及既有 legacy 表使用自己的明确映射，不强制改列或转换单位。

## 管理与新增文件

多个数据集共用的新格式可以在这里新增 `<格式名>.schema.json`，或在 CSV 合同中增加明确条目，并从共同输入规范登记适用条件和消费者。只属于一个数据集的坐标/列映射放在其 `data/experiments/.../statistics/`。

每次新增必须说明字段、单位、必填项及版本，并确定由哪个工具或 loader 实际加载验证；若没有消费者，标明它只是格式声明。需要自动验证时同时实现调用、失败信息和有效/无效样例测试。schema 变动不能替代修改具体 definition 和读取器，也不能自动激活新实验。

---

[共同输入规范](../../INPUT_STANDARD.md) · [共享目录](../../README.md)
