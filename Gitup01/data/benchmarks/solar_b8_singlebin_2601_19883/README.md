# Solar B8：独立单 bin 输入（2601.19883v2）

主线入口：[修订 onboarding](../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md)。

[analysis.input.json](analysis.input.json)是本分析专属 JSON 格式（不是三文件 Experiment Input Package），拥有全部物理输入、标准引文、精确页/图/式、原始PDF向量和哈希；Runtime仅显式读取本目录及用户选定的共享核表。

| 文件 | 含义与来源 |
|---|---|
| [b8_source.txt](b8_source.txt) | R6 官网829点前两列；MeV, MeV⁻¹；不含总通量 |
| [xe_isotopes.txt](xe_isotopes.txt) | R7 NIST九行 A/原子质量/数丰度；不重归一 |
| [pandax_paired_total.txt](pandax_paired_total.txt) | R2 v3 p3 Fig.1黑实线；T,总效率；1.1–3 keVnr |
| [pandax_us2_total.txt](pandax_us2_total.txt) | R2 v3 p3 Fig.1黑虚线；T,总效率；0.3–3；已含ROI |
| [xenonnt_combined.txt](xenonnt_combined.txt) | R3 v2 p4 Fig.1黑线；T,总接受度,可见标记；末端约2.77 keVnr，未延伸到3 |
| [fitted_yields.json](fitted_yields.json) | R2/R3拟合信号、R4 Table II取整误差；R1 Eq.88三个独立12% pull；不含逐箱D/B |

准备：[prepare_solar_b8_singlebin.py](../../../tools/prepare_solar_b8_singlebin.py)，仅创建新目录；计算：[solar_singlebin.py](../../../cevns_pyeft/experiments/solar_singlebin.py)。数值文件不从多bin NPZ、Qy或响应基底读入，后续修改须独立更新本参数卡和新结果。

<!-- latest-analyses:start -->

## 当前最新分析与处理方式

[五条实验最新入口](<../../../docs/experiments/LATEST_EXPERIMENTS.md>)

| 分析 | 方法/版本 | 输入 | 结果与核对范围 |
|---|---|---|---|
| 太阳⁸B：单bin（三样本） | [v3.2.1 / 20261111_response_run2；处理方式](<../../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/METHODS.md>) | [当前输入](<analysis.input.json>) | [SM结果](<../../../outputs/solar_b8_singlebin/20261111_response_run2/README.md>) |

来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。

<!-- latest-analyses:end -->
