# 太阳⁸B SNuDD完整统计与论文比较 v3.4.1（新版本）

**2026-11-12。完整计算结果版：已计算三样本联合最小值、601×601二维面及90%区域。2601.19883v2 Fig.4绿色区域的精确复现未通过；科学接受NOT_REVIEWED。** 旧v3.4五点接入结果、v3.3本地传播、v3.2.1 SM、多bin与V/B−L均保留。

[固定来源/参数卡](<../../../../extensions/solar_rho_snudd/snudd.input.json>) · [完整计算结果](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json>) · [数值文件和图](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/README.md>) · [旧v3.4接入读本](<SNUDD_EXTERNAL_ONBOARDING.v3.4.md>)

<a id="toc"></a>

## 目录

- [结果与范围](#status)
- [Source：通量、振荡和实际传播数据](#source)
- [Target与核振幅Response](#nuclear)
- [Detector与单bin数据](#detector)
- [事例数：各阶段实际计算](#prediction)
- [Statistics：三个独立pull与联合最小值](#statistics)
- [与论文Fig.4的定量比较](#comparison)
- [尾段和传播对照](#controls)
- [验收、主线入口与复算](#validation)
- [仍未闭合的论文等价条件](#gaps)
- [标准文献与原件](#references)

<a id="status"></a>

## 结果与范围

| 量 | 本次实际结果 | 解释/依据 |
|---|---|---|
| SM三信号[events] | 2.487830, 47.043420, 11.857363 | paired、US2、XENONnT；原核Response和Total接受度 |
| SM联合χ² | 1.6127578892 | 式(88)三个独立12%pull的解析profile |
| 联合χ²min | 1.1198509051 | 声明的近似数学模型内全域搜索；(eu,ed)=(-17.26210630,15.67596277) |
| SM的Δχ² | 0.4929069841 | 小于4.61，SM在所用二维90%区域内；不据此宣称NSI发现 |
| 论文图区域交并比 | 84.203255% | 只在[-1,1]²和601²网格比较；不是拟合优度或复现通过率 |
| 核Response/探测器Response | 核W和原振幅计算；探测器使用单bin Total接受度 | 本分支无Ne/S2迁移矩阵、无ci校准；不是多bin谱 |


仅重新计算Fig.4的绿色太阳联合区域；橙色CONUS+与蓝色COHERENT本轮未重算，不列作本轮复现成果。[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维阈值；p23 Fig.4绿色区域 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[返回目录](#toc)

<a id="source"></a>

## Source：通量、振荡和实际传播数据

入射源是地球处所有活跃味的总⁸B通量，谱形与绝对强度分开：

$$
\frac{d\phi_{\rm total}}{dE_\nu}=\Phi_{8B}f_{8B}(E_\nu),\qquad
\frac{d\phi_\alpha}{dE_\nu}=\Phi_{8B}f_{8B}(E_\nu)\rho_{\alpha\alpha}(E_\nu;eu,ed).
$$

这是总通量和密度矩阵的定义；总通量不随NSI自由缩放。传播改变各味组成；本轮仍用固定5.46×10⁶。统计的12%先验只作用在式(88)的各样本信号项，不能冒称另取了一个标准太阳模型通量。

| 输入 | 实际数值/数组、单位 | 数值文件与具体依据/核验范围 |
|---|---|---|
| 总通量 | 5.46×10⁶ cm⁻²s⁻¹ | [只读基础卡](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)；[R5] p5 Eq.(29)，本项目沿用选择；未称为2601作者原始卡 |
| 谱形 | 829×2；E=0–16.56 MeV；原网格积分=0.999986544；首/末(0,0)/(16.56,0) | [原Bahcall表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt>)；[R6]官网829行第1/2列；单位MeV、MeV⁻¹；保留原舍入，线性插值，不额外归一 |
| 密度 | log10(ne/NA)=2.36−4.52x−0.33exp[−(x/0.075)^1.1]；log10(nn/NA)=1.72−4.80x；mol/cm³ | [实际函数](<../../../../.externals/SNuDD/snudd/nsi/solar_profiles.py>)；[S_density]直接采用软件拟合；未独立认证原论文每个拟合系数 |
| 产生位置 | [96, 2]；x=r/Rsun，0–0.17；首/末(0,0)/(.17,0)；max=18.3642858 | [96×2原表](<../../../../.externals/SNuDD/snudd/data/flux_distributions/8B_dist.txt>)；[S_production]表头指向1302.2791；软件线性插值，域外0，按dr归一、不加r² |
| 振荡前三项 | θ12=0.583638rad，θ13=0.149575rad，Δm21²=7.42e-05 eV² | [实际显式传入值](<../../../../extensions/solar_rho_snudd/snudd.input.json>)；沿用v3.3固定PEANUTS示例的项目选择；[固定示例原件](<../../../../outputs/solar_b8_nsi/20261112_fig4_run1/source_evidence/peanuts_examples_solar_test.yaml>) |
| 其余参数 | θ23=43.3°，δCP=212°，Δm31²=2.513×10⁻³ eV² | [osc_params_best](<../../../../.externals/SNuDD/snudd/nsi/oscillation.py>)；[S_remaining_oscillation]固定软件默认；Δ31用于适用性诊断，μτ分配不影响ee-only事例数 |
| 传播数值源 | 1000径向节点，其中485非零权重；144个正式E节点；完整rho可重建 | [1000节点数值源](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/propagation_source/source.npz>) / [原件hash/实际参数](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/propagation_source/manifest.json>)；[S_software]完全相同求积，不用概率插值或缩减非零节点 |


传播采用SNuDD有效两味绝热模型并平均质量相位；输出为三维味密度矩阵，**不是完整三味微分方程演化**，不含地球再生。令eu=εee_uV、ed=εee_dV，εp=2eu+ed、εn=eu+2ed，则电子物质势为√2GF·ne[1+εp+(nn/ne)εn]；1是SM，ε只传新物理部分。映射依据[S_nsi_mapping]实际GeneralNSI的ξp、ξn。

扫描只把同一模型的ee-only代数式编译执行；不修改上游或Runtime：每个E、每个耦合点都在原1000点求积。完整ρ=U diag(c13²(1+〈cos2θm〉)/2,c13²(1−〈cos2θm〉)/2,s13²)U†。5个点的完整矩阵已与独立SNuDD进程核对，差异见验收。


[R5] LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024. PDF p5 Eq.(29): flux 5.46(1+-0.12)e6; p6 Table II paired exposure 1.25 conflicts with R2 1.20; choose official R2 [原始网址](https://arxiv.org/abs/2409.04703v2)。

[R6] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from 8B decay[J]. Physical Review C, 1996, 54: 411-422. DOI: 10.1103/PhysRevC.54.411. Official numerical spectrum[DS/OL], accessed 2026-11-06. 829 numeric rows, columns 1 and 2; normalized shape, not total flux; original rounding retained [原始网址](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)。

[S_software] AMARAL D W P, CERDEÑO D, CHEEK A, COSTA V, FOLDENAUER P. SNuDD: Solar Neutrinos for Direct Detection[EB/OL]. arXiv:2607.22817v1, 2026. SolarDensityMatrixCalculator.density_mass/density; ProbabilityCalculator._cos_matter_average; direct adopted software, effective two-flavor and mass-decohered flavor reconstruction [原始网址](https://arxiv.org/abs/2607.22817v1)。

[S_density] BAHCALL J N, SERENELLI A M, BASU S. 10,000 Standard Solar Models: a Monte Carlo Simulation[J]. Astrophysical Journal Supplement, 2006,165:400-431. DOI:10.1086/504043. arXiv:astro-ph/0511337. log10_electron_density, log10_neutron_electron_density; e1..e5,n1,n2; adopted software fits, not B16 arrays [原始网址](https://arxiv.org/abs/astro-ph/0511337)。

[S_production] LOPES I, TURCK-CHIÈZE S. Solar neutrino physics oscillations: Sensitivity to the electronic density in the Sun’s core[J]. Astrophysical Journal,2013,765:14. DOI:10.1088/0004-637X/765/1/14. arXiv:1302.2791. raw two-column file header identifies1302.2791; flux_dists.interpolate_dist linear, outside0; native distribution normalized in dr over0-.35 by propagation code [原始网址](https://arxiv.org/abs/1302.2791v1)。

[S_nsi_mapping] SNuDD Collaboration. GeneralNSI model source[CP/OL]. Fixed Git commit 11622ded104994959a649d85e263c2d9f933ea74, accessed2026-11-12. GeneralNSI.xi_p/xi_n/xi_u/xi_d/xi_e; model eps_matrix multiplies each xi, phi=0 [原始网址](https://github.com/SNuDD/SNuDD/blob/11622ded104994959a649d85e263c2d9f933ea74/snudd/models.py)。

[S_remaining_oscillation] ESTEBAN I, GONZALEZ-GARCIA M C, MALTONI M, et al. NuFit-6.0: Updated global analysis of three-flavor neutrino oscillations[J]. JHEP,2024,12:216. DOI:10.1007/JHEP12(2024)216. arXiv:2410.05380. osc_params_best; explicit theta23=43.3deg,delta=212deg,dm31=2.513e-3eV² retained; theta12/13/dm21 overridden from v3.3 project card [原始网址](https://arxiv.org/abs/2410.05380)。

[返回目录](#toc)

<a id="nuclear"></a>

## Target与核振幅Response

| 输入 | 实际值/处理 | 直接来源与范围 |
|---|---|---|
| Xe丰度/质量 | 9×3：A=124–136、原子质量[u]、数丰度[1]；首行124,123.905892,.000952 | [原9行表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xe_isotopes.txt>)；[R7] NIST官网；核数分母用全部9行，再选择7个可用核表 |
| 靶核数与核质量 | N_A×10⁶[g]/平均摩尔质量[g/mol]×原数丰度；截面核质量A·amu | [build_targets](<../../../../cevns_pyeft/experiments/solar_singlebin.py>)；[R10]单位转换，原算法直接沿用 |
| 核W与振幅 | basis=(p,n)，y=(qb/2)²；W=e⁻²ʸΣa_k y^k；b单位GeV⁻¹ | [实际完整核表](<../../../../data/responses/responses_all.json>)；[R8]用户指定本地表及既有读取约定；外部作者表认证未闭合 |
| NSI匹配 | C61q_NP=−√2GF·εee_qV [GeV⁻²]；SM也由原共享LEFT振幅计算 | [ElectronVectorNSI](<../../../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>)；[R1] p22 Eq.(95)；不追加KN或自旋归一化因子 |


实际M系数四个位置依次pp,pn,np,nn；系数长度代表shape=(2,2,对应长度)。其他原核通道仍由原振幅读取。

| 核素 | J | b[GeV⁻¹] | M四多项式长度 | a0(pp,pn,np,nn) |
|---|---|---|---|---|
| Xe128 | 0 | 11.5792987 | [11, 11, 11, 11] | 2915.83781, 3995.65033, 3995.65033, 5475.34622 |
| Xe129 | 0.5 | 11.5924668 | [11, 11, 11, 11] | 2915.96165, 4049.60832, 4049.60832, 5623.98602 |
| Xe130 | 0 | 11.6055534 | [11, 11, 11, 11] | 2915.85322, 4103.52768, 4103.52768, 5774.96127 |
| Xe131 | 1.5 | 11.6185595 | [11, 11, 11, 11] | 2915.97733, 4157.70328, 4157.70328, 5928.19993 |
| Xe132 | 0 | 11.6314864 | [11, 11, 11, 11] | 2915.99213, 4211.83965, 4211.83965, 6083.55319 |
| Xe134 | 0 | 11.6571063 | [11, 11, 11, 11] | 2915.95906, 4319.24197, 4319.24197, 6397.84401 |
| Xe136 | 0 | 11.6824215 | [11, 11, 11, 11] | 2915.99793, 4427.99393, 4427.99393, 6723.98634 |


七核素原数丰度合计0.998158；未补Xe124/126、未重归一。这里认证本地数值存在、读取约定和本轮复用不变；不把格式名视为已认证外部作者来源。[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维阈值；p23 Fig.4绿色区域 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[R7] NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06. nine original A/mass/number-fraction rows; full nine-row mean molar mass used before selecting seven available responses [原始网址](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe)。

[R8] CEvNS-pyEFT local resource. responses_all.json[DS]. User-selected existing nuclear-response table; external author release and conversion NOT independently certified. Xe128,129,130,131,132,134,136; np basis ordered p,n; W=e^-2y sum a_k y^k; M,SigmaPP,SigmaP,PhiPP,PhiPT,Delta,MPhiPP,SigmaPDelta; no extra KN or spin prefactor 

[R10] BIPM. The International System of Units (SI), 9th edition[M/OL]. 2019. IAU. Julian year convention[Z]. Avogadro exact 6.02214076e23 mol^-1; year=365.25*86400 s as project unit convention; A*amu from existing shared foundation.constants [原始网址](https://www.bipm.org/en/publications/si-brochure)。

[返回目录](#toc)

<a id="detector"></a>

## Detector与单bin数据

| 样本 | 曝光[t·yr] | T积分[keVnr] | 数组shape | 原表范围与代表值 | 来源/数值 |
|---|---|---|---|---|---|
| PandaX_paired | 1.2 | [1.1, 3.0] | [52, 2] | 1.1–3；ε首/末=0.010829633/0.073827571 | [完整表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_paired_total.txt>)；R2 PDF p3 Fig.1 Total paired; official exposure 1.20, not R5 1.25; T bounds R4 Table II |
| PandaX_US2 | 1.04 | [0.3, 3.0] | [99, 2] | 0.3–3；ε首/末=0.0057913047/0.015546901 | [完整表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_us2_total.txt>)；R2 PDF p3 Fig.1 Total US2 and exposure; T bounds R4 Table II; no extra Qy/Ne window |
| XENONnT | 3.51 | [0.5, 3.0] | [40, 3] | 0.43–2.77；ε首/末=0.00011196658/0.12398753 | [完整表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xenonnt_combined.txt>)；R3 PDF p4 Fig.1 black combined; exposure R3 3.51; bounds R4 Table II |


PandaX Total已含选区，只乘一次；本次不使用Qy映射、Ne/S2逐箱模板或ci。XENONnT第三列是图线可见性/核验标记，效率用第2列。三样本的单bin处理来自[R1] p20 Eq.(87)；具体T界沿用[R4] p13 Table II。paired采用[R2]官方1.20 t·yr，已明确与[R5]1.25的差别。

**MISSING：XENONnT 2.7700000018–3 keVnr的原始接受度。** 主方案将末值0.12398752876529323延伸，是显式项目假设；zero/unit是0≤ε≤1界，profile_bounds另加尾段不确定区间，不称为论文原统计。

[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维阈值；p23 Fig.4绿色区域 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[R2] BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3. PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI [原始网址](https://arxiv.org/abs/2407.10892v3)。

[R3] APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2. PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr [原始网址](https://arxiv.org/abs/2408.02877v2)。

[R4] LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025. PDF p13 Table II: fitted yields, rounded statistical sigmas, T bounds, external SM references; p13 Eq.(E6) text flux 5.16e6; p14 Eq.(E8) shared pull, NOT adopted [原始网址](https://arxiv.org/abs/2502.10702v2)。

[返回目录](#toc)

<a id="prediction"></a>

## 事例数：各阶段实际计算

物理顺序与workflow一致：Source传播 → Target核数 → 原子核Response与振幅 → 截面/运动学 → Total接受度 → 单bin积分 → Statistics。传播与散射使用同一组eu、ed。

$$
\frac{d\sigma_{\rm eff}}{dT}=\frac{d\sigma_{\rm SM}}{dT}
+P_{ee}(E;eu,ed)\left[\frac{d\sigma_e(eu,ed)}{dT}-\frac{d\sigma_{\rm SM}}{dT}\right],
$$

$$
S_k=\mathcal E_k\sum_A n_A^{(1\,\mathrm{tonne})}
\int_{T_{\min,k}}^{T_{\max,k}}dT\,\varepsilon_k(T)
\int_{E_{\min}(T)}^{E_{\max}}dE\,t_{\rm yr}\Phi_{8B}f_{8B}(E)
\frac{d\sigma_{{\rm eff},A}}{dT}.
$$

第一式由ρ与diag(σe,σSM,σSM)的迹得到，只在当前实数ee-only子空间成立，μτ的SM事件仍保留。第二式是[R1] Eqs.(84),(87)按项目曝光单位展开；Ek单位t·yr，n_A^(1 tonne)是每吨该核素的核数，t_yr=31557600 s。各个质量/时间/效率只乘一次。

| 步骤/阶段 | 实际程序 | 具体输入→输出 |
|---|---|---|
| P03传播 | [独立SNuDD导出](<../../../../extensions/solar_rho_snudd/export_rho.py>)；[同源数值求积](<../../../../extensions/solar_rho_snudd/scan.py>) | 同一密度/产生区/振荡/NSI→ρ(E)；不提供源强和核截面 |
| P02/P04/P05 | [原核Response振幅](<../../../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>)；[原Target](<../../../../cevns_pyeft/experiments/solar_singlebin.py>) | 原核W、匹配Wilson、运动学→cm²/keV；天然Xe核数 |
| P06/P07 | [原NSIExecutor](<../../../../cevns_pyeft/experiments/solar_nsi.py>) | 原源强、ρ和截面→逐T密度→Total效率→3个events/bin |
| P08 | [原保留E轴的核](<../../../../cevns_pyeft/kernels/solar_nsi.py>) | K[7核素,known/tail,6单项式,144E]；原801个T网格并入效率节点 |
| P09 | [原三pull联合统计](<../../../../cevns_pyeft/statistics/solar_nsi.py>)；[本轮完整扫描入口](<../../../../tools/run_solar_b8_snudd_inference.py>) | 逐耦合点重算Pee、收缩K、profile、联合最小化、601²面 |


本轮使用标准load_snudd→PreparedExperiment→predict/evaluate核验扫描。旧v3.4核只在rebind_state验证每个不依赖传播的折叠输入hash一致后复用，保存新的物理身份；实际values逐位不变。[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维阈值；p23 Fig.4绿色区域 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[返回目录](#toc)

<a id="statistics"></a>

## Statistics：三个独立pull与联合最小值

| 样本 | 实验拟合信号D[events] | σstat[events] | σα | SM信号[events] | SM χ²k | 最佳点未移位信号[events] |
|---|---|---|---|---|---|---|
| PandaX_paired | 3.5 | 1.2985 | .12 | 2.487829836 | 0.577102414 | 2.851150910 |
| PandaX_US2 | 75.0 | 27.975 | .12 | 47.043419726 | 0.959607249 | 57.840675139 |
| XENONnT | 10.7 | 3.9483 | .12 | 11.857362687 | 0.076048226 | 13.823521150 |


D来自[R2] p2摘要和[R3] p5 Table I的实验信号拟合值；不是原始选中候选计数。σ由[R1] p20 Eq.(88)紧随文字的37.1%、37.3%、36.9%分别乘D推导；三个独立12%pull，按论文简化统计执行，不改成共用一次通量pull。实际数组见[统计卡](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json>)

$$
\chi^2=\min_{\alpha_1,\alpha_2,\alpha_3}\sum_k
\left\{\frac{[D_k-(1+\alpha_k)S_k]^2}{\sigma_k^2}+\frac{\alpha_k^2}{0.12^2}\right\}
=\sum_k\frac{(D_k-S_k)^2}{\sigma_k^2+0.12^2S_k^2},
$$

$$
\alpha_k^*=\frac{0.12^2 S_k(D_k-S_k)}{\sigma_k^2+0.12^2S_k^2},\qquad
\Delta\chi^2(eu,ed)=\chi^2(eu,ed)-\min_{eu,ed}\chi^2.
$$

这里右侧是对式(88)独立高斯pull的解析极小化推导，并用独立三变量最小二乘核对。二维90%区域按[R1] p22给定Δχ²≤4.61；本轮未另做覆盖率toy校准。不把很小的SM与最小值差异解读为新物理显著性。


各最佳pull=0.0147737911, 0.017203304, -0.0339006617。联合χ²min=1.119850905140；3个独立DE种子加121²包围域网格多起点，DE结果spread=1.09e-13。图内601²最低χ²=1.21410762；主面实际减的是全域数学模型的1.11985091，未减SM或图内最小值。

US2正定电子截面二次型与Pee下界给出包含所有可能最小值/90%点的有限椭圆；搜索在其包围方形内，见[系数、搜索边界和每次优化记录](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/MINIMUMS.json>)。有限包围域有解析依据，域内多起点收敛是数值检查；不是对任意近似有效性的证明。

[三样本信号/误差图](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/solar_snudd_signal_comparison.png>)

[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维阈值；p23 Fig.4绿色区域 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[R2] BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3. PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI [原始网址](https://arxiv.org/abs/2407.10892v3)。

[R3] APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2. PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr [原始网址](https://arxiv.org/abs/2408.02877v2)。

[返回目录](#toc)

<a id="comparison"></a>

## 与论文Fig.4的定量比较

![实际计算与论文边界](../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/solar_Fig4_snudd_vs_paper.png)

绿色填充/绿边为本次计算；灰色虚线为论文绿色区域边界，黑十字为SM，红点为(0,.178)。灰线仅验收参考，不参与前向计算、最小化或校准。

| 比较项 | 本轮SNuDD计算 | 论文原图/依据 |
|---|---|---|
| eu=0时ed边界 | -0.1508790, 0.5234600 | -0.1962416, 0.1551313, 0.1947402, 0.5460905 |
| (0,.178) | Δχ²=3.331335007<4.61，允许 | 两块绿色多边形均不含此点，排除 |
| [-1,1]²允许面积占比 | 30.862595% | 32.254894%；601²网格估计 |
| 区域交并比IoU | 84.203255% | intersection/union；不能当作统计p值 |
| 接入前本地B16的IoU | 84.156520% | 同一论文原生参考、同样比较框；只用于传播方案对照 |


**结果：整体沿对角线延伸的相关带结构一致，但论文中间的窄禁区未被本计算复现；不能写“Fig.4精确复现成功”。** 换用SNuDD传播没有消除差异。尾段、传播固定与各自最小值的对照已保存；本轮未通过改通量、改味定义、加ci或拟合图线来对齐论文。

论文参考是p23 PDF的386/342顶点两块完整绿色填充路径，已重新从原生PDF逐点核对，坐标差0；不受橙/蓝遮挡影响。原件hash与方法在[原图独立核验](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/source_evidence/PAPER_VECTOR_VALIDATION.json>)，完整边界在[参考多边形](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/source_evidence/paper_fig4_green_reference.json>)。其数字化精度不等于作者提供了原始χ²网格。

[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维阈值；p23 Fig.4绿色区域 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[返回目录](#toc)

<a id="controls"></a>

## 尾段和传播对照

| 方案（各减自己联合最小值） | χ²min | (eu,ed)min | eu=0的ed边界 |
|---|---|---|---|
| flat_sensitivity | 1.1198509051 | (-17.262106,15.675963) | -0.1508790, 0.5234600 |
| zero | 1.1052420584 | (-17.396627,15.794940) | -0.1513936, 0.5240704 |
| unit | 1.2239933097 | (-16.510925,15.010863) | -0.1472426, 0.5191575 |
| profile_bounds | 1.1052420584 | (-17.396627,15.794940) | -0.1513936, 0.5240704 |
| fixed_SM_propagation | 1.1524262823 | (18.784636,-16.687461) | -0.1580100, 0.5163789 |


flat_sensitivity为主方案末值延伸；zero/unit为未知尾段效率取0/1；profile_bounds在逐点信号上下界内自由选择最有利信号，是额外未知尾处理；fixed_SM_propagation只改变散射、把传播固定在SM，用于诊断，未取代主模型。

![](../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/solar_snudd_controls.png)

所有对照源于同一原核/统计输入及已声明的尾段选择。不是将几条不同假设下的轮廓合并为一个置信区域。原实验尾段缺失依据见Detector；统计依据仍为[R1] Eq.(88)。

[返回目录](#toc)

<a id="validation"></a>

## 验收、主线入口与复算

| 检查 | 实际结果/证据 |
|---|---|
| 直接完整ρ核对 | 5点×144E×3×3；max差=8.816e-16；[完整记录](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/DIRECT_RUNTIME_VALIDATION.json>) |
| 主线predict/evaluate | 5点×3样本；事例差最大5.648e-11；联合χ²差最大1.884e-12 |
| 新最佳点Slow/Fast | PandaX_paired: &#124;ΔS&#124;=0.0008302; PandaX_US2: &#124;ΔS&#124;=0.00507; XENONnT: &#124;ΔS&#124;=0.0036705 events；容差max(3e−4,0.2%) |
| 既有v3.4前向对照 | 9个Slow/Fast点及US2的1201×216加密已冻结，本轮只读引用；[原记录](<../../../../outputs/external/solar_rho_snudd/20261112_run1/FORWARD_VALIDATION.json>) |
| 本轮测试 | 63项通过；[实际JUnit记录](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/tests.xml>) |
| 保护 | 472份原core/data/旧SNuDD源码与结果hash不变；[本轮验收](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/QA.json>) |
| 默认包/注册 | 主进程无snudd import；不改默认实验Catalog，不改根依赖；独立显式入口 |


图和表由同一结果JSON/数组生成；[实际601²原χ²/Δχ²/信号面](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/solar_NSI_surfaces.npz>)、[各切线根](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/SLICE_BOUNDARIES.json>)可独立重算核对。主线两实验的SNUDD_FIG4_BRANCH.json及P09/P10报告引用本轮结果，不覆盖旧版本报告。

```powershell
# 工作目录：Gitup01；新输出目录，旧结果禁止覆盖。
# 使用已配置的主项目Python；外部导出由独立.venvs/snudd解释器执行。
.venvs/snudd/Scripts/python.exe -B -m extensions.solar_rho_snudd.scan_source --output outputs/external/solar_rho_snudd/NEW_RUN/propagation_source
python -B tools/run_solar_b8_snudd_inference.py --output outputs/external/solar_rho_snudd/NEW_RUN --grid 601
# 本次冻结run的验收及同源文档检查：
python -B -m pytest tests/test_solar_snudd_inference.py tests/test_solar_snudd.py tests/test_solar_nsi.py tests/test_solar_singlebin.py
python -B tools/finalize_solar_b8_snudd_inference.py --check
node tools/validate_solar_b8_snudd_inference.mjs
```

[返回目录](#toc)

<a id="gaps"></a>

## 仍未闭合的论文等价条件

| 未闭合项 | 本次如何处理 | 仍受限的声明 |
|---|---|---|
| 2601作者完整数值卡/原χ²面 | 用逐项有来源的项目选择；论文多边形只作参考 | 不能确定中间禁区差异唯一来自传播、核表或其他数值约定；需原作者输入/中间量逐项对照 |
| 大NSI的两味有效近似 | 远处最小值给出所声明数学模型下的数值；各ρ包保存γ和2EV/Δ31诊断 | 不能把γ大等同完整三味有效；全域数学最小值不等于已认证大耦合物理拟合 |
| XENONnT尾段接受度 | 明确末值假设＋0/1界及额外profile | 精确论文前向折叠仍缺该原数据；不能说SNuDD补出了探测器数据 |
| 核响应外部原件 | 按用户选择直接复用既有数值/读取约定，七核表公开在本地 | 外部作者表/转换认证未闭合；不影响本地重复运行，限制论文同源认证 |


| 点 | 最小绝热γ | 最大&#124;2EV/Δm31²&#124; | 核验 |
|---|---|---|---|
| SM | 1105.7662 | 0.10778137 | 4001个径向点；独立两能级有限差分 |
| 差异点 | 1082.7433 | 0.14575935 | 4001个径向点；独立两能级有限差分 |
| 数学模型最佳点 | 3443.6697 | 1.2421453 | 4001个径向点；独立两能级有限差分 |


γ大仅检查绝热性；2EV/Δ31不小时仍不能保证真空θ13的两味约化。最终能力交接：三样本事例数、SM点χ²、声明近似模型下完整NSI统计与对照均已算出；技术验证与科学接受分开。精确Fig.4复现状态保持未成立。无需等待另一份现成响应矩阵才能重复本次单bin结果。

[返回目录](#toc)

<a id="references"></a>

## 标准文献与原件

[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维阈值；p23 Fig.4绿色区域 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[R2] BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3. PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI [原始网址](https://arxiv.org/abs/2407.10892v3)。

[R3] APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2. PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr [原始网址](https://arxiv.org/abs/2408.02877v2)。

[R4] LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025. PDF p13 Table II: fitted yields, rounded statistical sigmas, T bounds, external SM references; p13 Eq.(E6) text flux 5.16e6; p14 Eq.(E8) shared pull, NOT adopted [原始网址](https://arxiv.org/abs/2502.10702v2)。

[R5] LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024. PDF p5 Eq.(29): flux 5.46(1+-0.12)e6; p6 Table II paired exposure 1.25 conflicts with R2 1.20; choose official R2 [原始网址](https://arxiv.org/abs/2409.04703v2)。

[R6] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from 8B decay[J]. Physical Review C, 1996, 54: 411-422. DOI: 10.1103/PhysRevC.54.411. Official numerical spectrum[DS/OL], accessed 2026-11-06. 829 numeric rows, columns 1 and 2; normalized shape, not total flux; original rounding retained [原始网址](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)。

[R7] NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06. nine original A/mass/number-fraction rows; full nine-row mean molar mass used before selecting seven available responses [原始网址](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe)。

[R8] CEvNS-pyEFT local resource. responses_all.json[DS]. User-selected existing nuclear-response table; external author release and conversion NOT independently certified. Xe128,129,130,131,132,134,136; np basis ordered p,n; W=e^-2y sum a_k y^k; M,SigmaPP,SigmaP,PhiPP,PhiPT,Delta,MPhiPP,SigmaPDelta; no extra KN or spin prefactor 

[R9] Project SM benchmark decision, retained from the 2411.11749v1 analysis, 2026-11-10/11[Z]. sin^2 theta_W=0.23857 retained as explicit project input; NOT claimed as a printed numeric default of 2601.19883v2 [原始网址](https://arxiv.org/abs/2411.11749v1)。

[R10] BIPM. The International System of Units (SI), 9th edition[M/OL]. 2019. IAU. Julian year convention[Z]. Avogadro exact 6.02214076e23 mol^-1; year=365.25*86400 s as project unit convention; A*amu from existing shared foundation.constants [原始网址](https://www.bipm.org/en/publications/si-brochure)。

[S_software] AMARAL D W P, CERDEÑO D, CHEEK A, COSTA V, FOLDENAUER P. SNuDD: Solar Neutrinos for Direct Detection[EB/OL]. arXiv:2607.22817v1, 2026. SolarDensityMatrixCalculator.density_mass/density; ProbabilityCalculator._cos_matter_average; direct adopted software, effective two-flavor and mass-decohered flavor reconstruction [原始网址](https://arxiv.org/abs/2607.22817v1)。

[S_nsi_mapping] SNuDD Collaboration. GeneralNSI model source[CP/OL]. Fixed Git commit 11622ded104994959a649d85e263c2d9f933ea74, accessed2026-11-12. GeneralNSI.xi_p/xi_n/xi_u/xi_d/xi_e; model eps_matrix multiplies each xi, phi=0 [原始网址](https://github.com/SNuDD/SNuDD/blob/11622ded104994959a649d85e263c2d9f933ea74/snudd/models.py)。

[S_density] BAHCALL J N, SERENELLI A M, BASU S. 10,000 Standard Solar Models: a Monte Carlo Simulation[J]. Astrophysical Journal Supplement, 2006,165:400-431. DOI:10.1086/504043. arXiv:astro-ph/0511337. log10_electron_density, log10_neutron_electron_density; e1..e5,n1,n2; adopted software fits, not B16 arrays [原始网址](https://arxiv.org/abs/astro-ph/0511337)。

[S_production] LOPES I, TURCK-CHIÈZE S. Solar neutrino physics oscillations: Sensitivity to the electronic density in the Sun’s core[J]. Astrophysical Journal,2013,765:14. DOI:10.1088/0004-637X/765/1/14. arXiv:1302.2791. raw two-column file header identifies1302.2791; flux_dists.interpolate_dist linear, outside0; native distribution normalized in dr over0-.35 by propagation code [原始网址](https://arxiv.org/abs/1302.2791v1)。

[S_remaining_oscillation] ESTEBAN I, GONZALEZ-GARCIA M C, MALTONI M, et al. NuFit-6.0: Updated global analysis of three-flavor neutrino oscillations[J]. JHEP,2024,12:216. DOI:10.1007/JHEP12(2024)216. arXiv:2410.05380. osc_params_best; explicit theta23=43.3deg,delta=212deg,dm31=2.513e-3eV² retained; theta12/13/dm21 overridden from v3.3 project card [原始网址](https://arxiv.org/abs/2410.05380)。

全部实际来源文件和hash见固定输入卡、旧来源台账与本轮SOURCE_FINGERPRINTS/DELIVERY_FILES。软件原件直接网址由snudd.input.json的direct_url给出；“软件已核”与“原论文→软件数值已认证”分开保留。

[返回目录](#toc)
