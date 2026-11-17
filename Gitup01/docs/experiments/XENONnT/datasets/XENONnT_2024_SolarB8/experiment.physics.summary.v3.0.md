# XENONnT_2024_SolarB8 — onboarding v3.0 精简阅读版

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

XENONnT采用R17早期官方YBe响应；原2024严格等价性限制保留。

[返回目录](#toc)

<a id="inputs"></a>

## 实际输入

| 模块 | 已有数据/范围 | 直接来源与采用范围 |
|---|---|---|
| Source | Bahcall 829×4原表；中心谱积分0.999986544；Φ=5.46×10⁶cm⁻²s⁻¹ | R04官网原表列1/2；R01 PDF p5式(11)后；不重归一化 |
| Target | 天然Xe九核素；NIST数丰度和原子质量；参考吨核数 | R09全部九行；R13 SI常量；R18本地质量换算约定 |
| Response | 每run16×10×10×3接受后概率；YBe Ly/Qy各501点；T支撑0.51–5keVnr | R17 HDF5/median JSON |
| Observable/曝光 | 两run各自3箱；1.174398/2.342593t·yr；按箱序号合计 | R17原bins/livetime；R08官方D |
| 共享理论 | SM/KN；轻矢量V、B−L | R01 PDF p3式(1)–(3)；R19 PDF p5式(2.6),(2.10)；无需本地多项式核响应 |

[正式YAML](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml>) · [完整NPZ](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz>) · [P00标准书目](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P00_SOURCE_REGISTER.yaml>)


### 本章参考文献与核验范围

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本地直接采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本地直接采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本地直接采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)
- [R19] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). [本地直接采用源](<../../../../references/Solar_CEvNS/JCAP_2025_05_012_published.pdf>)

[返回目录](#toc)

<a id="results"></a>

## 结果与限制

| m=10MeV、g=2×10⁻⁵的项目测试点 | SM | V | B−L |
|---|---|---|---|
| 信号总数[events] | 12.317233224 | 2.274392628 | 17.750786609 |

两实验各7点通过分维度收敛；2026-11-08相关27项测试通过。未运行χ²/90%CL。使用公开早期重铸Response，不宣称精确2024官方分析认证。

[完整逐箱、干涉分解及测试限制](<experiment.physics.v3.0.md#prediction>)

[返回目录](#toc)

<a id="handoff"></a>

## 下一步交接

| 下一步能力 | 当前状态 | 具体需要什么/阻断范围 |
|---|---|---|
| 当前SM/V/B−L重建谱 | 可运行；早期R17重铸模型范围内已算 | 严格2024复现仍需模型版本等价性/重铸误差核验 |
| XENONnT精确原生4D likelihood | 未实现/未认证 | 2024配套81箱模板及tLy/tQy数值约束/相关性；R17已有模板与R08后续候选分开 |
| Fig.2/一维统计 | 未运行；不能把公式存在当拟合完成 | 明确采用分箱、flux nuisance参数化与数据/背景角色，再实现统计；联合通量约束仅一次 |
| Fig.4 V/B−L排除限 | 未请求/未运行；前向测试点已完成 | 具体χ²/CL构造、阈值与profile方案；无需S/A/T的自旋核输入 |
| S/A/T/Full EFT | 未实现本任务benchmark | 对应标量或自旋输入、匹配/归一化与外源核验；本地JSON存在不等于原文已核 |
| 味相关接触NSI | 不在当前模型范围 | 具体ε定义、flavor矩阵及太阳传播/味组成；不能沿用味普适代表态 |

[返回目录](#toc)
