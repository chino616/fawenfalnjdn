# datafiles：保留的谱表和旧辅助资料

本目录保存 `8Bflux_*.txt`、`SNSflux_*.txt`、`Xenon_8B_2024_spectrum_w_acceptance.txt`、`Ar_eff.txt` 等表，以及 `ScaleConstants.txt`、`NeutrinoList.txt` 等辅助资料。它们在当前副本中被保留，但文件存在不代表已绑定到活动实验。

## 与当前运行路径的关系

三个活动实验的有效输入由 [各自 definition](../../cevns_pyeft/experiments/coherent/) 和 [资源清单](../resource_manifest.json) 决定。当前 SNS 注量由 [SNSLegacySource](../../cevns_pyeft/sources/sns.py) 调用 COHERENT 的谱构造代码产生，并不直接读取这里的 `SNSflux_*.txt`。

旧 COHERENT 效率/观测表已经迁到 `data/experiments/`；旧地址由 [resources.py](../../cevns_pyeft/foundation/resources.py) 的有限映射兼容。名称相似的 `Ar_eff.txt` 不能替代已绑定的 `CENNS10AnlAEfficiency.txt`。

## 为什么保留，怎样管理

这些文件可以用于来源追踪和研究对照，不能仅凭文件名判断单位、是否含效率或适用的数据集。新的正式实验输入优先放 `data/experiments/<实验族>/<dataset_id>/`，不要继续把不同实验的新数据堆在这个旧混合目录。

若明确需要接入某张表，先补足来源、列语义、归一化与适用范围，再编写/选择读取器、在 definition 声明资源并验证实际调用；仅复制文件不会生效。原表受内容保护，重新整理时保留原始字节及溯源记录。管理入口见 [data 总览](../README.md)。

---

[上一级](../README.md) · [项目总览](../../README.md)
