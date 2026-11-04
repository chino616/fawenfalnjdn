# Task10 — 项目活动数据集三文件迁移

2026-11-04。工程状态：COMPLETE；科学状态：DRAFT/PARTIAL，人工 NOT_REVIEWED。
分支 `refactor/07-gitup01-20261104`，起止核实 HEAD
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。工作区已有 Tasks02–09 和并行阶段审计修改；
保留原修改，没有 reset/stash/clean、切分支、commit 或 push。

## 实际范围与依据

工作根为 `.github-publish/gitup01-20261104/Gitup01`，未向同级普通 Gitup01 写入。
读取当前 registry/manifest、Catalog、owned_files、资源、Runtime 与能力登记，确认且只确认
CsI2021、CsI2017、Ar2020 为 active/installed；见[盘点](PROJECT_DATASET_MIGRATION_INVENTORY.md)。
CONUS、ROOTTime、time-resolved、demo、archive 和 backup 不纳入迁移。

关键依据包括任务规则/顺序/Task10、根 AGENTS、Master/runtime-maintenance workflow、
共同输入规范、既有 Definition/Catalog/loader/runtime、模型绑定、三文件 compiler、
registry_io/management/build hook 及冻结接口与 legacy Fast 参考。
备份按每次修改前的真实文件保存，登记到 backup/BACKUP_MANIFEST.md；
backup 仅作恢复点，没有作为物理资料或数值基准。

## 每个数据集的权威与模型

| Dataset | 三文件位置 | 格式/规模 | 原行为保持 |
|---|---|---|---|
| CsI2021 | [目录](../data/experiments/COHERENT_CsI/CsI2021/README.md) | v1，17模型/105参数/23数组 | Gamma 响应、九 PE 箱、legacy Gaussian 双 pull；Task05–09 已迁移。 |
| Ar2020 | [目录](../data/experiments/COHERENT_Ar/Ar2020/README.md) | v2，7模型/80参数/20数组 | Ar40、sigma 依赖观测值的 Gaussian 折叠、12箱、近似 asymmetric IRLS。 |
| CsI2017 | [目录](../data/experiments/COHERENT_CsI/CsI2017/README.md) | v2，7模型/82参数/28数组 | Cs133/I127、确定性 PE、固定251个 Slow 节点、原 bin-edge 插值/梯形积分、25箱、近似单 pull Gaussian。 |

先迁移 Ar2020，再迁移 CsI2017。`migrate_legacy_input_packages.py` 仅提取当时真实旧实现的
legacy-derived 输入，保存每个实验的独立 IR 和声明数组。两者均调用相同
`package_compiler`，没有实验特有的第二套三文件生成器。迁移后重编使用保存 IR，
不再从薄 definition 反向猜测参数。人填、AI 摘录和混合资料仍进入同一 IR/compiler。

Runtime 只读 YAML/NPZ，MD 是确定性的全部参数/公式/资源/单位/轴/归一化/来源/能力视图。
旧 spec、效率表、统计表与 response JSON 保留历史身份，不提供默认 Runtime 参数。
两个新增包的实验数值全部标明 legacy-derived，不冒充官方原文核准。

## 调用链与实现边界

`*_definition.py → definition_from_package → 原 Catalog/ResourceCatalog/loader → PreparedExperiment
→ 原 Runtime → 受控 package profile → 公共 interaction/recoil/folding → Prediction/原统计 profiler`。
没有第二个 Catalog、Runtime 或任意 YAML callable/eval。

`package_profiles.py` 装配数组源谱、固定味态、靶库存、核响应和探测器；
`rates/legacy_observables.py` 共享两种原有积分策略。公共 LEFT matching、响应收缩和截面数学未改。
源连续谱已经包含 POT、yield、geometry，不重复归一化；原始生成输入及依赖指纹必须匹配。
靶分数、质量和核数是校验后的只读派生缓存。公共常数/active LEC 必须明确存在且匹配
所绑定引擎版本，不能声称任意 LEC 扫描或用缺失参数 fallback。

旧 Fast builder 与新的 Runtime Fast 分开验收。前者保留原 conversion/channel 算术，
从已装配包取得 source/response/detector/target 并调用原 builder；冻结数组要求逐元素精确相等。
新 v2 Fast 复用公共 differential coefficients 和同一 profile 折叠；保存格式复用原 storage，
实际物理/实现/网格身份或数组内容变动会拒绝旧缓存。统计专用输入按消费者投影，
其变化不污染物理缓存；原始文件仍受 immutable snapshot 检查。

## 独立验收总表

PASS 只指该列的实际工程检查，不代表科学批准。

| Dataset | Package schema | Physics MD | Runtime | Prediction | Fast | Statistics | Standalone | Install/export | Scientific approval |
|---|---|---|---|---|---|---|---|---|---|
| CsI2021 | PASS | PASS | PASS | PASS | PASS | PARTIAL | PASS | PASS | BLOCKED |
| Ar2020 | PASS | PASS | PASS | PASS | PASS | PARTIAL | PASS | PASS | BLOCKED |
| CsI2017 | PASS | PASS | PASS | PASS | PASS | PARTIAL | PASS | PASS | BLOCKED |

Statistics 的 PARTIAL：旧近似计算可执行并保留原统计语义，官方 likelihood 未验证。
Physics MD PASS 仅检查覆盖和与机器输入一致，不确认来源真实性。
三个实验的模型绑定合同均 PASS；此状态不授予科学批准。CsI2021 的 Tasks06/09 证据保留，
本任务又对同一最终分发物中的三个实验完成了独立安装验证。

## 实际命令与结果

解释器为 `F:/Work/.codex_conda_envs/codex-py311/python.exe`，使用 `-B`。
pytest 的 basetemp 使用工作区独立新目录，未使用有 ACL 问题的系统临时根。

| 命令/验证 | 当前真实结果 |
|---|---|
| `pytest tests/test_project_package_migration.py`，初次版本 | 11 passed；两个包冻结 SM/multiflavor、逐源分量、Fast回读、两文件、参数扰动与单位拒绝。 |
| project migration + compiler + distribution，project02 | 39 passed；包括新增合同拒绝和统计数组变化复用物理缓存。 |
| modularization + runtime migration + refactor03，contracts01 | 50 passed，1 failed；唯一失败为 Catalog.describe 提前导入核响应。已改为固定源码路径取指纹，最终复测 PASS。 |
| 原 legacy builder 冻结数组（前续执行） | 3 passed；三个实验 full/diag/pair/index array_equal，无参考或容差修改。 |
| project migration + 全 fast_model_contract，final-physics01 | 65 passed，1 failed；新增两个包全22算符复味矩阵逐源/核素 Fast–Slow 通过，三个旧 builder 冻结数组也通过。唯一失败仍为随后修复的延迟导入。 |
| binding + schema + compiler + package loader/runtime，binding-final01 | 113 passed，1 failed；unsafe formula 已被更早的 Schema 拒绝，旧测试只因提示文字不同失败；改为匹配同一 specification 拒绝并复测通过。 |
| project + distribution + lazy catalog + unsafe formula，final-package01 | **35 passed**；最终包状态、单位/引用/模型/源谱依赖、两文件、缓存、全算符和三实验 export/ignore 均通过。 |
| compiler-final01 | **13 passed**；包括 canonical 覆盖恢复点位于 backup、活动 data 只保留三份正式文件。 |
| management01 | **25 passed**；三个实验逐一真实卸载/重装/逆向回滚，新进程验证其他实验预测与统计；全部在隔离副本。 |
| legacy-final01 | **12 passed，24 deselected**；旧标量味态与 Ar2020/CsI2017 冻结源分量保持。 |
| lazy-wording-final01 | **2 passed**；两项曾失败的合同均通过。 |
| 三份 package validator、两个 IR compiler `--check` | **PASS**；精确同源 MD、数组 key/shape/dtype/hash 与确定性重编通过。 |
| resource audit / Skill-pack / affected docs / Git whitespace | **PASS**；6份机器资源全部哈希匹配；17 Skills/9 workflows/15 routes，17篇受影响文档无失效本地链接。 |

这些组有重叠，不把次数相加成独立物理测试数。没有运行全部 pytest suite，也没有把
未执行的外部科学复现或默认网格收敛记为 PASS。XML、机器验收及源码变更清单见
[Task10结果](../outputs/onboarding/task10/results.json)与
[变更清单](../outputs/onboarding/task10/change-manifest.json)。

实际最终命令组为 `pytest tests/test_project_package_migration.py tests/test_dataset_package_distribution.py`
加 lazy/formula 两个单项；`pytest tests/test_package_compiler.py`；`pytest tests/test_dataset_management.py`；
`pytest tests/test_refactor_csi2021_regression.py tests/test_legacy_coherent_scalar_regression.py -k 'shared_coherent or legacy_scalar'`。
每组使用不同 `.pytest-tmp/task10-*` 和 `--junitxml=outputs/onboarding/task10/...xml`。
全局检查为 `workflows/cevns-pyeft/qa/validate_skill_pack.py`、
`tools/validate_resource_manifest.py --root . --json-out outputs/onboarding/task10/resource-audit.json`、
`tools/validate_docs.py --files <17篇受影响文档> --json-report outputs/onboarding/task10/docs-audit.json`，
以及 `git -c core.safecrlf=false -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check`。
outputs/README 因校验器的 archive/cache 排除规则不进入链接扫描，已按变更清单人工核对；
其新增段落只有产物目录说明，没有新增文件链接。混合 CR/CRCRLF 的六份 README 在备份后
仅规范换行，逐项确认所有非空行原样保留。

## 最终安装与两文件独立执行

执行 `python -B tools/validate_project_packages.py --output <新的外部目录>`。
最终完整日志/临时引擎位于
`F:/Work/2026-07-15 CEvNSpyEFT-Local/project-package-validation-20261104-run02/`，
完整 JSON 已复制到[安装验收](../outputs/onboarding/task10/installation-results.json)。

实际离线执行 sdist → 从该 sdist 构建 wheel → target 安装 → 外部 cwd；另验证 editable 安装。
sdist 与 wheel **各且仅各含9份正式文件**，逐字节等于三个 canonical 包。
三种环境均对全部三个 ID 执行 Slow、近似统计、Fast、Fast 保存回读和冻结比较。
两文件环境先删除临时引擎内全部旧 definitions、两类 legacy_parameters、保留候选适配副本和
bundled data，再仅复制每实验 YAML/NPZ。import/file guards 拒绝旧定义、旧表、MD 和原项目访问。
全部 PASS；同一主机和已安装声明依赖，不声称第二台物理机器或全新系统依赖安装。

| Dataset | 实际 Slow 网格 | 预测总数 | legacy近似 χ² | Fast与Slow最大绝对差 |
|---|---|---|---|---|
| CsI2021 | small：5/12/4，PE step=4 | 379.8315235321747 | 12.021755137669244 | 2.84e-14 |
| CsI2017 | 固定251 PE节点，n_enu=12 | 167.55855004906752 | 24.696754086455268 | 1.78e-14 |
| Ar2020 | medium：11/40/8 | 136.6322232033332 | 9.484606567676185 | 1.07e-14 |

冻结比较维持 rtol=1e-10、atol=1e-12；这些数字是工程兼容证据，不是官方实验结果。
sdist SHA256：`19a0b4715e5f9d50777127b0e9c822a2a50fb7de68b473c163e4d7376c78894c`；
wheel SHA256：`1ef5b4b44c3ef1510aba08464e97bbded20639d4d44b104844d2881654bf3691`。

## 分发、生命周期与文档

registry 为两个新增包登记三份 owned files、SHA256、runtime_required、版本和共享模块；
resource manifest 只将 package_input/package_arrays 绑定为默认输入。
MD 随包分发但 runtime_required=false。原历史 owned files 保留，不作为运行来源。
精确 gitignore 例外开放三个实验的九份正式文件及新增 Ar2020 所属 README；私有附属数据继续遵守父目录规则。
`package_build.py` 构建时从唯一 canonical data 树复制到 wheel，sdist 保留原树和 hook。
首次分发复核发现 compiler 恢复副本会被递归打入 sdist。已验证9个本轮生成恢复目录的摘要并
移入 Task10 backup；canonical 覆盖现在把恢复点存入 backup/package_compiler 并登记清单，
MANIFEST 也排除旧 compiler-backup 目录。最终 run02 已验证精确文件集合。
另移除 CsI2017 不实际使用的 recoil_min 控制项，参数数为82；没有改变其 PE 网格或预测。

文件与所属说明同步：package/profile/compiler/adapter → experiments/README 与 coherent/README；
数值策略 → rates/README；每个三文件 → 各 data README 与 registry/DATASETS；
测试 → tests/README；迁移/安装工具 → tools/README；报告 → docs/README、software/README；
生成证据 → outputs/README。Workflow 的统一 IR/compiler 入口已在 Task08 同步。

## 科学限制与保留文件

三个实验均未获得本任务的人工 Physics Approval。官方 likelihood、一般反中微子 EFT 和科学发布
继续 BLOCKED。未解决外部核表来源、反中微子约定、探测器有效域和统计数据解释问题，
不得用工程迁移或旧程序一致性关闭。CsI2021 默认网格收敛尚未证明；Task06 的 refined
诊断与冻结兼容不能混同。本任务没有调数值、改公式或放宽阈值来制造科学 PASS。

按用户要求，`coherent/csi2021_package.py`、`coherent/csi2021_package_contract.json` 和
`tests/test_csi2021_input_package.py` 保留原样；默认迁移没有依赖其实现。
并行阶段审计报告原样保留。本任务的结束条件是全部活动实验的最终 package-backed
Runtime 与安装验证实际通过，现已满足；Tasks02–10 工程工作完成。
三个保留文件末次 SHA256 与续跑起点完全一致，记录在 Task10 results.json。
冻结参考未修改，科学门槛继续按能力保留。没有发布或提交 Git，也不自动开始新任务。
