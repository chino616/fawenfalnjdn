# 03 逐场景替换手册

每个场景先看物理合同，再按 [02 代码地图](02-current-code-map.md) 找实际 owner 和所有调用方。
以下“修改”是范围建议，不是宣称已实施；新增实验尽量保留原 COHERENT 实现，用薄适配器接入。

## A. 只调整同一种 SNS 源的归一化

**物理变化**：POT、r、点源几何下的 L；谱形、源分量、端点均不变。

1. 实际运行值在 `src/cevns_pyeft/experiments/coherent/sns.py::SNS_DATASETS`，不是 SNSDataset 类定义。
2. 由 `src/cevns_pyeft/experiments/coherent/sns.py::_n_time_integrated_flux_cm2` 计算新注量。
3. 同步记录 spec/来源；先证明代码消费链，不能只更新 experiment.yaml 并宣称数值已生效。
4. 对现有源支撑和接口，无需改变 counts 的物理积分算法或理论截面。
5. 重算源图、Slow 谱和受影响的已积分 H；旧 H 不自动读到新 POT。

**验证**：只改 POT/r 且其它量固定，逐 bin 按同一比例变化；只改 L 且 rho 不受 L 影响时按 L^-2。
这种解析缩放是物理预言和交叉检查，不是用全局比例强行校准模型。
基线进入传播时，另重算 rho(E,L)。

## B. 改 SNS 连续谱或改为输入数值表

**物理变化**：S01/S04；粒子和源类别仍沿原 SNS 契约。

1. 修改或在适配器中替代 `_michel_nue_spectrum`、`_michel_numubar_spectrum`、`loadNeutrinoEmpiricalFluxSNS`。
2. 指明替代的是单位形状还是绝对 fluence；表格是否已含 Φ0。禁止重复乘 Φ0。
3. 需要读表时明确 table loader、列单位、排序、插值、端点和域外行为。仅覆盖 SNSflux_*.txt 不会改变现有解析 loader。
4. 若支撑/分量名/线结构不变，已有计数接口可保留；但仍做源积分与网格收敛检查。
5. 若物理端点改变，转场景 C，同时检查所有 T 网格和 Fast 源积分。

**保持不变**：Wilson→ci、R、W、核质量、响应和效率，除非本次还有独立物理变化。
**失效**：源谱、反冲谱、重建谱、N_i、源积分 H、由它们得到的统计预测。

## C. 从 SNS 换成太阳、反应堆或其它源

**物理变化**：可能同时涉及 S01–S05、P01–P03；必须区分“同源的新实验”与“不同源”。

### 源层

- 新建本实验的 `source.py` 或配置消费适配器，提供真实 source IDs、flux/fluence、物理支撑、连续谱和可选谱线。
- 不把原 SNS loader 改成返回另一种源，避免改变 CsI2017/CsI2021/Ar2020。
- 根据材料选择绝对通量或源强推导，固定时间基准；低能源也不能沿用 0–52.8 MeV 稀疏网格而不检查误差。
- 明确粒子类别与探测器处 rho，传播在外部独立计算。

### Slow 入口

以 `slow_counts_csi2021` 为结构参考，新增/适配实验入口；替换 load SNS、源循环、state 生成、目标组成及选择接受率。
不要把新源硬塞成 e/mub 标签以绕过接口检查；源 ID 与 particle_kind/flavor 是不同字段。

### 积分层逐项检查

| 当前假设 | 必须处理的位置 | 推荐替换方向 |
| --- | --- | --- |
| Emax 固定 μ DAR | counts._rate_per_kg、counts.empirical_dNdPE_response_csi | 每分量从 source support 取得上限 |
| T 网格上限固定 μ DAR | counts._er_grid、实验 T grid builder | 由新源最大允许能量和共享 Tmax 计算 |
| 所有源必须有 muLine | 两条 counts 路径 | 空或多条 energy_lines 列表 |
| mu 无连续谱，e/mub 名字写死 | counts._choose_phi_cont 和 empirical 内部 phi_cont | 每分量自带 continuum callable |
| source=='SNS' 才处理线 | empirical_dNdPE_response_csi | 按谱线列表，独立于源名字 |
| rho 仅按原 energy_shape 广播 | differential_cross_section_nn + source_state 调用方 | 在真实积分子网格求 rho；线能量另求 |

不要修改 `emax_muon_dar_mev()` 的物理定义；新积分器应不再硬编码调用它。
`enr_max_keV(A,Emax_MeV=...)` 已可接收外部上限，但所有未显式传 Emax 的调用仍需核对。

### Fast、存储、统计路由

如需要 Fast，核对 builder 的 FLAVORS、_choose_phi_cont、load_flux、_build_target_static、
_build_one_target_kernel、_build_one_target_kernel_csi2017_ar 的同类绑定。
同时核对 reconstruction 的固定 rho/source keys、storage.DATASETS 与 predictors 的固定分量键和 PE 语义。
仅注册新 dataset 字符串不能完成这些适配。新增物理积分 H 需与新 Slow 逐箱比较。

**通常可复用**：在适用域内的 NeutrinoState、弹性运动学、核响应读取和微分截面。
**仍需物理审核**：新能区的相干性/响应有效域、反ν振幅、传播 NP、有限质量或非弹性效应。

## D. 只改入射 flavor 组成或传播

1. 常量 rho：保留源强和谱形，在实验源 adapter 中替换 state；不修改 flux 归一化或 detector。
2. ρ(E)：使用携带能量值的传播输出，在每个实际积分网格匹配/插值，校验 trace/Hermitian/PSD。
3. 掩码 Enu>=Emin 后不能继续传未切片的整网格 rho；源线不能用任意数组第一项代替其 rho(Eline)。
4. 插值可选择有物理依据的方法。例如同基底两个 PSD、trace=1 矩阵的非负凸组合保留这些性质；
   样条插值未必保留。外推必须按合同处理，不能自动修补错误态。
5. 单改 nu/antinu 标签不触发当前 kernel 物理变化；需要反ν支持时审计振幅核心并做独立基准。
6. 若 Wilson 影响传播与检测，共用模型参数但保持 NP-only 传播转换与检测 SM 合并的不同归属。

**Fast**：固定 rho 的低层 B 重建可复用独立于 rho 构建的 H；但高层固定源映射要适配。
能量相关 rho 或随系数变化的 rho 不能一般性抽出能量积分；新增 transfer tensor 或回到直接积分。

## E. 更换靶核、材料或同位素丰度

1. 检查响应数据库是否有每个 isotope key，并确认核算符截断/来源/规范适用。
2. 在实验层提供 composition：number_fraction 或 mass_fraction、molar mass/nucleus mass、有效质量。
3. 替换 slow_counts 中 target_specs 与 combine_equal_stoichiometry；不能把 Xe/Ge/混合物当 Cs:I=1:1。
4. 若继续使用 A*amu 近似，显式保留；若用精确质量，同时核对核数、Tmax/Emin、q 和 Fast。
5. 新核素可只换 data/response key；新核结构模型可能要求替换 W provider 和规范转换。
6. 多探测器不可自动混成一个平均丰度/效率，除非证明这种近似满足目标精度。

**不必修改**：适用的源谱、Wilson 定义和公共积分公式。
**失效**：目标 W(q)、散射 K、核数因子、T 网格、反冲及重建谱、H 和统计预测。

## F. 只调整有效质量、曝光或运行期

- 当前 CsI2021 质量从 SNS_DATASETS→flux.basic.detectorMassKg→bin_events_csi 读取。
- 当前 CsI2017 的 Slow/Fast 另有 14.6 kg 常量，虽 SNSDataset 为 14.57 kg；不能假设只改一处便全部生效。
- 当前 Ar2020 Slow 读 flux metadata，Fast 调用另传 24.0 kg；需同步真实 owner。
- 新模块化方案应由 TargetExposure 提供质量/时间，Source 只报告其已经包含的曝光因子。
- 运行期改变可能也改变效率、源谱、dead time 和背景，不能假设只是总数缩放。

**验证**：固定所有谱形/选择时对未包含的独立质量或时间线性缩放；逐 bin 及逐源检查。

## G. 替换 quenching、yield 或分辨率

1. CsI2021 参考 owner：rates.differential.eee_quenching_csi、p_smearing_csi。
2. 若只改 quenching，保持 resolution 模型选择不变，但它依赖新的均值时其数值也随之改变。
3. 若改响应分布，定义 P(x|T) 单位、全域归一化、均值/宽度、支持域和数据标定范围。
4. counts 的默认 smear_func 在函数定义时绑定。当前外层 slow_counts_csi2021 没暴露自定义 smear 参数，
   因而需要显式透传新 response，或在新 adapter 中直接编排；仅局部重绑函数名字不足以证明生效。
5. Fast 的 CsI fold 与 Ar/2017 专有 fold 是独立实现；改 Slow 后要同步或改成共用 detector provider。
6. 数据表若给 migration probability per bin，不再把它当密度乘一次 Δx；若 fold 已含 ε/dT，标明归属。

**失效**：detector acceptance/fold、重建谱、N_i、相关 H；如果源/理论没变，单核真反冲谱可复用。
**验证**：响应全域积分、均值、宽度、窗外迁移、delta/窄宽极限、重建谱与 bin 积分闭合。

## H. 只替换效率、阈值或组件接受率

1. CsI2021 ε(PE)：slow_counts_csi2021.efficiency_csi2021；组件常数：DEFAULT_ACCEPTANCE。
2. CsI2017/Ar 效率表由 experiments.base._interp_eff 加载；替换表路径/列单位，核查边界规则。
3. 确定 ε 的变量是 T、mean x 或 x_reco；它们需要放到不同积分位置。
4. analysis lower edge、触发阈值、零效率域不是自动等价的概念。
5. 接受率 a_s 随能量/时间变化时，不能继续在最外层乘常数。
6. Fast 检查 builder 导入别名与 fold。重建保存的 H 不会自动反映修改后的效率函数。

**可复用**：源、rho、W、截面、真实反冲谱；仅 ε 改变时原 P(x|T) 也可复用。

## I. 改变 binning 或重建 observable

1. 只改 edges：更新 Slow、Fast 和统计数据的同一 bin 契约；用新 edges 重新积分。
2. 同步 widths 和 counts/width 输出；不能用旧 N_i 只换横坐标或除另一组宽度。
3. 改 observable 如 PE→keVee：定义新 response/效率坐标和 Jacobian，不是重命名字典键。
4. 已知子 bin 计数/协方差时才可按明确求和矩阵重分箱；单有粗 bins 不足以无模型细分。
5. 改成能量–时间二维：按 S05 新建时间输入与 detector joint response，扩展输出/统计/cache 轴。

## J. 改 EFT 模型、SM 参数或 LEC

- **只改已有 Wilson 数值**：传 wc_triplets/left_wcs；保留 source/detector；有效 H 可重用。
- **只改 sW²**：传 sin2thetaW；当前系数空间 H 与系数独立时可只重建总系数/B。
- **改 GF/普适常数**：检查 SM、NSI 转换、传播和单独比较模型，避免只改其中一个入口。
- **改 LEC**：构造新 Li2026LECs 并显式传到匹配/振幅/截面；rates/Slow/Fast 是否透传需扩展。
- **改已有算符匹配**：left_to_ci 为主要 owner；Fast 调它生成 unit ci，另查独立 R 副本。
- **新增算符**：operators registry、matching、sector、R、kernels.basis、builder、存储 schema 和测试联动。
- **SMEFT/RG**：当前只是 metadata，新增可执行匹配/演化属于新物理模块，不可宣称改常数字符串就已实现。
- **换 Helm**：选择独立比较 provider；不能把 Helm F²再乘到 full W 结果，也不能宣称完整 LEFT 支持。

**验证**：零 NP、单系数、混合系数、复数相位、纯/混合入射态、sector 和允许干涉，逐核素逐通道检查。
纯 FC NP 对当前纯 SNS 源无 SM 干涉是特例，不可把这一结论硬编码成删除所有 SM–NP cross terms。

## K. 改运动学或核响应规范

1. 理论支撑使用 theory.kinematics；q 构造在 amplitude 和 builder/TargetStatic 中各有实现。
2. 采用精确 |q|²=2mAT+T² 时，相应 invariant 应为 −2mAT；不要单改一个 q 破坏匹配一致性。
3. responses_R 公式本身使用的展开阶数也要审查；更精确输入不自动让截断公式整体更精确。
4. 更换 W normalization、p/n 顺序、混合通道方向或 spin average 需要修改/转换对应收缩。
5. 保留已声明的外部审计缺口；内部 pn/iso 一致不等于外部源表规范全部正确。

## L. 改事件积分算法与性能

1. 先固定物理输入、有限域、插值与期望容差，保存可信逐 bin 对照。
2. 优先抽出 Y_A,s(T)，一次计算后在不同 PE/bin 重用；保留各源、各靶分量。
3. 将 continuous 与 line 两种能量积分路径独立；对 endpoint/分段节点进行数值处理。
4. 纯数值算法改变不改 source normalization、W 或 detector 参数来迎合旧结果。
5. 验证重排积分、向量化、自适应求积、并行化是否保持输出；计时与物理误差分别报告。
6. 只改 n_er/n_enu/n_pe_bin/pe_step 可直接使用现接口，但这改变数值误差而非增加物理能力。

## M. 改观测数据、背景、likelihood 或置信区间

1. 数据/背景/误差/协方差归 statistics.datasets 或新实验 stats adapter，不改理论 signal 当作补偿。
2. 核对 observed 是 raw、on/off 还是 excess；当前 CsI2021 是 legacy approximate excess。
3. 改 bins 同步全部统计轴；events/bin→counts/PE 由 observables 显式转换。
4. 改 likelihood/nuisance 在 likelihoods/profiling；改扫描与区间规则在 scans/confidence。
5. 只有统计模型变化而物理预测输入不变时，可重用相同 N_i 与 H；有依赖的 nuisance 可能需要重算谱。

## N. 最后才接 registry 和发布入口

当前 registry、storage、predictors 有各自 dataset 或 source 假设。新实验必须分别核对 capability。
只有 source 通过验证不能宣布 Slow/Fast/statistics 都可用；注册某个名字也不能代替其计算实现。
将实际改动与回归报告写入对应流程已有的实施清单；不要仅凭本手册更新正式 Gate。
