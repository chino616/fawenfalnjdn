# Ar2020

COHERENT CENNS-10 首次液氩 CEvNS 测量的项目复现身份；测量论文和数据释放说明指向同一测量，不另设两个 Dataset。

- 实验：COHERENT。
- 探测器／靶材：CENNS-10 液氩探测器；靶核为 Ar-40。
- 数据采集时间：2017 年 7 月至 2018 年 12 月，见 2003.10630v7 正文的数据选择说明。
- 数据释放与论文时间：测量论文 arXiv:2003.10630（本库 v7 为 2021 年论文版本）；数据释放说明 arXiv:2006.12659（本库 v2 为 2020-07-29 论文版本），发布数据 DOI：[10.5281/zenodo.3903810](https://doi.org/10.5281/zenodo.3903810)。精确数据释放日期／版本本页未注明，论文版本时间不代替释放时间。

## 程序中的位置

已接入；真实 `dataset_id` 为 `Ar2020`，身份与活动状态见[唯一注册表](../../../../cevns_pyeft/experiments/dataset_registry.json)。当前实现采用12 个观测能量箱的既有复现输入。

- 兼容定义入口：[ar2020_definition.py](../../../../cevns_pyeft/experiments/coherent/ar2020_definition.py)。
- 正式输入目录：[data/experiments/COHERENT_Ar/Ar2020/](../../../../data/experiments/COHERENT_Ar/Ar2020/README.md)。
- 机器输入：[experiment.input.yaml](../../../../data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml)、[experiment.resources.npz](../../../../data/experiments/COHERENT_Ar/Ar2020/experiment.resources.npz)。
- 输入的物理说明：[experiment.physics.md](../../../../data/experiments/COHERENT_Ar/Ar2020/experiment.physics.md)。

这些输入保留既有复现的来源和科学审查限制；论文归档及此 README 不表示它们已经按官方数据完全验证。

## 关联论文

- [首次氩测量：2003.10630v7](../../../references/COHERENT/2003.10630v7.pdf)。
- [同一测量的数据释放说明：2006.12659v2](../../../references/COHERENT/2006.12659v2.pdf)。
- [CsI/LAr 联合分析：2211.11905v2](../../../references/COHERENT/2211.11905v2.pdf)。
- [跨实验 NSI 分析：2409.04703v2](../../../references/General_CEvNS/2409.04703v2.pdf)。
- [通用 EFT 框架：2601.19883v2](../../../references/General_CEvNS/2601.19883v2.pdf)。
- [太阳测量与 COHERENT 等约束比较：2411.11749v1](../../../references/Solar_CEvNS/2411.11749v1.pdf)，属于再分析，非 Ar2020 的新数据释放。

[COHERENT](../README.md) · [COHERENT 文献](../../../references/COHERENT/README.md)
