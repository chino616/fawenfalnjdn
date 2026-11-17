# 论文图NoteBook：用运行时接口生成论文图与检查数据

[论文图公共主题 v4.0](../plotting/paper_theme/README.md) · [主题规范](../plotting/paper_theme/PAPER_THEME_GUIDE.md) · [唯一参数](../plotting/paper_theme/PAPER_THEME.json) · [绘图文件架构](../plotting/README.md)：以后新图统一读取公共主题。原本层的 v1 规范和 JSON 已移除；编号图集中的旧样式仅用于历史图复现。具体生成器和结果仍放本目录。

[CsI2021 味分量重画（2026-11-15）](<13. CsI2021_Flavor_Components/README.md>)：按通用论文主题输出 PE／时间双面板，补上包含平滑 SSB 时间相关性的 C＋AC 计数统计误差条；保留原中心值与分箱，完整系统误差未纳入。[生成器](generate_csi2021_flavor_components.py) · [PDF](<13. CsI2021_Flavor_Components/Figure_CsI2021_Flavor_Components.pdf>)。

[CsI2021 Comparator修订（2026-11-15）](<8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.md>)：补论文SM总率341±11理论±42实验，原句定位到第4页右栏Results；[修订后的数值表](<8. SM_experiment_benchmarks/Table_SM_Numerical_Summary.pdf>)及合集入口见SM图集。

[截断能标独立图集（2026-11-14）](<12. Cutoff_Scale_Benchmarks/README.md>)：原两套各5图保留；本轮按9. SM_uniform_style的蓝/橙/绿视觉角色重画10图，新增9张逐算符论文比较与三组联合图、3套19页合集。太阳传播条件、LNV味和dim-8正定性限制明确分开。

[二维SM/NSI benchmark图集（2026-11-13）](<11. TwoD_Chi2_Benchmarks/README.md>)：41个逐实验参数面、12张论文汇总图、完整域/显示域比较、原文轮廓、参考文献、图注与全部数据。沿用180 mm/STIX统一版式。

[一维SM/NSI χ²图集（2026-11-13）](<10. OneD_Chi2_Benchmarks/README.md>)：七张统一180 mm版式图、合集、参考文献、英文图注及66条逐点χ²；[完整计算路线](../docs/experiments/COMPUTATION_ROUTES_20261113.md)与[全部数值区间](../outputs/one_d_benchmark_20261113_run1/RESULTS.md)。论文区间与新算曲线明确区分。

这里保存研究 Notebook、独立生成脚本及对应图表。公式和实验计数来自 `cevns_pyeft`；本层负责选取展示参数、作图、导出完整数组和保存数值核对。

| 生成入口 | 对应结果与代码路径 |
|---|---|
| 原 1. presenting Notebook（文件当前缺失） | [1. paper_figures](<1. paper_figures/README.md>)：味截面、相干性、反冲谱、探测器计数 |
| 原 2. CsI2021 Notebook（文件当前缺失） | [2. paper_figures_csi2021](<2. paper_figures_csi2021/README.md>)：截面、SNS 反冲分量及实验参考图 |
| 原 4. v2 Notebook（文件当前缺失） 第 9 节 | [4. particle_R_figures](<4. particle_R_figures/README.md>)：调用 `left_to_ci`、`compute_R_matrices` |
| 同一 v2 Notebook 第 10–11 节 | [5. nuclear_W_and_kernel_figures](<5. nuclear_W_and_kernel_figures/README.md>)：调用 `ResponseDB`、味核和截面接口 |
| [generate_unified_response_figures.py](generate_unified_response_figures.py)；v2 第 12 节调用 | [6. unified_R_W_K_figures](<6. unified_R_W_K_figures/README.md>)：同一网格上的 R、W、K 和截面 |
| [generate_csi2021_detector_figures.py](generate_csi2021_detector_figures.py)；v2 第 13 节调用 | [7. csi2021_detector_figures](<7. csi2021_detector_figures/README.md>)：公共 Slow 计数、收敛检查、表格与缓存 |

[历史统一样式图集（2026-11-13）](<9. SM_uniform_style/README.md>)：当时的 180 mm/STIX 图件、数值与样式快照保留。[历史规范](<9. SM_uniform_style/STYLE_GUIDE.md>) 和[历史生成器](generate_uniform_sm_figures.py)仅供复现该版本；后续新图或样式更新采用公共 v4。

[最新标准模型论文图集（2026-11-13）](<8. SM_experiment_benchmarks/README.md>)：CONUS+、CsI-time、CsI2017、Ar2020与太阳单bin/多bin，含矢量PDF、SVG、PNG、逐箱表、来源和英文图注。生成器为[generate_sm_experiment_figures.py](generate_sm_experiment_figures.py)，从已有结果作图，不修改Runtime或重跑物理拟合。

[3. COHERENT_statistics_figure_prompts.md](<3. COHERENT_statistics_figure_prompts.md>) 是绘图任务说明，不是可执行的统计入口。

## 当前代码位置与重跑条件

当前活动包在根 `cevns_pyeft/`，本目录部分旧入口仍写 `src/cevns_pyeft/`：Notebook 的自动找根逻辑和两个脚本的源码哈希采集都保留旧路径。**现有图表可以阅读，但不能据此声明当前脚本可直接完整重跑。** 安装包只解决 import，不解决错误的源码哈希路径。

前两份 Notebook 可显式设置 `PROJECT_ROOT` 绕过旧找根；其 `FIG_DIR = ROOT / FIGURE_DIRNAME` 默认写根目录的 `paper_figures` 或 `paper_figures_csi2021`，不会自动写入当前带编号的结果目录。v2 后续节和脚本还需按实际代码迁移路径后验证。重跑前核对 `cevns_pyeft.__file__`、资源根和输出目录，避免误用其他 checkout。

## 文件管理与新增规则

新的绘图入口放本目录独立 Notebook/`generate_<主题>_figures.py`，显式调用包内公式与预测 API；新结果建立独立子目录。保存 PDF/PNG 供排版，CSV 供曲线核查，NPZ 供完整复数/多轴数组，JSON 记录参数、网格、单位、源码与输入哈希及检查结果。

公共字体、色板、坐标轴、系列编码与导出规则在 `../plotting/paper_theme/` 维护。后续具体脚本读取该目录 JSON，不能把编号图集中的旧 `STYLE.json` 当作全局默认。`generate_csi2021_flavor_components.py` 已默认采用公共 v4 填充色，输出到新的 `CsI2021_Flavor_Components_v4`；13号目录仍是历史图。

两个生成脚本支持 `--output-dir`。迁移路径并验证后，使用新的输出目录保存新版本，避免无意覆盖旧图。统一响应脚本的 `export_data` **会重写结果目录 README.md**；长期手工维护说明应放本层或同步到生成模板，不能只编辑下次就会被覆盖的生成文字。探测器脚本还管理 grids 缓存，缓存身份不匹配时需重新计算，不能手改哈希绕过。

本目录的图和数值检查不自动成为 `tests/reference`，展示参数也不自动改变实验 definition。改图样式只改绘图层；改公式回到 `theory/`，改实际实验响应回到 definition/`detectors/` 并执行相应回归。

---

[上一级](../README.md)
