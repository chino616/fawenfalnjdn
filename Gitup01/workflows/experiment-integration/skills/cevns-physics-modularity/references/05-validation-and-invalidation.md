# 05 验证、缓存失效和当前能力边界

## 1. 验证分层：先证明模块契约，再证明整条链

文档中“需检查”不是“当前所有测试已经覆盖”。使用真实物理值、独立解析极限或适用的外部参考；
不用另写一遍同一个公式当作唯一基准。只读定位不必跑整套昂贵 Slow，但实现变化必须按风险验证。

| 模块 | 单模块验证 | 替换后端到端验证 |
| --- | --- | --- |
| C00 单位/配置 | 每字段真实消费方；MeV/GeV、keV/GeV 转换；配置扰动对应真实输出 | 相同物理输入的不同单位表示产生同一物理预测 |
| S01 连续谱 | 支撑、有限/非负、分量积分、绝对 normalization、插值/端点 | 保留 source-resolved 真反冲谱，与旧源/新源分别对照 |
| S02 归一化 | POT/r/L/时间 owner；绝对谱不重复乘总强度 | 在可分离条件下逐箱检验线性缩放及 L^-2 |
| S03 谱线 | 能量/权重单位；空/多条线；每条线的支撑 | 单线解析求值与人工窄线积分在收敛极限一致 |
| S04 支撑/数值域 | 物理域与表格域区别；超出输入域行为 | T 接近各源端点、阈值或插值断点时逐箱收敛 |
| S05 时间 | φ 与 Φ 的积分闭合；时间窗/选择因子 owner | 时间联合结果对所有时间 bins 求和与对应积分分析一致 |
| P01 粒子身份 | 接口接受/拒绝；真正 ν/反ν 振幅 benchmark | 同 flavor 不同粒子身份是否按物理预期变化 |
| P02 rho | Hermitian/PSD/trace=1；纯态/混合态/相干态 | 真实 E 子网格和线能量对齐；基底一致 |
| P03 传播 | 后端只输出 rho；SM 与 NP 不重复；源态极限 | 传播参数改变时检测预测跟随改变；与外部传播参考比较 |
| T01 核数 | 数/质量分数换算；丰度和；molar/nucleus mass 一致 | 等化学计量 Cs/I 等核数；单核素极限 |
| T02 曝光 | mass/time/exposure 的独立因子与单位 | 逐 bin 质量/时间缩放；多运行期总和 |
| T03 W | key/channel 完整、y 单位、基底变换、来源规范 | pn/iso 预测一致；外部来源表逐通道核对另行进行 |
| E01 Wilson | 支持键、维数、矩阵轴、重复输入拒绝 | 单算符/多算符/复系数与新 basis 完整性 |
| E02 SM+NP | SM 零 NP、pure FC 特例、允许/禁止干涉 | 总系数路径与独立振幅展开在适用点一致 |
| E03/E04 LEC/匹配 | 质量维数、极点 q²、p/n/isospin、c10 约定 | LEC 改变确实穿透 rates/Slow/Fast，逐核逐通道一致 |
| E05 运动学 | Tmax/Emin 互逆、支撑域外、q 各定义一致 | Slow/Fast 端点同一；近似阶数和误差明确 |
| E06/E07 R/K | 最终 K 的 Hermitian/PSD；R 的伴随配对、sector、混合项复相位和通道和 | 不要求每个混合 R/W 分块单独 PSD；Slow 与系数空间公式逐点一致 |
| E08 截面 | 单位、核质量、能量依赖、正定性适用条件 | 对固定 rho 的 K 收缩与标量截面接口一致 |
| H01 Helm | q→0 的 F²→1、模型范围和 endpoint | 同物理条件下比较，而非把两种核模型相乘 |
| D01 映射 | 标定域、物理取值、需要时单调性、单位 | 平均响应改变造成正确重建谱移动 |
| D02 分辨率 | full-domain normalization、均值/宽度、非负 | 窗外迁移保留，delta/窄宽极限和概率矩阵闭合 |
| D03/D04 效率/选择 | 变量/边界/阈值、非重复、物理上界 | ε=1、ε=0、a_s=1 等极限；分量接受率只乘一次 |
| D05 分箱 | edges 严增、宽度、counts/density 变换 | 合并 bins 的求和闭合；统计数据同步 |
| I01/I02 积分/fold | 每源单线/连续谱、真实谱、重建谱中间量 | 求积加密、重排积分、逐箱绝对与相对容差 |
| I03/I04 计数 | raw 的质量/权重状态与单位明确 | 各源/靶/探测器分量精确组合成总计 |
| F01/F02 h/H | basis/sector/轴、构建输入、源/响应内嵌范围 | 多个 SM/NP/复数点逐箱匹配权威 Slow |
| F03 重建 | full 与 diag/re/im 等价；纯/混合 rho | 不只比总数，单通道与源分量也能追溯 |
| F04 缓存 | 内容依赖、版本/单位/轴、读写一致性 | 改一项依赖后拒用旧缓存，保留无关缓存 |
| L01 数据 | bin/单位/语义/背景/误差和 provenance | 不产生负的 Poisson mean；excess 可为负 |
| L02/L03 推断 | nuisance toy、profiling、阈值/自由度/相关性 | 参数区间及联合相关性，不以 forward 一致冒充官方统计复现 |
| O01 路由 | source/Slow/Fast/stats capability 分别注册 | 从真实用户入口到输出的 smoke test |

## 2. 复用与失效矩阵

这里的 H 专指已经积分 source/target/detector/exposure/bin 的 EFT 系数核。
“重算”仅针对有依赖的结果；纯比例解析更新也必须按其数学适用条件验证，不能校准到外部总数。

| 变化 | 通常可保留 | 需更新/重算 |
| --- | --- | --- |
| 仅 Wilson 数值，模型/基底/传播固定 | W、detector matrix、系数无关 h/H | 总系数/B、截面或 Fast N、统计预测 |
| 仅 sW² 且 H 不含固定 SM 系数 | W、detector matrix、完整系数 H | 检测 SM 系数/B、N、统计 |
| 仅固定 rho，H 本身独立于 rho | W、h、detector matrix、相同 source 的 H | rho/B 与高层 source 映射、N；先核对缓存表示 |
| rho(E) 或 rho 随扫描参数变化 | W 与适用的裸 h、detector matrix | 传播/能量收缩/与 rho 绑定的积分，通常需更高维 transfer 或 Slow |
| 源连续谱、谱线或能区 | 核物理、适用能区内 W、相同 T 网格的 detector matrix | 源插值、E/T 网格、反冲/重建/N、H、统计 |
| POT/r，固定其它物理 | W、h、detector matrix | 归一化及含它的 H/N/统计；按合同允许解析比例更新 |
| baseline | 裸核/探测器物理 | flux、可能的 rho、H/N/统计 |
| active mass 或独立时间 | 每核反冲谱、响应概率 | 核数/曝光归一化与含它的 H/N/统计 |
| isotope/质量/丰度 | 源与独立传播，适用的 detector 模型 | W/kinematics/核数或组成、K、反冲谱、H/N |
| W normalization/核模型 | 源、detector 模型 | 规范适配、K、截面、所有源积分与 H/N |
| LEC/matching/R/kinematics | 依赖无关的源与 detector 标定 | ci/R/h/K/截面及下游 H/N；检查 Fast 独立公式 |
| quenching/resolution | 源、rho、真实反冲谱、裸 h | detector fold、重建谱/N、对应 H |
| efficiency/component selection | 源/核截面/真实谱；可能保留裸 P | acceptance/fold/N/H；与 E/time 相关时重审积分因子化 |
| bin edges | 源/裸 h/真实谱/可复用的连续重建谱 | bin acceptance、H/N、stat data/covariance；不可凭粗 bins 细分 |
| statistical observed/background/covariance | 物理输入不变时 N/H | dataset/likelihood/profile/interval |
| 数值网格/插值/容差 | 未改变的物理模型 | 受该离散表示影响的中间数组/H/N及数值误差验证 |

探测器响应矩阵不一定因源改变失效：只有它含源权重或其 T 网格依赖新能区时才变。
同理，不应把在完整 H 中成立的缓存条件强加给裸 W 或 h。

## 3. 推荐的缓存内容键（PROPOSED）

当前 storage 校验 schema/shape/dataset 等，尚不能据此声称所有物理输入内容已自动核对。
新缓存应按所缓存对象选择依赖，不要求每类缓存都填整张表：

```text
representation_kind + schema_version
theory_model + amplitude/response_convention + particle_kind_route
operator_basis/order + coefficient_units/scales + LEC/model parameters
target/isotope/mass/fraction convention + response data content digest
source spectrum/line content digest + support/interpolation/time basis
propagation/state dependency, including whether rho is integrated or external
detector mapping/resolution/efficiency/selection digests
exposure ownership and values included in this representation
observable name/unit + bin edges
integration grid/quadrature/tolerances
relevant implementation digest/version
```

文件路径不是内容指纹；同路径覆盖新数据后旧 H 仍可能加载。仅相同 dataset_id 也不足以证明相同物理。
变化检测应说明拒绝原因、哪些对象仍可用及重建入口，而非静默返回陈旧预测。

## 4. 当前测试入口与其证据等级

以下文件在活动目录存在；应根据本次变更选择，不声称文件存在就代表全部物理测试通过。

- `tests/test_source_state_p2.py`：状态、shape、粒子标签及当前约定；不证明反ν振幅正确。
- `tests/test_rates_differential_flavor.py`：rates flavor 截面接口。
- `tests/test_li2026_amplitude_flavor.py`：振幅 flavor 路径。
- `tests/test_li2026_units_contract.py`：单位/匹配/core-rate 契约。
- `tests/test_nuclear_response_convention.py`：数据库声明与部分内部规范；不关闭外部来源表审计。
- `tests/test_legacy_coherent_scalar_regression.py`：保护既有 COHERENT 行为；不把旧程序一致性写成独立物理正确性。
- `tests/test_experiment_specs.py`：spec 发现/装载；不证明数值程序自动消费全部字段。

共享代码变化后，仓库要求保护 CsI2017/CsI2021/Ar2020 的既有回归。
若其它实验共享被修改的 core，还需选其实际回归；这里不复制其它实验的物理常数作为 COHERENT 默认。
未找到所需测试或基准时报告缺口并增加与物理不变量有关的检查，不能调 reference 值或放宽容差让新结果过关。

## 5. 当前限制必须在替换报告中按相关性保留

1. SMEFT/RG 只有 metadata 时不能宣称完整 UV 运行链。
2. LNV 零对角校验不等于完整 flavor 对称性已实现，也不是所有 LNV 结构的普遍物理定理。
3. 核响应外部来源/normalize/mixed ordering 尚未完成全面验证。
4. reference 总核响应公式与当前 R×W 权重的对应尚需独立核实。
5. ν/反ν标签存在，但当前互动核未据其完成物理切换。
6. 当前 COHERENT source 是积分注量；没有通用联合能量–时间积分。
7. energy_shape 相同不等于 E 值相同，旧积分器也不自动处理任意 rho(E) 的切片。
8. 默认 source/response 函数与参数对象在 Python 定义时已绑定；Notebook 改全局名不等于所有调用方生效。
9. 保存 H 只读入和重建，不因源/效率代码更新而自动重建。
10. 小网格可验证调用与轴，不能充当收敛的科学 benchmark。
11. 当前 stats 的 legacy approximate 标签必须保留，不能因新 signal 更精确就宣称官方 likelihood。

## 6. 模块完成与发布的判据

模块文档完成：物理定义、当前 owner、建议边界、替换清单、下游影响和检验均可追溯。
模块实现完成：实际调用方已接入，新参数确实被消费，并通过相应单模块/链路验证。
模块物理验证完成：还要有适用的外部基准或明确的解析范围；内部回归不能替代。
本 Skill 的文档校验只检查引用和链接，不能将上述三种完成状态混成一个 PASS。

与既有 workflow 的职责对应：Target/Exposure→P02，Source/State→P03，Theory/W→P04，
Kinematics/CrossSection→P05，Detector→P06，Slow→P07，Fast→P08，Statistics→P09，Validation→P10。
这份模块手册补充其工程定位，不自动更新或批准任何已有阶段状态。
