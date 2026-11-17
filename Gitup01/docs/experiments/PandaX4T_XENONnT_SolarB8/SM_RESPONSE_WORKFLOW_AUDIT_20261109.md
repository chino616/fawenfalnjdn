# SM Response 逐步计算与 workflow 核对：2411.11749v1 Fig. 1

2026-11-09，主项目复算与审计记录。**目标 benchmark 是 2411.11749v1 的 Fig. 1（PDF第7页）事件数谱。** 左图是PandaX-4T US2的电子数谱，右图是XENONnT的S2谱；蓝线表示作者预测的SM信号加背景，彩色直方图是实验方拟合参考。Fig. 2属于之后的通量／弱混合角统计分析，本轮未计算。

**本轮已用主项目正式包和标准Runtime重新计算，结果逐箱复现旧运行。物理计算链与workflow的模块顺序一致；完整论文Fig. 1复现仍为PARTIAL。** XENONnT采用公开早期重铸Response；PandaX已有提取能区内的ROI选后总量估计及真实T分布，仍缺US2逐电子数箱Response。机器重复计算通过不等于论文分析等价性或人工科学审核通过。

[原论文PDF](../../references/Solar_CEvNS/2411.11749v1.pdf) · [原文Fig. 1整页图](../../../outputs/solar_b8_sm/20261109_response_audit_run1/paper/page_7.png) · [本轮数值、源码指纹与验收](../../../outputs/solar_b8_sm/20261109_response_audit_run1/README.md) · [联合目录](README.md) · [onboarding v3.0](SOLAR_B8_ONBOARDING.v3.0.md)

<a id="toc"></a>

## 目录

- [1. 从论文到主程序：计算对象与调用链](#scope)
- [2. Source：中微子能谱与通量](#source)
- [3. Target：天然氙与曝光](#target)
- [4. Interaction／Nuclear／Kinematics：SM截面](#cross-section)
- [5. 从入射通量得到真实反冲谱](#recoil)
- [6. Detector Response：真实反冲进入哪个观测箱](#response)
- [7. 折叠、叠加背景及本轮结果](#prediction)
- [8. 与workflow逐阶段核对及验收边界](#workflow)
- [9. 数据来源、复算和下一步缺口](#references)

<a id="scope"></a>

## 1. 从论文到主程序：计算对象与调用链

本轮固定SM参数，不拟合：总通量为5.46×10⁶ cm⁻² s⁻¹，sin²θW=0.23857；源谱采用Bahcall中心值表，核形因子采用Klein–Nystrand（KN）。前两个数来自文献[1] PDF第3页式(1)–(3)附近、第5页式(11)后与第7页Sec. IV A。天然Xe组成和常量采用项目明确的本地资源约定，不能把这些全部说成文献[1]逐数值列出的参数。

| 层 | 本次真实消费者 | 输入与输出 |
|---|---|---|
| 正式包 | [package_loader.py](../../../cevns_pyeft/experiments/package_loader.py)，`load_experiment_package` | 各实验YAML／NPZ → 已准备模型及资源指纹 |
| 标准Runtime | [runtime.py](../../../cevns_pyeft/experiments/runtime.py)，`predict_experiment` | 已准备模型、固定SM点、Slow网格 → Prediction |
| 实验适配 | [solar_b8.py](../../../cevns_pyeft/experiments/solar_b8.py)，`SolarPreparation`／`SolarExecutor` | 装配Source、Target、共享截面及Detector，按run执行 |
| 共享截面 | [sm_coherent.py](../../../cevns_pyeft/theory/sm_coherent.py)，`StandardModelKN.dsigma_dT` | Eν、T、核素、弱混合角 → cm²/keV |
| 共享反冲积分 | [recoil.py](../../../cevns_pyeft/rates/recoil.py)，`integrate_recoil_yield` | 通量／注量与截面 → 每核反冲产额 |
| 共享探测器折叠 | [folding.py](../../../cevns_pyeft/rates/folding.py)，`probability_fold` | 每核反冲产额和接受后箱概率 → 每核逐箱产额 |

Runtime不读取workflow台账来计算。workflow负责输入依据、模块选择、阶段检查和人工接受；正式YAML／NPZ及当前代码负责实际数值。

[返回目录](#toc)

<a id="source"></a>

## 2. Source：中微子能谱与通量

要先知道“每单位能量有多少中微子到达探测器”：

$$
\frac{d\phi}{dE_\nu}=\Phi_{8B}f_{8B}(E_\nu). \tag{1}
$$

依据：文献[1] PDF第5页式(11)后的通量选择；谱形原件为文献[2]及其Bahcall官方数值表。这里的Φ是地球处总通量，不再乘一次源到探测器的几何衰减。

| 输入／处理 | 实际值与单位 | 取得情况、来源和用途 |
|---|---|---|
| Φ8B | 5.46×10⁶ cm⁻² s⁻¹ | 文献[1] PDF p5式(11)后；两套正式卡一致 |
| Eν节点 | 829点，0–16.56 MeV | Bahcall原表的能量列；完整正式数组见下面两个资源文件 |
| f8B | 829点，MeV⁻¹ | 原表中心谱列，不采用上下变形列；分段线性插值，支撑外置零 |
| 表格积分 | 0.999986544 | 对原节点作梯形积分的项目推导值；保留原表，未强制再次归一化 |
| 入射味态 | 总活动味通量，味普适树级SM | 文献[1] PDF p3式(2)、味普适讨论与脚注；代码以trace=1的代表态表达，无额外“乘3”或MSW概率 |
| 12%通量误差 | 本次不作随机乘数 | 文献[1] PDF p6式(17)后的统计先验；固定点前向计算不等于已执行nuisance拟合 |

本地实际输入：[XENONnT标量卡](../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.input.yaml)／[完整数组](../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz)，[PandaX标量卡](../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.input.yaml)／[完整数组](../../../data/experiments/PandaX4T/PandaX4T_2024_US2/experiment.resources.npz)。数组键为`source_energy_MeV`和`source_shape_per_MeV`；出处是上述文献和原表，键名本身不是出处。

实际执行位置：`solar_b8.py::SolarSpectrum.__call__`。两实验复用同一源谱，不把已折叠的实验反冲谱当成中微子源。

[返回目录](#toc)

<a id="target"></a>

## 3. Target：天然氙与曝光

给定单个氙核的散射率后，必须明确探测器内有多少个各类核。这里使用天然Xe的9个核素，而不是默认纯Xe-131：

$$
\overline M=\sum_A f_A M_A,\qquad
N_A^{(1\,\mathrm{t})}=\frac{10^6N_{\mathrm{Av}}f_A}{\overline M\,[\mathrm{g/mol}]}. \tag{2}
$$

依据：文献[3]的数丰度和原子质量，经上述核数公式推导。原子质量用于物质数；运动学核质量取原子质量乘u的GeV换算后减54个电子质量，忽略电子结合能。沿用项目以u数值对应g/mol的摩尔质量常量近似。

| 输入／推导 | 实际值 | 来源／含义 |
|---|---|---|
| A顺序 | 124、126、128、129、130、131、132、134、136 | 文献[3]，两套正式NPZ的天然Xe表 |
| 数丰度 | 0.000952、0.000890、0.019102、0.264006、0.040710、0.212324、0.269086、0.104357、0.088573 | 文献[3]对应各核素；总和1 |
| 平均原子质量 | 131.29276144779053 u | 上述9核素质量／丰度加权，完整质量数组见正式包和本轮数值清单 |
| 每吨核数总和 | 4.586803334466193×10²⁷ | 式(2)，NAv=6.02214076×10²³ mol⁻¹ |
| PandaX US2曝光 | 1.04 t·yr | 文献[1] PDF p5式(12)后的实验曝光 |
| XENONnT本次曝光 | SR0=1.174398，SR1=2.342593 t·yr；合计3.516991 | 文献[4]固定发布的`statistical_model_base.yaml`，作为本次实际采用值 |
| XENONnT论文打印曝光 | 3.51 t·yr | 文献[1] PDF p5；与发布值分别保留，不静默替换 |

1000 kg和31557600 s/yr是计算锚点，不是人为补造独立的实测质量和活时间。先算“1吨×1参考年”的产额，再按run曝光缩放，质量、时间各施加一次。

实际执行位置：`solar_b8.py::SolarPreparation`。全部核素的核质量、核数和中间反冲率列于[本轮逐核素数值记录](../../../outputs/solar_b8_sm/20261109_response_audit_run1/AUDIT_NUMERICS.json)。

[返回目录](#toc)

<a id="cross-section"></a>

## 4. Interaction／Nuclear／Kinematics：SM截面

本轮选择文献[1] PDF第3页式(1)–(3)，不加入新相互作用，也不增加高阶辐射修正：

$$
\frac{d\sigma_A}{dT}=\frac{G_F^2m_A}{\pi}
\left(Q_{V,A}^{\rm SM}\right)^2 F_{\rm KN}^2(q)
\left(1-\frac{m_AT}{2E_\nu^2}-\frac{T}{E_\nu}\right),\qquad
Q_{V,A}^{\rm SM}=\frac{1-4\sin^2\theta_W}{2}Z-\frac{A-Z}{2}. \tag{3}
$$

$$
F_{\rm KN}(q)=\frac{3j_1(qR_A)}{qR_A}\frac{1}{1+(qa_k)^2},\qquad
R_A=1.23A^{1/3}\,\mathrm{fm},\quad a_k=0.7\,\mathrm{fm}. \tag{4}
$$

这里的核形因子属于Nuclear Structure；后面的Detector Response描述读出和事件选择，是独立对象。本次不使用`responses_all.json`的EFT多项式来代替选定的KN形因子。

| 数值／选择 | 本次值或实现 | 直接依据 |
|---|---|---|
| sin²θW | 0.23857 | 文献[1] PDF p3与p7，固定值 |
| Z、gpV、gnV | 54、0.02286、−0.5 | Z为Xe；由文献[1]式(2)及固定弱混合角得到 |
| G_F | 1.1663787×10⁻⁵ GeV⁻² | 文献[6]项目公共常量的本地复用，写入正式卡；非声称论文逐数值给出 |
| ħc | 0.1973269804 GeV·fm | 同一项目常量约定，用于q的fm⁻¹转换 |
| 截面面积换算 | 1 GeV⁻²=3.893793721×10⁻²⁸ cm² | 同一项目常量约定；dT从GeV换到keV再乘10⁻⁶ |
| 核质量转换 | 1 u=0.93149410372 GeV；me=0.00051099895069 GeV | 正式卡的项目常量；结合文献[3]原子质量 |
| 运动学 | 精确弹性两体Eν下限／T上限 | [kinematics.py](../../../cevns_pyeft/theory/kinematics.py)；相同守恒关系，不以固定能量下限代替 |

$$
E_{\nu,\min}(T)=\frac{T+\sqrt{T^2+2m_AT}}{2},\qquad
T_{\max}(E_\nu)=\frac{2E_\nu^2}{m_A+2E_\nu}. \tag{5}
$$

数值核对点：Xe-132、Eν=10 MeV、T=1 keV时，QV=−37.76556，F²=0.9456863839872542，Eν,min=7.83760243888223 MeV，dσ/dT=1.0775314085158783×10⁻³⁹ cm²/keV。它们是本地采用质量、常量及式(3)–(5)的推导结果，完整输入见本轮JSON。代码保留式(1)中的−T/Eν项，没有将它漏掉。

[返回目录](#toc)

<a id="recoil"></a>

## 5. 从入射通量得到真实反冲谱

对每个核素分别计算：

$$
\frac{dR_A^{(1\,\mathrm{t}\cdot\mathrm{yr})}}{dT}
=N_A^{(1\,\mathrm{t})}t_{\rm yr}
\int_{E_{\nu,\min}(T)}^{E_{\nu,\max}}
dE_\nu\,\Phi_{8B}f_{8B}(E_\nu)\frac{d\sigma_A}{dT}. \tag{6}
$$

依据：文献[1] PDF p5式(11)的源与截面卷积，加上显式核数和参考年归一化。式(6)是一个参考曝光1 t·yr的产额，微分单位为events/keVnr；除以该参考曝光就是events/(t·yr·keVnr)的比率，两者在所用单位下数值相同。此处尚未施加探测器选择。`recoil.py::integrate_recoil_yield`先输出每核产额，`SolarExecutor`再乘核数。

实际源为连续8B谱；能量积分合并均匀网格与原谱断点，按每个T的精确Eν,min筛选合法节点。当前代码不声称向每个能量网格额外插入Eν,min节点。反冲积分合并均匀网格、Response／产额曲线断点；PandaX还并入真实反冲箱边界。均采用梯形求积，并在P10做加密检查。

| 模型中的T域 | 未选取真实反冲数／每t·yr | 用途与边界 |
|---|---|---|
| XENONnT：0.51 keV至各核素物理端点（模板支撑上限5 keV） | 304.46327220617616 | 源＋靶＋SM的中间结果；还不是重建S2信号数 |
| PandaX：已提取接受度可见域约0.3–3 keVnr | 488.1567929189261 | 尚未乘Total(US2)的真实反冲中间结果；乘该效率后才包括ROI选择 |

直接数值在两实验新运行的`sm_prediction.npz`中，以逐核素T网格及`rate_per_tyr_keV_Xe...`保存。[全部中间量与链接](../../../outputs/solar_b8_sm/20261109_response_audit_run1/AUDIT_NUMERICS.json)记录了实际节点数、物理端点和1 keV处的值。

[返回目录](#toc)

<a id="response"></a>

## 6. Detector Response：真实反冲进入哪个观测箱

Response要回答的是：“真实反冲为T的一个事件，通过选择并进入观测箱i的概率是多少？”采用接受后概率Kri(T)，包含能量迁移、分辨率／涨落和该模板的选择；其和通常小于1，不能自行归一化到1。

$$
S_{ri}=\frac{\mathcal E_r}{1\,\mathrm{t}\cdot\mathrm{yr}}\sum_A\int dT\,
\frac{dR_A^{(1\,\mathrm{t}\cdot\mathrm{yr})}}{dT}\,K_{ri}(T). \tag{7}
$$

这里以实际曝光除以参考曝光，R的参考归一化如式(6)。式(7)是本项目的探测器概率折叠定义；它不是论文原文已经给出的响应矩阵。核数和参考年已在R中，不再乘第二遍。

### XENONnT：确实执行了Response折叠

来源为文献[4]固定官方发布的单能模板，先对shadow、S1BDT、S2BDT三个观测轴求和，保留cS2三箱；再沿T、Ly、Qy三轴内插，选取该发布YBe的median产额曲线。原四维模板的边际化保留原有选取，没有另外乘一次已数字化的总效率。

| 真实输入 | 数组形状／支撑 | 单位和直接出处 |
|---|---|---|
| response_SR0、response_SR1 | 各16×10×10×3 | 接受后箱概率，无量纲；文献[4]每run 1600份单能HDF5模板，后三个观测轴边际化后的项目派生数组 |
| response_energy_keV | 16点，0.51–5 | keVnr；同发布的`BASIS_E_R`和HDF5坐标 |
| response_Ly、response_Qy | 各10点，1–10 | photon/keVnr、electron/keVnr；同发布的扫描坐标 |
| yield_energy_keV、yield_Ly_median、yield_Qy_median | 各501点；原产额T域0.3–10，本次仅在Response支撑内使用 | 同发布YBe median JSON的coordinate_system和map；没有用另一版本产额替换 |

完整数组在[XENONnT正式NPZ](../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/experiment.resources.npz)，逐数组出处、代表值和哈希见[本轮数值记录](../../../outputs/solar_b8_sm/20261109_response_audit_run1/AUDIT_NUMERICS.json)及[v3.0 Detector章](../XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v3.0.md#detector)。

例如T=1 keV时，SR0三个接受后概率约为[0.0055498311, 0.0044507837, 0.0007170622]，SR1约为[0.0036041575, 0.0047918885, 0.0009193304]。同样能量可以进入不同观测箱，也可能全部未通过。这正是单一均值映射TQy所不包含的信息。

论文式(14)的g2=16.9 PE/electron描述其平均S2换算。本次Response已有S2标定及选取，实际内插没有额外的g2乘数；这不等于已经证明该发布内含的所有标定都与论文16.9完全等价。类似地，式(13)的Jacobian在式(7)的T空间概率积分中无需再额外乘一次。

### PandaX：当前不能称为Ne Response折叠

已取得文献[5] PDF p3 Fig. 1黑色Total(US2)的99个可见矢量节点，以及p5 Fig. 4下图的Qy曲线。**原文p3的ROI说明与Fig.1标题明确：Total(US2)已经包含Ne∈[4,8]的ROI选择。** 当前正式包采用该总接受度作ROI选后样本的真实反冲投影；Qy均值仍是辅助参考，没有另外进入该投影的Runtime输入，也不应再次施加均值ROI窗口。

**MISSING：US2逐Ne箱的接受后概率KUS2,i(T)。** 已有总ROI接受度给出这八箱概率之和，可以计算已提取T域内的ROI总量；它仍无法唯一决定八个箱各占多少。Qy只提供均值，不能补出这个分配。完整一维Ne目标只需要对应的一维边际响应，不强制要求取得完整原生多维likelihood。

目前实际执行的是对真实T箱积分“反冲率×含ROI的总接受度”，T域约0.3–3 keVnr；这给出该能区内的ROI选后总量及T分布，尚未得到Ne的八箱形状。效率在未提取能区的贡献也不能直接宣告为零。不能把真实T分布贴到论文Fig. 1左图的电子数横轴上。此前将该积分笼统标为“不是ROI总量”不准确，本段按原文更正，数值没有改动。

### 为什么没有c_i

文献[1] PDF p5式(12)后明确说明：作者忽略分辨率，采用一维简化分析，再以ci校准到合作组参考谱。本项目以接受后Response处理迁移和选择，不额外引入ci。

不含ROI的选择效率与确定性平均读数窗口相乘，是无迁移模型的一种极限；已经包含ROI的Total(US2)不能再随意重复裁剪平均窗口。采用完整概率核与作者的简化校准路线具有不同探测器假设；不能因此保证蓝线逐点相同，更不能再拟合一个任意ci来掩盖Response版本差异。

[返回目录](#toc)

<a id="prediction"></a>

## 7. 折叠、叠加背景及本轮结果

### XENONnT逐run及逐箱结果

| run | cS2完整边界[PE] | 第1箱SM | 第2箱SM | 第3箱SM |
|---|---|---:|---:|---:|
| SR0 | 90, 170.161773681641, 249.889739990234, 500 | 1.582992963966 | 1.943639708297 | 0.968433185828 |
| SR1 | 90, 155.937850952148, 232.292022705078, 500 | 1.931037953966 | 3.705468864915 | 2.185660546577 |
| 按各run箱序号相加 | 共同序号1／2／3，非同一组PE边界 | 3.514030917931 | 5.649108573212 | 3.154093732404 |

这些边界来自文献[4]各run原HDF5的`bins/0`，数值在正式NPZ；事件数由式(7)推导。合计信号为**12.317233223547694 events**。

加入背景是文献[1] PDF p6式(16)的步骤：μi=Si+ΣkBi,k。本次绘图读取文献[4]的名义AC、ER和neutron模板并按各自run曝光换算，观测来自当前登记的逐run事件分箱文件；它们不进入前面的信号折叠。

| 当前模型的箱序号 | SM信号 | 名义背景合计 | SM＋背景 | 观测D |
|---|---:|---:|---:|---:|
| 1 | 3.514031 | 8.496674 | 12.010705 | 16 |
| 2 | 5.649109 | 8.592265 | 14.241374 | 14 |
| 3 | 3.154094 | 9.306219 | 12.460313 | 7 |
| 合计 | 12.317233 | 26.395159 | 38.712392 | 37 |

直接来源：[观测逐run表](../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_official_observed_bins.txt)、[SR0模板](../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_and_b8_early_release.npz)、[SR1模板](../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_and_b8_early_release.npz)。本地来源、数组及转换范围沿用[v3.0 Statistics章](../XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v3.0.md#statistics)，没有把名义模板当成论文postfit背景。这里只画图和比较，没有执行式(17)的profiling。

![本轮XENONnT逐箱SM计算；合并面板按run箱序号相加](../../../outputs/solar_b8_sm/20261109_response_audit_run1/calculation/XENONnT_2024_SolarB8/events.png)

紫色参考线对应公开早期发布自身的信号模板，总量11.916094375365525，与本轮信号相差约+3.36636%。它是独立发布参考，尚未将源谱／形因子／响应等条件全部对齐，不把这个差异当成纯数值积分误差或Fig. 1蓝线的复现误差。

### 直接对照论文Fig.1蓝线（2026-11-09补充）

从原v1 PDF第7页的深蓝色矢量阶梯直接取点，并以坐标框标定线性计数轴。以下比较的是信号加背景；按显示箱序号粗对照，各run的实际边界与论文分析参数点尚未全部统一。

| 显示箱序号 | 论文蓝线：信号＋背景 | 主项目：信号＋背景 | 相对差异 |
|---|---:|---:|---:|
| 1 | 11.8612 | 12.0107 | +1.26% |
| 2 | 13.8845 | 14.2414 | +2.57% |
| 3 | 11.7930 | 12.4603 | +5.66% |
| 合计 | 37.5387 | 38.7124 | +3.13% |

这才是针对论文蓝线的直接数值对照；上述3.37%是另一个官方信号模板比较，不是这张图的蓝线误差。不能将当前差异全部归于Response，背景／选取／归一化条件也还未一一对齐。彩色背景来自实验拟合，不能在未核对作者nuisance的情况下从蓝线扣除并认证为作者的纯信号。原始路径、来源SHA256、标定及算法见[本图逐箱对照记录](../../../outputs/solar_b8_sm/20261109_fig1_comparison/README.md)。

### 必须单独保留的比较边界

1. 文献[1] **正文p5写S2∈[120,500] PE，而Fig. 1图示延伸到约90 PE**；既有图线数字化表也保留约[90,155,235,500]的显示边界。当前发布Response是run-specific cS2∈[90,500] PE。raw S2／cS2、选取和发布版本的对应仍需核验；没有自行断言正文是笔误。
2. SR0、SR1的实际内部边界不同。合并箱序号符合当前模板表示，不等于将两run重分箱到统一PE轴；不能在粗箱内部假设均匀分布来切出120 PE阈值。
3. 本次实际曝光为3.516991 t·yr。若仅按3.51/3.516991缩放，信号为12.292749288995168 events；这只是曝光敏感性核对，未被采用，也不能解决坐标、选取或版本问题。
4. 作者的无分辨率＋ci与本次早期官方Response不是同一探测器实现。**因此当前结果不能标成“2411.11749v1 Fig. 1严格逐箱复现通过”。**

### PandaX当前可计算的量

本轮接受度加权的真实反冲积分为**47.02675280087643 events**，曝光1.04 t·yr。由于Total(US2)已含ROI，它是已提取T域约0.3–3 keVnr内的ROI选后总信号估计；尚无Ne八箱分配。论文彩色信号是拟合参考，当前为固定通量点；总量比较仍须对齐拟合参数／源及响应假设和未覆盖能区，不直接把两者之比当作复现精度。

![PandaX计算范围：左侧真实反冲投影已计算，右侧仅为论文电子数谱参考](../../../outputs/solar_b8_sm/20261109_response_audit_run1/calculation/PandaX4T_2024_US2/events.png)

右侧八箱参考来自原有[论文Fig. 1数字化表](../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_benchmark_fig1.txt)，用于说明尚未计算的目标，不冒充本程序预测。

[返回目录](#toc)

<a id="workflow"></a>

## 8. 与workflow逐阶段核对及验收边界

| workflow阶段 | 本次对应工作 | 实际状态 |
|---|---|---|
| P01 Dataset | 保持PandaX4T_2024_US2、XENONnT_2024_SolarB8身份，benchmark指向Fig. 1 | 既有身份复用，无新dataset或默认激活 |
| P02 Target／Exposure | 天然Xe核数、核质量、run曝光及单位账本 | 实际读入并计算；项目采用约定与论文打印值分列 |
| P03 Source | Bahcall谱形、总通量、味普适入射态及插值 | 实际读入并计算 |
| P04 Interaction／Nuclear | 树级SM、固定弱混合角、KN | 对照论文p3式(1)–(3)，实际执行共享模块 |
| P05 Kinematics／Cross-section | 精确运动学、弱荷、q与截面单位 | 实际执行；约束由原有测试覆盖 |
| P06 Detector | XENONnT接受后概率；PandaX效率投影与缺失Ne核 | XENONnT在已声明早期模型内可算；PandaX Ne保持BLOCKED |
| P07 Slow | 对Eν与T积分、折叠、核素／run求和，输出逐箱数组 | 本轮重新运行；与旧结果逐箱完全一致 |
| P08 Fast | 不是本轮计算入口 | 未执行，不将缓存结果冒充Slow复算 |
| P09 Statistics | 观测／背景画图；式(17)拟合尚未实现于本轮 | D/B不反向校准信号；Fig. 2未计算 |
| P10 Validation | 输入／代码指纹、加密、能力边界和参考比较 | 内部重复及收敛PASS；论文复现PARTIAL，人工接受不自动升级 |

前期P00来源登记、P01证据、P02缺口、P03物理合同是onboarding台账；不要将这些文件编号与上表物理计算阶段混为一谈。旧台账部分字段／人工审核仍为DRAFT或NOT_REVIEWED，本次没有用可执行包的存在替代它们的科学审阅。

实际执行命令是既有主项目脚本：

```powershell
python -B tools/run_solar_b8_sm_benchmark.py --output outputs/solar_b8_sm/20261109_response_audit_run1/calculation
```

网格依次为(nT,nEν)=(201,120)、(401,120)、(801,120)、(801,480)，并入各自原表断点；不是把标量卡默认的(401,240)误写成实际最终网格。接受标准逐箱为绝对差≤max(2×10⁻⁴ events, 0.2%×该箱事件数)，反冲与中微子能量维度分别加密。本轮两实验均通过，结果及每次时间见[SM总记录](../../../outputs/solar_b8_sm/20261109_response_audit_run1/calculation/BENCHMARK_SUMMARY.json)。

原有`tests/test_solar_b8_sm_contract.py`的7项相关测试通过，覆盖零反冲绝对单位、KN、弹性端点、关闭SM、响应概率、run边界、天然Xe／通量、通量线性及缺失响应的禁止升级。297份代码、输入、canonical记录和旧SM结果哈希未变。本次未修改物理实现、数值表或科学Gate。

[返回目录](#toc)

<a id="references"></a>

## 9. 数据来源、复算和下一步缺口

| 下一项能力 | 还需什么 | 不能用什么替代 |
|---|---|---|
| PandaX Fig. 1左图的SM Ne八箱谱 | 2024 US2对应的接受后KUS2,i(T)，或足以生成它的受核验响应模型 | Qy均值、总接受度和已对源谱积分的参考信号不能唯一反演该核 |
| XENONnT与论文Fig. 1同一分析的定量比较 | 确认S2／cS2坐标、90／120阈值、run分箱、选取／标定版本与参考参数点 | 不能靠曝光重标、粗箱均匀切分或任意ci宣告等价 |
| Fig. 2参数卡方曲线 | 在已闭合的对应逐箱预测上另行配置式(17)、背景先验和通量相关性 | 信号图画出来或7个单元测试通过不等于χ²已经复现 |

本轮是固定SM点的复算与说明，不把待补问题转成新的已批准科学选择。具体来源和数值核验范围还可从[统一v3.0](SOLAR_B8_ONBOARDING.v3.0.md)及[实际输入、数组与逐核素记录](../../../outputs/solar_b8_sm/20261109_response_audit_run1/AUDIT_NUMERICS.json)逐项追查。

标准参考文献：

1. DE ROMERI V, PAPOULIAS D K, TERNES C A. Bounds on new neutrino interactions from the first CEνNS data at direct detection experiments[J]. Journal of Cosmology and Astroparticle Physics, 2025, 05: 012. DOI: [10.1088/1475-7516/2025/05/012](https://doi.org/10.1088/1475-7516/2025/05/012). **实际核对版本为[arXiv:2411.11749v1](https://arxiv.org/abs/2411.11749v1)，2024-11-18**；[本地PDF](../../references/Solar_CEvNS/2411.11749v1.pdf)，p3式(1)–(3)，p5–6式(11)–(17)，p7 Fig. 1及Sec. IV A。本轮保留整页文本与原图，未用期刊版替换v1。
2. BAHCALL J N, LISI E, ALBURGER D E, et al. Standard neutrino spectrum from ⁸B decay[J]. Physical Review C, 1996, 54: 411–422. DOI: [10.1103/PhysRevC.54.411](https://doi.org/10.1103/PhysRevC.54.411). [Bahcall官方数值表](https://www.sns.ias.edu/~jnb/SNdata/Export/B8spectrum/b8spectrum.txt)[DS/OL]，原下载访问日2026-11-06；原件SHA256 `75ce26216a638b811d131b692e2d22b8624fcbb711839fd167c25cefaafb9789`，本次读取其已登记的正式中心谱数组，未重新联网认证。
3. NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Atomic Weights and Isotopic Compositions for Xenon[DB/OL]. [NIST Xe条目](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe)[2026-11-06]. 本次直接复用项目[天然Xe数值表](../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/xenon_natural_isotopes_nist_v2.txt)及正式包数组；原子质量／数丰度及核数推导范围如第3节，不声称这些数值逐项印在文献[1]。
4. XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. [固定GitHub提交a09cd8fd77570dc2095f65f094fbcc114b634dfc](https://github.com/XENONnT/light_wimp_data_release/tree/a09cd8fd77570dc2095f65f094fbcc114b634dfc)[2026-11-06]. 关联：APRILE E, et al. First Search for Light Dark Matter in the Neutrino Fog with XENONnT[J]. Physical Review Letters, 2025, 134: 111802. DOI: [10.1103/PhysRevLett.134.111802](https://doi.org/10.1103/PhysRevLett.134.111802). 发布README给出[10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)；本地实际核验的是GitHub ZIP而非Zenodo附件，ZIP SHA256 `275418ce030902c27f887f54e3b4397213beccc8a7fc835553db42f54ac9d4bd`。具体来源链及转换见[v3.0对应章节](../XENONnT/datasets/XENONnT_2024_SolarB8/experiment.physics.v3.0.md#detector)。
5. BO Z, et al. (PandaX Collaboration). First Indication of Solar ⁸B Neutrino Flux through Coherent Elastic Neutrino-Nucleus Scattering in PandaX-4T[J]. Physical Review Letters, 2024, 133: 191001. DOI: [10.1103/PhysRevLett.133.191001](https://doi.org/10.1103/PhysRevLett.133.191001). [arXiv:2407.10892v3](https://arxiv.org/abs/2407.10892v3)，2024-09-13；[本地PDF](../../references/Solar_CEvNS/2407.10892v3.pdf)，p3 Fig. 1 Total(US2)，p5 Fig. 4下图Qy与p6 Fig. 5观测／背景。数字化值和适用范围沿用[v3.0 Detector章](../PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v3.0.md#detector)，本轮未重新数字化。
6. CEvNS-pyEFT Project. [foundation/constants.py](../../../cevns_pyeft/foundation/constants.py)与两实验正式输入包[CP/OL]. 本地项目工作副本[2026-11-09]. 本次采用现有公共常量和显式参数卡约定；本地复用与外部常量原文认证分别说明。代码、包及来源文件哈希见[本轮资源核对](../../../outputs/solar_b8_sm/20261109_response_audit_run1/RESOURCE_AUDIT.json)。

[返回目录](#toc)
