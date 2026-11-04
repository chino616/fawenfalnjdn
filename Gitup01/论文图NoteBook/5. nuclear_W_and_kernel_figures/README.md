# nuclear_W_and_kernel_figures：从核响应 W 到味核与截面

原 v2 Notebook（`4. CEvNS_pyEFT_COHERENT_CsI2021_paper_figures - v2.ipynb`）第 10–11 节生成这里的两组结果；当前目录不含该 Notebook。它们消费实际核响应表和 Li2026 实现，不施加实验源注量、探测器效率或核数。

| 文件前缀 | 计算关系 |
|---|---|
| `fig_csi_05_nuclear_W_Cs133` | `ResponseDB` 读取 Cs133 响应，并按当前表约定求 W |
| `fig_csi_06_amplitude_kernel_cross_section` | 粒子 R 与核 W 收缩，经 `flavor_kernel_onebody_li2026` 和截面接口核对 K 与 dσ/dT |

每组包含 PDF/PNG、CSV、NPZ、JSON 与图注；[validation_summary.json](validation_summary.json) 汇总当时内部数值检查。核表外部来源／归一化仍待核验，不能用绘图闭合检查代替。

## 管理与新增文件

新的核素、通道或截面对照从公共接口取值，保存完整矩阵、基底、动量/能量网格、单位及来源哈希。改变绘图只修改 Notebook/生成器，改变核表或公式需在数据/理论的权威位置处理并重新验证。

该节 `_wk_find_root` 仍查找旧 `src/cevns_pyeft/theory/li2026/amplitude.py`；重跑必须先核对当前 flat 布局和实际包来源。已有输出按元数据解释，新场景另建目录或明确版本前缀，避免混用旧图与新数组。

---

[上一级](../README.md) · [项目总览](../../README.md)
