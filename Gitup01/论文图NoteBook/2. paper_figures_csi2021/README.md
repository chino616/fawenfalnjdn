# paper_figures_csi2021：CsI2021 的截面、源谱与参考图

本目录对应 [CsI2021 Notebook](<../2. CEvNS_pyEFT_COHERENT_CsI2021_paper_figures.ipynb>) 的前三组图；v2 Notebook 的前半部分也保留同类流程。

| 文件前缀 | 内容与计算入口 |
|---|---|
| `fig_csi_01_flavor_dsigma` | `differential_cross_section_nn` 的味相关截面 |
| `fig_csi_02_sns_recoil_components` | `loadNeutrinoEmpiricalFluxSNS`、`sns_component_state` 与 `_rate_per_kg` 的 SNS 反冲分量 |
| `fig_csi_03_detector_reference` | `slow_counts_csi2021` 计数和 Notebook 中声明的实验参考数组展示 |

PDF/PNG/CSV 按前缀配套管理。画出参考点不等于调用完整 likelihood，也不等于完成拟合。

## 为什么单独保存，怎样扩展

这组图对应特定 Notebook 的展示配置，不与后续统一 R/W/K 或收敛计数图混用元数据。新增图在来源 Notebook 或独立生成器中增加计算/导出步骤，沿用公共 API，保存对应数据、参数和单位；需要新的基准时建立独立输出目录。

Notebook 默认 `FIGURE_DIRNAME="paper_figures_csi2021"`，写入 `ROOT/paper_figures_csi2021`，不是本目录。若需更新本组，应显式选择 `论文图NoteBook/2. paper_figures_csi2021`，并按[上级说明](../README.md)核对显式 `PROJECT_ROOT`、包导入和旧 src 路径。不要只替换 PNG 而保留不匹配的 CSV。

---

[上一级](../README.md) · [项目总览](../../README.md)
