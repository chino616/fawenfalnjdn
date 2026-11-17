# PandaX-4T 2024 US2 — onboarding v2.2（新版本，SM主线计算草稿）

**2026-11-07，DRAFT/PARTIAL。** 本版补充正式输入包、Runtime执行、逐箱结果、收敛及外部参考差异；旧版原位保留。

[旧v2.1详细版](<experiment.physics.v2.1.md>) · [同源正式包完整数值和来源](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.physics.md>) · [P00来源](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P00_SOURCE_REGISTER.yaml>) · [P01证据](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P01_EVIDENCE_LEDGER.yaml>) · [P03配置](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/P03_PHYSICS_CONTRACT.yaml>) · [本轮SM报告](<../../../../../workflows/cevns-pyeft/runs/PandaX4T/PandaX4T_2024_US2/SM_BENCHMARK_REPORT.md>) · [事件数图](<../../../../../outputs/solar_b8_sm/20261107_run1/PandaX4T_2024_US2/events.png>)

<a id="toc"></a>

## 目录

- [模型与来源](#model)
- [实际数值](#numbers)
- [验证与限制](#validation)
- [复算入口](#reproduce)

<a id="model"></a>

## 模型与来源

| 输入/选择 | 本轮实际采用 | 直接出处与核验范围 |
|---|---|---|
| SM截面/核形状 | 树级SM含−T/E；Klein–Nystrand，R=1.23 A^(1/3)fm、a=0.7fm | [R01] PDF p3式(1)–(3)，解析共享模块；不借用Fig.4的EFT系数 |
| 弱混合角 | sin²θW=0.23857 | [R01] PDF p3式(2)后 |
| 源谱/总通量 | Bahcall中心829点；Φ=5.46×10⁶ cm⁻²s⁻¹ | [R04] 官网原表前两列；[R01] PDF p5式(11)后；不重复效率 |
| 靶 | 天然Xe九核素，NIST数丰度 | [R09] 原子质量给核数；动力学近似扣除54电子质量，忽略电子结合能 |
| Response/投影 | 原图99节点接受度×真实反冲率；Ne响应仍缺 | [R02] PDF p3 Fig.1黑色Total(US2) |
| 曝光 | US2合计1.04 t·yr | [R02] PDF p3 |
| 常量/单位 | 正式参数卡固定项目G_F、amu、m_e、hbarc与截面换算 | [R18] 本地采用的foundation/constants.py；31557600s/yr只出现一次 |
| 绘图观测误差 | 68.268949% Garwood Poisson区间，图示用 | 本轮项目推导：χ²分布分位点，不冒充论文原始误差或完整统计模型 |

### Source、Target与折叠定义

源的总量和能量形状分别施加：

$$
\frac{d\phi}{dE_\nu}=\Phi_{8B} f_{8B}(E_\nu).
$$

Phi的单位cm⁻²s⁻¹，f的单位MeV⁻¹，Eν用MeV。直接依据[R01] PDF p5式(11)及后文与[R04]官网谱表；不是把已含接受度的反冲谱当作中微子通量。

核数由天然数丰度构建：

$$
\overline m_{\rm atom}=\sum_A f_A m_{{\rm atom},A},\qquad n_A=\frac{M_{\rm anchor}f_A}{\overline m_{\rm atom}}.
$$

这里f_A是[R09]的数丰度，m_atom由NIST的u数值乘10⁻³kg/mol再除以[R13]的N_A，采用常用摩尔质量常量1g/mol近似；M_anchor=1000kg是项目归一化锚点。核数单位nuclei，n_A^(t)表示每吨核数。kg原子质量用于物质数，扣除电子后的GeV质量用于运动学，两者分别登记。

本轮只计算真实能量箱上的接受度加权诊断：

$$
N_j^{\rm recoil}=\mathcal E\,t_{\rm yr}\sum_A n_A^{(t)}\int_{T_j}^{T_{j+1}}dT\int dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT}\epsilon_{\rm US2}(T).
$$

epsilon来自[R02] Fig.1黑线。真实能量T的单位keVnr；缺失的是Ne箱的P_i(T)，本式不能作为Ne预测。

E_r/曝光单位t·yr，t_yr=31557600s/yr，n_A^(t)单位nuclei/t，截面输出cm²/keVnr，积分后的mu/N为events/bin。代码先算参考年注量与参考吨核数，再乘exposure/anchor_tonne，与上式等价；曝光、核数及接受率各一次。上述实验侧折叠关系为项目推导，代码owner为solar_b8.SolarExecutor与共享recoil/folding，不含c_i；共享SM/KN内部截面公式只登记模块和[R01]定位。

### 本章参考文献

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本次数值的直接原件/本地采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [本次数值的直接原件/本地采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本次数值的直接原件/本地采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R13] BUREAU INTERNATIONAL DES POIDS ET MESURES. The International System of Units (SI)[S/OL]. 9th ed., V4.01 (June 2026). Sèvres: BIPM, 2026[2026-11-06]. DOI: [10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291). [官方入口](https://www.bipm.org/en/publications/si-brochure). §2.2/Table 1，印刷页 123–124（英文 PDF 第 13–14 页）给出阿伏伽德罗常量的精确值；§2.3.1 印刷页 130 给出摩尔质量常量关系。
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本次数值的直接原件/本地采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本次数值的直接原件/本地采用源](<../../../../../cevns_pyeft/foundation/constants.py>)

[返回目录](#toc)

<a id="numbers"></a>

## 实际数值

真实反冲可见区间的接受度加权SM投影合计 **47.026752801** events；27箱完整数组见结果文件。该数不是Ne∈[4,8]的预测，不能与论文拟合信号75.147431直接取复现比。

图左为本轮计算的真实能量谱；图右为文献[R01] Fig.1数字化的观测、背景及拟合/参考信号，明确标为reference only。US2逐箱响应缺失，所以没有本轮计算的Ne信号直方图。

### 本章参考文献

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本次数值的直接原件/本地采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R02] BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). 实际使用 [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3), 2024-09-13。 [本次数值的直接原件/本地采用源](<../../../../references/Solar_CEvNS/2407.10892v3.pdf>)

[返回目录](#toc)

<a id="validation"></a>

## 验证与限制

| 加密维度 | 最大逐箱相对差异 | 最大绝对差异(events) | 预定数值条件 |
|---|---|---|---|
| recoil | 0.0192102% | 0.000176217 | PASS：max(2e-4 events, 0.2%) |
| neutrino_energy | 0.0161712% | 3.51052e-05 | PASS：max(2e-4 events, 0.2%) |

运行网格（基础T节点/Eν节点）与总数：

| 步骤 | T基础节点 | Eν基础节点 | 总事件数 |
|---|---|---|---|
| base | 201 | 120 | 47.024977515 |
| recoil_refined | 401 | 120 | 47.0260347567 |
| recoil_fine | 801 | 120 | 47.0264243837 |
| energy_refined | 801 | 480 | 47.0267528009 |

Eν另并入829点源表断点，T另并入响应、产额和输出箱断点。保存各run/九核素分量，检查非负、组分和、通量线性、弹性端点和截面单位。SM点数值收敛不等于论文曲线/官方likelihood复现；本轮没有拟合、置信区间或BSM扫描。

本轮测试实际为95项通过、4项失败；新增solar合同7项通过，所选旧实验数值Slow/Fast/分量回归通过。4项失败为两个旧Physics MD同步检查与两个旧资源清单哈希检查。旧输入、数组、MD和资源清单与此前快照逐字节一致；移除新增solar绑定仍能复现旧MD差异，因此不改旧参考或容差来掩盖。[实际测试记录](<../../../../../outputs/solar_b8_sm/20261107_run1/TEST_RESULTS.json>) · [旧MD独立对照](<../../../../../outputs/solar_b8_sm/20261107_run1/LEGACY_MD_BASELINE_CHECK.json>) · [旧文件指纹](<../../../../../outputs/solar_b8_sm/20261107_run1/LEGACY_INPUT_PRESERVATION.json>)。

PandaX缺少固定真实反冲到Ne箱的通过概率；没有用Qy均值、任意Poisson/Gaussian宽度或c_i代替它。仅该重建谱能力受阻。

[返回目录](#toc)

<a id="reproduce"></a>

## 复算入口

从原Gitup01根目录运行：

```powershell
python -B tools/run_solar_b8_sm_benchmark.py --output outputs/solar_b8_sm/repeat_run
```

直接标准Runtime入口：

```python
from cevns_pyeft.experiments.package_loader import load_experiment_package
from cevns_pyeft.experiments.runtime import predict_experiment
experiment = load_experiment_package("data/experiments/PandaX4T/PandaX4T_2024_US2")
prediction = predict_experiment(experiment, numerics={"n_er": 801, "n_enu": 480})
print(prediction.counts)
```

主项目代码、正式包、阶段记录和结果均已落盘。通过显式输入包加载时使用项目现有scoped Catalog；没有把PARTIAL结果无条件加入默认活动实验清单。旧onboarding保持原位。

[返回目录](#toc)
