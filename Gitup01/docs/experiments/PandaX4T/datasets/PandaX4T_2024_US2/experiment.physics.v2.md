# PandaX-4T 2024 US2 — Response onboarding v2.0（新版本）

**版本：v2.0；日期：2026-11-06；方法：完整探测器 Response 折叠；状态：资料已补充，完整原实验适配仍为 PARTIAL。**

[精简版 v2](<experiment.physics.summary.v2.md>) · [用户资料 v2](<EXPERIMENT_USER_INPUT.v2.md>) · [标准参考文献](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md>) · [数据目录](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/README.md>) · [旧 onboarding（原位保留）](<../../../../../../../.experiment-auto-runs/cevns-threephase-20261105-high01/snapshot/docs/experiments/PandaX_4T/datasets/PandaX4T_SolarB8_Run0_Run1/EXPERIMENT_USER_INPUT.md>)

本轮用户明确指定采用 Response 方法并要求严格来源标注。本文件落实该选择，不再把作者的逐箱 c_i 作为探测器输入；未运行拟合、未激活新 Runtime，也不把机器回读通过当作论文复现成功。与旧版相比，谱形/绝对通量、Qy/完整响应、事件/模板版本和原实验/再分析 B 均分开登记。

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

实验输入以 [[2]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-2) 的早期太阳 8B 测量为身份依据，以 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) 的 Fig.1/2/4 为对照。新版采用 response 卷积，因模型不同，不宣称必须逐点重现作者含 c_i 的简化曲线。 范围固定为 Run0+Run1 的 US2，未加入 paired/2-hit/3-hit 的统计通道。后续 259-day 官方事件仅作单独标记的交叉核对。

旧版用户资料及两份 Physics MD 均原位保留，不覆盖、不重命名；旧版的其它实验/联合分析目标不自动延续为本 v2 的范围。

[返回目录](#toc)

<a id="s2"></a>

## 2. Source

太阳 $^8\mathrm{B}$ 源谱使用完整 Bahcall 官方四列表 [[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-4)。第一列为 $E_\nu$（MeV），第二列中心谱形（MeV$^{-1}$），第三/四列为有效 ±3σ 谱形；它们不含总通量、效率、靶核数或曝光。

$$
\frac{d\phi}{dE_\nu}=\Phi_{8B} f_{8B}(E_\nu). \tag{1}
$$

| 符号/输入 | 定义与单位 | 资源与精确出处 |
|---|---|---|
| $f_{8B}$ | 归一化能谱形，MeV$^{-1}$ | `b8_bahcall1996_official.txt` 第二列；[[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-4) 原表列 2 |
| $\Phi_{8B}$ | 总通量，cm$^{-2}$s$^{-1}$；参考值 $5.46\times10^6$，归一化相对误差 12% | [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) Sec.III 式 (11) 后及式 (17) 后；上游 SSM 文献 [[5]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-5) |
| 谱形误差 | ±3σ 包络，非 12% 总率误差 | [[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-4) 原表列 3/4；不直接改成独立逐点 Gaussian |

中心表 829 行，0–16.56 MeV，保留官网原始小数；梯形积分约 0.999986544，本次不静默重新归一化。计划在表内线性插值，表外置零是明确的数值约定而非论文给出所有高能尾的精确证明；需做端点/积分收敛检查。味普适 SM/NGI 基准使用所有活跃味总通量；改为味相关相互作用时需另给传播与味分量，不能沿用此简化。

[返回目录](#toc)

<a id="s3"></a>

## 3. Target

靶材为液氙，采用多同位素求和；新补充的 NIST 天然数丰度表是参考组成 [[9]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-9)，没有假装取得两实验的独立氙样品同位素化验。

$$
\overline M=\sum_A f_A M_A,\qquad n_A^{(t)}=\frac{10^6 N_{\rm A}f_A}{\overline M}. \tag{2}
$$

| 符号 | 定义与单位 | 数据位置/性质 |
|---|---|---|
| $f_A$ | 核素数丰度，无量纲 | `xenon_natural_isotopes_nist_v2.txt` 列 3；[[9]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-9) 对应 Xe 行 |
| $M_A$ | 原子摩尔质量，g/mol，数值对应原子质量 u | 同表列 2；它不是裸核质量 |
| $N_{\rm A}$ | 阿伏伽德罗常量，$6.02214076\times10^{23}$ mol$^{-1}$ | [[13]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-13) §2.2/Table 1，精确 SI 定义常量 |
| $n_A^{(t)}$ | 每吨氙中该核素核数，nuclei/t | 本文推导量；$10^6$ g/t |

丰度包含 Xe124/126/128/129/130/131/132/134/136，和为 1；未将数丰度直接当质量分数。将原子质量 u 的数值用于 g/mol 时，本版显式近似摩尔质量常量为 1 g/mol；现代 SI 下并非精确恒等，见 [[13]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-13) 印刷页 130。这是本版显式的质量换算近似，未将其解释为实验质量误差。截面所需裸核质量仍须由共享模块明确转换/近似，不把原子质量改称裸核质量。旧单一 Xe131 近似不用于新版默认。式 (2) 为项目的质量到核数推导。


参考天然组成的平均摩尔质量约 131.292761448 g/mol、每吨总核数约 4.586803334e+27；由式 (2) 与 NIST 表中心值计算，未传播组分误差。

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

[返回目录](#toc)

<a id="s4"></a>

## 4. 共享物理模块选择

Interaction、Nuclear structure、Kinematics、Cross-section 是独立选择，实验文档只登记接口选择，不复制公共 EFT/核响应推导。

| 维度 | 项目已存在候选 | v2 说明 |
|---|---|---|
| Interaction | `li2026_sm_left_v1` / `li2026_matching_v1` | 先以 SM 验证 response；NGI 需逐项匹配 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) 的算符/耦合约定 |
| Nuclear structure | `nuclear_np_polynomial_v1` | 本地 JSON 的 Xe 系数存在；外部源表/符号/归一化溯源未闭合，不称已获独立科学验证 |
| Kinematics | `elastic_kinematics_v1` | 校验真实反冲/入射能量的单位、支撑与运动学阈值 |
| Cross-section | `li2026_dsigma_v1` | 核响应进入截面；探测器 Response 在其后折叠，二者不混同 |
| Detector | 尚无该实验正式 Runtime binding | 本文完整响应合同，不虚构已注册实现 |

对照的 SM 参考点为 $\sin^2\theta_W=0.23857$（无量纲），直接定位 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) PDF 第 3 页 Sec.II A 式 (2) 后文字；Fig.2 扫描该参数时不固定为此数。本版只登记参考点，没有改 Runtime 默认值或替共享模块补参数。

文献 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) 的 SM/Scalar/Vector 使用 Klein–Nystrand 形状因子，见式 (3)；不能因选择项目核响应模块就声称两者逐点完全相同。Fig.4 所需轴矢量/张量自旋响应、标量核子输入及理论约定须完成独立对照后再作精确比较。

[返回目录](#toc)

<a id="s5"></a>

## 5. Detector Response

定义含选择的响应核，而不是只用平均 $n=TQ_y(T)$ 替换观测量：

$$
P_{r\mathbf i}(T;\boldsymbol\eta)=\int_{\Omega_{r\mathbf i}}d\mathbf x\,p_r(\mathbf x\mid T;\boldsymbol\eta)\,\epsilon_r(\mathbf x,T;\boldsymbol\eta),\qquad 0\le\sum_{\mathbf i}P_{r\mathbf i}\le1. \tag{3}
$$

| 符号 | 定义 | 单位/资源 |
|---|---|---|
| $T$ | 真实核反冲能量 | keVnr |
| $p_r$ | 给定真实能量的重建观测分布，含涨落与迁移 | 相应观测空间密度 |
| $\epsilon_r$ | 尚未计入 $p_r$ 的选择概率 | 无量纲；必须记录因子归属 |
| $P_{r\mathbf i}$ | 通过选择并进入 run r 的箱 i 的概率 | 无量纲；完整 response 的直接对象 |
| $\boldsymbol\eta$ | 校准/系统误差坐标 | 按来源定义，不能从图线误差带猜完整 prior |

式 (3) 是本项目对完整探测器 response 的合同表达，不声称论文 [1] 采用了该完整模型。response 若已含效率，不再乘旧 Total efficiency/Combined acceptance，也不乘 $c_i$。Qy 和 g2 仅为完整概率模型的均值/增益输入；不以一个均值曲线或任意 Poisson 假设冒充整个响应。

[[2]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-2) 第 5 页说明使用 NEST v2.3.6、Poisson/binomial 量子产生/探测涨落及 waveform simulation；[[6]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-6) Sec.II–VI/附录 A 提供产生、收集、重建、校正、选择框架。本次增加其 Table II 的 10 个明确校准值；例如 g1 和 g2b 是校准参数，**g2b 为底部阵列增益，不能当 total S2 gain**。通用 NR 校准拟合域约 6–90 keV，不能据此宣称 US2 的 sub-keV 核已齐备。

已提取的 Qy nominal/best-fit/±1σ 来自 [2] Fig.4，用作均值/校准核对；完整 $P_r(N_e,w\mid T)$、随漂移/位置变化的损失、single-electron 增益分布、width/ROI 选择及低能校准关联仍待官方资源/可复查模型。新版不给出没有证据的高斯宽度，也不设 c_i 来消除缺口。

[返回目录](#toc)

<a id="s6"></a>

## 6. Observable 与分箱

严格响应分析保留 run。原实验 US2 likelihood 在 `(Ne, S2 width)` 二维空间 [[2]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-2) 第 6 页；目标论文的一维核对使用 Ne edges=`[4,4.5,5,5.5,6,6.5,7,7.5,8]`，D=`[73,44,29,44,41,38,28,35]`，共 332。

新增后续官方 CSV [[10]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-10)：Run0=158、Run1=174 行；各自八箱为 `[38,21,14,19,18,17,14,17]` 和 `[35,23,15,25,23,21,14,18]`，相加与发表 D 一致。由于文件缺事件 ID 和不可变发布标签，不仅凭计数相同证明 2024 的完整事件集合相同；它们保持 `later_release_crosscheck`，二维 width 箱界也未从散点猜造。

[返回目录](#toc)

<a id="s7"></a>

## 7. Prediction folding

对各 run、各氙同位素独立进行真实谱到重建箱的折叠：

$$
\mu^{\rm sig}_{r\mathbf i}=\mathcal E_r\,t_{\rm yr}\sum_A n_A^{(t)}\int dT\int dE_\nu\,\frac{d\phi}{dE_\nu}\frac{d\sigma_A}{dT}P_{r\mathbf i}(T;\boldsymbol\eta). \tag{4}
$$

| 符号 | 定义/单位 | 来源与归属 |
|---|---|---|
| $\mathcal E_r$ | run 曝光，t·yr | 对应测量文献，不从 detector mass 再乘一次 |
| $t_{\rm yr}$ | yr 到秒转换，31557600 s/yr | 本版数值约定：365.25 d/yr；非额外实验活时间 |
| $n_A^{(t)}$ | nuclei/t | 式 (2)；天然组成暂作参考 |
| $d\sigma_A/dT$ | cm²/keVnr | 共享截面输出，独立核响应选择 |
| $P_{r\mathbf i}$ | 含选择的 response | 式 (3)，不能再乘效率/曝光 |
| $\mu^{\rm sig}$ | 预测信号 events/bin | 项目推导关系，无作者 c_i |

曝光参考总量：PandaX US2 1.04 t·yr，XENONnT 2024 3.51 t·yr，定位文献 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) Sec.III 及相应原测量。run 分解必须来自测量/对应版本，而非用更新模板发布中的 live time 替换。能量积分需要检验运动学域、网格收敛、阈值涨落及响应支撑外尾；不能用 c_i 拟合数值误差。

完整 Response 与作者简化模型的差异会真实影响预测。固定 c_i 是对特定参考谱的逐箱补偿，不能普遍替代会随 EFT 谱形变化的卷积。本版 $c_i$ 不属于输入字段。

[返回目录](#toc)

<a id="s8"></a>

## 8. Statistics 与背景

每箱总预测由信号和背景组成；独立泊松计数的比较为：

$$
\mu_{r\mathbf i}=\mu^{\rm sig}_{r\mathbf i}+\sum_k B^k_{r\mathbf i}, \tag{5}
$$

| 符号 | 定义/单位 | 输入与来源 |
|---|---|---|
| $\mu$ | 总预测，events/bin | 项目推导：同 run、同箱的信号与背景相加 |
| $\mu^{\rm sig}$ | 信号预测，events/bin | 式 (4) 的 response 折叠结果 |
| $B^k$ | 背景 k 的期望，events/bin | 本节下方的原图/官方模板；率模板先乘其对应曝光 |

$$
-2\ln\mathcal L=2\sum_{r,\mathbf i}\left[\mu_{r\mathbf i}-D_{r\mathbf i}+D_{r\mathbf i}\ln\frac{D_{r\mathbf i}}{\mu_{r\mathbf i}}\right]+\boldsymbol\eta^\mathsf{T}C_\eta^{-1}\boldsymbol\eta. \tag{6}
$$

| 符号 | 含义/单位 | 来源与限制 |
|---|---|---|
| $D$ | 未扣背景的观测，events/bin | 原论文黑点或官方事件直接统计 |
| $\mu$ | 总预测，events/bin | 式 (5)，与 D 使用相同分箱 |
| $B^k$ | 各背景组分期望，events/bin | 原文/官方模板各自标明 nominal 或 fitted，不混用 |
| $\boldsymbol\eta,C_\eta$ | nuisance 与协方差 | 按正式测量提供；缺失不补单位阵 |

式 (6) 表达本版拟议的响应统计接口，零观测箱按 $D\ln(D/\mu)=0$ 的极限处理。是否使用 Gaussian 先验、哪些变量相关及其覆盖，必须由实际来源确定；不宣称它已经完整复现合作组 PLR/toy-MC 构造。文献 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) 式 (17) 的简化 nuisance 只作 benchmark 方法对照。两实验联合时太阳通量为同一个物理量；若采用其 12% 理论约束，只加入一份共同通量约束。Fig.2 通量测量扫描的先验构造另行核对，不能把“参考误差已知”自动变成给待测通量加先验。

已有两个投影 B 版本：原实验 Fig.5 的 cathode/MD 是拟合后的堆叠分量，benchmark Fig.1 是再分析参考分量，均注明 `fitted/reference`。不能将其无条件当成独立 prefit B 并再次施加原始 prior。2D US2 的 prefit 模板、width binning 和完整 nuisance/morphing 仍缺。[[2]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-2) Table IV 的 selection/model 误差也不等于任意响应参数的协方差。

[返回目录](#toc)

<a id="s9"></a>

## 9. 数据清单与逐项出处

新增文件的逐项说明如下。旧 Qy/D/B 的完整行列映射另见 [数据 README](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/README.md>)。新文件 SHA256 集中保存在 [本次文件指纹与处理记录](<../../../../../../重构/20261106_Response_onboarding_v2/NEW_DATA.json>)，避免长哈希挤占阅读表格。

| 数据文件 | 来源与定位 | 操作 / 单位 |
|---|---|---|
| [8B 官网四列表](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/b8_bahcall1996_official.txt>) | [[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-4)；官网 b8spectrum.txt；全部四列 | 原件字节保留；MeV、MeV⁻¹ |
| [天然氙组成](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/xenon_natural_isotopes_nist_v2.txt>) | [[9]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-9)；NIST Xe 九个同位素行 | 网页中心值；原子质量 u、数丰度 |
| [PandaX Run0 事件](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run0_events.csv>) | [[10]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-10)；官方后续 run0_data.csv | 原件字节保留；Ne、Width，后者单位待核 |
| [PandaX Run1 事件](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run1_events.csv>) | [[10]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-10)；官方后续 run1_data.csv | 原件字节保留；Ne、Width，后者单位待核 |
| [PandaX 逐 run 计数](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/statistics/pandax_official_later_run_bins_v2.txt>) | [[10]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-10)；两份官方 CSV；4–8 electron 八箱 | 直接直方图；events/bin |
| [PandaX 校准参数](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/detector/pandax_response_calibration_2403.04239v2.json>) | [[6]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-6)；2403.04239v2，PDF p21 Table II | 逐项转录；10 个参数，单位见数据说明 |

此前提取的 Qy、D/B 和版本对照仍在原处，完整逐文件出处见 [既有数据说明](<../../../../../data/experiments/PandaX4T/PandaX4T_2024_US2/README.md>)；这些旧数值文件本次字节未变。新增 NPZ 是有文献定位的数值容器，不是正式 Experiment Package，不创建隐式资源绑定。

数据质量等级：官方原件=下载字节保留；直接数组提取=与源 HDF5 逐值一致；图线数字化=有坐标标定、图号和原节点；项目推导=公式和上游数据明确；来源/适用性未闭合=单独列明，不写成官方确认。

[返回目录](#toc)

<a id="s10"></a>

## 10. 缺失、验证与参考文献

PandaX：仍缺 US2 sub-keV、run-dependent 完整响应核/WS 参数及选取合同，缺二维 prefit B/精确 width edges/统计相关性。本次已取得的通用校准参数和 Qy 不自动填补这些缺口。

已明确且无需再问用户的决定：使用完整 Response；不引入 c_i；旧版保留；每个数据与参数严格附来源。科学缺失由执行者继续查证，不要求用户猜值。

验收分开登记：数据字节/shape/单位/归一化/来源映射、Markdown 文件链接与锚点、数学渲染；未完成的物理核验与 runtime 测试不写成 PASS。[本次补充与验收记录](<../../../../../../重构/20261106_Response_onboarding_v2/README.md>)保存旧版指纹、新文件清单、处理脚本和逐源哈希。

全部标准参考文献见 [编号参考文献 v2](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md>)。旧版不覆盖，本版为独立可审阅的新 onboarding，不等同于完整可运行 Package。

[返回目录](#toc)
