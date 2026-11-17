# 太阳⁸B完整ρ与Tr(ρK) onboarding v3.5（新版本／实施前合同）

**2026-11-12。按用户要求先更新onboarding：源端传完整SNuDD味密度矩阵，散射端实际计算Tr(ρK)。本轮只改文档、来源核对和主线待办；运行物理代码、事例数与统计结果尚未按新合同重算。** 旧v3.4/v3.4.1及其结果保留，不能把旧投影实现标成新版trace实现。

[新版机器可读合同](<SNUDD_FULL_TRACE_CONTRACT.v3.5.json>) · [既有固定来源/参数卡](<../../../../extensions/solar_rho_snudd/snudd.input.json>) · [输入与源码核对](<../../../../outputs/external/solar_rho_snudd/20261112_trace_onboarding/README.md>) · [旧统计报告](<SNUDD_FULL_BENCHMARK.v3.4.1.md>)

<a id="toc"></a>

## 目录

- [新要求、当前实现与版本](#scope)
- [入射通量和完整rho](#source)
- [核Response、微分截面和总截面](#cross-section)
- [事例数：完整积分与单bin形式](#events)
- [哪些公式相同，哪些输入不同](#experiments)
- [统计与旧结果的关系](#statistics)
- [程序逐处对应和必须修改的内容](#implementation)
- [下一步验收与交接](#handoff)
- [标准文献与直接来源](#references)

<a id="scope"></a>

## 新要求、当前实现与版本

| 对象 | 本版要求 | 当前真实状态 |
|---|---|---|
| Source | 完整复数ρ(E)，味顺序e,μ,τ；不重分配μ/τ，不删除非对角元 | 原始完整NPZ已存在；当前state.__call__仍返回等价对角投影，待改 |
| 散射 | 先从原核Response/振幅构造3×3 K，再实际Tr(ρK) | 共享K/trace API已存在；太阳专用dsigma分支仍使用Pee简式，待接入 |
| 事例数与Fast | 保留E轴及K的两个味指标；每个参数点用完整ρ收缩 | 当前太阳Fast和联合扫描都是标量Pee表示；新版矩阵核尚未生成 |
| 统计 | 沿用2601式(88)，前向信号改由新版trace得到 | 旧601²面仍属旧实现；本轮没有重命名或重算 |
| 范围 | PandaX paired、US2和XENONnT的2601单bin；实数ee-only uV/dV | SM、多bin、V/B−L各自保留；不自动扩大到非对角NSI |


方法选择来自用户原话“散射端需要改用trace(rho K)”；本轮顺序来自“你先把onboarding修改了”“总的截面积分公式也给一下”“截面，事例数公式”。这是明确的方法要求，不把程序待实现包装成已完成。

[返回目录](#toc)

<a id="source"></a>

## 入射通量和完整rho

定义Φ8B为地球处所有活跃味合计的总通量，f8B为谱形；ρ为每个能量的单位迹密度矩阵，不包含通量或曝光：

$$
\frac{d\phi_{\rm tot}}{dE}=\Phi_{8B}f_{8B}(E),\qquad
F(E)=\frac{d\phi_{\rm tot}}{dE}\,\rho(E),\qquad
\rho=\rho^\dagger,\quad\operatorname{Tr}\rho=1,\quad\rho\succeq0.
$$

F是通量矩阵，单位cm⁻²s⁻¹MeV⁻¹；ρ单位1，shape=(N_E,3,3)。本版后续公式采用“总通量×单位迹ρ”的写法；若改用F，公式中不能再乘一次总通量。

| 输入 | 实际数值/数组 | 数值位置、具体出处与核验范围 |
|---|---|---|
| 总通量/谱形 | Φ=5.46×10⁶ cm⁻²s⁻¹；829×2，E=0–16.56MeV，f单位MeV⁻¹，原网格积分0.999986544 | [Bahcall原表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt>)；[R5]p5 Eq.(29)总通量；[R6]官网第1/2列；保留原舍入与线性插值，不任意改通量 |
| 振荡值 | θ12=.583638rad、θ13=.149575rad、Δm21²=7.42×10⁻⁵eV²；θ23=43.3°、δ=212°、Δm31²=2.513×10⁻³eV² | [实际输入卡](<../../../../extensions/solar_rho_snudd/snudd.input.json>)；前三项为沿用v3.3固定PEANUTS示例的项目选择：[实际示例Neutrinos字段](<../../../../outputs/solar_b8_nsi/20261112_fig4_run1/source_evidence/peanuts_examples_solar_test.yaml>)；其余[S_remaining_oscillation]固定软件默认 |
| 电子/中子密度 | log10(ne/NA)=2.36−4.52x−.33exp[−(x/.075)^1.1]；log10(nn/NA)=1.72−4.80x；mol/cm³ | [实际解析函数](<../../../../.externals/SNuDD/snudd/nsi/solar_profiles.py>)；[S_density]直接采用固定软件拟合，原论文系数认证单列 |
| 产生区/求积 | 原96×2表，x=0–.17Rsun；软件在0–.35的1000节点按dr求积归一、线性插值、域外0 | [原产生区数据](<../../../../.externals/SNuDD/snudd/data/flux_distributions/8B_dist.txt>)；[S_production]表头原文；不乘r² |
| 实际ρ | 下表；均为独立SNuDD进程输出的完整复矩阵，包含非零非对角元 | [逐包身份、哈希和10MeV矩阵](<../../../../outputs/external/solar_rho_snudd/20261112_trace_onboarding/RHO_INPUT_AUDIT.json>)；[S_software]density_mass→density；没有新生成矩阵 |


| 点 | (eu,ed) | shape | E范围[MeV] | 原始数值 |
|---|---|---|---|---|
| SM | (0,0) | [1450, 3, 3] | 0.00114662141–16.56 | [原始rho.npz](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/validation_cache/8e2417073e926516c86038b6f3e5984f14f9d41bb05cb97da8fb1e5c078828cd/rho.npz>) |
| Fig4_difference_point | (0,0.178) | [1450, 3, 3] | 0.00114662141–16.56 | [原始rho.npz](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/validation_cache/adcedd118cdb5c452cc4d147862a8c1743aea87d2bb60dece2c300d9079f8d69/rho.npz>) |
| previous_mathematical_minimum | (-17.262106,15.675963) | [1450, 3, 3] | 0.00114662141–16.56 | [原始rho.npz](<../../../../outputs/external/solar_rho_snudd/20261112_fig4_run2/validation_cache/94190e9efd4fc2f5c9f8e892ef5158334f35858fc98e73a85a191278b24275e6/rho.npz>) |


传播仍为SNuDD有效两味绝热模型、产生区平均及质量相位平均，再用UρmassU†转换成完整味矩阵；不含地球再生，不是完整三味ODE。质量相位平均并不意味着味基底的非对角元必须为零。

**基底/相位：** ρ采用固定SNuDD.UPMNS的味相位约定。当前实数对角ee NSI的K对味重定相不变；若以后加入非对角耦合，ρ、Wilson矩阵及K须一起转换。不能只按另一个PMNS约定修改ρ非对角元的符号；本版未批准该扩展。


[R5] LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024. PDF p5 Eq.(29): flux 5.46(1+-0.12)e6; p6 Table II paired exposure 1.25 conflicts with R2 1.20; choose official R2 [原始网址](https://arxiv.org/abs/2409.04703v2)。

[R6] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from 8B decay[J]. Physical Review C, 1996, 54: 411-422. DOI: 10.1103/PhysRevC.54.411. Official numerical spectrum[DS/OL], accessed 2026-11-06. 829 numeric rows, columns 1 and 2; normalized shape, not total flux; original rounding retained [原始网址](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)。

[S_software] AMARAL D W P, CERDEÑO D, CHEEK A, COSTA V, FOLDENAUER P. SNuDD: Solar Neutrinos for Direct Detection[EB/OL]. arXiv:2607.22817v1, 2026. SolarDensityMatrixCalculator.density_mass/density; ProbabilityCalculator._cos_matter_average; direct adopted software, effective two-flavor and mass-decohered flavor reconstruction [原始网址](https://arxiv.org/abs/2607.22817v1)。

[S_density] BAHCALL J N, SERENELLI A M, BASU S. 10,000 Standard Solar Models: a Monte Carlo Simulation[J]. Astrophysical Journal Supplement, 2006,165:400-431. DOI:10.1086/504043. arXiv:astro-ph/0511337. log10_electron_density, log10_neutron_electron_density; e1..e5,n1,n2; adopted software fits, not B16 arrays [原始网址](https://arxiv.org/abs/astro-ph/0511337)。

[S_production] LOPES I, TURCK-CHIÈZE S. Solar neutrino physics oscillations: Sensitivity to the electronic density in the Sun’s core[J]. Astrophysical Journal,2013,765:14. DOI:10.1088/0004-637X/765/1/14. arXiv:1302.2791. raw two-column file header identifies1302.2791; flux_dists.interpolate_dist linear, outside0; native distribution normalized in dr over0-.35 by propagation code [原始网址](https://arxiv.org/abs/1302.2791v1)。

[S_remaining_oscillation] ESTEBAN I, GONZALEZ-GARCIA M C, MALTONI M, et al. NuFit-6.0: Updated global analysis of three-flavor neutrino oscillations[J]. JHEP,2024,12:216. DOI:10.1007/JHEP12(2024)216. arXiv:2410.05380. osc_params_best; explicit theta23=43.3deg,delta=212deg,dm31=2.513e-3eV² retained; theta12/13/dm21 overridden from v3.3 project card [原始网址](https://arxiv.org/abs/2410.05380)。

[返回目录](#toc)

<a id="cross-section"></a>

## 核Response、微分截面和总截面

先区分三个对象：核响应 $W_X^{NN'}(q)$ 作用在核子p/n空间；$K_A(E,T)$ 是求和出射中微子味、包含核振幅和截面相空间因子的**入射味空间3×3微分截面矩阵**；探测器迁移/接受度作用在真实反冲T与实验读数x之间。三者不是同一个Response。

设A标识同位素，α、β标识入射味，f为出射味。K由共享核振幅构造，其结构为：

$$
[K_A(E,T)]_{\alpha\beta}
=\mathcal P_A(E,T)\sum_f
\overline{\mathcal M_{f\alpha}^*(E,T)\mathcal M_{f\beta}(E,T)},
\qquad K_A=K_A^\dagger\succeq0.
$$

横线代表既有振幅约定中的核自旋平均/求和，P代表其相空间和单位因子；不在此额外加自旋或KN因子。实际Li2026核心的截面步骤对其振幅核乘m_A/(8πE²)及GeV⁻²→cm²，再将cm²/GeV换为cm²/keV；由cross_section.py和rates/differential.py拥有归一化。

**微分截面：**

$$
\frac{d\sigma_A}{dT}(E,T;\rho,\epsilon)
=\operatorname{Tr}[\rho(E;\epsilon)K_A(E,T;\epsilon)]
=\sum_{\alpha,\beta}\rho_{\alpha\beta}(E;\epsilon)
[K_A(E,T;\epsilon)]_{\beta\alpha}.
$$

K和dσ/dT单位cm²/keV；ρ无量纲。矩阵指标必须反向相乘，不能用同位置元素乘积代替迹。展开后是Σα ρααKαα+2ReΣα<β ραβKβα，实部和虚部干涉都由迹保留。

**固定入射能量E的物理总截面：**

$$
\sigma_A(E;\rho,\epsilon)=
\int_0^{T_{\max,A}(E)}dT\,
\operatorname{Tr}[\rho(E;\epsilon)K_A(E,T;\epsilon)].
$$

此量单位cm²，不含探测器效率、靶核数、曝光或源通量。若需要某实验的“选中有效截面”，应另外标注：

$$
\sigma^{\rm sel}_{k,A}(E)=
\int_0^{T_{\max,A}(E)}dT\,a_k(T)\,
\operatorname{Tr}[\rho(E)K_A(E,T)].
$$

这里k是实验样本，a_k是完整选择概率；它不是微观核截面的一部分。

**所有实验共用的弹性运动学：**

$$
T_{\max,A}(E)=\frac{2E^2}{m_A+2E},\qquad
E_{\min,A}(T)=\frac{T+\sqrt{T^2+2m_AT}}{2}.
$$

这两式内部的E、T、m_A必须使用相同能量单位。实际程序入口E使用MeV、T使用keV，进入核心后统一为GeV；不能直接把不同单位的数值代入上式。

当前ee-only实数矢量NSI仍按[R1]p22 Eq.(95)设置C61q_NP=−√2GF·εee_qV·diag(1,0,0)，再加完整SM。若算得K为对角且Kμμ=Kττ，这是当前Wilson模型产生的结果；程序依然传完整ρ并实际计算矩阵迹，不以这个性质为理由改写Source或跳过迹。

| 截面所需输入 | 实际数值/约定 | 出处与实现位置 |
|---|---|---|
| 核W | Xe128/129/130/131/132/134/136；basis p,n；W=e⁻²ʸΣa_k y^k，y=(qb/2)² | [既有完整数值核表](<../../../../data/responses/responses_all.json>)；[R8]用户选用本地表，外部作者原表认证未闭合；读取[nuclear.response] |
| Xe丰度/质量 | 9×3，A124–136；七核表按原数丰度，合计.998158，不重归一；核质量A·amu | [NIST九行](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xe_isotopes.txt>)；[R7]；核数分母仍用九行平均摩尔质量 |
| SM点/NSI | sin²θW=.23857；NP只有ee,uV/dV；单位GeV⁻² | [原物理卡](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)；[R9]明确项目选择；[R1]Eq.(95)；[nsi_point/Wilson映射](<../../../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>) |
| 完整K函数 | 已存在，输出E.shape+(3,3)，complex128，cm²/keV；太阳专用接入待改 | [differential_flavor_kernel_nn，第225行](<../../../../cevns_pyeft/rates/differential.py>)；[截面相空间/单位定义](<../../../../cevns_pyeft/theory/li2026/cross_section.py>) |
| 迹函数 | 已存在，einsum(...ab,...ba)，验证ρ与K；不是论文数值表 | [contract_density_kernel_grid，第281行](<../../../../cevns_pyeft/theory/li2026/flavor.py>) |


迹公式是密度矩阵散射概率的定义；上面的总截面、选择截面由微分截面积分得到，属显式推导。核振幅采用[R1]框架与已有共享实现，不引用另一篇图线替代K。[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维4.61阈值；p23 Fig.4 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[R7] NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06. nine original A/mass/number-fraction rows; full nine-row mean molar mass used before selecting seven available responses [原始网址](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe)。

[R8] CEvNS-pyEFT local resource. responses_all.json[DS]. User-selected existing nuclear-response table; external author release and conversion NOT independently certified. Xe128,129,130,131,132,134,136; np basis ordered p,n; W=e^-2y sum a_k y^k; M,SigmaPP,SigmaP,PhiPP,PhiPT,Delta,MPhiPP,SigmaPDelta; no extra KN or spin prefactor 

[R9] Project SM benchmark decision, retained from the 2411.11749v1 analysis, 2026-11-10/11[Z]. sin^2 theta_W=0.23857 retained as explicit project input; NOT claimed as a printed numeric default of 2601.19883v2 [原始网址](https://arxiv.org/abs/2411.11749v1)。

[返回目录](#toc)

<a id="events"></a>

## 事例数：完整积分与单bin形式

令k表示样本，$n_A$ 是靶中同位素A的核数，$t_k$ 是观测时间；先用最直观的固定靶核数形式表示。$P_{k,i}(T)$ 是反冲T进入实验第i箱并通过选择的概率：

$$
S_{k,i}=t_k\sum_A n_A
\int_0^{E_{\max}}dE\,\Phi_{8B}f_{8B}(E)
\int_0^{T_{\max,A}(E)}dT\,P_{k,i}(T)
\operatorname{Tr}[\rho(E;\epsilon)K_A(E,T;\epsilon)].
$$

这是**事例数**，单位events；与截面的区别是增加了源通量、靶核数、观测时间和选择概率。微观K、完整ρ及迹的形式不随探测器改变。

若探测器给出真实反冲到读数x的核R_k(x|T)，则：

$$
P_{k,i}(T)=\int_{x\in\mathrm{bin}_{k,i}}dx\,\mathcal R_k(x\mid T).
$$

若R已经包含效率/ROI，不能再乘一次同一效率。若R只是归一化为1的条件分辨函数，则需在所声明的位置单独乘效率。多bin方案用各自P_{k,i}；不能把单bin的总接受度反推为已取得逐箱迁移核。

**本次2601单bin方案：** 采用实验Total/combined接受度和已选定的真实T积分界，不再做一次Ne/S2选区转换：

$$
a_k(T)=\mathbf1_{[T_{\min,k},T_{\max,k}]}(T)\,\varepsilon_k^{\rm Total}(T).
$$

项目数据给的是曝光 $\mathcal E_k$ [tonne·yr]，不需要任意拆成质量和时间。定义 $n_A^{(1\mathrm t)}$ 为每吨该核素核数，$t_{\rm yr}=31557600$ s/yr，则上式写成实际计算形式：

$$
S_k=\mathcal E_k\sum_A n_A^{(1\mathrm t)}t_{\rm yr}\Phi_{8B}
\int_{T_{\min,k}}^{T_{\max,k}}dT\,\varepsilon_k^{\rm Total}(T)
\int_{E_{\min,A}(T)}^{E_{\max}}dE\,f_{8B}(E)
\operatorname{Tr}[\rho(E;\epsilon)K_A(E,T;\epsilon)].
$$

若E_min超过E_max，该T点贡献为0。T单位keV、K单位cm²/keV，E单位MeV、f单位MeV⁻¹。用完整核素平均摩尔质量Mbar [g/mol]与数丰度η_A计算：

$$
n_A^{(1\mathrm t)}=\frac{10^6\,\mathrm{g}}{\overline M}\,N_{\rm Av}\eta_A,
\qquad \overline M=\sum_A\eta_A M_A.
$$

这些式子是[R1]Eqs.(84),(87)按本项目通量/单位/曝光约定展开。每吨核数、曝光和一年秒数各用一次；若另选已含曝光的积分通量，必须相应移除外面的同一时间/质量因子。

| 输入/符号 | 实际值或定义 | 出处 |
|---|---|---|
| Φ、f、ρ、K | 同上一、二节；K必须由完整矩阵接口返回 | 各节逐项来源；K太阳新绑定仍PENDING |
| n_A^(1t) | 九行NIST丰度质量构成Mbar，选择七核表；不补缺核表、不重归一 | [实际九行数组](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xe_isotopes.txt>)；[R7]；[build_targets原换算](<../../../../cevns_pyeft/experiments/solar_singlebin.py>) |
| t_yr、N_Av | 31557600s/yr；6.02214076×10²³mol⁻¹ | [R10]Julian year项目单位约定及SI常数 |
| 曝光/ε/T界 | 下节三样本对照；具体数组、有效域和尾段假设分别保存 | [R2][R3]曝光与接受度；[R4]Table II积分界 |


[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维4.61阈值；p23 Fig.4 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[R2] BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3. PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI [原始网址](https://arxiv.org/abs/2407.10892v3)。

[R3] APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2. PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr [原始网址](https://arxiv.org/abs/2408.02877v2)。

[R4] LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025. PDF p13 Table II: fitted yields, rounded statistical sigmas, T bounds, external SM references; p13 Eq.(E6) text flux 5.16e6; p14 Eq.(E8) shared pull, NOT adopted [原始网址](https://arxiv.org/abs/2502.10702v2)。

[R7] NIST. Atomic Weights and Isotopic Compositions for Xenon[DS/OL]. Accessed 2026-11-06. nine original A/mass/number-fraction rows; full nine-row mean molar mass used before selecting seven available responses [原始网址](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe)。

[R10] BIPM. The International System of Units (SI), 9th edition[M/OL]. 2019. IAU. Julian year convention[Z]. Avogadro exact 6.02214076e23 mol^-1; year=365.25*86400 s as project unit convention; A*amu from existing shared foundation.constants [原始网址](https://www.bipm.org/en/publications/si-brochure)。

[返回目录](#toc)

<a id="experiments"></a>

## 哪些公式相同，哪些输入不同

| 物理对象/公式 | 本次是否共用 | 具体差别在哪里 |
|---|---|---|
| 核振幅→K、dσ/dT=Tr(ρK)、σ=∫dT Tr(ρK) | PandaX与XENONnT相同 | 相同Xe核素、同一Wilson点和核表时K相同；不因实验名另乘一个核截面修正 |
| 太阳Φ、f及ρ(E) | 本次三样本相同 | 都用同一地球处⁸B日间平均源；未模拟地点/时段相关地球再生，不能声称包含该差别 |
| 弹性Emin/Tmax及每吨天然Xe核数 | 相同定义与资源 | 随核素质量A变化；本次不按实验换核素或重新归一丰度 |
| S=源×核数×时间×选择×Tr(ρK)双积分 | 同一总公式 | k下标的曝光、ε和T窗口不同，数值不能直接复用 |
| 实验读数和迁移 | 一般不同 | paired依赖成对S1/S2选择，US2依赖无配对S2/电子选择，XENONnT有自身S2选择；本次均已折入各自Total/combined的单bin方案 |
| 多bin与单bin | 同一个总概率积分框架，具体P不同 | 多bin用P_k,i(T)，单bin用完整ROI接受度及指定T窗口；数据与流程继续隔开 |
| 统计形式 | 本次同用Eq.(88)独立pull | 实验D和σ不同；这不是对所有实验普适的likelihood规则 |


更广泛地，其他实验也共用矩阵迹和源/靶/选择双积分的结构，但K随核素与相互作用变，ρ和通量随源及传播变，选择概率随探测器变。反中微子必须用对应的反中微子K和ρ；不能直接复用太阳中微子的数值。这些区别不能仅靠更换一个曝光常数处理。

| 样本 | 曝光[t·yr] | T积分[keVnr] | 数组shape | 原表支撑与代表值 | 数值及精确来源 |
|---|---|---|---|---|---|
| PandaX_paired | 1.2 | [1.1, 3.0] | [52, 2] | 1.1–3；ε首/末=0.010829633/0.073827571 | [完整表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_paired_total.txt>)；R2 PDF p3 Fig.1 Total paired; official exposure 1.20, not R5 1.25; T bounds R4 Table II |
| PandaX_US2 | 1.04 | [0.3, 3.0] | [99, 2] | 0.3–3；ε首/末=0.0057913047/0.015546901 | [完整表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_us2_total.txt>)；R2 PDF p3 Fig.1 Total US2 and exposure; T bounds R4 Table II; no extra Qy/Ne window |
| XENONnT | 3.51 | [0.5, 3.0] | [40, 3] | 0.43–2.77；ε首/末=0.00011196658/0.12398753 | [完整表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xenonnt_combined.txt>)；R3 PDF p4 Fig.1 black combined; exposure R3 3.51; bounds R4 Table II |


PandaX的两条Total来自[R2]p3 Fig.1，XENONnT的combined来自[R3]p4 Fig.1；积分界来自[R4]p13 Table II。paired采用官方1.20 t·yr，未采用[R5]表中的1.25。

**仍缺的实验数据：XENONnT约2.7700000018–3keVnr接受度。** 旧主方案末点0.12398752876529323恒值延伸只是显式项目假设，zero/unit是0≤ε≤1界；保留这些方案，不能在修改trace时静默填补、调归一或改通量。PandaX两份Total覆盖本次积分界。

[R2] BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3. PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI [原始网址](https://arxiv.org/abs/2407.10892v3)。

[R3] APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2. PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr [原始网址](https://arxiv.org/abs/2408.02877v2)。

[R4] LIAO J, TANG J, ZHANG B L. Tensor interaction in coherent elastic neutrino-nucleus scattering[EB/OL]. arXiv:2502.10702v2, 2025. PDF p13 Table II: fitted yields, rounded statistical sigmas, T bounds, external SM references; p13 Eq.(E6) text flux 5.16e6; p14 Eq.(E8) shared pull, NOT adopted [原始网址](https://arxiv.org/abs/2502.10702v2)。

[R5] LI G, SONG C Q, TANG F J, et al. Constraints on neutrino non-standard interactions from COHERENT, PandaX-4T and XENONnT[EB/OL]. arXiv:2409.04703v2, 2024. PDF p5 Eq.(29): flux 5.46(1+-0.12)e6; p6 Table II paired exposure 1.25 conflicts with R2 1.20; choose official R2 [原始网址](https://arxiv.org/abs/2409.04703v2)。

[返回目录](#toc)

<a id="statistics"></a>

## 统计与旧结果的关系

[R1]p20 Eq.(88)所用D是实验拟合信号量，不是原始候选事例数。每个样本有独立12%归一化pull：

$$
\chi^2(\epsilon)=\min_{\{\alpha_k\}}\sum_k\left[
\frac{(D_k-(1+\alpha_k)S_k(\epsilon))^2}{\sigma_k^2}
+\frac{\alpha_k^2}{0.12^2}\right]
=\sum_k\frac{(D_k-S_k(\epsilon))^2}{\sigma_k^2+0.12^2S_k(\epsilon)^2}.
$$

右侧为逐pull解析极小化推导。新版只要求把S换成完整trace前向结果，观测量、误差定义与统计结构不随本轮改变。二维阈值沿用论文p22的Δχ²≤4.61，减联合参数最小值。

| 样本 | D[events] | σ[events] | σα | 来源 |
|---|---|---|---|---|
| PandaX_paired | 3.5 | 1.2985 | 0.12 | [R2]p2/[R3]p5 Table I的拟合信号；σ按[R1]p20的37.1%/37.3%/36.9%乘D |
| PandaX_US2 | 75.0 | 27.975 | 0.12 | [R2]p2/[R3]p5 Table I的拟合信号；σ按[R1]p20的37.1%/37.3%/36.9%乘D |
| XENONnT | 10.7 | 3.9483 | 0.12 | [R2]p2/[R3]p5 Table I的拟合信号；σ按[R1]p20的37.1%/37.3%/36.9%乘D |


实际数组：[拟合信号/误差卡](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json>)。旧v3.4.1的SM信号、χ²和601²区域仍是旧执行记录；新矩阵接口完成且验证后，另存新版结果。当前不声称改文档便已重算，也不预设trace改写会消除论文禁区差异。[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维4.61阈值；p23 Fig.4 [原始网址](https://arxiv.org/abs/2601.19883v2)。

[R2] BO Z, et al. (PandaX Collaboration). First Indication of Solar 8B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: 10.1103/PhysRevLett.133.191001. arXiv:2407.10892v3. PDF p2 abstract fitted yields; p3 exposure and Fig.1 Total curves; Total includes ROI [原始网址](https://arxiv.org/abs/2407.10892v3)。

[R3] APRILE E, et al. (XENON Collaboration). First Indication of Solar 8B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: 10.1103/PhysRevLett.133.191002. arXiv:2408.02877v2. PDF p4 Fig.1 black combined; p5 Table I fitted signal 10.7(-4.2,+3.7); official exposure 3.51 t yr [原始网址](https://arxiv.org/abs/2408.02877v2)。

[返回目录](#toc)

<a id="implementation"></a>

## 程序逐处对应和必须修改的内容

| 程序位置 | 符号/位置 | 已核实行为与必须改什么 |
|---|---|---|
| [state.py](<../../../../extensions/solar_rho_snudd/state.py>) | __call__，第119行 | CURRENT: builds diag(Pee,(1-Pee)/2,(1-Pee)/2); must pass raw full rho instead |
| [ee_vector_nsi.py](<../../../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>) | dsigma_dT，第93行 | CURRENT: scalar SM+rho_ee correction; must call full flavor-kernel trace |
| [differential.py](<../../../../cevns_pyeft/rates/differential.py>) | differential_flavor_kernel_nn，第225行 | AVAILABLE: returns actual incoming-flavor3x3 K, cm2/keV, before state contraction |
| [flavor.py](<../../../../cevns_pyeft/theory/li2026/flavor.py>) | contract_density_kernel_grid，第281行 | AVAILABLE: validated einsum(...ab,...ba), actual Tr(rho K) |
| [solar_nsi.py](<../../../../cevns_pyeft/kernels/solar_nsi.py>) | blocks，第39行 | CURRENT: stores scalar ee coefficients and consumes Pee; new matrix representation required |
| [solar_nsi.py](<../../../../cevns_pyeft/kernels/solar_nsi.py>) | predict，第73行 | CURRENT: calls state_model.pee; full-rho matrix contraction required |
| [solar_nsi.py](<../../../../cevns_pyeft/statistics/solar_nsi.py>) | blocks，第37行 | CURRENT: joint scan uses scalar Pee; must bind the same full-rho trace evaluator |
| [scan.py](<../../../../extensions/solar_rho_snudd/scan.py>) | rho，第77行 | AVAILABLE: same upstream quadrature reconstructs full rho; not currently used by joint-rate blocks |


后续散射入口必须实际执行下面这个结构；这是现有共享API的调用说明，不宣称已替换生产入口：

```python
# Source: raw native flavor density, shape (N_E, 3, 3), no projection.
rho = source.full_rho(E_MeV, epsilon_ee_uV, epsilon_ee_dV)

# Theory/Response: actual K before selecting incoming flavor, cm^2/keV.
K = differential_flavor_kernel_nn(
    nuclear_response, T_keV, E_MeV,
    wc_triplets=point.wc_triplets,  # NP only; SM added once below
    include_sm=True, sin2thetaW=point.sin2thetaW,
).kernel_cm2_per_keV

# Cross section: all flavor entries are retained up to the contraction.
dsigma_dT = contract_density_kernel_grid(rho, K)
```

Source给Slow的IncidentStateBatch.rho须与原ρ包精确相同；Fast须保留K的两个味指标及E轴，收缩采用rho[...,a,b]K[...,b,a]，不能仍读Pee再把旧标量核称为完整矩阵核。若用精确系数分解加速，需展示各味矩阵系数及其与共享振幅的等价核验，并给独立缓存格式/指纹。

本轮只规定以上算法合同。共享函数已存在不等于太阳专用Runtime、Fast与联合统计已接好；不能只改报告中的公式而保留实际执行路径不变。


[源码SHA、精确行号与逐处状态](<../../../../outputs/external/solar_rho_snudd/20261112_trace_onboarding/IMPLEMENTATION_AUDIT.json>)；[完整必改清单与禁用替代](<SNUDD_FULL_TRACE_CONTRACT.v3.5.json>)。

[返回目录](#toc)

<a id="handoff"></a>

## 下一步验收与交接

| 交接项 | 当前状态 | 下一步具体验收 |
|---|---|---|
| ρ来源/数值 | AVAILABLE | 画原始完整矩阵实/虚部、对角元随E；核验trace=1、Hermitian、PSD及质量/味基底变换；不要画投影冒充ρ |
| Source→Runtime | PENDING | 实际source.state_at的每个矩阵元与原SNuDD包一致，包括非对角元 |
| K→截面 | 共享API AVAILABLE，太阳绑定PENDING | 按共享核Response生成K；核验Hermitian/PSD、能区、单位和实际Tr(ρK)，并与直接振幅比对 |
| 矩阵指标 | NOT_RUN | 加入复数非对角正定ρ和K的纯数学测试，抓出ρ_abK_ab、只取对角、丢虚部等错误；不因此扩大物理NSI范围 |
| 单bin事件数 | NOT_RUN | 三样本执行同一双积分，核对逐核素贡献、曝光/通量/Total只用一次；新旧结果另存比较 |
| Fast/联合统计 | NOT_RUN | 新矩阵核与直接Slow逐点比对；统计只消费该同一trace前向；通过后另算/另存区域 |
| 文献精确复现 | 未成立 | 保留两味近似、X尾段和核表外部原件认证边界；不靠归一化或味定义改动贴图 |


当前待办是实现/接入未改，不是缺一份新的ρ数据。用户当前要求先更新本版onboarding；本轮没有修改物理代码、生成新K/ρ图或重算统计。已有数据来源、方法选择和待实现接口已集中在本版，不需要从旧版零散拼接。

[返回目录](#toc)

<a id="references"></a>

## 标准文献与直接来源

[R1] LI G, SONG C Q, TANG F J, YU J H. Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering[EB/OL]. arXiv:2601.19883v2, 2026. PDF p19 Eq.(84); p20 Eqs.(87),(88); p22 Eq.(95)和二维4.61阈值；p23 Fig.4 [原始网址](https://arxiv.org/abs/2601.19883v2)。

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

本版直接读取固定输入卡、原数值表和ρ包，逐文件hash在新版合同及输入审计中。标准引文、具体原文位置、软件/表格转录核验范围分别保留；不把程序字段名、文件存在或hash当成原论文真实性认证。

[返回目录](#toc)
