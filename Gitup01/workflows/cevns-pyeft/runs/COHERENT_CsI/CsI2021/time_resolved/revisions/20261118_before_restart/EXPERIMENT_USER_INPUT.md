# CsI2021 时间分辨分析 用户资料与补充记录

[详细版](<experiment.physics.md>) · [精简版](<experiment.physics.summary.md>) · [用户资料](<EXPERIMENT_USER_INPUT.md>) · [来源P00](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P00_SOURCE_REGISTER.yaml>) · [证据P01](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P01_EVIDENCE_LEDGER.yaml>) · [缺失P02](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P02_MISSING_AND_CONFLICTS.md>) · [配置P03](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/P03_PHYSICS_CONTRACT.yaml>) · [Benchmark旧诊断与范围](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/README.md>) · [完整数据与生成入口](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/README.md>)

**修订草稿r2+timing-diagnostics-20261117，2026-11-17，DRAFT/PARTIAL。** 已取得官方事件、背景、ROOT、校准系数及原data中的Cs/I核响应。用户已明确选择直接调用原核表，本次资源复用输入就绪。外部作者生成链仅作未核实的补充事项。BRN/NIN绝对归一及严格论文配置等价仍待补，外部benchmark继续BLOCKED。

<a id="report-toc"></a>

## 目录

- [H0 目标与已记录选择](#input-target)
- [H1 已取得材料与本轮新增](#input-materials)
- [H2 实际数值及来源](#input-values)
- [来源缺口与影响](#input-gaps)
- [H3 补充问答与当前处理](#input-qa)
- [下一步输入交接](#input-handoff)
- [标准来源及核验范围](#input-sources)

<a id="input-target"></a>

## H0 目标与已记录选择

CsI2021_time_9x11，使用用户指定RESPONSE，保留两套独立benchmark。用户选项登记在DECISION_LOG，核响应外部来源另行审核。

[返回目录](#report-toc)

<a id="input-materials"></a>

## H1 已取得材料与本轮新增

- 按用户补充直接绑定原data/responses/responses_all.json；外部生成链不再阻断本次原表复用
- 将旧P03中的Helm候选改为用户指定RESPONSE，并展开全部Cs/I数值数组
- 取得作者固定提交的Elastic密度矩阵及Mu2e_NRET源码，保留未证实的转换对应
- 将9份官方数值附件、校准原文、NIST/PDG原表并入主项目并给出页行定位
- 显式列出14.57/14.6kg及−0.3333/−0.333322等旧诊断差异
- 详细版、精简版、用户资料、P02和交接表从本套记录重生成
- 2026-11-17新增可选时间诊断：默认0ns不变；信号/BRN/NIN同步源平移、固定观测效率和零位移分母；原生SM与KN分开重算

[返回目录](#report-toc)

<a id="input-values"></a>

## H2 实际数值及来源

| 输入与数值状态 | 实际数值或数组范围 | 单位 | 完整数值文件与范围 | 直接出处及定位 | 核验范围与适用性 |
|---|---|---|---|---|---|
| 累计POT `C_POT` 来源已提取；本稿候选 | 3.198e+23 | POT | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines76–81 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 每味每POT产额 `C_YIELD` 来源已提取；本稿候选 | 0.0848 | neutrinos/flavor/POT | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines78–81；10%误差 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 基线 `C_L` 来源已提取；本稿候选 | 19.3 | m | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 lines78–81 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 论文探测器质量 `C_MASS` 来源已提取；本稿候选 | 14.6 | kg | 标量或定义，见直接出处 | [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) Supplement p2 line81；2211 p12 Eq28段落 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 实际调用资源与核素映射 `C_RESOURCE_BINDING` 用户已确认；本稿候选 | {"path": "data/responses/responses_all.json", "reader": "cevns_pyeft.nuclear.response.ResponseDB", "nucleus_keys": {"Cs133": "Cs133", "I127": "I"}} | 1 | 标量或定义，见直接出处 | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) 原JSON nuclei.Cs133和nuclei.I；D_LOCAL_RESPONSE | 完整原表为调用权威；提取NPZ只用于查看及逐值一致性核验；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| Cs133_M系数 `C_W_Cs133_M` 来源已提取；用户选定本地资源 | shape=[2, 2, 11], k=[0, 10]; c_pp[0:3]=[3024.998274020381, -11027.633404691845, 15552.131264975062] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.Cs133.responses.M key=Cs133_M shape=[2, 2, 11] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.Cs133.responses.M；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| I127_M系数 `C_W_I127_M` 来源已提取；用户选定本地资源 | shape=[2, 2, 11], k=[0, 10]; c_pp[0:3]=[2808.9995665607275, -10034.66474862081, 13985.083771812386] | dimensionless coefficients under local convention | [responses_all.json](<../../../../../data/responses/responses_all.json>) · [逐值提取供核对](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/nuclear_response_CsI.npz>) json_key=nuclei.I.responses.M key=I127_M shape=[2, 2, 11] | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) nuclei.I.responses.M；全部2×2×K系数逐值复制 | 直接来源是原data核表，未冒充作者原文。八通道均保留；SigmaPDelta粒子响应为0的实施说明另记；数值资源已取得；原表逐值回读；直接来源为本地原data；外部上游待核（可选）；提取值完全一致；本次原表复用已选 |
| 可选外部作者导出链审计 `C_W_CONVERSION` MISSING；可选外部审计 | **MISSING** | 1 | 标量或定义，见直接出处 | [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_MU2E](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Mu2e_NRET/v2/mathematica/mu2elib_v2.wl>) 缺少当前聚合JSON的原始导出脚本/Notebook、版本、基底/归一化逐项对照 | 用户已明确接受原data直接调用。外部作者溯源仍未闭合，仅限制外部来源认证，不阻断本次本地资源复用；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| nominal淬灭多项式系数 `C_QF` 来源已提取；本稿候选 | [0.0554628, 4.30681, -111.707, 840.384] | [1,MeV^-1,MeV^-2,MeV^-3] | 标量或定义，见直接出处 | [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) scintRespCoefficients.txt line7；2211 p12 Eqs30–31前；输入MeVnr，输出MeVee | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| QF拟合适用域 `C_QF_DOMAIN` 来源已提取；本稿候选 | [2, 70] | keVnr | 标量或定义，见直接出处 | [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) Sec8，PDF p23/印刷p21 Fitting approach | 校准点范围3–63keVnr，与拟合域分别记录；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 官方nominal能量效率系数 `C_EFF` 来源已提取；本稿候选 | [1.32045, 0.285979, 10.8646, -0.333322] | a,d dimensionless; b PE^-1; c PE | 标量或定义，见直接出处 | [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) effCoefficients.txt line7，公式与x=PE见头部line1–4 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 旧程序效率常数项 `C_EFF_LEGACY` 存在差异；旧诊断 | -0.3333 | 1 | 标量或定义，见直接出处 | [S_LEGACY_EFF](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/slow_counts_csi2021.py>) · [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) 旧slow_counts_csi2021.py CsI2021EfficiencyParams.d；官方line7为−0.333322 | 旧数值结果使用舍入值；本草稿nominal采用官方−0.333322，旧拟合不是本草稿同条件结果；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| PE边界 `C_PE` 项目推导；本稿候选 | [0.0, 8.0, 12.0, 16.0, 20.0, 24.0, 32.0, 40.0, 48.0, 60.0] | PE | 标量或定义，见直接出处 | [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) · [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) D_PE；Supplement p5 Fig2水平误差棒 | 指定重建值；尚未取得作者机器数字边界表；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| 时间边界 `C_TIME` 来源已提取；本稿候选 | [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 2.0, 4.0, 6.0] | us | 标量或定义，见直接出处 | [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) p35 Fig18全部十一面板标签 | 已核直接材料中的本条数值/单位及所列定位；核验范围限于该项，不认证未列出的上游关系；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 |
| C逐箱原始计数 `C_OBS` 项目推导；本稿候选 | 9×11，全部数值见详细版Observable矩阵及完整数据文件；sum=1578 | events/bin | [analysis_inputs.npz](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/analysis_inputs.npz>) · [完整99箱观测CSV](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/observed_99bins.csv>) key=C_counts shape=[9, 11] | [S_dataBeamOnC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnC.txt>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) 原始文件全部8916行PE,time_us；按C_PE/C_TIME重分箱，轴顺序[PE,time] | 总计1578，为官方逐事件表的项目重分箱值；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_PE,C_TIME,C_ENDPOINT_RULE |
| AC逐箱原始计数 `C_CONTROL` 项目推导；本稿候选 | 9×11，全部数值见详细版Observable矩阵及完整数据文件；sum=1295 | events/bin | [analysis_inputs.npz](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/analysis_inputs.npz>) · [完整99箱观测CSV](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/data/observed_99bins.csv>) key=AC_counts shape=[9, 11] | [S_dataBeamOnAC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnAC.txt>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) 原始文件全部8532行PE,time_us；按C_PE/C_TIME重分箱，轴顺序[PE,time] | 总计1295，为官方逐事件表的项目重分箱值；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_PE,C_TIME,C_ENDPOINT_RULE |
| BRN/NIN全域概率候选效率后总数 `C_BG_GAP` 项目推导；本稿候选 | [18.309633271138438, 5.1789999582711825] | events | 标量或定义，见直接出处 | [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>) background_audit；分母为各PE表全域和，未用prior作缩放目标 | 18.30963327/5.17899996与18.4/5.6不闭合；时间效率前口径仍待发布者说明；数值资源已取得；直接材料已读；上游核验见P00；适用性待审 输入=C_BRN_PE,C_BRN_TIME,C_NIN_PE,C_NIN_TIME,C_TIME_EFF,C_PRIORS |

[返回目录](#report-toc)

<a id="input-gaps"></a>

## 来源缺口与影响

| 问题 | 已有数据 | 尚缺数据/溯源 | 影响及当前状态 |
|---|---|---|---|
| G_NUCLEAR RESPONSE原表复用与可选外部生成链 | 本地Cs/I全部16个通道数组、作者Elastic密度矩阵和Mu2e_NRET代码已取得 | 本次直接调用原data已获用户明确选择；外部导出Notebook/版本仍可补充，只影响作者来源认证 | LOCAL_REUSE_READY；外部作者来源认证 |
| G_BG BRN/NIN绝对归一与时间效率 | 官方四个表、曝光和两个效率作用域均已取得，候选算法及差额已回读 | 作者明确PE概率归一、Trec绝对归一和TableI在时间效率前/后的口径 | BLOCKED；P09论文统计组成,P10外部benchmark |
| G_THEORY 原生Interaction/Matching与论文定义 | 原生代码可读取，G_F和质量常数已追到NIST/PDG，弱角两个配置已分列 | 按所选SM/LEFT范围完成核子与匹配数值到原文式及单位的逐项对应；此项是未完成审计，不能写成数值文件不存在 | PARTIAL；P04共享理论适用性,同模型外部比较 |
| G_CONFIG 旧诊断与本草稿输入差异 | 统一14.6kg/官方效率/解析DAR谱的原生SM353.465609及全支撑329.016423已生成；20261117高网格逐箱复核一致 | 同条件本地数值已完成；作者模型/时钟/背景口径等价仍依赖G_CLOCK/G_BG/G_THEORY，不由数值复核认证 | PARTIAL；同条件数值比较 |
| G_PE PE边界原始数字表 | 用户指定边界、Fig2图示和原事件重分箱 | 严格作者边界复现仍需机器边界表或作者配置；当前保留重建标记 | PROJECT_DERIVED；精确作者分箱声称 |
| G_RADIUS 2211半径nuisance与RESPONSE | 原文5%约束及当前固定核结构 | 有来源并经审核的RESPONSE半径变形映射，或明确固定半径的不同主张 | BLOCKED；严格2211七nuisance复现 |
| G_QF QF范围外贡献 | 2–70keVnr原始拟合域、当前域保护与旧低反冲延拓诊断 | 完整ROOT高能尾的范围外响应及小反nu_e绝对源权重，若以后选择该完整源 | PARTIAL；完整ROOT源的全反冲预测 |
| G_CLOCK ROOT时钟起点与prompt νμ时间形状 | 0与+75ns诊断、固定观测窗口/效率的实现及交接包测试；ROOT时间边缘保持原样 | 发布者的ROOT时钟起点、onset定义和作者逐分量时间模板；不能把19.3m/c自动再加一次 | PARTIAL；官方时间零点认定,prompt逐箱作者复现 |
| G_FIG1 论文图形与正文积分的口径 | 已核验原始矢量图与主论文内嵌几何一致；图形信号积分约312.59；截图proxy不作权威 | 作者原始模板解释Fig.1可见曲线与正文306±20、PE/time残差积分的差别 | PARTIAL；论文图精确总率复现,逐味实验显著性 |

[返回目录](#report-toc)

<a id="input-qa"></a>

## H3 补充问答与当前处理

询问了原始导出脚本或作者数据包位置后，用户明确答复“response本来就可以直接去调用原始的 data中的response”。已回填DECISION_LOG的D_LOCAL_RESPONSE，更新P00/P01/P03并重新生成本版。当前核表按原data直接调用，提取NPZ仅供阅读核验。作者公开密度矩阵和源码保留为可选上游材料，尚未证实的外部对应关系继续如实标注。

[返回目录](#report-toc)

<a id="input-handoff"></a>

## 下一步输入交接

| 下一步能力 | 当前状态 | 必需输入与出处 | 实际下一步 |
|---|---|---|---|
| P04原有RESPONSE资源复用 | LOCAL_RESOURCE_READY | C_RESOURCE_BINDING USER_CONFIRMED [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>); C_W_Cs133_M SOURCE_EXTRACTED [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>); C_W_I127_M SOURCE_EXTRACTED [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) | 通过ResponseDB直接加载原data核表，沿原基底/单位约定使用 |
| P06 nominal探测器响应准备 | DRAFT_INPUTS_PRESENT | C_QF SOURCE_EXTRACTED [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>); C_QF_DOMAIN SOURCE_EXTRACTED [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>); C_GAMMA SOURCE_EXTRACTED [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>); C_EFF SOURCE_EXTRACTED [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>); C_TIME_EFF SOURCE_EXTRACTED [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) | 按官方nominal系数核对实现，保留systematic标签冲突 |
| P07下一轮逐箱预测准备 | INPUTS_PRESENT_CONFIG_REVIEW | C_RESOURCE_BINDING USER_CONFIRMED [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>); C_SOURCE_CHOICE PROJECT_DERIVED [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) · [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>); C_DENOM PROJECT_DERIVED [S_TIME_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/time_acceptance.py>) · [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) | 复用原核表和预测入口，以明确的14.6kg/官方效率及时间口径生成同条件结果 |
| P09论文统计 | BLOCKED | C_BG_GAP PROJECT_DERIVED [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>); C_RADIUS SOURCE_EXTRACTED [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) | 闭合背景归一，分别声明固定半径诊断和完整论文nuisance |
| P10外部benchmark | BLOCKED | C_BG_GAP PROJECT_DERIVED [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>); C_RADIUS SOURCE_EXTRACTED [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) | 分别验收用户选定RESPONSE诊断和原论文模型，闭合背景与配置差异 |

[返回目录](#report-toc)

<a id="input-sources"></a>

## 本章标准来源及核验范围

- [S_2211](<../../../../references/COHERENT/2211.11905v2.pdf>) V. De Romeri et al., Physics implications of a combined analysis of COHERENT CsI and LAr data, JHEP 04 (2023) 035, arXiv:2211.11905v2. p3、p12–14、p33 Table II、p35 Fig.18 已核。 [原始网址](https://arxiv.org/abs/2211.11905v2)
- [S_AUDIT](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/input_resolution.json>) Project-generated CsI input-resolution audit, 2026-11-06, selected legacy260929 checkout. Numerical diagnostic with unresolved primary nuclear provenance. 原始输出已回读；其186项测试属于旧目录工程验证，核响应上游缺口传递到物理解释。
- [S_AUDIT_CODE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/tools/resolve_input_issues.py>) Project resolve_input_issues.py, native Response numerical diagnostic and recorded input transformations,2026-11-06. 算法和文件字节已保留；其余旧共享代码按原SHA引用。
- [S_DECISION](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/DECISION_LOG.json>) User decisions transcribed from this conversation,2026-11-06. 仅记录实际用户选项，不将其视作外部事实核验。
- [S_LEGACY_EFF](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/evidence/legacy_resolution/code/legacy/slow_counts_csi2021.py>) Project legacy CsI implementation, legacy/slow_counts_csi2021.py, snapshot2026-11-06. 旧效率参数及非负裁剪的直接代码，属于项目实施依据，外部科学来源另记。
- [S_LOCAL_W](<../../../../../data/responses/responses_all.json>) CEvNS-pyEFT project, local aggregated responses_all.json, format Mu2eNRET_ResponseW_v1, original export provenance unresolved. 用户明确选择直接复用原data核表；Cs133/I八通道已读、逐值提取；现读码的单位/基底约定已核。外部作者生成链仍未核实，不是本次原表复用前置。
- [S_MU2E](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/Mu2e_NRET/v2/mathematica/mu2elib_v2.wl>) Berkeley Electroweak Physics, Mu2e_NRET v2/mathematica/mu2elib_v2.wl, commit 15bef514375298b57d9b07852870be3c408c2b19; W. C. Haxton et al., Phys. Rev. C 107, 035504 (2023), DOI 10.1103/PhysRevC.107.035504. 作者代码和README引文已取得；尚未证明当前JSON由此版本生成。 [原始网址](https://github.com/Berkeley-Electroweak-Physics/Mu2e_NRET/blob/15bef514375298b57d9b07852870be3c408c2b19/v2/mathematica/mu2elib_v2.wl)
- [S_PREPARE](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/prepare_records.py>) Project onboarding data-reading and derivation script, prepare_records.py,2026-11-06. 本次提取/直方图/数组逐值核对算法，可重跑。
- [S_QF_PAPER](<../../../../references/COHERENT/2111.02477v2.pdf>) COHERENT Collaboration, Measurement of scintillation response of CsI[Na] to low-energy nuclear recoils by COHERENT, JINST 17 (2022) P10034, arXiv:2111.02477v2. Sec.8，PDF p23/印刷p21 的2–70keV拟合域与式(8.1)已核。 [原始网址](https://arxiv.org/abs/2111.02477v2)
- [S_SUP](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) COHERENT Collaboration, Supplemental Material to Phys. Rev. Lett. 129, 081801 (2022), 2110.07730v2 ancillary. p2–3 参数与背景说明、p5 Fig.2、p7 Table I 已读。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf)
- [S_dataBeamOnAC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnAC.txt>) COHERENT Collaboration, dataBeamOnAC.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/dataBeamOnAC.txt)
- [S_dataBeamOnC](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/dataBeamOnC.txt>) COHERENT Collaboration, dataBeamOnC.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/dataBeamOnC.txt)
- [S_effCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/effCoefficients.txt>) COHERENT Collaboration, effCoefficients.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/effCoefficients.txt)
- [S_scintRespCoefficients](<../../../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/official/scintRespCoefficients.txt>) COHERENT Collaboration, scintRespCoefficients.txt, arXiv:2110.07730v2 ancillary data release. 实际文件已读取，SHA与此前官方下载核验一致；适用性与变换逐claim登记。 [原始网址](https://arxiv.org/src/2110.07730v2/anc/scintRespCoefficients.txt)

[返回目录](#report-toc)


## 2026-11-17 νμ时间诊断补充（默认保持）

默认 Δt=0 ns，注量口径 `reference_window`，中子模式 `raw`。新增控制不授予论文等价、时钟校准或拟合接受。

对完整支撑域归一化的时间源 $h_f$，使用 $W_{fj}(\delta)=\int_{t_j}^{t_{j+1}}h_f(t-\delta)\epsilon_T(t)dt/q_f$；$q_f=\int_0^6h_f(t)dt$ 固定为零位移值。`full_support` 模式的分母为1。两模式使用相同数值η，是不同注量口径的对照，不能直接删除 `/q` 当作物理修复。

正位移使源晚到；观测箱及εT(t_rec)固定。信号和BRN/NIN同步平移，SSB、观测C/AC及计数误差不变。中子归一化分母同样锚定零位移，平移后不拉回固定总数。

| 中子模式 | 明确约定 |
|---|---|
| raw（默认） | 原始官方PE×Trec表，零位移约27.423763/6.908565事件 |
| prior_posteff | 零位移分析窗、时间效率后18.4/5.6事件 |
| bestfit_posteff | 零位移效率后17.3/5.5事件；仅总数控制，不是完整论文最佳拟合模板 |
| prior_preeff | 零位移时间效率前18.4/5.6事件 |

后三者是独立归一化解释；现有证据尚不能唯一确定论文实现。+75ns为诊断候选，不能据此断定ROOT读错、遗漏飞行时间或已确定作者onset。主线原生SM/RESPONSE保持；KN是独立对照，均未拟合或逐味缩放。

原生SM参考窗353.465609、全支撑329.016423，相差24.449186事件；KN参考窗333.113488，+75ns约331.266392。341是不同模型/口径的论文SM参考，不作为调参目标。原生二维ROOT联合源的完整等价未验证。

论文对照采用经主论文内嵌几何核验的原作者矢量图，图中CEνNS积分约312.59，与正文306±20的差别保留；每味分量是论文模型曲线，并非独立逐味测量。截图proxy的νe≈89.23及强制总数不能用于科学定标。

直接材料：[用户README](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/README.md>) · [交接说明](<../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/HANDOFF_PROMPT.md>)。

实际入口：[时间/中子适配器](<../../../../../examples/COHERENT_CsI/time_resolved_common/timing_diagnostics.py>) · [主线计算入口（已撤下）](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_benchmark.py>) · [复算与新图生成器（已撤下）](<../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py>) · [本次结果](<../../../../../outputs/csi2021_timing_diagnostics_20261117/README.md>)。
