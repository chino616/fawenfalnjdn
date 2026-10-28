# 逐文件职责迁移与修改计划

状态：DESIGN。下列路径相对于 Gitup01；新增路径尚不存在。
实际修改前复读当前函数并运行 `rg` 核对调用者，不能依赖旧行号。阶段见 [08](08_IMPLEMENTATION_PHASES.md)。

## 1. 新目录的最小集合

| 建议新增路径 | 公开责任 | 阶段 |
|---|---|---|
| `src/cevns_pyeft/contracts/source.py` | RunExposure、DetectorFluence、谱线/支撑/入射态合同 | R1 |
| `src/cevns_pyeft/contracts/target.py` | TargetInventory/TargetIsotope | R1 |
| `src/cevns_pyeft/contracts/interaction.py` | InteractionModel、Kinematics、截面结果 | R1 |
| `src/cevns_pyeft/contracts/observation.py` | 观测模型、入箱概率、轴和分箱 | R1 |
| `src/cevns_pyeft/contracts/prediction.py` | RecoilYield、Prediction、分量记录 | R1 |
| `src/cevns_pyeft/contracts/modules.py` | ModuleDescriptor、兼容性错误与模型记录 | R1/R3 |
| `src/cevns_pyeft/contracts/parameters.py` | TheoryPoint、StateParameters、IntegrationSettings 等跨边界参数对象 | R1 |
| `src/cevns_pyeft/sources/sns.py` | SNSLegacySource 显式参数适配 | R1 |
| `src/cevns_pyeft/targets/materials.py` | 材料组成到核数，CsI 工厂 | R1 |
| `src/cevns_pyeft/theory/li2026/adapter.py` | 包装现有截面和响应数据 | R1 |
| `src/cevns_pyeft/detectors/csi2021.py` | CsI 映射、展宽、效率的明确实现 | R1/R2 |
| `src/cevns_pyeft/detectors/selection.py` | 选择模型、legacy 分量接受率 | R1/R2 |
| `src/cevns_pyeft/rates/recoil.py` | 通用源能量积分，输出每核反冲产额 | R2 |
| `src/cevns_pyeft/rates/folding.py` | 物理概率折叠与明确的 legacy 数值策略 | R2 |
| `src/cevns_pyeft/core/model.py` | ExperimentModel 组装对象；引用 contracts 中的参数类型 | R3 |
| `src/cevns_pyeft/core/predict.py` | validate/predict/assemble 调用链 | R2/R3 |
| `src/cevns_pyeft/experiments/coherent/csi2021.py` | make_csi2021_model 默认组装 | R3 |
| `src/cevns_pyeft/statistics/adapters.py` | 带轴 Prediction 到现有统计接口 | R3 |

这些是职责建议，不要求机械创建空壳文件。强相关且很小的合同可合并，但须在实施记录中给出最终唯一位置，避免同一对象多处定义。
新增包添加必要 `__init__.py`，只导出稳定公开符号；不依赖 wildcard import 完成新架构路由。

## 2. 现有文件如何处理

| CURRENT 文件与符号 | DESIGN 处理 | 必须保护 |
|---|---|---|
| `experiments/coherent/sns.py::SNSDataset/SNS_DATASETS/loadNeutrinoEmpiricalFluxSNS` | 保留旧入口；抽出接受显式配置的源构造；新 source adapter 使用同一计算实现 | 原数据集参数、插值和 muLine 权重 |
| `experiments/coherent/sns.py::sns_component_state` | 复用；由新组件关联入射态 provider | nu/antinu 的现有语义 |
| `sources/state.py::NeutrinoState` | 复用校验；新查询边界补充真实能量坐标和参数依赖 | 现有状态测试与旧 import |
| `propagation/base.py::PropagationState` | 将其作为能量态适配的既有基础 | 只输出传播态，不混入事例数 |
| `experiments/base.py::TargetComponent` | 不直接把 weight 改义；新增明确核数对象，再保留旧兼容 | 旧调用者参数含义 |
| `rates/differential.py::eee_quenching_csi/p_smearing_csi` | 实验专用响应最终归 detector；原位置保留兼容转发 | 原函数签名、数值和默认绑定行为 |
| `rates/differential.py::differential_cross_section_nn` | 首先包装；逐步显式穿透必要理论参数 | shape、单位、SM 合并、rho 收缩 |
| `rates/counts.py::empirical_dNdPE_response_csi/bin_events_csi` | 新 recoil/folding 分工；原函数保留，待调用者迁移后再决定委托 | PE 插值、求积、截断顺序、历史输出 |
| `rates/counts.py::_rate_per_kg/_folded_counts/_er_grid` | R0–R3 不破坏其旧用途；新通用接口不依赖其中的 SNS 假设 | CsI2017/Ar2020 |
| `slow_counts_csi2021.py::slow_counts_csi2021` | 新链验证后变为工厂+predict+旧结果适配 | 所有返回键、默认参数、raw 语义 |
| `slow_counts_csi2021.py::efficiency_csi2021/DEFAULT_ACCEPTANCE` | 确立唯一实验实现/配置归属，旧位置兼容导出 | 不产生两套可变默认 |
| `kernels/builder.py` | R4 去除共用执行对具体实验的反向依赖；共用模型输入与 folded data | 算符顺序、通道、相位符号、归一化 |
| `kernels/reconstruction.py` | 分量及靶布局来自模型记录；去除固定源名字/材料求和 | full/pair 重建一致性 |
| `kernels/storage.py` | 增加物理内容兼容检查；旧文件通过明确 legacy 路由 | 不给旧模板补假的新指纹 |
| `experiments/registry.py` | 注册工厂及独立能力，保留旧发现函数 | spec 可发现不等于可计算 |
| `statistics/predictors.py` | 调用统一 predict 及适配器，避免复制实验路由 | 旧统计结果与单位转换 |
| `statistics/observables.py` | 保留旧一维 API；新轴对象在适配边界使用 | 不擅自重释旧数据语义 |
| `core/engine.py` | 保留兼容 re-export，不加入新计算公式 | 下游旧 import |

## 3. 后续条件性文件

R4 可新增 `kernels/compiler.py`、`kernels/fingerprint.py`，但物理系数公式不应再复制一份。
R5 核对实际模块描述、替换和依赖。R6 可新增运行记录与模型描述的只读导出命令；Skill 只读它们进行计划和验证，不作为 runtime 依赖。

## 4. 迁移顺序

1. 先新增合同、适配器和独立新入口，原入口继续运行。
2. 新旧结果按固定输入比较，通过后修改 CsI2021 入口委托。
3. 单独修改统计调用桥；比较旧统计值，不修改数据和公式。
4. 新 Fast 编译/重建接入同一模型，再处理存储和缓存检查。
5. 最后才删除确实无使用者的内部重复逻辑；删除不属于初始默认动作。

## 5. 改动边界检查

对修改的公共符号运行 `rg -n '<symbol>' src tests`，列出直接调用方与 import。
新增通用 rates、contracts 不得 import `experiments.coherent.*`。兼容的旧 counts 文件在迁移期可以保留，不能据此误判所有过渡工作失败。
可对目标新增模块做 AST import 检查，白名单只允许标记清楚的实验装配和 legacy adapter。

CsI2017 当前直接使用 14.6 的计数归一化，而 SNSDataset 写 14.57；这属于需保留并记录的既有行为，不在第一条 CsI2021 接口迁移中自动统一。
Ar 现有展宽/效率定义也不能因为名字相近就直接改用 CsI 的通用实现。

## 6. 原项目文件保护

不移动已有平铺 data 目录，不扫描 backup，不修改工作流 Gate，不修改已存在参考数组。
若后续属于实验接入并触发仓库备份/写入流程，按实际路由执行，见 00。
每个 task 的最终 create/modify/delete 清单写入任务卡；本表是候选范围，不是任意修改授权。
