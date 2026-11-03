# 论文图NoteBook：用运行时接口生成论文图与检查数据

这里保存研究 Notebook、两个独立生成脚本及对应图表。公式和实验计数来自 `cevns_pyeft`；本层负责选取展示参数、作图、导出完整数组和保存数值核对。

| 生成入口 | 对应结果与代码路径 |
|---|---|
| [1. presenting Notebook](<1. CEvNS_pyEFT_paper_figures_presenting.ipynb>) | [1. paper_figures](<1. paper_figures/README.md>)：味截面、相干性、反冲谱、探测器计数 |
| [2. CsI2021 Notebook](<2. CEvNS_pyEFT_COHERENT_CsI2021_paper_figures.ipynb>) | [2. paper_figures_csi2021](<2. paper_figures_csi2021/README.md>)：截面、SNS 反冲分量及实验参考图 |
| [4. v2 Notebook](<4. CEvNS_pyEFT_COHERENT_CsI2021_paper_figures - v2.ipynb>) 第 9 节 | [4. particle_R_figures](<4. particle_R_figures/README.md>)：调用 `left_to_ci`、`compute_R_matrices` |
| 同一 v2 Notebook 第 10–11 节 | [5. nuclear_W_and_kernel_figures](<5. nuclear_W_and_kernel_figures/README.md>)：调用 `ResponseDB`、味核和截面接口 |
| [generate_unified_response_figures.py](generate_unified_response_figures.py)；v2 第 12 节调用 | [6. unified_R_W_K_figures](<6. unified_R_W_K_figures/README.md>)：同一网格上的 R、W、K 和截面 |
| [generate_csi2021_detector_figures.py](generate_csi2021_detector_figures.py)；v2 第 13 节调用 | [7. csi2021_detector_figures](<7. csi2021_detector_figures/README.md>)：公共 Slow 计数、收敛检查、表格与缓存 |

[3. COHERENT_statistics_figure_prompts.md](<3. COHERENT_statistics_figure_prompts.md>) 是绘图任务说明，不是可执行的统计入口。

## 当前代码位置与重跑条件

当前活动包在根 `cevns_pyeft/`，本目录部分旧入口仍写 `src/cevns_pyeft/`：Notebook 的自动找根逻辑和两个脚本的源码哈希采集都保留旧路径。**现有图表可以阅读，但不能据此声明当前脚本可直接完整重跑。** 安装包只解决 import，不解决错误的源码哈希路径。

前两份 Notebook 可显式设置 `PROJECT_ROOT` 绕过旧找根；其 `FIG_DIR = ROOT / FIGURE_DIRNAME` 默认写根目录的 `paper_figures` 或 `paper_figures_csi2021`，不会自动写入当前带编号的结果目录。v2 后续节和脚本还需按实际代码迁移路径后验证。重跑前核对 `cevns_pyeft.__file__`、资源根和输出目录，避免误用其他 checkout。

## 文件管理与新增规则

新的绘图入口放本目录独立 Notebook/`generate_<主题>_figures.py`，显式调用包内公式与预测 API；新结果建立独立子目录。保存 PDF/PNG 供排版，CSV 供曲线核查，NPZ 供完整复数/多轴数组，JSON 记录参数、网格、单位、源码与输入哈希及检查结果。

两个生成脚本支持 `--output-dir`。迁移路径并验证后，使用新的输出目录保存新版本，避免无意覆盖旧图。统一响应脚本的 `export_data` **会重写结果目录 README.md**；长期手工维护说明应放本层或同步到生成模板，不能只编辑下次就会被覆盖的生成文字。探测器脚本还管理 grids 缓存，缓存身份不匹配时需重新计算，不能手改哈希绕过。

本目录的图和数值检查不自动成为 `tests/reference`，展示参数也不自动改变实验 definition。改图样式只改绘图层；改公式回到 `theory/`，改实际实验响应回到 definition/`detectors/` 并执行相应回归。

---

[上一级](../README.md)
