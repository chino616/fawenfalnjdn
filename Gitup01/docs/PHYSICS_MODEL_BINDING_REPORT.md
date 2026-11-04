# Task 03 — Controlled Physics Model Binding

2026-11-04；branch `refactor/07-gitup01-20261104`；HEAD
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。开始时已有 Task 01/02 修改及并行候选文件，
未提交、推送或重置。三个用户指定保留的候选文件没有被本任务编辑、导入或用作实现。

## 范围与实现

读取了任务规则/顺序、Task 03、runtime-maintenance 流程、实际 definition/catalog/loader/
assembly/runtime、source/state、target、ResponseW、Li2026 matching/amplitude、differential、
folding、detector 和 Gaussian profiler。复用现有模型合同，没有第二个实验 Catalog 或 Runtime。

新增 [model_registry.py](../cevns_pyeft/experiments/model_registry.py)、
[受控规格](../cevns_pyeft/experiments/model_bindings.json)、
[数组适配器](../cevns_pyeft/experiments/package_components.py) 和
[测试](../tests/test_physics_model_registry.py)。pyproject 登记公共绑定 JSON 包资源。
规格只有公式指纹、单位/资源 slot、依赖、输出、边界和能力信息，没有实验标量副本。
实现 key 是项目内部函数；输入文档不能指定 import/callable，也不能执行公式字符串。

| model_id | 实际消费者 / 约束 | 绑定结果 |
|---|---|---|
| sns_fluence_legacy_v1 | 明列 spherical_fluence 推导；POT/yield/geometry 一次 | BOUND_AND_TESTED |
| sns_michel_tabulation_legacy_v1 | ArrayContinuum；NPZ 物化注量；线性插值、范围外零 | BOUND_AND_TESTED |
| sns_prompt_line_v1 | FluenceLine；分离谱线能量与积分注量 | BOUND_AND_TESTED |
| sns_fixed_state_v1 | ArrayState/IncidentStateBatch；保留 antinu；拒绝扫描态参数 | BOUND_AND_TESTED |
| csi_target_inventory_v1 | TargetInventory；读取经校验派生核数，质量守恒，无二次乘质量 | BOUND_AND_TESTED |
| li2026_sm_left_v1 | 原 _sm_left_dim6；显式共同理论快照检查 | BOUND_AND_TESTED |
| li2026_matching_v1 | 原 left_to_ci；np、一体流、原 c10 约定 | BOUND_AND_TESTED |
| elastic_kinematics_v1 | 原 ElasticKinematics；A*amu 质量约定 | BOUND_AND_TESTED |
| nuclear_np_polynomial_v1 | NPZ→ResponseW；p/n/power 轴；不读响应 JSON | BOUND_AND_TESTED |
| li2026_R_W_kernel_v1 | 原 flavor_kernel_onebody_li2026；不执行 RHS | BOUND_AND_TESTED |
| li2026_dsigma_v1 | ArrayInteraction→原 differential_cross_section_nn；cm²/keV | BOUND_AND_TESTED |
| csi_quenching_legacy_v1 | 原 eee_quenching_csi；q1..q4 顺序 | BOUND_AND_TESTED |
| legacy_csi_gamma | 原 CsIGammaResponse/p_smearing_csi；shape-rate | BOUND_AND_TESTED |
| csi2021_logistic_legacy | 原 CsI2021Efficiency；零下限，实际折叠检查上限 | BOUND_AND_TESTED |
| legacy_component_acceptance | 原 LegacyComponentAcceptance；按 component 一次 | BOUND_AND_TESTED |
| legacy_csi2021_v1 | 原 core.predict/legacy_density_fold；固定网格 trapezoid | BOUND_AND_TESTED |
| gaussian_two_pull_legacy_v1 | 原 profile_gaussian_two_pull；预测除箱宽一次 | BOUND_AND_TESTED |

BindingSession 记录实际 adapter 参数读取、资源读取和成功调用；report 区分 specified/bound/
executed/reference_only/end_to_end_verified。输入里的 consumed 标志不是证据。
所有 active 参数均有受控 consumer slot；资源生成输入只作为物化依赖校验，不能误报为运行时重乘。
本任务所有 end_to_end_verified 均为 false，完整包尚未装配。

公共算法当前闭包使用引擎常数与 DEFAULT_LECS。本版本将包中的共同理论值显式绑定为
不可任意替换的版本快照：不一致报错，不静默忽略。改变这些值需要新引擎绑定；不能把
“输入包值可编辑”推广成“任意 LEC 扫描已支持”。不活跃 LEC 不读取、不报 consumed。

## 验证与限制

实际命令使用 `F:/Work/.codex_conda_envs/codex-py311/python.exe -B -m pytest`。
`test_physics_model_registry.py`、`test_li2026_units_contract.py`、`test_li2026_amplitude_flavor.py`、
`test_nuclear_response_convention.py` 和 `test_interface_contracts.py`：**71 passed**。
覆盖全部 17 个模型、真实微分截面、未知模型/任意公式、单位/consumer/循环/shape/轴拒绝，
13 个探测器参数的直接中间量扰动、反中微子标签、快照不符拒绝及全部核响应多点比较。

开发时修正了 ArrayState 的关键字参数和测试中 acceptance_mu 扰动超出 [0,1] 的问题，
没有放宽模型边界或数值容差。碘 M_nn(0) 残差原样保留；SigmaPDelta 继续因粒子响应零而排除。
一般反中微子 EFT、官方 likelihood 与科学发布没有获得批准。

组件/模块化回归另行执行并在后文追加实际结果。第一次收集受到并行 registry 中不支持的
`schema` owned-file role 阻断；准备最小修正时该项已被其他写入修好，因此本任务没有覆盖它。
观察到同工作区仍有外部写入；保留三文件指本任务不编辑，不声称外部写入被锁住。

修改既有文件前的恢复点登记在 backup/task03-model-binding-20261104/ 与 BACKUP_MANIFEST.md。
最终 registry+component_replacement+experiment_modularization：**80 passed**。
其中 registry 测试与前述 71 项重叠，不累加成独立测试数；四份受影响 Markdown 的 60 个
本地链接检查通过。保护清单正在被外部写入同时更新，本任务的更新因上下文变化被拒绝，
没有强制覆盖；新增绑定文件的最终登记在后续统一核对时完成，暂不记全局 QA PASS。
数学算法、数组、默认 CsI2021 Definition 和物理语义未改变。下一步 Task 04 建立显式两文件
Loader，仍不切换默认入口；消费状态和完整运行证据由后续任务单独产生。
