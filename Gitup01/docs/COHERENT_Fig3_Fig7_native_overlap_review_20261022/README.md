# 截图对应的 COHERENT Fig.3–Fig.7 原始 native overlap 结果整理

整理日期：2026-10-22。本报告以用户提供的 Fig.4 截图为定位依据，整理 `native_overlap_comparison` 中保留 CsI2021+Ar2020 联合轮廓的原始结果。它与此前汇总的 `4cbc4e508f5a383b` 高分辨率 CsI 单实验图组是不同运行。

## 1. 截图准确对应哪个文件

- [与截图对应的 Fig.4 原始对照 PNG](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/comparison/Fig04_native_approx_comparison.png>)：左侧为论文 PDF 页面，右侧为 native 计算。
- [Fig.4 右侧四面板单独 PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/reproduced/Fig04_native_approx_reproduction.pdf>)：两种单实验的叠加图，以及联合图。
- [原版 Fig.3–Fig.7 汇总 PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/output/pdf/benchmark_2211_11905_native_overlap_comparison.pdf>)。
- [原结果说明](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/NATIVE_OVERLAP_COMPARISON_REPORT.md>)、[生成时 provenance](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/provenance_native_overlap.json>)、[面板状态表](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/panel_status.csv>)。

图内标题 `Native approximate reproduction / Not paper-matched` 是该结果原本的声明。右侧采用原工程的核 Response、Fast 事件预测和 legacy 能谱统计；没有为了生成这张图读取 ROOT 时间分箱。左侧是论文 arXiv:2211.11905v2 第 20 页的图像渲染，不是程序产生的曲线。

![用户截图对应的原 Fig.4 对照图](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/comparison/Fig04_native_approx_comparison.png>)

## 2. 一共完成了哪些图

所有 Fig.3–6 都只打开图示的两个实数矢量 NSI 参数，其他 NP 参数固定为零。非对角项填入其厄米共轭。每排左面板叠加 CsI（紫红）与 Ar（橙黄）的单实验区域，右面板显示 CsI+Ar 的蓝色联合区域。统一使用二维 90% 渐近阈值 `Δχ²=4.605170185988092`。

| 图 | 上排 (x,y) | 下排 (x,y) | 完成情况 |
|---|---|---|---|
| Fig.3 | (ε_ee^dV, ε_ee^uV) | (ε_μμ^dV, ε_μμ^uV) | 两个单实验与联合均有真实 χ² 网格 |
| Fig.4 | (ε_ee^uV, ε_μμ^uV) | (ε_ee^dV, ε_μμ^dV) | 即用户截图；两个单实验与联合均已计算 |
| Fig.5 | (ε_ee^dV, ε_eτ^dV) | (ε_μμ^dV, ε_μτ^dV) | 对角与 tau 味改变项的补偿 |
| Fig.6 | (ε_ee^dV, ε_eμ^dV) | (ε_μμ^dV, ε_eμ^dV) | 对角与 e–mu 味改变项的补偿 |
| Fig.7 | scalar/vector/tensor NGI 一维及二维基准 | — | 本次比较未计算，标记 NGI_MISSING / NOT_COMPARABLE |

共 8 个二维参数平面，每个平面保存 `x,y,chi2_csi,chi2_lar,chi2_joint`。矩阵方向为 `[y_index,x_index]`，每张表面为 101×101。共有 24 张 χ² 表面；它们是程序计算值，不是从左侧论文图像反推得到的。

| 图 | x 扫描范围 | y 扫描范围 |
|---|---|---|
| Fig.3 两排 | [-1,1] | [-1,1] |
| Fig.4 两排 | [-0.4,0.8] | [-0.3,0.6] |
| Fig.5 两排 | [-0.4,0.6] | [-0.6,0.6] |
| Fig.6 两排 | [-0.4,0.6] | [-0.3,0.3] |

定义来自[manifest.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/benchmark_2211_11905_fig3_fig7/manifest.json>)；该文件是比较配置，不能把其中的实施要求当作全部已经完成的验证记录。

## 3. “根据原程序处理”具体采用了什么

### 3.1 物理和事件预测

程序使用 Flavor 版 Li2026 核响应与矢量 NSI 参数接口：

\[
\hat C_{1q}^{(6),\mathrm{NP}}=-\sqrt2 G_F\epsilon^{qV},\qquad q=u,d.
\]

`vector_nsi_to_np_wilson` 返回 NP-only 的两个 3×3 矩阵；预测默认加入 SM。核响应经 SNS 三种入射源卷积与探测器折叠，随后计算分箱事件数。不同入射源的事件贡献求和，不能把 νe 与 νμ 入射振幅相加。

| 数据集 | 本图实际使用的核 | 积分设置 |
|---|---|---|
| CsI2021 | [tests/reference_CsI2021/fast_kernel.npz](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/tests/reference_CsI2021/fast_kernel.npz>) | n_ER=21、n_Enu=120、n_PE_sub=8、pe_step=3 |
| Ar2020 | [Ar Fast 核](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/flavor_benchmark/COHERENT_highres_all_grid101/ar2020_fast_kernel_ne21_nenu120_nobs8/ar2020_fast_kernel.npz>) | n_ER=21、n_Enu=120、n_obs_sub=8 |

因此，参数平面上的 101×101 采样不意味着事件积分也达到高精度；Fast 的系数重建与积分网格误差是两个问题。该截图并未使用后来 `(81,240,64,pe_step=.75)` 的更细 CsI 核。

### 3.2 CsI2021：9 箱残差能谱 Gaussian

输入数据、背景和对称误差的单位都是 counts/PE。原始预测 events/bin 先除以实际 PE 箱宽，χ² 为

\[
\chi^2_{\rm CsI}(\theta,\alpha,\beta)=
\sum_i\frac{[D_i-(1+\alpha)S_i(\theta)-(1+\beta)B_i]^2}{\sigma_i^2}
+(\alpha/0.125)^2+(\beta/0.35)^2.
\]

调用 `chi2_csi2021`，每个物理点解析求解两个 nuisance；本调用不对 α、β 另加截断边界。它不是 9 PE×11 时间箱的原始计数 Poisson 模型。相关[数据](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/datasets.py>)、[likelihood](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/likelihoods.py>)和[profile](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/profiling.py>)均保留。

### 3.3 Ar2020：12 箱非对称误差 Gaussian

Ar 使用 legacy 的观测、背景、上下误差数组。信号和背景归一化 σ 分别为 0.12、0.146；调用 `chi2_ar2020_irls`。当预测高于观测时使用上侧误差，否则使用下侧误差，迭代更新误差侧和两个归一化参数。

源码实际设置最多 8 次 IRLS，归一化参数截断到 [-1,1]；没有采用另一个 `chi2_ar2020_bounded` 入口。原 NPZ 只保存 χ² 表面，没有保存每个点的完整 nuisance、误差侧、迭代收敛诊断或失败掩码。因此不能只由有限 χ² 值推断整张表面所有 nuisance 优化均已严格验证。

### 3.4 联合统计

两实验在同一 ε 参数点各自处理 nuisance，然后相加 raw χ²：

\[
\widetilde\chi^2_{\rm joint}(\theta)
=\widetilde\chi^2_{\rm CsI}(\theta)+\widetilde\chi^2_{\rm Ar}(\theta),
\quad
\Delta\chi^2_{\rm joint}
=\widetilde\chi^2_{\rm joint}-\min_{\theta\in\Omega}\widetilde\chi^2_{\rm joint}.
\]

本版只联合 CsI2021 与 Ar2020，没有加入 CsI2017。它假定两实验 nuisance 独立，没有引入跨实验共享通量等相关 nuisance。每个实验、每张联合平面都减去自身扫描域上的网格最低值；本版没有进一步连续细化全局最低点。

本次已核对 8 个 NPZ：`chi2_joint` 与 `chi2_csi+chi2_lar` 逐元素一致。数学上，若先将两实验各自的 Δχ² 相加，再对总和重新归零，也会得到等价的联合 Δχ²；直接相加后不重新归零则一般不等价。

## 4. 截图 Fig.4 应如何解读

上排同时改变 u 夸克的电子味、缪子味对角耦合；下排对 d 夸克作相同分析。它是 flavor-preserving 的味依赖分析：两个对角元不相等不代表散射把 νe 改变成 νμ。真正的味改变参数出现在 Fig.5、6。

右侧四个 native 面板表示：

1. 左上紫红与橙黄环带分别是 CsI2021、Ar2020 对 uV 参数的 90% 区域。
2. 右上蓝环是二者 raw χ² 相加再减联合最低值所得结果，不是把两个彩色区域的几何交集重新涂色。
3. 下排给出 dV 的对应结果，核内夸克组合不同，所以位置和尺度不同。
4. 环带中心附近可以出现信号抑制；电子味和缪子味的贡献还可互相补偿，导致同一事件谱对应一族耦合组合。时间积分能谱保留了较强退化。

下面是从截图所属的 NPZ 直接读取的网格最低值。坐标按本排 (x,y) 列出；不同实验的最低点不同，所以联合最低 χ² 不等于两个单实验最低 χ² 简单相加。

| 图/排 | 数据集 | 网格最优 (x,y) | 最低 χ² | 允许域触框 |
|---|---|---|---:|---|
| Fig.4 top | CsI2021 | (0.152, -0.030) | 3.480365 | 否 |
| Fig.4 top | Ar2020 | (0.560, 0.186) | 8.214251 | 否 |
| Fig.4 top | CsI+Ar | (0.272, 0.420) | 12.775690 | 否 |
| Fig.4 bottom | CsI2021 | (0.164, -0.030) | 3.464126 | 否 |
| Fig.4 bottom | Ar2020 | (0.524, 0.168) | 8.234186 | 否 |
| Fig.4 bottom | CsI+Ar | (0.236, 0.384) | 12.915410 | 否 |

这些是给定扫描框内的离散网格结果，不是连续最优值，也不代表唯一最优解。特别是环状退化带上，相近的 χ² 可以出现在不同位置。

本次用原核与原统计函数重新计算 SM，得到：

| 数据集 | 名义信号事件数 | SM χ² | α | β |
|---|---:|---:|---:|---:|
| CsI2021 | 332.933835 | 3.887878 | -0.037280 | -0.024457 |
| Ar2020 | 139.107912 | 9.426911 | 0.026306 | -0.117848 |
| CsI+Ar | — | 13.314789 | 各自独立 | 各自独立 |

CsI 的 SM χ²=3.887878 属于截图使用的粗参考核；上一份高分辨率单实验整理中的 4.230765 属于另一套核，不能替换这里的共同最低值或用来定义本图 Δχ²。

### 与论文左图的差别

截图左侧的论文 CsI 区域、以及 CsI+LAr 联合区域呈上下分离的弯带；右侧 native 的对应区域仍为连续环带。这个差别确实存在，不能把右图称为论文轮廓已复现成功。

主要已知模型差异包括：CsI 使用时间积分 Gaussian 残差而非能量—时间 Poisson；Ar 未采用论文完整时间—能量模板和形状 nuisance；原生核响应、源谱及探测器数值设置也未逐项锁定为论文方案。时间结构能区分 prompt νμ 与 delayed 成分，因而与 Fig.4 中两种入射味的补偿直接相关；但在没有保持其他条件完全相同的对照前，不能把全部轮廓差异只归因于时间信息。

左图页面正文的一维参数区间和右图的二维 90% 区域具有不同统计条件，不能直接拿其端点判断这张二维图的宽度。原图目前是整页渲染，未提供经过人工审计的精确裁剪或论文轮廓数字化点，所以本次不报告像素差、面积重合率或论文 raw χ² 数值偏差。

## 5. 其余各图说了什么

### Fig.3：同一味的 u/d 退化

上排只改电子味，下排只改缪子味。核的矢量 NSI 大致受 `(2Z+N)ε_u+(Z+2N)ε_d` 控制，因此两个夸克耦合可以补偿。Cs、I 和 Ar 的权重不同，联合可改变允许带；但这个有限扫描框仍需检查截断。Fig.3 某些最低点在边缘，本次表格明确标记允许域触框，不将它当作完整闭合限制。

Fig.3 的两个参数与早期 uV/dV 图相同，但本图横轴为 dV、纵轴为 uV；历史脚本读取旧表面时做了转置，不能忽略这个轴顺序。

### Fig.5：对角参数与 eτ / μτ 味改变参数

SNS 没有入射 tau 味，也仍可经 νe→ντ 或 νμ→ντ 贡献不可分辨末态散射。非对角平方项能补偿对角项对 SM 的破坏性干涉。在本图纯味入射、单个实数非对角参数的设置下，非对角参数变号应保持率和 χ² 不变。

### Fig.6：对角参数与 eμ 味改变参数

eμ 同时作用于电子味与缪子味源的散射贡献，和 Fig.5 只涉及某一种入射味的 tau-changing 参数不同。此处的形状来自不同入射态的事件率求和与末态求和，不能解释为 νe、νμ 两个入射振幅的直接干涉。

### Fig.7：本比较没有完成的 NGI 基准

保留的 `Fig07_NGI_not_comparable.png` 是状态说明，没有 scalar/tensor 的新 χ² 数据。本项目存在其他 EFT 算符的实现，并不自动意味着本次比较已完成论文特定 NGI 的归一化、响应和干涉验证。

## 6. 全部 24 张表面的网格结果

以下均从原保存表面读取；本次没有重扫或移动轮廓。允许域触框表示边界至少有一个点满足该表面自己的 90% 阈值。

| 图/排 | 数据集 | 网格最优 (x,y) | 最低 χ² | 允许域触框 |
|---|---|---|---:|---|
| Fig.3 top | CsI2021 | (-0.880, 1.000) | 3.548789 | 是 |
| Fig.3 top | Ar2020 | (-0.360, 0.840) | 8.550754 | 是 |
| Fig.3 top | CsI+Ar | (-0.560, 1.000) | 12.810344 | 是 |
| Fig.3 bottom | CsI2021 | (-0.840, 0.940) | 3.490231 | 是 |
| Fig.3 bottom | Ar2020 | (-0.500, 0.940) | 8.745519 | 是 |
| Fig.3 bottom | CsI+Ar | (-0.360, 0.780) | 12.922195 | 是 |
| Fig.4 top | CsI2021 | (0.152, -0.030) | 3.480365 | 否 |
| Fig.4 top | Ar2020 | (0.560, 0.186) | 8.214251 | 否 |
| Fig.4 top | CsI+Ar | (0.272, 0.420) | 12.775690 | 否 |
| Fig.4 bottom | CsI2021 | (0.164, -0.030) | 3.464126 | 否 |
| Fig.4 bottom | Ar2020 | (0.524, 0.168) | 8.234186 | 否 |
| Fig.4 bottom | CsI+Ar | (0.236, 0.384) | 12.915410 | 否 |
| Fig.5 top | CsI2021 | (0.030, -0.036) | 3.648024 | 否 |
| Fig.5 top | Ar2020 | (0.430, 0.000) | 8.574677 | 否 |
| Fig.5 top | CsI+Ar | (0.350, 0.000) | 13.155286 | 否 |
| Fig.5 bottom | CsI2021 | (0.010, 0.000) | 3.724120 | 否 |
| Fig.5 bottom | Ar2020 | (0.380, 0.024) | 8.784636 | 否 |
| Fig.5 bottom | CsI+Ar | (0.350, 0.000) | 13.087996 | 否 |
| Fig.6 top | CsI2021 | (0.140, 0.084) | 3.534141 | 否 |
| Fig.6 top | Ar2020 | (0.430, 0.000) | 8.574677 | 否 |
| Fig.6 top | CsI+Ar | (0.280, -0.078) | 13.144052 | 否 |
| Fig.6 bottom | CsI2021 | (0.010, 0.000) | 3.724120 | 否 |
| Fig.6 bottom | Ar2020 | (0.180, 0.174) | 8.604658 | 否 |
| Fig.6 bottom | CsI+Ar | (0.350, 0.000) | 13.087996 | 否 |

精确机器可读值位于 [grid_minima_24.csv](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_Fig3_Fig7_native_overlap_review_20261022/grid_minima_24.csv>)；[panel_definitions_8.csv](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_Fig3_Fig7_native_overlap_review_20261022/panel_definitions_8.csv>)记录范围、参数和阈值；[SM_checks.csv](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_Fig3_Fig7_native_overlap_review_20261022/SM_checks.csv>)记录 SM 数值及 nuisance。

## 7. 图、数据与代码位置

| 图 | 论文/native 对照 PNG | native 单独 PDF | 原始表面 |
|---|---|---|---|
| Fig.3 | [对照](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/comparison/Fig03_native_approx_comparison.png>) | [PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/reproduced/Fig03_native_approx_reproduction.pdf>) | [上排](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/raw_native_approx/fig3_top.npz>)、[下排](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/raw_native_approx/fig3_bottom.npz>) |
| Fig.4 | [截图原文件](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/comparison/Fig04_native_approx_comparison.png>) | [PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/reproduced/Fig04_native_approx_reproduction.pdf>) | [上排](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/raw_native_approx/fig4_top.npz>)、[下排](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/raw_native_approx/fig4_bottom.npz>) |
| Fig.5 | [对照](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/comparison/Fig05_native_approx_comparison.png>) | [PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/reproduced/Fig05_native_approx_reproduction.pdf>) | [上排](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/raw_native_approx/fig5_top.npz>)、[下排](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/raw_native_approx/fig5_bottom.npz>) |
| Fig.6 | [对照](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/comparison/Fig06_native_approx_comparison.png>) | [PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/reproduced/Fig06_native_approx_reproduction.pdf>) | [上排](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/raw_native_approx/fig6_top.npz>)、[下排](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/raw_native_approx/fig6_bottom.npz>) |
| Fig.7 | [未完成状态图](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_overlap_comparison/figures/comparison/Fig07_NGI_not_comparable.png>) | — | 无本次 NGI 扫描数据 |

当时的生成脚本曾被修改过。Git 提交 `16dd773` 中的 `Gitup01/tools/statistics/run_2211_11905_native_overlap_comparison.py` 保留了截图版本，包含 `chi2_joint=chi2_csi+chi2_lar` 及左侧叠加/右侧联合布局。本次只读出 Git blob，存为[原版脚本文本](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_Fig3_Fig7_native_overlap_review_20261022/source_at_16dd773.py.txt>)，没有切换分支或恢复旧代码。

当前同名[生成脚本](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/tools/statistics/run_2211_11905_native_overlap_comparison.py>)已经改为输出 `native_separate_experiment_comparison`，所以直接运行当前脚本不会得到截图的原联合布局。生成时 provenance 记录的基础提交为 `880dabab9a54911caa247c7dda12781e8c970123`；不能把该值误认为脚本修改后已提交的完整代码快照。

## 8. 与后来的 separate 版本、此前高分辨率图的区别

| 版本 | 目录/标识 | 内容 |
|---|---|---|
| 用户截图的原版 | native_overlap_comparison | CsI/Ar 叠加，另画 joint；8 个 NPZ 含 chi2_joint |
| 后来修改的展示版 | native_separate_experiment_comparison | 两列分别 CsI-only、Ar-only；没有 joint 数组 |
| 前一轮回复重点整理的主图 | paper_coherent_statistics/4cbc4e508f5a383b | 更细 CsI 单实验核、六条 1D 与四个 2D 平面；不是本截图的原联合图 |

本次逐项核对发现，后来的 separate 版与截图原版的 8 组 `x,y,chi2_csi,chi2_lar` 完全相同：修改的是展示和是否保存/显示 joint，单实验表面没有改变。见[separate 版报告](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_separate_experiment_comparison/NATIVE_OVERLAP_COMPARISON_REPORT.md>)。这版的移除联合图不应被解释为更换了 likelihood 或已经修复论文差异。

此前[另一组高分辨率结果整理](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_statistics_review_20261022/README.md>)可继续作为补充，但本次应以本报告提供的截图原文件和原表面为定位入口。

## 9. 本次核查做了什么，哪些仍未验证

本次完成：确认截图与原图对应；读取八个原 NPZ；验证联合表面确实等于两个 raw profile 表面之和；验证后来 separate 版保留了同一单实验表面；用记录的两个 Fast 核与统计函数重新计算每张表面保存的网格最低点；在同一模型下计算 SM；从 Git 恢复原脚本为只读文本；检查报告链接与文件哈希。全部 24 个网格最低值的重算差值保存在 [EVIDENCE.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_Fig3_Fig7_native_overlap_review_20261022/EVIDENCE.json>)。

本次没有执行全参数扫描、重建核、修改积分分辨率、替换数据或重新生成图。原版目录全部文件的 SHA256 保持一致，图和 χ² 数组均保留。

该截图运行本身没有提供与其全部八个平面配套的积分收敛研究、连续全局最低值细化、完整 nuisance 诊断和 toys 覆盖率校准。Fast/Slow 在某参考设置一致只能证明同设置的重建一致，不能替代积分收敛或与论文 likelihood 的等价性验证；后来另一套高分辨率核的检查也不能直接移用为这张粗核截图的验证。

因此可准确称为“基于原工程核响应和 legacy 能谱统计的 CsI2021、Ar2020 及其独立 nuisance 联合 NSI 比较结果”，原运行状态是 `PARTIAL_NATIVE_APPROXIMATE_COMPARISON`。其主要物理展示是 u/d 退化、电子/缪子味补偿与味改变平方项；与论文 Fig.4 分离弯带的差异仍是需要解释的结果。

对应原 Codex 对话名为 **【COHENRENT问题】迁移统计部分**，ID `01a0ca87-49c4-7061-983e-70c35ea11800`。后来 **处理 COHENRENT 的 root 细节** 是另一个统计模型的任务，不是截图右侧 native 环带的生成入口。
