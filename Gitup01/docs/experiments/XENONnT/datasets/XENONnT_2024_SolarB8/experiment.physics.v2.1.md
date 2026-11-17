# XENONnT 2024 Solar 8B — Response onboarding v2.1 修订草稿（新版本）

**版本：v2.1 修订草稿。日期：2026-11-06。方法：完整探测器 Response 折叠。状态：DRAFT / PARTIAL，逐项数值输入审阅草稿。**

[P00来源登记](<../../../../../../重构/20261106_Onboarding_provenance_revision/P00_SOURCE_REGISTER.yaml>) · [P01逐项证据](<../../../../../../重构/20261106_Onboarding_provenance_revision/XENONnT_P01_EVIDENCE_LEDGER.yaml>) · [P03配置草稿](<../../../../../../重构/20261106_Onboarding_provenance_revision/XENONnT_P03_PHYSICS_CONTRACT.yaml>) · [下一步输入](<../../../../../../重构/20261106_Onboarding_provenance_revision/P02_MISSING_AND_HANDOFF.md>)

[精简版 v2.1](<experiment.physics.summary.v2.1.md>) · [用户资料 v2.1](<EXPERIMENT_USER_INPUT.v2.1.md>) · [标准参考文献](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md>) · [数据目录](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/README.md>) · [旧 onboarding（原位保留）](<../../../../../../../.experiment-auto-runs/cevns-threephase-20261105-high01/snapshot/docs/experiments/XENONnT/datasets/XENONnT_SolarB8/EXPERIMENT_USER_INPUT.md>)

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

实验范围为XENONnT SR0+SR1的2024太阳8B测量。结果比较目标为2411.11749v1 Fig.1/2/4。下表列出本轮已取得资料及需要补充的输入。

| 实际输入 | 本轮已取得 | 待补内容 |
|---|---|---|
| Detector | 早期YBe六表、响应基底/名义三箱核、2024接受度/参考谱。另存2026模板 | 早期重铸核对原2024 CEvNS分析的精度/等价性 |
| Statistics | 原图D/B、原文率约束及早期官方完整B/B8模板 | 模板/约束配套与严格原生分析等价性 |

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）。本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)。本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1。官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)

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
| [官网四列源谱](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/b8_bahcall1996_official.txt>) | 829×4，Eν=0–16.56MeV，列2/3/4为中心/±3σ形状，单位MeV⁻¹ | [[4]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4>) 官网原件全部四列逐字节核对 |
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

| 曝光输入 | 实际值 | 直接出处与性质 |
|---|---|---|
| SR0/SR1活时间 | 108.0 / 208.5 d | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p2 Dataset |
| SR0/SR1 FV质量 | 3.97±0.20 / 4.10±0.19 t | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p3 FV |
| 总曝光 | 3.51 t yr | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p3 FV |
| 按印刷中心值计算逐run曝光 | 1.17388090 / 2.34045175 t yr | 项目推导，质量×活时间/365.25，受原文印刷精度限制 |
| 早期公开reader曝光因子 | 1.174398 / 2.342593 t yr | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) statistical_model_base.yaml livetime_sr0/1名义字段。配套率模板乘数，候选版本 |

### 本章参考文献

- APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）。本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值。未称为实验氙同位素实测报告，也未称为裸核质量。 [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) [本地实际核对材料](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- BUREAU INTERNATIONAL DES POIDS ET MESURES. The International System of Units (SI)[S/OL]. 9th ed., V4.01 (June 2026). Sèvres: BIPM, 2026[2026-11-06]. DOI: [10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291). [官方入口](https://www.bipm.org/en/publications/si-brochure). §2.2/Table 1，印刷页 123–124（英文 PDF 第 13–14 页）给出阿伏伽德罗常量的精确值。§2.3.1 印刷页 130 给出摩尔质量常量关系。 [[13]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-13>)
- XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)。本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1。官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)

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

**已取得早期官方YBe重铸基底及名义三箱响应，另保留release2026完整模板。** 原2024 CEvNS分析的精确等价性待核。数值取得与版本适用性分开登记。

式(3)为本项目对通过选择并进入观测箱概率的数学定义，来自概率密度在箱域上的积分。

$$
P_{r\mathbf i}(T;\boldsymbol\eta)=\int_{\Omega_{r\mathbf i}}p_r(\mathbf x\mid T;\boldsymbol\eta)\epsilon_r(\mathbf x,T;\boldsymbol\eta)\,d\mathbf x,\qquad0\le\sum_{\mathbf i}P_{r\mathbf i}\le1. \tag{3}
$$

本次2411.11749v1基准比较采用一维电子数/S2谱。PandaX原生二维响应可沿width积分，XENONnT原生四维模板可沿其余三个观测轴求和，得到相应一维箱概率。原生多维likelihood的附加输入另列为独立能力。直接依据为文献[1] PDF p5 Eq.(12)后的S2-only说明。


### 进一步取得的早期官方YBe数值与响应基底

文献 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 公开了关联文献[12]的早期轻暗物质重铸数据。现在实际取得六份YBe光/电荷产额JSON、单能响应基底和原始B/B8模板。不再把XENONnT写成没有早期响应数值。基底HDF5日期为2024-08-06，B/B8为2024-06-30。日期是原文件metadata，不能单独证明它与2024 CEvNS主分析逐点等价。

| 完整原始数值 | 数组/能量域 | 代表值（原节点） | 产额单位 | 具体来源 |
|---|---|---|---|---|
| [YBe LY lower](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_lower.json>) | 501×2，存储域0.3–10keV | 原行173: T=1.00228572, yield=4.23592536 | photon/keVnr | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/ly_ybe_model_lower.json; utils.py::load_default_yield_model |
| [YBe LY median](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_median.json>) | 501×2，存储域0.3–10keV | 原行173: T=1.00228572, yield=5.07201493 | photon/keVnr | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/ly_ybe_model_median.json; utils.py::load_default_yield_model |
| [YBe LY upper](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_upper.json>) | 501×2，存储域0.3–10keV | 原行173: T=1.00228572, yield=5.91355144 | photon/keVnr | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/ly_ybe_model_upper.json; utils.py::load_default_yield_model |
| [YBe QY lower](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_lower.json>) | 501×2，存储域0.3–10keV | 原行173: T=1.00228572, yield=5.51044017 | electron/keVnr | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/qy_ybe_model_lower.json; utils.py::load_default_yield_model |
| [YBe QY median](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_median.json>) | 501×2，存储域0.3–10keV | 原行173: T=1.00228572, yield=6.18356191 | electron/keVnr | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/qy_ybe_model_median.json; utils.py::load_default_yield_model |
| [YBe QY upper](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_upper.json>) | 501×2，存储域0.3–10keV | 原行173: T=1.00228572, yield=6.78031926 | electron/keVnr | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/qy_ybe_model_upper.json; utils.py::load_default_yield_model |

lower/median/upper为官方重铸参数t=−1/0/+1的曲线。它们不提供逐能量独立误差或任意协方差。JSON存储域不等于物理适用域：原测量文献[3] PDF p3说明0.5keV以下产额设零，官方重铸reader只在0.51–5keV积分，不直接采用JSON在更低能量的非零曲线值。这里旧的SR0 WIMP Qy只保留作版本对照。早期YBe模型有了独立原始数值。

[SR0完整早期基底](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_basis.npz>)：轴顺序(energy,Ly,Qy,cs2,shadow,s1_bdt,s2_bdt)，shape=16×10×10×3×3×3×3。能量节点为 [0.51, 0.6, 0.7, 0.8, 0.9, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 3.5, 4, 4.5, 5] keV，Ly与Qy分别为1…10 photon/keV与electron/keV。每run1600个原HDF5全部逐值堆叠，保留原非零floor和检测效率，未把每行归一化成1。文件名tly_1…10/tqy_1…10在此表示物理产额，不能与2026模板的±3 nuisance坐标混淆。直接来源为 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) orthonormal_basis/及utils.py::BASIS_E_R、Template.interpolator。

[SR1完整早期基底](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_basis.npz>)：轴顺序(energy,Ly,Qy,cs2,shadow,s1_bdt,s2_bdt)，shape=16×10×10×3×3×3×3。能量节点为 [0.51, 0.6, 0.7, 0.8, 0.9, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 3.5, 4, 4.5, 5] keV，Ly与Qy分别为1…10 photon/keV与electron/keV。每run1600个原HDF5全部逐值堆叠，保留原非零floor和检测效率，未把每行归一化成1。文件名tly_1…10/tqy_1…10在此表示物理产额，不能与2026模板的±3 nuisance坐标混淆。直接来源为 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) orthonormal_basis/及utils.py::BASIS_E_R、Template.interpolator。

[SR0名义一维响应](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_nominal_1d.txt>)：46×4，列为T及三个cS2箱的通过概率，概率无量纲。

[SR1名义一维响应](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_nominal_1d.txt>)：46×4，列为T及三个cS2箱的通过概率，概率无量纲。

| run | T (keVnr) | cS2箱1概率 | cS2箱2概率 | cS2箱3概率 | 推导依据 |
|---|---|---|---|---|---|
| SR0 | 0.51 | 0.000250822205 | 6.73116677e-05 | 1.85242619e-06 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR0 | 1 | 0.00554983107 | 0.00445078373 | 0.000717062224 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR0 | 1.5 | 0.0128417143 | 0.0199721098 | 0.00873277685 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR0 | 2 | 0.0143824429 | 0.0358614995 | 0.0331001576 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR0 | 3 | 0.00678255508 | 0.0336521369 | 0.105760899 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR0 | 5 | 0.00029646588 | 0.00376196905 | 0.0913221503 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR1 | 0.51 | 0.000177950309 | 8.24732258e-05 | 2.61244063e-06 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR1 | 1 | 0.00360415749 | 0.00479188849 | 0.000919330393 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR1 | 1.5 | 0.00739187049 | 0.0187258611 | 0.0102584515 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR1 | 2 | 0.00730870609 | 0.029643203 | 0.0361044644 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR1 | 3 | 0.00270167687 | 0.0220718383 | 0.104573261 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |
| SR1 | 5 | 7.17318528e-05 | 0.00159903569 | 0.0819168817 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 基底与YBe median。项目推导 |

推导先对三个无关观测轴求和，再按官方utils.py::Template.interpolator的线性RegularGridInterpolator在(E,Ly,Qy)内插，并沿官方median产额曲线取值。能量网格为本地46点。此表标为PROJECT_DERIVED，不是论文直接给出的数组。没有使用Poisson宽度假设、额外效率、曝光、随机抽样或c_i。原reader采用随机抽样积分混合谱。本次只整理固定能量的响应，不运行其推断流程。

这套公开重铸方法的精度声明针对关联轻暗物质分析，不能直接推广成所有EFT谱形的误差界。严格复现2411.11749v1仍需检查所选响应、能量支撑与参考信号的偏差。[逐HDF5来源与处理记录](<../../../../../../重构/20261106_Onboarding_provenance_revision/EARLY_RESPONSE_EXTRACTION.json>) · [转换与一维推导脚本](<../../../../../../重构/20261106_Onboarding_provenance_revision/extract_early_response_candidate.py>)。

### 已执行的名义SM一致性检查

| run | 箱1差异 | 箱2差异 | 箱3差异 | 依据与覆盖 |
|---|---|---|---|---|
| SR0 | +0.45546% | +1.59765% | +6.29927% | (基底折叠/原始B8模板−1)，官方SM CDF与median YBe。项目验证 |
| SR1 | -3.23459% | -2.50075% | +1.55458% | (基底折叠/原始B8模板−1)，官方SM CDF与median YBe。项目验证 |

用原包CDF谱及总率335.5964691089417 events/(t·yr)，在0.51–5keV截断而不重新归一化，以10万/20万确定性分位中点核对积分。加密变化小于4×10⁻⁶。逐箱残差最大约6.30%，不能用总体相近替代逐箱检查。它是名义SM点的有限核验，不覆盖全部nuisance/EFT谱，也没有用c_i修正。来源为文献 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) 的signal/cevns_spectrum.json、原始B8 HDF5和响应基底。算法和结果见 [验证脚本](<../../../../../../重构/20261106_Onboarding_provenance_revision/validate_early_response.py>) 与 [完整验证结果](<../../../../../../重构/20261106_Onboarding_provenance_revision/EARLY_RESPONSE_VALIDATION.json>)。

### 独立保留的2026更新版模板

| 符号/输入 | 实际数值或数组 | 数值位置和单位 | 直接出处与适用性 |
|---|---|---|---|
| $T,\mathbf x$ | 0.5…5keVnr，每0.1一格。4个观测轴各3箱 | energy_keVnr与bin_edges_0…3 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) templates/sr0,1/mono/*文件名与/bins |
| $P_{ri}$ | 7×7×46×3×3×3×3，2254单能模板/run | probability，概率无量纲 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) HDF5 /templates/template无损堆叠，2026校准 |
| $p_r,\epsilon_r$ | 重建和选择在联合P模板中编码 | 原发布mono为检测效率，ΣP≤1 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) README Templates及单能原数组 |
| $\eta=(tLy,tQy)$ | 各轴[-3,-2,-1,0,1,2,3] | tLy、tQy，无量纲 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) 原文件名和模板网格。约束细节见第8节 |
| 2024原版对应 | 早期YBe基底和名义核已有，精确等价性待核 | 下述早期官方重铸核与2026更新核各自保留 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p3。[[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>)早期公开重铸。[[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>)更新分析 |
| 2024增益 | SR0 g2=16.5±0.6，SR1=16.9±0.5 | PE/e⁻，下表及校准JSON | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p3 gains段落 |
| 2024接受度 | S1、S2、combined各40个原PDF节点，附可见域标志 | [2024接受度数值表](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_fig1_acceptance.txt>)，无量纲 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1上图。边际选择检查，不能代替逐箱响应 |

### 从2024实验文章直接提取的接受度与参考谱

| 原表行 | T (keVnr) | S1接受度 | S2接受度 | combined接受度 | 直接出处 |
|---|---|---|---|---|---|
| 5 | 0.67 | 0.035798171 | 0.041267673 | 0.001505766 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1上图 |
| 13 | 1.15 | 0.080416399 | 0.19648051 | 0.015913495 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1上图 |
| 22 | 1.69 | 0.14080368 | 0.35726898 | 0.050997588 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1上图 |
| 31 | 2.23 | 0.20359698 | 0.44656326 | 0.092132138 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1上图 |
| 40 | 2.77 | 0.25556291 | 0.47874398 | 0.12398753 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1上图 |

完整40×8表见 [三条接受度及可见域标志](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_fig1_acceptance.txt>)。前三条曲线分别是浅蓝S1、深蓝S2和黑色combined。combined直接从黑线提取，不假设它等于S1×S2。原矢量能量节点约0.43–2.77keVnr，图框从0.5keVnr开始，部分低能combined节点在图框下方。原节点完整保留，inside_energy/inside_S1/inside_S2/inside_combined标出可见范围。图外节点不自动视为已核适用输入。

下图两条SM谱的完整40×6表见 [真实反冲参考谱及可见域标志](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_2024_fig1_sm_recoil_spectra.txt>)，横轴仍是真实反冲能量，纵轴为events/(t·yr·keVnr)。它们供卷积链结果检查，其中with-acceptance已经含接受度，不再乘一次效率，也不能作为中微子源谱或S2迁移矩阵。

| 原表行 | T (keVnr) | 未含接受度SM率 | 已含接受度SM率 | 直接出处 |
|---|---|---|---|---|
| 3 | 0.55 | 871.46548 | 0.27213946 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1下图，粉/红实线 |
| 12 | 1.09 | 269.23564 | 2.463553 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1下图，粉/红实线 |
| 21 | 1.63 | 71.116568 | 2.3150163 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1下图，粉/红实线 |
| 30 | 2.17 | 13.731096 | 0.84443486 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1下图，粉/红实线 |
| 39 | 2.71 | 1.4954892 | 0.12546826 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p4 Fig.1下图，粉/红实线 |

提取直接读取原PDF绘图路径，用真实刻度线标定线性能量/接受度与对数率坐标，无平滑、补点、外推或重新归一化。小数位仅用于重现图线。[原路径、坐标标定与源PDF指纹](<../../../../../../重构/20261106_Onboarding_provenance_revision/XENONNT2024_FIG1_VECTOR.json>) · [可复查提取脚本](<../../../../../../重构/20261106_Onboarding_provenance_revision/extract_xenon2024_fig1.py>)。这些是原图模型曲线的数值化，不能称为合作组原始校准数表。

### 完整数组文件与直接代表值

[SR0完整概率网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_release2026_v2.npz>)。全部网格的ΣP范围2.275041467e-14–1.662898717e-01。

[SR1完整概率网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_release2026_v2.npz>)。全部网格的ΣP范围2.318696623e-14–1.638626002e-01。

| run | T (keVnr) | cS2箱1概率 | cS2箱2概率 | cS2箱3概率 | 原始文件与推导 |
|---|---|---|---|---|---|
| SR0 | 0.5 | 1.0559645438e-04 | 2.1843030563e-05 | 3.5919993500e-07 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_0.500，tly=tqy=0 |
| SR0 | 1 | 4.1341844207e-03 | 2.8274737296e-03 | 3.5522422174e-04 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_1.000，tly=tqy=0 |
| SR0 | 1.5 | 1.1539532064e-02 | 1.5162963695e-02 | 5.0071236977e-03 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_1.500，tly=tqy=0 |
| SR0 | 2 | 1.5181640209e-02 | 3.2057033926e-02 | 2.1740113366e-02 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_2.000，tly=tqy=0 |
| SR0 | 3 | 9.2893339657e-03 | 3.9439197526e-02 | 8.7661872138e-02 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_3.000，tly=tqy=0 |
| SR0 | 5 | 7.0472125535e-04 | 7.3795907099e-03 | 1.1277266728e-01 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_5.000，tly=tqy=0 |
| SR1 | 0.5 | 8.2687551102e-05 | 2.7237839071e-05 | 4.7088371681e-07 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_0.500，tly=tqy=0 |
| SR1 | 1 | 3.0492564845e-03 | 3.2500666686e-03 | 4.6609651611e-04 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_1.000，tly=tqy=0 |
| SR1 | 1.5 | 7.6112460735e-03 | 1.5579541160e-02 | 6.2160878977e-03 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_1.500，tly=tqy=0 |
| SR1 | 2 | 8.9153218677e-03 | 2.9359088793e-02 | 2.5451562508e-02 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_2.000，tly=tqy=0 |
| SR1 | 3 | 4.2694627339e-03 | 2.8781082991e-02 | 9.2949021080e-02 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_3.000，tly=tqy=0 |
| SR1 | 5 | 2.0288400972e-04 | 3.5408200837e-03 | 1.0765568592e-01 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) mono_5.000，tly=tqy=0 |

probability轴顺序为(tLy,tQy,energy,cs2,shadow,s1_bdt,s2_bdt)。上述一维值在名义tLy=tQy=0处，对shadow、s1_bdt、s2_bdt三轴求和，完整46×3结果与算法回填P01/P03。完整keys还有energy_keVnr、tLy、tQy、axis_names及bin_edges_0…3。原模板metadata为2026-06-06，背景为2026-01-11，发布README关联文献[14]。

### 2024两run探测器与曝光原文数值

| 输入 | 实际数值与误差 | 单位 | 直接出处 |
|---|---|---|---|
| g1_SR0 | 0.151 ± 0.001 | PE/photon | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p3, Dataset and detector calibration text |
| g2_SR0 | 16.5 ± 0.6 | PE/electron | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p3, Dataset and detector calibration text |
| fiducial_mass_SR0 | 3.97 ± 0.2 | t | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p3, Dataset and detector calibration text |
| livetime_SR0 | 108 | day | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p2, Dataset and detector calibration text |
| g1_SR1 | 0.137 ± 0.001 | PE/photon | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p3, Dataset and detector calibration text |
| g2_SR1 | 16.9 ± 0.5 | PE/electron | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p3, Dataset and detector calibration text |
| fiducial_mass_SR1 | 4.1 ± 0.19 | t | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p3, Dataset and detector calibration text |
| livetime_SR1 | 208.5 | day | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p2, Dataset and detector calibration text |
| combined_exposure | 3.51 | t yr | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p3, fiducial-volume paragraph |

完整精度和字段见 [xenonnt_2024_calibration_inputs.v2.1.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_calibration_inputs.v2.1.json>)。

### 已取得的Qy原节点

完整99×4原表与精度见 [xenonnt_qy_sr0_23Vcm.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_23Vcm.txt>)。能量覆盖约0.5–100keVnr。直接来源为2406.13638v1 PDF p6 Fig.3右下SR0(23V/cm)，代表行如下。[[7]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-7>)

| 原表行 | T (keVnr) | Qy (e⁻/keV) | 可见域标志 | 原线虚线标志 |
|---|---|---|---|---|
| 1 | 0.4999999979 | 7.45102999 | 0 | 1 |
| 50 | 6.884361053 | 5.476034667 | 1 | 0 |
| 99 | 100 | 1.991116633 | 1 | 1 |

完整100×3原表与精度见 [xenonnt_qy_sr0_band.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_band.txt>)。能量覆盖约0.5–100keVnr。直接来源为2406.13638v1 PDF p6 Fig.3右下SR0(23V/cm)，代表行如下。[[7]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-7>)

| 原表行 | T (keVnr) | Qy下界 | Qy上界 |
|---|---|---|---|
| 1 | 0.4999999979 | 7.201570776 | 7.765614808 |
| 51 | 7.262838105 | 5.205385499 | 5.657345402 |
| 100 | 100 | 1.883201701 | 2.116291405 |


该旧Qy对应SR0 WIMP模型，2024 CEvNS的专门YBe响应由文献[3] PDF p3说明。原曲线的可见域、虚线标志和原节点保存在数据列中。

### 响应矩阵与模拟配置的物理含义

矩阵的一行对应真实反冲能量T，一列对应通过选取后的观测箱。矩阵元P_i(T)给出该反冲落入该箱的概率。固定T反复模拟，统计各箱事件数占全部生成事件的比例，即可得到这一行。各箱概率之和是分析窗口内的总接受率。

模拟配置规定产生上述概率的物理随机过程，包括电荷与光产额、量子和复合涨落、电子漂移损失、提取和S2增益、信号重建及选取。影响选取的宽度、位置和S1信息通过模型积分进一维核。其能量与run适用域、校准参数和数值实现均需具体来源。

Qy约束平均电子数，接受度约束通过选取的总比例，各观测箱的概率还需要重建量的分布。原事件表给出实测读数D，响应需要已知真实输入的校准或模拟。主文第7节将真实反冲谱与这些箱概率折叠。

实验文章中已展示的Qy、效率和D/B/SM投影均可提取，本版已保存相应数值。已核PandaX文献[2] Fig.1/4/5与XENONnT文献[3] Fig.1/2没有展示固定真实能量的逐箱概率表。SM信号投影混合了不同真实能量。仅凭这一条卷积结果，连同均值Qy和总接受率，不能唯一确定每个能量落入各箱的概率。若依据文中模型另作响应重建，须明确补入的涨落/选择参数与验证范围，不能标为原图直接提取的完整核，也不引入c_i来补偿缺口。

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [[2]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-2>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）。本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- APRILE E, et al. (XENON Collaboration). XENONnT WIMP search: Signal and background modeling and statistical inference[J]. Physical Review D, 2025, 111: 103040. DOI: [10.1103/PhysRevD.111.103040](https://doi.org/10.1103/PhysRevD.111.103040). 实际提取 [arXiv:2406.13638v1](https://arxiv.org/abs/2406.13638v1), 2024-06-19，第 6 页 Fig.3 右下图。期刊版为后续版本，不替换本次所用曲线。 [[7]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-7>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2406.13638v1.pdf>)
- XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`。Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本。SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。 [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)
- APRILE E, et al. (XENON Collaboration). First Search for Light Dark Matter in the Neutrino Fog with XENONnT[J]. Physical Review Letters, 2025, 134: 111802. DOI: [10.1103/PhysRevLett.134.111802](https://doi.org/10.1103/PhysRevLett.134.111802). 实际资料版本 [arXiv:2409.17868v1](https://arxiv.org/abs/2409.17868v1), 2024-09-26。文献 [1] 的背景关联来源 [72]。 [[12]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-12>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2409.17868v1.pdf>)
- APRILE E, et al. (XENON Collaboration). Probing the Solar ⁸B Neutrino Fog with XENONnT[J]. Physical Review Letters, 2026, 137: 091807. DOI: [10.1103/xvpn-w3q9](https://doi.org/10.1103/xvpn-w3q9). 本库保存 [arXiv:2604.06002v2](https://arxiv.org/abs/2604.06002v2), 2026-08-28。文献 [8] README 指定它为后续数据与模板的关联论文。本任务只提取 SR0/SR1 候选，不纳入 SR2。 [[14]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-14>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2604.06002v2.pdf>)
- XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)。本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1。官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)

[返回目录](#toc)

<a id="s6"></a>

## 6. Observable 与分箱

保留两个 run 的四维空间 `(cS2, shadow quantile, S1 BDT score, S2 BDT score)`，每维 3 箱、每 run 81 箱 [[3]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3) Fig.2 和 [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8) 的 `/bins/0…3`。新版已补齐所有四维事件与直方图，未只保留一维投影。

| run | cS2 edges（PE） | 三个 cS2 箱 D | 全部 D |
|---|---|---|---:|
| SR0 | `[90,170.161773681641,249.889739990234,500]` | `[5,3,1]` | 9 |
| SR1 | `[90,155.937850952148,232.292022705078,500]` | `[11,11,6]` | 28 |


| run | 观测轴 | 全部edges | 单位 | 直接出处 |
|---|---|---|---|---|
| SR0 | cS2 | [90.0, 170.16177368164062, 249.88973999023438, 500.0] | PE | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) binning/sr0.yaml及HDF5 /bins/0 |
| SR0 | shadow quantile | [0.0, 0.3333333333333333, 0.6666666666666666, 1.0] | 1 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) binning/sr0.yaml及HDF5 /bins/1 |
| SR0 | S1 BDT | [0.0, 0.28230122040303945, 0.4985350929997924, 1.0] | 1 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) binning/sr0.yaml及HDF5 /bins/2 |
| SR0 | S2 BDT | [0.8069558, 0.8833061584120925, 0.9237314564974191, 1.0] | 1 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) binning/sr0.yaml及HDF5 /bins/3 |
| SR1 | cS2 | [90.0, 155.93785095214844, 232.29202270507812, 500.0] | PE | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) binning/sr1.yaml及HDF5 /bins/0 |
| SR1 | shadow quantile | [0.0, 0.3333333333333333, 0.6666666666666666, 1.0] | 1 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) binning/sr1.yaml及HDF5 /bins/1 |
| SR1 | S1 BDT | [0.0, 0.27857412179472935, 0.4931583216785349, 1.0] | 1 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) binning/sr1.yaml及HDF5 /bins/2 |
| SR1 | S2 BDT | [0.7752842, 0.8595200471327761, 0.902943575516978, 1.0] | 1 | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) binning/sr1.yaml及HDF5 /bins/3 |

原文[3] PDF p3用S2描述(120,500)PE的ROI，p6 Fig.2用校正后的cS2作图。官方事件列为cS2，118.58632PE按原值保留。应依据校正定义核对选取坐标和作图坐标。benchmark式(14)的单一S2均值变量与官方cS2的对应继续待核。

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）。本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`。Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本。SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。 [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)

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
| run曝光 | 原文总量与质量/活时间已有，逐run为印刷中心值推导 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 相应原文段落 |
| 完整响应P | 早期官方基底与46×3名义核已有，重铸误差及原分析等价性待核。2026另存 | 第5节数据与状态传播到P07 |
| 积分网格及误差容限 | 待P07制定并验证 | 项目数值约定，DRAFT |

另存的 [早期官方真实反冲参考谱](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_early_release_cevns_spectrum.json>) 为501节点CDF，coordinate_system=0…1、map=0.45…10keV、总率335.5964691089417 events/(t·yr)，来自文献 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/cevns_spectrum.json及utils.py::Template.required_keys。仅用于与该发布原模板验证。不能替换本次Bahcall中微子能谱或把它当接受度。

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）。本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06。四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [[4]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4>) [本地实际核对材料](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)。本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1。官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)

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
| D | 下表给完整小型投影，原始事件/4D文件见第6节 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) Fig.2 |
| $\pi(\eta)$ | 已取得的率约束列下表，完整约束和模板依赖仍待核 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 原测量统计段落 |
| D=0箱 | D log(D/µ)取0的极限 | 泊松deviance的数学极限，项目推导 |

### 本次一维benchmark的归一化约束

| 分量 | 相对标准差 | 直接出处 |
|---|---|---|
| 信号FV | 0.05 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |
| AC | 0.048 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |
| Neutron | 0.5 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |
| ER | 1 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p6 Eq.(17)后 |

共同通量归一化误差为0.12，联合实验共用一次，直接依据为文献[1] PDF p6。下面的benchmark Fig.1分量按该再分析的参考状态保存。原生合作组likelihood的形状与校准约束作为另一项比较能力登记。Fig.2通量扫描时α与待测通量的参数化还需按原文构造核对。

### 原实验拟合投影

| 箱序号 | D | AC | Neutron | ER | 参考信号 | 直接出处 |
|---|---|---|---|---|---|---|
| 1 | 16 | 8.418287 | 0.070106 | 0.008422 | 3.135580 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p6 Fig.2 |
| 2 | 14 | 8.418376 | 0.118453 | 0.044527 | 4.969953 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p6 Fig.2 |
| 3 | 7 | 8.418376 | 0.262790 | 0.491975 | 2.606486 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p6 Fig.2 |

完整精度见 [xenonnt_original_fig2.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_original_fig2.txt>)，单位events/bin。背景和参考信号按原图拟合/参考状态保存，堆叠分量按多边形厚度提取。

### benchmark参考投影

| 箱序号 | D | AC | Neutron | ER | 参考信号 | 直接出处 |
|---|---|---|---|---|---|---|
| 1 | 16 | 8.433333 | 0.113027 | 0.067296 | 3.094290 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1右 |
| 2 | 14 | 8.433333 | 0.147510 | 0.120011 | 4.906605 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1右 |
| 3 | 7 | 8.433333 | 0.239464 | 0.512692 | 2.699105 | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) PDF p7 Fig.1右 |

完整精度见 [xenonnt_benchmark_fig1.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_benchmark_fig1.txt>)，单位events/bin。背景和参考信号按原图拟合/参考状态保存，堆叠分量按多边形厚度提取。

### 2024拟合前总数与约束原文值

| 输入 | 实际数值与误差 | 单位 | 直接出处 |
|---|---|---|---|
| AC_SR0_prefit | 7.5 ± 0.7 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 Table I expectation, AC(SR0) |
| AC_SR1_prefit | 17.8 ± 1 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 Table I expectation, AC(SR1) |
| ER_combined_prefit | 0.7 ± 0.7 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 Table I expectation, ER |
| neutron_combined_prefit | 0.5 −0.3/+0.2 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 Table I expectation, Neutron |
| total_background_prefit | 26.4 −1.3/+1.4 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 Table I expectation, Total background |
| signal_reference | 11.9 −4.2/+4.5 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 Table I expectation, 8B |
| AC_SR0_relative_rate_uncertainty | 0.09 | 1 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 AC model paragraph |
| AC_SR1_relative_rate_uncertainty | 0.058 | 1 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 AC model paragraph |
| neutron_relative_rate_uncertainty | 0.58 | 1 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 neutron paragraph |
| ER_relative_rate_uncertainty | 1 | 1 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 ER paragraph |
| signal_total_acceptance_relative_uncertainty | 0.1 | 1 | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) PDF p5 first column, S2 acceptance paragraph |
| neutron_SR0_prefit | 0.13 ± 0.07 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p5 neutron paragraph |
| neutron_SR1_prefit | 0.33 ± 0.19 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p5 neutron paragraph |
| ER_SR0_prefit | 0.13 ± 0.13 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p5 ER paragraph |
| ER_SR1_prefit | 0.56 ± 0.56 | events | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p5 ER paragraph |

完整精度和字段见 [xenonnt_prefit_inputs_2024.v2.1.json](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_prefit_inputs_2024.v2.1.json>)。

### 早期官方原始B及B8参考模板

| run | 组分 | cS2箱1率 | 箱2率 | 箱3率 | 具体来源 |
|---|---|---|---|---|---|
| SR0 | AC | 2.123493992 | 2.123570891 | 2.123570891 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/ac/，原数组名义tly=tqy=0 |
| SR0 | ER | 0.002472399992 | 0.01028979868 | 0.09439584039 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/er/，原数组名义tly=tqy=0 |
| SR0 | Neutron | 0.02363435233 | 0.03142987943 | 0.05800522503 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/rg/，原数组名义tly=tqy=0 |
| SR0 | B8信号参考 | 1.293757422 | 1.572084297 | 0.7495555867 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/b8/，原数组名义tly=tqy=0 |
| SR1 | AC | 2.528121712 | 2.528121712 | 2.528121712 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/ac/，原数组名义tly=tqy=0 |
| SR1 | ER | 0.00324310777 | 0.01854289048 | 0.2145480952 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/er/，原数组名义tly=tqy=0 |
| SR1 | Neutron | 0.01802698998 | 0.03566726171 | 0.08894539461 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/rg/，原数组名义tly=tqy=0 |
| SR1 | B8信号参考 | 0.8212316766 | 1.565380702 | 0.8876136646 | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/b8/，原数组名义tly=tqy=0 |

单位为events/(t·yr·bin)，未乘曝光。AC/ER为81箱数组，neutron/B8另有7×7形变网格。完整文件见 [SR0早期率模板](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_and_b8_early_release.npz>) · [SR1早期率模板](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_and_b8_early_release.npz>)。B8在本太阳中微子分析中是信号参考，不作为额外背景再加入。官方重铸reader的先验与原论文[1]统计设置分别登记，未直接导入其推断配置。

原始B模板边界与基底的边界各自保留。基底shadow边界的原文件小数截断造成最大3.34×10⁻⁹差异，不能声称二者逐字节相同。当前仅沿对应箱序号比较投影，严格逐事件边界归属仍须使用所属原文件。

发布reader的曝光因子1.174398/2.342593 t·yr见文献 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) statistical_model_base.yaml的livetime_sr0/1名义字段。与每t·yr模板相乘。计算得到AC(SR0/SR1)=7.48166191/17.76708067 events，B8总数=11.91609438 events，ER总数=0.67948078、neutron总数=0.46693518。这些项目推导量与文献[3] Table I打印的7.5/17.8、11.9、0.7、0.5在印刷精度内一致。它核验名义归一化与版本相容性，不替代原论文完整likelihood等价性证明。

### 已取得的2026背景数值

| run | Σ AC | Σ ER | Σ Neutron(tLy=tQy=0) | 原数组 |
|---|---|---|---|---|
| SR0 | 6.370635775 | 0.1070131463 | 0.1459054168 | [xenonnt_sr0_background_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_release2026_v2.npz>) |
| SR1 | 7.584365135 | 0.2342045985 | 0.1730147165 | [xenonnt_sr1_background_release2026_v2.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_release2026_v2.npz>) |

单位events/(t yr)，由原81箱rate求和。AC/ER为3⁴，Neutron为7×7×3⁴，直接来源为文献[8]各run的ac/er/rg HDF5及其单位说明。2024形状的版本对应待核。

原生四维likelihood在文献[3] PDF p6明确使用Gaussian pull，AC率按run独立、其他参数耦合，并用toy-MC构造临界值。该能力的tLy/tQy约束数值实现和2024模板形变仍待取得。

### 本章参考文献

- DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18。期刊版本不替代所用 v1。 [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）。本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- XU D (XENONnT). XENONnT/cevns_data_release: SR0+SR1+SR2[DS/OL]. Version sr0_sr1_sr2. Zenodo, 2026-06-07[2026-11-06]. DOI: [10.5281/zenodo.20576156](https://doi.org/10.5281/zenodo.20576156). 本次数值提取来自 [GitHub 固定提交](https://github.com/XENONnT/cevns_data_release/tree/60d230dd7a5646fd4aa2368c5fdfba575ee0cb88)，ZIP SHA256 `18c750ab841e99f072161c7fee42ae549451bca147c2bbb8ae2b1e880bbbce25`。Zenodo DOI 说明发布身份，本地 ZIP 并非该 DOI 附件的字节核验。模板属更新版本。SR0/SR1 事件的早期使用身份与模板校准版本分开。 固定提交指纹 `60d230dd7a5646fd4aa2368c5fdfba575ee0cb88`。 [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) [本地实际核对材料](<../../../../../../重构/20261106_8B_Qy_DB提取/official_release/cevns_data_release-master/README.md>)
- APRILE E, et al. (XENON Collaboration). First Search for Light Dark Matter in the Neutrino Fog with XENONnT[J]. Physical Review Letters, 2025, 134: 111802. DOI: [10.1103/PhysRevLett.134.111802](https://doi.org/10.1103/PhysRevLett.134.111802). 实际资料版本 [arXiv:2409.17868v1](https://arxiv.org/abs/2409.17868v1), 2024-09-26。文献 [1] 的背景关联来源 [72]。 [[12]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-12>) [本地实际核对材料](<../../../../references/Solar_CEvNS/2409.17868v1.pdf>)
- XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)。本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1。官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) [本地实际核对材料](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)

[返回目录](#toc)

<a id="s9"></a>

## 9. 数据清单与逐项出处

| 实际数值文件 | 完整覆盖范围 | 直接出处与定位 | 处理方法 |
|---|---|---|---|
| [XENONnT旧Qy曲线](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_23Vcm.txt>) | all rows; T_keVnr,Qy_e_per_keV,inside_visible_axes,source_line_dashed | [[7]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-7>) 2406.13638v1 PDF p6 Fig.3 bottom right; deep red SR0 23 V/cm | PDF vectors; clipped nodes and original extrapolation flags retained |
| [XENONnT旧Qy带](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_qy_sr0_band.txt>) | all rows; T_keVnr,Qy_lower,Qy_upper | [[7]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-7>) 2406.13638v1 PDF p6 Fig.3 bottom right; same figure; deep red model band | original band; no nuisance covariance inferred |
| [XENONnT原实验投影](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_original_fig2.txt>) | all 3 rows; bin,D,AC,neutron,ER,signal; events/bin | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p6 Fig.2 upper | fitted components; run bin edges are in the separate official bin table |
| [XENONnT benchmark投影](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_benchmark_fig1.txt>) | all 3 rows; bin,display_left_PE,display_right_PE,D,AC,neutron,ER,signal; events/bin | [[1]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-1>) 2411.11749v1 PDF p7 Fig.1 right | plot coordinates are not certified likelihood edges; reference B |
| [官方一维D](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_bins.txt>) | all 6 rows; run,bin,cS2_low_PE,cS2_high_PE,D | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) fixed commit data/sr0.csv,sr1.csv; binning/sr0.yaml,sr1.yaml | direct official histogram; no cuts |
| [官方事件cS2](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_events.txt>) | all 37 rows; run,CSV_zero_based_row,cS2_PE | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) fixed commit data/sr0.csv,sr1.csv | direct event values; original row order retained |
| [8B官网完整谱表](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/b8_bahcall1996_official.txt>) | all rows/keys; detailed key map below | [[4]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-4>) official b8spectrum.txt, all four columns | byte-identical download |
| [天然Xe九核素表](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/xenon_natural_isotopes_nist_v2.txt>) | all rows/keys; detailed key map below | [[9]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-9>) Xe rows 124,126,128,129,130,131,132,134,136 | parsed central values; uncertainties retained in official source download, not treated as zero |
| [SR0概率网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_release2026_v2.npz>) | all rows/keys; detailed key map below | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) templates/sr0/mono/*; /templates/template and /bins/* | lossless direct HDF5 array stacking; no interpolation or normalization |
| [SR0背景网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_release2026_v2.npz>) | all rows/keys; detailed key map below | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) templates/sr0/ac,er,rg/*; /templates/template | lossless HDF5 array stacking |
| [SR0四维D](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_observed_4d_v2.npz>) | all rows/keys; detailed key map below | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) data/sr0.csv; binning/sr0.yaml | histogramdd without cuts; exact event values |
| [SR1概率网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_release2026_v2.npz>) | all rows/keys; detailed key map below | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) templates/sr1/mono/*; /templates/template and /bins/* | lossless direct HDF5 array stacking; no interpolation or normalization |
| [SR1背景网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_release2026_v2.npz>) | all rows/keys; detailed key map below | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) templates/sr1/ac,er,rg/*; /templates/template | lossless HDF5 array stacking |
| [SR1四维D](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_observed_4d_v2.npz>) | all rows/keys; detailed key map below | [[8]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-8>) data/sr1.csv; binning/sr1.yaml | histogramdd without cuts; exact event values |
| [2024增益与曝光](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_calibration_inputs.v2.1.json>) | all records | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p2-p3, Dataset and gain/FV paragraphs | transcribed printed primary-source values |
| [2024 prefit与约束](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_prefit_inputs_2024.v2.1.json>) | all records | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p5 Table I and background text, p6 statistical inference | transcribed printed primary-source values |
| [2024三条接受度](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_2024_fig1_acceptance.txt>) | 40x8: T, three acceptance paths, energy/three curve visibility flags | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p4 Fig.1 upper: light-blue S1, dark-blue S2, black combined acceptance | Direct PDF vector digitization with tick-axis calibration; all original vertices and clipping flags retained; no interpolation or extrapolation |
| [2024真实反冲参考谱](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_2024_fig1_sm_recoil_spectra.txt>) | 40x6: T, two true-recoil reference spectra, energy/two curve visibility flags | [[3]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-3>) 2408.02877v1 PDF p4 Fig.1 lower: light-pink without acceptance and dark-red with acceptance SM curves | Direct PDF vector digitization with tick-axis calibration; all original vertices and clipping flags retained; no interpolation or extrapolation |
| [YBe LY lower](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_lower.json>) | 501 energy and 501 yield values; original JSON also retains coordinate_type/name | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/ly_ybe_model_lower.json; utils.py::load_default_yield_model; notebook 1 cells 9-13 | byte-identical copy from pinned official archive |
| [YBe LY median](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_median.json>) | 501 energy and 501 yield values; original JSON also retains coordinate_type/name | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/ly_ybe_model_median.json; utils.py::load_default_yield_model; notebook 1 cells 9-13 | byte-identical copy from pinned official archive |
| [YBe LY upper](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/ly_ybe_model_upper.json>) | 501 energy and 501 yield values; original JSON also retains coordinate_type/name | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/ly_ybe_model_upper.json; utils.py::load_default_yield_model; notebook 1 cells 9-13 | byte-identical copy from pinned official archive |
| [YBe QY lower](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_lower.json>) | 501 energy and 501 yield values; original JSON also retains coordinate_type/name | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/qy_ybe_model_lower.json; utils.py::load_default_yield_model; notebook 1 cells 9-13 | byte-identical copy from pinned official archive |
| [YBe QY median](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_median.json>) | 501 energy and 501 yield values; original JSON also retains coordinate_type/name | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/qy_ybe_model_median.json; utils.py::load_default_yield_model; notebook 1 cells 9-13 | byte-identical copy from pinned official archive |
| [YBe QY upper](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/ybe_early_release/qy_ybe_model_upper.json>) | 501 energy and 501 yield values; original JSON also retains coordinate_type/name | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/qy_ybe_model_upper.json; utils.py::load_default_yield_model; notebook 1 cells 9-13 | byte-identical copy from pinned official archive |
| [早期官方SM反冲源参考](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/reference/xenonnt_early_release_cevns_spectrum.json>) | all original JSON keys and arrays | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/signal/cevns_spectrum.json; utils.py::Template.required_keys and format_custom_signal_spectrum | byte-identical copy from pinned official archive |
| [SR0早期响应基底](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_basis.npz>) | 16x10x10x3x3x3x3 basis, 1600 source HDF5/run, all four bin-edge arrays | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/orthonormal_basis/SR0 selected by utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP and Template.interpolator | lossless stacking of author HDF5 /templates/template; original nonzero floor and normalization retained |
| [SR0早期名义三箱响应](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_early_release_nominal_1d.txt>) | 46x4: true energy and three accepted cS2-bin probabilities | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) utils.py::Template.interpolator/default_yield_model; original 1600 SR0 HDF5 plus ly/qy median JSON | Project derivation of author's linear recasting interpolator, marginalize three unused observables; local energy grid; no c_i or added efficiency |
| [SR0早期B与B8参考模板](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_and_b8_early_release.npz>) | AC/ER each 3x3x3x3; B8/neutron each 7x7x3x3x3x3; all bin edges retained | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/ac,er,b8,rg/template_XENONnT_sr0_*; statistical_model_base.yaml in_events_per_bin | lossless original HDF5 template stacking, no exposure applied or rescaling |
| [SR1早期响应基底](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_basis.npz>) | 16x10x10x3x3x3x3 basis, 1600 source HDF5/run, all four bin-edge arrays | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/orthonormal_basis/SR1 selected by utils.py::BASIS_E_R/LY_SWEEP/QY_SWEEP and Template.interpolator | lossless stacking of author HDF5 /templates/template; original nonzero floor and normalization retained |
| [SR1早期名义三箱响应](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_early_release_nominal_1d.txt>) | 46x4: true energy and three accepted cS2-bin probabilities | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) utils.py::Template.interpolator/default_yield_model; original 1600 SR1 HDF5 plus ly/qy median JSON | Project derivation of author's linear recasting interpolator, marginalize three unused observables; local energy grid; no c_i or added efficiency |
| [SR1早期B与B8参考模板](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_and_b8_early_release.npz>) | AC/ER each 3x3x3x3; B8/neutron each 7x7x3x3x3x3; all bin edges retained | [[17]](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md#ref-17>) data/ac,er,b8,rg/template_XENONnT_sr1_*; statistical_model_base.yaml in_events_per_bin | lossless original HDF5 template stacking, no exposure applied or rescaling |

字段、原始精度、指纹和output位置见 [P01逐项证据](<../../../../../../重构/20261106_Onboarding_provenance_revision/XENONnT_P01_EVIDENCE_LEDGER.yaml>)，配置逐字段引用P01，来源身份由P00统一维护。

[返回目录](#toc)

<a id="s10"></a>

## 10. 缺失、验证与参考文献

| 下一步能力 | 必需输入 | 实际状态 | 具体补充或核验 |
|---|---|---|---|
| Source/Target物理审阅 | 源谱、组成、核数、曝光 | 已有数值与原文，候选约定待审阅 | 按第2–3节逐项核对 |
| P06→P07一维重建谱 | 一维箱概率P_i(T)、曝光和观测窗口 | 早期官方重铸响应数值已有，精确原分析等价性/误差待核 | 核实一维响应或其生成配置 |
| P09一维benchmark统计 | D/B参考投影与Eq.(17)归一化误差 | 数值已有，前向P核及通量扫描参数化待核 | 沿用对应再分析的参考状态并核对统计构造 |
| 原生多维likelihood | 二维/四维形状、分箱、校准约束 | 附加能力，仍有独立缺口 | 仅在该能力被请求时补齐原生输入 |
| Fig.4物理比较 | 核原始系数、归一化和算符匹配 | 来源待核 | 共享模块专项核验 |

本版为数据审阅草稿，相关P03字段均保留DRAFT。记录与查找结果见 [P02待补输入](<../../../../../../重构/20261106_Onboarding_provenance_revision/P02_MISSING_AND_HANDOFF.md>) 和 [本轮补充与验收](<../../../../../../重构/20261106_Onboarding_provenance_revision/README.md>)。

[返回目录](#toc)
