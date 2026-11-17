# XENONnT 2024 — onboarding v2.2（新版本，SM主线计算草稿）

**2026-11-07，DRAFT/PARTIAL。** 本版补充正式输入包、Runtime执行、逐箱结果、收敛及外部参考差异；旧版原位保留。

[旧v2.1详细版](<experiment.physics.v2.1.md>) · [同源正式包完整数值和来源](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.physics.md>) · [P00来源](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P00_SOURCE_REGISTER.yaml>) · [P01证据](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P01_EVIDENCE_LEDGER.yaml>) · [P03配置](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/P03_PHYSICS_CONTRACT.yaml>) · [本轮SM报告](<../../../../../workflows/cevns-pyeft/runs/XENONnT/XENONnT_2024_SolarB8/SM_BENCHMARK_REPORT.md>) · [事件数图](<../../../../../outputs/solar_b8_sm/20261107_run1/XENONnT_2024_SolarB8/events.png>)

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
| Response/投影 | 早期官方YBe基底，按(E,Ly,Qy)线性插值、其余观测轴求和 | [R17] orthonormal_basis/、signal/*median.json、utils.py::Template.interpolator |
| 曝光 | SR0=1.174398、SR1=2.342593 t·yr | [R17] statistical_model_base.yaml livetime_sr0/1；合计3.516991，与论文打印3.51分别报告 |
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

响应为原接受后四维概率的边际化：

$$
P_{ri}(T)=\sum_{j,k,l}p_r(i,j,k,l\mid T,L_y(T),Q_y(T)),\qquad 0\leq\sum_iP_{ri}(T)\leq1.
$$

p_r是[R17]每个单能HDF5的接受后箱概率；(E,Ly,Qy)取值按官方utils.py的三线性内插，Ly/Qy取原median表。它已经包含选取，不是需要再乘总效率的归一化条件密度。每run/每同位素的信号为本项目对[R01]式(11)–(12)采用完整Response后的推导：

$$
\mu_{ri}^{\rm SM}=\mathcal E_r t_{\rm yr}\sum_A n_A^{(t)}\int dT\,dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT}P_{ri}(T).
$$

E_r/曝光单位t·yr，t_yr=31557600s/yr，n_A^(t)单位nuclei/t，截面输出cm²/keVnr，积分后的mu/N为events/bin。代码先算参考年注量与参考吨核数，再乘exposure/anchor_tonne，与上式等价；曝光、核数及接受率各一次。上述实验侧折叠关系为项目推导，代码owner为solar_b8.SolarExecutor与共享recoil/folding，不含c_i；共享SM/KN内部截面公式只登记模块和[R01]定位。

### 本章参考文献

- [R01] DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). 本任务实际使用 [arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1), 2024-11-18；期刊版本不替代所用 v1。 [本次数值的直接原件/本地采用源](<../../../../references/Solar_CEvNS/2411.11749v1.pdf>)
- [R04] BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [arXiv:nucl-th/9601044v2](https://arxiv.org/abs/nucl-th/9601044v2). 数值来源：[Bahcall 官方 b8spectrum.txt](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，访问日期 2026-11-06；四列完整原件，SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`。 [本次数值的直接原件/本地采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/Bahcall-b8spectrum.txt>)
- [R09] NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL].[2026-11-06]. [NIST Xe 表](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe&ascii=ascii2&isotype=all). 下载 HTML SHA256 `873d7f0675cc47bf2cb1304b25aa62f4d7182594f7421a99210bb594e57b91a3`。提取天然同位素数丰度和原子质量中心值；未称为实验氙同位素实测报告，也未称为裸核质量。 [本次数值的直接原件/本地采用源](<../../../../../../重构/20261106_Response_onboarding_v2/source_downloads/NIST-Xe.html>)
- [R13] BUREAU INTERNATIONAL DES POIDS ET MESURES. The International System of Units (SI)[S/OL]. 9th ed., V4.01 (June 2026). Sèvres: BIPM, 2026[2026-11-06]. DOI: [10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291). [官方入口](https://www.bipm.org/en/publications/si-brochure). §2.2/Table 1，印刷页 123–124（英文 PDF 第 13–14 页）给出阿伏伽德罗常量的精确值；§2.3.1 印刷页 130 给出摩尔质量常量关系。
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本次数值的直接原件/本地采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)
- [R18] CEvNS-pyEFT Project. foundation/constants.py[CP/OL]. 本地项目工作副本[2026-11-07]. 采用现有常量约定，不把本地复用当作独立上游文献核验。 [本次数值的直接原件/本地采用源](<../../../../../cevns_pyeft/foundation/constants.py>)

[返回目录](#toc)

<a id="numbers"></a>

## 实际数值

| 箱序号 | 本轮SM信号 | 原发布名义信号 | 背景 | SM+背景 | 观测D |
|---|---|---|---|---|---|
| 1 | 3.514030918 | 3.443197706 | 8.496674222 | 12.010705140 | 16 |
| 2 | 5.649108573 | 5.513302530 | 8.592265462 | 14.241374035 | 14 |
| 3 | 3.154093732 | 2.959594139 | 9.306218864 | 12.460312596 | 7 |

合计SM信号 **12.317233224**，背景 **26.395158547**，总期望 **38.712391771**，D=37。单位events/bin。

三箱是各run自身的cS2箱按序号求和；SR0边界[90,170.161773681641,249.889739990234,500]PE，SR1边界[90,155.937850952148,232.292022705078,500]PE。不是一套共同PE边界的重新直方图。

| run | 箱1 | 箱2 | 箱3 | 合计 |
|---|---|---|---|---|
| SR0 | 1.582992964 | 1.943639708 | 0.968433186 | 4.495065858 |
| SR1 | 1.931037954 | 3.705468865 | 2.185660547 | 7.822167365 |

背景与原始信号对照来自[R17]原HDF5名义模板，按相应曝光相乘；D来自官方事件表的直接箱计数，与[R03] PDF p6 Fig.2核对。原发布B8模板仅作信号对照，没有再作为背景加入。

本轮SM与原发布名义信号的三箱相对差异为 +2.05719%, +2.46324%, +6.57183%；逐run最大绝对差异约 10.01465%。它与此前“同一官方CDF谱重铸验证”的最高6.30%不是同一比较，不能混用。

论文打印总曝光3.51t·yr，本轮响应配套发布采用3.516991t·yr，相差约0.199%。若只把曝光改成3.51，按线性缩放得到总SM 12.292749289；默认结果未作这个缩放，也没有通过c_i强行对齐参考。

### 本章参考文献

- [R03] APRILE E, et al. (XENON Collaboration). First Indication of Solar ⁸B Neutrinos via Coherent Elastic Neutrino-Nucleus Scattering with XENONnT[J]. Physical Review Letters, 2024, 133: 191002. DOI: [10.1103/PhysRevLett.133.191002](https://doi.org/10.1103/PhysRevLett.133.191002). D/B 版本对照实际使用 [arXiv:2408.02877v1](https://arxiv.org/abs/2408.02877v1), 2024-08-06（v1 题名为 First Measurement…）；本库原有 v2 保留，不能追溯当成 benchmark v1 的输入。 [本次数值的直接原件/本地采用源](<../../../../../../重构/20261106_8B_Qy_DB提取/references/2408.02877v1.pdf>)
- [R17] XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [GitHub固定版本](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]，提交指纹`a09cd8fd77570dc2095f65f094fbcc114b634dfc`，下载ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。关联论文为文献[12]，Phys. Rev. Lett. 134, 111802 (2025)，arXiv:2409.17868。包内README给出数据DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本次核验GitHub ZIP，未将其冒充Zenodo附件逐字节核验。实际读取signal/六份YBe JSON、orthonormal_basis/单能HDF5、ac/er/b8/rg模板、utils.py与notebook 1；官方重铸方法与原2024 CEvNS分析的精确等价性单独待核。 [本次数值的直接原件/本地采用源](<../../../../../../重构/20261106_Onboarding_provenance_revision/sources/xenon-light-wimp-release-master.zip>)

[返回目录](#toc)

<a id="validation"></a>

## 验证与限制

| 加密维度 | 最大逐箱相对差异 | 最大绝对差异(events) | 预定数值条件 |
|---|---|---|---|
| recoil | 0.0015079% | 4.75593e-05 | PASS：max(2e-4 events, 0.2%) |
| neutrino_energy | 0.00260442% | 8.65115e-05 | PASS：max(2e-4 events, 0.2%) |

运行网格（基础T节点/Eν节点）与总数：

| 步骤 | T基础节点 | Eν基础节点 | 总事件数 |
|---|---|---|---|
| base | 201 | 120 | 12.3169533416 |
| recoil_refined | 401 | 120 | 12.3169554103 |
| recoil_fine | 801 | 120 | 12.3170251124 |
| energy_refined | 801 | 480 | 12.3172332235 |

Eν另并入829点源表断点，T另并入响应、产额和输出箱断点。保存各run/九核素分量，检查非负、组分和、通量线性、弹性端点和截面单位。SM点数值收敛不等于论文曲线/官方likelihood复现；本轮没有拟合、置信区间或BSM扫描。

本轮测试实际为95项通过、4项失败；新增solar合同7项通过，所选旧实验数值Slow/Fast/分量回归通过。4项失败为两个旧Physics MD同步检查与两个旧资源清单哈希检查。旧输入、数组、MD和资源清单与此前快照逐字节一致；移除新增solar绑定仍能复现旧MD差异，因此不改旧参考或容差来掩盖。[实际测试记录](<../../../../../outputs/solar_b8_sm/20261107_run1/TEST_RESULTS.json>) · [旧MD独立对照](<../../../../../outputs/solar_b8_sm/20261107_run1/LEGACY_MD_BASELINE_CHECK.json>) · [旧文件指纹](<../../../../../outputs/solar_b8_sm/20261107_run1/LEGACY_INPUT_PRESERVATION.json>)。

XENONnT只在公开重铸支持域0.51–5keV使用响应，不外推。8B表最高能量对应的Xe反冲上限低于5keV；低于0.51keV的响应不由本模型认证，0.5–0.51keV的技术截断与原分析差异仍保留。

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
experiment = load_experiment_package("data/experiments/XENONnT/XENONnT_2024_SolarB8")
prediction = predict_experiment(experiment, numerics={"n_er": 801, "n_enu": 480})
print(prediction.counts)
```

主项目代码、正式包、阶段记录和结果均已落盘。通过显式输入包加载时使用项目现有scoped Catalog；没有把PARTIAL结果无条件加入默认活动实验清单。旧onboarding保持原位。

[返回目录](#toc)
