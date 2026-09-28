# 2211.11905v2 Fig. 3–7 复现与对照绘图包

**状态：绘图、文献原图提取与输入校验工具；不是已完成的论文数值复现。**

**完整物理/统计复现对比标准**：请先阅读同目录的 [`DETAILED_PHYSICS_STATISTICS_COMPARISON_CN.md`](DETAILED_PHYSICS_STATISTICS_COMPARISON_CN.md)。包括论文公式、程序对接证据、每图假设、分阶段验证与差异量化。 目前缺少用户电脑本地 `2211.11905v2.pdf` 和指定 Github 分支的可运行源码/实验数据，因此不能生产真实的复现数据。绘图器刻意不会用模拟数据替代实际结果。

## 输入材料

请从指定的本地目录提供 (1) 原版 `2211.11905v2.pdf`，(2) 指定分支 `Gitup01/` 的完整 ZIP（包含 `src/`, `data/`, `tests/`, 统计入口与所有需要的数据文件），(3) 若已存在精细扫描的真实 raw-profiled chi2 矩阵，可以单独提供其 NPZ/CSV 及数据定义。

由于公开 README 是分拆包说明，不能仅凭 README 推断分支目前 statistical API 的完整名称；必须检查完整代码后才适配实际数值入口。

## 论文 Fig. 3–7 的范围

| 图 | 内容 | 数据 | PDF 页码（1-based） |
|---|---|---|---:|
| 3 | (eps_ee_dV, eps_ee_uV); (eps_mumu_dV, eps_mumu_uV) | CsI / LAr / joint | 19 |
| 4 | (eps_ee_uV, eps_mumu_uV); (eps_ee_dV, eps_mumu_dV) | 同上 | 20 |
| 5 | (eps_ee_dV, eps_etau_dV); (eps_mumu_dV, eps_mutau_dV) | 同上 | 21 |
| 6 | (eps_ee_dV, eps_emu_dV); (eps_mumu_dV, eps_emu_dV) | 同上 | 22 |
| 7 | NGI Cq_S, Cq_V, Cq_T：上排一维，下排三种二维平面 | 同上 | 23 |

Fig. 3–6 与 Fig. 7 下排：90% CL (2 d.o.f.), Δχ² = 4.605170185988092。Fig. 7 上排必须用一维 profile，不应画成二维的截面切片。每一二维平面只开对应两个耦合，其余归零；NGI 的 scalar/vector/tensor 应核查 Eq. (7)–(11)，不得把 Fig. 7 当成 NSI Wilson 矩阵的另一种横坐标。

**论文数据组合为 CsI2021 + LAr2020**，不将 CsI2017 再次相加。真实联合网格必须从原始 chi2 求和后取全局最小值，而不是逐个 Δchi2 简单相加。计算时建议保留 profile 后 raw chi2 与 nuisance 最优点；若 CsI、LAr 各自 nuisance 相互独立，可逐点加和 profiled raw chi2。

论文 CsI 的 Poisson likelihood（9 PE × 11 timing bins）见 §3.3 Eq. (3.9)，本次 CEνNS-only 的预测项见 Eq. (3.11)；LAr 使用 12 energy × 10 timing bins，其 Gaussian likelihood/shape nuisance 见 Eq. (3.12)–(3.13)。上述编号按可访问 JHEP 正文，执行时应以提供的 v2 PDF 再核实。不同似然实现必须明确标注为 approximate comparison，不能叫 exact reproduction。NSI/NGI 重现图使用 CsI 中 CEνNS only，不附加 ES signal。参考 https://arxiv.org/pdf/2211.11905v2 。

## 运行环境

```powershell
python -m pip install numpy matplotlib pymupdf pillow
python plot_benchmark.py --paper-pdf 'F:\Work\2026-07-15 CEvNSpyEFT-Local\260820Gitup1-Flavor\git-worktree-f0\Gitup01\Benchmark\260928 COHENRENT-NSI\2211.11905v2.pdf' --paper-only --out output
```

上面的命令将从 `manifest.json` 所列候选页开始搜索图注、必要时扫描全文寻找对应图号并提取 `Fig03_original.png` 等；**仍须人工核对 crop 是否只包含完整图像，不应自动把整页文字视为图的一部分**。**只有原图，尚无复现图。**

## 输入数值协议

必须在实际分支跑出以下 14 个 NPZ 才能复现（8 个 NSI + 6 个 NGI）：

```text
fig3_top.npz                 fig3_bottom.npz
fig4_top.npz                 fig4_bottom.npz
fig5_top.npz                 fig5_bottom.npz
fig6_top.npz                 fig6_bottom.npz
fig7_profile_scalar.npz      fig7_profile_vector.npz     fig7_profile_tensor.npz
fig7_plane_scalar_tensor.npz fig7_plane_vector_scalar.npz fig7_plane_vector_tensor.npz
```

二维 NPZ 必须包含 `x`、`y`（严格升序一维轴）及 `chi2_csi`、`chi2_lar`（按 `[len(y),len(x)]` 排列，且为每格 nuisance profiling 后的 **原始** chi2）。可额外提供 `chi2_joint`；缺省则自动逐格加和两个 raw chi2。一维 NPZ 必须有 `x`、`chi2_csi`、`chi2_lar`；也可额外给 `chi2_joint`。推荐保留 raw profiled chi2 以追溯各实验 absolute chi2 与最优值。若两实验使用同一参数网格，分别减去自己的常数最小值以后，在**逐点求和之后再次减去联合最小值**，数学上仍能得到相同的 joint Delta chi2；不能把未再归零的直接和称作 joint Delta chi2。

实际分支适配后，在本地运行：

```powershell
python plot_benchmark.py --paper-pdf 'F:\...\2211.11905v2.pdf' --grids 'F:\...\real_benchmark_npz' --out 'F:\...\benchmark_comparison'
```

每张图分别输出 `FigXX_original.png`、`FigXX_reproduction.png` / `.pdf`、`FigXX_comparison.png`，另有合并 `Fig03_to_Fig07_comparison.pdf` 与 SHA256 provenance.json。对照是并排视觉检查，不代表进行了原论文曲线数据数字化；如需量化边界偏差，必须另外建立对照曲线坐标数据和同轴误差度量。

## 数值验收顺序

1. 检查系数定义和符号、SM 恢复、off-diagonal ± 对称性与 q=u/d 的核电荷加权。
2. 检查 CsI 与 Ar 的 SM 各 bin 数、源味拆分、时间谱、效率、形状因子。
3. 检查各自 nuisance profiling，保存逐点 raw chi2；明确区分 global minimum 与固定二维切片 minimum。
4. 检查 Fig. 3 中两支弱电荷简并结构、Fig. 4 中 e/μ 同时变化、Fig. 5/6 flavor-changing 符号对称。
5. 单独实现或核对 Fig. 7 的 NGI scalar/tensor 正确核截面及干涉项。Fig. 7 中 Cq_X = g_νX g_qX，并且该文假设 Cu_X=Cd_X=Cq_X。
6. 标记任何触及扫描框的 contour，扩大参数域；不得把截断边界写成最终约束。
7. 将运行 git commit、PDF SHA256、数据版本、binning、EFT convention、nuisance definition、optimizer、阈值、seed 等写入 provenance。
