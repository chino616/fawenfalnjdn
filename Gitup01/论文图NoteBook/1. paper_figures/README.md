# paper_figures：程序介绍用的四组物理图

本目录保存 [presenting Notebook](<../1. CEvNS_pyEFT_paper_figures_presenting.ipynb>) 对应的导出结果，将微观截面、入射相干性、反冲谱和探测器计数放在同一展示序列中。

| 文件前缀 | 生成时使用的实际接口 |
|---|---|
| `fig_3_2a_flavor_dsigma` | `rates.differential` 的味态差分截面 |
| `fig_3_2b_flavor_coherence` | 显式密度矩阵与味空间核收缩，展示相干项 |
| `fig_3_3_csi2021_recoil_components` | SNS 分量与 `rates.counts._rate_per_kg` 的真实反冲谱 |
| `fig_3_4_csi2021_detector_counts` | CsI2021 Slow 探测器计数 |

每组 PNG 用于预览，PDF 用于排版，CSV 保存曲线数值。它们是生成结果，不被实验 loader 读取。

## 管理与新增图

在来源 Notebook 或新的独立生成器中修改展示逻辑，再统一导出同前缀的图与数据，不手改 CSV/PDF 造成不同格式内容不一致。新增物理情景使用新文件前缀并记录参数/单位；替换公式应修改对应 runtime，避免在 Notebook 复制第二套实现。

当前 Notebook 默认 `FIGURE_DIRNAME="paper_figures"`，实际输出是 `ROOT/paper_figures`。要写回本目录需显式设置为 `论文图NoteBook/1. paper_figures`；重跑还需按[上级运行说明](../README.md)处理旧 src 找根和本地安装。这里已有文件不证明本次已完成重算或收敛验证。

---

[上一级](../README.md) · [项目总览](../../README.md)
