# XENONnT 2024 Solar 8B — Response onboarding v2.0（新版本）

**版本：v2.0；日期：2026-11-06；方法：完整探测器 Response 折叠；状态：资料已补充，完整原实验适配仍为 PARTIAL。**

[精简版 v2](<experiment.physics.summary.v2.md>) · [用户资料 v2](<EXPERIMENT_USER_INPUT.v2.md>) · [标准参考文献](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md>) · [数据目录](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/README.md>) · [旧 onboarding（原位保留）](<../../../../../../../.experiment-auto-runs/cevns-threephase-20261105-high01/snapshot/docs/experiments/XENONnT/datasets/XENONnT_SolarB8/EXPERIMENT_USER_INPUT.md>)

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

实验输入以 [[3]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-3) 的早期太阳 8B 测量为身份依据，以 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) 的 Fig.1/2/4 为对照。新版采用 response 卷积，因模型不同，不宣称必须逐点重现作者含 c_i 的简化曲线。 范围固定为 SR0+SR1 的 37 个事件，不纳入 SR2。后续发布的 response 模板以 release2026 命名，数据身份与响应校准身份严格分开。

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

已补充文献 [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8) 的完整模板候选：每个 run 的 `probability` 数组轴为 `(tLy,tQy,energy,cs2,shadow,s1_bdt,s2_bdt)`，shape=`(7,7,46,3,3,3,3)`；energy=0.5…5.0 keV，每 0.1 keV 一点，tLy/tQy 各为 −3…3。每个原 HDF5 的 `/templates/template` 原样堆叠，未按箱宽再乘/除，也未重归一化为 1；总和保留检测效率。

模板内核由 2026 年发布版本生成，原文件 metadata 为 2026-06-06；B 模板为 2026-01-11。发布说明明确模板用于更新分析，而早期 run 的事件曾用于 2024 测量。这些数组是完整 Response 的可用**后续校准候选**，**不是已证明等同于 2024 原版的 kernel**。在 2024 严格复现中，该版本适用性保留为科学缺口；不自动把新核追溯应用旧数据。

计划的模板内插采用能量与 nuisance 域内的非负多线性权重；网格外拒绝外推。0.5–5 keV 之外必须做尾贡献界限或取得扩展核，不能直接令物理谱为零而不检查。上述是显式数值方案，尚未实现 Runtime。使用 full template 时不再另乘 g2、Qy 映射、效率或单独 smearing；文献 [[7]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-7) 的旧 Qy 只作模型来源/均值交叉检查。

发布 README 将模板关联到 [[14]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-14)，并将数据产品标为 CC-BY-4.0。使用时同时引用关联论文和文献 [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8) 的固定数据发布。

[返回目录](#toc)

<a id="s6"></a>

## 6. Observable 与分箱

保留两个 run 的四维空间 `(cS2, shadow quantile, S1 BDT score, S2 BDT score)`，每维 3 箱、每 run 81 箱 [[3]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-3) Fig.2 和 [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8) 的 `/bins/0…3`。新版已补齐所有四维事件与直方图，未只保留一维投影。

| run | cS2 edges（PE） | 三个 cS2 箱 D | 全部 D |
|---|---|---|---:|
| SR0 | `[90,170.161773681641,249.889739990234,500]` | `[5,3,1]` | 9 |
| SR1 | `[90,155.937850952148,232.292022705078,500]` | `[11,11,6]` | 28 |

各 run 按箱**序号**相加为 `[16,14,7]`，不是在一套公共 cS2 边界下混合事件。其余三维精确 edges 保存在各 NPZ `bin_edges_1/2/3`。论文 [1] 正文 120PE 与绘图/官方 binning 90PE 的关系仍单独记录；原 CSV 包含一个 118.58632PE 事件，不擅自删点以制造 120PE 样本。

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

本次补充的 2026 B 模板 AC、ER 单位为 `/t/y/bin`，neutron 有 7×7 nuisance 网格；不得与 2024 plot B 的 events/bin 直接相加。必须乘该模板对应的曝光才能得到 B；2024 的对应版本未确认前，只作为版本隔离候选。已新增 4D D，但更新模板与早期 D 的完整 likelihood 一致性尚未确认。[[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8) 的 tLy/tQy 节点是模型变化坐标，不自动意味着每个坐标都有独立 $N(0,1)$ prior。

[返回目录](#toc)

<a id="s9"></a>

## 9. 数据清单与逐项出处

新增文件的逐项说明如下。旧 Qy/D/B 的完整行列映射另见 [数据 README](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/README.md>)。新文件 SHA256 集中保存在 [本次文件指纹与处理记录](<../../../../../../重构/20261106_Response_onboarding_v2/NEW_DATA.json>)，避免长哈希挤占阅读表格。

| 数据文件 | 来源与定位 | 操作 / 单位 |
|---|---|---|
| [8B 官网四列表](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/b8_bahcall1996_official.txt>) | [[4]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-4)；官网 b8spectrum.txt；全部四列 | 原件字节保留；MeV、MeV⁻¹ |
| [天然氙组成](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/xenon_natural_isotopes_nist_v2.txt>) | [[9]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-9)；NIST Xe 九个同位素行 | 网页中心值；原子质量 u、数丰度 |
| [SR0 响应网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr0_response_release2026_v2.npz>) | [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8)；templates/sr0/mono/*；原 HDF5 数组 | 无损堆叠；概率无量纲，已含选择 |
| [SR0 背景网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_background_release2026_v2.npz>) | [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8)；templates/sr0/ac, er, rg/* | 无损提取；events/(t yr bin)，未乘曝光 |
| [SR0 四维观测](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr0_observed_4d_v2.npz>) | [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8)；data/sr0.csv；对应 binning YAML | 完整事件与直方图；events/bin |
| [SR1 响应网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/detector/xenonnt_sr1_response_release2026_v2.npz>) | [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8)；templates/sr1/mono/*；原 HDF5 数组 | 无损堆叠；概率无量纲，已含选择 |
| [SR1 背景网格](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_background_release2026_v2.npz>) | [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8)；templates/sr1/ac, er, rg/* | 无损提取；events/(t yr bin)，未乘曝光 |
| [SR1 四维观测](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/statistics/xenonnt_sr1_observed_4d_v2.npz>) | [[8]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-8)；data/sr1.csv；对应 binning YAML | 完整事件与直方图；events/bin |

此前提取的 Qy、D/B 和版本对照仍在原处，完整逐文件出处见 [既有数据说明](<../../../../../data/experiments/XENONnT/XENONnT_2024_SolarB8/README.md>)；这些旧数值文件本次字节未变。新增 NPZ 是有文献定位的数值容器，不是正式 Experiment Package，不创建隐式资源绑定。

数据质量等级：官方原件=下载字节保留；直接数组提取=与源 HDF5 逐值一致；图线数字化=有坐标标定、图号和原节点；项目推导=公式和上游数据明确；来源/适用性未闭合=单独列明，不写成官方确认。

[返回目录](#toc)

<a id="s10"></a>

## 10. 缺失、验证与参考文献

XENONnT：完整后续 Response 和 B 已能回读，2024 原版响应/后续校准追溯适用性尚未证明；run 曝光、响应支撑外贡献、nuisance prior/covariance 和官方推断校准仍需对应版本证据。

已明确且无需再问用户的决定：使用完整 Response；不引入 c_i；旧版保留；每个数据与参数严格附来源。科学缺失由执行者继续查证，不要求用户猜值。

验收分开登记：数据字节/shape/单位/归一化/来源映射、Markdown 文件链接与锚点、数学渲染；未完成的物理核验与 runtime 测试不写成 PASS。[本次补充与验收记录](<../../../../../../重构/20261106_Response_onboarding_v2/README.md>)保存旧版指纹、新文件清单、处理脚本和逐源哈希。

全部标准参考文献见 [编号参考文献 v2](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md>)。旧版不覆盖，本版为独立可审阅的新 onboarding，不等同于完整可运行 Package。

[返回目录](#toc)
