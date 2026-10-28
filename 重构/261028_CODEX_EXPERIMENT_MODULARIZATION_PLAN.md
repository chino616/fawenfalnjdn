# Codex 实施方案：独立实验定义、统一加载与数据集启停

状态：IMPLEMENTATION PLAN，尚未执行本方案中的代码修改。  
日期：2026-10-28（Asia/Shanghai）。  
目标项目：CEvNS-pyEFT，仓库子目录 Gitup01。  
审查分支：refactor/modular-interfaces-20261028。  
审查基准提交：d7182a116353faf0ba5ba581338db1d2a4b63074。

## 0. 交给 Codex 的任务

在上述项目现有组合式接口上完成“实验分析单元”的模块化。用户应能通过配置选择、增加或排除实验数据集；每个具体实验数据发布/分析版本都有独立定义；所有实验设定都有明确权威来源；新增符合既有能力的数据集不需要修改公共积分器、折叠器或统计名称分支。

本次要解决的是多实验管理和物理设定归属。复用已建立的 contracts、ExperimentModel、Prediction、新 Slow/Fast 及缓存机制。不得将任务再次收窄为只完善 CsI2021，也不得为了一个统一接口把不同实验的数值方法或物理定义改成相同。

本文件指定以下已有数据集，不新增真实实验身份：

| dataset_id（保留现有值） | 本轮处理对象 |
|---|---|
| CsI2021 | 现有九箱、legacy approximate statistics 复现分析 |
| CsI2017 | 现有二十五箱与确定性 PE 映射复现分析 |
| Ar2020 | 现有十二箱、响应与近似统计复现分析 |
| conus_plus_2025_c2c3c5_ge73_pyeft | 仓库已有 Ge73 候选模型、C2/C3/C5 三探测器及其现有统计范围 |

CONUS+ 范围是上述精确 ID；不得自动换成天然 Ge、其他 CONUS 发布或官方 on/off likelihood。年份标签不自动等于真实采集年份。已有数据的科学适用性沿用当前声明，不因工程迁移而升级。

### 可复制的启动指令

~~~text
请读取本方案，先核对当前代码版本、Git 状态和适用 AGENTS，然后按 M0–M7 顺序实施。

主要目标：
1. 每个已有实验数据集都有独立、可追踪的完整定义。
2. 使用统一 load_experiment / predict_experiment 入口。
3. 用户通过实验 ID 列表增减参与计算的数据集。
4. 修复旧 Fast 统计路径的实验身份误标。
5. 消除运行参数、分箱、响应参数和统计输入的重复权威来源。
6. 保留现有四个数据集的物理语义、公开兼容入口及受保护数值结果。
7. 交付实际跨实验切换与独立新数据集注册的验证证据。

不要只增加目录、Protocol、registry 名字或 YAML；定义必须实际控制计算。
不要把包装整个旧函数称为组件迁移完成；过渡包装需要明确标记。
先冻结独立基线，保留原参考，逐阶段验证，不自动更新参考或放宽容差。
统一入口允许不同数值策略和后端能力；记录每个数据集实际使用的实现。
遵守当前有效授权及项目工作流；已有授权覆盖的动作不重复确认。
本方案本身不等于 Physics Gate 通过，也不授权新的科学假设。

最终交付：实现代码、逐文件变更说明、参数归属表、能力矩阵、实测验证、
可运行的用户例子，以及准确标注的未完成项。
~~~

## 1. 已核实的起点与风险

以下是对基准提交的源码及运行检查结果，不是未来实现要求的完成记录。

| 编号 | 已核实事实 | 实施含义 |
|---|---|---|
| F01 | 只有 experiments/coherent/csi2021.py 构造真实 ExperimentModel | 需要把实验定义层推广到其余数据集 |
| F02 | registry.get_experiment 对三个 COHERENT 名称返回通量字典，对 CONUS+ 返回 spec 字典 | 不能把现有函数当成统一模型加载器 |
| F03 | CONUS+ 可被 list_experiments 列出，但 get_slow_count_function 不包含它 | “可发现”和“可计算”必须分开表述 |
| F04 | CsI2021 的运行默认值在工厂和 SNS_DATASETS 中重复；分箱还在统计层重复 | 需要确立单一权威值和兼容读取路径 |
| F05 | CsIGammaResponse.describe 手写参数，density 实际调用另一处常数公式 | 参数描述必须由实际实例参数生成 |
| F06 | 工厂不消费 experiment.yaml；简化 YAML 解析器将内联参数映射解析为字符串 | 不能宣称现有 YAML 是运行时配置来源 |
| F07 | statistics.predictors 的旧 Fast 分支不核对所请求实验与核文件身份 | 首先修复可复现的身份误标 |
| F08 | CsI2017、Ar2020、CONUS+ 的实验选择仍进入各自计算函数；公共统计层仍按名称分支 | 需要完整实验对象绑定预测、数据与统计 |
| F09 | 新 Fast 编译器、物理依赖指纹和统一响应多项式已实现 | 保留并接入；不重新复制截面公式 |
| F10 | 当前 CONUS+ 输出包含三个探测器和十九个观测箱，计数采用 kg·day 曝光 | 不能伪装成 SNS 曝光或无标识的 57 元素向量 |

### 身份误标复现

在基准提交，用 CsI2021 的核文件调用：

~~~python
predict_raw_components("Ar2020", mode="fast", fast_kernel_path=csi_kernel)
~~~

会成功返回标为 Ar2020 的九箱 CsI2021 结果；不存在的名称同样可以被接受。这是旧统计 Fast 入口的缺陷，不等于新 CompiledKernel 的物理指纹失效检查无效。

### 本次审查测试基线

审查环境：Python 3.12.14、NumPy 2.3.5、SciPy 1.17.0、pytest 9.2.0。完整 tests 结果：186 passed、1 failed、0 skipped。

唯一失败：
test_existing_fast_builders_preserve_pre_refactor_arrays_exactly[CsI2021]。

核数组与提交内参考的最大相对差约 4.24775396e-16。原始 builder 与新 builder 在同一审查环境生成的 full/diag/pair 数组完全相等，两者与冻结参考存在相同差异；对应 SM 逐箱事件数最大差约 2.13e-14。证据支持跨环境浮点差异解释，不能把这个失败当成已经解决，更不能自动放宽原测试。

后续实施者先在自己的执行环境重跑、记录版本。原报告的 187 passed 不是当前环境的自动验收结果。

## 2. 首先明确“一个实验 part”的边界

一个 part 是“一个可独立加载、追踪与验证的数据集/分析定义”，其中至少绑定：

- 实验家族与稳定 dataset_id；
- 引用的运行记录；
- 数据发布身份与本次分析定义版本；
- 源、曝光、材料、响应、效率、选择、轴及分箱；
- 观测、背景、误差资源和统计模型；
- 默认数值策略、计算能力及验证入口。

同一实验家族可有多个独立 part。运行记录可被不同发布引用；一个发布也可引用多个运行期，所以不能简单把发布年当成曝光期，不能仅靠目录包含关系推断数据独立性。

保留已有 dataset_id 和兼容调用名。新增 analysis_revision 只表示工程分析定义版本，必须与实验官方 release_id 区分。缺少官方发布编号或准确采集时间时保留 None/明确缺失，不编造。

本轮支持的数据集集合就是第 0 节的四项；启停是本次分析选择，不删除原始数据、参考数组和历史定义。

## 3. 目标结构与依赖方向

推荐先使用 Python 实验定义；本轮不建设通用配置语言。YAML/TOML 仅用于选择数据集、资源根和明确允许的覆盖项。

最小新增结构：

| 结构 | 职责 |
|---|---|
| ExperimentDefinition | 某个数据集的不可变定义、资源引用、参数和能力声明 |
| PreparedExperiment | 定义解析后实际参与计算的模型/子模型、执行器、统计绑定、解析记录 |
| ExperimentPrediction | 带 dataset_id、定义版本、探测器/运行分项及观测身份的预测结果 |
| AnalysisSelection | 本次启用的 dataset_id 列表、允许的覆盖项、后端选择 |

类型和字段可沿用现有类扩展，避免为同一个概念重复创建对象。新增外层结果应包装现有 Prediction；不要复制它的数组存储和归一化逻辑。

依赖规则：

1. 定义选择模型和数值策略；公共算法只消费约定输入。
2. loader 负责解析资源、构造不可变实例、检查兼容性。
3. registry 只做 ID/别名/能力索引及惰性加载；不存物理默认数值。
4. runtime 编排不出现按 CsI2021、Ar2020、CONUS+ 名称决定公式或数据的 if/elif。
5. 专用适配器可以位于实验模块，接收显式设定；实验名称不进入通用积分算法。
6. 统计模型由实验定义绑定。只计算物理预测时，不强制加载统计数据。
7. 增加实验后只改自己的定义、必要组件、数据和注册项，不应修改公共算法。

ExperimentDefinition 应声明下列内容，不要求所有大数组内联：

| 字段组 | 内容 |
|---|---|
| identity | experiment_slug、dataset_id、release_id（可缺失）、analysis_revision、run_refs |
| physical_settings | 源参数、归一化方案、材料、曝光、响应/效率/选择参数 |
| observation | 轴、单位、分箱、探测器/运行子项及明确的聚合规则 |
| resources | 逻辑资源 ID、路径解析规则、内容校验信息、语义 |
| numerical_profiles | 各受支持策略的参数、有效范围、历史兼容约定 |
| statistics | 数据 loader、observable 转换、likelihood evaluator、nuisance 定义、状态 |
| capabilities | supported / unsupported / requires_resource / legacy_compat 及原因 |
| validation | 可执行的合同、基线和替换验证入口 |

已解析记录必须从实际实例和实际资源导出。配置覆盖顺序固定为：权威定义默认值 → 当前调用显式覆盖 → 校验。文件位置变化可以只改变 provenance；资源内容变化必须按依赖影响计算。

### 后端兼容不等于强制同一算法

公开入口统一，数值策略可以不同：

- CsI2021 继续使用已有 ExperimentModel 和新 Slow/Fast。
- CsI2017 的确定性映射需要专门折叠策略，不能使用窄 Gaussian 假装等价。
- Ar2020 保持现有响应、网格及折叠规则。
- CONUS+ 保持分段 Gauss 求积、kg·day 和多探测器组织。

第一阶段允许显式 legacy executor 连接旧实现以验证加载链；它必须标为 legacy_compat，且只能消费完整定义传入的设定。最终参数集中验收不接受“忽略定义，内部继续调用固定全局默认函数”的空壳包装。

不以“所有实验共用一个巨大积分函数”作为完成标准。模型选择、物理设定和算法依赖明确，且统一入口真实消费它们，才满足本任务。

## 4. 统一 API 目标

以下是 DESIGN，不是现有 API。创建这些函数前应检查仓库是否已有可复用实现。

~~~python
from cevns_pyeft.experiments.loader import load_experiment
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment

experiment = load_experiment(
    "CsI2021",
    resources=resource_catalog,
)
prediction = predict_experiment(
    experiment,
    parameters=theory_point,
    backend="slow",
)
fit = evaluate_experiment(experiment, prediction)
~~~

约定：

- load_experiment 返回 PreparedExperiment，不混合返回通量字典、YAML 字典或计数数组。
- parameters=None 时使用明确标记的复现默认理论设置；显式 TheoryPoint 不得被实验默认值覆盖。
- 不同实验现有 sin²θW 默认值可能不同，必须记录。例如 CONUS+ 现有 .23857 与 COHERENT .2387。统一接口不得静默统一这些复现设置。
- 默认 numerics 来自实验定义；显式数值覆盖必须检查对应策略是否消费。不能静默忽略 n_er 等字段。
- backend="fast" 不支持时明确报错；backend="auto" 允许记录原因后选择可用后端。
- predict_experiment 对单探测器、多个探测器返回相同的外层结果类型；内部子预测有稳定键、轴和物理单位。
- evaluate_experiment 必须核对 dataset_id、定义版本、观测映射及统计能力，拒绝错配。
- 旧 get_experiment 返回语义保持兼容，不能悄悄将 dict 改成新对象。新增明确入口，并在文档中标出旧 API 的边界。

### 运行选择配置

第一版只需要有限结构，不支持任意 Python import、表达式执行或从 YAML 自动执行 callable。

~~~yaml
datasets:
  - id: CsI2021
    enabled: true
    backend: slow
  - id: Ar2020
    enabled: true
    backend: slow
  - id: CsI2017
    enabled: false
~~~

AnalysisSelection 严格检查：

- ID 存在；别名规范化后不能重复。
- 不认识的字段报错。
- disabled 项不加载资源、不编译核、不参与统计。
- enabled 项缺必需资源时给出具体错误，不静默跳过。
- 对同一物理 part 使用两个别名不能重复计入。
- 返回按 dataset_id 索引的结果，不能自动把不同轴的数组相加。

默认只逐实验计算和评价。本轮不新建联合 likelihood；若已有联合入口要继续使用，必须明确重叠关系和共享 nuisance。未知独立性不能默认转化为可相加 chi²。预测全部实验不需要先解决联合统计关系。

## 5. 实验设定的唯一来源

先输出 PARAMETER_OWNERSHIP.md，逐项列出：

量名 → 物理语义/单位 → 权威定义或资源 → 实际消费函数 → 旧兼容出口 → 依赖失效范围。

至少覆盖：

- 距离、POT、源强、活时间或 kg·day；
- 有效探测器质量、材料组成、核素质量约定、核数；
- 源能量支撑、谱线、插值约定、入射态；
- 淬灭、分辨率、效率、接受率与阈值；
- 观测轴、分箱、数据、背景、误差、归一化 nuisance；
- 默认数值网格及复现理论设置。

实施规则：

1. 同一语义参数只能有一个权威值；旧名字可作为从定义生成的兼容出口。
2. 校准表的数值由校准资源拥有，定义拥有资源选择和解释；不要再抄一份表。
3. response.describe() 必须读响应实例参数，禁止手写与实际函数不同步的数值。
4. 通用 SNS 谱实现接受显式源参数；SNS_DATASETS 保留时只能是从权威定义派生的兼容视图。
5. CsI2021 的响应/效率参数必须可构造、可替换；同样的参数对象同时用于计算和记录。
6. 分箱由分析定义拥有；预测和观测数据通过显式映射核对。观测数据自身的原始分箱元数据保留，用于发现错误，不能通过改写它来“配合”预测。
7. 不从源码路径、当前工作目录或文件名猜测实验身份和资源。
8. 普通路径覆盖只允许资源定位变化；归一化、响应或选择变化必须重新验证并记录新定义指纹。
9. 避免导入环：定义的数据声明保持轻量；模型构造使用局部导入；旧兼容常数不要在模块导入时反向触发完整模型构造。

### 必须保留的历史差异

- CsI2017 的源元数据质量 14.57 kg 与计数采用的 14.6 kg，具有已知历史差异。分别用 legacy_source_metadata_mass_kg 与 effective_count_mass_kg 等明确字段记录，原路径分别复现；不自行决定哪一个是新的物理真值。
- CsI2021 的旧 raw 按每核素使用整台质量，新最终贡献已含材料权重与选择。兼容层继续分别表达。
- 已有近似统计定义保持近似标签。
- 旧 Fast 模板的历史单位约定保留明确 legacy 边界；新模型使用当前统一常数。禁止用输出修正系数掩盖不一致。

## 6. 数据、曝光和多探测器的物理约束

### COHERENT

沿用已有链：

运行期注量 → 单核反冲产额 → 探测器折叠 → 实际核数加权 → 分箱事件数。

源不得拥有探测器质量。源分量名不等于味索引，接受率键必须与实际分量身份匹配。

### CONUS+ 的 kg·day

当前数据只提供质量—时间积时，不允许虚构 detector_mass=1 kg、live_time=119 day 并把它们当作真实运行记录。

保留明确的 MassTimeExposure 表达，采用已有物理等价关系：

N[d,b] =
exposure_kg_day[d] × seconds_per_day ×
Σ_A nuclei_per_kg[A] ×
∫dT ∫dE flux_per_second(E) × dsigma_A/dT × B[d,A,b](T)。

具体实现可以复用现有 per-kg-day 率积分，随后施加曝光；必须有类型和归一化记录。不要把 kg·day 再同时乘实际质量和时间，也不要直接把 flux_per_second 塞进只接受 DetectorFluence 的合同。

如果最终要将该路线推广为共享积分能力，应独立实现显式的 rate + mass-time-exposure 路径，并验证它与现有注量 + 实际核数路径在可分离、常量条件下等价。不能改变 DetectorFluence 的物理含义来避免新增能力。

### 多探测器结果

CONUS+ 保留 C2/C3/C5 的有名子预测，每个十九箱，轴单位为其实际 eVee 约定：

- detector_predictions["C2"] 等保存分项；
- combined_prediction 只由明确的相同分箱求和规则产生；
- 当前十九箱统计输入只消费规定的 combined_prediction；
- 不伪造每探测器观测分配，也不对三个探测器分别使用同一十九箱数据重复拟合；
- 不把探测器轴当成源分量轴。

当前硬编码 NUCLEI_PER_KG 及 Ge73 复现约定先按原值迁移；其一致性另行记录，不能借架构重构修正物理解释。

## 7. 实施阶段 M0–M7

M 编号是本方案工程工作包，不替代项目 P01–P10。

### M0：版本与独立基线

动作：

- 核对实际工作目录、当前 commit、用户已有修改和适用 AGENTS。
- 当前 HEAD 若不同于审查提交，只读比较相关路径；不得回退或覆盖用户改动。
- 记录四个数据集当前 Slow、已有 Fast、统计入口及资源/代码哈希。
- 在变更前保存独立结果，覆盖代表性 SM、合法 NP、复系数/多味点，及各实验至少两组实际有意义的数值设置。
- 对已有接口忽略的数值参数明确标记，不能把无效参数变化称为第二网格。
- 保留现有参考不动。新增本次迁移基线应写入独立、获准位置。
- 区分已知失败、环境失败和新增回归。

通过条件：新旧对比的“旧”确实来自改造前实现；原始命令、资源与参数可复现。

### M1：修复实验身份误标

修改 statistics/predictors.py 的旧 Fast 路由：

- 规范化并验证请求的 dataset_id。
- 加载 kernel 后读取其真实 metadata.dataset。
- 请求与核身份不符时抛出包含双方 ID 的明确错误。
- 结果身份从校验后的对象构造，不把传入名字直接贴上去。
- 既有核缺少版本信息时标为 legacy identity，仅能验证已知字段；不能伪造新物理指纹。
- 检查 kwargs 是否实际消费；明确拒绝无法作用于已保存核的设置。
- 将相同身份约束扩展到后续新实验运行入口和统计评价入口。

验收：匹配可运行；Ar2020 + CsI2021 核、未知 ID、错误观测定义全部拒绝；原数值不变。

### M2：实验定义、加载器与轻量目录

建立上述最小结构和内置 catalog。

- 首先为四个精确 ID 建立独立定义与能力记录。
- catalog 仅保留定义的引用，惰性导入工厂；列实验不读取大型核响应文件。
- 新 load_experiment 始终返回 PreparedExperiment。
- 提供显式 registry 参数或 register_definition 机制，允许测试/调用方注入定义；不要 monkeypatch 全局 loader。
- 重复 ID 和别名冲突立即拒绝。
- 缺失统计资源只阻断统计，不阻断已有物理预测。
- 过渡包装通过统一入口时标 legacy_compat，尚未完成参数集中。

验收：四项身份与能力可列出；启用的定义实际构造可计算对象；旧 API 返回语义保留。

### M3：集中 CsI2021 设定，消除重复默认

- 新建独立定义并迁移运行、观测、效率和响应参数归属。
- 现有 make_csi2021_model 委托同一权威定义装配。
- SNS_DATASETS 的兼容值从定义派生；源公式保留参数化实现。
- 参数化 CsIGammaResponse 与淬灭模型，使 describe 和 density 使用相同参数。
- 统计数据和 likelihood 作为定义绑定，通用统计入口不再按名称选择。
- 保留新 Slow/Fast、缓存、旧 raw 与五个返回键。

验收：只改一个显式源参数或响应参数，实际输出、解析记录和核失效同步变化；原定义实例不受污染；新旧结果满足冻结标准。

### M4：完成 CsI2017、Ar2020 的独立模块

对每个数据集分别执行：

- 集中实验参数和资源引用。
- 让旧入口及新统一入口共同消费该定义。
- 从计算函数中移出实验选择，把复用的公式/算法提取到明确组件。
- CsI2017 保留确定性映射、Jacobian、阈值、插值和历史质量。
- Ar2020 保留现有响应函数、效率列选择、积分网格与观测单位约定；单位审计若发现争议单列，不直接更名改变统计解释。
- 数值策略可以专用，但参数必须显式，禁止退回全局名称查表。
- 保护已有 Fast；新统一入口标明其是 legacy 后端还是已有内容指纹后端，支持范围按实测发布。

验收：CsI2021 → Ar2020 → CsI2017 → CsI2021 的同进程切换；每项与独立旧基线一致；禁用某项不触发其资源加载。仅包装固定旧函数不能通过本阶段。

### M5：完成 CONUS+ 的定义与执行适配

- 仅迁移既有精确 dataset_id。
- 把源归一化、曝光、核数约定、阈值、响应参数、分箱和统计绑定集中到定义/资源。
- 接入既有源/率计算，保留分段 Gauss 求积、能区诊断和三探测器输出。
- 按第 6 节明确 MassTimeExposure 的归一化路线。
- 选择其现有 Fast 时声明实际数学表示；不能强行标成 CsI 的 operator_bilinear_v1。
- 每种 Fast 保存/加载、曝光/响应变化的失效逻辑单独验证。
- 原有函数保留兼容调用；内部接受从定义构造的不可变配置，不继续重复维护常数。
- 保留 existing paper benchmark 统计语义；若资源缺失明确 statistics unavailable，不把预测阶段一起阻断。

验收：从相同 load_experiment / predict_experiment 入口得到有名探测器结果；逐探测器/分量/能区/箱回归；combined 与分项求和一致；十九箱统计只计一次。

### M6：分析选择、资源隔离与可扩展性

- 实现 AnalysisSelection 的加载与严格校验。
- 按启用列表计算，结果按 dataset_id 返回。
- 资源根和资源解析器由调用方提供，不靠 cwd 或全局数据路径。
- 同一进程可加载两个同家族不同版本、不同资源根的实例。
- 运行记录与缓存按数据集/定义版本区分；物理内容相同的核是否可复用由物理指纹决定。
- 新增一个测试专用的独立数据集定义：非内置 ID、不同源分量名/能区或不同观测分箱，通过公开注册与运行入口求值，并有解析/独立参考。
- fixture 明确标为 synthetic，不注册为真实实验，不修改正式数据。
- 不实现未经授权的联合统计假设。

验收：增减已有数据集只修改选择配置；增加 fixture 不修改共享积分器、折叠器和统计名称分支。

### M7：兼容、发行、文档和最终报告

- 全套原有测试及新增任务验收通过，或明确报告未解决失败及范围。
- 检查旧函数签名、返回键、旧导入、核模板读取及公开统计调用。
- 实际从 wheel 或等价隔离安装中加载定义；项目外 cwd 下用显式外部资源运行。
- 检查惰性加载：未启用实验缺少可选文件时，不影响其他实验。
- 更新 README 和实际能力矩阵，清理“全部实验已模块化”等超出证据的描述。
- 提供可复制的单实验、跨实验、启停、实例覆盖示例。
- 提供项目级 Skill 操作说明，不创建或覆盖已安装的 SKILL.md，除非用户另行请求。
- 最终注明完成的是工程模块化，未新增物理验证结论。

## 8. 建议文件改动地图

下列路径相对 Gitup01；属于设计目标，部分文件当前不存在。实施者应根据已有结构微调名称并在 manifest 中记录，不能重复实现同一职责。

| 路径 | 动作与职责 |
|---|---|
| src/cevns_pyeft/experiments/definition.py | 新增最小定义、资源和能力数据结构 |
| src/cevns_pyeft/experiments/catalog.py | 新增惰性内置定义目录，不存物理数值 |
| src/cevns_pyeft/experiments/loader.py | 新增统一加载、资源解析、兼容性检查 |
| src/cevns_pyeft/experiments/runtime.py | 新增单实验及启用列表编排，不写实验名分支 |
| src/cevns_pyeft/experiments/selection.py | 新增选择配置与重复/未知字段检查 |
| src/cevns_pyeft/experiments/coherent/csi2021_definition.py | CsI2021 权威定义与资源引用 |
| src/cevns_pyeft/experiments/coherent/csi2017_definition.py | CsI2017 权威定义与资源引用 |
| src/cevns_pyeft/experiments/coherent/ar2020_definition.py | Ar2020 权威定义与资源引用 |
| src/cevns_pyeft/experiments/conus_plus/definition.py | 已有 CONUS+ 精确 ID 的权威定义 |
| src/cevns_pyeft/experiments/coherent/csi2021.py | 兼容工厂委托新定义 |
| src/cevns_pyeft/experiments/registry.py | 保留旧返回合同，暴露新目录/入口，避免混淆 |
| src/cevns_pyeft/experiments/coherent/sns.py | 源构造参数化；旧数据表改成派生兼容视图 |
| src/cevns_pyeft/detectors/csi2021.py | 响应和效率消费显式参数，describe 不重复手写 |
| src/cevns_pyeft/rates/differential.py | 旧响应函数保留兼容包装；理论接口不借机重写 |
| src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py | 旧入口消费定义；抽出参数化数值策略 |
| src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py | 旧入口消费定义；响应/效率/选择独立 |
| src/cevns_pyeft/experiments/conus_plus/source.py 等 | 现有源、响应、Slow/Fast/statistics 接收定义提供的实例设置 |
| src/cevns_pyeft/statistics/predictors.py | 优先身份校验，逐步委托统一运行层 |
| src/cevns_pyeft/statistics/datasets.py | 保留兼容 loader；数据与参数由实验定义/资源提供 |
| src/cevns_pyeft/statistics/likelihoods.py | 保留已验证公式；新增实验由绑定选择，不增长名称分支 |
| src/cevns_pyeft/statistics/adapters.py | 通用轴转换与实验专用兼容转换分清；不将 eVee 当 PE |
| src/cevns_pyeft/kernels/* | 保留新缓存合同；只为必要身份/策略适配修改 |
| tests/test_experiment_loading.py 等 | 验证真实公开入口与跨实验行为 |
| docs/experiment_modularization/* | 参数归属、能力、迁移结果及用户操作说明 |

不得为整理目录批量移动已有 data/experiments。现有平铺路径继续引用；新增真实发布才按当前仓库规范采用实验家族/dataset 两级目录。旧路径搬迁如有必要，必须独立列出兼容和恢复方案。

## 9. Fast、预测身份与缓存边界

区分两个身份：

- 物理核身份：由实际源、曝光、材料、响应、选择、分箱、理论表示和数值策略等内容决定。
- 实验分析身份：dataset_id、发布/分析版本、数据/背景/统计定义及预测归属。

两套统计数据可能使用相同物理预测，统计数据变化不应强制重建物理核。反过来，物理核可复用不意味着预测可以贴上任意实验名称。

新入口流程：

1. 加载实验定义并验证请求身份。
2. 解析实际模型和观测。
3. 若使用新 CompiledKernel，核对实际物理依赖。
4. 将得到的 Prediction 绑定到已加载的实验分析身份。
5. 统计评价核对这一身份和明确观测映射。

旧核缺少完整物理依赖时：

- 只保留原实验、原约定的兼容用途；
- 核对可核对的 dataset、分箱、单位、布局及资源信息；
- 不允许自定义物理覆盖项借旧核假装已经生效；
- 不把 dataset 名称一致写成完整物理兼容通过；
- 内容发生变化且无法证明兼容时重建或拒绝。

## 10. 验收用例：必须验证真实行为

| 编号 | 输入/动作 | 必须观察到的结果 |
|---|---|---|
| A01 | 列出内置实验 | 四个精确 ID；各能力与资源要求明确；不读取大型数据 |
| A02 | 分别 load_experiment 四个 ID | 同一外层类型，身份不混淆；已有预测能力可运行 |
| A03 | Ar2020 名称 + CsI2021 旧核 | 明确拒绝，不生成误标结果 |
| A04 | 未知 ID 或重复别名 | 明确拒绝 |
| A05 | A→B→A 跨实验运行 | 两次 A 一致，无全局参数污染 |
| A06 | 修改 CsI2021 的一个显式源强 | 对应计数缩放、记录变化、原核失效；其他实验不变 |
| A07 | 修改一个响应/效率参数 | 实际求值和 describe 同步，受影响预测/核更新 |
| A08 | 修改本次 enabled 列表 | 被禁用项不计算、不加载资源、不计入评价 |
| A09 | 禁用实验的资源缺失 | 不影响已启用且资料完整的实验 |
| A10 | 启用实验的必需资源缺失 | 精确报错，不静默跳过、不返回全零 |
| A11 | 相同数值分箱但不同分析身份 | 不能未经显式兼容映射交换统计数据 |
| A12 | CONUS+ 三探测器 | 有名结果与旧输出逐项一致，combined 求和一致 |
| A13 | CONUS+ kg·day 曝光翻倍 | 对应探测器计数翻倍；不会重复乘质量或时间 |
| A14 | 仅修改观测/误差 | 物理核不变，统计评价使用新数据 |
| A15 | 新增测试专用 dataset definition | 只新增定义/组件/测试和注册，不改公共算法即可运行 |
| A16 | 不支持的显式 Fast | 明确拒绝；auto 才能有记录地回退 |
| A17 | 新旧公开入口 | 保持各自签名、单位、分量及 raw 历史含义 |
| A18 | 项目外 cwd / wheel + 外置资源 | 可以发现定义并运行；资源不靠源码仓库相对路径 |
| A19 | 未消费覆盖项或不支持 YAML 结构 | 明确拒绝，不能默默忽略或变成字符串继续运行 |
| A20 | 当前统计含义与观测轴 | counts/PE 只转换一次；eVee 不误当 PE；背景减除数据不当作原始 Poisson 计数 |

测试应含真实旧数据回归与独立小模型基准。仅断言 dataclass 字段等于赋值、registry 出现名字或新旧包装器调用同一函数，不足以验收。

### 数值判据

- 同算法接口迁移首先使用本项目已经冻结的逐箱标准；计数候选标准仍是 atol_events=1e-12、rtol=1e-10，并在 M0 核对适用性。
- 截面、率、核矩阵分别按物理量级制定标准，不照搬事件数 atol。
- 现有 assert_array_equal 测试原样保留；环境差异不能自动修改为 allclose。
- 如跨环境位级测试失败，提供同环境旧/新实现对比、环境记录和独立数值验收。需要改变测试政策时单独提出依据。
- 工程回归与科学收敛分别报告，不把接口容差写成物理积分精度。

## 11. 交付物与阶段完成定义

最终应提供：

1. 代码改动和精确 create/modify/delete 清单。
2. PARAMETER_OWNERSHIP.md：所有实验设定的权威来源及实际消费者。
3. CAPABILITY_MATRIX.md：每个数据集的加载、Slow、Fast、统计、资源和兼容状态。
4. MIGRATION_REPORT.md：版本、环境、基线、逐项误差、失败及限制。
5. resolved_experiments.json：实际解析后的定义与内容指纹。
6. analysis_selection.example.yaml：启用和停用已有数据集。
7. 可执行的单实验、切换实验、替换参数和注册 fixture 示例。
8. Skill 操作说明：加载定义 → 识别 slot/数据集 → 兼容性检查 → 定向修改 → 依赖失效 → 实测报告。
9. 恢复办法：代码提交或获准逐文件备份；不删除旧数据或覆盖参考。

完成状态按事实分别记录：

- definition_centralized；
- unified_loading_verified；
- component_inputs_consumed；
- slow_regression_verified；
- fast_status（含 legacy_compat / unsupported）；
- statistics_status（保留 approximate 等含义）；
- selection_verified；
- release_verified。

全任务完成至少要求四个现有数据集达到定义集中、统一加载、已支持预测能力可运行、实际输入消费、选择启停验证。某项统计输入缺失可准确标记，不能把其余已完成内容一并否定；也不能将未完成的实验包装成全项目完成。

本任务不要求给所有实验新增同一种 Fast 表示，但要求保护已有 Fast 能力，并在统一入口中准确暴露其能力、身份和失效边界。

## 12. 项目工作流与授权的处理

本文件是工程方案，不是安装用 Skill，不修改 Master Skill 或正式 Physics Gate。

执行前读取当前项目：

- AGENTS.md；
- workflows/experiment-integration/AGENTS.md；
- workflows/experiment-integration/_shared.md；
- workflows/experiment-integration/skills/cevns-experiment/SKILL.md。

目标是迁移四个已明确的已有数据集，不能仅因同属 COHERENT 而混用身份，也不要把旧代码视为新的物理批准。按现有 Master 解析各数据集当前状态，复用有效授权与已有物理选择。

本方案不新增审批门槛。若实际执行环境的适用规则确实要求额外批准且当前授权不覆盖，先完成允许的只读核查和具体变更准备，再指出确切规则、路径、动作与受阻范围；不要把计划生成、只读审查或其他独立工作一起停掉。

不自动扫描 backup；不把备份当作物理基线；不修改 workflow 来绕开要求。数据目录布局遵守当前规范，已有平铺目录保持兼容。

## 13. 源码证据与方案使用边界

所有源码链接固定到已审查提交，后续执行以实际工作树为准：

- [CsI2021 工厂](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/src/cevns_pyeft/experiments/coherent/csi2021.py#L12)
- [旧 registry](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/src/cevns_pyeft/experiments/registry.py#L12)
- [统计 Fast 路由](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/src/cevns_pyeft/statistics/predictors.py#L126)
- [SNS 数据表](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/src/cevns_pyeft/experiments/coherent/sns.py#L33)
- [CsI 响应适配](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/src/cevns_pyeft/detectors/csi2021.py#L71)
- [新预测入口](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/src/cevns_pyeft/core/predict.py#L59)
- [新 Fast 编译器](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/src/cevns_pyeft/kernels/compiler.py#L200)
- [CONUS+ 曝光及计数](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/src/cevns_pyeft/experiments/conus_plus/slow_counts.py#L250)
- [项目规则](https://github.com/chino616/fawenfalnjdn/blob/d7182a116353faf0ba5ba581338db1d2a4b63074/Gitup01/AGENTS.md)

方案重点：让实验分析定义决定实际计算，让公共算法保持可复用，让用户和 Skill 能明确知道增加或移除哪个数据集会影响哪些输入、预测与统计结果。

