# XENONnT_2024_SolarB8：onboarding v2.3（新版本，V/B−L benchmark草稿）

**2026-11-08, DRAFT/PARTIAL.** 固定点前向谱；数值质量/耦合为项目测试选择，不是论文拟合点或90% CL边界。

[共享模型与期刊原始公式](<../../../../../outputs/solar_b8_vector/20261108_run1/REPORT.md>) · [显式测试点卡](<../../../../../data/benchmarks/solar_b8_vector_v1/benchmark.input.json>) · [事例数图](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/events.png>) · [正式输入与逐项出处](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.physics.md>)

<a id="toc"></a>

旧版本保留：[v2.2 SM详细版](<experiment.physics.v2.2.md>) · [P00来源](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P00_SOURCE_REGISTER.yaml>) · [P01证据](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P01_EVIDENCE_LEDGER.yaml>)

## 目录

- [已有输入与来源](#inputs)
- [结果](#results)
- [验证与缺口](#checks)

<a id="inputs"></a>

## 已有输入与来源

| 模块 | 实际数值/数组 | 本地数值与直接出处 |
|---|---|---|
| Source | Φ=5.46e6 cm⁻²s⁻¹；829点f(E)，0–16.56 MeV；积分0.999986544 | [source_energy_MeV/source_shape_per_MeV](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>)；R04官网b8spectrum.txt第一/二列；R01 PDF p5式(11)后给总通量，不重新归一化 |
| Target | 天然Xe九核素A=124,126,128,129,130,131,132,134,136；1t核数为代数锚点，非实测质量 | [target_mass_number/target_atomic_mass_u/target_number_fraction](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>)；R09 NIST Xe全部九行。原子质量用于核数，动力学扣54电子质量，见正式参数卡 |
| SM与新模型 | sin²θW=0.23857；KN R=1.23 A^(1/3)fm、a=0.7fm；V κ=1，B−L κ=−1/3 | R01 PDF p3式(1)–(3)；R19正式期刊版PDF p5/印刷p4式(2.6),(2.10)。C_V=3Ag²；旧v1记号冲突没有静默混用 |
| Response | 每run [16,10,10,3]概率基底，Ly/Qy中位数各501点；支撑0.51–5keVnr | [完整响应/产额数组](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>)；R17 orthonormal_basis/原HDF5对shadow/S1BDT/S2BDT求和；YBe median JSON；已有选取只施加一次 |
| 曝光/Observable | SR0=1.174398、SR1=2.342593 t·yr；各自三箱按序号求和 | R17 statistical_model_base.yaml livetime_sr0/1与原HDF5 /bins/0；合计3.516991，未改为论文打印3.51 |
| 新参数 | m=1/10/100MeV；g=1/2/3×10⁻⁵（各点组合见下表） | 数值为PROJECT_BENCHMARK_CHOICE，直接采用源为显式测试点卡；R19只提供模型定义与κ，不提供这些测试点的实验依据 |

### 本节参考文献

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。

- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: 10.1088/1475-7516/2025/05/012. [期刊原件](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)；PDF p5，印刷p4。

SR0原生cS2边界：[90.0, 170.161773681641, 249.889739990234, 500.0] PE；SR1：[90.0, 155.937850952148, 232.292022705078, 500.0] PE。两个run的箱边界不同，合计图只相加同序号箱。

绘图观测与背景直接文件：

| 文件 | 来源与处理 |
|---|---|
| [xenonnt_official_observed_bins.txt](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_bins.txt>) | R08 fixed author event CSV and native binning; XENONnT-C016; observed counts, not digitized best fit |
| [xenonnt_sr0_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_and_b8_early_release.npz>) | R17 original ac/er/rg HDF5 templates and statistical_model_base.yaml; XENONnT-C042/C045; B8 signal excluded from B |
| [xenonnt_sr1_background_and_b8_early_release.npz](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_and_b8_early_release.npz>) | R17 original ac/er/rg HDF5 templates and statistical_model_base.yaml; XENONnT-C042/C045; B8 signal excluded from B |

D合计37；名义AC/ER/neutron背景合计26.395158547事例。均只用于作图，无背景profiling；误差棒为项目计算的68.268949% Garwood Poisson区间。

[返回目录](#toc)

<a id="results"></a>

## 结果

| 点 | m [MeV] | g | κ | 箱1 | 箱2 | 箱3 | 总信号/投影 [events] | 相对SM总量 |
|---|---|---|---|---|---|---|---|---|
| SM | — | 0.0 | — | 3.514030918 | 5.649108573 | 3.154093732 | 12.317233224 | 1.000000000 |
| V10_g1 | 10.0 | 1e-05 | 1.0 | 2.436180037 | 4.084558483 | 2.405778680 | 8.926517199 | 0.724717722 |
| V10_g2 | 10.0 | 2e-05 | 1.0 | 0.463013854 | 1.009259782 | 0.802118992 | 2.274392628 | 0.184651259 |
| V10_g3 | 10.0 | 3e-05 | 1.0 | 1.375691753 | 1.278267183 | 0.266971082 | 2.920930019 | 0.237141732 |
| BL10_g2 | 10.0 | 2e-05 | -0.3333333333333333 | 5.277932287 | 8.154747990 | 4.318106332 | 17.750786609 | 1.441134246 |
| V1_g2 | 1.0 | 2e-05 | 1.0 | 0.347819902 | 0.596343248 | 0.510307035 | 1.454470186 | 0.118084164 |
| V100_g2 | 100.0 | 2e-05 | 1.0 | 3.342058655 | 5.373834989 | 3.001488381 | 11.717382025 | 0.951299842 |

带符号分解：

| 点 | SM总量 | 干涉项 | 纯NP项 | 总量 | 闭合最大误差 [events] |
|---|---|---|---|---|---|
| V10_g1 | 12.317233224 | -3.684051316 | 0.293335292 | 8.926517199 | 3.55e-15 |
| V10_g2 | 12.317233224 | -14.736205266 | 4.693364670 | 2.274392628 | 1.72e-15 |
| V10_g3 | 12.317233224 | -33.156461848 | 23.760158644 | 2.920930019 | 8.88e-15 |
| BL10_g2 | 12.317233224 | 4.912068422 | 0.521484963 | 17.750786609 | 5.33e-15 |
| V1_g2 | 12.317233224 | -19.713278715 | 8.850515677 | 1.454470186 | 4.22e-15 |
| V100_g2 | 12.317233224 | -0.607339908 | 0.007488709 | 11.717382025 | 4.44e-15 |

[查看图](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/events.png>) · [全部逐箱TSV](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/counts_by_point.tsv>)

- [SM：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/SM/RESULT.json>)
- [V10_g1：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/V10_g1/RESULT.json>)
- [V10_g2：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/V10_g2/RESULT.json>)
- [V10_g3：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/V10_g3/RESULT.json>)
- [BL10_g2：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/BL10_g2/RESULT.json>)
- [V1_g2：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/V1_g2/RESULT.json>)
- [V100_g2：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/XENONnT_2024_SolarB8/V100_g2/RESULT.json>)

[返回目录](#toc)

<a id="checks"></a>

## 验证与缺口

| 点 | 最大T加密差异 | 最大Eν加密差异 | 数值验收 |
|---|---|---|---|
| SM | 0.0015079% | 0.00260442% | PASS |
| V10_g1 | 0.00144467% | 0.0027149% | PASS |
| V10_g2 | 0.00111276% | 0.00336687% | PASS |
| V10_g3 | 0.00293125% | 0.00141567% | PASS |
| BL10_g2 | 0.00157237% | 0.00249524% | PASS |
| V1_g2 | 0.000900519% | 0.0039116% | PASS |
| V100_g2 | 0.0015074% | 0.00260554% | PASS |

预定条件逐箱max(2×10⁻⁴ events, 0.2%)；T和Eν分别加密，另含正式源/响应/产额断点。SM与上一轮保存的SM输出逐箱核对。新相互作用通过组件描述与源文件哈希形成独立physics fingerprint；旧输入包及SM数值不改写。

XENONnT已完成本组参数点的重建谱计算。响应仍为官方早期重铸版本，其与原2024分析的精确等价性未认证；本轮无实验提供的非零新物理信号模板，所以解析极限/分解闭合不等于外部论文曲线复现。

下一步能力交接：传统接触ε或味非普适NSI需要独立的耦合定义与太阳入射态；S/A/T需要相应标量输入或自旋结构函数核验。本轮没有生成它们，也未计算Fig.4的χ²/90% CL边界。

[返回目录](#toc)
