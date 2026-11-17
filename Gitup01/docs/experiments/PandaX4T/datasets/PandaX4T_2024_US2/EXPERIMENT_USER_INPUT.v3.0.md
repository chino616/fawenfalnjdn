# PandaX4T_2024_US2 — onboarding v3.0 用户资料

2026-11-09，完整整合版本。[详细版：全部数值、公式、来源和交接](<experiment.physics.v3.0.md>) · [两实验完整总文档](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>)

<a id="toc"></a>

## 目录

- [范围与决定](#scope)
- [实际输入](#inputs)
- [结果与限制](#results)
- [下一步交接](#handoff)

<a id="scope"></a>

## 范围与决定

用户已指定：使用完整Response、严格逐数据出处、保留旧版；先SM，再按同论文做V与B−L轻媒介子事例数谱。质量/耦合测试点是项目明示选择，不冒充文献拟合。当前不是Fig.2或Fig.4统计复现。

PandaX原Response路线保留；2026-11-10用户新增简化方法，SM八箱已计算，完整Ne响应仍MISSING。

[返回目录](#toc)

<a id="inputs"></a>

## 实际输入

| 模块 | 已有数据/范围 | 直接来源与采用范围 |
|---|---|---|
| Source | Bahcall 829×4原表；中心谱积分0.999986544；Φ=5.46×10⁶cm⁻²s⁻¹ | R04官网原表列1/2；R01 PDF p5式(11)后；不重归一化 |
| Target | 天然Xe九核素；NIST数丰度和原子质量；参考吨核数 | R09全部九行；R13 SI常量；R18本地质量换算约定 |
| Response | 99点US2总接受度；Qy nominal/best-fit/带已取得；Ne箱概率MISSING | R02 PDF p3 Fig.1、p5 Fig.4；Qy不能替代涨落核 |
| Observable/曝光 | 简化Ne=4…8八箱已算；原0.3–3keVnr的27箱保留；1.04t·yr | R01 p5式(12)后；R02 PDF p3及Fig.5 |
| 共享理论 | SM/KN；轻矢量V、B−L | R01 PDF p3式(1)–(3)；R19 PDF p5式(2.6),(2.10)；无需本地多项式核响应 |

[正式YAML](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml>) · [完整NPZ](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz>) · [P00标准书目](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P00_SOURCE_REGISTER.yaml>)


### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本地直接采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). [本地直接采用源](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)

[返回目录](#toc)

<a id="results"></a>

## 结果与限制

| m=10MeV、g=2×10⁻⁵的项目测试点 | SM | V | B−L |
|---|---|---|---|
| 真实反冲投影[events] | 47.026752801 | 3.306022173 | 77.216760990 |

两实验各7点通过分维度收敛；2026-11-08相关27项测试通过。未运行χ²/90%CL。**这些数不是Ne∈[4,8]重建事件数。**

**2026-11-10新增、已实际计算：PandaX SM简化平均映射八箱谱。** 采用R01 PDF p5式(11)–(13)、p6式(15)，nominal Qy来自R02 PDF p5 Fig.4下图；Total(US2)已含ROI且只乘一次，忽略分辨率。直接积分（项目c_i=1基线）为**25.851676事例**，SSM通量固定为5.46×10⁶。R02 PDF p6 Fig.5后验拟合谱乘5.46/8.4的历史参考为**48.654331事例**；它仍带实验拟合响应参数，不是同一基准响应下独立校准的SM预测，不作为验证。

[结果、逐步物理及标准文献引用](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/REPORT.md>) · [真正计算的八箱表](<../../../../../outputs/solar_b8_sm/20261110_pandax_simplified_run1/events_by_bin.tsv>) · [来源/方法参数卡](<../../../../../data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json>)

[完整逐箱、干涉分解及测试限制](<experiment.physics.v3.0.md#prediction>)

[返回目录](#toc)

<a id="handoff"></a>

## 下一步交接

| 下一步能力 | 当前状态 | 具体需要什么/阻断范围 |
|---|---|---|
| 当前SM/V/B−L真实反冲投影 | 可运行；ROI选后总量估计及T分布；缺Ne箱分配 | 可见T域内无新增必需数据；域外贡献待核，保留1.04t·yr合计曝光 |
| PandaX SM简化Ne八箱谱 | SSM通量固定、c=1直接预测；后验拟合谱仅作参考 | 严格作者等价性仍需原c_i及全套拟合点；参考谱缩放不提供独立验证 |
| PandaX完整Response Ne谱 | **BLOCKED / MISSING** | 2024 US2的P(Ne箱\|T)，或能生成它的完整低能响应与选择配置；简化谱不解决该缺口 |
| PandaX逐run预测/原生2D likelihood | 部分输入已有，能力仍待补 | afterglow veto后逐run有效曝光；width完整边界、prefit背景形状及约束/相关性 |
| Fig.2/一维统计 | 未运行；不能把公式存在当拟合完成 | 明确采用分箱、flux nuisance参数化与数据/背景角色，再实现统计；联合通量约束仅一次 |
| Fig.4 V/B−L排除限 | 未请求/未运行；前向测试点已完成 | 具体χ²/CL构造、阈值与profile方案；无需S/A/T的自旋核输入 |
| S/A/T/Full EFT | 未实现本任务benchmark | 对应标量或自旋输入、匹配/归一化与外源核验；本地JSON存在不等于原文已核 |
| 味相关接触NSI | 不在当前模型范围 | 具体ε定义、flavor矩阵及太阳传播/味组成；不能沿用味普适代表态 |

[返回目录](#toc)
