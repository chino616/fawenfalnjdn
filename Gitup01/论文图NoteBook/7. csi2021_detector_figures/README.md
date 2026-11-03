# csi2021_detector_figures：从反冲谱到 CsI2021 事件数

[generate_csi2021_detector_figures.py](../generate_csi2021_detector_figures.py) 的 `compute_grid` 通过 `get_slow_count_function("CsI2021")` 调用公共 Slow 入口，比较 SM、FV NP 和 SM+FV NP。`run_calculation` 管理逐级网格、缓存与收敛，`export` 导出图表和完整结果。

| 内容 | 阅读用途 |
|---|---|
| [NUMERICAL_REPORT.md](NUMERICAL_REPORT.md) | 当前保存的事件数与收敛范围说明，先读它解释各输出 |
| `fig_csi_07_detector_level_FV.*`、`fig_csi_07_supplement_true_recoil.*` | PE 观测谱与真反冲补充图 |
| `table_csi2021_event_count_comparison.*` | 同一事件数表的 CSV/Markdown/TeX/图片/PDF 版本 |
| [source_target_bin_predictions.csv](source_target_bin_predictions.csv)、[target_total_comparison.csv](target_total_comparison.csv) | 按源/核素/箱及材料总数核对 |
| [csi2021_detector_complete.npz](csi2021_detector_complete.npz)、[metadata.json](metadata.json) | 完整数组、配置和源码/核表身份 |
| [grids/](grids/)、[convergence_report.json](convergence_report.json)、[exact_cache_validation.json](exact_cache_validation.json) | 每级计算、网格比较和 exact memoization 对照 |

现有报告选用 `(128,192,96,0.75)` 网格；≥1 事件分量的相对阈值 1%，较小分量绝对阈值 0.02 事件，总数阈值 0.2%。这是数值网格检查。基准系数为 1e-5 GeV⁻²，sin²θW=0.23873；没有进行 likelihood 拟合。

## 归一化与文件管理

旧 raw target 数组按“整台质量全为某核素且未施加源接受率”计算。物理 Cs/I 贡献还需乘 133/260、127/260 和分量接受率；POT 已在注量中，质量只施加一次。完整结果保留接受率前后的反冲谱，补充图使用前者。mub 仍遵循共享 nu/antinu 核约定。

脚本的 `source_hashes` 当前读取旧 `src/cevns_pyeft/`，重跑前必须核对并迁移该路径；安装包本身不能修复这个文件定位。路径问题处理后，用 `--output-dir` 建立新结果目录，`--max-levels` 控制最多网格级数。`grids/<网格名>/prediction.npz` 和 metadata 由程序管理，身份不匹配时应重新计算，不能手改哈希或数组使旧缓存通过。

新增情景在生成器中定义参数并统一导出配套数组、表格、图和验证；新的物理公式仍修改 runtime。结果文件不是 `data/` 输入或 `tests/reference/` 的自动替代物。

---

[上一级](../README.md) · [项目总览](../../README.md)
