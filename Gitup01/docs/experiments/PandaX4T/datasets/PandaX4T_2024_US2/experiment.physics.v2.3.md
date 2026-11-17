# PandaX4T_2024_US2：onboarding v2.3（新版本，V/B−L benchmark草稿）

**2026-11-08, DRAFT/PARTIAL.** 固定点前向谱；数值质量/耦合为项目测试选择，不是论文拟合点或90% CL边界。

[共享模型与期刊原始公式](<../../../../../outputs/solar_b8_vector/20261108_run1/REPORT.md>) · [显式测试点卡](<../../../../../data/benchmarks/solar_b8_vector_v1/benchmark.input.json>) · [事例数图](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/events.png>) · [正式输入与逐项出处](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.physics.md>)

<a id="toc"></a>

旧版本保留：[v2.2 SM详细版](<experiment.physics.v2.2.md>) · [P00来源](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P00_SOURCE_REGISTER.yaml>) · [P01证据](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P01_EVIDENCE_LEDGER.yaml>)

## 目录

- [已有输入与来源](#inputs)
- [结果](#results)
- [验证与缺口](#checks)

<a id="inputs"></a>

## 已有输入与来源

| 模块 | 实际数值/数组 | 本地数值与直接出处 |
|---|---|---|
| Source | Φ=5.46e6 cm⁻²s⁻¹；829点f(E)，0–16.56 MeV；积分0.999986544 | [source_energy_MeV/source_shape_per_MeV](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>)；R04官网b8spectrum.txt第一/二列；R01 PDF p5式(11)后给总通量，不重新归一化 |
| Target | 天然Xe九核素A=124,126,128,129,130,131,132,134,136；1t核数为代数锚点，非实测质量 | [target_mass_number/target_atomic_mass_u/target_number_fraction](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>)；R09 NIST Xe全部九行。原子质量用于核数，动力学扣54电子质量，见正式参数卡 |
| SM与新模型 | sin²θW=0.23857；KN R=1.23 A^(1/3)fm、a=0.7fm；V κ=1，B−L κ=−1/3 | R01 PDF p3式(1)–(3)；R19正式期刊版PDF p5/印刷p4式(2.6),(2.10)。C_V=3Ag²；旧v1记号冲突没有静默混用 |
| 接受度投影 | 99节点Total(US2)接受度；27个真实反冲箱，非Ne箱 | [efficiency_energy_keV/efficiency](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>)；R02 2407.10892v3 PDF p3 Fig.1黑色Total(US2)99节点；P(Ne-bin\|T)仍为MISSING |
| 曝光/Observable | 1.04t·yr；0.3–3keVnr区间的27个投影箱 | R02 PDF p3 US2总曝光；本轮箱边界沿用正式包的项目输出坐标，不称为原始Ne边界 |
| 新参数 | m=1/10/100MeV；g=1/2/3×10⁻⁵（各点组合见下表） | 数值为PROJECT_BENCHMARK_CHOICE，直接采用源为显式测试点卡；R19只提供模型定义与κ，不提供这些测试点的实验依据 |

### 本节参考文献

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。

- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: 10.1088/1475-7516/2025/05/012. [期刊原件](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)；PDF p5，印刷p4。

[返回目录](#toc)

<a id="results"></a>

## 结果

| 点 | m [MeV] | g | κ | 总信号/投影 [events] | 相对SM总量 |
|---|---|---|---|---|---|
| SM | — | 0.0 | — | 47.026752801 | 1.000000000 |
| V10_g1 | 10.0 | 1e-05 | 1.0 | 29.508388184 | 0.627480879 |
| V10_g2 | 10.0 | 2e-05 | 1.0 | 3.306022173 | 0.070300881 |
| V10_g3 | 10.0 | 3e-05 | 1.0 | 47.477838291 | 1.009592104 |
| BL10_g2 | 10.0 | 2e-05 | -0.3333333333333333 | 77.216760990 | 1.641975182 |
| V1_g2 | 1.0 | 2e-05 | 1.0 | 16.804273790 | 0.357334342 |
| V100_g2 | 100.0 | 2e-05 | 1.0 | 44.708924779 | 0.950712565 |

**全部数字均为真实反冲接受度加权投影，不是Ne∈[4,8]的重建事件数，不能与论文Ne拟合总数取复现比。**

带符号分解：

| 点 | SM总量 | 干涉项 | 纯NP项 | 总量 | 闭合最大误差 [events] |
|---|---|---|---|---|---|
| V10_g1 | 47.026752801 | -19.714425270 | 2.196060653 | 29.508388184 | 1.33e-15 |
| V10_g2 | 47.026752801 | -78.857701082 | 35.136970454 | 3.306022173 | 1.3e-15 |
| V10_g3 | 47.026752801 | -177.429827434 | 177.880912924 | 47.477838291 | 1.78e-15 |
| BL10_g2 | 47.026752801 | 26.285900361 | 3.904107828 | 77.216760990 | 1.78e-15 |
| V1_g2 | 47.026752801 | -122.632538799 | 92.410059789 | 16.804273790 | 4.88e-15 |
| V100_g2 | 47.026752801 | -2.347120962 | 0.029292941 | 44.708924779 | 8.88e-16 |

[查看图](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/events.png>) · [全部逐箱TSV](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/counts_by_point.tsv>)

- [SM：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/SM/RESULT.json>)
- [V10_g1：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/V10_g1/RESULT.json>)
- [V10_g2：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/V10_g2/RESULT.json>)
- [V10_g3：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/V10_g3/RESULT.json>)
- [BL10_g2：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/BL10_g2/RESULT.json>)
- [V1_g2：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/V1_g2/RESULT.json>)
- [V100_g2：数组、run/核素分量、参数与收敛](<../../../../../outputs/solar_b8_vector/20261108_run1/PandaX4T_2024_US2/V100_g2/RESULT.json>)

[返回目录](#toc)

<a id="checks"></a>

## 验证与缺口

| 点 | 最大T加密差异 | 最大Eν加密差异 | 数值验收 |
|---|---|---|---|
| SM | 0.0192102% | 0.0161712% | PASS |
| V10_g1 | 0.0189741% | 0.0161719% | PASS |
| V10_g2 | 0.248543% | 0.0161746% | PASS |
| V10_g3 | 0.122093% | 0.016182% | PASS |
| BL10_g2 | 0.0194737% | 0.0161705% | PASS |
| V1_g2 | 0.269182% | 0.0161759% | PASS |
| V100_g2 | 0.0192061% | 0.0161713% | PASS |

预定条件逐箱max(2×10⁻⁴ events, 0.2%)；T和Eν分别加密，另含正式源/响应/产额断点。SM与上一轮保存的SM输出逐箱核对。新相互作用通过组件描述与源文件哈希形成独立physics fingerprint；旧输入包及SM数值不改写。

PandaX仍缺US2的P(Ne-bin|T)，只阻断Ne重建谱和依赖它的拟合。没有从平均Qy猜出Poisson/Gaussian宽度，也不加c_i。

下一步能力交接：传统接触ε或味非普适NSI需要独立的耦合定义与太阳入射态；S/A/T需要相应标量输入或自旋结构函数核验。本轮没有生成它们，也未计算Fig.4的χ²/90% CL边界。

[返回目录](#toc)
