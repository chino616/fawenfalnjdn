# COHERENT 原程序 legacy Gaussian 统计分析结果整理

定位更正：用户随后用截图明确指向早期包含 CsI2021+Ar2020 联合轮廓的 Fig.3–Fig.7 对照版本。截图对应的完整整理已另存为[原始 native overlap 结果报告](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_Fig3_Fig7_native_overlap_review_20261022/README.md>)。本文件保留为另一组高分辨率 CsI 单实验分析的补充，下面的 4.230765 等数值不用于替代截图版本。

整理日期：2026-10-22。按用户确认，本报告聚焦原程序的时间积分能谱 Gaussian 统计；ROOT 能量—时间 Poisson 分析不作为本报告的拟合结果。

主要数值采用已经完成的 CsI2021 高分辨率运行 `4cbc4e508f5a383b`。早期粗积分结果、101×101 多实验扫描和文献比较作为历史记录另列，避免将不同积分、扫描框和统计模型的数字混在一起。本次复算已有 Fast 核上的 SM 与六个一维最优点，核对保存文件与来源，不重建积分核，不重新做全扫描，不修改物理或统计实现。

## 1. “根据原本的处理”具体指什么

这里保留了原程序的核 Response、SNS 源、探测器折叠和 legacy 统计输入。Flavor 迁移把标量耦合推广为味矩阵，并把统计输入、预测、profile 与扫描拆成模块；它没有把旧数据替换为官方完整 likelihood。

计算链为

\[
\epsilon^{qV}_{\alpha\beta}
\longrightarrow \hat C_{1q}^{(6),\mathrm{NP}}
\longrightarrow \frac{d\sigma}{dT_{\rm nr}}
\longrightarrow N^{(\nu_\ell)}_{i,\mathrm{Cs/I}}
\longrightarrow S_i\,[\mathrm{counts/PE}]
\longrightarrow \min_{\alpha,\beta}\chi^2
\longrightarrow \Delta\chi^2\text{ 与允许区间}.
\]

CsI2021 的本套分析没有时间分箱，也不需要 ROOT。三种源成分的整体接受率是 `mu=0.997, e=0.848, mub=0.848`；源名称不代表已使用时间谱信息。

| 数据集 | 原统计处理 | 数据/单位 | nuisance |
|---|---|---|---|
| CsI2021 | Gaussian 残差能谱、解析双 pull profile | 9 个 PE 箱，counts/PE | 信号 0.125、背景 0.35 |
| CsI2017 | Gaussian 残差能谱、解析单 pull profile | 25 个 PE 箱，counts/bin | 信号 0.28 |
| Ar2020 | Gaussian 非对称误差，IRLS；另有 bounded 优化实现 | 12 个箱，counts/bin | 信号 0.12、背景 0.146 |

来源记录明确写有 `legacy approximate statistics` 和 `Not an official/full COHERENT likelihood`。这限定的是实验统计输入与模型的适用范围，并不等于核 Response 没有被使用。参见 [CsI2021 provenance](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/data/experiments/CsI2021/statistics/provenance.yaml>)、[统计分派](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/likelihoods.py>)和[profile 实现](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/profiling.py>)。

## 2. CsI2021 的数据与 χ²

PE 边界是 `[0.001,8.001,12.001,16.001,20.001,24.001,32.001,40.001,48.001,60.001]`，实际宽度分别为 `[8,4,4,4,4,8,8,8,12]`。

| PE 箱（边界均另加 0.001） | 数据 D | 背景 B | 对称误差 σ |
|---|---:|---:|---:|
| 0–8 | 1.021 | 0 | 0.454695767 |
| 8–12 | 13.195 | 0.229 | 3.816688713 |
| 12–16 | 18.941 | 0.455 | 4.717813051 |
| 16–20 | 13.059 | 0.480 | 4.304453263 |
| 20–24 | 11.043 | 0.429 | 3.858024691 |
| 24–32 | 5.977 | 0.329 | 2.543540564 |
| 32–40 | 1.838 | 0.229 | 2.466380071 |
| 40–48 | 2.274 | 0.179 | 2.339616402 |
| 48–60 | -0.831 | 0.154 | 1.785714286 |

三列单位均为 counts/PE。最后一箱的负值来自 residual 定义，可以进入 Gaussian χ²；这组数组不能直接用作 Poisson 原始事件计数。保存值见 [datasets.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/datasets.py>)。

统计函数为

\[
\chi^2(\epsilon,\alpha,\beta)=
\sum_{i=1}^{9}\frac{[D_i-(1+\alpha)S_i(\epsilon)-(1+\beta)B_i]^2}{\sigma_i^2}
+\left(\frac{\alpha}{0.125}\right)^2
+\left(\frac{\beta}{0.35}\right)^2.
\]

每个物理点都对 α、β 求最小值。由于模型对两个归一化参数线性，代码解一个 2×2 线性方程组，得到解析 profile；这套调用没有给 pull 另加截断边界。置信扫描使用的是 profile 后的 χ²。

原始预测 events/bin 必须先除以各箱宽再进入上式。总事件数则从 events/bin 求和；不能把九个 counts/PE 值直接相加当作事件总数。

## 3. 主要结果版本与 SM 拟合

主结果位于 [高分辨率运行目录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b>)；[原运行说明](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/README_RUN.md>)和[元数据](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/metadata.json>)保留了配置、提交、代码与核指纹。元数据记录分支为 `flavor-v8-coherent-benchmark-pdf-20260929`，基础提交为 `16dd773d5273e0558965540d92d737e7054e77db`，当时工作区为 dirty；因此不能只靠提交号重建本次所有绘图代码，应同时使用文件指纹。

| 项目 | 主结果 |
|---|---:|
| SM 名义信号总事件数 | 328.62910649 |
| SM 点 profile χ² | 4.23076509 |
| 数据项 χ² | 4.15916880 |
| nuisance 惩罚项 | 0.07159629 |
| α 最优值 | -0.03242130 |
| β 最优值 | -0.02301310 |
| α/0.125 | -0.25937040 |
| β/0.35 | -0.06575171 |

这里的 SM 点只固定 NP 为零，仍优化两个归一化 nuisance。它不是允许全部 NSI 同时变化后的全局最优点。

主核积分设置为 `(n_ER,n_Enu,n_PE_sub)=(81,240,64)`、`pe_step=0.75`；一维保存 401 点，范围 `[-1,1]`；主要二维扫描为 161×161。`n_Enu`、PE 子积分与参数扫描点数是不同概念。

早期参考核曾给出 `SM=332.93383489` 例、`χ²_SM=3.88787765`。该粗核结果保留在历史图中；本文引用更细积分的 328.6291 / 4.230765。两者同属 legacy 统计，但不应将不同核的极小值、Δχ² 和区间互相拼接。

## 4. 六种一维 NSI 结果

每行仅放开所列实数 NSI 参数，其余 NP 参数固定为零；α、β 每点 profile。下表是条件一参数的渐近 90% 区间，使用 `Δχ²=2.71`，不表示所有 NSI 同时自由时的边缘化区间。

| 参数 | 最优值 | 最低 χ² | 90% 允许集合 |
|---|---:|---:|---|
| ε_ee^uV | 0.025252 | 4.037586 | [-0.065273, 0.453706] |
| ε_μμ^uV | 0.009603 | 4.104530 | [-0.036648, 0.054343] ∪ [0.338309, 0.425199] |
| Re ε_eμ^uV | ≈0 | 4.230765 | [-0.103220, 0.103220] |
| ε_ee^dV | 0.022679 | 4.040281 | [-0.059197, 0.411472] |
| ε_μμ^dV | 0.008585 | 4.107235 | [-0.033222, 0.049013] ∪ [0.305023, 0.385592] |
| Re ε_eμ^dV | ≈0 | 4.230765 | [-0.093541, 0.093541] |

精确值见本次汇总的[一维区间 CSV](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_statistics_review_20261022/legacy_1d_intervals.csv>)和[一维最优点 CSV](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_statistics_review_20261022/legacy_1d_bestfits.csv>)，原件为 [intervals.csv](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/data/intervals.csv>)、[bestfits.csv](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/data/bestfits.csv>)。

这些结果说明：

1. 味对角项可以与 SM 振幅干涉，因此正负 ε 一般不对称。
2. μμ 存在靠近零和约 0.3–0.4 的两支允许区间。散射观测振幅平方，弱电荷改变符号后仍可给出相近事件谱，因此单个上限不能完整表达结果。
3. 当前纯味源、单实数 eμ 矢量参数的 NP 末态与 SM 末态正交，非对角贡献对 ε 的符号对称；表中 eμ 最优值约零，区间左右对称。
4. 六种一维分析都包含 SM 点；所列对角模型的最佳改善小于 0.2 个 χ² 单位。结果没有在这些条件模型中给出强烈的非零 NSI 偏好。

ee 曲线也有两个谷底，但 profile 后两谷之间的峰低于 2.71，所以 90% 允许集合连成一个区间；固定 nuisance 的中间峰更高。不能仅凭看到双谷就认定置信区间一定断开。

NSI 到原生 Wilson 矩阵的映射是 `C_NP=-sqrt(2)*G_F*epsilon`，返回 `(6,1,"u")`、`(6,1,"d")` 的 NP-only 矩阵，非对角元填入厄米共轭，预测层通过 `include_sm=True` 加 SM 一次。此 legacy 参数接口直接使用原生矩阵约定，不要从后来 Time2D 的另一个公开矩阵接口照搬转置。见 [parameters.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/parameters.py>)。

## 5. 四个二维参数平面

二维结果使用 `Δχ²=4.61`，对应两个所示物理参数。每个平面从自身共同最低 χ² 定义 Δχ²，不逐个允许岛分别归零；其他 NSI 均固定为零。主结果的轮廓在保存扫描框内闭合。

| 平面（x,y） | 细化最优点 (x,y) | 最低 χ² |
|---|---|---:|
| (ε_ee^uV, ε_μμ^uV) | (0.178258, -0.034202) | 3.862194 |
| (ε_ee^dV, ε_μμ^dV) | (0.169029, -0.031190) | 3.853047 |
| (ε_ee^uV, Re ε_eμ^uV) | (0.169134, -0.097498) | 3.936827 |
| (ε_ee^dV, Re ε_eμ^dV) | (0.165493, 0.089138) | 3.919427 |

精确值见[二维摘要 CSV](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_statistics_review_20261022/legacy_2d_bestfits.csv>)和[原二维元数据](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/data/plane_summaries.json>)。混合平面含 eμ→−eμ 对称点；表中列出优化器保存的一支，不代表只有这一个最优点。

S3 图中的星号标注为离散 `Grid minimum`，表中列出的是连续细化结果；平坦退化带上两者可以处在不同坐标，不能据此将星号坐标直接当成表中的最优值。该 legacy 结果呈闭合环状允许带，不应套用后来时间二维分析的分支形状来解读。

S3 表示电子味和缪子味耦合可相互补偿，但 prompt νμ 与 delayed νe、反νμ 的不同能谱仍提供区分。S4 表示味对角干涉降低事件率时，可以补偿味改变平方项提高的事件率；所以一维的 eμ 上限不能直接当作混合平面的上限。uV、dV 约束不同来自核中质子、中子的夸克组合。

本次最高分辨率主结果只使用 CsI2021；没有把 CsI2017 与 CsI2021 当成两个独立样本相加，也没有把未经匹配验证的 Ar 联合结果带入这四个平面。

## 6. 图表对应关系与读图方法

| 图 | 结果文件 | 应关注的比较 |
|---|---|---|
| S1 | [SM 能谱与残差 PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/figures/fig_S1_csi2021_spectrum.pdf>) | 数据、三源信号和背景；比较名义 SM 与仅调整 α/β 的条件 SM 模型 |
| S2 | [六个一维 profile PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/figures/fig_S2_1d_profiles.pdf>) | 对角项符号不对称、μμ 第二支、eμ 正负对称；蓝线 profile、橙线固定 nuisance |
| S3 | [ee–μμ 二维限制 PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/figures/fig_S3_ee_mumu.pdf>) | 两种入射味的补偿，以及 uV/dV 之间的差异 |
| S4 | [对角–味改变二维限制 PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/figures/fig_S4_diagonal_flavorchanging.pdf>) | 对角干涉和非对角平方项如何共同改变允许域 |
| V1 | [Fast/Direct 与积分验证 PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/figures/fig_V1_fast_direct_statistics.pdf>) | 区分参考积分设置的代数一致性和高分辨率核的积分收敛 |
| A2 | [nuisance pulls PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/figures/fig_A2_nuisance_pulls.pdf>) | 检查允许域中归一化调整的大小，不能只根据谱线重合判断拟合 |

S2 中 profile 和 fixed 两种曲线各自减去自己的最低值。因此应比较阈值交点与曲线形状；若要比较最优拟合绝对优劣，应查看保存的 raw χ²，而不能从两个已各自归零的谷底读出改善量。原图注见 [FIGURE_CAPTIONS.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/FIGURE_CAPTIONS.md>)。

![legacy 六种一维 NSI profile](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/figures/fig_S2_1d_profiles.png>)

![legacy ee–mumu 二维 profile](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/figures/fig_S3_ee_mumu.png>)

## 7. 数值验证实际完成到哪一步

本段区分旧运行的验证记录和本次对保存结果的复核；本次没有重新执行多小时积分或全部测试套件。

| 检查 | 已保存结果 |
|---|---|
| 参考设置 Fast/Direct 的最大 Δχ² 差 | 8.17×10^-7，通过 |
| 参考设置最大端点相对位移 | 3.00×10^-8，通过 |
| 主核独立细化 ER、Eν、PE | 通过所设积分目标 |
| 六条 1D 曲线的相关区最大 Δχ² 变化 | 0.013113 |
| 1D 端点最大变化 / 所在允许区间宽度 | 0.093656% |
| 四个 2D 平面轮廓附近最大 Δχ² 变化 | 0.013424 |
| 2D 允许面积的最大积分细化变化 | 0.101854% |
| 2D 允许面积的最大扫描网格变化 | 1.079650% |
| 与主核同等高分辨率的独立 Direct 全面核对 | NOT_RUN |
| 总体数值验证状态 | PARTIAL |
| 官方统计输入溯源 | LEGACY_APPROXIMATE_UNVERIFIED |

本运行的数值目标为相关区 `|Δχ²|` 变化小于 0.05、1D 区间端点变化小于该区间宽度的 1%。积分目标通过不意味着整个二维边界已达到任意精度；尤其不能把 2D 面积的扫描网格变化与积分变化混为一项。

原始记录见 [NUMERICAL_VALIDATION.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/NUMERICAL_VALIDATION.md>)和[validation_summary.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/data/validation_summary.json>)。更早 `(21,120,8,pe_step=3)` 的粗核未通过后来设定的积分目标，其图保留作诊断。

本次补做的轻量复核包括：重新加载已有主核计算 SM χ²、α、β 和总事件数；在六个保存的一维最优参数值重新计算 profile χ²；比较运行记录的代码/核指纹；核对所有报告链接对应的文件。具体差值和当前代码一致性保存在 [EVIDENCE.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_statistics_review_20261022/EVIDENCE.json>)；文件大小与 SHA256 索引保存在 `FILE_INDEX.csv`。这些检查不等于新做了一轮最小值搜索或覆盖率校准。

## 8. 更早的多实验结果如何归档

### 8.1 第一轮 CsI2021 flavor 与 CsI+Ar 图

第一轮 [flavor_gate_report.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/flavor_benchmark/CsI2021/flavor_gate_report.md>)记录了味选择、对角干涉、非对角符号对称及粗设置 Slow/Fast 检查。由于其参考核和扫描范围不同，不能把其中约 3.5–3.9 的最小 χ² 与主结果约 4.2 直接作物理优劣比较。

[CsI+Ar 初步结果报告](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/flavor_benchmark/COHERENT_CsI_Ar/ar_combined_gate_report.md>)使用低分辨率 Ar 核，提供 u/d 退化方向示例。单独每个实验先 profile，再逐点加 raw χ²；不能先将两个实验各自的 Δχ² 相加冒充联合 profile。

### 8.2 101×101 历史扫描

[HIGHRES_REPORT.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/flavor_benchmark/COHERENT_highres_all_grid101/HIGHRES_REPORT.md>)曾对 CsI2021、CsI2017、Ar2020 及三者相加扫描三个 u/d 平面，每轴 `[-1,1]`、101 点，生成 15 组图（含对比图）。其 12 行数据集/平面摘要均标记扫描框截断，部分网格最优值落在框边界。因此其 `PASS` 仅表示当时的数值/产物检查，不能当作闭合的全参数物理限制。

该历史版把 CsI2017 和 CsI2021 相加；它们包含重叠的数据，不能未经联合数据定义就作为独立样本使用。应保留历史文件，但不推荐把这版 combined 曲线作为论文的正式 COHERENT 联合约束。

完整旧摘要已按原值另存为[历史 101×101 数值记录](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/docs/COHERENT_statistics_review_20261022/historical_101_grid_results.csv>)，原件为 [highres_scan_summary.csv](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/flavor_benchmark/COHERENT_highres_all_grid101/highres_scan_summary.csv>)；原[汇总 PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/output/pdf/coherent_flavor_highres_grid101_lowres_summary.pdf>)仍可查阅。

u/d 退化来自近似弱荷组合 `(2Z+N) ε_u + (Z+2N) ε_d`。Cs 为 `188 ε_u+211 ε_d`，I 为 `180 ε_u+201 ε_d`，Ar 为 `58 ε_u+62 ε_d`。不同靶核可以改变退化方向，但不保证有限扫描框内必然得到完全闭合的允许域。

### 8.3 与 arXiv:2211.11905 的早期比较

此前另做过 [CsI2021-only 与 Ar2020-only 并列比较](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/Benchmark/260928 COHENRENT-NSI/native_separate_experiment_comparison/NATIVE_OVERLAP_COMPARISON_REPORT.md>)及[七页汇总 PDF](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/output/pdf/benchmark_2211_11905_csi2021_ar2020_separate_comparison.pdf>)。修订版分别显示两个实验，没有输出新的 joint 网格。它使用 legacy 能谱近似，因此仅是模型/轮廓比较；论文使用的能量—时间信息和 nuisance 模型不同。Fig.7 的 NGI scalar/tensor 未复现，报告明确标为不可比较。

## 9. 代码在哪里，修改什么参数

原结果的完整绘图代码在另一个工作树中，不能只在当前 Gitup01 搜索输出文件名。

| 内容 | 真实文件 |
|---|---|
| 统计输入、背景、误差、nuisance σ | [datasets.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/datasets.py>) |
| Gaussian χ² 分派 | [likelihoods.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/likelihoods.py>) |
| nuisance 解析求解、Ar IRLS | [profiling.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/profiling.py>) |
| ε→NP Wilson 味矩阵 | [parameters.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/parameters.py>) |
| events/bin→counts/PE 与箱边界验证 | [observables.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/observables.py>) |
| 全局极小值细化、置信交点 | [confidence.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/src/cevns_pyeft/statistics/confidence.py>) |
| 主结果生成入口 | [generate_coherent_paper_figures.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/tools/statistics/generate_coherent_paper_figures.py>) |
| 401 / 161 网格、阈值及主核选择 | [coherent_paper_figures_highres.json](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/configs/coherent_paper_figures_highres.json>) |
| 主结果使用的积分核 | [csi_nER81_nEnu240_nPE64_step0p75.npz](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/kernels/csi_nER81_nEnu240_nPE64_step0p75.npz>) |
| 旧版主统计接口（当前 Gitup01） | [当前 likelihoods.py](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/src/cevns_pyeft/statistics/likelihoods.py>) |

只改扫描范围或作图布局时应改配置/绘图脚本；改观测数据、误差或 σ 时才改变统计输入，并重新标识统计模型。不要直接修改保存的 χ² 数组或置信端点去匹配文献。上述为现有文件地图，本次没有更改这些实现。

重新绘图的已有入口（在结果所属的工作树 Gitup01 中运行）为：

```powershell
python tools/statistics/generate_coherent_paper_figures.py --config configs/coherent_paper_figures_highres.json --stage plot
python tools/statistics/generate_coherent_paper_figures.py --config configs/coherent_paper_figures_highres.json --stage report
```

这些命令供之后复用；本次没有执行重新扫描或覆盖原图。原运行 `--stage all` 含高成本积分，不是只改图形所必需的操作。

## 10. 与最新 Notebook 图、ROOT 分析的边界

最新 Notebook 第 13 节的 SM/FV NP/总信号 `328.646/3181.740/3510.386` 是给定非对角 Wilson benchmark 的探测器级信号预测；当时没有把这三个谱送入本报告的 χ² 得到限制。不能把 3181.740 例当作已经被拟合允许的新物理事件数。

该 Notebook 明确使用 `sin²θW=0.23873`，主统计核沿用其自身记录的源、常数与积分设置；即使 SM 总数很接近，也应按各自元数据核对，不能把最新图的总数替换为旧统计拟合输入。相关[Notebook](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/论文图NoteBook/4. CEvNS_pyEFT_COHERENT_CsI2021_paper_figures - v2.ipynb>)和[信号预测报告](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260929Gitup1-CONUS-2/Gitup01/论文图NoteBook/7. csi2021_detector_figures/NUMERICAL_REPORT.md>)保持原样。

后来读取 ROOT、原始 C/AC 事件并构建 9×11 Poisson likelihood 的工作属于独立统计模型，其 80 多的 χ² 与此处约 4 的 Gaussian χ² 不可直接比较。本报告按用户选择不将那套数字作为 legacy 结果。

## 11. 对应的 Codex 对话和本报告可采用的结论

旧统计迁移与第一轮扫描对话的原名是 **【COHENRENT问题】迁移统计部分**，对话 ID 为 `01a0ca87-49c4-7061-983e-70c35ea11800`。后续论文图工作位于当前对话 **【论文图】阅读 CEvNS 程序中的相干散射**，ID 为 `01a15f94-64e5-7c80-9b24-b0cca23e4e31`。本次仅阅读对话记录，没有向其他对话发送消息。

可准确表述为：

> 使用 CEvNS-pyEFT 原生核响应与 SNS 预测链，在保留原程序 legacy Gaussian 时间积分能谱统计模型的条件下，完成 CsI2021 的味依赖矢量 NSI 一维和二维 profile 分析。μ 味对角参数出现分离允许区间，单实数非对角参数体现正负对称；混合平面显示干涉项与味改变平方项的补偿。主积分核通过独立积分细化检查；同分辨率全面 Direct 核对尚未执行，实验输入仍应标注 legacy approximate。

这些结果适合说明程序的味结构、profile 和扫描能力；它们没有加入官方完整的时间—能量 likelihood、覆盖率 toys 校准或完整多算符分析。完整限制记录见[原 PROVENANCE_AND_LIMITATIONS.md](<F:/Work/2026-07-15 CEvNSpyEFT-Local/260820Gitup1-Flavor/git-worktree-f0/Gitup01/results/paper_coherent_statistics/4cbc4e508f5a383b/PROVENANCE_AND_LIMITATIONS.md>)。
