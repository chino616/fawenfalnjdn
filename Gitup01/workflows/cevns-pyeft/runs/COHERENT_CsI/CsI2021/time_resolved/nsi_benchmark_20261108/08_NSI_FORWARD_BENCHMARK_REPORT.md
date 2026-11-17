# CsI2021 时间分辨 NSI 事例数 benchmark

2026-11-08，Asia/Shanghai。**所列实对称u/d矢量NSI点的前向数值检查通过；严格论文复现仍为待核草稿。** 用户已选择先做未拟合事例数与SM对照。所有结果为信号预测，不是测量或参数区间。

[来源与配置](<NSI_CONFIG.json>) · [核资源审计](<RESOURCE_AUDIT.json>) · [机器验收](<../../../../../../../outputs/csi2021_time_nsi_20261108/VALIDATION_RESULTS.json>) · [参数矩阵](<../../../../../../../outputs/csi2021_time_nsi_20261108/points.json>) · [逐箱CSV](<../../../../../../../outputs/csi2021_time_nsi_20261108/events_99bins.csv>) · [数据字典](<../../../../../../../outputs/csi2021_time_nsi_20261108/DATA_DICTIONARY.json>) · [r2证据](<../P01_EVIDENCE_LEDGER.yaml>)

<a id="report-toc"></a>

## 目录

- [范围与实际计算链](#scope)
- [沿用输入与直接来源](#inputs)
- [NSI定义与测试点](#nsi)
- [24个点的事例数](#counts)
- [数值验收与保留失败](#validation)
- [图和逐箱数据](#figures)
- [限制与下一步输入](#limits)
- [复算与文件归属](#reproduce)

<a id="scope"></a>

## 范围与实际计算链

本轮走validation_only，消费既有r2输入与SM配置。主项目通用predict只支持一维观测：用既有compile_fast生成PE核，再调用既有reconstruct_channels和旧time_acceptance/time_profile生成9×11箱。核形状为(2核素,3入射分量,8响应通道,4算符,4算符,9PE箱)，结果为(24点,2核素,3入射分量,9PE箱,11时间箱)。未修改生产Runtime、核表或冻结参考；本轮工程核未作为正式P08冻结。

[计算入口](<../../../../../../../examples/COHERENT_CsI/time_resolved_nsi/run_benchmark.py>) → [主项目编译器](<../../../../../../../cevns_pyeft/kernels/compiler.py>) → [原生SM与RESPONSE](<../../../../../../../cevns_pyeft/theory/li2026/adapter.py>)；时间权重的原目录和SHA见配置。最终态味求和后仍按入射源分量分配时间，不能把变成τ的末态重新分配成不存在的τ源。

[返回目录](#report-toc)

<a id="inputs"></a>

## 沿用输入与直接来源

全部数值逐项沿用上一轮SM，未套用旧程序的拟合nuisance。完整常数、LEC和SM矩阵保存在本轮配置（直接实施来源为原代码；其外部逐项等价审计未完成）。以下每项的核验范围和来源SHA均随配置保留。

| 输入 | 采用值与单位 | 直接来源及定位 |
|---|---|---|
| 累计POT | 3.198e+23 POT | [S_SUP](<../sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；Supplement p2 lines76–81 |
| 每味每POT产额 | 0.0848 neutrinos/flavor/POT | [S_SUP](<../sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；Supplement p2 lines78–81；10%误差 |
| 基线 | 19.3 m | [S_SUP](<../sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；Supplement p2 lines78–81 |
| 几何稀释后的每味积分注量 | 579361763793233.9 cm^-2 | [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../prepare_records.py>)；p12 Eq29后归一化；prepare_records.py eta表达式 |
| 论文探测器质量 | 14.6 kg | [S_SUP](<../sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；Supplement p2 line81；2211 p12 Eq28段落 |
| Cs/I化学计量 | [1, 1] number ratio | [S_MEAS](<../../../../../../../docs/references/COHERENT/2110.07730v2.pdf>) · [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)；CsI[Na]靶身份；p12 Eq28后靶核计数定义 |
| muon质量 | 105.6583755 MeV | [S_NIST](<../sources/NIST_CODATA2022_allascii.txt>)；allascii line223 |
| 带电pion质量 | 139.57039 MeV | [S_PDG](<../sources/PDG2024_pi_charged.pdf>)；PDF/印刷p1 OUR FIT；误差0.00018MeV |
| prompt谱线能量 | 29.792140909877446 MeV | [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../prepare_records.py>)；p12 Eq29；两体衰变公式 |
| 论文DAR能谱上限 | 52.82918775 MeV | [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)；p12 Eqs28–29，m_mu/2近似 |
| 2211名义弱混合角 | 0.23857 1 | [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)；p3 Sec2.1 Eqs1–3后说明，原文误差(5) |
| nominal淬灭多项式系数 | [0.0554628, 4.30681, -111.707, 840.384] [1,MeV^-1,MeV^-2,MeV^-3] | [S_scintRespCoefficients](<../sources/official/scintRespCoefficients.txt>) · [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)；scintRespCoefficients.txt line7；2211 p12 Eqs30–31前；输入MeVnr，输出MeVee |
| QF拟合适用域 | [2, 70] keVnr | [S_QF_PAPER](<../../../../../../../docs/references/COHERENT/2111.02477v2.pdf>)；Sec8，PDF p23/印刷p21 Fitting approach |
| 光产额 | 13.35 PE/keVee | [S_SUP](<../sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；p3 lines90–93 |
| Gamma展宽参数 | {"a_numerator": 0.0749, "b_slope": 9.56} a=0.0749/Eee(keVee); b=9.56*Eee(keVee) | [S_SUP](<../sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)；Supplement p3 Eq3 lines94–101；2211 p12 Eq31 |
| 官方nominal能量效率系数 | [1.32045, 0.285979, 10.8646, -0.333322] a,d dimensionless; b PE^-1; c PE | [S_effCoefficients](<../sources/official/effCoefficients.txt>)；effCoefficients.txt line7，公式与x=PE见头部line1–4 |
| 时间效率转折及衰减 | [0.52, 0.0494] [us,us^-1] | [S_SUP](<../sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)；Supplement p2 Eq1 lines64–68；2211 p13 Eq33 |
| PE边界 | [0.0, 8.0, 12.0, 16.0, 20.0, 24.0, 32.0, 40.0, 48.0, 60.0] PE | [S_DECISION](<../DECISION_LOG.json>) · [S_SUP](<../sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>)；D_PE；Supplement p5 Fig2水平误差棒 |
| 时间边界 | [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 2.0, 4.0, 6.0] us | [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)；p35 Fig18全部十一面板标签 |
| 端点归箱规则 | "每箱左闭右开，PE60及t6us排除" 1 | [S_DECISION](<../DECISION_LOG.json>) · [S_PREPARE](<../prepare_records.py>)；统一端点的用户要求；histogram筛选实现 |
| 实际调用资源与核素映射 | {"path": "data/responses/responses_all.json", "reader": "cevns_pyeft.nuclear.response.ResponseDB", "nucleus_keys": {"Cs133": "Cs133", "I127": "I"}} 1 | [S_LOCAL_W](<../../../../../../../data/responses/responses_all.json>) · [S_DECISION](<../DECISION_LOG.json>)；原JSON nuclei.Cs133和nuclei.I；D_LOCAL_RESPONSE |
| 源表示选择 | "DAR解析谱 × ROOT各味时间边缘" 1 | [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>) · [S_DECISION](<../DECISION_LOG.json>)；p12 Eq29、p13 Eq32；D_REUSE |
| 平移后的时间归一分母 | "固定零位移0–6us参考分数" 1 | [S_TIME_CODE](<../evidence/legacy_resolution/code/time_acceptance.py>) · [S_2211](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)；time_acceptance.build_time_weights的nominal参考分数；论文p13脚注8未给完整程序细节 |
| 反冲积分域保护 | [2, 70] keVnr | [S_QF_PAPER](<../../../../../../../docs/references/COHERENT/2111.02477v2.pdf>) · [S_DOMAIN_CODE](<../evidence/legacy_resolution/code/analysis_inputs.py>)；校准Sec8；analysis_inputs.py guards；DAR上界还受运动学约束 |

核结构直接采用用户指定的 [原responses_all.json](<../../../../../../../data/responses/responses_all.json>)，SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。读取器按(p,n)行列和升幂系数使用数组；q为GeV、b为GeV⁻¹、y=(qb/2)²，指数因子−2，系数无量纲。外部作者生成链未核实；本次原表复用有用户明确选择。完整16个数组见 [逐值NPZ](<../data/nuclear_response_CsI.npz>)；以下示例和shape直接回读原JSON。

| 核素 | 实际核表与代表值 | 通道和完整资源 |
|---|---|---|
| Cs133 | b=11.6443349607501 GeV⁻¹；M_pp系数前三项=[3024.998274020381, -11027.633404691845, 15552.131264975062] | {"Delta": [2, 2, 9], "M": [2, 2, 11], "MPhiPP": [2, 2, 10], "PhiPP": [2, 2, 9], "PhiPT": [2, 2, 9], "SigmaP": [2, 2, 11], "SigmaPDelta": [2, 2, 10], "SigmaPP": [2, 2, 11]}；[逐数组定位和归一化](<../data/nuclear_response_inventory.json>) |
| I | b=11.5660479522363 GeV⁻¹；M_pp系数前三项=[2808.9995665607275, -10034.66474862081, 13985.083771812386] | {"Delta": [2, 2, 9], "M": [2, 2, 11], "MPhiPP": [2, 2, 10], "PhiPP": [2, 2, 9], "PhiPT": [2, 2, 9], "SigmaP": [2, 2, 11], "SigmaPDelta": [2, 2, 10], "SigmaPP": [2, 2, 11]}；[逐数组定位和归一化](<../data/nuclear_response_inventory.json>) |

核数沿用当前模型：Cs133、I127各约3.38166366×10²⁵；质量和核计数算法见 [归一化台账](<../sm_benchmark_20261107/NORMALIZATION_LEDGER.json>)。未另加Helm、核半径修正、曝光或acceptance。官方ROOT原始网址和对象/轴域已在 [P00来源](<../P00_SOURCE_REGISTER.yaml>) 与 [ROOT实际数组目录](<../data/ROOT_inventory.json>) 中保留；本轮只采用其三主味时间边缘，能谱用2211 Eq.(29)解析DAR。

[返回目录](#report-toc)

<a id="nsi"></a>

## NSI定义与测试点

文献基准为V. De Romeri et al., *Physics implications of a combined analysis of COHERENT CsI and LAr data*, JHEP04(2023)035，[2211.11905v2本地PDF](<../../../../../../../docs/references/COHERENT/2211.11905v2.pdf>)，[原始网址](https://arxiv.org/abs/2211.11905v2)，PDF第5页Sec.2.2、式(5)–(6)。它给出矢量NSI定义；不提供本轮24点的预期事件表。

本轮调用 [旧程序vector_nsi_wilson](<../../../../../../../../../260929Gitup1-CONUS-2/Gitup01/src/cevns_pyeft/experiments/coherent/2021CsI_root_time/kernels/vector_nsi.py>)，将上述定义与项目LEFT约定匹配（项目转换关系，非论文原样公式）：

$$
\Delta C_{61q}[f,i]=-\sqrt{2}\,G_F(\epsilon^{qV})^{\mathsf T}[f,i],\qquad q=u,d.\tag{1}
$$

| 符号/配置 | 实际值、单位及直接来源 |
|---|---|
| ε | 实对称3×3无量纲矩阵，味顺序(e,μ,τ)；[points.json全部矩阵](<../../../../../../../outputs/csi2021_time_nsi_20261108/points.json>)。上三角以对称方式复制到下三角，其余为0 |
| G_F | 1.1663787e-05 GeV⁻²；[项目常数](<../../../../../../../cevns_pyeft/foundation/constants.py>)，运行时SciPy常数表；原SM配置保存实际解析值和来源范围 |
| ΔC61q | 额外NSI项，GeV⁻²，原生算符(6,1,u/d)，矩阵轴[final,initial]；NPZ coefficients_GeV_minus2存储的是SM+NSI总矩阵，减去point0矩阵才是ΔC |
| SM | include_sm=True，保留原SM vector/axial；仅叠加NSI vector。编译基底为(6,1,u),(6,1,d),(6,2,u),(6,2,d) |

因εV=εL+εR且夸克PL/PR各含1/2矢量流，项目采用−√2GF。实对称范围内转置数值不变；当前检查不认证一般复数相位或非矢量EFT。

前8点只取 [旧benchmark_points.json](<../../../../../../../../../260929Gitup1-CONUS-2/Gitup01/src/cevns_pyeft/experiments/coherent/2021CsI_root_time/benchmarks/results_fine/benchmark_points.json>) 的name/point字段，逐行定位见points.json；不采用旧χ²或拟合nuisance。旧scan_branch坐标只作历史诊断点，不标为本轮或论文最佳拟合。4个u对角边角为项目精度域选择(−0.4或0.8)²，直接位置为 [旧precision_points](<../../../../../../../../../260929Gitup1-CONUS-2/Gitup01/src/cevns_pyeft/experiments/coherent/2021CsI_root_time/tools/resolve_input_issues.py>) 第244–249行；其余12点为本轮run_benchmark.py::benchmark_points明确设计的有限测试刺激，均非文献测量。两组的直接代码SHA和定位也存入NSI_CONFIG。

[返回目录](#report-toc)

<a id="counts"></a>

## 24个点的事例数

主约定：零平移0–6μs参考窗注量，PE∈[0,60)、t_rec∈[0,6)μs。最细网格SM为 **353.465577772 events**；相同数值eta改作全支撑域注量时为 **329.016330343 events**。两种注量含义分别保存，不能混用。

下表ε只列上三角非零值；非对角元素均含对称伴项，未列项为0。完整有效位数、来源kind、Cs/I与各入射味总数见 [summary.csv](<../../../../../../../outputs/csi2021_time_nsi_20261108/summary.csv>) 和 [points.json](<../../../../../../../outputs/csi2021_time_nsi_20261108/points.json>)。

| 点 | 非零ε（无量纲） | 信号事例 | NSI/SM | ΔN |
|---|---|---:|---:|---:|
| SM | all zero | 353.465578 | 1.000000 | +0.000000 |
| mu_cancellation | u:mu,mu=0.2 | 117.157649 | 0.331454 | -236.307929 |
| electron_compensation | u:e,e=-0.12; u:mu,mu=0.2 | 305.425283 | 0.864088 | -48.040295 |
| mu_sign_flip | u:mu,mu=0.4 | 380.216334 | 1.075681 | +26.750757 |
| legacy_scan_branch_0 | u:e,e=0.002854992041426147; u:mu,mu=0.0184604881163346 | 307.335887 | 0.869493 | -46.129690 |
| legacy_scan_branch_1 | u:e,e=0.003550157067839762; u:mu,mu=0.3722235851030103 | 309.602899 | 0.875907 | -43.862679 |
| legacy_scan_branch_2 | u:e,e=0.3864453745855023; u:mu,mu=0.01801828188493387 | 308.284436 | 0.872177 | -45.181142 |
| legacy_scan_branch_3 | u:e,e=0.3857981786304465; u:mu,mu=0.3726273386665798 | 310.530284 | 0.878530 | -42.935293 |
| u_domain_corner_0 | u:e,e=-0.4; u:mu,mu=-0.4 | 3296.740933 | 9.326908 | +2943.275355 |
| u_domain_corner_1 | u:e,e=-0.4; u:mu,mu=0.8 | 3376.993203 | 9.553952 | +3023.527625 |
| u_domain_corner_2 | u:e,e=0.8; u:mu,mu=-0.4 | 3336.212312 | 9.438578 | +2982.746734 |
| u_domain_corner_3 | u:e,e=0.8; u:mu,mu=0.8 | 3416.464582 | 9.665622 | +3062.999004 |
| d_ee_plus | d:e,e=0.1 | 258.549921 | 0.731471 | -94.915657 |
| d_ee_minus | d:e,e=-0.1 | 523.544306 | 1.481175 | +170.078728 |
| d_mumu_plus | d:mu,mu=0.1 | 161.152413 | 0.455921 | -192.313165 |
| d_mumu_minus | d:mu,mu=-0.1 | 698.077318 | 1.974951 | +344.611740 |
| u_emu_plus | u:e,mu=0.1 | 446.690054 | 1.263744 | +93.224476 |
| u_emu_minus | u:e,mu=-0.1 | 446.690054 | 1.263744 | +93.224476 |
| d_emu_plus | d:e,mu=0.1 | 467.196401 | 1.321759 | +113.730823 |
| d_emu_minus | d:e,mu=-0.1 | 467.196401 | 1.321759 | +113.730823 |
| d_etau | d:e,tau=0.1 | 391.047114 | 1.106323 | +37.581536 |
| d_mutau | d:mu,tau=0.1 | 429.614866 | 1.215436 | +76.149288 |
| mixed_ud_emu | u:e,mu=0.1; d:e,mu=-0.05 | 372.163800 | 1.052900 | +18.698223 |
| tau_diagonal_control | u:tau,tau=0.2 | 353.465578 | 1.000000 | +0.000000 |

μ对角正耦合在约0.2处明显压低μ源贡献；eμ非对角±号给出相同增量，eτ仅改变νe入射项，μτ仅改变νμ/反νμ项；ττ对角在无τ源时恢复SM。以上是当前原生模型的计算行为，不能替代实验约束。

[返回目录](#report-toc)

<a id="validation"></a>

## 数值验收与保留失败

| 检查 | 实际结果与范围 |
|---|---|
| 原始Slow对照 | 全24点，16/40 pilot网格；最大核素/源/箱差异7.8159701e-14 events。仅证明同网格方法等价，pilot不作精度冻结 |
| 原始系数能量求值对照 | pilot与256/480同网格全24点最大差异4.97379915×10⁻¹⁴ events；[逐项记录](<../../../../../../../outputs/csi2021_time_nsi_20261108/COEFFICIENT_ENERGY_EQUIVALENCE.json>) |
| 最终网格 | {"n_er": 1024, "n_enu": 1920, "n_observed_bin": 512, "observed_step": 0.03125, "recoil_min_keV": 2.0, "strategy": "legacy_csi2021_v1"}；QF下限2keVnr，运动学端点不变 |
| 整体加密 | grid_512_960→grid_1024_1920；全24点最大总信号箱误差0.00108254136，分量箱误差0.000665052166 events |
| 独立recoil积分 | 全24点最大总箱差0.000191110406，分量箱差0.00045833589 events；均<0.005 |
| 独立neutrino_energy积分 | 全24点最大总箱差0.00143479441，分量箱差0.000511082375 events；均<0.005 |
| 独立PE积分 | 全24点最大总箱差0.000833052931，分量箱差0.000239635104 events；均<0.005 |
| Runtime回归 | 24项通过，0失败；[JUnit](<../../../../../../../outputs/csi2021_time_nsi_20261108/runtime-tests.xml>)、[实际日志](<../../../../../../../outputs/csi2021_time_nsi_20261108/runtime-tests.log>) |
| 输入保护 | 126个原package/helper Python文件未变；原响应与P00指纹审计见资源记录 |

保留未通过项：512/960网格在最强u对角角点的独立Eν检查为0.00514593365 events/bin，超过0.005；[失败记录](<../../../../../../../outputs/csi2021_time_nsi_20261108/REJECTED_GRID_512_CHECKS.json>)和原网格均保留。此次通过来自加密积分，没有放宽门限。

仅对所列24点验收，未验证连续参数域。为控制运行时间，本轮消费者对四个dim6算符的E²H(E)作二次重构，每个反冲用3个原生定义点与4个原生holdout（含两端点）逐张量检验，rtol=2×10⁻¹⁰、atol=2×10⁻¹²；失败就回到原始能量数组。原始Slow不使用此捷径；生产编译器未改。检查统计与代码SHA在配置内。

[返回目录](#report-toc)

<a id="figures"></a>

## 图和逐箱数据

图中仅画信号；分箱宽度不相同，PE和时间投影分别除以真实ΔPE和Δt。曲线是本次计算，不是论文数字化或拟合结果。图注与 [PLOT_MANIFEST](<../../../../../../../outputs/csi2021_time_nsi_20261108/PLOT_MANIFEST.json>) 连接输入、点定义与生成代码。

![NSI与SM投影](<../../../../../../../outputs/csi2021_time_nsi_20261108/figures/nsi_sm_projections.png>)

[11个时间窗PNG](<../../../../../../../outputs/csi2021_time_nsi_20261108/figures/nsi_time_slices.png>) · [味分量变化PNG](<../../../../../../../outputs/csi2021_time_nsi_20261108/figures/nsi_flavor_changes.png>) · [矢量图SVG](<../../../../../../../outputs/csi2021_time_nsi_20261108/figures/nsi_sm_projections.svg>)

[99箱比较CSV](<../../../../../../../outputs/csi2021_time_nsi_20261108/events_99bins.csv>)（24×99行） · [核素/源逐箱CSV](<../../../../../../../outputs/csi2021_time_nsi_20261108/components_99bins.csv>)（24×2×3×99行） · [PE投影](<../../../../../../../outputs/csi2021_time_nsi_20261108/PE_projection.csv>) · [时间投影](<../../../../../../../outputs/csi2021_time_nsi_20261108/time_projection.csv>) · [全部NPZ](<../../../../../../../outputs/csi2021_time_nsi_20261108/benchmark.npz>)。轴、单位、列定义、归一化与来源链见数据字典。

[返回目录](#report-toc)

<a id="limits"></a>

## 限制与下一步输入

本轮已具备所列实对称矢量NSI点的未拟合信号预测和SM对照。BRN/NIN未缩放到18.4/5.6，本轮不使用背景、不计算likelihood。原生SM含axial/RESPONSE，尚未与论文辐射修正/Helm逐项等价，不能据此宣布严格复现2211图或官方统计。原表外部导出链继续未核，按用户选择直接复用本地data。PE边界保留为用户指定重建值，不升级为官方原始发布边界。

| 下一步能力 | 仍需信息或审查 | 当前可执行范围 |
|---|---|---|
| 更多未拟合实对称u/d NSI点 | 明确矩阵；每点重跑同一精度检查 | 可沿本轮链计算，不能默认域内已全验收 |
| 统计拟合/区间 | BRN/NIN的曝光、效率、时间归一与18.4/5.6的物理闭合；nuisance域、非负约束、阈值/分支 | 尚未执行，本轮不提供约束 |
| 严格2211论文benchmark | 独立Helm/辐射修正配置，论文参考逐箱曲线及可核验误差，时间零点与核半径处理 | 继续待补，不由本轮数值PASS认证 |
| 完整ROOT能量—时间模型 | 对照联合分布与当前DAR×时间边缘的逐箱差异，并审阅适用源选择 | 当前采用既定因子化源，未宣称ROOT二维相关被保留 |
| 一般复数/非矢量EFT或正式Fast冻结 | 对应理论与能力合同、独立Slow、参数域和人工审查 | 本轮不覆盖 |

[r2全部缺口](<../P02_MISSING_AND_CONFLICTS.md>)保留原状态；本轮不改写此前背景与论文等价问题。

[返回目录](#report-toc)

<a id="reproduce"></a>

## 复算与文件归属

以下命令从主项目根执行，路径中的OLD为用户指定旧目录 `.../260929Gitup1-CONUS-2/Gitup01/src/cevns_pyeft/experiments/coherent/2021CsI_root_time`。需numpy/scipy，原文/ROOT指纹回读还需PyYAML/uproot；绘图需matplotlib。为保留旧结果，RUN使用新目录。实际Python、依赖与命令另见本次运行环境记录。

```powershell
python -B examples/COHERENT_CsI/time_resolved_nsi/run_benchmark.py --legacy-time-dir OLD --output-dir RUN/pilot --n-er 16 --n-enu 40 --n-pe-bin 12 --pe-step 2
# 原生和checked pilot、256/480、512/960及最终1024/1920各独立目录；完整顺序见示例README
python -B examples/COHERENT_CsI/time_resolved_nsi/validate_benchmark.py --legacy-time-dir OLD --run-dir RUN --stage native
python -B examples/COHERENT_CsI/time_resolved_nsi/validate_benchmark.py --legacy-time-dir OLD --run-dir RUN --stage precision --finest grid_1024_1920
python -B examples/COHERENT_CsI/time_resolved_nsi/summarize_benchmark.py --run-dir RUN
python -B examples/COHERENT_CsI/time_resolved_nsi/plot_benchmark.py --run-dir RUN
```

[示例与可复算代码](<../../../../../../../examples/COHERENT_CsI/time_resolved_nsi/README.md>) · [本轮完整输出](<../../../../../../../outputs/csi2021_time_nsi_20261108/README.md>) · [主线计算记录](<README.md>) · [之前SM报告](<../../../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md>)。所有report副本从本脚本同源生成，路径按输出位置调整。

[返回目录](#report-toc)
