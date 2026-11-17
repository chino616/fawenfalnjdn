# experiments：实验身份、装配与统一运行入口

<!-- solar-singlebin-v321:start -->

## 太阳⁸B：单 bin独立能力

[solar_singlebin.py](solar_singlebin.py)的`load_singlebin`返回标准PreparedExperiment，通过独立scoped Catalog绑定三样本。SourceSpectrum/build_targets/TotalAcceptance/SingleBinExecutor对应onboarding Source/Target/Detector/Prediction；不导入旧solar_*多bin装配、不读其NPZ/Qy/D/B。`predict_experiment`和`evaluate_experiment`仍是通用主线入口；全局默认实验IDs不变。

<!-- solar-singlebin-v321:end -->

<!-- solar-nuclear-v31:start -->

## Solar SM：显式原子核Response入口

[solar_nuclear.py](solar_nuclear.py)提供`with_solar_nuclear_response`：绑定实际七核素JSON，复用共享SM振幅，再交给原有标准Runtime。PandaX先调用`with_pandax_mean_map`。不修改旧KN输入包，不用KN替代缺表核素；源/探测器输入保持原配置。

<!-- solar-nuclear-v31:end -->

[package_compiler.py](package_compiler.py) 从通用IR生成三文件；
[generic_input.py](generic_input.py)、[v2 Schema](generic_input.schema.json)、
[component_bindings.json](component_bindings.json)提供跨实验合同；[package 编译器入口](../../tools/compile_experiment_package.py)。

本目录回答“给定 dataset ID，到底运行哪套模型、用哪些数据”。持久身份清单由 [dataset_registry.json](dataset_registry.json) 管理，[manifest.py](manifest.py) 提供 Python 视图，目前为 CsI2021、CsI2017、Ar2020。

## 从 ID 到结果

| 文件 | 实际运行责任 |
|---|---|
| [catalog.py](catalog.py) | `ExperimentCatalog` 解析 ID/别名，延迟导入 definition，拒绝 archived/spec_only 的运行 |
| [definition.py](definition.py) | `ExperimentDefinition` 绑定物理设置、资源、观测轴、统计、数值配置和 `prepare` |
| [loader.py](loader.py) | `ResourceCatalog` 解析路径；`load_experiment` 调用 `prepare`，应用组件覆盖、快照与指纹，返回 `PreparedExperiment`；统计文件延迟读取 |
| [assembly.py](assembly.py) | 记录实际组件与执行器身份，防止只改实例却沿用旧缓存身份 |
| [input_package.py](input_package.py)、[input_package.schema.json](input_package.schema.json) | 正式三文件合同的只读结构/语义/资源校验与 MD 渲染；没有绑定或装配运行对象，详见[正式输入 schema](input_package.schema.json) |
| [model_registry.py](model_registry.py)、[model_bindings.json](model_bindings.json)、[package_components.py](package_components.py) | 受控物理模型绑定、公式/单位合同、参数消费记录与 NPZ 数组适配 |
| [package_loader.py](package_loader.py) | 显式两文件 `load_experiment_package` → 现有 Definition/Catalog/loader/PreparedExperiment；物理/统计内容投影分离 |
| [runtime.py](runtime.py) | `predict_experiment`、`compile_experiment`、`evaluate_experiment`、`predict_selection`；校验数值键、输出轴与身份 |
| [selection.py](selection.py) | 严格读取本次运行选择；禁用项不解析资源或执行预测，各实验结果分别返回 |
| [coherent/](coherent/README.md) | 三个活动实验的 definition/旧 API 均为正式 YAML/NPZ 的兼容适配层；没有独立实验参数权威 |
| [package_profiles.py](package_profiles.py) | v2 的显式装配与现有 Runtime executor；保留确定性 PE 与观测值相关 Gaussian 的不同语义，Fast 使用公共微分系数和同一折叠权重 |
| [package_compatibility.py](package_compatibility.py) | 旧字典/工厂接口；从包内资源调用原有 legacy builder 算术以保留冻结 Fast 数组，与 interface Fast 分别验证 |
| [specs.py](specs.py)、[registry.py](registry.py)、[base.py](base.py) | 外置说明 YAML 读取、旧 API 分派与效率等兼容实现；不是第二份活动清单 |

这种分工让“哪个实验可运行”“实验用什么输入”“算法如何执行”分别有明确入口。例如改变观测误差只影响评价，改变物理响应会使对应物理身份和缓存失效。

## 新建一个实验实现

真实新数据集先从[Master 工作流](../../workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md)确定物理范围和数据证据。获得对应范围的实现授权后：

1. 按[package 编译器入口](../../tools/compile_experiment_package.py)整理人填、AI 摘录或混合资料，形成同一 IR，记录模型、参数角色、单位、归一化、来源和缺失能力。
2. 使用 `package_compiler` 生成唯一三文件。先通过结构、绑定和资源检查；缺模型语义时新增经审查的公共 binding/profile，不能仅按 dataset 名复制物理代码。
3. executor 接收 `(experiment, point, backend, numerics, kernel)`，返回 `(combined_prediction, detector_predictions, raw_result, execution_record)`；总数、分量、轴必须满足 `runtime.py` 的检查。
4. 正式三文件放入根 `data/experiments/<实验族>/<dataset_id>/`，经 `definition_from_package` 接入已有 Definition/loader；测试放 `tests/test_<模块名>_contract.py`。声明 Fast 或统计能力前实跑对应验证。
5. 先用 `ExperimentCatalog(builtins=False).register(...)` 运行隔离实例。正式激活时在 `dataset_registry.json` 维护活动 entry，`manifest.py` 读取其 Python 视图，字符串模块路径相对于本包，最终导出 `DEFINITION`。

可参考 [synthetic_dataset.py](../../examples/experiment_modularization/synthetic_dataset.py)。[scaffold_experiment.py](../../tools/scaffold_experiment.py) 能创建 definition/execution、资源与能力说明及合同测试，但生成的是演示骨架，不会更新 manifest，也不产生真实物理模型。

三个活动实验的默认参数只在正式 YAML/NPZ 维护；definition 只做兼容适配。单次 what-if 使用受支持的 `dataclasses.replace` 或 `components` 覆盖；物化源谱的生成依赖改变时必须显式再生成，不能只刷新指纹。不要另建活动 ID 列表或用 `experiment.yaml` 的存在代替注册。相关检查见[迁移合同](../../tests/test_project_package_migration.py)、[统一运行测试](../../tests/test_experiment_modularization.py) 和[资源合同](../../tests/test_runtime_migration_contracts.py)。

## Dataset 管理入口

[DATASETS.md](DATASETS.md)是用户可见的动态注册/安装/文件归属表；[MANAGEMENT.md](MANAGEMENT.md)给出实际可执行命令。[dataset_registry.json](dataset_registry.json)集中保存唯一身份、installed/status、版本、definition、文件归属、依赖和资源声明；manifest.py读取它生成兼容条目，Catalog和兼容视图继续共用同一活动身份。

[management.py](management.py)实现包哈希、只读计划、事务备份、文件操作、README/资源同步、新进程验证与回滚/中断恢复；[registry_io.py](registry_io.py)用标准库约束登记结构、唯一路径和安全边界。需要维护新安装单元时更新准确归属和依赖，不能把实现指纹依赖直接视为独占文件。

---

[上一级](../README.md) · [项目总览](../../README.md)


## CsI2021 P04–P10 package 执行审计

[coherent/csi2021_package.py](coherent/csi2021_package.py) 是本次 revision-2 三文件审计的局部适配器，显式绑定现有 typed 组件；[csi2021_package_contract.json](coherent/csi2021_package_contract.json) 只约束模型/单位/轴，不保存第二套物理数值。同期通用 package_loader 的默认迁移独立保留。阶段证据、当前与固定版本差异见[执行报告](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/11_FINAL_EXECUTION_REPORT.md)。

`input_package.render_physics` 与 `generic_input.render` 共用报告选择和数学格式。
H3 报告元数据使用受严格校验的 `lab.physics_report` namespace；既有输入沿用显式绑定声明，
不按模型名猜测公式。`package_compiler.write_package` 在目标目录创建继承 ACL 的临时文件，
支持失败恢复及只读 YAML/NPZ 的两份 MD 更新，见[package 编译器入口](../../tools/compile_experiment_package.py)。

现有 render_physics / generic_input.render 通过 summary=True 选择精简视图；
默认详细视图完整记录实验侧公式与数据，共享模块只列实际 ID/配置。
两视图的单一规范位于 workflows/_shared/references/onboarding/，
符号引用同时核对精确 Parameter ID 与 NPZ key；运行期仍只读取 YAML/NPZ。

<!-- solar-b8-sm-20261107:start -->

## Solar B8 SM profile

新增[solar_b8.py](solar_b8.py)与只读文件合同[solar_input.py](solar_input.py)：显式solar_b8_sm_v1输入包走标准Runtime；XENONnT用官方基底，PandaX只提供真实反冲诊断。包经Compiler生成；不按实验名复制核心算法，不无条件激活PARTIAL包。

<!-- solar-b8-sm-20261107:end -->

<!-- solar-vector-20261108:start -->

## Solar B8 vector benchmark

[solar_vector.py](solar_vector.py)用已有interaction组件替换接口加载太阳8B的V/B−L固定点；保留原正式SM输入包、源、靶与Response。`load_solar_light_vector`或`with_solar_light_vector`返回标准PreparedExperiment。

<!-- solar-vector-20261108:end -->

<!-- pandax-simplified-20261110:start -->

## PandaX US2：显式简化平均映射

[solar_mean_map.py](solar_mean_map.py)以`with_pandax_mean_map`绑定nominal Qy资源、独立观测轴与代码指纹，再交由标准Runtime和共享SM反冲积分生成八箱谱。原正式包、原Response分支与全局默认注册保持原状；c=1直接输出不暗含有效校准。

<!-- pandax-simplified-20261110:end -->

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

solar_nsi.py独立scoped loader/Slow/Fast调用，复用只读单bin表；不改全局默认实验。

[完整新onboarding：实际输入、标准引文、物理与程序](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->
