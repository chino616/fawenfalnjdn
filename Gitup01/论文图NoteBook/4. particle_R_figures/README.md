# particle_R_figures：粒子响应 R 的味结构

生成代码位于 [v2 Notebook](<../4. CEvNS_pyEFT_COHERENT_CsI2021_paper_figures - v2.ipynb>) 第 9 节。它调用 `rates.differential._build_total_left_hat`、`theory.li2026.left_to_ci.left_to_ci` 与 `responses.compute_R_matrices`，展示 R 的味分解。

本目录 `fig_csi_04_particle_R_flavor_decomposition` 的 PDF/PNG 是图，CSV 是绘制曲线，NPZ 保存完整复数数组，JSON 保存配置/核查，`_caption.txt` 保存图注。R 在此尚未经过源积分和探测器折叠，不能直接解释为事件数。

## 管理与新增文件

新增响应通道或味分量展示，应从同一代码接口取张量，明确味轴、核子轴和单位，再在该节或新生成器统一保存图、完整数组和核查。公式变更进入 `theory/li2026/responses.py`，不要只修改绘图单元中的某条曲线。

该节当前 `_rfig_find_root` 检查旧 `src/cevns_pyeft/theory/li2026/responses.py`，与当前 flat 包布局不同。重跑前需修正/核对定位逻辑与导入来源；本次 README 仅说明实际路径限制。新基准建议用独立目录，保持已有 JSON/NPZ 与图注的对应关系。

---

[上一级](../README.md) · [项目总览](../../README.md)
