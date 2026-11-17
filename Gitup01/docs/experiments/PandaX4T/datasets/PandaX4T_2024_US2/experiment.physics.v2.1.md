# PandaX-4T 2024 US2 — Response onboarding v2.1 修订草稿（新版本）

**版本：v2.1 修订草稿。日期：2026-11-06。方法：完整探测器 Response 折叠。状态：DRAFT / PARTIAL，逐项数值输入审阅草稿。**

[P00来源登记](<../../../../../../重构/20261106_Onboarding_provenance_revision/P00_SOURCE_REGISTER.yaml>) · [P01逐项证据](<../../../../../../重构/20261106_Onboarding_provenance_revision/PandaX4T_P01_EVIDENCE_LEDGER.yaml>) · [P03配置草稿](<../../../../../../重构/20261106_Onboarding_provenance_revision/PandaX4T_P03_PHYSICS_CONTRACT.yaml>) · [下一步输入](<../../../../../../重构/20261106_Onboarding_provenance_revision/P02_MISSING_AND_HANDOFF.md>)

[精简版 v2.1](<experiment.physics.summary.v2.1.md>) · [用户资料 v2.1](<EXPERIMENT_USER_INPUT.v2.1.md>) · [标准参考文献](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md>) · [数据目录](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/README.md>) · [旧 onboarding（原位保留）](<../../../../../../../.experiment-auto-runs/cevns-threephase-20261105-high01/snapshot/docs/experiments/PandaX_4T/datasets/PandaX4T_SolarB8_Run0_Run1/EXPERIMENT_USER_INPUT.md>)

本版将已取得的数值、数据文件和直接原文定位放入对应物理章节。完整响应核及统计依赖的取得情况按字段登记。

<a id="toc"></a>

## 目录

- [1. 实验范围与版本](#s1)
- [2. Source](#s2)
- [3. Target](#s3)
- [4. 共享物理模块选择](#s4)
- [5. Detector Response](#s5)
- [6. Observable 与分箱](#s6)
- [7. Prediction folding](#s7)
- [8. Statistics 与背景](#s8)
- [9. 数据清单与逐项出处](#s9)
- [10. 缺失、验证与参考文献](#s10)

<a id="s1"></a>

## 1. 实验范围与版本

实验范围为PandaX-4T Run0+Run1的US2。结果比较目标为2411.11749v1 Fig.1/2/4。下表列出本轮已取得资料及需要补充的输入。

| 实际输入 | 本轮已取得 | 待补内容 |
|---|---|---|
| Detector | Qy、接受度曲线、通用校准及逐run率误差 | 2024 US2完整低能核 |
| Statistics | 原实验与benchmark投影D/B、原文率约束 | 原版完整形状、分箱/约束细节 |

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)

[返回目录](#toc)

<a id="s2"></a>

## 2. Source

太阳 $^8\mathrm{B}$ 源谱使用完整 Bahcall 官方四列表 [[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4)。第一列为 $E_\nu$（MeV），第二列中心谱形（MeV$^{-1}$），第三/四列为有效 ±3σ 谱形。它们不含总通量、效率、靶核数或曝光。

$$
\frac{d\phi}{dE_\nu}=\Phi_{8B}f_{8B}(E_\nu). \tag{1}
$$

| 符号/输入 | 定义与单位 | 资源与精确出处 |
|---|---|---|
| $f_{8B}$ | 归一化能谱形，MeV$^{-1}$ | `b8_bahcall1996_official.txt` 第二列。[[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4) 原表列 2 |
| $\Phi_{8B}$ | 总通量，cm$^{-2}$s$^{-1}$。参考值 $5.46\times10^6$，归一化相对误差 12% | [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1) Sec.III 式 (11) 后及式 (17) 后。上游 SSM 文献 [[5]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-5) |
| 谱形误差 | ±3σ 包络，非 12% 总率误差 | [[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4) 原表列 3/4。不直接改成独立逐点 Gaussian |

中心表 829 行，0–16.56 MeV，保留官网原始小数。梯形积分约 0.999986544，本次不静默重新归一化。计划在表内线性插值，表外置零是明确的数值约定而非论文给出所有高能尾的精确证明。需做端点/积分收敛检查。味普适 SM/NGI 基准使用所有活跃味总通量。改为味相关相互作用时需另给传播与味分量，不能沿用此简化。

| 实际数值文件/处理 | 数据与取得情况 | 直接原文定位与核验 |
|---|---|---|
| [官网四列源谱](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/b8_bahcall1996_official.txt>) | 829×4，Eν=0–16.56MeV，列2/3/4为中心/±3σ形状，单位MeV⁻¹ | [[4]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4>) 官网原件全部四列逐字节核对 |
| 总通量参考 | 5.46×10⁶ cm⁻²s⁻¹ | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p5 Eq.(11)后 |
| 总通量相对误差 | 0.12 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |
| 中心谱梯形积分 | 0.999986544 | 项目推导，输入为原829行中心谱与能量 |
| 插值与端点 | 拟议表内线性插值、表外零，DRAFT | 本版数值约定，P07需检查收敛和尾贡献 |

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06。四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [[4]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4>) [本地实际核对材料](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- VINYOLES N, SERENELLI A M, VILLANTE F L, et al. A new generation of standard solar models[J]. The Astrophysical Journal, 2017, 835(2): 202. DOI: [10.3847/1538-4357/835/2/202](https://doi.org/10.3847/1538-4357/835/2/202). [arXiv:1611.09867](https://arxiv.org/abs/1611.09867). 本任务采用的通量值与 12% 误差直接定位于文献 [1] 第 III 节和式 (17) 后文字，后者引用本篇。未声称从任意 SSM 表重新推导。 [[5]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-5>) [本地实际核对材料](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Vinyoles-abs.html>)

[返回目录](#toc)

<a id="s3"></a>

## 3. Target

靶材为液氙，采用多同位素求和。新补充的 NIST 天然数丰度表是参考组成 [[9]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9)，没有假装取得两实验的独立氙样品同位素化验。

$$
\overline M=\sum_A f_A M_A,\qquad n_A^{(t)}=\frac{10^6N_{\rm A}f_A}{\overline M}. \tag{2}
$$

| 符号 | 定义与单位 | 数据位置/性质 |
|---|---|---|
| $f_A$ | 核素数丰度，无量纲 | `xenon_natural_isotopes_nist_v2.txt` 列 3。[[9]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9) 对应 Xe 行 |
| $M_A$ | 原子摩尔质量，g/mol，数值对应原子质量 u | 同表列 2。它不是裸核质量 |
| $N_{\rm A}$ | 阿伏伽德罗常量，$6.02214076\times10^{23}$ mol$^{-1}$ | [[13]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-13) §2.2/Table 1，精确 SI 定义常量 |
| $n_A^{(t)}$ | 每吨氙中该核素核数，nuclei/t | 本文推导量。$10^6$ g/t |

丰度包含 Xe124/126/128/129/130/131/132/134/136，和为 1。未将数丰度直接当质量分数。将原子质量 u 的数值用于 g/mol 时，本版显式近似摩尔质量常量为 1 g/mol。现代 SI 下并非精确恒等，见 [[13]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-13) 印刷页 130。这是本版显式的质量换算近似，未将其解释为实验质量误差。截面所需裸核质量仍须由共享模块明确转换/近似，不把原子质量改称裸核质量。旧单一 Xe131 近似不用于新版默认。式 (2) 为项目的质量到核数推导。


参考天然组成的平均摩尔质量约 131.292761448 g/mol、每吨总核数约 4.586803334e+27。由式 (2) 与 NIST 表中心值计算，未传播组分误差。

| 核素 A | 数丰度 | 核数（nuclei/t，推导） |
|---|---:|---:|
| 124 | 0.00095 | 4.366636774e+24 |
| 126 | 0.00089 | 4.082254968e+24 |
| 128 | 0.01910 | 8.761711729e+25 |
| 129 | 0.26401 | 1.210943601e+27 |
| 130 | 0.04071 | 1.867287637e+26 |
| 131 | 0.21232 | 9.738884312e+26 |
| 132 | 0.26909 | 1.234244562e+27 |
| 134 | 0.10436 | 4.786650356e+26 |
| 136 | 0.08857 | 4.062669317e+26 |

### 原子质量与数丰度的完整输入

| A | 原子质量(u) | 数丰度 | 直接出处 |
|---|---|---|---|
| 124 | 123.9058920000 | 0.00095 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |
| 126 | 125.9042983000 | 0.00089 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |
| 128 | 127.9035310000 | 0.01910 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |
| 129 | 128.9047808611 | 0.26401 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |
| 130 | 129.9035093490 | 0.04071 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |
| 131 | 130.9050840600 | 0.21232 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |
| 132 | 131.9041550856 | 0.26909 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |
| 134 | 133.9053946600 | 0.10436 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |
| 136 | 135.9072144840 | 0.08857 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe对应A行 |

| 曝光输入 | 实际值 | 直接出处与取得情况 |
|---|---|---|
| Run0/Run1 US2 FV质量 | 2.78 / 2.16 t | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3 FV段落，括号内US2 |
| US2总曝光 | 1.04 t yr | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3同段及摘要 |
| 逐run有效曝光 | MISSING | 需取得afterglow veto后的有效时间/曝光，阻断run相关P07 |

### 本章参考文献

- BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值。未称为实验氙同位素实测报告，也未称为裸核质量。 [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) [本地实际核对材料](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- BUREAU INTERNATIONAL DES POIDS ET MESURES. The International System of Units (SI)[S/OL]. 9th ed., V4.01 (June 2026). Sèvres: BIPM, 2026[2026-11-06]. DOI: [10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291). [官方入口](https://www.bipm.org/en/publications/si-brochure). §2.2/Table 1，印刷页 123–124（英文 PDF 第 13–14 页）给出阿伏伽德罗常量的精确值。§2.3.1 印刷页 130 给出摩尔质量常量关系。 [[13]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-13>)

[返回目录](#toc)

<a id="s4"></a>

## 4. 共享物理模块选择

Interaction、Nuclear structure、Kinematics、Cross-section 是独立选择，实验文档只登记接口选择，不复制公共 EFT/核响应推导。

| 维度 | 项目已存在候选 | v2 说明 |
|---|---|---|
| Interaction | `li2026_sm_left_v1` / `li2026_matching_v1` | 先以 SM 验证 response。NGI 需逐项匹配 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1) 的算符/耦合约定 |
| Nuclear structure | `nuclear_np_polynomial_v1` | 本地 JSON 的 Xe 系数存在。外部源表/符号/归一化溯源未闭合，不称已获独立科学验证 |
| Kinematics | `elastic_kinematics_v1` | 校验真实反冲/入射能量的单位、支撑与运动学阈值 |
| Cross-section | `li2026_dsigma_v1` | 核响应进入截面。探测器 Response 在其后折叠，二者不混同 |
| Detector | 尚无该实验正式 Runtime binding | 本文完整响应合同，不虚构已注册实现 |

对照的 SM 参考点为 $\sin^2\theta_W=0.23857$（无量纲），直接定位 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1) PDF 第 3 页 Sec.II A 式 (2) 后文字。Fig.2 扫描该参数时不固定为此数。本版只登记参考点，没有改 Runtime 默认值或替共享模块补参数。

文献 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1) 的 SM/Scalar/Vector 使用 Klein–Nystrand 形状因子，见式 (3)。不能因选择项目核响应模块就声称两者逐点完全相同。Fig.4 所需轴矢量/张量自旋响应、标量核子输入及理论约定须完成独立对照后再作精确比较。

| 本地实际资源 | 已有内容 | 原文与科学核验范围 |
|---|---|---|
| [共享模型登记](<../../../../../cevns_pyeft/experiments/model_bindings.json>) | 本章候选ID在登记中存在 | [[15]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-15>) 模型ID与接口声明已核 |
| [核响应JSON](<../../../../../data/responses/responses_all.json>) | nuclei/Xe128,129,130,131,132,134,136 的basic、exp_factor、responses | [[16]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-16>) 本地内容已有，原始外部来源与归一化待核 |
| 天然Xe覆盖 | Xe124/Xe126系数MISSING，其参考数丰度合计0.00184 | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>)两行丰度求和与本地JSON键检查，所选核模型的覆盖处理待审阅 |

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值。未称为实验氙同位素实测报告，也未称为裸核质量。 [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) [本地实际核对材料](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- CEvNS-pyEFT共享模型登记[CP/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `1d03f7e0136be69c7d8c12324eb4e26c1c0c6093496efc7c19bfd77f9f1bcf24`。 [[15]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-15>) [本地实际核对材料](<../../../../../cevns_pyeft/experiments/model_bindings.json>)
- 本地核响应聚合表responses_all.json[DS/OL]. 本地工作副本, 2026-11-06. 版本SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。本地文件责任者与上游核物理来源待核。直接文件内容已核，外部科学来源保持待补。 [[16]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-16>) [本地实际核对材料](<../../../../../data/responses/responses_all.json>)

[返回目录](#toc)

<a id="s5"></a>

## 5. Detector Response

**本次八箱一维响应P(Ne箱|T)为 MISSING。** 已有Qy、总接受度曲线和通用校准参数，分别用于均值检查、边际接受率检查和模型参考。

式(3)为本项目对通过选择并进入观测箱概率的数学定义，来自概率密度在箱域上的积分。

$$
P_{r\mathbf i}(T;\boldsymbol\eta)=\int_{\Omega_{r\mathbf i}}p_r(\mathbf x\mid T;\boldsymbol\eta)\epsilon_r(\mathbf x,T;\boldsymbol\eta)\,d\mathbf x,\qquad0\le\sum_{\mathbf i}P_{r\mathbf i}\le1. \tag{3}
$$

本次2411.11749v1基准比较采用一维电子数/S2谱。PandaX原生二维响应可沿width积分，XENONnT原生四维模板可沿其余三个观测轴求和，得到相应一维箱概率。原生多维likelihood的附加输入另列为独立能力。直接依据为文献[1] PDF p5 Eq.(12)后的S2-only说明。

| 符号/必需输入 | 实际数值取得情况 | 数值文件及单位 | 直接出处及影响 |
|---|---|---|---|
| $T,\mathbf x$ | 本次x为重建Ne，范围4–8。原生二维另含width | electron，width用µs | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3 ROI、p6 Fig.5，[[11]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-11>) PDF p4 Fig.2 |
| $P_{ri}(T;\eta)$ | **MISSING 八箱一维概率核** | 需要P(Ne箱\|T)，或可生成它的完整模型 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5指向NEST/WS，[[10]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-10>) 官网提供两个事件CSV |
| $p_r(N_e\mid T)$ | MISSING能量相关重建Ne分布与选取的联合响应 | 需要量子涨落、电子损失、S2增益/涨落及选择，或直接一维模板 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5模型说明。影响选取的width/位置效应可通过边际化包含 |
| $\epsilon_r(N_e,w,T)$ | 条件选取待补，边际总接受度已有 | [总接受度数值表](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_us2_acceptance_2407.10892v3.txt>)，无量纲 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3 Fig.1黑色虚线，供ΣP(T)检查 |
| $Q_y(T)$ | nominal、best-fit和±1σ带均已数字化 | 下表给原节点及完整文件，e⁻/keV | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Fig.4下图。模型曲线选择保持DRAFT |
| $L_y(T)$及光/电荷关联 | 模拟生成US2选择时需要。Ly曲线已定位，数值与关联模型待整理 | Fig.4上图尚未提取为数值表，直接提供一维P时由核包含 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Fig.4上图及NEST/WS说明 |
| 增益及涨落 | 通用校准10参数已有，US2低能完整配置待补 | [Table II参数](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_response_calibration_2403.04239v2.json>) | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) PDF p21 Table II，通用NR拟合域约6–90keV |
| $\Omega_{ri},\eta$ | 本次Ne八箱edges与benchmark归一化误差已有 | 第6、8节。响应形变扫描另需校准网格及约束 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p5–6，原生二维width边界列为附加输入 |

### 已取得的Qy原节点

完整36×2原表与精度见 [pandax_qy_nominal.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal.txt>)。能量覆盖约0.2–3.1keVnr。直接来源为2407.10892v3 PDF p5 Fig.4下图，代表行如下。[[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>)

| 原表行 | T (keVnr) | Qy (e⁻/keV) |
|---|---|---|
| 1 | 0.2 | 2.291009926 |
| 19 | 0.8035793763 | 6.384272539 |
| 36 | 3.1 | 6.658439429 |

完整37×2原表与精度见 [pandax_qy_bestfit.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_bestfit.txt>)。能量覆盖约0.2–3.1keVnr。直接来源为2407.10892v3 PDF p5 Fig.4下图，代表行如下。[[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>)

| 原表行 | T (keVnr) | Qy (e⁻/keV) |
|---|---|---|
| 1 | 0.2 | 4.422195042 |
| 19 | 0.3935761577 | 6.097661276 |
| 37 | 3.1 | 7.21562959 |

完整119×3原表与精度见 [pandax_qy_nominal_band.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal_band.txt>)。能量覆盖约0.20185–3.05512keVnr。直接来源为2407.10892v3 PDF p5 Fig.4下图，代表行如下。[[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>)

| 原表行 | T (keVnr) | Qy下界 | Qy上界 |
|---|---|---|---|
| 1 | 0.2018500125 | 0.1202865379 | 4.518662938 |
| 60 | 0.7852876747 | 5.475680312 | 7.228347122 |
| 119 | 3.055123576 | 6.093280149 | 7.239561605 |


### US2总接受度的实际数值

| 原表行 | T (keVnr) | 总接受度 | 直接出处 |
|---|---|---|---|
| 1 | 0.2999999995 | 0.00579130467 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3 Fig.1 Total(US2) |
| 25 | 0.7629999995 | 0.1397927242 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3 Fig.1 Total(US2) |
| 50 | 1.6405 | 0.1418463306 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3 Fig.1 Total(US2) |
| 75 | 2.479 | 0.05028643461 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3 Fig.1 Total(US2) |
| 99 | 2.999999999 | 0.01554690094 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p3 Fig.1 Total(US2) |

完整99节点见 [接受度数据](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_us2_acceptance_2407.10892v3.txt>)。线性T与log接受度坐标标定原PDF矢量节点，图框边界由折线求交，覆盖约0.3–3keVnr。灰带与协方差继续待补。

### 通用响应模型的已取得校准值

| 输入 | 实际数值与误差 | 单位 | 直接出处 |
|---|---|---|---|
| p_dpe | 0.22 | 1 | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| g1 | 0.0997 −0.0005/+0.0002 | PE/photon | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| g2b | 4.12 −0.04/+0.06 | PE/electron | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| f_g1_Run1 | 0.90985 | 1 | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| f_g2b_Run1 | 1.22067 | 1 | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| pNR_0 | 0.7 −0.3/+0.3 | 1 | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| pNR_1 | -1.6 −0.7/+0.9 | 1 | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| pNR_2 | 1.3 −0.7/+0.5 | 1 | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| pNR_3 | -0.6 −0.4/+0.4 | 1 | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |
| A_NR | 1.06 −0.1/+0.09 | 1 | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 PDF p21 Table II |

完整精度和字段见 [pandax_response_calibration_2403.04239v2.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_response_calibration_2403.04239v2.json>)。

g2b对应底部阵列增益。文献[2] PDF p2给出总g2约17–20 PE/e⁻作为量级参考。US2 sub-keV条件下的完整涨落和选取配置需要配套输入。

事件表中的Ne是由S2换算的重建量，因此可以为小数。Qy控制平均产生电子数，S2增益及测量涨落继续影响重建箱归属。

### 响应矩阵与模拟配置的物理含义

矩阵的一行对应真实反冲能量T，一列对应通过选取后的观测箱。矩阵元P_i(T)给出该反冲落入该箱的概率。固定T反复模拟，统计各箱事件数占全部生成事件的比例，即可得到这一行。各箱概率之和是分析窗口内的总接受率。

模拟配置规定产生上述概率的物理随机过程，包括电荷与光产额、量子和复合涨落、电子漂移损失、提取和S2增益、信号重建及选取。影响选取的宽度、位置和S1信息通过模型积分进一维核。其能量与run适用域、校准参数和数值实现均需具体来源。

Qy约束平均电子数，接受度约束通过选取的总比例，各观测箱的概率还需要重建量的分布。原事件表给出实测读数D，响应需要已知真实输入的校准或模拟。主文第7节将真实反冲谱与这些箱概率折叠。

实验文章中已展示的Qy、效率和D/B/SM投影均可提取，本版已保存相应数值。已核PandaX文献[2] Fig.1/4/5与XENONnT文献[3] Fig.1/2没有展示固定真实能量的逐箱概率表。SM信号投影混合了不同真实能量。仅凭这一条卷积结果，连同均值Qy和总接受率，不能唯一确定每个能量落入各箱的概率。若依据文中模型另作响应重建，须明确补入的涨落/选择参数与验证范围，不能标为原图直接提取的完整核，也不引入c_i来补偿缺口。

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）。本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- LUO Y, BO Z, ZHANG S, et al. (PandaX Collaboration). Signal response model in PandaX-4T[J]. Physical Review D, 2024, 110: 023029. DOI: [10.1103/PhysRevD.110.023029](https://doi.org/10.1103/PhysRevD.110.023029). 实际提取 [arXiv:2403.04239v2](https://arxiv.org/abs/2403.04239v2), 2024-03-08，第 21 页 Table II。本文 NR 拟合适用范围不能外推冒充 US2 sub-keV 校准。 [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2403.04239v2.pdf>)
- PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)。[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件。属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。 [[10]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-10>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)
- ZHANG M, et al. (PandaX Collaboration). Search for Light Dark Matter with 259 Days of Data in PandaX-4T[J]. Physical Review Letters, 2025, 135: 211001. DOI: [10.1103/rtnh-jn8s](https://doi.org/10.1103/rtnh-jn8s). [arXiv:2507.11930](https://arxiv.org/abs/2507.11930). 用于后续事件资料的采样/选择范围核对，不将其带约束的 DM likelihood 替换为 2024 自由 8B likelihood。 本轮实际核对arXiv:2507.11930v3（2025-12-08），PDF p4 Fig.2给出width单位µs，p7–8 Data availability与ref.[39]指定官方事件发布。 [[11]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-11>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-2507.11930v3.pdf>)

[返回目录](#toc)

<a id="s6"></a>

## 6. Observable 与分箱

严格响应分析保留 run。原实验 US2 likelihood 在 `(Ne, S2 width)` 二维空间 [[2]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2) 第 6 页。目标论文的一维核对使用 Ne edges=`[4,4.5,5,5.5,6,6.5,7,7.5,8]`，D=`[73,44,29,44,41,38,28,35]`，共 332。

新增后续官方 CSV [[10]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-10)：Run0=158、Run1=174 行。各自八箱为 `[38,21,14,19,18,17,14,17]` 和 `[35,23,15,25,23,21,14,18]`，相加与发表 D 一致。由于文件缺事件 ID 和不可变发布标签，不仅凭计数相同证明 2024 的完整事件集合相同。它们保持 `later_release_crosscheck`，width单位由文献[11] v3 PDF p4 Fig.2核为µs，二维width箱界仍为MISSING。

CSV的Ne列单位为electron，Width单位为µs，原发布由文献[11] PDF p7–8 Data availability/ref.[39]连接到官方页面。

### 本章参考文献

- BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- PANDAX COLLABORATION. PandaX-4T: Search for Light Dark Matter with 259-day data[DS/OL].[2026-11-06]. [官方发布入口](https://pandax.sjtu.edu.cn/data-release/pandax-4t-search-for-light-dark-matter-with-259-day-data/)。[run0_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv)、[run1_data.csv](https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv)。未提供不可变发布标签，访问日和 SHA256 固定本次原件。属于文献 [11] 的后续发布，逐箱相同不能独立证明 2024 事件 ID 完全相同。 本轮已直接核对新网址的发布正文，页面列出两个事件CSV下载链接。 [[10]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-10>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-release-259day.html>)
- ZHANG M, et al. (PandaX Collaboration). Search for Light Dark Matter with 259 Days of Data in PandaX-4T[J]. Physical Review Letters, 2025, 135: 211001. DOI: [10.1103/rtnh-jn8s](https://doi.org/10.1103/rtnh-jn8s). [arXiv:2507.11930](https://arxiv.org/abs/2507.11930). 用于后续事件资料的采样/选择范围核对，不将其带约束的 DM likelihood 替换为 2024 自由 8B likelihood。 本轮实际核对arXiv:2507.11930v3（2025-12-08），PDF p4 Fig.2给出width单位µs，p7–8 Data availability与ref.[39]指定官方事件发布。 [[11]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-11>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/pandax-2507.11930v3.pdf>)

[返回目录](#toc)

<a id="s7"></a>

## 7. Prediction folding

对各 run、各氙同位素独立进行真实谱到重建箱的折叠：

$$
\mu^{\rm sig}_{r\mathbf i}=\mathcal E_r t_{\rm yr}\sum_A n_A^{(t)}\int dT\,dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT}P_{r\mathbf i}(T;\boldsymbol\eta). \tag{4}
$$

| 符号 | 定义/单位 | 来源与归属 |
|---|---|---|
| $\mathcal E_r$ | run 曝光，t·yr | 对应测量文献，不从 detector mass 再乘一次 |
| $t_{\rm yr}$ | yr 到秒转换，31557600 s/yr | 本版数值约定：365.25 d/yr。非额外实验活时间 |
| $n_A^{(t)}$ | nuclei/t | 式 (2)。天然组成暂作参考 |
| $d\sigma_A/dT$ | cm²/keVnr | 共享截面输出，独立核响应选择 |
| $P_{r\mathbf i}$ | 含选择的 response | 式 (3)，不能再乘效率/曝光 |
| $\mu^{\rm sig}$ | 预测信号 events/bin | 项目推导关系，无作者 c_i |

曝光参考总量：PandaX US2 1.04 t·yr，XENONnT 2024 3.51 t·yr，定位文献 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1) Sec.III 及相应原测量。run 分解必须来自测量/对应版本，而非用更新模板发布中的 live time 替换。能量积分需要检验运动学域、网格收敛、阈值涨落及响应支撑外尾。不能用 c_i 拟合数值误差。

完整 Response 与作者简化模型的差异会真实影响预测。固定 c_i 是对特定参考谱的逐箱补偿，不能普遍替代会随 EFT 谱形变化的卷积。本版 $c_i$ 不属于输入字段。

| 式(4)输入 | 实际取得情况 | 来源与下一步依赖 |
|---|---|---|
| 源谱与靶核数 | 第2–3节有数值表及推导 | 对应P01/P03 claim |
| run曝光 | US2总量已有，逐run MISSING | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 相应原文段落 |
| 完整响应P | 2024 US2核MISSING | 第5节数据与状态传播到P07 |
| 积分网格及误差容限 | 待P07制定并验证 | 项目数值约定，DRAFT |

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06。四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [[4]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4>) [本地实际核对材料](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)

[返回目录](#toc)

<a id="s8"></a>

## 8. Statistics 与背景

每箱总期望由信号与各背景相加，式(5)为本项目的计数分量定义。

$$
\mu_{r\mathbf i}=\mu^{\rm sig}_{r\mathbf i}+\sum_k B^k_{r\mathbf i}. \tag{5}
$$

| 符号 | 实际取得情况 | 单位与来源 |
|---|---|---|
| $\mu^{sig}$ | 由第7节折叠求得，完整输入待补 | events/bin，项目推导 |
| $B^k$ | 下面给出已取得数值与拟合状态 | events/bin或原发布rate |
| $\mu$ | 同run同箱求和 | events/bin，项目推导 |

独立泊松计数和外部约束π构成式(6)的候选统计接口。

$$
-2\ln\mathcal L=2\sum_{r,\mathbf i}\left[\mu_{r\mathbf i}-D_{r\mathbf i}+D_{r\mathbf i}\ln\frac{D_{r\mathbf i}}{\mu_{r\mathbf i}}\right]-2\ln\pi(\boldsymbol\eta). \tag{6}
$$

| 符号/输入 | 实际取得情况 | 直接出处与处理 |
|---|---|---|
| D | 下表给完整小型投影，原始事件/4D文件见第6节 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) Fig.5 |
| $\pi(\eta)$ | 已取得的率约束列下表，完整约束和模板依赖仍待核 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 原测量统计段落 |
| D=0箱 | D log(D/µ)取0的极限 | 泊松deviance的数学极限，项目推导 |

### 本次一维benchmark的归一化约束

| 分量 | 相对标准差 | 直接出处 |
|---|---|---|
| 信号 | 0.22 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |
| Cathode | 0.31 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |
| MD | 0.23 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |

共同通量归一化误差为0.12，联合实验共用一次，直接依据为文献[1] PDF p6。下面的benchmark Fig.1分量按该再分析的参考状态保存。原生合作组likelihood的形状与校准约束作为另一项比较能力登记。Fig.2通量扫描时α与待测通量的参数化还需按原文构造核对。

### 原实验拟合投影

| Ne箱 | D | Cathode | MD | 参考信号 | 直接出处 |
|---|---|---|---|---|---|
| 4–4.5 | 73 | 27.269891 | 34.093572 | 13.918514 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p6 Fig.5上图 |
| 4.5–5 | 44 | 26.388059 | 6.246193 | 12.326476 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p6 Fig.5上图 |
| 5–5.5 | 29 | 27.354001 | 2.088537 | 10.811358 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p6 Fig.5上图 |
| 5.5–6 | 44 | 31.218598 | 0.970110 | 9.663606 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p6 Fig.5上图 |
| 6–6.5 | 41 | 20.835613 | 0.498423 | 8.498072 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p6 Fig.5上图 |
| 6.5–7 | 38 | 28.118928 | 0.545846 | 7.432962 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p6 Fig.5上图 |
| 7–7.5 | 28 | 24.752272 | 0.222476 | 6.615482 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p6 Fig.5上图 |
| 7.5–8 | 35 | 22.849224 | 0.336738 | 5.586346 | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p6 Fig.5上图 |

完整精度见 [pandax_original_fig5.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_original_fig5.txt>)，单位events/bin。背景和参考信号按原图拟合/参考状态保存，堆叠分量按多边形厚度提取。

### benchmark参考投影

| Ne箱 | D | Cathode | MD | 参考信号 | 直接出处 |
|---|---|---|---|---|---|
| 4–4.5 | 73 | 26.629834 | 33.977900 | 13.817828 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1左 |
| 4.5–5 | 44 | 25.801105 | 6.132597 | 12.337798 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1左 |
| 5–5.5 | 29 | 26.629834 | 2.486188 | 10.801845 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1左 |
| 5.5–6 | 44 | 30.441989 | 0.994475 | 9.671681 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1左 |
| 6–6.5 | 41 | 20.165746 | 0.497238 | 8.481800 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1左 |
| 6.5–7 | 38 | 27.458564 | 0.497238 | 7.628396 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1左 |
| 7–7.5 | 28 | 24.143647 | 0.165746 | 6.720131 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1左 |
| 7.5–8 | 35 | 22.320442 | 0.165746 | 5.687952 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1左 |

完整精度见 [pandax_benchmark_fig1.txt](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_benchmark_fig1.txt>)，单位events/bin。背景和参考信号按原图拟合/参考状态保存，堆叠分量按多边形厚度提取。

### 原实验US2拟合前总数

| 输入 | 实际数值与误差 | 单位 | 直接出处 |
|---|---|---|---|
| cathode_Run0 | 100 ± 24 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, cathode, US2 Run0 |
| cathode_Run1 | 104 ± 21 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, cathode, US2 Run1 |
| MD_Run0 | 25 ± 3 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, MD, US2 Run0 |
| MD_Run1 | 20 ± 4 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, MD, US2 Run1 |
| ER_Run0 | 1.3 ± 0.1 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, ER, US2 Run0 |
| ER_Run1 | 0.9 ± 0.2 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, ER, US2 Run1 |
| total_background_Run0 | 126 ± 24 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, total_background, US2 Run0 |
| total_background_Run1 | 125 ± 21 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, total_background, US2 Run1 |
| signal_reference_Run0 | 18 ± 4 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, signal_reference, US2 Run0 |
| signal_reference_Run1 | 25 ± 6 | events | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, signal_reference, US2 Run1 |

完整精度和字段见 [pandax_prefit_inputs_2024.v2.1.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_prefit_inputs_2024.v2.1.json>)。

### 原实验US2逐run率误差

| 输入 | 实际数值与误差 | 单位 | 直接出处 |
|---|---|---|---|
| signal_selection_Run0 | 0.11 | fractional rate uncertainty | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Table IV, US2 Run0 |
| signal_selection_Run1 | 0.17 | fractional rate uncertainty | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Table IV, US2 Run1 |
| signal_model_Run0 | 0.17 | fractional rate uncertainty | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Table IV, US2 Run0 |
| signal_model_Run1 | 0.16 | fractional rate uncertainty | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Table IV, US2 Run1 |
| cathode_model_Run0 | 0.24 | fractional rate uncertainty | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Table IV, US2 Run0 |
| cathode_model_Run1 | 0.2 | fractional rate uncertainty | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Table IV, US2 Run1 |
| MD_model_Run0 | 0.13 | fractional rate uncertainty | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Table IV, US2 Run0 |
| MD_model_Run1 | 0.16 | fractional rate uncertainty | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) PDF p5 Table IV, US2 Run1 |

完整精度和字段见 [pandax_us2_rate_uncertainties_2024.v2.1.json](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_us2_rate_uncertainties_2024.v2.1.json>)。

原文p6说明系统误差关联，p5说明信号模型与paired通道的关联。原生二维prefit cathode/MD/ER形状、width边界与低能形变仍需资料。文献[1] PDF p6 Eq.(17)后的22%、31%、23%为其简化配置，按对应分析分别登记。

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)

[返回目录](#toc)

<a id="s9"></a>

## 9. 数据清单与逐项出处

| 实际数值文件 | 完整覆盖范围 | 直接出处与定位 | 处理方法 |
|---|---|---|---|
| [PandaX Qy标称](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal.txt>) | all rows; T_keVnr,Qy_e_per_keV | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p5 Fig.4 lower; Nominal dashed line | PDF vector digitization; logarithmic energy; no gain/efficiency/exposure |
| [PandaX Qy拟合值](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_bestfit.txt>) | all rows; T_keVnr,Qy_e_per_keV | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p5 Fig.4 lower; same figure; Best-fit solid line | joint paired+US2 fitted mean; not US2-only calibration |
| [PandaX Qy带](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_qy_nominal_band.txt>) | all rows; T_keVnr,Qy_lower,Qy_upper | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p5 Fig.4 lower; same figure; nominal gray +/-1 sigma band | PDF vector band; no covariance inferred |
| [PandaX原实验投影](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_original_fig5.txt>) | all 8 rows; bin,Ne_low,Ne_high,D,cathode,MD,signal; events/bin | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p6 Fig.5 upper, 4<=Ne<8 | D integers; fitted stacked components separated by polygon thickness |
| [PandaX benchmark投影](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_benchmark_fig1.txt>) | all 8 rows; bin,Ne_low,Ne_high,D,cathode,MD,signal; events/bin | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) 2411.11749v1 PDF p7 Fig.1 left | benchmark reference components; not independent prefit B |
| [8B官网完整谱表](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/b8_bahcall1996_official.txt>) | all rows/keys; detailed key map below | [[4]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4>) official b8spectrum.txt, all four columns | byte-identical download |
| [天然Xe九核素表](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/xenon_natural_isotopes_nist_v2.txt>) | all rows/keys; detailed key map below | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe rows 124,126,128,129,130,131,132,134,136 | parsed central values; uncertainties retained in official source download, not treated as zero |
| [Run0原事件CSV](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run0_events.csv>) | all rows/keys; detailed key map below | [[10]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-10>) p4-light-dark-matter/run0_data.csv | byte-identical download |
| [Run1原事件CSV](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run1_events.csv>) | all rows/keys; detailed key map below | [[10]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-10>) p4-light-dark-matter/run1_data.csv | byte-identical download |
| [PandaX逐run计数](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run_bins_v2.txt>) | all rows/keys; detailed key map below | [[10]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-10>) two event CSV; 0.5-electron bins in [4,8] | numpy.histogram by run |
| [通用响应十参数](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_response_calibration_2403.04239v2.json>) | all rows/keys; detailed key map below | [[6]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-6>) 2403.04239v2 p21 Table II | manual transcription with visual check |
| [US2逐run率误差](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_us2_rate_uncertainties_2024.v2.1.json>) | all records | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p5 Table IV, US2 columns | transcribed printed primary-source values |
| [US2总接受度](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_us2_acceptance_2407.10892v3.txt>) | all 99 rows, both columns | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p3 Fig.1, black dashed Total(US2), PDF curve index9 | native PDF vertices calibrated to linear energy/log efficiency; edge intersections in PDF coordinates |
| [US2 prefit总数](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_prefit_inputs_2024.v2.1.json>) | all ten scalar records | [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) 2407.10892v3 PDF p4 Table III, US2 Run0/Run1 expectation | transcription of printed prefit totals and uncertainties |

字段、原始精度、指纹和output位置见 [P01逐项证据](<../../../../../../重构/20261106_Onboarding_provenance_revision/PandaX4T_P01_EVIDENCE_LEDGER.yaml>)，配置逐字段引用P01，来源身份由P00统一维护。

[返回目录](#toc)

<a id="s10"></a>

## 10. 缺失、验证与参考文献

| 下一步能力 | 必需输入 | 实际状态 | 具体补充或核验 |
|---|---|---|---|
| Source/Target物理审阅 | 源谱、组成、核数、曝光 | 已有数值与原文，候选约定待审阅 | 按第2–3节逐项核对 |
| P06→P07一维重建谱 | 一维箱概率P_i(T)、曝光和观测窗口 | PandaX八箱核MISSING | 核实一维响应或其生成配置 |
| P09一维benchmark统计 | D/B参考投影与Eq.(17)归一化误差 | 数值已有，前向P核及通量扫描参数化待核 | 沿用对应再分析的参考状态并核对统计构造 |
| 原生多维likelihood | 二维/四维形状、分箱、校准约束 | 附加能力，仍有独立缺口 | 仅在该能力被请求时补齐原生输入 |
| Fig.4物理比较 | 核原始系数、归一化和算符匹配 | 来源待核 | 共享模块专项核验 |

本版为数据审阅草稿，相关P03字段均保留DRAFT。记录与查找结果见 [P02待补输入](<../../../../../../重构/20261106_Onboarding_provenance_revision/P02_MISSING_AND_HANDOFF.md>) 和 [本轮补充与验收](<../../../../../../重构/20261106_Onboarding_provenance_revision/README.md>)。

[返回目录](#toc)
