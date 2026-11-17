# CsI2021

[味分量历史图（2026-11-15）](<../../../../论文图NoteBook/13. CsI2021_Flavor_Components/README.md>)：保留已有预测和分箱，补上从 C/AC 计数协方差传播的统计误差条；尚不包含完整系统误差。[历史 PDF](<../../../../论文图NoteBook/13. CsI2021_Flavor_Components/Figure_CsI2021_Flavor_Components.pdf>) · [生成器](../../../../论文图NoteBook/generate_csi2021_flavor_components.py)。新作图已默认读取[公共主题 v4.0](../../../../plotting/paper_theme/README.md)，输出到新目录。

[CsI2021主线现状与查验入口（2026-11-15）](MAINLINE_REVIEW_20261115.md)：区分99箱时间、9箱能谱及联合分析，集中列出已有结果、P01–P10程序、文献依据、论文图和全部选定文件地址；仅整理现状，未新增计算。

COHERENT 更新 CsI 数据的项目复现身份；当前注册实现使用九个 PE 箱，不等于论文中完整的能量-时间二维分析。

[CsI2021 时间分辨 onboarding 修订草稿](time_resolved/README.md)已并入主项目。该入口展示各章实际数值、原始文件/引文定位、原data中RESPONSE的直接调用映射、用户补充及下一步交接。

- 实验：COHERENT。
- 探测器／靶材：CsI[Na] 闪烁体；主要靶核为 Cs-133、I-127。
- 数据采集起止时间：本次核对的原始测量及补充材料未注明完整日历起止区间，本页不推测；论文说明样本在探测器退役前扩展。
- 数据释放与论文时间：原始测量 [2110.07730v2](../../../references/COHERENT/2110.07730v2.pdf) 首发于 2021-10-14，v2 修订于 2022-06-02，期刊发表于 2022 年。官方附件按 arXiv v2 定位，独立数据释放日期未注明；这些日期不代表数据采集时间。

## 程序中的位置

已接入；真实 `dataset_id` 为 `CsI2021`，身份与活动状态见[唯一注册表](../../../../cevns_pyeft/experiments/dataset_registry.json)。当前实现采用九个 PE 箱的既有复现输入。

- 兼容定义入口：[csi2021_definition.py](../../../../cevns_pyeft/experiments/coherent/csi2021_definition.py)。
- 正式输入目录：[data/experiments/COHERENT_CsI/CsI2021/](../../../../data/experiments/COHERENT_CsI/CsI2021/README.md)。
- 机器输入：[experiment.input.yaml](../../../../data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml)、[experiment.resources.npz](../../../../data/experiments/COHERENT_CsI/CsI2021/experiment.resources.npz)。
- 输入的物理说明：[experiment.physics.md](../../../../data/experiments/COHERENT_CsI/CsI2021/experiment.physics.md)。

这些输入保留既有复现的来源和科学审查限制；论文归档及此 README 不表示它们已经按官方数据完全验证。

## 关联论文

- [更新 CsI 原始测量：2110.07730v2](../../../references/COHERENT/2110.07730v2.pdf)。
- [CsI/LAr 联合分析：2211.11905v2](../../../references/COHERENT/2211.11905v2.pdf)。
- [首次 CsI 观测：1708.01294v1](../../../references/COHERENT/1708.01294v1.pdf)，对应独立的 CsI2017 身份。
- [跨实验 NSI 分析：2409.04703v2](../../../references/General_CEvNS/2409.04703v2.pdf)。
- [通用 EFT 框架：2601.19883v2](../../../references/General_CEvNS/2601.19883v2.pdf)。
- [太阳测量与 COHERENT 等约束比较：2411.11749v1](../../../references/Solar_CEvNS/2411.11749v1.pdf)。

## 对应官方数据资源

官方 [v2 附件入口](https://arxiv.org/abs/2110.07730v2) 及其事件、背景、效率、响应和 ROOT 通量资源已在 [COHERENT 文献 README](../../../references/COHERENT/README.md#csi2021-官方数据附件) 登记。时间分辨草稿现已取得实际附件，文件、SHA、原始网址、读取与变换范围见[来源登记](../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P00_SOURCE_REGISTER.yaml)。原九箱注册输入和时间分析各自的观测、统计与适用性分别说明。

[COHERENT](../README.md) · [COHERENT 文献](../../../references/COHERENT/README.md)
