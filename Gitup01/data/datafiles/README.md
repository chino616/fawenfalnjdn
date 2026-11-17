# datafiles：历史混合资料，不再接收新数据

本目录现保留六份 SNS/CHOOZ 旧辅助文件。当前三个正式 Package 不读取它们；源谱来自各自 NPZ，生成来源是原有 SNS 代码，不是这里的同名 TXT。2026-11-06 两份已核实归属的 Ar2020 表原样移入 Dataset；七份太阳 8B 表维持 2026-11-05 的清理归档，不恢复为活动输入。

## 六份现存文件

以下文件已与 Bradley Kavanagh 的 [CEvNS 仓库固定提交](https://github.com/bradkav/CEvNS/tree/6adce961e769cfbf8edc9acef140ebac46009c36/DataFiles)逐值核对：五份数值文件完全一致，`NeutrinoList.txt` 仅换行不同。本地存在换行/数字写法差异，因此不称字节一致；更早的一手生成来源尚未核实，不将第三方代码表称为合作组官方数据。

| 文件 | 原文件位置、列含义与单位 | 转换与当前消费者 |
|---|---|---|
| [SNSflux_nue.txt](SNSflux_nue.txt) | 上游 `DataFiles/SNSflux_nue.txt`；50×2：中微子能量 MeV、归一化前 νe 谱表值（原始纵轴绝对单位未独立确认） | 上游另乘源强并除以 DAR 积分；本地仅数值格式不同，无当前 Runtime 消费者 |
| [SNSflux_numu.txt](SNSflux_numu.txt) | 上游 `DataFiles/SNSflux_numu.txt`；147×2：MeV、归一化前 νμ 谱表值（原始纵轴绝对单位未独立确认） | 同上；不能当作当前 Package 的 prompt 谱线或已积分注量 |
| [SNSflux_numub.txt](SNSflux_numub.txt) | 上游 `DataFiles/SNSflux_numub.txt`；28×2：MeV、归一化前反νμ 谱表值（原始纵轴绝对单位未独立确认） | 同上；上游由该表计算 DAR 归一化，再用于三味谱 |
| [neutrino_spectrum.txt](neutrino_spectrum.txt) | 上游 `DataFiles/neutrino_spectrum.txt`；20000×2：能量 keV、旧 CHOOZ 反应堆谱的每 keV 未缩放值；独立绝对单位/最初物理谱模型尚未核实 | 上游横轴 ×10⁻³ 转 MeV，纵轴 ×10³ 并乘 `ScaleConstants` 首值；当前无读取者 |
| [ScaleConstants.txt](ScaleConstants.txt) | 上游同名文件；1×2，`[1.326e10, 0]`；首值是上述 CHOOZ 归一化常数，独立单位未完整说明 | 上游读取首值，第二值未用；本地未改数值，当前无读取者 |
| [NeutrinoList.txt](NeutrinoList.txt) | 上游同名文件；文本 `neutrino_spectrum`，是旧谱文件名指针，无物理单位 | 与上游换行归一后相同；当前无读取者 |

上游的具体操作见 [CEvNS.py 的 loadNeutrinoFlux](https://github.com/bradkav/CEvNS/blob/6adce961e769cfbf8edc9acef140ebac46009c36/CEvNS.py#L320-L382)。其输出通量按代码约定为 `cm^-2 s^-1 MeV^-1`，不能由此将原始未归一化表的纵轴直接写成该单位。旧上游的源强和端点也不能替代本项目正式 YAML 中的运行期注量约定。

## 两份已归位的 Ar2020 文件

| 原 `datafiles/` 文件 | 当前位置、来源与含义 |
|---|---|
| `Ar_eff.txt` | [Ar2020/detector/Ar_eff.txt](../experiments/COHERENT_Ar/Ar2020/detector/Ar_eff.txt)；80×2，逐值等于官方 `CENNS10AnlAEfficiency.txt` 第 2、3 列：keVnr、效率；是选列派生表，历史选列操作人/时间未知 |
| `cevnspdf.txt` | [Ar2020/statistics/cevnspdf.txt](../experiments/COHERENT_Ar/Ar2020/statistics/cevnspdf.txt)；960×4，逐值等于 [COHERENT 官方 release](https://doi.org/10.5281/zenodo.3903810)同名文件；keVee、F90、μs、每箱 SM 预期事件数 |

两份文件只改变位置，SHA256 不变；均未接入当前 Package。列坐标、归一化及官方说明见 [Ar2020 README](../experiments/COHERENT_Ar/Ar2020/README.md)。它们不是当前观测数组或可任意互换的效率坐标。

## 七份此前归档的太阳 8B 文件

下表补齐分析文档中原 15 份文件的去向。原字节保存在 `backup/solar-b8-legacy-cleanup-20261105-01/data/datafiles/`；本次不移动或修改归档。六份未取得历史导出链的表仍写来源未知，不把候选图线升级成官方来源。

| 原文件 | 来源核实与内容边界 |
|---|---|
| `8Bflux_nu.txt` | 已核实与 [Bahcall 官网谱表](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)前两列 829 行逐值一致；MeV、MeV⁻¹，单位归一化谱形，离散积分约 0.999986544；不含总通量、曝光或效率 |
| `8Bflux_Ortiz.txt` | 历史导出来源未知；123×2；谱形候选，零尾/端点的生成规则未确认 |
| `8Bflux_eff.txt` | 历史导出来源未知；48×2；旧 Notebook 曾作为 PandaX US2 效率使用，不能凭该用法证明原始出处、单位和效率组成 |
| `8Bflux_effpaired.txt` | 历史导出来源未知；155×2；paired 效率候选，具体取点/插值未确认 |
| `8Bflux_Paired.txt` | 历史导出来源未知；79×2；不能与上一份表自动当成独立效率因子相乘 |
| `8Bflux_Eff_XENONnT.txt` | 历史导出来源未知；74×2；接受度候选，尾部恒值延伸规则未确认 |
| `Xenon_8B_2024_spectrum_w_acceptance.txt` | 历史导出来源未知；71×2；含接受度 SM 参考谱候选，不能充当入射源通量 |

[清理说明](../../backup/solar-b8-legacy-cleanup-20261105-01/README.md)与[原路径/哈希清单](../../backup/solar-b8-legacy-cleanup-20261105-01/MANIFEST.json)保留回滚信息。归档不作为新实验的默认输入；恢复使用前仍须核实来源、列单位、谱形/绝对通量、有效域和响应因子。隔离运行快照中的同名文件不在此前清理范围内。

## 保留与维护边界

历史 `tests/reference/interface_refactor_v1/metadata.json` 保留当时的旧路径/哈希，不随本次归位改写为新的物理参考。本目录不再接收新数据；已确认专属于实验的资料放入该 Dataset，对照材料也在其 README 说明，不因文件移动自动建立资源绑定。

不根据文件名猜单位，不规范化原表字节，不为通过验证重建数值。资源读取与有限旧路径兼容见 [data 总览](../README.md)及 [resources.py](../../cevns_pyeft/foundation/resources.py)。

---

[上一级](../README.md) · [项目总览](../../README.md)
