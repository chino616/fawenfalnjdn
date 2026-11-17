# 太阳⁸B电子味矢量NSI onboarding v3.3：主线计算与核对版（新版本）

**2026-11-12。已在原 Gitup01 实现并完成三样本联合计算。** 本版集中给出实际数值、来源、代码和结果；旧SM v3.2.1、多bin v3.1和轻媒介子V/B−L版本保留。

**能力结论：NSI区域已经算出；2601.19883v2 Fig.4绿色区域的精确复现尚未成立。** 传播采用明确的两味绝热近似，XENONnT尾段采用显式项目假设并做界；论文中间窄禁区与本计算不一致。科学接受仍为NOT_REVIEWED，不将数值通过升级为原文等价或终稿认证。

[NSI来源与参数卡](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json>) · [只读基础输入](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>) · [实际结果与验收](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>) · [主线运行入口](<../../../../tools/run_solar_b8_nsi_benchmark.py>)

<a id="toc"></a>

## 目录

- [本轮目标、版本与三条隔离流程](#scope)
- [Source：通量、密度与产生区](#source)
- [Source：电子味存活概率](#state)
- [Target与原子核Response](#target)
- [Interaction：只改变电子味散射](#interaction)
- [Detector与Observable：三个单bin](#detector)
- [Prediction：Slow与保留能量轴的Fast](#prediction)
- [Statistics：联合区域](#statistics)
- [实际结果、对照与论文差异](#results)
- [Onboarding到程序及复算](#code)
- [核验范围和下一步](#handoff)
- [标准参考文献与原件](#references)

<a id="scope"></a>

## 本轮目标、版本与三条隔离流程

| 流程 | 输入与模型 | 程序/结果 |
|---|---|---|
| 旧多bin | 2411.11749v1；Ne/cS2、Qy、逐箱数据/背景及旧响应 | [multibin入口](<../../../../tools/run_solar_b8_multibin_benchmark.py>) |
| 旧单bin SM v3.2.1 | 固定SM、三份Total效率；原舍入误差1.3/28/3.95 | [冻结读本](<SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md>) |
| 本版单bin NSI v3.3 | 实数ee-uV/dV；传播+散射；精确论文百分比误差；独立kernel | [NSI目录](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) / [独立输出](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>) |


只读复用旧单bin的谱形、同位素与Total表。NSI独立data、dataset/analysis身份、状态、相互作用、统计和缓存；不读取多bin的Qy、D_i、B_i、c_i，也不把V/B−L轻媒介子结果改名为接触NSI。新loader使用scoped Catalog，不改变全局默认实验列表。

[返回目录](#toc)

<a id="source"></a>

## Source：通量、密度与产生区

总通量与谱形分开：$d\phi/dE_\nu=\Phi_{8B}f_{8B}(E_\nu)$；不因拟合、换核响应或开启NSI而重标定太阳通量。

| 输入 | 实际数值/数组、单位 | 数值文件、出处与核验范围 |
|---|---|---|
| 总通量 | 5.46×10⁶ cm⁻²s⁻¹；固定 | [physics](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/nsi.input.json>)；[propagation] p5 Eq.(29)。2601未重印作者输入卡，属明确项目选取 |
| 谱形 | 829×2；E=0–16.56 MeV，f单位MeV⁻¹；原网格积分=0.999986544 | [b8_source.txt](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt>)；[R6]官网原829行前两列；分段线性、表外0、保留原精度 |
| 振荡参数 | θ12=0.583638 rad；θ13=0.149575 rad；Δm²21=7.42×10⁻⁵ eV² | [固定PEANUTS示例 Neutrinos](<../../../../outputs/solar_b8_nsi/20261112_fig4_run1/source_evidence/peanuts_examples_solar_test.yaml>)；[peanuts]。明确项目选择，不冒称2601作者卡 |
| 弱混合角 | sin²θW=0.23857，单位1 | [基础物理卡](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)；[R9]既有项目SM点 |
| 时间与常数 | 31557600 s/yr；N_A=6.02214076×10²³ mol⁻¹ | [R10]单位约定；G_F、ℏc使用[共享常数](<../../../../cevns_pyeft/foundation/constants.py>) |


profile列顺序：r/Rsun、ne/N_A [mol/cm³]、nn/N_A [mol/cm³]、⁸B产生区分布[任意整体归一]。

| profile | shape | 逐列范围 | 首行代表值 | 文件 |
|---|---|---|---|---|
| solar_b16_gs98_profile.txt | [1000, 4] | 0.0005–0.5; 1.1534533–100.92529; 0.19954674–49.874711; 5.3446518e-23–18.360128 | 0.0005, 100.92529, 49.874711, 0.012353955 | [完整数值](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/solar_b16_gs98_profile.txt>) |
| solar_b16_agss09_profile.txt | [1000, 4] | 0.0005–0.5; 1.1561122–100.92529; 0.18888776–47.974711; 2.3316418e-23–18.337016 | 0.0005, 100.92529, 47.974711, 0.012600673 | [完整数值](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/solar_b16_agss09_profile.txt>) |


主计算B16-GS98；AGSS09仅作密度/产生区敏感性，总通量仍固定5.46×10⁶。PEANUTS原产生区表1000行，取列1/3/9，电子密度从log10转换；Magnus质量密度2000行，取半径严格相同的前1000行，无跨模型插值。原四表保留在NSI数据目录，逐文件SHA256见参数卡。

**中子密度是PROJECT_DERIVED**：$n_n/N_A=\rho_{\rm mass}-n_e/N_A$，采用中性物质和每重子1u近似。它不是论文直接发布的中子密度表。产生区按 $dr$ 积分归一；原表已是径向分布，不能额外乘 $r^2$。

PEANUTS固定commit `39ef11f6d10014822809da65fa60752ea21aabb6`。Magnus固定commit `7eb53ef0b3e960b3b10383fef99bfe0c9110cc8f`的质量密度是**明确采用的二手转录**。原作者结构表URL本轮返回403/HTML验证页，原47列文件与此转录的等价性未独立认证；没有将HTML当数据，也未执行下载的外部代码。


[propagation] LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024. p5 explicitly includes NSI in propagation; p10 Appendix B EqsB4-B9, two-flavor adiabatic average, theta13_m=theta13, no Earth matter. For ee-only: epsilonD_q=-cos²theta13 epsilonee_q/2, epsilonN=0; sum u+d potentials.。

[R6] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from 8B decay[J]. Physical Review C, 1996, 54: 411-422. DOI: 10.1103/PhysRevC.54.411. Official numerical spectrum[DS/OL], accessed 2026-11-06. 829 numeric rows, columns 1 and 2; normalized shape, not total flux; original rounding retained。

[R9] Project SM benchmark decision, retained from the 2411.11749v1 analysis, 2026-11-10/11[Z]. sin^2 theta_W=0.23857 retained as explicit project input; NOT claimed as a printed numeric default of 2601.19883v2。

[R10] BIPM. The International System of Units (SI), 9th edition[M/OL]. 2019. IAU. Julian year convention[Z]. Avogadro exact 6.02214076e23 mol^-1; year=365.25*86400 s as project unit convention; A*amu from existing shared foundation.constants。

[b16] VINYOLES N, SERENELLI A M, VILLANTE F L, et al. A new generation of standard solar models[J]. Astrophysical Journal, 2017, 835: 202. DOI:10.3847/1538-4357/835/2/202. arXiv:1611.09867. B16 GS98 / AGSS09 numerical model tables; n_e and B8 production from nudistr columns1,3,9; mass density from struct column4 (distributed as trimmed column2)。

[peanuts] GONZALO T E, LUCENTE M. PEANUTS: a software for the automatic computation of solar neutrino flux and its propagation within Earth[J]. European Physical Journal C, 2024, 84:119. DOI:10.1140/epjc/s10052-024-12423-3. arXiv:2303.15527. Data/nudistr_b16_gs98.dat and agss09.dat headers/columns; peanuts/solar.py SolarModel and solar_flux_mass use normalized integral in dr, not extra r²; examples/solar_test.yaml Neutrinos gives adopted oscillation inputs。

[magnus] BUSTAMANTE M. Magnus: public tabulated solar model distribution[DS/OL]. Fixed Git commit, accessed2026-11-12. src/magnus/data/solar_models/b16_gs98.dat and b16_agss09met.dat; tools/build_solar_model_tables.py. Header supplies original source URL and original SHA256.。

[返回目录](#toc)

<a id="state"></a>

## Source：电子味存活概率

太阳先产生电子味中微子，传播后只有 $P_{ee}$ 部分仍以电子味到达。开启电子味NSI时，不能继续采用SM的味等价代表态。

采用[propagation] PDF p10 Appendix B Eqs.(B4)–(B9)的**两味绝热近似**：$\theta_{13,m}=\theta_{13}$，忽略地球再生。实数ee-only矢量子空间给出：

$$
n_u=2n_e+n_n,\quad n_d=n_e+2n_n,\qquad
V_{ee}=\sqrt2G_F(n_e+n_u\epsilon_{ee}^{uV}+n_d\epsilon_{ee}^{dV}),
$$

$$
A=2E_\nu\cos^2\theta_{13}V_{ee},\qquad
\cos2\theta_{12,m}=\frac{\Delta m_{21}^2\cos2\theta_{12}-A}{\sqrt{(\Delta m_{21}^2\cos2\theta_{12}-A)^2+(\Delta m_{21}^2\sin2\theta_{12})^2}},
$$

$$
P_{ee}(E_\nu;\epsilon)=\sin^4\theta_{13}
+\frac{\cos^4\theta_{13}}2\left[1+\cos2\theta_{12}\int dr\,w_{8B}(r)\cos2\theta_{12,m}(E_\nu,r;\epsilon)\right],\quad\int dr\,w_{8B}=1.
$$

以上是原文B4–B9在ee-only子空间的代入；$\epsilon_D^q=-\cos^2\theta_{13}\epsilon_{ee}^{qV}/2$，$\epsilon_N=0$，u、d的势相加。密度与角度数值均见上一节实际文件，没有缺省的“真实Pee数组”。程序每个参数点重算Pee，不复用固定SM概率。

| 数值函数 | 实际取得与验证 | 程序/结果 |
|---|---|---|
| Pee(E;eu,ed) | 上述两味模型；能量MeV→eV，密度mol/cm³→自然单位；每径向面板8阶Gauss | [SolarMSW.pee / radial_quadrature](<../../../../cevns_pyeft/sources/solar_msw.py>) |
| SM Pee(2,5,10,15MeV) | 0.486440602, 0.390788439, 0.323455858, 0.305219461 | [实际数值](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/NSI_RESULTS.json>) |
| 状态ρ(E) | diag(Pee,(1−Pee)/2,(1−Pee)/2)，shape=N_E×3×3；逐能量检查finite/PSD/trace=1 | μ/τ相等分配仅在两味SM散射相同的ee-vector子空间观测等价，并非分别Pμ、Pτ的传播预测 |
| 独立核验 | 原生径向1000点积分、2×2 Hamiltonian本征向量、真空限与概率界；径向8→16阶 | [测试](<../../../../tests/test_solar_nsi.py>) / [径向收敛](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/NSI_RESULTS.json>) |


[propagation] LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024. p5 explicitly includes NSI in propagation; p10 Appendix B EqsB4-B9, two-flavor adiabatic average, theta13_m=theta13, no Earth matter. For ee-only: epsilonD_q=-cos²theta13 epsilonee_q/2, epsilonN=0; sum u+d potentials.。

**适用限制：这不是完整三味数值演化。** 尤其大耦合处的全平面最小值是本近似模型的外推；不能由数值收敛证明θ13,m近似在所有大耦合仍准确。

[返回目录](#toc)

<a id="target"></a>

## Target与原子核Response

核数仍用完整九行NIST数丰度作分母：$n_A^{(1t)}=10^6N_A\eta_A/\sum_B\eta_Bm_B^{\rm atom}$。截面内部核质量沿用共享 $A m_u$ 约定。 平均摩尔质量=131.29276145 g/mol；实际七核素数丰度99.8158%。

| 核素key | 数丰度[1] | 原子质量[u] | 每吨核数[推导] | 实际M核表 |
|---|---|---|---|---|
| Xe124 | 0.000952 | 123.905892 | 4.3666368e+24 | MISSING：不计入、不补KN、不重归一 |
| Xe126 | 0.00089 | 125.9042983 | 4.082255e+24 | MISSING：不计入、不补KN、不重归一 |
| Xe128 | 0.019102 | 127.903531 | 8.7617117e+25 | J=0; b=11.579299 GeV⁻¹; M[2, 2, 11]; pp/pn/nn a0=2915.838/3995.65/5475.346 |
| Xe129 | 0.264006 | 128.90478086 | 1.2109436e+27 | J=0.5; b=11.592467 GeV⁻¹; M[2, 2, 11]; pp/pn/nn a0=2915.962/4049.608/5623.986 |
| Xe130 | 0.04071 | 129.90350935 | 1.8672876e+26 | J=0; b=11.605553 GeV⁻¹; M[2, 2, 11]; pp/pn/nn a0=2915.853/4103.528/5774.961 |
| Xe131 | 0.212324 | 130.90508406 | 9.7388843e+26 | J=1.5; b=11.61856 GeV⁻¹; M[2, 2, 11]; pp/pn/nn a0=2915.977/4157.703/5928.2 |
| Xe132 | 0.269086 | 131.90415509 | 1.2342446e+27 | J=0; b=11.631486 GeV⁻¹; M[2, 2, 11]; pp/pn/nn a0=2915.992/4211.84/6083.553 |
| Xe134 | 0.104357 | 133.90539466 | 4.7866504e+26 | J=0; b=11.657106 GeV⁻¹; M[2, 2, 11]; pp/pn/nn a0=2915.959/4319.242/6397.844 |
| Xe136 | 0.088573 | 135.90721448 | 4.0626693e+26 | J=0; b=11.682421 GeV⁻¹; M[2, 2, 11]; pp/pn/nn a0=2915.998/4427.994/6723.986 |


[9×3原子质量/丰度表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xe_isotopes.txt>)；[实际核响应数值文件](<../../../../data/responses/responses_all.json>)。核表SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。

采用ResponseDB的(p,n)基底、W=e⁻²ʸ∑a_k yᵏ和已有全部实现通道M/SigmaPP/SigmaP/PhiPP/PhiPT/Delta/MPhiPP/SigmaPDelta；经原Li2026适配器进入振幅。没有再乘KN、Helm或额外自旋因子。共享理论公式在原模块维护，本文件只记录调用与实际资源。核表数值可用；外部作者原始版本和转换仍未独立认证，保留为R8本地直接采用来源。

[R7] NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06. nine original A/mass/number-fraction rows; full nine-row mean molar mass used before selecting seven available responses。

[R8] CEvNS-pyEFT local resource. responses_all.json[DS]. User-selected existing nuclear-response table; external author release and conversion NOT independently certified. Xe128,129,130,131,132,134,136; np basis ordered p,n; W=e^-2y sum a_k y^k; M,SigmaPP,SigmaP,PhiPP,PhiPT,Delta,MPhiPP,SigmaPDelta; no extra KN or spin prefactor。

[返回目录](#toc)

<a id="interaction"></a>

## Interaction：只改变电子味散射

[paper2601] PDF p22 Eq.(95)采用 $C_{1,q}^{(6),\mathrm{NSI}}=-\sqrt2G_F\epsilon_{ee}^{qV}$，q=u,d，单位GeV⁻²；只有味矩阵ee元非零。SM及共享的LEFT→核子匹配、粒子响应R与核响应W、振幅归一化全部委托既有Li2026LegacyInteraction。

在本子空间，μ、τ仍是SM截面，因此实际入射态收缩为：

$$
\frac{d\sigma_{\rm eff}}{dT}
=\frac{d\sigma_{\rm SM}}{dT}
+P_{ee}(E_\nu;\epsilon)\left[\frac{d\sigma_e(\epsilon)}{dT}-\frac{d\sigma_{\rm SM}}{dT}\right].
$$

这是味密度矩阵与对角散射核收缩的代数式。即使电子味振幅被NSI抵消，$(1-P_{ee})\sigma_{\rm SM}$仍在，不能把全部太阳通量都按电子味NSI散射。

| 对象 | 实际输入/输出 | 位置与依据 |
|---|---|---|
| 扫描参数 | 实数εee-uV、εee-dV；无量纲；其余NSI=0 | [nsi_point / couplings](<../../../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>)；Eq.(95)；非法味、复数和非对角项拒绝 |
| 截面 | cm²/keV；E轴MeV，T轴keVnr；6个单项式1,eu,ed,eu²,eu·ed,ed² | ElectronVectorNSI.spectral_coefficients；共享适配器四个SM vector/axial维6基底；固定T的E²dσ精确二次代数，不是拟合校准 |
| 传播/散射绑定 | 同一组(eu,ed)，错误参数点拒绝 | [check_point](<../../../../cevns_pyeft/experiments/solar_nsi.py>) |


[paper2601] LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2. p19 Eq84; p20 Eqs87,88 (three independent .12 pulls, percentages); p22 Eq95 mapping and 2-parameter Delta chi2=4.61; p23 Fig4 green region。

[propagation] LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024. p5 explicitly includes NSI in propagation; p10 Appendix B EqsB4-B9, two-flavor adiabatic average, theta13_m=theta13, no Earth matter. For ee-only: epsilonD_q=-cos²theta13 epsilonee_q/2, epsilonN=0; sum u+d potentials.。

[返回目录](#toc)

<a id="detector"></a>

## Detector与Observable：三个单bin

| 样本 | shape | 表内T[keVnr] | 首/末ε[1] | 积分T[keVnr] | 曝光[t·yr] | 数据与直接位置 |
|---|---|---|---|---|---|---|
| PandaX_paired | [52, 2] | 1.1–3 | 0.0108296334/0.0738275713 | [1.1, 3.0] | 1.2 | [数值表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_paired_total.txt>)；R2 PDF p3 Fig.1 Total paired; official exposure 1.20, not R5 1.25; T bounds R4 Table II |
| PandaX_US2 | [99, 2] | 0.3–3 | 0.00579130472/0.0155469009 | [0.3, 3.0] | 1.04 | [数值表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_us2_total.txt>)；R2 PDF p3 Fig.1 Total US2 and exposure; T bounds R4 Table II; no extra Qy/Ne window |
| XENONnT | [40, 3] | 0.429999996–2.77 | 0.000111966578/0.123987529 | [0.5, 3.0] | 3.51 | [数值表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xenonnt_combined.txt>)；R3 PDF p4 Fig.1 black combined; exposure R3 3.51; bounds R4 Table II |


PandaX来自[R2] 2407.10892v3 PDF p3 Fig.1黑Total paired实线、US2虚线；曝光1.20、1.04 t·yr来自原实验。2409 Table II的paired=1.25与其冲突，本版沿用原实验1.20。XENONnT来自[R3] 2408.02877v2 PDF p4 Fig.1黑combined；3.51 t·yr。积分T界来自[R4] PDF p13 Table II。均为原生PDF矢量坐标提取，转数值后分段线性插值。X表第三列保留可见标记，低端在图框下的原生路径已提取，但不能声称逐点视觉核实。

**XENONnT约2.77–3 keVnr效率仍为MISSING。** 主扫描明确令ε(T)=末点0.123987528765，名称flat_sensitivity，是项目假设；另算zero/unit的0≤ε≤1两端，以及逐参数点对未知尾信号区间的无惩罚profile。后者是附加未知尾nuisance，不冒称论文原likelihood。范围外不静默插值为实验数据。

总效率已含选择和ROI，只乘一次；本单bin积分不再要求Qy、S1/S2二维概率矩阵或按Ne切窗。这里的探测器效率与原子核Response W是不同物理对象。


[R2] BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3. PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI。

[R3] APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2. PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr。

[R4] LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025. PDF p13 Table II: fitted yields, rounded statistical sigmas, T bounds, external SM references; p13 Eq.(E6) text flux 5.16e6; p14 Eq.(E8) shared pull, NOT adopted。

[返回目录](#toc)

<a id="prediction"></a>

## Prediction：Slow与保留能量轴的Fast

[paper2601] p19 Eq.(84)、p20 Eq.(87)，曝光、每吨核数和时间展开一次：

$$
S_k=\mathcal E_k\sum_A n_A^{(1t)}t_{\rm yr}\int_{T_{\min,k}}^{T_{\max,k}}dT\,\varepsilon_k(T)
\int_{E_{\min,A}(T)}^{16.56\,\mathrm{MeV}}dE_\nu\,\Phi_{8B}f_{8B}(E_\nu)\frac{d\sigma_{{\rm eff},A}}{dT}.
$$

输出每样本shape=(1,)，单位events/bin；核表→振幅→截面→含味概率的反冲率→Total效率→曝光→一个信号数。源通量、核数、效率、曝光各一次。没有c_i、信号标定或为贴图调整通量。

Fast只预积与味态无关的部分，保留E轴：$S_k=\sum_{A,j}w_j[K_{kA,0}(E_j)+P_{ee}(E_j;\epsilon)\sum_{m=1}^5K_{kA,m}(E_j)p_m(\epsilon)]$。K中已含源强、核数、曝光和效率；p_m为上节单项式。**Pee在每个扫描点重算，最终率面不是固定二次式。** 后端`energy_resolved_ee_vector_nsi_v1`独立于原固定ρ的interface_kernel_v1。

| 样本 | K shape | 实际Gauss E轴 | 文件 |
|---|---|---|---|
| PandaX_paired | [7, 2, 6, 144] | 0.0011466214–16.558853 MeV | [实际kernel](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/kernels/PandaX_paired.npz>) |
| PandaX_US2 | [7, 2, 6, 144] | 0.0011466214–16.558853 MeV | [实际kernel](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/kernels/PandaX_US2.npz>) |
| XENONnT | [7, 2, 6, 144] | 0.0011466214–16.558853 MeV | [实际kernel](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/kernels/XENONnT.npz>) |


K轴依次[核素, 已知段/未施效率尾段, 6单项式, E]；energy_weights另存MeV权重。NPZ禁止pickle，数组摘要和所有折叠依赖指纹均校验；只更换传播/profile时，rebind_state先要求源强/靶/曝光/效率/截面与数值设置的digest完全相同。

实际检验：T节点401→801，E Gauss96→144；9个Slow(801×480)对Fast点包括SM、(0.3,−0.1)、(−17.3,15.7)，同时检查三个样本。容差max(3×10⁻⁴ events,0.2%)；径向8→16阶独立核验。详见[前向实测记录](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/FORWARD_VALIDATION.json>)。

[paper2601] LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2. p19 Eq84; p20 Eqs87,88 (three independent .12 pulls, percentages); p22 Eq95 mapping and 2-parameter Delta chi2=4.61; p23 Fig4 green region。

[返回目录](#toc)

<a id="statistics"></a>

## Statistics：联合区域

采用[paper2601] PDF p20 Eq.(88)和p22的二维90%阈值4.61。观测是实验拟合信号产额，非逐箱原始候选；不再添加背景或使用Poisson计数。三个样本各自一个独立12% Gaussian pull：

$$
\chi^2(\epsilon)=\sum_{k=1}^{3}\min_{a_k}\left\{\frac{[D_k-(1+a_k)S_k(\epsilon)]^2}{\sigma_k^2}+\frac{a_k^2}{0.12^2}\right\},\qquad
\chi^2_{\rm prof}=\sum_k\frac{(D_k-S_k)^2}{\sigma_k^2+0.12^2S_k^2}.
$$

| 样本顺序 | D[events] | σstat[events] | 来源与处理 |
|---|---|---|---|
| PandaX paired | 3.5 | 1.2985 | [paper2601] p20 Eq.(88)文本；σ=D×37.1%，本轮精确采用印出百分数 |
| PandaX US2 | 75.0 | 27.975 | [paper2601] p20 Eq.(88)文本；σ=D×37.3%，本轮精确采用印出百分数 |
| XENONnT | 10.7 | 3.9482999999999997 | [paper2601] p20 Eq.(88)文本；σ=D×36.9%，本轮精确采用印出百分数 |


实际数组：[NSI独立统计表](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json>)。旧v3.2.1舍入误差表保持原字节；本次SMχ²有相应微小区别。解析pull由Eq.(88)求导，已用独立的同时三pull线性最小二乘及Runtime逐样本统计核对。

定义 $\Delta\chi^2(\epsilon)=\chi^2(\epsilon)-\min_{\epsilon_{ee}^{uV},\epsilon_{ee}^{dV}}\chi^2$；减去联合参数最小值，不减SM值或各实验独立最小值之和。每种尾段/传播方案分别求自己的最小值。

绘图区为[-1,1]²的601×601网格，**最小化不局限图框**。利用Pee正下界、天然Xe电子散射正定二次型和US2正信号给出包围所有相关点的有限椭圆；白化后3个独立DE随机种子(17/41/83)加独立121×121网格局部多起点搜索。该包围域证明属于项目数值推导，仅在所声明近似模型内成立；不是对完整三味传播大耦合物理有效性的证明。


[全域界、所有搜索点和最小值](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/MINIMUMS.json>) · [SolarNSIJoint](<../../../../cevns_pyeft/statistics/solar_nsi.py>)

[paper2601] LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2. p19 Eq84; p20 Eqs87,88 (three independent .12 pulls, percentages); p22 Eq95 mapping and 2-parameter Delta chi2=4.61; p23 Fig4 green region。

[返回目录](#toc)

<a id="results"></a>

## 实际结果、对照与论文差异

| 位置 | (eu,ed) | raw χ² | paired/US2/X信号[events] |
|---|---|---|---|
| SM | (0,0) | 1.61275788923 | 2.487829836, 47.043419726, 11.857362687 |
| 本近似模型联合最小值 | (-17.26300151,15.67675329) | 1.11985791048 | 2.851155002, 57.840470947, 13.823525446 |


下图绿色填充是**本轮实际计算**；灰虚线才是论文PDF绿色矢量轮廓参照。论文轮廓在优化和前向扫描之后读取，仅用于比较，没有进入likelihood、效率、通量或kernel。

![](../../../../outputs/solar_b8_nsi/20261112_fig4_run2/solar_Fig4_computed_vs_paper.png)

601×601网格mask交并比=0.841565199，只是图形核对指标，不是物理精度认证。在(eu,ed)=(0,0.178)，本计算rawχ²=4.450872058、Δχ²=3.331014148<4.61，允许；原PDF绿色多边形却排除此点。

| eu=0截线 | ed边界 |
|---|---|
| paper_green_reference | -0.196241555, 0.155131256, 0.194740238, 0.546090470 |
| flat_sensitivity | -0.149455023, 0.523600119 |
| zero | -0.149959159, 0.524211182 |
| unit | -0.145890790, 0.519293268 |
| profile_bounds | -0.149959159, 0.524211182 |
| fixed_SM_propagation | -0.157592252, 0.515961197 |
| alternative_AGSS09_profile | -0.149697159, 0.523573409 |


zero/unit尾段、固定SM传播和AGSS09 profile均未恢复论文中间禁区。将所有味散射都改成电子味NSI的诊断在此点得到χ²≈21.7914，但那是另一个物理模型，**未采纳，也不能据此断言作者的代码这样实现**。当前差异原因尚未确定。

![](../../../../outputs/solar_b8_nsi/20261112_fig4_run2/solar_NSI_controls.png)

![](../../../../outputs/solar_b8_nsi/20261112_fig4_run2/solar_Pee_NSI.png)

[全部数值与限制](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/NSI_RESULTS.json>) · [差异记录](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/PAPER_COMPARISON.json>) · [原PDF参考轮廓/坐标标定](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/source_evidence/paper_fig4_green_reference.json>)

[paper2601] LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2. p19 Eq84; p20 Eqs87,88 (three independent .12 pulls, percentages); p22 Eq95 mapping and 2-parameter Delta chi2=4.61; p23 Fig4 green region。

[返回目录](#toc)

<a id="code"></a>

## Onboarding到程序及复算

| 阶段 | 物理职责 | 程序对应 |
|---|---|---|
| P01 | 三样本单bin身份与来源卡 | experiments/solar_nsi.py::load_solar_nsi；独立scoped Catalog |
| P02 | 同位素核数、曝光（只读基础输入） | experiments/solar_singlebin.py::build_targets / SingleBinPreparation |
| P03 | 绝对源强、产生区平均Pee与ρ | sources/solar_msw.py::SolarMSW / SolarDiagonalState |
| P04–P05 | ee-only Wilson系数→共享振幅/核Response/截面 | theory/li2026/ee_vector_nsi.py::nsi_point / ElectronVectorNSI |
| P06 | 三份Total效率及显式X尾假设 | experiments/solar_nsi.py::tail_epsilon；旧TotalAcceptance只读复用 |
| P07 | 实际按E、T积分，输出三信号 | experiments/solar_nsi.py::NSIExecutor.__call__ / make_prediction |
| P08 | 保留E的K，每点重算Pee | kernels/solar_nsi.py::compile_kernel / SolarNSIKernel.blocks / rebind_state |
| P09 | 三pull解析profile、联合最小值、二维面 | statistics/solar_nsi.py::SolarNSIJoint.chi2 / certified_domain / minimize |
| P10 | 收敛、Slow/Fast、来源/保护、图形差异 | run_solar_b8_nsi_benchmark.py；test_solar_nsi.py；finalize_solar_b8_nsi.py |


[solar_msw.py](<../../../../cevns_pyeft/sources/solar_msw.py>) · [ee_vector_nsi.py](<../../../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>) · [solar_nsi.py](<../../../../cevns_pyeft/experiments/solar_nsi.py>) · [solar_nsi.py](<../../../../cevns_pyeft/kernels/solar_nsi.py>) · [solar_nsi.py](<../../../../cevns_pyeft/statistics/solar_nsi.py>)

源码各模块docstring/核心函数注释标注上述职责；共享理论公式不在实验loader复制。以下是实际Runtime最小调用，注释同时指出onboarding输入：

```python
from cevns_pyeft.experiments.solar_nsi import load_solar_nsi
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point
from cevns_pyeft.experiments.runtime import compile_experiment, predict_experiment

# Source/Target/Detector：显式NSI卡 + 只读单bin表；X尾假设有独立analysis身份。
experiment = load_solar_nsi('PandaX_US2', propagation='nsi_msw', tail_mode='flat_sensitivity')
# Interaction与Source使用相同epsilon；不把SM代表态带入NSI。
point = nsi_point(0.3, -0.1)
# Prediction：E保留在kernel中；每点重算Pee，再与核Response截面收缩。
numerics = {'n_er': 801, 'n_enu': 144}
kernel = compile_experiment(experiment, numerics=numerics)
prediction = predict_experiment(experiment, parameters=point, backend='fast', kernel=kernel, numerics=numerics)
print(prediction.counts)  # events/bin，不是逐箱Ne谱
```

从Gitup01根目录复算到新目录（拒绝覆盖已有最终结果）。当前runner还从output/source_evidence读取只作比较的参考轮廓，需先显式复制，避免计算完才因缺比较文件失败：

```powershell
New-Item -ItemType Directory -Force outputs/solar_b8_nsi/repeat_new/source_evidence
Copy-Item -LiteralPath outputs/solar_b8_nsi/20261112_fig4_run2/source_evidence/paper_fig4_green_reference.json -Destination outputs/solar_b8_nsi/repeat_new/source_evidence/
python -B tools/run_solar_b8_nsi_benchmark.py --output outputs/solar_b8_nsi/repeat_new --grid 601
```

数据已经存在，不需要再次运行create-only准备器。其来源转换可读prepare_solar_b8_nsi.py；文档由build_solar_b8_nsi_onboarding.py同源生成，默认--check只读，--write仅更新本版派生说明。


[返回目录](#toc)

<a id="handoff"></a>

## 核验范围和下一步

| 能力/材料 | 当前状态 | 影响 |
|---|---|---|
| 实际太阳NSI前向与联合区域 | COMPUTED；内部数值验证通过 | 有真实计算图、参数面、最小值与代码快照；与旧单bin/多bin隔离 |
| 论文Fig.4绿色形状精确复现 | NOT_ESTABLISHED | 指定差异点与截线；需核对作者传播、散射、输入卡及统计约定，不能以贴图调参代替 |
| XENONnT约2.77–3 keV接受度 | MISSING；假设及界已算 | 限制无假设点预测；不阻断本版明确条件的区域 |
| 作者振荡/太阳模型精确卡 | 未公布/未取得 | 本版明确用固定PEANUTS示例与B16表；不能认证作者数值相同 |
| 完整三味传播/大NSI有效性 | 本版未实现 | 大耦合全域最小值属于两味近似；后续严谨大域研究需改进传播并独立复算 |
| 太阳结构原始47列表 | 二手固定分发已采用；原始等价未独立核实 | 不把转录来源冒充官网原件认证 |
| Xe124/126及核表外部认证 | 前两核MISSING，外部认证UNRESOLVED | 七核素不重归一；只主张既有本地核表约定下的计算 |
| 科学结果接受 | NOT_REVIEWED | 记录用户执行授权，不虚构结果接受或FULLY_INTEGRATED |


本轮42项太阳相关测试通过；完整旧COHERENT dataset回归在collection时被两份既有experiment.input.yaml的OS权限错误阻碍，默认与提权读取均失败。未改权限、旧数据或参考值，不将它们记为本轮PASS。164份保护基线及当前实现/缓存指纹逐项验收见[主线QA](<../../../../outputs/solar_b8_nsi/20261112_fig4_run2/QA.json>)。输入可用性、来源认证、数值通过与论文等价分别记录。

[返回目录](#toc)

<a id="references"></a>

## 标准参考文献与原件

**[R1]** LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2.

PDF p19 Sec.VI.A Eq.(84): recoil rate; PDF p20 Eqs.(87),(88): single-bin integration and independent 12% pulls。

[https://arxiv.org/abs/2601.19883v2](https://arxiv.org/abs/2601.19883v2) · [直接本地材料](<../../../references/General_CEvNS/2601.19883v2.pdf>) · 

SHA256 `e72ae8b8d7642027b9723ce9758b2477d7322c802b53cef67f561191289d90cd`。

**[R2]** BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3.

PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI。

[https://arxiv.org/abs/2407.10892v3](https://arxiv.org/abs/2407.10892v3) · [直接本地材料](<../../../references/Solar_CEvNS/2407.10892v3.pdf>) · 

SHA256 `fc5e460404919cd82debece761b724576093f8b01539b566e9acd281e9102026`。

**[R3]** APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2.

PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr。

[https://arxiv.org/abs/2408.02877v2](https://arxiv.org/abs/2408.02877v2) · [直接本地材料](<../../../references/Solar_CEvNS/2408.02877v2.pdf>) · 

SHA256 `d63e3f8ca5c868c47a0a6ffe3acc5f33ce8d3faf86de449c4c812a0c3f700776`。

**[R4]** LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025.

PDF p13 Table II: fitted yields, rounded statistical sigmas, T bounds, external SM references; p13 Eq.(E6) text flux 5.16e6; p14 Eq.(E8) shared pull, NOT adopted。

[https://arxiv.org/abs/2502.10702v2](https://arxiv.org/abs/2502.10702v2) · [直接本地材料](<../../../references/General_CEvNS/2502.10702v2.pdf>) · 

SHA256 `73e230f1380eaf5cf042fecf19b4a4525557023375dc15c0a97eade0e1dabcf7`。

**[R5]** LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024.

PDF p5 Eq.(29): flux 5.46(1+-0.12)e6; p6 Table II paired exposure 1.25 conflicts with R2 1.20; choose official R2。

[https://arxiv.org/abs/2409.04703v2](https://arxiv.org/abs/2409.04703v2) · [直接本地材料](<../../../references/General_CEvNS/2409.04703v2.pdf>) · 

SHA256 `15f239ca06ed6e4eca541a46d3facd83f9c039d5eb01023c728bea666be61c88`。

**[R6]** BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from 8B decay[J]. Physical Review C, 1996, 54: 411-422. DOI: 10.1103/PhysRevC.54.411. Official numerical spectrum[DS/OL], accessed 2026-11-06.

829 numeric rows, columns 1 and 2; normalized shape, not total flux; original rounding retained。

[https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt) · [直接本地材料](<../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/b8_bahcall1996_official.txt>) · 

SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。

**[R7]** NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06.

nine original A/mass/number-fraction rows; full nine-row mean molar mass used before selecting seven available responses。

[https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe) · [直接本地材料](<../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/xenon_natural_isotopes_nist_v2.txt>) · 

SHA256 `5fd5a0d923c969cb53bcc1267a4eb20d8f6c71e6c2da749d7199676ef361af67`。

**[R8]** CEvNS-pyEFT local resource. responses_all.json[DS]. User-selected existing nuclear-response table; external author release and conversion NOT independently certified.

Xe128,129,130,131,132,134,136; np basis ordered p,n; W=e^-2y sum a_k y^k; M,SigmaPP,SigmaP,PhiPP,PhiPT,Delta,MPhiPP,SigmaPDelta; no extra KN or spin prefactor。

[直接本地材料](<../../../../data/responses/responses_all.json>) · 

SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。

**[R9]** Project SM benchmark decision, retained from the 2411.11749v1 analysis, 2026-11-10/11[Z].

sin^2 theta_W=0.23857 retained as explicit project input; NOT claimed as a printed numeric default of 2601.19883v2。

[https://arxiv.org/abs/2411.11749v1](https://arxiv.org/abs/2411.11749v1) · 

**[R10]** BIPM. The International System of Units (SI), 9th edition[M/OL]. 2019. IAU. Julian year convention[Z].

Avogadro exact 6.02214076e23 mol^-1; year=365.25*86400 s as project unit convention; A*amu from existing shared foundation.constants。

[https://www.bipm.org/en/publications/si-brochure](https://www.bipm.org/en/publications/si-brochure) · 

**[paper2601]** LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2.

p19 Eq84; p20 Eqs87,88 (three independent .12 pulls, percentages); p22 Eq95 mapping and 2-parameter Delta chi2=4.61; p23 Fig4 green region。

[直接本地材料](<../../../references/General_CEvNS/2601.19883v2.pdf>) · 

SHA256 `e72ae8b8d7642027b9723ce9758b2477d7322c802b53cef67f561191289d90cd`。

**[propagation]** LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024.

p5 explicitly includes NSI in propagation; p10 Appendix B EqsB4-B9, two-flavor adiabatic average, theta13_m=theta13, no Earth matter. For ee-only: epsilonD_q=-cos²theta13 epsilonee_q/2, epsilonN=0; sum u+d potentials.。

[直接本地材料](<../../../references/General_CEvNS/2409.04703v2.pdf>) · 

SHA256 `15f239ca06ed6e4eca541a46d3facd83f9c039d5eb01023c728bea666be61c88`。

**[b16]** VINYOLES N, SERENELLI A M, VILLANTE F L, et al. A new generation of standard solar models[J]. Astrophysical Journal, 2017, 835: 202. DOI:10.3847/1538-4357/835/2/202. arXiv:1611.09867.

B16 GS98 / AGSS09 numerical model tables; n_e and B8 production from nudistr columns1,3,9; mass density from struct column4 (distributed as trimmed column2)。

[https://doi.org/10.3847/1538-4357/835/2/202](https://doi.org/10.3847/1538-4357/835/2/202) · 

**[peanuts]** GONZALO T E, LUCENTE M. PEANUTS: a software for the automatic computation of solar neutrino flux and its propagation within Earth[J]. European Physical Journal C, 2024, 84:119. DOI:10.1140/epjc/s10052-024-12423-3. arXiv:2303.15527.

Data/nudistr_b16_gs98.dat and agss09.dat headers/columns; peanuts/solar.py SolarModel and solar_flux_mass use normalized integral in dr, not extra r²; examples/solar_test.yaml Neutrinos gives adopted oscillation inputs。

[https://github.com/michelelucente/PEANUTS/tree/39ef11f6d10014822809da65fa60752ea21aabb6](https://github.com/michelelucente/PEANUTS/tree/39ef11f6d10014822809da65fa60752ea21aabb6) · direct pinned software distribution verified; original B16 author URL not independently fetched this run

**[magnus]** BUSTAMANTE M. Magnus: public tabulated solar model distribution[DS/OL]. Fixed Git commit, accessed2026-11-12.

src/magnus/data/solar_models/b16_gs98.dat and b16_agss09met.dat; tools/build_solar_model_tables.py. Header supplies original source URL and original SHA256.。

[https://github.com/mbustama/Magnus/tree/7eb53ef0b3e960b3b10383fef99bfe0c9110cc8f](https://github.com/mbustama/Magnus/tree/7eb53ef0b3e960b3b10383fef99bfe0c9110cc8f) · secondary transcription explicitly adopted; primary URL returned403/HTML challenge; original 47-column author-file equivalence not independently certified



[返回目录](#toc)
