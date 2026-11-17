# CsI2021 时间分辨分析 详细溯源草稿

[详细版](<experiment.physics.md>) · [精简版](<experiment.physics.summary.md>) · [用户资料](<EXPERIMENT_USER_INPUT.md>) · [来源P00](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P00_SOURCE_REGISTER.yaml>) · [证据P01](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P01_EVIDENCE_LEDGER.yaml>) · [缺失P02](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P02_MISSING_AND_CONFLICTS.md>) · [配置P03](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P03_PHYSICS_CONTRACT.yaml>) · [Benchmark旧诊断与范围](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/README.md>) · [完整数据与生成入口](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/README.md>)

**修订草稿r3-onboarding-restart-20261118，2026-11-18，DRAFT/PARTIAL。** 已取得官方事件、背景、ROOT、校准系数及原data中的Cs/I核响应。用户已明确选择直接调用原核表，本次资源复用输入就绪。外部作者生成链仅作未核实的补充事项。BRN/NIN绝对归一及严格论文配置等价仍待补，外部benchmark继续BLOCKED。

<a id="report-toc"></a>

## 目录

- [身份、目标与本轮补充](#identity)
- [Source 数值与来源](#source)
- [Target 与曝光](#target)
- [Nuclear RESPONSE 实际数据和上游缺口](#nuclear)
- [常数及单位来源](#constants)
- [Detector Response 与校准](#detector)
- [Observable、分箱与原始计数](#observable)
- [Prediction folding 与旧诊断](#prediction)
- [Statistics 与独立benchmark](#statistics)
- [缺口与下一步交接](#handoff)

<a id="identity"></a>

## 身份、目标与本轮补充

本轮补充记录由同一P00/P01/P03生成。旧隔离候选版本保存在修订归档。

- 2026-11-18按用户要求重新进行同一99箱分析onboarding，旧计算仅参考，不继承阶段通过
- 三个并列入口已撤下；保留无CLI的兼容辅助模块，未新建替代计算入口
- Interaction/Nuclear/Kinematics/Cross-section/Detector独立列出审核状态
- 式75装配、核表归一、注量支撑域与两体流截断分别登记缺口；未修改共享公式
- P08/P09本轮未请求；阶段报告及Compiler输出只在实际执行后产生

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| 分析身份 `C_ID` 来源已提取；本稿候选 | CsI2021_time_9x11 | 1 | 标量或定义，见直接出处 | [S_MEAS](<../../../../references/COHERENT/2110.07730v2.pdf>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) 原测量标题与摘要；D_PROVENANCE | 同一测量的时间分辨分析草稿，尚未取得终稿科学接受；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 本轮重新onboarding范围 `C_RESTART_SCOPE` 用户已确认；本稿候选 | {"analysis_id": "CsI2021_time_9x11", "interaction": "SM candidate", "nuclear_resource": "data/responses/responses_all.json", "timing_onset_ns": 0, "plus75ns": "REFERENCE_ONLY diagnostic", "two_body": "not implemented; theory truncation must be disclosed", "requested": ["P01-P07 signal forward", "P10 scoped validation"], "not_requested": ["P08 new Fast", "P09 likelihood fit"], "old_results": "REFERENCE_ONLY; no current accepted Slow"} | 1 | 标量或定义，见直接出处 | [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) · [S_RESTART_BUILDER](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/restart_records.py>) r3 restart: explicit source/code comparison and user restart instruction | 候选整理；不是新公式、新注量或Slow的科学接受；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |

### 本章标准来源及核验范围

- [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) User decisions transcribed from this conversation,2026-11-06. 仅记录实际用户选项，不将其视作外部事实核验。
- [S_MEAS](<../../../../references/COHERENT/2110.07730v2.pdf>) D. Akimov et al. (COHERENT), Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT, Phys. Rev. Lett. 129, 081801 (2022), arXiv:2110.07730v2. 版本、实验身份和测量用途已核，数值附件另登记。 [原始网址](https://arxiv.org/abs/2110.07730v2)
- [S_RESTART_BUILDER](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/restart_records.py>) Project deterministic r3 onboarding-restart overlay, 2026-11-18. 仅整理来源、冲突、候选配置和阶段范围，不执行或批准物理计算。

[返回目录](#report-toc)

<a id="source"></a>

## Source 数值与来源

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| 累计POT `C_POT` 来源已提取；本稿候选 | 3.198e+23 | POT | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines76–81 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 每味每POT产额 `C_YIELD` 来源已提取；本稿候选 | 0.0848 | neutrinos/flavor/POT | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines78–81；10%误差 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 基线 `C_L` 来源已提取；本稿候选 | 19.3 | m | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines78–81 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 几何稀释后的每味积分注量 `C_ETA` 项目推导；本稿候选 | 579361763793233.9 | cm^-2 | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) p12 Eq29后归一化；prepare_records.py eta表达式 | 100是m→cm的精确换算，曝光只施加一次；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_POT,C_YIELD,C_L |
| prompt谱线能量 `C_LINE` 项目推导；本稿候选 | 29.792140909877446 | MeV | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) p12 Eq29；两体衰变公式 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_MPI,C_MMU |
| 论文DAR能谱上限 `C_ENDPOINT` 项目推导；本稿候选 | 52.82918775 | MeV | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p12 Eqs28–29，m_mu/2近似 | 旧积分器包含electron质量修正，其数值不与此混用；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_MMU |
| 采用的DAR分量 `C_COMPONENTS` 来源已提取；本稿候选 | ["nu_mu", "nu_e", "anti_nu_mu"] | 1 | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p12 Eq29 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 官方ROOT完整二维数组 `C_ROOT` 来源已提取；本稿候选 | 4个TH2F，每个[15000 time,600 energy]；完整轴域与代表值见下表 | weighted bin mass | [snsFlux2D.root](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/snsFlux2D.root>) keys=['convolved_energy_time_of_nu_mu', 'convolved_energy_time_of_nu_e', 'convolved_energy_time_of_anti_nu_mu', 'convolved_energy_time_of_anti_nu_e'] | [S_snsFlux2D](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/snsFlux2D.root>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) 各TH2F对象的time(ns),energy(MeV)轴；原始15000×600箱 | 全部四味已读；默认DAR仅三主味。ROOT权重由源模型单独赋绝对注量；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| ROOT时间边缘与0–6us分数 `C_TIME_MARGINAL` 项目推导；本稿候选 | [0.999951141657252, 0.9191783169548304, 0.919376108274515] | probability | [analysis_inputs.npz](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/analysis_inputs.npz>) keys=['mu_time_mass', 'e_time_mass', 'mub_time_mass'] shape=[3, 15000] | [S_snsFlux2D](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/snsFlux2D.root>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) 每TH2F对完整能量轴求和后，前6000个1ns时间箱/全域和 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_ROOT |
| 源表示选择 `C_SOURCE_CHOICE` 项目推导；本稿候选 | DAR解析谱 × ROOT各味时间边缘 | 1 | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) p12 Eq29、p13 Eq32；D_REUSE | 按目标论文形式形成草稿；完整ROOT联合与因子化不同，旧结果只作诊断；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_COMPONENTS,C_ROOT |
| 旧Michel谱表示 `C_INTERPOLATION_LEGACY` 仅参考；旧诊断 | 200 | nodes over0.001–300MeV | 标量或定义，见直接出处 | [S_LEGACY_SNS](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/sns.py>) loadNeutrinoEmpiricalFluxSNS num_points=200默认及CsI2021范围；np.interp分段线性 | 旧诊断输入，论文解析谱见Eq29，端点和质量约定分列；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| POT注量与时间支撑域解释 `C_FLUENCE_SCOPE_REVIEW` 存在差异；本稿候选 | {"eta_cm_minus2": 579361763793233.9, "adopted_scope": null, "candidates": ["full_support: normalized all-time source with time-window acceptance", "reference_window: requires evidence that eta is a 0-6us reference fluence"], "known": "Both numerical definitions are available; closeness to341 is not a selection criterion"} | 1 | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_TIME_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py>) r3 restart: explicit source/code comparison and user restart instruction | 候选整理；不是新公式、新注量或Slow的科学接受；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_ETA,C_DENOM |

| ROOT分量 | shape和完整轴域 | 实际最大权重箱(index,value) | 0–6us分数 |
|---|---|---|---|
| mu | [15000, 600]；time0–15000ns，energy0–600MeV | {'index': [499, 30], 'value': 54945.265625} | 0.999951141657 |
| e | [15000, 600]；time0–15000ns，energy0–600MeV | {'index': [796, 36], 'value': 278.8775939941406} | 0.919178316955 |
| mub | [15000, 600]；time0–15000ns，energy0–600MeV | {'index': [800, 52], 'value': 312.0618591308594} | 0.919376108275 |
| ebar | [15000, 600]；time0–15000ns，energy0–600MeV | {'index': [629, 45], 'value': 0.27518460154533386} | 0.937147877203 |

上述数值从S_snsFlux2D各TH2F读取/求和，算法与单位换算登记为C_ROOT及C_TIME_MARGINAL。

[S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p12 Eq29与后续归一化段。

$$
\eta=\frac{rN_{\rm POT}}{4\pi(100L)^2},\quad E_\pi=\frac{m_\pi^2-m_\mu^2}{2m_\pi} \tag{1}
$$

| 符号 | 数值取得情况 | 数据、数值或定义及出处 |
|---|---|---|
| eta | PROJECT_DERIVED | 579361763793233.9 cm^-2；[S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) p12 Eq29后归一化；prepare_records.py eta表达式 |
| r | SOURCE_EXTRACTED | 0.0848 neutrinos/flavor/POT；[S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines78–81；10%误差 |
| N_POT | SOURCE_EXTRACTED | 3.198e+23 POT；[S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines76–81 |
| L | SOURCE_EXTRACTED | 19.3 m；[S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines78–81 |
| m_pi | SOURCE_EXTRACTED | 139.57039 MeV；[S_PDG](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/PDG2024_pi_charged.pdf>) PDF/印刷p1 OUR FIT；误差0.00018MeV |
| m_mu | SOURCE_EXTRACTED | 105.6583755 MeV；[S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>) allascii line223 |
| E_pi | PROJECT_DERIVED | 29.792140909877446 MeV；[S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) p12 Eq29；两体衰变公式 |

[S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p12 Eq29，0≤E≤m_mu/2。

$$
\phi_{\nu_\mu}(E)=\eta\delta(E-E_\pi),\quad\phi_{\nu_e}(E)=\eta\frac{192E^2}{m_\mu^3}\left(\frac12-\frac{E}{m_\mu}\right),\quad\phi_{\bar\nu_\mu}(E)=\eta\frac{64E^2}{m_\mu^3}\left(\frac34-\frac{E}{m_\mu}\right) \tag{2}
$$

| 符号 | 数值取得情况 | 数据、数值或定义及出处 |
|---|---|---|
| E | 定义或明确限制 | 积分变量MeV，数值域见C_ENDPOINT |
| phi | 定义或明确限制 | 由已列输入定义的每味谱，不另索取实验采样表 |
| m_mu | SOURCE_EXTRACTED | 105.6583755 MeV；[S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>) allascii line223 |
| eta | PROJECT_DERIVED | 579361763793233.9 cm^-2；[S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) p12 Eq29后归一化；prepare_records.py eta表达式 |

### 本章标准来源及核验范围

- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2. p3、p12–14、p33 Table II、p35 Fig.18 已核。 [原始网址](https://arxiv.org/abs/2211.11905v2)
- [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) User decisions transcribed from this conversation,2026-11-06. 仅记录实际用户选项，不将其视作外部事实核验。
- [S_LEGACY_SNS](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/sns.py>) Project legacy CsI implementation, legacy/sns.py, snapshot2026-11-06. 旧SNS质量元数据与200点插值源的直接代码，属于项目实施依据，外部科学来源另记。
- [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) Project onboarding data-reading and derivation script, prepare_records.py,2026-11-06. 本次提取/直方图/数组逐值核对算法，可重跑。
- [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) COHERENT Collaboration, Supplemental Material to Phys. Rev. Lett. 129, 081801 (2022), 2110.07730v2 ancillary. p2–3 参数与背景说明、p5 Fig.2、p7 Table I 已读。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf)
- [S_TIME_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py>) Project legacy CsI implementation, time_acceptance.py, snapshot2026-11-06. 时间形状、固定参考分母及注量转换的直接代码，属于项目实施依据，外部科学来源另记。
- [S_snsFlux2D](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/snsFlux2D.root>) COHERENT Collaboration, snsFlux2D.root, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/snsFlux2D.root)

[返回目录](#report-toc)

<a id="target"></a>

## Target 与曝光

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| 论文探测器质量 `C_MASS` 来源已提取；本稿候选 | 14.6 | kg | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 line81；2211 p12 Eq28段落 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| Cs/I化学计量 `C_STOICH` 来源已提取；本稿候选 | [1, 1] | number ratio | 标量或定义，见直接出处 | [S_MEAS](<../../../../references/COHERENT/2110.07730v2.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) CsI[Na]靶身份；p12 Eq28后靶核计数定义 | Na掺杂未加入第三个靶核贡献，需保留适用性说明；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 旧诊断实际质量 `C_MASS_LEGACY` 仅参考；旧诊断 | 14.57 | kg | 标量或定义，见直接出处 | [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) ROOT_vs_legacy.identical_absolute_inputs.detector_mass_kg | 旧生成结果的输入；本草稿论文质量14.6kg见C_MASS；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| Cs133实际核表元数据 `C_BASIC_Cs133` 仅参考；本稿候选 | {"name": "Cs133", "A": 133, "Z": 55, "N": 78, "J": 3.5, "T": 11.5, "b": 11.644334960750054} | A,Z,N,J,T dimensionless; b GeV^-1 in current reader | 标量或定义，见直接出处 | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) nuclei.Cs133.basic | 数值已取得；b单位按原读取器约定，用户选择复用原表。外部作者对应仍未核实；数值资源已取得；直接材料已读；直接来源为本地原data；外部上游待核（可选）；本次原表复用已选 |
| I127实际核表元数据 `C_BASIC_I127` 仅参考；本稿候选 | {"name": "I", "A": 127, "Z": 53, "N": 74, "J": 2.5, "T": 10.5, "b": 11.566047952236252} | A,Z,N,J,T dimensionless; b GeV^-1 in current reader | 标量或定义，见直接出处 | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) nuclei.I.basic | 数值已取得；b单位按原读取器约定，用户选择复用原表。外部作者对应仍未核实；数值资源已取得；直接材料已读；直接来源为本地原data；外部上游待核（可选）；本次原表复用已选 |

### 本章标准来源及核验范围

- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2. p3、p12–14、p33 Table II、p35 Fig.18 已核。 [原始网址](https://arxiv.org/abs/2211.11905v2)
- [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) Project-generated CsI input-resolution audit, 2026-11-06, selected legacy260929 checkout. Numerical diagnostic with unresolved primary nuclear provenance. 原始输出已回读；其186项测试属于旧目录工程验证，核响应上游缺口传递到物理解释。
- [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) CEvNS-pyEFT project, local aggregated responses_all.json, format Mu2eNRET_ResponseW_v1, original export provenance unresolved. 用户明确选择直接复用原data核表；Cs133/I八通道已读、逐值提取；现读码的单位/基底约定已核。外部作者生成链仍未核实，不是本次原表复用前置。
- [S_MEAS](<../../../../references/COHERENT/2110.07730v2.pdf>) D. Akimov et al. (COHERENT), Measurement of the Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by COHERENT, Phys. Rev. Lett. 129, 081801 (2022), arXiv:2110.07730v2. 版本、实验身份和测量用途已核，数值附件另登记。 [原始网址](https://arxiv.org/abs/2110.07730v2)
- [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) COHERENT Collaboration, Supplemental Material to Phys. Rev. Lett. 129, 081801 (2022), 2110.07730v2 ancillary. p2–3 参数与背景说明、p5 Fig.2、p7 Table I 已读。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf)

[返回目录](#report-toc)

<a id="nuclear"></a>

## Nuclear RESPONSE 实际数据和上游缺口

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| 核结构选择 `C_NUCLEAR_CHOICE` 用户已确认；本稿候选 | native RESPONSE | 1 | 标量或定义，见直接出处 | [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) D_RESPONSE、D_LOCAL_RESPONSE | 直接调用原data核表；外部生成链不作为本次复用前置；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 实际调用资源与核素映射 `C_RESOURCE_BINDING` 用户已确认；本稿候选 | {"path": "data/responses/responses_all.json", "reader": "cevns_pyeft.nuclear.response.ResponseDB", "nucleus_keys": {"Cs133": "Cs133", "I127": "I"}} | 1 | 标量或定义，见直接出处 | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) 原JSON nuclei.Cs133和nuclei.I；D_LOCAL_RESPONSE | 完整原表为调用权威；提取NPZ只用于查看及逐值一致性核验；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| Cs133_Delta系数 `C_W_Cs133_Delta` 来源已提取；用户选定本地资源 | shape=[2, 2, 9], k=[0, 8]; c_pp[0:3]=[2.777767329081821, -6.672857949038999, 6.55129294731681] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.Delta key=Cs133_Delta shape=[2, 2, 9] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.Delta；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| Cs133_M系数 `C_W_Cs133_M` 来源已提取；用户选定本地资源 | shape=[2, 2, 11], k=[0, 10]; c_pp[0:3]=[3024.998274020381, -11027.633404691845, 15552.131264975062] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.M key=Cs133_M shape=[2, 2, 11] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.M；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| Cs133_MPhiPP系数 `C_W_Cs133_MPhiPP` 来源已提取；用户选定本地资源 | shape=[2, 2, 10], k=[0, 9]; c_pp[0:3]=[-337.2270119061203, 1028.1187793706663, -1191.3713542557764] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.MPhiPP key=Cs133_MPhiPP shape=[2, 2, 10] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.MPhiPP；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| Cs133_PhiPP系数 `C_W_Cs133_PhiPP` 来源已提取；用户选定本地资源 | shape=[2, 2, 9], k=[0, 8]; c_pp[0:3]=[92.77117991352004, -227.5432243891409, 211.79690175505195] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.PhiPP key=Cs133_PhiPP shape=[2, 2, 9] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.PhiPP；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| Cs133_PhiPT系数 `C_W_Cs133_PhiPT` 来源已提取；用户选定本地资源 | shape=[2, 2, 9], k=[0, 8]; c_pp[0:3]=[0.017221086156055408, -0.010712014633078523, 0.0029834868952053955] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.PhiPT key=Cs133_PhiPT shape=[2, 2, 9] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.PhiPT；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| Cs133_SigmaP系数 `C_W_Cs133_SigmaP` 来源已提取；用户选定本地资源 | shape=[2, 2, 11], k=[0, 10]; c_pp[0:3]=[0.4027959920988274, -3.072499366548158, 8.226342731339976] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.SigmaP key=Cs133_SigmaP shape=[2, 2, 11] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.SigmaP；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| Cs133_SigmaPDelta系数 `C_W_Cs133_SigmaPDelta` 来源已提取；用户选定本地资源 | shape=[2, 2, 10], k=[0, 9]; c_pp[0:3]=[0.6733961453469848, -3.3771379778618753, 5.326274178703672] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.SigmaPDelta key=Cs133_SigmaPDelta shape=[2, 2, 10] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.SigmaPDelta；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| Cs133_SigmaPP系数 `C_W_Cs133_SigmaPP` 来源已提取；用户选定本地资源 | shape=[2, 2, 11], k=[0, 10]; c_pp[0:3]=[0.20139799604941389, -0.14750139319149005, 0.04729454446532723] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.SigmaPP key=Cs133_SigmaPP shape=[2, 2, 11] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.SigmaPP；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_Delta系数 `C_W_I127_Delta` 来源已提取；用户选定本地资源 | shape=[2, 2, 9], k=[0, 8]; c_pp[0:3]=[0.5358168796402408, -1.2859608404378045, 1.6442979109260578] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.Delta key=I127_Delta shape=[2, 2, 9] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.Delta；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_M系数 `C_W_I127_M` 来源已提取；用户选定本地资源 | shape=[2, 2, 11], k=[0, 10]; c_pp[0:3]=[2808.9995665607275, -10034.66474862081, 13985.083771812386] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.M key=I127_M shape=[2, 2, 11] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.M；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_MPhiPP系数 `C_W_I127_MPhiPP` 来源已提取；用户选定本地资源 | shape=[2, 2, 10], k=[0, 9]; c_pp[0:3]=[-358.9434624297877, 1071.860847241573, -1226.724001560627] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.MPhiPP key=I127_MPhiPP shape=[2, 2, 10] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.MPhiPP；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_PhiPP系数 `C_W_I127_PhiPP` 来源已提取；用户选定本地资源 | shape=[2, 2, 9], k=[0, 8]; c_pp[0:3]=[201.1953955323554, -482.868031339836, 442.67902718816634] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.PhiPP key=I127_PhiPP shape=[2, 2, 9] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.PhiPP；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_PhiPT系数 `C_W_I127_PhiPT` 来源已提取；用户选定本地资源 | shape=[2, 2, 9], k=[0, 8]; c_pp[0:3]=[0.0002687821306724113, -0.0012325808757454723, 0.01758896344149697] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.PhiPT key=I127_PhiPT shape=[2, 2, 9] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.PhiPT；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_SigmaP系数 `C_W_I127_SigmaP` 来源已提取；用户选定本地资源 | shape=[2, 2, 11], k=[0, 10]; c_pp[0:3]=[0.26026299886965265, -1.5935648492504124, 5.29611648786122] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.SigmaP key=I127_SigmaP shape=[2, 2, 11] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.SigmaP；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_SigmaPDelta系数 `C_W_I127_SigmaPDelta` 来源已提取；用户选定本地资源 | shape=[2, 2, 10], k=[0, 9]; c_pp[0:3]=[-0.1783018283767848, 0.7598245640626068, -1.4954404774973509] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.SigmaPDelta key=I127_SigmaPDelta shape=[2, 2, 10] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.SigmaPDelta；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_SigmaPP系数 `C_W_I127_SigmaPP` 来源已提取；用户选定本地资源 | shape=[2, 2, 11], k=[0, 10]; c_pp[0:3]=[0.1301314994348263, -0.48853937121139385, 1.8336914142506728] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.SigmaPP key=I127_SigmaPP shape=[2, 2, 11] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.SigmaPP；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| 取得的作者核结构材料 `C_UPSTREAM` 来源已提取；候选上游 | ["Elastic Cs133_GCN5082.txt", "Elastic I127_GCN5082.txt", "Mu2e_NRET v1/v2 author code"] | 1 | 标量或定义，见直接出处 | [S_ELASTIC_CS](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Elastic/Cs133_GCN5082.txt>) · [S_ELASTIC_I](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Elastic/I127_GCN5082.txt>) · [S_MU2E](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Mu2e_NRET/v2/mathematica/mu2elib_v2.wl>) Elastic全部密度矩阵行；Mu2e_NRET作者README和响应函数实现 | 固定提交及SHA已保存，尚未证实为当前JSON的确切上游；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 可选外部作者导出链审计 `C_W_CONVERSION` MISSING；可选外部审计 | **MISSING** | 1 | 标量或定义，见直接出处 | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_MU2E](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Mu2e_NRET/v2/mathematica/mu2elib_v2.wl>) 缺少当前聚合JSON的原始导出脚本/Notebook、版本、基底/归一化逐项对照 | 用户已明确接受原data直接调用。外部作者溯源仍未闭合，仅限制外部来源认证，不阻断本次本地资源复用；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| I127局部M_nn(0)与N²残差 `C_I_ZERO` 项目推导；本稿候选 | {"M_nn_0": 5475.961194368475, "N_squared": 5476, "residual": -0.03880563152506511} | 1 | 标量或定义，见直接出处 | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.M[1][1][0]；N=74 | 内部归一化诊断，不能代替原始核表核验；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_W_I127_M,C_BASIC_I127 |
| 共享RESPONSE装配与论文对应审核 `C_RESPONSE_ASSEMBLY_REVIEW` 存在差异；本稿候选 | {"state": "CONFLICT_PENDING_AUDIT", "paper_locator": "2601.19883v2 p15 Eq75, p18-19 Eq82", "implementation": "amplitude.py direct contraction; responses.py R_Delta and zero R_SigmaPDelta", "required": "Verify response prefactors, spin/isospin normalization and interference against actual table-generation convention; no correction adopted"} | 1 | 标量或定义，见直接出处 | [S_LI2026](<../../../../references/General_CEvNS/2601.19883v2.pdf>) · [S_CURRENT_AMPLITUDE](<../../../../../cevns_pyeft/theory/li2026/amplitude.py>) · [S_CURRENT_R](<../../../../../cevns_pyeft/theory/li2026/responses.py>) · [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) r3 restart: explicit source/code comparison and user restart instruction | 候选整理；不是新公式、新注量或Slow的科学接受；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_RESOURCE_BINDING |

按用户补充，本次直接调用原data/responses/responses_all.json，资源绑定见C_RESOURCE_BINDING。现有数值和原读取器约定已取得。作者上游与当前表的等价关系尚未证实，属于可选外部审计。S_ELASTIC_CS/S_ELASTIC_I仍只列候选上游，C_W_CONVERSION的MISSING仅限制外部来源认证。

Cs133 M(0)实际矩阵，来源为该通道本地JSON的k=0系数。

|  | p列 | n列 |
|---|---:|---:|
| p行 | 3024.99827402038 | 4289.99964122997 |
| n行 | 4289.99964122997 | 6084.00245375786 |

I127 M(0)实际矩阵，来源为该通道本地JSON的k=0系数。

|  | p列 | n列 |
|---|---:|---:|
| p行 | 2808.99956656073 | 3921.98580077547 |
| n行 | 3921.98580077547 | 5475.96119436847 |

零动量残差用于诊断现表；本次沿用原读取器的归一化约定，外部作者归一化对应仍未核实。接近Z²/N²不能认证外部来源。

### 本章标准来源及核验范围

- [S_CURRENT_AMPLITUDE](<../../../../../cevns_pyeft/theory/li2026/amplitude.py>) Current local one-body amplitude assembly. flavor_kernel_onebody_li2026与直接R/W收缩已读；未认证与论文式75全等。
- [S_CURRENT_R](<../../../../../cevns_pyeft/theory/li2026/responses.py>) Current local particle-response polynomials. R_Delta及强制零R_SigmaPDelta已读；需要独立逐项核验。
- [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) User decisions transcribed from this conversation,2026-11-06. 仅记录实际用户选项，不将其视作外部事实核验。
- [S_ELASTIC_CS](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Elastic/Cs133_GCN5082.txt>) Berkeley Electroweak Physics, Elastic/Cs133_GCN5082.txt, commit a979c39c89c615c7e719b84006cafa94526b4517. 作者原始密度矩阵已取得并读到数值；与当前聚合W系数的对应关系仅为候选。 [原始网址](https://github.com/Berkeley-Electroweak-Physics/Elastic/blob/a979c39c89c615c7e719b84006cafa94526b4517/Cs133_GCN5082.txt)
- [S_ELASTIC_I](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Elastic/I127_GCN5082.txt>) Berkeley Electroweak Physics, Elastic/I127_GCN5082.txt, commit a979c39c89c615c7e719b84006cafa94526b4517. 作者原始密度矩阵已取得；尚未复算当前聚合系数。 [原始网址](https://github.com/Berkeley-Electroweak-Physics/Elastic/blob/a979c39c89c615c7e719b84006cafa94526b4517/I127_GCN5082.txt)
- [S_LI2026](<../../../../references/General_CEvNS/2601.19883v2.pdf>) G. Li, C.-Q. Song, F.-J. Tang, J.-H. Yu, Comprehensive Effective Field Theory Framework for Coherent Elastic Neutrino-Nucleus Scattering, arXiv:2601.19883v2 (2026). PDF p12-19 Eqs40-83/TableIII-IV及p30结论已核读；式75与当前装配的对应存在未闭合问题。 [原始网址](https://arxiv.org/abs/2601.19883v2)
- [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) CEvNS-pyEFT project, local aggregated responses_all.json, format Mu2eNRET_ResponseW_v1, original export provenance unresolved. 用户明确选择直接复用原data核表；Cs133/I八通道已读、逐值提取；现读码的单位/基底约定已核。外部作者生成链仍未核实，不是本次原表复用前置。
- [S_MU2E](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Mu2e_NRET/v2/mathematica/mu2elib_v2.wl>) Berkeley Electroweak Physics, Mu2e_NRET v2/mathematica/mu2elib_v2.wl, commit 15bef514375298b57d9b07852870be3c408c2b19; W. C. Haxton et al., Phys. Rev. C 107, 035504 (2023), DOI 10.1103/PhysRevC.107.035504. 作者代码和README引文已取得；尚未证明当前JSON由此版本生成。 [原始网址](https://github.com/Berkeley-Electroweak-Physics/Mu2e_NRET/blob/15bef514375298b57d9b07852870be3c408c2b19/v2/mathematica/mu2elib_v2.wl)
- [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) Project onboarding data-reading and derivation script, prepare_records.py,2026-11-06. 本次提取/直方图/数组逐值核对算法，可重跑。

[返回目录](#report-toc)

<a id="constants"></a>

## 常数及单位来源

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| muon质量 `C_MMU` 来源已提取；本稿候选 | 105.6583755 | MeV | 标量或定义，见直接出处 | [S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>) allascii line223 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| electron质量 `C_ME` 来源已提取；本稿候选 | 0.51099895069 | MeV | 标量或定义，见直接出处 | [S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>) allascii line109 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 原子质量单位能量 `C_U` 来源已提取；本稿候选 | 0.93149410372 | GeV | 标量或定义，见直接出处 | [S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>) allascii line24；MeV除1000 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| Fermi常数 `C_GF` 来源已提取；本稿候选 | 1.1663787e-05 | GeV^-2 | 标量或定义，见直接出处 | [S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>) allascii line135 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 带电pion质量 `C_MPI` 来源已提取；本稿候选 | 139.57039 | MeV | 标量或定义，见直接出处 | [S_PDG](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/PDG2024_pi_charged.pdf>) PDF/印刷p1 OUR FIT；误差0.00018MeV | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 2211名义弱混合角 `C_SIN2_PAPER` 来源已提取；论文参考 | 0.23857 | 1 | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p3 Sec2.1 Eqs1–3后说明，原文误差(5) | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 旧原生诊断弱混合角 `C_SIN2_NATIVE` 仅参考；旧诊断 | 0.2387 | 1 | 标量或定义，见直接出处 | [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>) verified_sm_cross_section直接原生调用的sin2thetaW参数 | 项目配置值；与2211名义数值分列，后续统一配置需审阅；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |

### 本章标准来源及核验范围

- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2. p3、p12–14、p33 Table II、p35 Fig.18 已核。 [原始网址](https://arxiv.org/abs/2211.11905v2)
- [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>) Project resolve_input_issues.py, native Response numerical diagnostic and recorded input transformations,2026-11-06. 算法和文件字节已保留；其余旧共享代码按原SHA引用。
- [S_NIST](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/NIST_CODATA2022_allascii.txt>) NIST Standard Reference Database 121, CODATA 2022 recommended values, data update May2024, allascii table. 逐常数原始行值与单位已核。 [原始网址](https://physics.nist.gov/cuu/Constants/Table/allascii.txt)
- [S_PDG](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/PDG2024_pi_charged.pdf>) S. Navas et al. (Particle Data Group), Review of Particle Physics, Phys. Rev. D 110, 030001 (2024), charged pion listing. p1 pi± MASS OUR FIT 139.57039±0.00018MeV已视觉核对。 [原始网址](https://pdg.lbl.gov/2024/listings/rpp2024-list-pi-plus-minus.pdf)

[返回目录](#report-toc)

<a id="detector"></a>

## Detector Response 与校准

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| nominal淬灭多项式系数 `C_QF` 来源已提取；本稿候选 | [0.0554628, 4.30681, -111.707, 840.384] | [1,MeV^-1,MeV^-2,MeV^-3] | 标量或定义，见直接出处 | [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) scintRespCoefficients.txt line7；2211 p12 Eqs30–31前；输入MeVnr，输出MeVee | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 淬灭系数全部模型 `C_QF_SYSTEMATICS` 来源已提取；本稿候选 | [[0.0554628, 4.30681, -111.707, 840.384], [0.0613632, 3.51547, -85.5548, 595.562], [0.0495624, 5.09815, -137.858, 1085.2], [0.055413, 3.93597, -93.1045, 630.092], [0.0555126, 4.67765, -130.309, 1050.68]] | 同nominal系数单位 | [scintRespCoefficients.txt](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) shape=[5, 4] | [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) line7、10、12、15、17；nominal与两条±1sigma方向 | 文件全部取得；当前简化统计只使用总率误差，未声称逐形状实现；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| QF拟合适用域 `C_QF_DOMAIN` 来源已提取；本稿候选 | [2, 70] | keVnr | 标量或定义，见直接出处 | [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) Sec8，PDF p23/印刷p21 Fitting approach | 校准点范围3–63keVnr，与拟合域分别记录；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 光产额 `C_LY` 来源已提取；本稿候选 | 13.35 | PE/keVee | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) p3 lines90–93 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| Gamma展宽参数 `C_GAMMA` 来源已提取；本稿候选 | {"a_numerator": 0.0749, "b_slope": 9.56} | a=0.0749/Eee(keVee); b=9.56*Eee(keVee) | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) Supplement p3 Eq3 lines94–101；2211 p12 Eq31 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 官方nominal能量效率系数 `C_EFF` 来源已提取；本稿候选 | [1.32045, 0.285979, 10.8646, -0.333322] | a,d dimensionless; b PE^-1; c PE | 标量或定义，见直接出处 | [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) effCoefficients.txt line7，公式与x=PE见头部line1–4 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 效率系数全部模型 `C_EFF_SYSTEMATICS` 存在差异；本稿候选 | [[1.32045, 0.285979, 10.8646, -0.333322], [1.3439, 0.285366, 9.84596, -0.356364], [1.297, 0.286592, 11.8832, -0.31028]] | 同nominal效率单位 | 标量或定义，见直接出处 | [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) line7、10、12；两条systematic注释均写+1sigma | 原发布文件的符号标签歧义保留CONFLICT；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 旧程序效率常数项 `C_EFF_LEGACY` 存在差异；旧诊断 | -0.3333 | 1 | 标量或定义，见直接出处 | [S_LEGACY_EFF](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/slow_counts_csi2021.py>) · [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) 旧slow_counts_csi2021.py CsI2021EfficiencyParams.d；官方line7为−0.333322 | 旧数值结果使用舍入值；本草稿nominal采用官方−0.333322，旧拟合不是本草稿同条件结果；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 时间效率转折及衰减 `C_TIME_EFF` 来源已提取；本稿候选 | [0.52, 0.0494] | [us,us^-1] | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) Supplement p2 Eq1 lines64–68；2211 p13 Eq33 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 时间及效率位移范围 `C_SHIFTS` 来源已提取；本稿候选 | {"time_shift_us": [-0.25, 0.25], "efficiency_shift_PE": [-1, 1]} | us and PE | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p12 Eq30、p13脚注8和p14 alpha6/alpha7说明 | 原文无完整shift后分母程序说明，固定nominal分母为项目约定；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |

[S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) 系数文件line1–7；Supplement p3 lines90–93；校准Eq8.1。

$$
E_{ee}[{\rm keVee}]=10^3\sum_{j=1}^{4}q_j\left(10^{-3}T[{\rm keVnr}]\right)^j,\quad \overline{\rm PE}=13.35\,E_{ee} \tag{3}
$$

| 符号 | 数值取得情况 | 数据、数值或定义及出处 |
|---|---|---|
| q_j | SOURCE_EXTRACTED | [0.0554628, 4.30681, -111.707, 840.384] [1,MeV^-1,MeV^-2,MeV^-3]；[S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) scintRespCoefficients.txt line7；2211 p12 Eqs30–31前；输入MeVnr，输出MeVee |
| T | 定义或明确限制 | 真实反冲变量keVnr，适用域C_QF_DOMAIN |
| E_ee,PE_mean | 定义或明确限制 | 由该式定义的派生量 |

[S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) Supplement p3 Eq3；2211 p12 Eq31。

$$
G(x\mid E_{ee})=\frac{[a(1+b)]^{1+b}}{\Gamma(1+b)}x^b e^{-a(1+b)x},\quad a=0.0749/E_{ee},\quad b=9.56E_{ee} \tag{4}
$$

| 符号 | 数值取得情况 | 数据、数值或定义及出处 |
|---|---|---|
| x | 定义或明确限制 | 重建PE，x≥0 |
| a,b | SOURCE_EXTRACTED | {"a_numerator": 0.0749, "b_slope": 9.56} a=0.0749/Eee(keVee); b=9.56*Eee(keVee)；[S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) Supplement p3 Eq3 lines94–101；2211 p12 Eq31 |
| E_ee | 定义或明确限制 | keVee，来自F_QF |
| Gamma | 定义或明确限制 | Euler gamma数学函数 |

[S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_LEGACY_EFF](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/slow_counts_csi2021.py>) 系数文件头；2211 p12 Eq30；非负裁剪为现有实现约定。

$$
\epsilon_E(x)=\max\left(0,\frac{a}{1+e^{-b(x-c)}}+d\right),\quad x={\rm PE}+\delta_{\rm PE} \tag{5}
$$

| 符号 | 数值取得情况 | 数据、数值或定义及出处 |
|---|---|---|
| a,b,c,d | SOURCE_EXTRACTED | [1.32045, 0.285979, 10.8646, -0.333322] a,d dimensionless; b PE^-1; c PE；[S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) effCoefficients.txt line7，公式与x=PE见头部line1–4 |
| delta_PE | SOURCE_EXTRACTED | {"time_shift_us": [-0.25, 0.25], "efficiency_shift_PE": [-1, 1]} us and PE；[S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p12 Eq30、p13脚注8和p14 alpha6/alpha7说明 |
| max(0,...) | 定义或明确限制 | PROJECT_CONVENTION，避免低PE负效率，需审核 |

[S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) Supplement p2 Eq1；2211 p13 Eq33。

$$
\epsilon_T(t)=\begin{cases}1&t<0.52\,\mu{\rm s}\\e^{-0.0494(t-0.52)}&t\ge0.52\,\mu{\rm s}\end{cases} \tag{6}
$$

| 符号 | 数值取得情况 | 数据、数值或定义及出处 |
|---|---|---|
| t | 定义或明确限制 | 观测时间us，位移后效率留在此坐标 |
| 0.52,0.0494 | SOURCE_EXTRACTED | [0.52, 0.0494] [us,us^-1]；[S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) Supplement p2 Eq1 lines64–68；2211 p13 Eq33 |

### 本章标准来源及核验范围

- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2. p3、p12–14、p33 Table II、p35 Fig.18 已核。 [原始网址](https://arxiv.org/abs/2211.11905v2)
- [S_LEGACY_EFF](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/slow_counts_csi2021.py>) Project legacy CsI implementation, legacy/slow_counts_csi2021.py, snapshot2026-11-06. 旧效率参数及非负裁剪的直接代码，属于项目实施依据，外部科学来源另记。
- [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) COHERENT Collaboration, Measurement of scintillation response of CsI[Na] to low-energy nuclear recoils by COHERENT, JINST 17 (2022) P10034, arXiv:2111.02477v2. Sec.8，PDF p23/印刷p21 的2–70keV拟合域与式(8.1)已核。 [原始网址](https://arxiv.org/abs/2111.02477v2)
- [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) COHERENT Collaboration, Supplemental Material to Phys. Rev. Lett. 129, 081801 (2022), 2110.07730v2 ancillary. p2–3 参数与背景说明、p5 Fig.2、p7 Table I 已读。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf)
- [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) COHERENT Collaboration, effCoefficients.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/effCoefficients.txt)
- [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) COHERENT Collaboration, scintRespCoefficients.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/scintRespCoefficients.txt)

[返回目录](#report-toc)

<a id="observable"></a>

## Observable、分箱与原始计数

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| PE边界 `C_PE` 项目推导；本稿候选 | [0.0, 8.0, 12.0, 16.0, 20.0, 24.0, 32.0, 40.0, 48.0, 60.0] | PE | 标量或定义，见直接出处 | [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) D_PE；Supplement p5 Fig2水平误差棒 | 指定重建值；尚未取得作者机器数字边界表；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 时间边界 `C_TIME` 来源已提取；本稿候选 | [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 2.0, 4.0, 6.0] | us | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p35 Fig18全部十一面板标签 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 端点归箱规则 `C_ENDPOINT_RULE` 项目推导；本稿候选 | 每箱左闭右开，PE60及t6us排除 | 1 | 标量或定义，见直接出处 | [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) 统一端点的用户要求；histogram筛选实现 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| C逐箱原始计数 `C_OBS` 项目推导；本稿候选 | 9×11，全部数值见详细版Observable矩阵及完整数据文件；sum=1578 | events/bin | [analysis_inputs.npz](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/analysis_inputs.npz>) · [完整99箱观测CSV](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/observed_99bins.csv>) key=C_counts shape=[9, 11] | [S_dataBeamOnC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnC.txt>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) 原始文件全部8916行PE,time_us；按C_PE/C_TIME重分箱，轴顺序[PE,time] | 总计1578，为官方逐事件表的项目重分箱值；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_PE,C_TIME,C_ENDPOINT_RULE |
| AC逐箱原始计数 `C_CONTROL` 项目推导；本稿候选 | 9×11，全部数值见详细版Observable矩阵及完整数据文件；sum=1295 | events/bin | [analysis_inputs.npz](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/analysis_inputs.npz>) · [完整99箱观测CSV](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/observed_99bins.csv>) key=AC_counts shape=[9, 11] | [S_dataBeamOnAC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnAC.txt>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) 原始文件全部8532行PE,time_us；按C_PE/C_TIME重分箱，轴顺序[PE,time] | 总计1295，为官方逐事件表的项目重分箱值；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_PE,C_TIME,C_ENDPOINT_RULE |

### C逐箱原始计数全部99箱

数值来自C_OBS的官方逐事件文件重分箱，端点和坐标见C_PE/C_TIME/C_ENDPOINT_RULE。

| PE范围 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [0.0,8.0) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 3 | 5 |
| [8.0,12.0) | 4 | 3 | 8 | 3 | 8 | 9 | 9 | 5 | 28 | 37 | 33 |
| [12.0,16.0) | 6 | 3 | 4 | 8 | 12 | 14 | 9 | 9 | 49 | 61 | 49 |
| [16.0,20.0) | 3 | 3 | 7 | 10 | 9 | 5 | 9 | 7 | 44 | 51 | 29 |
| [20.0,24.0) | 2 | 1 | 3 | 3 | 2 | 4 | 5 | 2 | 36 | 53 | 33 |
| [24.0,32.0) | 4 | 4 | 6 | 4 | 7 | 11 | 7 | 6 | 53 | 65 | 70 |
| [32.0,40.0) | 5 | 6 | 2 | 4 | 5 | 4 | 6 | 3 | 35 | 78 | 62 |
| [40.0,48.0) | 9 | 6 | 7 | 4 | 4 | 3 | 4 | 3 | 28 | 66 | 59 |
| [48.0,60.0) | 1 | 5 | 5 | 6 | 5 | 8 | 7 | 6 | 38 | 77 | 77 |

列索引0–10依次对应C_TIME给出的十一时间窗，事件数单位为events/bin。

### AC逐箱原始计数全部99箱

数值来自C_CONTROL的官方逐事件文件重分箱，端点和坐标见C_PE/C_TIME/C_ENDPOINT_RULE。

| PE范围 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [0.0,8.0) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 1 |
| [8.0,12.0) | 2 | 2 | 5 | 2 | 1 | 2 | 3 | 2 | 24 | 27 | 28 |
| [12.0,16.0) | 3 | 2 | 3 | 2 | 3 | 3 | 3 | 3 | 28 | 43 | 51 |
| [16.0,20.0) | 2 | 4 | 3 | 7 | 2 | 3 | 6 | 4 | 24 | 38 | 30 |
| [20.0,24.0) | 2 | 1 | 3 | 3 | 4 | 1 | 4 | 2 | 18 | 37 | 30 |
| [24.0,32.0) | 5 | 5 | 6 | 5 | 2 | 4 | 1 | 6 | 40 | 65 | 63 |
| [32.0,40.0) | 2 | 5 | 4 | 5 | 5 | 4 | 4 | 1 | 30 | 60 | 62 |
| [40.0,48.0) | 5 | 1 | 2 | 3 | 4 | 7 | 8 | 4 | 25 | 64 | 52 |
| [48.0,60.0) | 2 | 4 | 4 | 5 | 7 | 8 | 2 | 8 | 43 | 98 | 81 |

列索引0–10依次对应C_TIME给出的十一时间窗，事件数单位为events/bin。

### 本章标准来源及核验范围

- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2. p3、p12–14、p33 Table II、p35 Fig.18 已核。 [原始网址](https://arxiv.org/abs/2211.11905v2)
- [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) User decisions transcribed from this conversation,2026-11-06. 仅记录实际用户选项，不将其视作外部事实核验。
- [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) Project onboarding data-reading and derivation script, prepare_records.py,2026-11-06. 本次提取/直方图/数组逐值核对算法，可重跑。
- [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) COHERENT Collaboration, Supplemental Material to Phys. Rev. Lett. 129, 081801 (2022), 2110.07730v2 ancillary. p2–3 参数与背景说明、p5 Fig.2、p7 Table I 已读。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf)
- [S_dataBeamOnAC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnAC.txt>) COHERENT Collaboration, dataBeamOnAC.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/dataBeamOnAC.txt)
- [S_dataBeamOnC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnC.txt>) COHERENT Collaboration, dataBeamOnC.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/dataBeamOnC.txt)

[返回目录](#report-toc)

<a id="prediction"></a>

## Prediction folding 与旧诊断

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| 反冲积分域保护 `C_RECOIL_POLICY` 项目推导；本稿候选 | [2, 70] | keVnr | 标量或定义，见直接出处 | [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) · [S_DOMAIN_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/analysis_inputs.py>) 校准Sec8；analysis_inputs.py guards；DAR上界还受运动学约束 | 下界从2keV开始是项目截断政策；原先0.1–2keV延拓影响另作诊断；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_QF_DOMAIN |
| 平移后的时间归一分母 `C_DENOM` 项目推导；本稿候选 | 固定零位移0–6us参考分数 | 1 | 标量或定义，见直接出处 | [S_TIME_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) time_acceptance.build_time_weights的nominal参考分数；论文p13脚注8未给完整程序细节 | 项目实施约定，未标成作者代码已核；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_TIME_MARGINAL |
| 旧实现数值诊断 `C_DIAGNOSTICS` 仅参考；旧诊断 | {"full_fluence_SM": 328.3189300697272, "same_eta_6us_SM": 352.71221639340564, "max_grid_change": 0.004015979465854969, "ROOT_correlation_max": 0.019906826571506775, "ROOT_vs_legacy_max": 1.0058675295241777} | events or events/bin | 标量或定义，见直接出处 | [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>) signal_convergence、time_fluence_scope、ROOT_correlation、ROOT_vs_legacy对应JSON字段 | 旧实现/旧配置的诊断值；r3不将其作为已接受的Slow或目标值；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_RESOURCE_BINDING,C_W_Cs133_M,C_W_I127_M,C_ETA,C_QF,C_EFF_LEGACY |
| 20261117可选时间诊断与默认保持 `C_TIMING_DIAGNOSTIC` 仅参考；旧诊断 | {"default_shift_ns": 0, "diagnostic_shifts_ns": [-125, -50, 0, 50, 75, 125], "positive_shift": "h(t-delta), source delayed; observer bins/efficiency fixed", "q": "unshifted integral of full-support normalized h from 0 to 6 us", "default_fluence_scope": "reference_window", "scopes": ["reference_window", "full_support"], "default_background_mode": "raw", "background_modes": ["raw", "prior_posteff", "bestfit_posteff", "prior_preeff"], "signal_and_neutrons_shift_together": true, "SSB_shifted": false, "official_onset_verified": false, "flight_time_added": false, "prior_posteff_zero_shift_ROI_events": [18.4, 5.6], "bestfit_posteff_zero_shift_ROI_events": [17.3, 5.5], "native_nominal_reference_events": 353.46560868634367, "native_full_support_reference_events": 329.01642259688515, "KN_nominal_reference_events": 333.11348797594866, "KN_plus75_reference_events": 331.2663916870358} | ns or explicitly named events | 标量或定义，见直接出处 | [S_TIMING_README](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/README.md>) · [S_TIMING_HANDOFF](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/HANDOFF_PROMPT.md>) · [S_TIMING_ZIP](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/20261117_CsI2021_ROOTTime_%25E6%25A0%25B8%25E5%25BF%2583%25E4%25BB%25A3%25E7%25A0%2581%25E4%25B8%258E%25E4%25B8%25BB%25E7%25BA%25BF%25E8%25BF%2581%25E7%25A7%25BB%25E4%25BA%25A4%25E6%258E%25A5%25E5%258C%2585.zip>) · [S_TIMING_ADAPTER](<../../../../../examples/COHERENT_CsI/time_resolved_common/timing_diagnostics.py>) · [S_TIMING_DRIVER](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py>) README/HANDOFF timing convention; handoff/background_shift.py; timing_audit/time_weight_shift_adapter.py; main diagnostic driver | 旧实现/旧配置的诊断值；r3不将其作为已接受的Slow或目标值；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_TIME_MARGINAL,C_DENOM,C_TIME_EFF,C_PRIORS |

[S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p12 Eq28与p13 Eq32，以重建PE作变量的等价书写。

$$
N_{ij}=\sum_{A,n}N_A\int_{\mathrm{PE}_i}^{\mathrm{PE}_{i+1}}dx\,\epsilon_E(x)\int dT\,G(x\mid T)\int dE\,\phi_n(E)\frac{d\sigma_{A,n}}{dT}\int_{t_j}^{t_{j+1}}dt\,f_n(t-\delta_t)\epsilon_T(t) \tag{7}
$$

| 符号 | 数值取得情况 | 数据、数值或定义及出处 |
|---|---|---|
| N_A | 定义或明确限制 | 按已选择的靶核数计算，质量源为C_MASS |
| d_sigma/dT | 定义或明确限制 | 选定RESPONSE，直接资源C_RESOURCE_BINDING；外部作者链另记 |
| f_n | 定义或明确限制 | C_TIME_MARGINAL与C_DENOM |
| G,epsilon | 定义或明确限制 | Detector已列输入 |
| x,T,E,t | 定义或明确限制 | 积分变量，单位分别PE,keVnr,MeV,us |

### 本章标准来源及核验范围

- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2. p3、p12–14、p33 Table II、p35 Fig.18 已核。 [原始网址](https://arxiv.org/abs/2211.11905v2)
- [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) Project-generated CsI input-resolution audit, 2026-11-06, selected legacy260929 checkout. Numerical diagnostic with unresolved primary nuclear provenance. 原始输出已回读；其186项测试属于旧目录工程验证，核响应上游缺口传递到物理解释。
- [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>) Project resolve_input_issues.py, native Response numerical diagnostic and recorded input transformations,2026-11-06. 算法和文件字节已保留；其余旧共享代码按原SHA引用。
- [S_DOMAIN_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/analysis_inputs.py>) Project legacy CsI implementation, analysis_inputs.py, snapshot2026-11-06. 2–70keVnr适用域保护的直接代码，属于项目实施依据，外部科学来源另记。
- [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) COHERENT Collaboration, Measurement of scintillation response of CsI[Na] to low-energy nuclear recoils by COHERENT, JINST 17 (2022) P10034, arXiv:2111.02477v2. Sec.8，PDF p23/印刷p21 的2–70keV拟合域与式(8.1)已核。 [原始网址](https://arxiv.org/abs/2111.02477v2)
- [S_TIME_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py>) Project legacy CsI implementation, time_acceptance.py, snapshot2026-11-06. 时间形状、固定参考分母及注量转换的直接代码，属于项目实施依据，外部科学来源另记。
- [S_TIMING_ADAPTER](<../../../../../examples/COHERENT_CsI/time_resolved_common/timing_diagnostics.py>) 本次默认保持的可选时间/背景诊断适配器 已读直接材料并运行独立及主线数值对照；75ns仍为可选诊断，官方时钟起点未验证。
- [S_TIMING_DRIVER](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py>) 本次原生SM和KN重新积分、逐箱对照生成器 已撤下入口的原字节历史快照；仅作REFERENCE，不是当前计算入口或阶段批准。
- [S_TIMING_HANDOFF](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/HANDOFF_PROMPT.md>) 用户提供主线接入建议：固定观测效率/窗口和零位移分母 已读直接材料并运行独立及主线数值对照；75ns仍为可选诊断，官方时钟起点未验证。
- [S_TIMING_README](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/README.md>) 用户提供νμ交接说明：75ns为诊断，非已验证时钟修正 已读直接材料并运行独立及主线数值对照；75ns仍为可选诊断，官方时钟起点未验证。
- [S_TIMING_ZIP](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/20261117_CsI2021_ROOTTime_%25E6%25A0%25B8%25E5%25BF%2583%25E4%25BB%25A3%25E7%25A0%2581%25E4%25B8%258E%25E4%25B8%25BB%25E7%25BA%25BF%25E8%25BF%2581%25E7%25A7%25BB%25E4%25BA%25A4%25E6%258E%25A5%25E5%258C%2585.zip>) 用户交接包：独立KN与背景适配器及测试；不能认证原生SM主线 已读直接材料并运行独立及主线数值对照；75ns仍为可选诊断，官方时钟起点未验证。

[返回目录](#report-toc)

<a id="statistics"></a>

## Statistics 与独立benchmark

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| SS平滑背景 `C_SS` 项目推导；本稿候选 | 1285.9265239871502 | events in0–6us | [analysis_inputs.npz](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/analysis_inputs.npz>) key=SS_counts shape=[9, 11] | [S_dataBeamOnAC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnAC.txt>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) AC PE<60、0≤t<12us 2242events；p2 lines55–59指数k=0.0494/us；prepare_records.py integrals | 整文件0–12us作为输入，与0–6us的1295个AC事件区别清楚；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_CONTROL,C_TIME_EFF |
| BRN能量表 `C_BRN_PE` 来源已提取；本稿候选 | {"shape": [250, 2], "center_range_PE": [0.5, 249.5], "sum": 1.4977778220000002, "first_rows": [[0.5, 0.0], [1.5, 0.0], [2.5, 0.0], [3.5, 0.0]]} | relative bin weight; epsilon_PE already applied | [brnPE.txt](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/brnPE.txt>) columns=['PE_center', 'weight'] | [S_brnPE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/brnPE.txt>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) PE文件全部两列；Supplement p2 lines60–75 | 不得重复施加能量效率；发布的绝对概率归一含义未完全闭合；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| BRN时间表 `C_BRN_TIME` 来源已提取；本稿候选 | {"shape": [650, 2], "center_range_us": [-0.245, 6.245], "sum": 27.632009229740003, "first_rows": [[-0.245, 0.0], [-0.235, 0.0], [-0.225, 0.0], [-0.215, 0.0]]} | events per0.01us bin at13.99GWhr; before epsilon_T | [brnTrec.txt](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/brnTrec.txt>) columns=['time_us', 'events_per_bin'] | [S_brnTrec](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/brnTrec.txt>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Trec文件全部两列；Supplement p2 lines62–68 | time效率另施加；曝光只出现一次；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| NIN能量表 `C_NIN_PE` 来源已提取；本稿候选 | {"shape": [250, 2], "center_range_PE": [0.5, 249.5], "sum": 1.3339572780000002, "first_rows": [[0.5, 0.0], [1.5, 0.0], [2.5, 0.0], [3.5, 0.0]]} | relative bin weight; epsilon_PE already applied | [ninPE.txt](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/ninPE.txt>) columns=['PE_center', 'weight'] | [S_ninPE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/ninPE.txt>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) PE文件全部两列；Supplement p2 lines60–75 | 不得重复施加能量效率；发布的绝对概率归一含义未完全闭合；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| NIN时间表 `C_NIN_TIME` 来源已提取；本稿候选 | {"shape": [650, 2], "center_range_us": [-0.245, 6.245], "sum": 7.564846239112, "first_rows": [[-0.245, 0.0], [-0.235, 0.0], [-0.225, 0.0], [-0.215, 0.0]]} | events per0.01us bin at13.99GWhr; before epsilon_T | [ninTrec.txt](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/ninTrec.txt>) columns=['time_us', 'events_per_bin'] | [S_ninTrec](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/ninTrec.txt>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Trec文件全部两列；Supplement p2 lines62–68 | time效率另施加；曝光只出现一次；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 官方背景总数prior `C_PRIORS` 来源已提取；本稿候选 | [18.4, 5.6, 1286] | events for BRN,NIN,SS | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) p7 TableI Prior Prediction | 不是模板归一化的调节目标；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| JHEP四pull宽度 `C_PULL_JHEP` 来源已提取；本稿候选 | [0.12, 0.25, 0.35, 0.021] | relative sigma | 标量或定义，见直接出处 | [S_2202](<../../../../references/COHERENT/2202.11002v3.pdf>) arXiv Eq6后说明，对应期刊Eq2.6 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 2211 CEvNS-only归一化宽度 `C_PULL_2211` 来源已提取；本稿候选 | [0.1145, 0.25, 0.35, 0.021] | relative sigma | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p14 Eqs36、38后说明 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 2211原文半径nuisance `C_RADIUS` 来源已提取；论文参考 | 0.05 | relative sigma | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p14 alpha4及Eq3的RA变形 | 原生RESPONSE当前固定半径，此原文nuisance尚未形成等价实现；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 2211论文SM最低卡方 `C_SM_PAPER` 来源已提取；论文参考 | 83.2 | chi2 | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p33 TableII CsI SM cell | 外部目标，仅引用原文；不与不一致配置的旧结果直接判PASS；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| BRN/NIN全域概率候选效率后总数 `C_BG_GAP` 项目推导；本稿候选 | [18.309633271138438, 5.1789999582711825] | events | 标量或定义，见直接出处 | [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>) background_audit；分母为各PE表全域和，未用prior作缩放目标 | 18.30963327/5.17899996与18.4/5.6不闭合；时间效率前口径仍待发布者说明；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_BRN_PE,C_BRN_TIME,C_NIN_PE,C_NIN_TIME,C_TIME_EFF,C_PRIORS |

[S_2202](<../../../../references/COHERENT/2202.11002v3.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) 2202 Eq6；2211 p14 Eq36，预测组成Eq38。

$$
\chi^2=2\sum_{ij}\left[\mu_{ij}-n_{ij}+n_{ij}\ln\frac{n_{ij}}{\mu_{ij}}\right]+\sum_k\left(\frac{\alpha_k}{\sigma_k}\right)^2 \tag{8}
$$

| 符号 | 数值取得情况 | 数据、数值或定义及出处 |
|---|---|---|
| n_ij | 定义或明确限制 | C_OBS，raw C counts |
| mu_ij | 定义或明确限制 | CEvNS+BRN+NIN+SS，BRN/NIN归一未闭合 |
| sigma_k | 定义或明确限制 | 两个benchmark各用自身宽度 |
| alpha_k | 定义或明确限制 | nuisance变量；2211半径项与当前固定RESPONSE不同 |

### 本章标准来源及核验范围

- [S_2202](<../../../../references/COHERENT/2202.11002v3.pdf>) M. Atzori Corona et al., Probing light mediators and (g−2)mu through detection of coherent elastic neutrino nucleus scattering at COHERENT, JHEP 05 (2022) 109, arXiv:2202.11002v3. arXiv 式(6)与期刊式(2.6)的统计分支及四个归一化误差已读。 [原始网址](https://arxiv.org/abs/2202.11002v3)
- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2. p3、p12–14、p33 Table II、p35 Fig.18 已核。 [原始网址](https://arxiv.org/abs/2211.11905v2)
- [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) Project-generated CsI input-resolution audit, 2026-11-06, selected legacy260929 checkout. Numerical diagnostic with unresolved primary nuclear provenance. 原始输出已回读；其186项测试属于旧目录工程验证，核响应上游缺口传递到物理解释。
- [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>) Project resolve_input_issues.py, native Response numerical diagnostic and recorded input transformations,2026-11-06. 算法和文件字节已保留；其余旧共享代码按原SHA引用。
- [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) Project onboarding data-reading and derivation script, prepare_records.py,2026-11-06. 本次提取/直方图/数组逐值核对算法，可重跑。
- [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) COHERENT Collaboration, Supplemental Material to Phys. Rev. Lett. 129, 081801 (2022), 2110.07730v2 ancillary. p2–3 参数与背景说明、p5 Fig.2、p7 Table I 已读。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf)
- [S_brnPE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/brnPE.txt>) COHERENT Collaboration, brnPE.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/brnPE.txt)
- [S_brnTrec](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/brnTrec.txt>) COHERENT Collaboration, brnTrec.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/brnTrec.txt)
- [S_dataBeamOnAC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnAC.txt>) COHERENT Collaboration, dataBeamOnAC.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/dataBeamOnAC.txt)
- [S_ninPE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/ninPE.txt>) COHERENT Collaboration, ninPE.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/ninPE.txt)
- [S_ninTrec](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/ninTrec.txt>) COHERENT Collaboration, ninTrec.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/ninTrec.txt)

[返回目录](#report-toc)

<a id="handoff"></a>

## 缺口与下一步交接

| 问题 | 已有数据 | 尚缺数据/溯源 | 影响及当前状态 |
|---|---|---|---|
| G_NUCLEAR RESPONSE原表复用与可选外部生成链 | 本地Cs/I全部16个通道数组、作者Elastic密度矩阵和Mu2e_NRET代码已取得 | 本次直接调用原data已获用户明确选择；外部导出Notebook/版本仍可补充，只影响作者来源认证 | LOCAL_REUSE_READY；外部作者来源认证 |
| G_BG BRN/NIN绝对归一与时间效率 | 官方四个表、曝光和两个效率作用域均已取得，候选算法及差额已回读 | 作者明确PE概率归一、Trec绝对归一和TableI在时间效率前/后的口径 | BLOCKED；P09论文统计组成,P10外部benchmark |
| G_THEORY 原生Interaction/Matching与论文定义 | 原生代码可读取，G_F和质量常数已追到NIST/PDG，弱角两个配置已分列 | 按所选SM/LEFT范围完成核子与匹配数值到原文式及单位的逐项对应；此项是未完成审计，不能写成数值文件不存在 | PARTIAL；P04共享理论适用性,同模型外部比较 |
| G_CONFIG 旧诊断与本草稿输入差异 | 统一14.6kg/官方效率/解析DAR谱的原生SM353.465609及全支撑329.016423已生成；20261117高网格逐箱复核一致 | 同条件本地数值已完成；作者模型/时钟/背景口径等价仍依赖G_CLOCK/G_BG/G_THEORY，不由数值复核认证 | PARTIAL；同条件数值比较 |
| G_PE PE边界原始数字表 | 用户指定边界、Fig2图示和原事件重分箱 | 严格作者边界复现仍需机器边界表或作者配置；当前保留重建标记 | PROJECT_DERIVED；精确作者分箱声称 |
| G_RADIUS 2211半径nuisance与RESPONSE | 原文5%约束及当前固定核结构 | 有来源并经审核的RESPONSE半径变形映射，或明确固定半径的不同主张 | BLOCKED；严格2211七nuisance复现 |
| G_QF QF范围外贡献 | 2–70keVnr原始拟合域、当前域保护与旧低反冲延拓诊断 | 完整ROOT高能尾的范围外响应及小反nu_e绝对源权重，若以后选择该完整源 | PARTIAL；完整ROOT源的全反冲预测 |
| G_CLOCK ROOT时钟起点与prompt νμ时间形状 | 0与+75ns诊断、固定观测窗口/效率的实现及交接包测试；ROOT时间边缘保持原样 | 发布者的ROOT时钟起点、onset定义和作者逐分量时间模板；不能把19.3m/c自动再加一次 | PARTIAL；官方时间零点认定,prompt逐箱作者复现 |
| G_FIG1 论文图形与正文积分的口径 | 已核验原始矢量图与主论文内嵌几何一致；图形信号积分约312.59；截图proxy不作权威 | 作者原始模板解释Fig.1可见曲线与正文306±20、PE/time残差积分的差别 | PARTIAL；论文图精确总率复现,逐味实验显著性 |
| G_EQ75 共享RESPONSE装配与源论文式75对应 | 论文p15/18/19原式、当前amplitude/responses代码及Cs/I实际核表可查 | 核实q²/mN²、-2q/mN、4π/(2J+1)、np/iso归一及DeltaSigma干涉，不通过计数拟合选约定 | BLOCKED；P04/P05物理接受,P07新权威Slow |
| G_FLUENCE_SCOPE POT总注量与0–6us时间归一解释 | η由POT/产额/距离计算；两种数值口径均已知 | H3明确采用的注量定义与原文依据；不能按结果接近341选择 | BLOCKED；P03源合同接受,P07总率解释 |
| G_TRUNCATION 一体流近似与遗漏两体流 | 2601.19883v2 p12-13功率计数、p30明确数值仅一体流 | 本轮先明确一体流主张及截断误差未知；若要两体流须另有电流与核矩阵元，不能用非M占比当误差 | PARTIAL；完整核理论精度声称 |

| 下一步能力 | 当前状态 | 必需输入与出处 | 实际下一步 |
|---|---|---|---|
| P04原有RESPONSE资源复用 | LOCAL_RESOURCE_READY | C_RESOURCE_BINDING USER_CONFIRMED [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>); C_W_Cs133_M SOURCE_EXTRACTED [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>); C_W_I127_M SOURCE_EXTRACTED [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) | 通过ResponseDB直接加载原data核表，沿原基底/单位约定使用 |
| P06 nominal探测器响应准备 | DRAFT_INPUTS_PRESENT | C_QF SOURCE_EXTRACTED [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>); C_QF_DOMAIN SOURCE_EXTRACTED [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>); C_GAMMA SOURCE_EXTRACTED [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>); C_EFF SOURCE_EXTRACTED [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>); C_TIME_EFF SOURCE_EXTRACTED [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) | 按官方nominal系数核对实现，保留systematic标签冲突 |
| P07下一轮逐箱预测准备 | BLOCKED_BY_CURRENT_PHYSICS_REVIEW | C_RESOURCE_BINDING USER_CONFIRMED [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>); C_SOURCE_CHOICE PROJECT_DERIVED [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>); C_DENOM PROJECT_DERIVED [S_TIME_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) | 先完成H3和P04/P05对应审核，再确定单一阶段计算入口并运行P07 |
| P09论文统计 | BLOCKED | C_BG_GAP PROJECT_DERIVED [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>); C_RADIUS SOURCE_EXTRACTED [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) | 闭合背景归一，分别声明固定半径诊断和完整论文nuisance |
| P10外部benchmark | NOT_RUN_FOR_R3 | C_BG_GAP PROJECT_DERIVED [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>); C_RADIUS SOURCE_EXTRACTED [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) | 按r3声明的能力验收；不继承旧诊断PASS |

原文核查记录与机器文件检查分别保留。数值存在、来源闭合、转换等价和物理适用性的接受各自有据，程序可运行不能替代它们。

[返回目录](#report-toc)

## 2026-11-17 νμ时间诊断补充（默认保持）

默认 Δt=0 ns，注量口径 `reference_window`，中子模式 `raw`。新增控制不授予论文等价、时钟校准或拟合接受。

对完整支撑域归一化的时间源 $h_f$，使用 $W_{fj}(\delta)=\int_{t_j}^{t_{j+1}}h_f(t-\delta)\epsilon_T(t)dt/q_f$；$q_f=\int_0^6h_f(t)dt$ 固定为零位移值。`full_support` 模式的分母为1。两模式使用相同数值η，是不同注量口径的对照，不能直接删除 `/q` 当作物理修复。

正位移使源晚到；观测箱及εT(t_rec)固定。信号和BRN/NIN同步平移，SSB、观测C/AC及计数误差不变。中子归一化分母同样锚定零位移，平移后不拉回固定总数。

| 中子模式 | 明确约定 |
|---|---|
| raw（默认） | 原始官方PE×Trec表，零位移约27.423763/6.908565事件 |
| prior_posteff | 零位移分析窗、时间效率后18.4/5.6事件 |
| bestfit_posteff | 零位移效率后17.3/5.5事件；仅总数控制，不是完整论文最佳拟合模板 |
| prior_preeff | 零位移时间效率前18.4/5.6事件 |

后三者是独立归一化解释；现有证据尚不能唯一确定论文实现。+75ns为诊断候选，不能据此断定ROOT读错、遗漏飞行时间或已确定作者onset。主线原生SM/RESPONSE保持；KN是独立对照，均未拟合或逐味缩放。

原生SM参考窗353.465609、全支撑329.016423，相差24.449186事件；KN参考窗333.113488，+75ns约331.266392。341是不同模型/口径的论文SM参考，不作为调参目标。原生二维ROOT联合源的完整等价未验证。

论文对照采用经主论文内嵌几何核验的原作者矢量图，图中CEνNS积分约312.59，与正文306±20的差别保留；每味分量是论文模型曲线，并非独立逐味测量。截图proxy的νe≈89.23及强制总数不能用于科学定标。

直接材料：[用户README](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/README.md>) · [交接说明](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/HANDOFF_PROMPT.md>)。

实际入口：[时间/中子适配器](<../../../../../examples/COHERENT_CsI/time_resolved_common/timing_diagnostics.py>) · [历史入口（已撤下）](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_benchmark.py>) · [历史诊断代码（已撤下）](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py>) · [本次结果](<../../../../../outputs/csi2021_timing_diagnostics_20261117/README.md>)。

## r3重新onboarding：当前审阅范围

**同一CsI2021_time_9x11；此版是物理配置草稿，未进入新的正式计数阶段。** 三个并列入口已撤下；旧353.465609及+75ns等结果仅作历史诊断，不是本轮已接受Slow。

| 独立维度 | 当前候选/资源 | 审核状态 |
|---|---|---|
| Interaction | 原生SM；描述符li2026_legacy | DRAFT，待P04 |
| Nuclear structure | 用户选定原RESPONSE，Cs133/I，np基底 | 原表复用选择保留；外部生成等价待核 |
| Kinematics/Cross-section | 现有elastic_neutrino_nucleus_v1 / Li2026LegacyInteraction | 式75装配与核表归一需P04/P05核对 |
| Detector | 14.6kg；QF→Gamma→PE效率→时间接受；T≥2keVnr候选 | 参数已取得，适用域/低反冲截断待P06复审 |
| Time source | 解析DAR能谱×ROOT时间边缘；0ns | +75ns仅历史对照，官方时钟未验证 |
| Fluence | η=5.793617637932339e14 cm⁻²/味 | full_support与reference_window含义需H3确认 |
| Observable | PE[0,8,12,16,20,24,32,40,48,60]×11时间箱，raw C/AC | 99箱数值已取得；边界来源限制保留 |
| Statistics/Fast | 本轮先做信号前向计算 | P08/P09 NOT_REQUESTED；不运行拟合 |

已取得官方事件/背景/ROOT、响应系数、原核表与原文。尚缺的是若干物理对应的核验，不是这些数值文件不存在。共享理论公式只在P04/P05核查，实验正文登记模块选择/资源和阻断范围。

Compiler/Renderer：本轮尚未生成新YAML/NPZ运行包。H3及必要合同接受后，按统一IR→tools/compile_experiment_package.py→机器文件/Physics MD生成，不以旧自定义报告冒充新包。

需要审核的具体问题：① η按完整时间支撑域还是0–6μs参考窗解释；② 本轮接受的一体流范围及未知两体流误差；③ 背景归一只作分列诊断，暂不认定作者完整模板。共享式75冲突须先核查，不用调参消除。

当前计划：[Phase0计划](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/00_EXECUTION_PLAN.md>) · [可恢复进度](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/00_MIGRATION_PROGRESS.md>) · [来源/冲突](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P02_MISSING_AND_CONFLICTS.md>)。
