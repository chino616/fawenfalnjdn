# 太阳⁸B单 bin onboarding v3.2.1：主线执行修订稿（新版本）

**2026-11-11。已接入原 Gitup01 主线并实际运行；本版与多 bin v3.1 并列，不替换它。** 原 v3.2 是可审阅规范，不能直接作为 Runtime 输入；本版补齐 paired 效率、核实 XENONnT 2024 图线并给出实际计算。主线代码接入完成不等于论文等价性或科学结果获批；XENONnT尾段仍缺数值依据，保持修订稿。

[用户原稿（保留）](<../../../../../重构/2026-11-11_SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2/SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.md>) · [单bin实际物理参数/来源](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>) · [独立统计数据](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/fitted_yields.json>) · [实际计算记录](<../../../../outputs/solar_b8_singlebin/20261111_response_run2/BENCHMARK_SUMMARY.json>) · [多bin v3.1](<../SOLAR_B8_ONBOARDING.v3.1.md>)

<a id="toc"></a>

## 目录

- [v3.2审查结论](#review)
- [两条主线流程与文件隔离](#isolation)
- [Source：通量与谱形](#source)
- [Target与原子核Response](#target)
- [Detector：总接受度](#detector)
- [Prediction：本次积分](#prediction)
- [Statistics：信号拟合量](#statistics)
- [实际标准模型结果](#results)
- [阶段与代码对应](#workflow)
- [下一步与剩余限制](#handoff)
- [标准参考文献](#references)

<a id="review"></a>

## v3.2审查结论

| 项目 | 结论与本次处理 |
|---|---|
| 物理与统计定义 | 基本正确：R1 PDF p19 Eq.(84)、p20 Eqs.(87),(88)，三个信号产额single-bin、三个独立12% pull；未采用R4共享pull。 |
| 可否直接运行 | 原稿明确DOCUMENTED_SPEC_NOT_EXECUTED；普通YAML不是正式三文件Package。现由独立JSON card及显式loader接入标准Runtime。 |
| PandaX paired | 原稿MISSING已更新：R2 PDF p3 Fig.1黑实线原生矢量，52×2；曝光采用原实验1.20 t·yr，R5 Table II的1.25保留冲突。 |
| PandaX US2 | 99×2总效率独立重提取；0.3–3积分，不再裁平均Ne=4–8；旧25.86不能当新单bin预测。 |
| XENONnT | 原稿“未提供”已过时：R3 v2 Fig.1原生黑线40点已取得；仅到约2.77，末段到3仍缺。旧三箱基底相加不替代该效率。 |
| 通量 | 5.46e6来自R5 Eq.(29)，是R1所引资料下的显式选择；R1未重印此数。R4的5.16e6与SM参考值只作外部比较。 |
| 误差与阶段 | 采用原稿指定R4 Table II取整误差1.3/28/3.95；与R1印出的37.1%/37.3%/36.9%有舍入差异。Statistics属P09，P08属Fast。 |
| 链接与版本 | 新版本修正原稿相对v3.1失效链接；旧原稿、原多bin数据/模型/冻结结果保持原字节。 |


[返回目录](#toc)

<a id="isolation"></a>

## 两条主线流程与文件隔离

| 层 | 多 bin：既有方案 | 单 bin：本次方案 |
|---|---|---|
| 物理目标 | 2411.11749v1 Fig.1类型的Ne/cS2谱 | 2601.19883v2 Eq.87总信号、Eq.88近似χ² |
| 实验输入 | [原PandaX Package](<../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/README.md>) / [原XENON Package](<../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/README.md>) | [独立单bin目录](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/README.md>) |
| 探测器处理 | PandaX Qy平均映射8箱；XENONnT早期YBe接受概率3箱 | 真反冲T×Total效率积分；paired/US2/X三个独立样本 |
| 数据语义 | 逐箱候选D_i、背景B_i作为谱比较资料 | 3.5±1.3、75±28、10.7±3.95：实验拟合信号；无显式背景项 |
| 计算模块 | [solar_nuclear](<../../../../cevns_pyeft/experiments/solar_nuclear.py>) + solar_mean_map/solar_b8 | [solar_singlebin](<../../../../cevns_pyeft/experiments/solar_singlebin.py>) |
| 入口 | [run_solar_b8_multibin_benchmark.py](<../../../../tools/run_solar_b8_multibin_benchmark.py>) | [run_solar_b8_singlebin_benchmark.py](<../../../../tools/run_solar_b8_singlebin_benchmark.py>) |
| 结果根 | [outputs/solar_b8_sm/](<../../../../outputs/solar_b8_sm/README.md>) | [outputs/solar_b8_singlebin/](<../../../../outputs/solar_b8_singlebin/README.md>) |


只共享实验无关的核表、SM匹配/粒子响应/截面及通用Runtime。单bin不导入旧solar_b8、solar_mean_map、solar_nuclear，不读取旧NPZ、Qy、逐箱D/B，不加载旧Fast缓存。资源allowlist、analysis/dataset/observation指纹及维度检查拒绝交叉统计。兼容旧入口不带analysis仍走历史多bin；新任务使用上表明确入口。

[返回目录](#toc)

<a id="source"></a>

## Source：通量与谱形

定义 $d\phi/dE_\nu=\Phi_{8B} f_{8B}(E_\nu)$。谱形与总通量各乘一次；采用单位迹的味等价入射态，SM味普适，不乘额外三倍，不需要逐味MSW表。此处定义对应R1 Eq.(84)，谱形数据来自R6，通量选择来自R5。

| 输入 | 实际数值/数组 | 单位 | 数值文件与直接出处 | 核验范围 |
|---|---|---|---|---|
| 总通量 | 5.46×10⁶ | cm⁻² s⁻¹ | [physics.flux](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)；[R5] PDF p5 Eq.(29) | 核对原式；未按拟合结果调整 |
| 谱形 | 829×2；E=0–16.56；梯形积分=0.999986544 | MeV, MeV⁻¹ | [源谱](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt>)；[R6] 官网b8spectrum前两列 | 原829点提取；保留原精度，不再归一 |
| 插值与边界 | 分段线性；表外0；积分含原谱节点 | — | [R6]网格 + 项目数值选择；SourceSpectrum及rates.recoil | 显式来源/支撑及网格加密检验 |
| 弱混合角 | sin²θW=0.23857 | 1 | [physics.sin2thetaW](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)；[R9]沿用项目SM点 | 明确项目输入，不冒称R1印出的默认值 |
| 时间换算 | 31557600=365.25×86400 | s/yr | [R10] Julian年单位约定 | 仅作单位换算；曝光未再乘独立活时间 |


[R6] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from 8B decay[J]. Physical Review C, 1996, 54: 411-422. DOI: 10.1103/PhysRevC.54.411. Official numerical spectrum[DS/OL], accessed 2026-11-06.

[R5] LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024. PDF p5 Eq.(29)。

[返回目录](#toc)

<a id="target"></a>

## Target与原子核Response

核数由 $n_A^{(1t)}=10^6 N_A\eta_A/\sum_B\eta_Bm_B^{\rm atom}$ 推导；分母使用完整九行，质量单位g/mol。输入来自[R7]；代数换算位于build_targets。振幅与运动学统一采用 $m_A=A\,m_u$；核数仍用原子质量。 九行平均摩尔质量=131.292761448 g/mol；可用七核素原数丰度99.8158%，保留缺失的0.1842%。

| 核素 | 数丰度 | 原子质量u | 每吨核数（推导） | 核响应可用性 |
|---|---|---|---|---|
| Xe124 | 0.000952 | 123.905892 | 4.36663677e+24 | MISSING：不计、不补KN、不重归一 |
| Xe126 | 0.00089 | 125.9042983 | 4.08225497e+24 | MISSING：不计、不补KN、不重归一 |
| Xe128 | 0.019102 | 127.903531 | 8.76171173e+25 | 已读核表 |
| Xe129 | 0.264006 | 128.904780861 | 1.2109436e+27 | 已读核表 |
| Xe130 | 0.04071 | 129.903509349 | 1.86728764e+26 | 已读核表 |
| Xe131 | 0.212324 | 130.90508406 | 9.73888431e+26 | 已读核表 |
| Xe132 | 0.269086 | 131.904155086 | 1.23424456e+27 | 已读核表 |
| Xe134 | 0.104357 | 133.90539466 | 4.78665036e+26 | 已读核表 |
| Xe136 | 0.088573 | 135.907214484 | 4.06266932e+26 | 已读核表 |


[完整9×3 NIST输入](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xe_isotopes.txt>)；[R7] NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06.

| key | J | b [GeV⁻¹] | M数组shape | M的pp,pn,nn常数项 |
|---|---|---|---|---|
| Xe128 | 0 | 11.5792987 | [2, 2, 11] | 2915.83781, 3995.65033, 5475.34622 |
| Xe129 | 0.5 | 11.5924668 | [2, 2, 11] | 2915.96165, 4049.60832, 5623.98602 |
| Xe130 | 0 | 11.6055534 | [2, 2, 11] | 2915.85322, 4103.52768, 5774.96127 |
| Xe131 | 1.5 | 11.6185595 | [2, 2, 11] | 2915.97733, 4157.70328, 5928.19993 |
| Xe132 | 0 | 11.6314864 | [2, 2, 11] | 2915.99213, 4211.83965, 6083.55319 |
| Xe134 | 0 | 11.6571063 | [2, 2, 11] | 2915.95906, 4319.24197, 6397.84401 |
| Xe136 | 0 | 11.6824215 | [2, 2, 11] | 2915.99793, 4427.99393, 6723.98634 |


核表实际文件：[responses_all.json](<../../../../data/responses/responses_all.json>)，SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。采用已有ResponseDB/Li2026的np基底(p,n)和多项式约定，全部已实现通道进入SM振幅；不乘KN/Helm/额外自旋因子。共享理论公式只在原理论模块维护，本分析通过[SMQuadraticInteraction](<../../../../cevns_pyeft/theory/li2026/sm_quadratic.py>)委托[Li2026LegacyInteraction](<../../../../cevns_pyeft/theory/li2026/adapter.py>)，仅做精确能量二次式向量化。

[R8] CEvNS-pyEFT local resource. responses_all.json[DS]. User-selected existing nuclear-response table; external author release and conversion NOT independently certified. **本地数值可用、直接采用获授权；外部原始作者版本和转换认证仍UNRESOLVED。** 此限制不被内部格式/收敛PASS消除。

[返回目录](#toc)

<a id="detector"></a>

## Detector：总接受度

| 样本 | shape | 表内T [keVnr] | 首/末ε [1] | 数值文件 | 直接原文定位 |
|---|---|---|---|---|---|
| PandaX_paired | [52, 2] | 1.1–3 | 0.0108296334 / 0.0738275713 | [pandax_paired_total.txt](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_paired_total.txt>) | R2 PDF p3 Fig.1 Total paired; official exposure 1.20, not R5 1.25; T bounds R4 Table II |
| PandaX_US2 | [99, 2] | 0.3–3 | 0.00579130472 / 0.0155469009 | [pandax_us2_total.txt](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_us2_total.txt>) | R2 PDF p3 Fig.1 Total US2 and exposure; T bounds R4 Table II; no extra Qy/Ne window |
| XENONnT | [40, 3] | 0.429999996183–2.77000000181 | 0.000111966578 / 0.123987529 | [xenonnt_combined.txt](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xenonnt_combined.txt>) | R3 PDF p4 Fig.1 black combined; exposure R3 3.51; bounds R4 Table II |


PandaX两线由[R2] PDF p3 Fig.1原生矢量重新提取，横轴线性/纵轴log；图边界交点在原PDF坐标求出，数值文件端点明确为0.3/1.1/3。转为数值后分段线性插值ε(T)，是一项项目数值选择；独立提取的US2 99点与旧原表在其写入精度内一致。Total已含ROI、选择和重建，均只施加一次。

XENONnT用[R3] **2408.02877v2 PDF p4 Fig.1黑色combined**，40×3第三列保留可见标记；低能几段在图框下裁掉，但原生PDF数值路径存在，不能称其为可见曲线逐点核实。末点约2.77 keV，**2.77–3 keV的ε(T)=MISSING**。主结果积分到末点并以0≤ε≤1给未知尾段的严格区间；不静默延伸。平坦延伸仅为单列的项目敏感性估计。

这里的Detector接受度不是原子核Response W，也不是完整重建概率矩阵。按本单bin目标只需总效率；Qy、二维S1/S2 kernel及逐箱迁移不属于这条简化积分的输入。

[R2] BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3.

[R3] APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2.

[返回目录](#toc)

<a id="prediction"></a>

## Prediction：本次积分

采用[R1] PDF p19 Eq.(84)、p20 Eq.(87)，将曝光显式移出通量，并按核素求和：

$$
S_k=\mathcal E_k\sum_A n_A^{(1t)}\,t_{\rm yr}
\int_{T_{\min,k}}^{T_{\max,k}}dT\,\epsilon_k(T)
\int_{E_{\min,A}(T)}^{E_{\max}}dE_\nu\,
\Phi_{8B}f_{8B}(E_\nu)\frac{d\sigma_A^{\rm SM}}{dT}.
$$

这里 $\mathcal E_k$ 数值单位t·yr，$n_A^{(1t)}$ 是每吨核数，$t_{\rm yr}$ 是s/yr；其余单位依次keV、MeV、cm⁻²s⁻¹MeV⁻¹、cm²/keV，结果为事件。$E_{\min,A}$、截面与核质量均由共享接口提供。本式的显式曝光和核素求和是对R1写法的单位展开，不新增物理归一化。

| 样本 | T积分 [keVnr] | 曝光 [t·yr] | 直接出处与选择 |
|---|---|---|---|
| PandaX_paired | [1.1, 3.0] | 1.2 | R2 PDF p3 Fig.1 Total paired; official exposure 1.20, not R5 1.25; T bounds R4 Table II |
| PandaX_US2 | [0.3, 3.0] | 1.04 | R2 PDF p3 Fig.1 Total US2 and exposure; T bounds R4 Table II; no extra Qy/Ne window |
| XENONnT | [0.5, 3.0] | 3.51 | R3 PDF p4 Fig.1 black combined; exposure R3 3.51; bounds R4 Table II |


未知XENONnT尾段满足下式。两端来自本次未加效率反冲谱积分，是数值推导的界，不是对缺失实验数据的猜测：

$$
S_{\rm known}\le S_{\rm full}\le S_{\rm known}+\mathcal E\sum_A n_A^{(1t)}t_{\rm yr}\int_{T_*}^{3\,\mathrm{keV}}dT\int dE_\nu\,\Phi f\,d\sigma_A/dT.
$$

执行顺序：源谱×截面 → 每核反冲率 → 原核数 → 总接受度 → 曝光 → 单信号计数。无 $c_i$，无拟合信号标定，无额外ROI窗，无源通量重拟合。每一数值输出都记录实际资源、实现哈希及Runtime物理/analysis指纹。


[返回目录](#toc)

<a id="statistics"></a>

## Statistics：信号拟合量

使用[R1] PDF p20 Eq.(88)：

$$
\chi^2=\sum_k\min_{a_k}\left\{\frac{[D_k-(1+a_k)S_k]^2}{\sigma_k^2}+\frac{a_k^2}{0.12^2}\right\}.
$$

$D_k$是实验多维拟合获得的**信号产额**；$\sigma_k$是其统计误差，非原始候选的Poisson误差；每个样本独立一个归一化pull。背景已在实验信号提取中处理，不能再加一次背景项或将3.5等信号量当原始Poisson计数。

| 样本 | D [events] | σstat [events] | σa [1] | 原文位置 |
|---|---|---|---|---|
| PandaX_paired | 3.5 | 1.3 | 0.12 | R2 abstract; R4 Table II |
| PandaX_US2 | 75.0 | 28.0 | 0.12 | R2 abstract; R4 Table II |
| XENONnT | 10.7 | 3.95 | 0.12 | R3 Table I: asymmetric -4.2/+3.7 averaged; R4 Table II |


具体数据文件为[fitted_yields.json](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/fitted_yields.json>)。原稿使用[R4] PDF p13 Table II的取整误差；[R1]印出的paired/US2/X百分数37.1%/37.3%/36.9%分别给1.2985/27.975/3.9483事例，差别仅舍入，当前仍明确沿用原稿1.3/28/3.95。

解析profile由对Eq.(88)求导得到，非另一个外部输入：

$$
a_* = \frac{0.12^2 S(D-S)}{\sigma^2+0.12^2 S^2},\qquad
\chi^2_{\rm prof}=\frac{(D-S)^2}{\sigma^2+0.12^2S^2}.
$$

程序独立数值最小化检验此解析式。未作参数扫描、最佳拟合搜索或置信区间。XENONnT部分积分由统计器拒绝作为完整点预测；只计算缺失尾数据导致的χ²范围。使用平坦延伸时，analysis身份与物理指纹独立变化，结果明确为项目假设。


[R1] LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2.

[R4] LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025. 原文Table II与Eq.(E8)分别核对；共享pull未采用。

[返回目录](#toc)

<a id="results"></a>

## 实际标准模型结果

| 样本 | SM信号 [events] | 实验拟合信号 [events] | profile χ² | 性质 |
|---|---|---|---|---|
| PandaX_paired | 2.487612254 | 3.5 ± 1.3 | 0.576090731 | complete_integral |
| PandaX_US2 | 47.042059756 | 75 ± 28 | 0.958056701 | complete_integral |
| XENONnT | 11.812101957–12.169955057 | 10.7 ± 3.95 | 部分积分禁入完整χ² | partial_integral_and_rigorous_tail_bounds |


XENONnT平坦尾段敏感性：末点ε=0.123987528765，完整假设积分=11.856471279，χ²=0.0758745967。**此点采用项目平坦尾假设，不是官方数据。** 三样本固定SM点χ²的严格范围为[1.604371930890435, 1.6559820592253394]；由于缺尾数据，主记录`joint_chi2=null`，没有宣称完整点χ²。采用平坦尾假设时总χ²=1.61002203。

三样本各做反冲201→401→801、随后中微子120→480的独立加密；保留源谱与效率原节点。收敛检查同时覆盖信号计数和区间两端，要求max(2e−4 events,0.2%)；不是论文等价性检查。原子核表读取、截面委托、分核素求和、独立曝光及所有实施版本均见[完整结果](<../../../../outputs/solar_b8_singlebin/20261111_response_run2/BENCHMARK_SUMMARY.json>)。

[R4] Table II在5.16e6通量下列2.4/44.3/11.2，且采用自己的核物理与共享pull；它们仅是外部比较量，未作为校准、源重缩放或程序参考数组。

![](<../../../../outputs/solar_b8_singlebin/20261111_response_run2/singlebin_SM_comparison.png>)

黑点为实验拟合信号及所采用统计误差；蓝点为独立SM积分；X蓝竖段为未知尾段区间；紫空心点仅为平坦尾段敏感性。

![](<../../../../outputs/solar_b8_singlebin/20261111_response_run2/singlebin_recoil_diagnostics.png>)

反冲密度是积分诊断，不是重建Ne/cS2直方图。

[返回目录](#toc)

<a id="workflow"></a>

## 阶段与代码对应

| 阶段 | 物理职责 | 程序中位置/原文 |
|---|---|---|
| P01 | sample/analysis/observation分离 | load_singlebin；独立scoped catalog，不改全局默认IDs |
| P02 | 天然Xe、核数、曝光 | build_targets；SingleBinPreparation；R2/R3/R7 |
| P03 | 源谱与绝对通量 | SourceSpectrum；UniversalState；R5/R6 |
| P04–P05 | 原子核W→振幅→截面 | SMQuadraticInteraction委托Li2026LegacyInteraction；无KN主预测 |
| P06 | 只采用总ROI效率 | TotalAcceptance；不读取Qy/迁移/旧basis |
| P07 | 重新计算单bin信号 | SingleBinExecutor → rates.recoil.integrate_recoil_yield |
| P08 | Fast未申请 | NOT_REQUESTED；不导入旧cache |
| P09 | 独立拟合信号Gaussian | statistics.solar_singlebin.profile/evaluate；Runtime.evaluate_experiment |
| P10 | 来源、隔离、收敛、回归 | test_solar_singlebin；科学接受NOT_REVIEWED，缺尾/外部认证保持可见 |


实际源码：[source/target/detector/executor/loader（含onboarding注释）](<../../../../cevns_pyeft/experiments/solar_singlebin.py>) · [单bin统计](<../../../../cevns_pyeft/statistics/solar_singlebin.py>) · [核Response截面委托](<../../../../cevns_pyeft/theory/li2026/sm_quadratic.py>) · [隔离与数值检验](<../../../../tests/test_solar_singlebin.py>)。

从Gitup01根目录分别运行（新输出目录，禁止覆盖）：

```powershell
python -B tools/run_solar_b8_singlebin_benchmark.py --output outputs/solar_b8_singlebin/repeat_new
python -B tools/run_solar_b8_multibin_benchmark.py --output outputs/solar_b8_sm/multibin_repeat_new
```

兼容路由可用`run_solar_b8_sm_benchmark.py --analysis singlebin ...`或`--analysis multibin ...`。两者各自的入口、实验输入、统计量、输出和指纹仍完全分离。

[返回目录](#toc)

<a id="handoff"></a>

## 下一步与剩余限制

| 项目 | 状态 | 影响与下一步 |
|---|---|---|
| 主线SM单bin计算 | 已执行 | PandaX两通道完整；XENONnT有严谨范围与单列的尾段假设敏感性 |
| XENONnT约2.77–3 keV接受度 | MISSING | 取得2024黑combined曲线完整数值或有依据的低能模型；仅阻断无假设的完整点预测/完整联合χ² |
| Xe124/Xe126核响应 | MISSING | 七核素结果不重归一；若需100%天然Xe，补独立核表，不以KN替代 |
| 已有核表外部认证 | UNRESOLVED | 按用户选择采用本地表；不阻断本地计算，但不能宣称外部原始发布与转换等价已认证 |
| 官方全响应/官方likelihood | 本次未请求 | 本方法是R1单bin近似，不替代原实验多维likelihood或旧多bin研究 |
| 科学结果接受 | NOT_REVIEWED | 机器PASS只证明已记录的检验；未标FULLY_INTEGRATED/论文精确复现 |


原稿与旧多bin保护哈希：[PROTECTED_BASELINE](<../../../../../重构/2026-11-11_SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2/_review/PROTECTED_BASELINE.json>)；逐文件归属与实测验收：[验证记录](<../../../../outputs/solar_b8_singlebin/20261111_validation/README.md>)。

[返回目录](#toc)

<a id="references"></a>

## 标准参考文献

**[R1]** LI G, SONG C Q, TANG F J, et al. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[J]. Physical Review D, 2026, 114: 055032. arXiv:2601.19883v2.

[https://arxiv.org/abs/2601.19883v2](https://arxiv.org/abs/2601.19883v2) · [本地原件](<../../../references/General_CEvNS/2601.19883v2.pdf>) · PDF p19 Sec.VI.A Eq.(84): recoil rate; PDF p20 Eqs.(87),(88): single-bin integration and independent 12% pulls。

SHA256 `e72ae8b8d7642027b9723ce9758b2477d7322c802b53cef67f561191289d90cd`。

**[R2]** BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3.

[https://arxiv.org/abs/2407.10892v3](https://arxiv.org/abs/2407.10892v3) · [本地原件](<../../../references/Solar_CEvNS/2407.10892v3.pdf>) · PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI。

SHA256 `fc5e460404919cd82debece761b724576093f8b01539b566e9acd281e9102026`。

**[R3]** APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2.

[https://arxiv.org/abs/2408.02877v2](https://arxiv.org/abs/2408.02877v2) · [本地原件](<../../../references/Solar_CEvNS/2408.02877v2.pdf>) · PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr。

SHA256 `d63e3f8ca5c868c47a0a6ffe3acc5f33ce8d3faf86de449c4c812a0c3f700776`。

**[R4]** LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025.

[https://arxiv.org/abs/2502.10702v2](https://arxiv.org/abs/2502.10702v2) · [本地原件](<../../../references/General_CEvNS/2502.10702v2.pdf>) · PDF p13 Table II: fitted yields, rounded statistical sigmas, T bounds, external SM references; p13 Eq.(E6) text flux 5.16e6; p14 Eq.(E8) shared pull, NOT adopted。

SHA256 `73e230f1380eaf5cf042fecf19b4a4525557023375dc15c0a97eade0e1dabcf7`。

**[R5]** LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024.

[https://arxiv.org/abs/2409.04703v2](https://arxiv.org/abs/2409.04703v2) · [本地原件](<../../../references/General_CEvNS/2409.04703v2.pdf>) · PDF p5 Eq.(29): flux 5.46(1+-0.12)e6; p6 Table II paired exposure 1.25 conflicts with R2 1.20; choose official R2。

SHA256 `15f239ca06ed6e4eca541a46d3facd83f9c039d5eb01023c728bea666be61c88`。

**[R6]** BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from 8B decay[J]. Physical Review C, 1996, 54: 411-422. DOI: 10.1103/PhysRevC.54.411. Official numerical spectrum[DS/OL], accessed 2026-11-06.

[https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt) · [直接采用的本地原表](<../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/b8_bahcall1996_official.txt>) · 829 numeric rows, columns 1 and 2; normalized shape, not total flux; original rounding retained。

SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。

**[R7]** NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06.

[https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe) · [直接采用的本地原表](<../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/xenon_natural_isotopes_nist_v2.txt>) · nine original A/mass/number-fraction rows; full nine-row mean molar mass used before selecting seven available responses。

SHA256 `5fd5a0d923c969cb53bcc1267a4eb20d8f6c71e6c2da749d7199676ef361af67`。

**[R8]** CEvNS-pyEFT local resource. responses_all.json[DS]. User-selected existing nuclear-response table; external author release and conversion NOT independently certified.

[本地原件](<../../../../data/responses/responses_all.json>) · Xe128,129,130,131,132,134,136; np basis ordered p,n; W=e^-2y sum a_k y^k; M,SigmaPP,SigmaP,PhiPP,PhiPT,Delta,MPhiPP,SigmaPDelta; no extra KN or spin prefactor。

SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。

**[R9]** Project SM benchmark decision, retained from the 2411.11749v1 analysis, 2026-11-10/11[Z].

[https://arxiv.org/abs/2411.11749v1](https://arxiv.org/abs/2411.11749v1) · sin^2 theta_W=0.23857 retained as explicit project input; NOT claimed as a printed numeric default of 2601.19883v2。

**[R10]** BIPM. The International System of Units (SI), 9th edition[M/OL]. 2019. IAU. Julian year convention[Z].

[https://www.bipm.org/en/publications/si-brochure](https://www.bipm.org/en/publications/si-brochure) · Avogadro exact 6.02214076e23 mol^-1; year=365.25*86400 s as project unit convention; A*amu from existing shared foundation.constants。



[返回目录](#toc)
