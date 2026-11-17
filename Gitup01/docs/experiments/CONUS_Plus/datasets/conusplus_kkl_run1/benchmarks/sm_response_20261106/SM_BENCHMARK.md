# CONUS+ 标准模型事例谱 v1（隔离候选，2026-11-06）

本版使用项目现有 Nuclear Response 与 Slow 管线，沿用天然锗五同位素和已选定的非负 Flux。输入直接来源、精确定位和未闭合的原始出处在各节可见。

<a id="report-toc"></a>

## 目录

- [结果与事例谱](#section-1)
- [现有流程与归一化](#section-2)
- [Source 数值与来源](#section-3)
- [Target 与理论配置及来源](#section-4)
- [探测器与观测数据来源](#section-5)
- [网格与数值验证](#section-6)
- [19箱与论文比较](#section-7)
- [仍需核实与下一步数据](#section-8)
- [复算与标准参考文献](#section-9)

<a id="section-1"></a>

## 结果与事例谱

| 量 | 结果与单位 | 口径 |
| --- | --- | --- |
| SM CEνNS 合计 | 149.419400 events | 1 kg、119 days、160–350 eVee |
| 论文蓝线纵值合计 | 152.092947 | 19 个中心取点，kg⁻¹(10 eVee)⁻¹ |
| 总量相对差 | -1.7578% | 本次／论文图线 − 1 |
| 逐箱比值范围 | 0.452219–1.050245 | 无拟合归一化 |

![SM 事例谱](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/conusplus_sm_event_spectrum.png>)

[19 箱数据](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/sm_counts_19bins.csv>) · [完整结果 JSON](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/summary.json>) · [逐输出溯源](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/OUTPUT_PROVENANCE.json>)

计算结果属于来源限制已标明的项目模型基准候选。数值收敛与论文物理复现分别记录。本次只计 CEνNS，SM 电子散射沿用 Ref.[1] PDF p.10 的 O(0.1) events 忽略近似。

谱形仍有明显差异。330–340 eVee箱的本次预测比原图蓝线约低54.8%，绝对差约0.43 events。该差异大于已检查的数值积分误差，具体来源仍待作者数值谱或代码核对。

[返回目录](#report-toc)

<a id="section-2"></a>

## 现有流程与归一化

| 阶段 | 本次工作 | 实际结果 |
| --- | --- | --- |
| Phase 0 | 恢复 conusplus_kkl_run1，选择原有 Slow executor | 已保存实施计划与输入指纹 |
| P01 | 19 箱、eVee、signed excess 数据语义 | 按原图取点表读入 |
| P02 | 天然 Ge 五同位素、核数和曝光 | 核数与质量归一化检查通过 |
| P03 | 已准备的非负反应堆谱 | 生成脚本 --check 与注量积分检查通过 |
| P04–P05 | 原有 Li2026LegacyInteraction、五个 Response key | SM 适用约定、基底、单位和运动学检查通过 |
| P06 | Lindhard + Gaussian 箱概率 adapter | CDF 与独立箱内积分一致，窗外损失保留 |
| P07 | 项目 core.predict，backend=slow | 最终网格及独立加密结果见数值节 |
| P10 | 图线对照、来源和能力检查 | 已产出本报告与阶段交接，科学来源状态 PARTIAL |
| P08、P09 | 本次未请求 | NOT_RUN / NOT_REVIEWED |

实际调用为 `ExperimentModel → core.predict.predict → rates.recoil.integrate_recoil_yield → Li2026LegacyInteraction → rates.folding.probability_fold`。源表、核表和共享包来自独立 snapshot。

本次新增的探测器 adapter 只返回无量纲箱概率。真实反冲直接以 keV 积分，Lindhard 映射进入箱概率，因此折叠时不再另乘 dT/dEee。

归一化路径为探测器处每秒通量 × 119×86400 秒 → 每核反冲产额 → 1 kg 中各同位素核数 → 重建箱概率。图中纵值由 Nᵦ / 1 kg × 10 eVee / ΔEᵦ 得到，本次 ΔEᵦ=10 eVee，因此数值等于逐箱事件数。

[阶段报告目录](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/sm_response_20261106/phase_reports/README.md>) · [实施计划](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/sm_response_20261106/EXECUTION_PLAN.json>) · [输入与代码快照](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/sm_response_20261106/INPUT_SNAPSHOT.json>)

[返回目录](#report-toc)

<a id="section-3"></a>

## Source 数值与来源

| 输入 | 实际值／数组 | 单位 | 直接数值文件 | 来源定位与核验范围 |
| --- | --- | --- | --- | --- |
| 粒子与入射态 | ν̄ₑ，ρ=diag(1,0,0) | 1 | [装配代码](<../../../../../../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py>) | Ref.[1] PDF p.8 的源描述，固定电子味 |
| 总通量 | 1.5×10¹³ | cm⁻² s⁻¹ | [配置](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>) | Ref.[1] PDF p.8，探测器处绝对通量 |
| 源能区与拼接 | 0–10，2 MeV 拼接 | MeV | [默认谱](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/reactor_flux_default.csv>) | Ref.[1] PDF p.9；具体拼接算法直接来自 Ref.[4] Flux 节 |
| 低能节点 | 32 点，E=0.010–2.000；首点(0.010,0.0774) | MeV，relative shape | [全部节点](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/kopeikin_low_energy_transcribed.csv>) | Ref.[4] Table 2，PDF p.6；与 Ref.[3] 原始数表的对应仍待核实 |
| 高能系数 | 4×6，U235 首行为 3.217,−3.111,1.395,−0.3690,0.04445,−0.002053 | 指数用 E/MeV | [全部系数](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/mueller_coefficients.csv>) | Ref.[2] Eq.(12)、Table VI、PDF p.13，24/24 已核验 |
| 参考裂变份额 | U235/U238/Pu239/Pu241=0.56/0.07/0.31/0.06 | number fraction | [份额](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/fission_fractions.csv>) | Ref.[4] Eqs.(1.22)–(1.25)，按用户要求采用该笔记 Flux 方案 |
| 低能端点与插值 | 补(0,0)，分段线性，范围外0 | 同各轴 | [生成器](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/build_inputs.py>) | Ref.[10] D_V2_003 用户决定 |
| 最终源数组 | 10001×2 数值列，步长0.001；归一化积分6.461600041891649 | MeV；cm⁻² s⁻¹ MeV⁻¹ | [默认谱](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/reactor_flux_default.csv>) | 上述表与算法的项目派生；CSV 积分相对误差1.21×10⁻⁸ |
| 原笔记线性外推对照 | 0–0.00653846 MeV 有负谱，保留为诊断 | 同默认谱 | [有符号对照](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/reactor_flux_reference_linear_extrapolation.csv>) | Ref.[4] 原线性外推和 Ref.[10] 用户决定；本次物理源使用非负默认谱 |

Ref.[1] 为 De Romeri、Papoulias、Sanchez Garcia，Phys. Rev. D 111, 075025 (2025)。Ref.[2] 为 Mueller et al.，Phys. Rev. C 83, 054615 (2011)。Ref.[4] 为用户提供的未发表 CONUS+ 项目笔记。标准引文与本地原文见文末。

[返回目录](#report-toc)

<a id="section-4"></a>

## Target 与理论配置及来源

| 核素／Response key | 数丰度 | NIST 原子质量 / u | 运动学质量 / GeV | 1 kg 中核数 | ROI 事例数 |
| --- | --- | --- | --- | --- | --- |
| Ge70 | 0.2057 | 69.92424875 | 65.2045872604 | 1.7056259646e+24 | 31.267456 |
| Ge72 | 0.2745 | 71.922075826 | 67.0675754678 | 2.2761027091e+24 | 41.304658 |
| Ge73 | 0.0775 | 72.923458956 | 67.9990695716 | 6.4261551897e+23 | 11.707179 |
| Ge74 | 0.365 | 73.921177761 | 68.9305636753 | 3.0265117990e+24 | 53.966883 |
| Ge76 | 0.0773 | 75.921402726 | 70.7935518827 | 6.4095715634e+23 | 11.173223 |

数丰度来自 Ref.[1] PDF p.9 和 Ref.[5] 各同位素行，原子质量来自 Ref.[5]。[配置](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>) 和 [库存原表](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/natural_ge_inventory.csv>) 保存直接值。平均原子质量为72.6275501646868 u，核数由数丰度除以加权原子质量与原子质量常数推导。

本次沿用现有引擎的运动学、振幅和相空间统一 A×u 约定。NIST 原子质量用于每公斤核数。onboarding 库存表中的原子质量减32个电子质量是另存的核质量估算，本次未作为运动学输入。两种运动学质量数值相差 0.1267%–0.1335%，此处不把质量差直接解释成事例数差。

| 输入／模块 | 实际选择与数值 | 直接来源与适用范围 |
| --- | --- | --- |
| 理论模块 | li2026_legacy，SM=True，所有 BSM 系数=0，p/n 基底 | [adapter](<../../../../../../../cevns_pyeft/theory/li2026/adapter.py>)，Ref.[7] Eqs.(75)–(78) 为理论来源 |
| 核表 | Ge70/72/73/74/76，各8个通道，每通道2×2多项式矩阵 | [直接 JSON](<../../../../../../../data/responses/responses_all.json>)，Ref.[8]；原始核计算链待核实 |
| 振子长度 b / GeV⁻¹ | Ge70=10.618824284005962；Ge72=10.661038969384785；Ge73=10.68180034434144；Ge74=10.702338447286174；Ge76=10.74276575001275 | 直接 JSON 五个 basic.b，执行 y=(qb/2)² |
| 核自旋 J | Ge70=0；Ge72=0；Ge73=4.5；Ge74=0；Ge76=0 | 直接 JSON 五个 basic.J，核响应的原始多体计算链仍待核实 |
| SM 非零响应 | M；Ge73 另有 SigmaP 与 Delta，按现有公式计算 | [amplitude](<../../../../../../../cevns_pyeft/theory/li2026/amplitude.py>) 和 [particle responses](<../../../../../../../cevns_pyeft/theory/li2026/responses.py>) |
| SigmaPDelta | 现有实现的粒子响应恒为0 | responses.py::_response_polynomials 的显式取零约定 |
| 弱角 | sin²θW=0.23857 | Ref.[1] PDF p.3 的低能 SM 参考值 |
| Fermi 常数 | 1.166378700e-05 GeV⁻² | Ref.[6] Fermi coupling constant 行，运行时 constants.G_F |
| 活跃 LEC | L1=1.855，L2=−1.017，L3=0.6377，L4=−0.220 | Ref.[7] Table II，PDF p.8；直接值见 DEFAULT_LECS |
| 核子质量 | mN=0.938918755685 GeV | 项目 constants.m_N=(m_p+m_n)/2，m_p/m_n 由 SciPy CODATA 常数提供；Ref.[6] 对应行 |
| cm² 换算 | 1 GeV⁻²=3.893793721000e-28 cm² | 运行时 constants.GEV_INV2_TO_CM2；精确执行值来自固定版本代码 |
| ν／反ν | 共用该引擎的 rate kernel | Ref.[7] PDF p.21、Eq.(92) 后一段明确采用该事例率约定；本次保留其近似范围 |

Ref.[7] 为 G. Li、C.-Q. Song、F.-J. Tang、J.-H. Yu，arXiv:2601.19883v2 (2026)。本地 Response 表已包含所选核响应，计算按该资源直接收缩。Ref.[1] 使用 Klein–Nystrand 形状因子，该差别和用户指定的 Flux 配方均须保留在论文对照的解释中。

[运行时理论检查和全部数值](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/validation.json>) · [实际模型与网格](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/fine_641.json>)

[返回目录](#report-toc)

<a id="section-5"></a>

## 探测器与观测数据来源

| 输入 | 实际数值与单位 | 数值文件／来源定位 | 核验范围 |
| --- | --- | --- | --- |
| 有效质量和曝光 | 1 kg；119 kg·day，即119 days | [配置](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>)；Ref.[1] PDF p.10 | 图1有效探测器处方 |
| 日到秒 | 86400 s/day，live=10281600 s | Ref.[9] Table 8 的 day 行，运行时 LiveTimeExposure | 曝光只进入 for_run 一次 |
| 重建量与分箱 | 160–350 eVee，19箱，10 eVee/箱 | Ref.[1] pp.9–10、Fig.1；[CSV](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/sm_counts_19bins.csv>) | 箱中心165..345，完整边界从中心±5导出 |
| Lindhard | k=0.162，Z=32，ε=11.5 Z^(−7/3) T_keV | Ref.[1] Eq.(31)，PDF p.9；[adapter](<../../../../../../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py>) | 均值 Eee=Q(T)T；k 的不确定度未在本次扫描 |
| Gaussian 宽度 | σ0=20.38 eVee，F=0.1096，η=2.96 eVee | Ref.[1] Eqs.(29)–(30)，PDF p.9 | σ²=σ0²+FηEee_true，采用真电离能 |
| 效率 | 分析箱内1 | Ref.[1] PDF p.9 的阈值以上约100%处方 | 按论文有效探测器近似 |
| 真电离能下界 | 2.96 eVee，对应T=0.027249421141 keV | Ref.[1] PDF p.9；数值反解 Eq.(31) | [低能尾部诊断](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/validation.json>) |
| 响应概率 | 161×19／同位素，共5套真反冲轴 | 由Gaussian CDF箱积分派生；[诊断CSV](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/true_recoil_and_response.csv>) | 窗外损失保留，ROI内未重归一化 |
| 观测点和误差 | 19点，上下误差各19项，保留6个负中心值 | [原数字化CSV](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/statistics/conusplus_2501_17843v3_fig1_digitized.csv>) | Ref.[1] Fig.1 黑点和误差棒；本次仅绘图对照 |

上述实验数值均直接定位到 De Romeri、Papoulias、Sanchez Garcia，Phys. Rev. D 111, 075025 (2025) 的对应页、公式或图。数值采用范围为该论文的有效探测器预测处方。

[返回目录](#report-toc)

<a id="section-6"></a>

## 网格与数值验证

| 计算版本 | 每核素反冲点 | 均匀 Eν 点 | ROI 总事例数 | 运行秒 |
| --- | --- | --- | --- | --- |
| base | 81 | 161 | 149.027869847 | 129.1 |
| energy_refined | 81 | 321 | 149.347399833 | 249.8 |
| recoil_refined | 161 | 161 | 149.036669718 | 250.4 |
| fine | 161 | 321 | 149.341528533 | 261.7 |
| energy_641 | 81 | 641 | 149.416569018 | 195.5 |
| fine_641 | 161 | 641 | 149.419399803 | 366.9 |

Eν 网格为均匀网格与已登记低能节点、2 MeV 和8 MeV断点的并集。不同反冲点按精确运动学下界选择 Eν 子网格。真反冲上界取10 MeV入射的两体端点，各核素独立。

| 独立加密 | 最大逐箱相对差 | 最大逐箱绝对差 / events | 预定条件 |
| --- | --- | --- | --- |
| E_nu_at_fine_recoil | 0.150843% | 0.01525515 | |ΔN|≤10⁻⁴+0.003|N|，通过 |
| recoil_at_fine_E_nu | 0.011404% | 0.00103002 | |ΔN|≤10⁻⁴+0.003|N|，通过 |
| both_from_321_energy_grid | 0.178058% | 0.01704661 | |ΔN|≤10⁻⁴+0.003|N|，通过 |

初始161→321能量网格的最大逐箱变化约0.600%，未达到预设条件，因此追加641点网格并保留全部旧输出。重建箱积分由Gaussian CDF解析给出，与独立数值积分的最大绝对差为 1.388e-16。未计入主结果的低于2.96 eVee真电离能尾部，诊断总贡献为 2.832e-11 events。

[全部检查](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/validation.json>) · [网格加密记录](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/sm_response_20261106/NUMERICS_REVISION_2.json>)

[返回目录](#report-toc)

<a id="section-7"></a>

## 19箱与论文比较

| 箱 | 范围 / eVee | 本次SM / events | 论文SM图线纵值 | 本次／论文 |
| --- | --- | --- | --- | --- |
| 1 | 160–170 | 33.854427 | 32.234786 | 1.050245 |
| 2 | 170–180 | 26.285171 | 25.110359 | 1.046786 |
| 3 | 180–190 | 20.439495 | 19.671628 | 1.039034 |
| 4 | 190–200 | 15.902642 | 15.489978 | 1.026641 |
| 5 | 200–210 | 12.368914 | 12.254218 | 1.009360 |
| 6 | 210–220 | 9.609926 | 9.735876 | 0.987063 |
| 7 | 220–230 | 7.452998 | 7.765560 | 0.959750 |
| 8 | 230–240 | 5.766215 | 6.216576 | 0.927555 |
| 9 | 240–250 | 4.447893 | 4.993424 | 0.890750 |
| 10 | 250–260 | 3.419056 | 4.023605 | 0.849749 |
| 11 | 260–270 | 2.617952 | 3.251726 | 0.805096 |
| 12 | 270–280 | 1.996029 | 2.635209 | 0.757446 |
| 13 | 280–290 | 1.514950 | 2.141153 | 0.707539 |
| 14 | 290–300 | 1.144368 | 1.744008 | 0.656171 |
| 15 | 300–310 | 0.860227 | 1.423834 | 0.604163 |
| 16 | 310–320 | 0.643465 | 1.165006 | 0.552328 |
| 17 | 320–330 | 0.478992 | 0.955225 | 0.501444 |
| 18 | 330–340 | 0.354891 | 0.784777 | 0.452219 |
| 19 | 340–350 | 0.261788 | 0.495999 | 0.527800 |

论文蓝线从固定PDF的矢量路径提取，逐箱按中心取值，来源为 Ref.[1] Fig.1。末端路径止于345 eVee，末值按该端点关联到名义340–350箱。第一个箱160–162.5 eVee的微小额外平台保存在来源追踪中，165 eVee中心取对应主平台。本表是与图线的数值比较，其小数位数只用于可重复计算。

[蓝线CSV](<../../../../../../../data/benchmarks/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/benchmark/conusplus_2501_17843v3_fig1_sm_digitized.csv>) · [蓝线逐段来源](<../../../../../../../data/benchmarks/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/benchmark/conusplus_2501_17843v3_fig1_sm_digitized.provenance.json>)

| 探测器 | kg | days | 阈值 / eVee | 本次阈值至350 eVee / events | 论文所报总量 |
| --- | --- | --- | --- | --- | --- |
| C2 | 0.95 | 117 | 180 | 83.390336 | 90 |
| C3 | 0.94 | 110 | 160 | 129.831647 | 143 |
| C5 | 0.94 | 119 | 170 | 108.631074 | 113 |

本次按 Ref.[1] PDF p.8 的质量、天数和阈值，从同一每kg每天谱派生，三探测器合计 321.853057 events。论文p.10报告346 events。这组总量包含不同曝光与阈值，图线19个纵值的合计使用1 kg有效探测器口径。逐探测器派生只覆盖本次上界350 eVee，原文“全部箱”的上界口径仍需作者数表核对。

[返回目录](#report-toc)

<a id="section-8"></a>

## 仍需核实与下一步数据

| 事项 | 现有材料 | 仍需补充什么 | 影响 |
| --- | --- | --- | --- |
| 低能谱上游出处 | 32节点已与用户笔记Table2核对 | Kopeikin原始对应图／表或作者数值文件 | 绝对归一化和来源真实性的正式原文核验 |
| Ge核表上游出处 | 本地JSON、key、哈希、低q归一化和基底检查 | 原作者核计算数据、生成／转换脚本和归一化说明 | 正式Nuclear Response物理来源认证 |
| 实验作者数表 | 19黑点／误差棒和蓝线矢量取点 | 作者原始19箱计数、误差与蓝线数组 | 超出原图精度的复现；当前绘图与取点对照已有输入 |
| 逐探测器响应 | 论文有效探测器近似及各质量／天数／阈值 | 如需原生实验复现，补各探测器效率与分辨率曲线、分箱曝光 | 原生逐探测器高精度预测 |
| 统计能力 | signed excess与上下误差 | 拟合前确定误差对称化、nuisance和区间定义，或提供作者likelihood | 弱角／NSI拟合；本次事例谱已计算 |

本次前向计算所需数值已到位，未决项以原文溯源、原图数字化精度和下一项能力的输入区分。输出的科学来源状态为 PARTIAL，全部 human_gate 为 NOT_REVIEWED。P07结果保留为候选，后续正式冻结或更换输入时须按依赖重算并审阅。

[返回目录](#report-toc)

<a id="section-9"></a>

## 复算与标准参考文献

```powershell
.\run_benchmark.ps1
```

入口依次检查输入快照、复用已存在的各网格输出或执行直接Slow计算，再生成检查、图和报告。所用Python、NumPy、SciPy、Matplotlib版本和依赖位置见 [运行环境](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/sm_response_20261106/ENVIRONMENT.json>)。

所有数值输出列的出处、转换、代码身份和文件SHA256见 [OUTPUT_PROVENANCE.json](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/OUTPUT_PROVENANCE.json>)。所有输入的原始逐字段映射见 [PROVENANCE_MAP.json](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/PROVENANCE_MAP.json>)。

[1] V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," **Phys. Rev. D 111**, 075025 (2025), doi:10.1103/PhysRevD.111.075025, arXiv:2501.17843v3. 本次定位为 PDF p.3、pp.8–10，Eqs.(26)–(32)、Fig.1。[原文](<../../../../../../references/CONUS/2501.17843v3.pdf>)

[2] Th. A. Mueller et al., "Improved predictions of reactor antineutrino spectra," **Phys. Rev. C 83**, 054615 (2011), doi:10.1103/PhysRevC.83.054615, arXiv:1101.2663v3. Eq.(12)、Table VI，PDF p.13，24 个系数已逐项核对。[原文](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/1101.2663v3.pdf>)

[3] V. I. Kopeikin, "Flux and spectrum of reactor antineutrinos," **Phys. At. Nucl. 75**, 143–152 (2012), doi:10.1134/S1063778812020123. 已核验出版信息，32 节点对应的原始数表仍待核实。[出版页快照](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/kopeikin_2012_publisher.html>)

[4] 作者未署名，"CEνNS-pyEFT 逐文件物理编程笔记"，第1章 CONUS+，未发表项目笔记（2026），用户提供。本次只采用 Flux 节，PDF pp.4–6、Table 2 和 Eqs.(1.22)–(1.25)。[直接材料](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/user_reference_CONUS.pdf>)

[5] NIST Physical Measurement Laboratory, "Atomic weights and isotopic compositions for germanium," online data table, accessed 2026-11-06. Ge70/72/73/74/76 行。[网页快照](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/nist_ge_isotopic_masses.html>)

[6] NIST Physical Measurement Laboratory, "Fundamental physical constants, 2022 CODATA adjustment," complete online listing, accessed 2026-11-06. 原子质量常数、电子/质子/中子静质量能、Fermi 常数行。[数表快照](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/nist_codata2022_allascii.txt>)

[7] G. Li, C.-Q. Song, F.-J. Tang, and J.-H. Yu, "Comprehensive effective field theory framework for coherent elastic neutrino-nucleus scattering," arXiv:2601.19883v2 (2026). Table II，PDF p.8；Eqs.(75)–(78)，PDF pp.15–17；ν/反ν事例率约定，PDF p.21、Eq.(92) 后一段。[原文](<../../../../../../references/General_CEvNS/2601.19883v2.pdf>)

[8] CEvNS-pyEFT project, "responses_all.json, Mu2eNRET_ResponseW_v1," local numerical asset, snapshot accessed 2026-11-06. nuclei.Ge70/72/73/74/Ge76，本地直接来源已固定，原始核计算/转换链待核实。[完整数表](<../../../../../../../data/responses/responses_all.json>)

[9] Bureau international des poids et mesures, *The International System of Units (SI)*, 9th ed. (2019), version 4.01 (June 2026), doi:10.59161/AUEZ1291. Chapter 4、Table 8，day 行，PDF p.142。[原文](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/bipm_si_brochure_9_v4_01.pdf>)

[10] User and CEvNS-pyEFT project, "CONUS+ onboarding decisions and input provenance," local project record (2026-11-06). D_V2_001–003、D_V3_001 和本次标准模型计算请求。[已有决定](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>) · [本次范围](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/sm_response_20261106/EXECUTION_PLAN.json>)

[返回目录](#report-toc)
