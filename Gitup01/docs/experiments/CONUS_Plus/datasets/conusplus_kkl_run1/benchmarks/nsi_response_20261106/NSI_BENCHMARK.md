# CONUS+ NSI benchmark v1（隔离候选，2026-11-06）

沿用现有项目流程、天然锗五同位素与Nuclear Response。本文逐节列出实际采用的输入、直接来源、推导、验证和未闭合事项。

<a id="report-toc"></a>

## 目录

- [单参数benchmark结果](#section-1)
- [前向输入与NSI映射来源](#section-2)
- [统计输入、公式与推断](#section-3)
- [上下误差敏感性](#section-4)
- [直接Slow与加速核验证](#section-5)
- [Fig.4二维benchmark](#section-6)
- [仍待核实与后续所需数据](#section-7)
- [复算、阶段与标准参考文献](#section-8)

<a id="section-1"></a>

## 单参数benchmark结果

| 耦合 | 本次1σ区间 | 论文Table II 1σ区间 | 最大端点差 |
| --- | --- | --- | --- |
| εᵘⱽₑₑ | [-0.036653, 0.025718] ∪ [0.348217, 0.410334] | [-0.037, 0.026] ∪ [0.348, 0.411] | 0.000666 |
| εᵈⱽₑₑ | [-0.033872, 0.023756] ∪ [0.321965, 0.379483] | [-0.034, 0.024] ∪ [0.322, 0.380] | 0.000517 |
| εᵘⱽₑμ | [-0.122640, 0.122640] | [-0.123, 0.123] | 0.000360 |
| εᵈⱽₑμ | [-0.113377, 0.113377] | [-0.114, 0.114] | 0.000623 |
| εᵘⱽₑτ | [-0.122640, 0.122640] | [-0.123, 0.123] | 0.000360 |
| εᵈⱽₑτ | [-0.113377, 0.113377] | [-0.114, 0.114] | 0.000623 |

SM点经α轮廓化后的χ²=7.366493276，α=0.014564760。对角NSI保留全部简并分支，eμ和eτ分别计算并核对相等。

![一维NSI谱线与区间](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_profiles_1d.png>)

[区间CSV](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_intervals.csv>) · [一维扫描CSV](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_scan_1d.csv>) · [19箱NSI事例谱](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_spectra_19bins.csv>)

外部区间直接来自 V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," Phys. Rev. D 111, 075025 (2025), doi:10.1103/PhysRevD.111.075025, arXiv:2501.17843v3. Table II，PDF p.13。[原文](<../../../../../../references/CONUS/2501.17843v3.pdf>)

[返回目录](#report-toc)

<a id="section-2"></a>

## 前向输入与NSI映射来源

| 输入／约定 | 实际数值与单位 | 直接依据、精确定位与核验范围 |
| --- | --- | --- |
| 矢量NSI | εqV=εqL+εqR，q=u,d，六个实数坐标 | 上述De Romeri等人论文Eqs.(7)–(9)，PDF pp.4–5；[原文](<../../../../../../references/CONUS/2501.17843v3.pdf>) |
| 到LEFT系数 | δC(6,1,q)=−√2 GF εqV，单位GeV⁻² | [项目parameters.py](<../../../../../../../cevns_pyeft/statistics/parameters.py>)::vector_nsi_to_np_wilson；按Eq.(7)投影至矢量夸克流 |
| SM | include_sm=True，sin²θW=0.23857，其他BSM=0 | [装配](<../../../../../../../examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/nsi_model.py>)，SM沿用同一参考；GF运行值来自固定项目常数 |
| 核响应与靶 | 天然Ge70/72/73/74/76，数丰度0.2057/0.2745/0.0775/0.3650/0.0773 | [数值配置](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>)，论文p.9；五个[核表key](<../../../../../../../data/responses/responses_all.json>) |
| 核数和质量 | 1kg库存；NIST原子质量用于核数，A u用于引擎运动学 | [库存](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/natural_ge_inventory.csv>)，实际执行装配为[sm_model.py](<../../../../../../../examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/sm_model.py>) |
| 源谱 | 10001行，0–10MeV；总通量1.5×10¹³ cm⁻²s⁻¹ | [完整源表](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/reactor_flux_default.csv>)，[逐列溯源](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/PROVENANCE_MAP.json>) |
| 曝光／探测器 | 1kg×119days；k=.162，σ0=20.38eVee，F=.1096，η=2.96eVee | 论文pp.8–10、Eqs.(29)–(31)；[配置](<../../../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json>) |
| 编译子空间 | 四个d=6算符，shape=(5,1,8,4,4,19) | [核文件](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_operator_kernel_161_641.npz>) 与 [编译记录](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/compile_summary.json>) |
| 真实积分网格 | 每核素161反冲点，Eν均匀641点并加源断点 | [实际Slow与Fast验证](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/validation.json>)；直接复用同一project Slow/compile_fast |

源、靶、探测器和原始来源状态沿用已固定SM输入，全部201个输入／代码文件由 [输入快照](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/nsi_response_20261106/INPUT_SNAPSHOT.json>)保存SHA256。核表原始多体计算链与低能32节点的Kopeikin原始数表对应仍待核实。 ν／反ν共用事例率kernel沿用既有Li2026约定，原文依据为G. Li等人，arXiv:2601.19883v2，PDF p.21、Eq.(92)后一段。

Flux的高能系数直接来自Th. A. Mueller et al., “Improved predictions of reactor antineutrino spectra,” Phys. Rev. C 83, 054615 (2011), doi:10.1103/PhysRevC.83.054615，Eq.(12)、Table VI、PDF p.13。[原文](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/1101.2663v3.pdf>)。低能32节点的直接材料为用户提供的未发表CONUS+笔记，Table2、PDF p.6，[材料副本](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/user_reference_CONUS.pdf>)。其所引用的V. I. Kopeikin, Phys. At. Nucl.75, 143–152 (2012), doi:10.1134/S1063778812020123，原始数表对应尚未核实。

靶库存使用NIST Physical Measurement Laboratory, “Atomic weights and isotopic compositions for germanium,” online table, accessed2026-11-06，各Ge同位素行。[数表快照](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/nist_ge_isotopic_masses.html>)。基本质量和Fermi常数采用NIST “2022 CODATA adjustment, complete listing”的对应行，实际引擎值保存在 [上一轮SM验证](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/sm_response_20261106/validation.json>)。

[返回目录](#report-toc)

<a id="section-3"></a>

## 统计输入、公式与推断

| 输入／处理 | 采用值与shape／单位 | 直接来源、核验和适用范围 |
| --- | --- | --- |
| 观测 | 19个signed excess，保留6个负值 | [统计输入CSV](<../../../../../../../data/benchmarks/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/statistics_input.csv>)，原文p.10 Fig.1黑点，矢量取点溯源在既有data/statistics目录 |
| 比较单位 | counts kg⁻¹(10eVee)⁻¹；19箱160–350eVee，宽10eVee | 同1kg119days预测，逐箱事件数数值等于本图单位纵值；单位转换只执行一次 |
| 主误差 | σi=(error_minus+error_plus)/2，19个正数 | 本次执行者选择，直接读取原取点上下误差后重算；全部数值见统计输入CSV |
| 误差敏感性 | 上下误差各独立作σi，分别重拟合 | [误差敏感性结果](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/error_sensitivity.json>)，这两套用于检查误差对称化影响 |
| χ² | 19箱独立高斯残差＋(α/.169)² | 论文Eq.(33)，PDF pp.9–10；[项目profile_gaussian_one_pull](<../../../../../../../cevns_pyeft/statistics/profiling.py>) |
| 累计归一化 | σα=0.169，α为无界实数高斯pull | 论文p.10；只按Eq.(33)作用于信号，不重改Flux或额外拟合全局输入归一化 |
| 协方差 | 采用Eq.(33)给出的对角形式 | 本次论文χ²比较所需输入已取得；未加入作者未提供的额外相关结构 |
| 单参数 | 每次只变1个实数ε，其余NSI=0；扫描[-1,1] | 与TableII单参数约束比较，寻找所有极小值并保留全部允许分支 |
| 一维阈值 | 1σ为Δχ²=1；90%为2.705543454095404 | TableII标注1σ；90%为χ²(df=1)的0.9分位数，数学派生 |
| 二维阈值 | 90%为Δχ²=4.605170185988092 | Fig.4标注90%；阈值由χ²(df=2)分位数派生 |
| 区间算法 | 4001扫描点定位，brentq根精度1e−12；2001点独立复查 | 项目推导算法，区间边界稳定容差5e−6，所有分支及局部极小值有记录 |

统计主张为基于 V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," Phys. Rev. D 111, 075025 (2025), doi:10.1103/PhysRevD.111.075025, arXiv:2501.17843v3. Eq.(33) 的近似论文benchmark。标称渐近Δχ²阈值用于对照，尚未用toys校准NSI边界、简并处的频率学覆盖率。本次NSI只涉及u/d夸克，按原文Fig.4采用CEνNS-only。

[返回目录](#report-toc)

<a id="section-4"></a>

## 上下误差敏感性

| 耦合 | 平均误差1σ | 固定下误差1σ | 固定上误差1σ |
| --- | --- | --- | --- |
| εᵘⱽₑₑ | [-0.036653, 0.025718] ∪ [0.348217, 0.410334] | [-0.036719, 0.025601] ∪ [0.348331, 0.410405] | [-0.036580, 0.025840] ∪ [0.348098, 0.410256] |
| εᵈⱽₑₑ | [-0.033872, 0.023756] ∪ [0.321965, 0.379483] | [-0.033934, 0.023648] ∪ [0.322072, 0.379547] | [-0.033806, 0.023869] ∪ [0.321854, 0.379414] |
| εᵘⱽₑμ | [-0.122640, 0.122640] | [-0.122762, 0.122762] | [-0.122508, 0.122508] |
| εᵈⱽₑμ | [-0.113377, 0.113377] | [-0.113489, 0.113489] | [-0.113255, 0.113255] |
| εᵘⱽₑτ | [-0.122640, 0.122640] | [-0.122762, 0.122762] | [-0.122508, 0.122508] |
| εᵈⱽₑτ | [-0.113377, 0.113377] | [-0.113489, 0.113489] | [-0.113255, 0.113255] |

[返回目录](#report-toc)

<a id="section-5"></a>

## 直接Slow与加速核验证

| 非零Slow点 | Slow总事例数 | 最大逐箱绝对差 | 最大逐箱相对差 |
| --- | --- | --- | --- |
| u_ee_005 | 80.238433222 | 4.974e-14 | 5.681e-15 |
| d_ee_034 | 139.835450837 | 1.066e-14 | 5.922e-16 |
| u_ee_cancellation | 0.216375166 | 8.363e-14 | 2.467e-12 |
| emu_u_010 | 192.157989417 | 2.842e-14 | 2.299e-15 |
| emu_complex_mixed | 185.406770457 | 4.619e-14 | 2.681e-15 |
| combined_real | 106.856155667 | 1.208e-13 | 5.028e-15 |

预定Slow/Fast条件为|ΔN|≤10⁻⁸+10⁻⁸|N|。同位素分量也逐箱核对。验证还覆盖SM恢复、复数跃迁、eμ/eτ、反号偶性、full/pair重建、60个多参数点、保存后加载、子空间外参数拒绝与曝光改变后的缓存失效。非零εuVee=.05的321→641能量网格最大逐箱变化为 0.152735%。

加速扫描的逐箱多项式来自现有已积分算符双线性核在明确NSI子空间的精确二次形式。其shape为每平面6×19，顺序为1,x,y,x²,xy,y²；并与原接口在60点直接核对。

[全部检查和实际数值](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/validation.json>) · [精确二次模板](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_quadratic_templates.npz>)

[返回目录](#report-toc)

<a id="section-6"></a>

## Fig.4二维benchmark

![二维NSI与原图比较](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/nsi_contours_2d.png>)

| 平面 | 原图非裁切顶点 | 本次Δχ²在原图边界中位数 | 范围 |
| --- | --- | --- | --- |
| diag_ud | 701 | 4.700733 | 4.634057–4.775110 |
| fc_ud | 359 | 4.660418 | 4.644898–4.688138 |
| ring_mu | 146 | 4.668054 | 4.640075–4.810917 |
| ring_tau | 146 | 4.668054 | 4.640075–4.810917 |

蓝色参考直接来自 V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," Phys. Rev. D 111, 075025 (2025), doi:10.1103/PhysRevD.111.075025, arXiv:2501.17843v3. Fig.4，PDF p.14。四组坐标按各图主要刻度校准，共7个轮廓多边形、1429个顶点。边界比较排除了原图面板边缘的裁切顶点，原图名义阈值为4.605170。该比较保留图形取点精度与模型差别。

[全部顶点CSV](<../../../../../../../data/benchmarks/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/benchmark/fig4_blue_polygons.csv>) · [直接出处及坐标校准](<../../../../../../../data/benchmarks/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/benchmark/REFERENCES_PROVENANCE.json>)

对本次显示轮廓的全部顶点重新计算了精确轮廓化χ²，501×501网格绘图插值的最大Δχ²偏差为 0.001310956。[逐面板插值检查](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/contour_rendering_checks.json>)

[返回目录](#report-toc)

<a id="section-7"></a>

## 仍待核实与后续所需数据

| 事项 | 已有内容 | 仍需什么 | 影响 |
| --- | --- | --- | --- |
| 原始低能谱 | 用户笔记32点和Kopeikin文献信息 | Kopeikin原数表／作者文件的逐点对应 | 原文数据来源认证 |
| Ge核响应 | 本地五核素数表、哈希与数值验证 | 原作者多体计算／生成转换脚本 | 正式Nuclear Response来源认证 |
| 作者数值统计包 | 论文取点、Eq.(33)、TableII与Fig4 | 原始19箱数表、误差处理和作者扫描数组／代码 | 更精确的论文复现和误差约定核对 |
| SM谱形 | 已知高能尾部与原图有差异 | 匹配原文Flux及形状因子设置并核对作者正向谱 | 当前NSI结果对论文差异的解释 |
| 正式基准冻结 | 候选P07/P08/P09数值与来源报告 | 对当前版本结果与统计选择的审阅 | 全部human_gate保持NOT_REVIEWED |

本次所选近似χ²所需数值已取得，SOURCE和TARGET上游原文来源保持PARTIAL。平均误差选择及其敏感性在同一版输出可见，后续更换误差只需重算统计，不改变已固定物理核。

[返回目录](#report-toc)

<a id="section-8"></a>

## 复算、阶段与标准参考文献

```powershell
.\run_nsi_benchmark.ps1
```

依次执行参考提取（首次）、直接Slow与现有系数核构建、区间与二维扫描、绘图和报告。[本次合同](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/nsi_response_20261106/NSI_CONTRACT.json>) 固定参数域与预定误差标准。[运行环境](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/nsi_response_20261106/ENVIRONMENT.json>) 保存依赖版本。

[逐输出溯源](<../../../../../../../outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/OUTPUT_PROVENANCE.json>) 保存文件列到数据、原文与算法的对应。[阶段记录](<../../../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmarks/nsi_response_20261106/phase_reports/README.md>) 保存P04、P05、P07–P10的实际交接与审核状态。

完整标准引文及上游资料链接沿用 [onboarding参考文献](<../../REFERENCES.md>)。本轮新增直接定位为基准论文Eqs.(7)–(9)、Eq.(33)、TableII、Fig.4。

[返回目录](#report-toc)
