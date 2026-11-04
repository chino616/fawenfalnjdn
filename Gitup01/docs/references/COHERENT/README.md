# COHERENT 文献

收录 COHERENT 的 CsI、液氩测量、公开数据说明和 CsI/LAr 联合分析。

分类以本页小标题区分；本目录内全部论文如下。每份 PDF 仅在文献库中保存一次。

## CsI2017：首次观测

### Observation of Coherent Elastic Neutrino-Nucleus Scattering

- 作者：D. Akimov et al.（COHERENT Collaboration）。
- arXiv：[1708.01294v1](https://arxiv.org/abs/1708.01294v1)；归档版本：v1。
- 涉及实验／数据集：COHERENT / CsI2017。
- 本地文件：[PDF](1708.01294v1.pdf)。

报告利用 SNS 中微子源和 CsI[Na] 探测器首次观测 CEvNS，是项目 CsI2017 身份和探测器背景的原始文献。

## Ar2020：测量与数据释放

### First Measurement of Coherent Elastic Neutrino-Nucleus Scattering on Argon

- 作者：D. Akimov et al.（COHERENT Collaboration）。
- arXiv：[2003.10630v7](https://arxiv.org/abs/2003.10630v7)；归档版本：v7。
- 涉及实验／数据集：COHERENT / Ar2020。
- 本地文件：[PDF](2003.10630v7.pdf)。

报告 CENNS-10 液氩探测器对 CEvNS 的首次测量，说明 2017 年 7 月至 2018 年 12 月采集的数据、信号和背景分析。

### COHERENT Collaboration data release from the first detection of coherent elastic neutrino-nucleus scattering on argon

- 作者：D. Akimov et al.（COHERENT Collaboration）。
- arXiv：[2006.12659v2](https://arxiv.org/abs/2006.12659v2)；归档版本：v2。
- 涉及实验／数据集：COHERENT / Ar2020。
- 本地文件：[PDF](2006.12659v2.pdf)。

说明首次液氩测量的公开数据释放，包括能量、F90、时间三维分箱及一维投影；对应数据发布 DOI 为 10.5281/zenodo.3903810。它是同一测量的数据说明，不另立 Dataset。

## CsI2021：更新 CsI 原始测量

### Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT

- 作者：D. Akimov et al.（COHERENT Collaboration）。
- arXiv：[2110.07730v2](https://arxiv.org/abs/2110.07730v2)；归档版本：v2（2022-06-02）。
- 期刊 DOI：[10.1103/PhysRevLett.129.081801](https://doi.org/10.1103/PhysRevLett.129.081801)。
- 涉及实验／数据集：COHERENT / 更新 CsI 数据；项目 CsI2021。
- 本地文件：[PDF](2110.07730v2.pdf)。

更新的 CsI[Na] 截面测量原始论文，采用增加后的 SNS 数据及改进的淬灭模型，并利用束流时间结构研究中微子味。官方事件和响应附件与项目现有九箱复现输入分别登记。

## CsI2021 与 Ar2020：联合分析

### Physics implications of a combined analysis of COHERENT CsI and LAr data

- 作者：V. De Romeri, O. G. Miranda, D. K. Papoulias, G. Sanchez Garcia, M. Tórtola, J. W. F. Valle。
- arXiv：[2211.11905v2](https://arxiv.org/abs/2211.11905v2)；归档版本：v2。
- 涉及实验／数据集：COHERENT / CsI2021、Ar2020；比较 CsI2017。
- 本地文件：[PDF](2211.11905v2.pdf)。

对更新的 COHERENT CsI 数据和液氩数据作联合统计分析，讨论标准模型检验及新物理约束，并处理效率、时间分布等不确定度。这是分析论文，不是新的独立数据释放。

## CsI2021 官方数据附件

来源为 [2110.07730v2 的 Ancillary files](https://arxiv.org/abs/2110.07730v2)，说明见[官方 Supplemental Material](https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf)。附件按论文 v2 定位；v2 日期 2022-06-02 是论文修订时间，不作为独立数据发布日。

| 资源 | 格式与主要含义 |
|---|---|
| [dataBeamOnC.txt](https://arxiv.org/src/2110.07730v2/anc/dataBeamOnC.txt)、[dataBeamOnAC.txt](https://arxiv.org/src/2110.07730v2/anc/dataBeamOnAC.txt) | 已选择的束流开启 C／AC 区间事件；每个事件含重建能量 PE 和时间 `t_rec`（µs） |
| [brnPE.txt](https://arxiv.org/src/2110.07730v2/anc/brnPE.txt)、[brnTrec.txt](https://arxiv.org/src/2110.07730v2/anc/brnTrec.txt) | 束流相关中子背景的能量／时间分布 |
| [ninPE.txt](https://arxiv.org/src/2110.07730v2/anc/ninPE.txt)、[ninTrec.txt](https://arxiv.org/src/2110.07730v2/anc/ninTrec.txt) | 中微子诱发中子背景的能量／时间分布 |
| [effCoefficients.txt](https://arxiv.org/src/2110.07730v2/anc/effCoefficients.txt) | 能量效率及其不确定度参数 |
| [scintRespCoefficients.txt](https://arxiv.org/src/2110.07730v2/anc/scintRespCoefficients.txt) | 闪烁响应／淬灭关系及其不确定度参数 |
| [snsFlux2D.root](https://arxiv.org/src/2110.07730v2/anc/snsFlux2D.root) | 各中微子味的二维源通量直方图 |

以上列出本次核对的主要附件，不把页面未展开的其他附件猜写为完整清单。资源未下载或逐数值校验；使用时需按补充材料分别核对效率、时间窗口和归一化。官方逐事件附件不是当前项目九箱 YAML/NPZ 的替代品，项目输入位置见 [CsI2021](../../experiments/COHERENT/CsI2021/README.md)。

## 相关资料

[COHERENT 实验](../../experiments/COHERENT/README.md)及 [CsI2017](../../experiments/COHERENT/CsI2017/README.md)、[CsI2021](../../experiments/COHERENT/CsI2021/README.md)、[Ar2020](../../experiments/COHERENT/Ar2020/README.md)。跨实验 NSI 与通用 EFT 文献见 [General_CEvNS](../General_CEvNS/README.md)；另见太阳测量再分析 [2411.11749v1](../Solar_CEvNS/2411.11749v1.pdf)，其中包含 COHERENT 比较。

[文献总目录](../README.md)
