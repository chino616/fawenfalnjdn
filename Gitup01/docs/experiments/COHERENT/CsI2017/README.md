# CsI2017

COHERENT 首次 CsI CEvNS 观测的项目复现身份，与更新的 CsI2021 分开。

- 实验：COHERENT。
- 探测器／靶材：CsI[Na] 闪烁体；主要靶核为 Cs-133、I-127。
- 数据采集起止时间：本页所用来源未注明。原始论文正文说明 308.1 个束流开启有效日与 153.5 个束流关闭有效日；有效运行天数不等于日历起止时间。
- 数据释放与论文时间：关联的是 2017 年首次观测；当前本地资料未注明独立数据释放的精确日期／版本。`2017` 不作为采集年份推断。

## 程序中的位置

已接入；真实 `dataset_id` 为 `CsI2017`，身份与活动状态见[唯一注册表](../../../../cevns_pyeft/experiments/dataset_registry.json)。当前实现采用25 个 PE 箱的既有复现输入。

- 兼容定义入口：[csi2017_definition.py](../../../../cevns_pyeft/experiments/coherent/csi2017_definition.py)。
- 正式输入目录：[data/experiments/COHERENT_CsI/CsI2017/](../../../../data/experiments/COHERENT_CsI/CsI2017/README.md)。
- 机器输入：[experiment.input.yaml](../../../../data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml)、[experiment.resources.npz](../../../../data/experiments/COHERENT_CsI/CsI2017/experiment.resources.npz)。
- 输入的物理说明：[experiment.physics.md](../../../../data/experiments/COHERENT_CsI/CsI2017/experiment.physics.md)。

这些输入保留既有复现的来源和科学审查限制；论文归档及此 README 不表示它们已经按官方数据完全验证。

## 关联论文

- [首次观测论文：1708.01294v1](../../../references/COHERENT/1708.01294v1.pdf)。
- [后续 CsI/LAr 联合分析：2211.11905v2](../../../references/COHERENT/2211.11905v2.pdf)，比较旧 CsI 数据；其更新 CsI 输入不等同于 CsI2017。
- [跨实验 NSI 分析：2409.04703v2](../../../references/General_CEvNS/2409.04703v2.pdf)。
- [通用 EFT 框架：2601.19883v2](../../../references/General_CEvNS/2601.19883v2.pdf)。

[COHERENT](../README.md) · [COHERENT 文献](../../../references/COHERENT/README.md)
