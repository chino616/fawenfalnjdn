# tools：显式执行的构建、审计和创建工具

[最新实验导航生成与校验工具](<latest_experiments.py>)。本入口仅列当前选定分析；不同方法的输入、代码、结果和审核范围分别说明。

<!-- solar-singlebin-v321:start -->

## 太阳⁸B：单 bin独立能力

单bin：[prepare_solar_b8_singlebin.py](prepare_solar_b8_singlebin.py)离线create-only提取PDF/数据；[run_solar_b8_singlebin_benchmark.py](run_solar_b8_singlebin_benchmark.py)独立Slow/收敛/统计/PNG；[build_solar_b8_singlebin_onboarding.py](build_solar_b8_singlebin_onboarding.py)同源生成新文档、默认check；[promote_solar_b8_singlebin.py](promote_solar_b8_singlebin.py)显式--write备份并登记canonical分支；[validate_solar_b8_singlebin.py](validate_solar_b8_singlebin.py)核对输入/实际快照/保护与阶段；[validate_solar_b8_singlebin.mjs](validate_solar_b8_singlebin.mjs)渲染/链接/公式/实际跳转。多bin：[run_solar_b8_multibin_benchmark.py](run_solar_b8_multibin_benchmark.py)只委托原核表多bin运行器。兼容旧SM入口支持`--analysis singlebin|multibin`；无analysis保持旧多bin行为。两者输出根分别solar_b8_singlebin/与solar_b8_sm/。

<!-- solar-singlebin-v321:end -->

<!-- solar-nuclear-v31:start -->

## Solar SM核Response：计算与onboarding

[run_solar_b8_sm_benchmark.py](run_solar_b8_sm_benchmark.py)默认调用[核表SM运行器](run_solar_b8_nuclear_benchmark.py)，`--legacy-kn`才回到历史KN。核表SM运行器保存同核素同质量KN对照、通道分解和独立网格收敛；必须指定新输出目录。[build_solar_b8_onboarding_v3_1.py](build_solar_b8_onboarding_v3_1.py)从结果/同一证据链生成v3.1，`--check`只读。v3.0生成器接管后只核对冻结历史。[build_pandax_nuclear_teaching.py](build_pandax_nuclear_teaching.py)生成全部11份独立M-only教学代码；[validate_pandax_nuclear_teaching.py](validate_pandax_nuclear_teaching.py)在空目录单文件执行并核对来源/主结果。[validate_solar_b8_nuclear_rendering.mjs](validate_solar_b8_nuclear_rendering.mjs)检查新报告的数学、导航与布局。

<!-- solar-nuclear-v31:end -->

<!-- solar-onboarding-v3:start -->

## Solar B8 onboarding v3.0

[build_solar_b8_onboarding_v3.py](build_solar_b8_onboarding_v3.py)从实际正式包、P00/P01及保存的SM/矢量结果同源生成完整总文档和两套详细/精简/用户资料；`--check`只读核对，`--validate`检查实际来源/文档/旧文件保护并只写本轮QA；科学Gate/输入/Runtime不变。[validate_solar_b8_onboarding_v3.mjs](validate_solar_b8_onboarding_v3.mjs)验证实际数学渲染、目录跳转、公式编号与窄屏布局。

<!-- solar-onboarding-v3:end -->

[package_build.py](package_build.py)由setuptools显式构建调用，仅将registry声明的正式三文件复制到构建产物；
源码data仍为唯一权威，不导入工作流或复制论文/台账。

[compile_experiment_package.py](compile_experiment_package.py) 将显式IR和声明数组编译为三文件，
支持只读check、默认create-only及显式覆盖备份，不负责论文理解或人工科学批准。

[validate_package_standalone.py](validate_package_standalone.py) 离线构建/安装隔离引擎，以 import/file guard
验证两文件独立运行、默认网格、扰动及十种篡改拒绝；输出目录必须全新，原源码不删改。

这里的脚本由维护者从项目根目录运行，不由 `predict_experiment` 自动调用。物理算法仍在 `cevns_pyeft/`；把管理工具分开，可以看清每个操作读取或生成什么文件。

| 脚本 | 实际输入、操作和输出 |
|---|---|
| [validate_experiment_input.py](validate_experiment_input.py) | 只读校验正式 package v1 的 JSON Schema、参数角色/消费者、派生与物化资源指纹、NPZ 和 Physics MD；`--check-schema` 校验 schema 自身；不装配 Runtime |
| [csi2021_input_contract.py](csi2021_input_contract.py) | 由 CsI2021 builder 调用的 Pilot/1→正式/1 元数据迁移适配；105 项数值和 NPZ 保持不变；不是通用生成器 |
| [build_csi2021_onboarding_pilot.py](build_csi2021_onboarding_pilot.py) | 仅为旧九箱 CsI2021 从当前 definition/实际模型和资源提取三文件试点；默认/`--check` 只读核对模型/参数/数组/MD 和当前源码，`--write` 只创建三份正式输入及审计报告并拒绝覆盖，`--render-md` 从已有 YAML/NPZ 渲染 MD 到 stdout；不是 Runtime Loader |
| [validate_resource_manifest.py](validate_resource_manifest.py) | 用 `--root` 指定包含 data/ 的目录，结合 Catalog/definition 与资源清单检查 ID、路径、覆盖作用域和 SHA256；`--json-out` 可保存报告 |
| [validate_docs.py](validate_docs.py) | 只读检查 Markdown 本地文件链接；`--files` 精确检查受影响 README/文档，优先于 `--scope docs/all`；默认跳过 backup、outputs 与缓存，`--json-report` 保存结果；不自动改写内容 |
| [readme_maintenance.py](readme_maintenance.py) | `plan` 按 Git/快照生成目录分组影响清单；`snapshot` 保存当前文件基线；`sync/check --readmes` 同步/检查明确选定的 README 自动清单区，保留人工说明并备份；不删除文件或提交 Git |
| [update_skill_library.py](update_skill_library.py) | 默认/`--check` 只读核对 [Skill 总表](../cevns_pyeft/SKILLS.md)；`--write` 从 catalog 展示摘要和 WORKFLOW 实际引用刷新标记区，保留人工规则，备份旧文件并登记；不改保护哈希或 runtime |
| [scaffold_experiment.py](scaffold_experiment.py) | 按 `--root`、`--dataset-id`、`--module-name` 创建演示实验包与合同测试，拒绝已存在的目录/ID；不注册到内置 manifest |
| [build_wheel.py](build_wheel.py) | 离线、无依赖安装地构建 wheel，再安装到项目内独立 target；写 `outputs/release/` 的 wheel、日志和 `wheel.json` |
| [verify_wheel.py](verify_wheel.py) | 读取 `wheel.json` 的安装路径，在项目外 cwd 用 `python -I` 检查三实验预测，写 `outside_cwd.json/log` |
| [workflow_validation/](workflow_validation/README.md) | 工作流校验器直接读取的保护清单和历史路径例外 |

## 常用命令与实际副作用

```powershell
python tools/validate_resource_manifest.py --root .
python tools/validate_docs.py --scope docs
python tools/scaffold_experiment.py --dataset-id DemoReadme --module-name demo_readme --root outputs/scaffold-demo
```

第三条命令会在指定根下创建 `cevns_pyeft/experiments/demo_readme/` 的 `__init__.py`、`definition.py`、`execution.py`、`resources.yaml`、`capabilities.yaml`，以及 `tests/test_demo_readme_contract.py`。它是 synthetic 工程骨架；后续需实现模型、资源和能力，并先用 custom catalog 验证。

构建顺序是 `python tools/build_wheel.py`，然后 `python tools/verify_wheel.py`。后者当前在项目旁 `CONUS-Backup/_migration/wheel_outside_cwd` 创建外部工作目录；这个目录名是脚本的历史路径，不表示恢复 CONUS。当前副本内旧 `wheel.json` 指向旧位置，验证前需先在当前根重新构建。

## 管理与新增文件

所有工具和说明执行[文件与 README 联动规则](../workflows/_shared/policies/file-lifecycle.md)：文件变化和相应目录条目、命令及上级导航在同次任务中维护。检查本次受影响文档可运行 `python tools/validate_docs.py --files README.md tools/README.md`；该命令只报告失效链接，新增文件的用途覆盖、正文裸路径和消费者仍须按变更清单核对。

大批量维护的基线、目录分组、自动清单区和 Git 复查步骤见[维护流程](../workflows/cevns-pyeft/definitions/repository-maintenance/WORKFLOW.md)。报告默认不覆盖；`sync` 是显式写操作，会在 backup 创建改动前 README 副本并追加清单，计划与验收保持只读。

新的跨实验维护命令放 `tools/<动词_对象>.py`，提供明确参数、入口函数、退出码和报告位置；写清是否创建/覆盖文件。实际计算应导入包内函数，不在工具中复制 EFT 公式。只生成当前用户结果的示例放 `examples/`，仅作绘图的脚本放 `论文图NoteBook/`。

新增工具后在此登记命令和副作用；文件解析、身份或迁移工具应有成功与错误输入检查，参考 [test_manifest_and_migration_tools.py](../tests/test_manifest_and_migration_tools.py) 和 [test_runtime_migration_contracts.py](../tests/test_runtime_migration_contracts.py)。机器配置放明确目录并由消费者直接读取，不能隐藏在历史说明副本中。

## Dataset 拆装工具入口

CsI2021 三文件试点的使用环境需要项目依赖；本次使用
`F:/Work/.codex_conda_envs/codex-py311/python.exe`（系统默认 Python 缺 SciPy）。
例如从项目根运行 `python -B tools/build_csi2021_onboarding_pilot.py --check`。
当前输入包见 [CsI2021 输入目录](../data/experiments/COHERENT_CsI/CsI2021/README.md)。该脚本保留历史提取／输入构建用途，不是已删除工程报告的当前检查入口。
它仅覆盖旧九箱数据集，没有给通用 Loader、安装器或 registry 添加新格式。

Dataset完整管理由运行包CLI提供：`python -m cevns_pyeft.cli datasets --help`。命令、文件归属、计划、安装/卸载与回滚见[管理说明](../cevns_pyeft/experiments/MANAGEMENT.md)；不在tools再维护第二套活动ID或另一个安装器。

---

[上一级](../README.md)

<!-- readme-inventory:start -->
**当前活动目录内容（自动维护区）**

备份、生成结果和历史/冻结证据不列入此区；用途见人工说明。

| 路径 | 类型 |
|---|---|
| [workflow_validation/](workflow_validation/README.md) | 目录 |
| [build_csi2021_onboarding_pilot.py](build_csi2021_onboarding_pilot.py) | 文件 |
| [build_wheel.py](build_wheel.py) | 文件 |
| [csi2021_input_contract.py](csi2021_input_contract.py) | 文件 |
| [readme_maintenance.py](readme_maintenance.py) | 文件 |
| [run_csi2021_package_phases.py](run_csi2021_package_phases.py) | 文件 |
| [scaffold_experiment.py](scaffold_experiment.py) | 文件 |
| [update_skill_library.py](update_skill_library.py) | 文件 |
| [validate_docs.py](validate_docs.py) | 文件 |
| [validate_experiment_input.py](validate_experiment_input.py) | 文件 |
| [validate_package_standalone.py](validate_package_standalone.py) | 文件 |
| [validate_resource_manifest.py](validate_resource_manifest.py) | 文件 |
| [verify_csi2021_package_release.py](verify_csi2021_package_release.py) | 文件 |
| [verify_wheel.py](verify_wheel.py) | 文件 |
<!-- readme-inventory:end -->


## CsI2021 P04–P10 可复现执行

[run_csi2021_package_phases.py](run_csi2021_package_phases.py) 读取指定三文件包，调用现有全物理 Runtime，保存阶段 JSON、逐源/核素/bin 数组、实际网格与统计；--profile 可单独计算收敛网格，--implementation-root 可固定已审计实现。默认输出本次 run 目录，同身份结果校验后复用；不修改输入。

[verify_csi2021_package_release.py](verify_csi2021_package_release.py) 用 --mode wheel 或 lifecycle 和一个新的 --output 目录执行离线构建/本地 target 安装、外部 cwd 或隔离拆装；拒绝已存在输出目录，不改变全局 Python 或 canonical dataset 安装状态。
# Active dataset package migration tools

[migrate_legacy_input_packages.py](migrate_legacy_input_packages.py) is an explicit,
one-dataset acquisition adapter for a definition that has not yet been migrated.
It writes an annotated IR and delegates three-file generation to the common
[compiler](compile_experiment_package.py). Already migrated datasets use their
saved IR and compiler `--check`.

[validate_project_packages.py](validate_project_packages.py) builds an sdist and
wheel with the existing [build hook](package_build.py), verifies all registered
formal files and runs installed datasets from an external cwd. It also tests
editable installation and a temporary engine with old definitions, legacy
defaults and bundled data removed. Run with a fresh output directory:
`python -B tools/validate_project_packages.py --output <fresh-directory>`.
Source files and global Python are not removed or installed into. Reports
distinguish approximate statistics, frozen compatibility and scientific approval.

现有 `compile_experiment_package.py --output <package> --md-only --overwrite`
只读现有 YAML/NPZ 并更新详细/精简两份 Physics MD；`--md-only --check` 只读核对。
完整编译仍用 `--draft/--arrays`。输出与权限状态及恢复行为见
[package 编译器入口](compile_experiment_package.py)。

<!-- solar-b8-sm-20261107:start -->

## Solar B8 SM profile

[prepare_solar_b8_mainline.py](prepare_solar_b8_mainline.py)备份/接入；[build_solar_b8_packages.py](build_solar_b8_packages.py)调用既有Compiler（--check只读，--overwrite按原Writer备份）；[run_solar_b8_sm_benchmark.py](run_solar_b8_sm_benchmark.py)标准Runtime/收敛/出图；[finalize_solar_b8_mainline.py](finalize_solar_b8_mainline.py)同源报告；[validate_solar_b8_mainline.py](validate_solar_b8_mainline.py)检查正式包、阶段schema、双文件可移植运行和旧文件保留；[validate_solar_b8_rendering.mjs](validate_solar_b8_rendering.mjs)检查Markdown数学、目录跳转及窄屏渲染。

<!-- solar-b8-sm-20261107:end -->

<!-- solar-vector-20261108:start -->

## Solar B8 vector benchmark

[run_solar_b8_vector_benchmark.py](run_solar_b8_vector_benchmark.py)读取显式卡、执行标准Slow、收敛、带符号分解与出图；--resume仅复用相同参数/物理指纹。[finalize_solar_b8_vector_benchmark.py](finalize_solar_b8_vector_benchmark.py)维护同源v2.3/阶段/导航，--validate-only只核验并写本轮QA。[validate_solar_b8_vector_rendering.mjs](validate_solar_b8_vector_rendering.mjs)检查公式、链接、实际目录点击与420px排版。

<!-- solar-vector-20261108:end -->

<!-- pandax-simplified-20261110:start -->

## PandaX US2：SM简化八箱计算

[run_pandax_us2_simplified_benchmark.py](run_pandax_us2_simplified_benchmark.py)读取[独立方法卡](../data/benchmarks/pandax_us2_simplified_v1/benchmark.input.json)，通过标准Runtime计算八箱，分别验证T/Eν收敛；保留固定SSM的c=1预测、后验拟合谱缩放参考、各核素数组、来源哈希和图。观测点显示68.27%中心Poisson（Garwood）误差棒。默认新运行目录，不覆盖旧运行。

<!-- pandax-simplified-20261110:end -->

<!-- xe132-representative-plot:start -->

## Xe132代表近似结果图

[plot_solar_b8_xe132_representative.py](plot_solar_b8_xe132_representative.py)读取原核Response运行的逐Xe132信号分量，按整份靶质量的纯Xe132核数换算，再与原七核素谱比较。保持通量/曝光/探测器处理；输出信号、S+B与观测误差棒、逐箱差异、PNG/PDF及逐项来源。运行时指定新的`--output`目录；不修改主计算输入。

[本轮图与来源](../outputs/solar_b8_sm/20261110_xe132_representative_plot/README.md)。

<!-- xe132-representative-plot:end -->

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

prepare/run/build/finalize/validate_solar_b8_nsi负责来源准备、实际计算、同源onboarding、主线登记和渲染验收；旧单bin工具允许较新并列分支。

[完整新onboarding：实际输入、标准引文、物理与程序](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->

<!-- solar-snudd-v34:start -->

## 太阳传播可选扩展：SNuDD v3.4

[已安装并接入主线的新onboarding](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_EXTERNAL_ONBOARDING.v3.4.md>) · [独立安装/API](<../extensions/solar_rho_snudd/README.md>) · [三样本实际对照](<../outputs/external/solar_rho_snudd/20261112_run1/README.md>)。只更换传播源，旧B16-MSW/SM/多bin入口保留；不改变全局默认注册。

<!-- solar-snudd-v34:end -->

<!-- solar-snudd-v341:start -->

## 太阳完整统计：SNuDD v3.4.1

[三样本全流程、联合区域和论文比较](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际结果、图与验收](<../outputs/external/solar_rho_snudd/20261112_fig4_run2/README.md>)。已计算601×601面与各方案联合最小值；2601 Fig.4绿色精确复现未成立，旧结果保留。

[run_solar_b8_snudd_inference.py](<run_solar_b8_snudd_inference.py>) · [finalize_solar_b8_snudd_inference.py](<finalize_solar_b8_snudd_inference.py>) · [validate_solar_b8_snudd_inference.mjs](<validate_solar_b8_snudd_inference.mjs>)

<!-- solar-snudd-v341:end -->

<!-- solar-full-rho-trace-onboarding-v35:start -->

## 当前太阳onboarding：完整ρ与Tr(ρK) v3.5

[微分/总截面、事例数积分与三样本差别](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md>) · [明确合同与待改程序](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_CONTRACT.v3.5.json>)。按用户要求先更新文档；旧投影程序尚未改成新版trace，旧结果保留。

[同源文档生成/检查](<build_solar_b8_trace_onboarding.py>)（--write或--check，只操作文档/来源审计/主线待办）；[公式、目录和渲染校验](<validate_solar_b8_trace_onboarding.mjs>)。

<!-- solar-full-rho-trace-onboarding-v35:end -->
