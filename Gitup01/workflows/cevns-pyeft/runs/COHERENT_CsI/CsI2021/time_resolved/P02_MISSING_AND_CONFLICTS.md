# P02 CsI2021时间分析缺失与冲突

修订草稿r3-onboarding-restart-20261118，2026-11-18。对应同一P00/P01/P03。原data核表复用已获用户选择，外部作者生成链不作为本次复用阻断。

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
| G_EQ75 共享RESPONSE装配与源论文式75对应 | 论文p15/18/19原式、当前amplitude/responses代码及Cs/I实际核表可查 | 核实q²/mN²、-2q/mN、4π/(2J+1)、np/iso归一及DeltaSigma干涉，不通过计数拟合选约定 | BLOCKED；P04/P05物理接受,P07新权威Slow |
| G_FLUENCE_SCOPE POT总注量与0–6us时间归一解释 | η由POT/产额/距离计算；两种数值口径均已知 | H3明确采用的注量定义与原文依据；不能按结果接近341选择 | BLOCKED；P03源合同接受,P07总率解释 |
| G_TRUNCATION 一体流近似与遗漏两体流 | 2601.19883v2 p12-13功率计数、p30明确数值仅一体流 | 本轮先明确一体流主张及截断误差未知；若要两体流须另有电流与核矩阵元，不能用非M占比当误差 | PARTIAL；完整核理论精度声称 |

| 下一步能力 | 当前状态 | 必需输入与出处 | 实际下一步 |
|---|---|---|---|
| P04原有RESPONSE资源复用 | LOCAL_RESOURCE_READY | C_RESOURCE_BINDING USER_CONFIRMED [S_LOCAL_W](<../../../../../../data/responses/responses_all.json>) · [S_DECISION](<DECISION_LOG.json>); C_W_Cs133_M SOURCE_EXTRACTED [S_LOCAL_W](<../../../../../../data/responses/responses_all.json>) · [S_PREPARE](<prepare_records.py>); C_W_I127_M SOURCE_EXTRACTED [S_LOCAL_W](<../../../../../../data/responses/responses_all.json>) · [S_PREPARE](<prepare_records.py>) | 通过ResponseDB直接加载原data核表，沿原基底/单位约定使用 |
| P06 nominal探测器响应准备 | DRAFT_INPUTS_PRESENT | C_QF SOURCE_EXTRACTED [S_scintRespCoefficients](<sources/official/scintRespCoefficients.txt>) · [S_2211](<../../../../../../docs/references/COHERENT/2211.11905v2.pdf>); C_QF_DOMAIN SOURCE_EXTRACTED [S_QF_PAPER](<../../../../../../docs/references/COHERENT/2111.02477v2.pdf>); C_GAMMA SOURCE_EXTRACTED [S_SUP](<sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../../../docs/references/COHERENT/2211.11905v2.pdf>); C_EFF SOURCE_EXTRACTED [S_effCoefficients](<sources/official/effCoefficients.txt>); C_TIME_EFF SOURCE_EXTRACTED [S_SUP](<sources/official/Paper_CEvNSCsI_FullDataset_SupMaterials.pdf>) · [S_2211](<../../../../../../docs/references/COHERENT/2211.11905v2.pdf>) | 按官方nominal系数核对实现，保留systematic标签冲突 |
| P07下一轮逐箱预测准备 | BLOCKED_BY_CURRENT_PHYSICS_REVIEW | C_RESOURCE_BINDING USER_CONFIRMED [S_LOCAL_W](<../../../../../../data/responses/responses_all.json>) · [S_DECISION](<DECISION_LOG.json>); C_SOURCE_CHOICE PROJECT_DERIVED [S_2211](<../../../../../../docs/references/COHERENT/2211.11905v2.pdf>) · [S_DECISION](<DECISION_LOG.json>); C_DENOM PROJECT_DERIVED [S_TIME_CODE](<evidence/legacy_resolution/code/time_acceptance.py>) · [S_2211](<../../../../../../docs/references/COHERENT/2211.11905v2.pdf>) | 先完成H3和P04/P05对应审核，再确定单一阶段计算入口并运行P07 |
| P09论文统计 | BLOCKED | C_BG_GAP PROJECT_DERIVED [S_AUDIT](<evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<evidence/legacy_resolution/code/tools/resolve_input_issues.py>); C_RADIUS SOURCE_EXTRACTED [S_2211](<../../../../../../docs/references/COHERENT/2211.11905v2.pdf>) | 闭合背景归一，分别声明固定半径诊断和完整论文nuisance |
| P10外部benchmark | NOT_RUN_FOR_R3 | C_BG_GAP PROJECT_DERIVED [S_AUDIT](<evidence/legacy_resolution/input_resolution.json>) · [S_AUDIT_CODE](<evidence/legacy_resolution/code/tools/resolve_input_issues.py>); C_RADIUS SOURCE_EXTRACTED [S_2211](<../../../../../../docs/references/COHERENT/2211.11905v2.pdf>) | 按r3声明的能力验收；不继承旧诊断PASS |

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

直接材料：[用户README](<../../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/README.md>) · [交接说明](<../../../../../../../重构/2026-11-17 核心修改代码集/2026-11-17 nu mu/HANDOFF_PROMPT.md>)。

实际入口：[时间/中子适配器](<../../../../../../examples/COHERENT_CsI/time_resolved_common/timing_diagnostics.py>) · [历史入口（已撤下）](<../../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_benchmark.py>) · [历史诊断代码（已撤下）](<../../../../../../../重构/20261118_CsI2021_onboarding_restart/retired_entries/run_timing_diagnostics.py>) · [本次结果](<../../../../../../outputs/csi2021_timing_diagnostics_20261117/README.md>)。

## r3重新onboarding：当前审阅范围

**同一CsI2021_time_9x11；此版是物理配置草稿，未进入新的正式计数阶段。** 三个并列入口已撤下；旧353.465609及+75ns等结果仅作历史诊断，不是本轮已接受Slow。

| 独立维度 | 当前候选/资源 | 审核状态 |
|---|---|---|
| Interaction | 原生SM；描述符li2026_legacy | DRAFT，待P04 |
| Nuclear structure | 用户选定原RESPONSE，Cs133/I，np基底 | 原表复用选择保留；外部生成等价待核 |
| Kinematics/Cross-section | 现有elastic_neutrino_nucleus_v1 / Li2026LegacyInteraction | 式75装配与核表归一需P04/P05核对 |
| Detector | 14.6kg；QF→Gamma→PE效率→时间接受；T≥2keVnr候选 | 参数已取得，适用域/低反冲截断待P06复审 |
| Time source | 解析DAR能谱×ROOT时间边缘；0ns | +75ns仅历史对照，官方时钟未验证 |
| Fluence | η=5.793617637932339e14 cm⁻²/味 | full_support与reference_window含义需H3确认 |
| Observable | PE[0,8,12,16,20,24,32,40,48,60]×11时间箱，raw C/AC | 99箱数值已取得；边界来源限制保留 |
| Statistics/Fast | 本轮先做信号前向计算 | P08/P09 NOT_REQUESTED；不运行拟合 |

已取得官方事件/背景/ROOT、响应系数、原核表与原文。尚缺的是若干物理对应的核验，不是这些数值文件不存在。共享理论公式只在P04/P05核查，实验正文登记模块选择/资源和阻断范围。

Compiler/Renderer：本轮尚未生成新YAML/NPZ运行包。H3及必要合同接受后，按统一IR→tools/compile_experiment_package.py→机器文件/Physics MD生成，不以旧自定义报告冒充新包。

需要审核的具体问题：① η按完整时间支撑域还是0–6μs参考窗解释；② 本轮接受的一体流范围及未知两体流误差；③ 背景归一只作分列诊断，暂不认定作者完整模板。共享式75冲突须先核查，不用调参消除。

当前计划：[Phase0计划](<00_EXECUTION_PLAN.md>) · [可恢复进度](<00_MIGRATION_PROGRESS.md>) · [来源/冲突](<P02_MISSING_AND_CONFLICTS.md>)。
