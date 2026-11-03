# experiments：按数据集解释实际模型与分析

当前本目录集中保存 [COHERENT](COHERENT/README.md) 三个活动实验的说明和两组科学审查。运行身份仍由 [manifest.py](../../cevns_pyeft/experiments/manifest.py) 决定，不由这里的目录自动注册。

| 说明入口 | 实际代码与输入归属 |
|---|---|
| [COHERENT/CsI2017](COHERENT/CsI2017/README.md) | `csi2017_definition.py`；25 箱、确定性 PE 映射、外部效率/统计表 |
| [COHERENT/CsI2021](COHERENT/CsI2021/README.md) | `csi2021_definition.py`；九箱、组合式模型、gamma 响应和内联统计数组 |
| [COHERENT/Ar2020](COHERENT/Ar2020/README.md) | `ar2020_definition.py`；十二箱、sigma(observed) 折叠和内联统计数组 |
| [COHERENT/reviews/](COHERENT/reviews/) | statistics review 与 Fig.3–Fig.7 overlap review 的独立历史分析、CSV 和证据 |

## 为什么不把说明放在数据表或源码旁一份一份复制

实验文档解释来源、选择与能力；`data/experiments/` 保存真正被读取的输入，`cevns_pyeft/experiments/` 保存定义和算法。三者通过 dataset ID、资源路径和代码链接对应，避免在 README 中另维护一套会被误当作运行默认值的数值表。

## 管理与新增文件

已运行实验的新说明放 `docs/experiments/<实验族>/<dataset_id>/`，链接自己的 definition、资源及验证入口。新增真实数据集的资料和合同按 Master/workflow 的获准身份创建；仅写 README 或放论文不会启用新模型。

新的科学审查使用独立、带日期和主题的目录，配套记录生成命令、代码/输入身份、统计定义及原始输出。不要把两项分析不同的历史 CSV 合并为一组“当前结果”，也不要改写旧证据中的数值来匹配新代码。当前目录整理后的分类以本页为入口，工程运行日志由 `outputs/` 管理。

---

[上一级](../README.md) · [项目总览](../../README.md)
