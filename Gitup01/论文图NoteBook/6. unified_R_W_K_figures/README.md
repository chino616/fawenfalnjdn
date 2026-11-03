# unified_R_W_K_figures：同一基准上的 R、W、K 与截面

生成入口是 [generate_unified_response_figures.py](../generate_unified_response_figures.py)，也由 v2 Notebook 第 12 节调用。`calculate` 通过 `left_to_ci`、`compute_R_matrices`、`ResponseDB` 和味核/截面接口取得数据；`plot_*` 画图，`export_data` 保存数组、图注、元数据和检查。

| 输出 | 含义 |
|---|---|
| `fig_unified_01_particle_R.*` | 四幅粒子响应面板 |
| `fig_unified_02_nuclear_W.*` | 三幅核响应面板；线型区分核子对 |
| `fig_unified_03_kernel_cross_sections.*` | K 的味分量、按响应通道分解的截面和末态分辨截面 |
| [unified_response_data.npz](unified_response_data.npz) | 完整复数 R/W/K、截面与末态分辨数据；`final_K` 轴为反冲、末味、入味 beta、入味 beta-prime |
| [unified_response_metadata.json](unified_response_metadata.json)、[validation_summary.json](validation_summary.json) | 实际配置、来源哈希、全部通道/核子收缩及末味求和检查 |

现有共同基准为 Cs133、Eν=30 MeV、`C6u1[e,mu]=C6u1[mu,e]*=1e-5 GeV^-2`、sin²θW=0.23873、反冲 0.05–13 keV、160 个点。蓝/橙/绿分别表示 M、Sigma-prime、Delta；总截面仍包含全部已实现通道。末态投影在双线性之前施加，并有独立投影对照；W 沿用存储表归一化，不额外加系数。

## 管理、生成条件与新增结果

脚本当前在 `calculate` 的源码哈希步骤读取旧 `root/src/cevns_pyeft/...`，需先迁移为实际源码位置并核对导入。完成该维护后，可从根目录调用脚本并通过 `--output-dir`、`--n-recoil`、`--coefficient` 显式选择输出和基准；这里不把该命令标为当前已完整复现。

新场景应独立输出，全部图使用同一参数/网格并配套重算 CSV/NPZ/检查。不要直接编辑图中曲线代替重新计算。`export_data` 会覆盖结果目录的 `README.md`；长期管理说明由[上级 README](../README.md)保留，若要自动保留更新后的结果说明，需要同步生成器的 README 模板。

---

[上一级](../README.md) · [项目总览](../../README.md)
