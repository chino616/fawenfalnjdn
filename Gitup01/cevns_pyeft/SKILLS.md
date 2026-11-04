# Skill 库总表与增减规则

本页汇总**本仓库内登记的全部 Skill**，便于查看每项能力的职责、产物、调用流程与原始文件。它是 `cevns_pyeft` 内的用户文档；Skill 的实际指令保存在 `workflows/`。这里的“全部”以仓库 [catalog](../workflows/catalog.yaml) 为准，不包括用户电脑上另行安装的个人或插件 Skill。

## 从哪里开始

1. 查看本页总表，点击 Skill 名称阅读完整 `SKILL.md`，点击流程查看交接顺序。
2. 执行任务时，从 [Master Skill](../workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md) 开始，由 [routes.yaml](../workflows/cevns-pyeft/router/routes.yaml) 选择流程；不要求每次都走全部物理阶段。
3. 整理实验资料时，先读[共同输入规范](../workflows/_shared/INPUT_STANDARD.md)，再由 `cevns-onboarding` 提取材料、证据、缺失和冲突，形成 partial Physics Contract；随后进入所需的 P01–P10。提取结果和审核状态按实验/dataset 独立保存。

统一的职责关系是：**catalog 登记身份 → routes 选择任务 → WORKFLOW 编排交接 → SKILL 执行单项能力**。共同规范、schema、空白模板和 QA 工具由各流程共享，分别在 [workflows 总览](../workflows/README.md) 与 [_shared](../workflows/_shared/README.md) 查看。

## 完整 Skill 表

下方标记区由 [update_skill_library.py](../tools/update_skill_library.py) 从 catalog 和各流程的实际 metadata 生成。用途、产物的中文摘要维护在 catalog 的 `summary_zh`、`outputs_zh`；执行细节以对应 `SKILL.md` 为准。调用关系是直接引用，表格顺序用于浏览，不能代替流程内的前置条件和审核。

<!-- skill-library:start -->
共 **17** 个已登记 Skill：**17** 个 active，**0** 个 deprecated。

类别统计：主路由 1；资料接入 1；物理阶段 10；工程能力 5。

| 类别 / 阶段 | Skill（点击查看完整指令） | 稳定 ID | 负责什么 | 主要产物 | 调用它的流程 | 状态 |
|---|---|---|---|---|---|---|
| 主路由 | [cevns-experiment](../workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md) | `cevns.router.experiment` | 识别任务与 dataset 歧义，路由 H0–H3 及统一报告规范 | 路由、范围和既有 Gate 状态、前期审阅交接 | [统一入口 routes.entry_skill](../workflows/cevns-pyeft/router/routes.yaml) | active |
| 资料接入 | [cevns-onboarding](../workflows/cevns-pyeft/skills/onboarding/cevns-onboarding/SKILL.md) | `cevns.onboarding.experiment` | 按 H0–H3 审阅材料、证据和独立模块选择，形成 P00–P03 | 来源/证据/缺失记录、partial contract、两份同源报告的元数据 | [experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md) | active |
| P01 | [cevns-dataset](../workflows/cevns-pyeft/skills/phases/cevns-dataset/SKILL.md) | `cevns.phase.p01.dataset` | 明确数据集身份、run/探测器范围、观测量、分箱与数据语义 | dataset 合同、观测轴/单位、分箱与数据身份记录 | [experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md) | active |
| P02 | [cevns-target](../workflows/cevns-pyeft/skills/phases/cevns-target/SKILL.md) | `cevns.phase.p02.target_exposure` | 核对核素组成、核响应键、真实核数及曝光/归一化归属 | 靶核清单、核数、曝光合同与归一化归属 | [experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md) | active |
| P03 | [cevns-source](../workflows/cevns-pyeft/skills/phases/cevns-source/SKILL.md) | `cevns.phase.p03.source` | 核对源分量、ν/反ν与味态、谱支持域/插值、绝对归一化和时间基准 | 源合同、注量/谱/入射态接口与检查证据 | [experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md) | active |
| P04 | [cevns-theory-response](../workflows/cevns-pyeft/skills/phases/cevns-theory-response/SKILL.md) | `cevns.phase.p04.theory_response` | 审查理论、算符/匹配与核响应覆盖，明确约定和适用范围 | 理论与核响应合同、覆盖矩阵、证据与限制 | [experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md)<br>[theory-extension](../workflows/cevns-pyeft/definitions/theory-extension/WORKFLOW.md) | active |
| P05 | [cevns-kinematics-cross-section](../workflows/cevns-pyeft/skills/phases/cevns-kinematics-cross-section/SKILL.md) | `cevns.phase.p05.kinematics_cross_section` | 建立弹性运动学与微分截面合同，核对质量、入射态、单位和支持域 | 运动学/截面合同、物理边界与核验结果 | [experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md)<br>[theory-extension](../workflows/cevns-pyeft/definitions/theory-extension/WORKFLOW.md) | active |
| P06 | [cevns-detector-response](../workflows/cevns-pyeft/skills/phases/cevns-detector-response/SKILL.md) | `cevns.phase.p06.detector_response` | 区分响应密度与接受后箱概率，核对效率/选择归属和观测轴 | 探测器观测算子合同、效率归属、轴与概率检查 | [experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md) | active |
| P07 | [cevns-slow-counts](../workflows/cevns-pyeft/skills/phases/cevns-slow-counts/SKILL.md) | `cevns.phase.p07.slow_counts` | 计算直接事件数，验证归一化和数值收敛，提交 Slow 参考供审核 | Slow 预测、收敛证据；实际接受后冻结的版本化参考 | [capability-maintenance](../workflows/cevns-pyeft/definitions/capability-maintenance/WORKFLOW.md)<br>[experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md) | active |
| P08 | [cevns-fast-counts](../workflows/cevns-pyeft/skills/phases/cevns-fast-counts/SKILL.md) | `cevns.phase.p08.fast_counts` | 将加速表示与已接受 Slow 比较，限定参数域、缓存依赖及逐箱误差 | Fast 能力记录、误差报告、缓存/适用域合同 | [capability-maintenance](../workflows/cevns-pyeft/definitions/capability-maintenance/WORKFLOW.md)<br>[experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md) | active |
| P09 | [cevns-statistics](../workflows/cevns-pyeft/skills/phases/cevns-statistics/SKILL.md) | `cevns.phase.p09.statistics` | 核对观测数据语义、似然、nuisance/covariance 和推断范围 | 统计合同与推断验证；标明近似模型或官方模型边界 | [capability-maintenance](../workflows/cevns-pyeft/definitions/capability-maintenance/WORKFLOW.md)<br>[experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md) | active |
| P10 | [cevns-validation](../workflows/cevns-pyeft/skills/phases/cevns-validation/SKILL.md) | `cevns.phase.p10.validation` | 核验目标所需能力、实际 runtime 接入与科学结论的证据范围 | 能力矩阵、验证/发布证据、待用户审核的最终结论 | [capability-maintenance](../workflows/cevns-pyeft/definitions/capability-maintenance/WORKFLOW.md)<br>[experiment-onboarding](../workflows/cevns-pyeft/definitions/experiment-onboarding/WORKFLOW.md)<br>[theory-extension](../workflows/cevns-pyeft/definitions/theory-extension/WORKFLOW.md) | active |
| 工程能力 | [cevns-physics-modularity](../workflows/cevns-pyeft/skills/engineering/cevns-physics-modularity/SKILL.md) | `cevns.engineering.physics_modularity` | 按物理职责定位文件/函数与替换点，判断复用、适配或扩展 | 模块分类、最小改动清单、失效影响与验证计划 | [capability-maintenance](../workflows/cevns-pyeft/definitions/capability-maintenance/WORKFLOW.md)<br>[runtime-maintenance](../workflows/cevns-pyeft/definitions/runtime-maintenance/WORKFLOW.md)<br>[theory-extension](../workflows/cevns-pyeft/definitions/theory-extension/WORKFLOW.md) | active |
| 工程能力 | [experiment-migration](../workflows/cevns-pyeft/skills/engineering/experiment-migration/SKILL.md) | `cevns.engineering.experiment_migration` | 先用 custom catalog 和 Slow 最小合同接入工程骨架，再核对激活条件 | 迁移清单、资源审计、合同测试计划与验证结果 | [runtime-maintenance](../workflows/cevns-pyeft/definitions/runtime-maintenance/WORKFLOW.md) | active |
| 工程能力 | [experiment-archive](../workflows/cevns-pyeft/skills/engineering/experiment-archive/SKILL.md) | `cevns.engineering.experiment_archive` | 将 archived/spec_only 从默认 runtime 发现中分离，保留历史 | 归档/隔离变更记录及未受影响实验的验证 | [archive-lifecycle](../workflows/cevns-pyeft/definitions/archive-lifecycle/WORKFLOW.md) | active |
| 工程能力 | [resource-manifest-auditor](../workflows/cevns-pyeft/skills/engineering/resource-manifest-auditor/SKILL.md) | `cevns.engineering.resource_manifest_auditor` | 审计资源 ID、路径/根、别名、哈希、覆盖作用域与统计延迟加载 | 资源审计报告、缺失/冲突项与修复验证 | [archive-lifecycle](../workflows/cevns-pyeft/definitions/archive-lifecycle/WORKFLOW.md)<br>[resource-maintenance](../workflows/cevns-pyeft/definitions/resource-maintenance/WORKFLOW.md)<br>[runtime-maintenance](../workflows/cevns-pyeft/definitions/runtime-maintenance/WORKFLOW.md) | active |
| 工程能力 | [experiment-release-validator](../workflows/cevns-pyeft/skills/engineering/experiment-release-validator/SKILL.md) | `cevns.engineering.experiment_release_validator` | 检查 manifest/catalog/runtime 一致性、隔离导入、外部资源与 wheel | 发布/隔离环境验证结果及限制 | [release-validation](../workflows/cevns-pyeft/definitions/release-validation/WORKFLOW.md)<br>[runtime-maintenance](../workflows/cevns-pyeft/definitions/runtime-maintenance/WORKFLOW.md) | active |
<!-- skill-library:end -->

**流程与 Skill 分别计数。** [仓库/README 维护](../workflows/cevns-pyeft/definitions/repository-maintenance/WORKFLOW.md)和 [Skill QA](../workflows/cevns-pyeft/definitions/skill-qa/WORKFLOW.md) 是调用工具的流程，目前不声明专属 Skill；它们不会凭 `WORKFLOW.md` 增加 Skill 数量。`_shared` 内的模板、规范也不计入此表。上表中的 active 表示活动登记状态；不代表全局安装、自动执行或科学审核通过。

## 新增：先复用，再登记和接入

1. 明确新增能力的触发条件、职责、输入、产物和退出条件。已有 Skill 足以承担时，修改现有说明或编排；只是新增实验数据时，复用共同规范和现有 Skill，不按实验名复制整套能力。
2. 在 `workflows/cevns-pyeft/skills/<类别>/<skill-name>/SKILL.md` 创建独立能力包。现有类别为 `router`、`onboarding`、`phases`、`engineering`；名称使用小写连字符，frontmatter 含唯一 `name` 与明确的 `description`，目录名与 name 一致。辅助脚本/参考资料放该包内，共同规则继续放 `_shared`。
3. 在 [catalog](../workflows/catalog.yaml) 添加唯一稳定 `id`、`name`、`kind`、相对于 `workflows/` 的 `path`、`status`、`summary_zh`、`outputs_zh`；阶段能力还要声明 `phase`。现有 P01–P10 映射保持唯一，不能把新能力硬塞成重复阶段。机器记录继续使用 JSON 语法（YAML 1.2 子集）。
4. 需要被执行时，在相应 `definitions/<流程>/WORKFLOW.md` 的 metadata `skills` 中引用稳定 ID，并写清正文交接；仅登记的能力会在总表显示“尚无工作流引用”。新增任务分类才修改 routes 和 request schema，普通能力扩展不新增第二套任务分类表。Skill 的显式 `invokes` 引用也需登记并检查循环。
5. 同步相关场景、测试、所属 README 和上级导航，执行下方同步与检查。已有文档/测试中的数量基线随合法增减一同复核；不能通过删掉检查、放宽物理容差或重写冻结参考掩盖问题。

新增 Skill 不会自动注册到 Python runtime，也不授予实验写入、物理选择或正式激活权限；仍按实际任务和已有授权执行。

## 修改、移动、停用和删除

| 操作 | 必须同步的内容 | 完成条件 |
|---|---|---|
| 修改职责、输入或产物 | `SKILL.md`、catalog 中文摘要、调用流程正文、适用场景/测试 | 用户能从表格找到准确职责；实际调用仍满足交接合同 |
| 移动或改名 | 保留稳定 ID；更新 catalog 路径/name、目录和 frontmatter，以及直接路径链接、README 和脚本引用 | 旧路径的当前消费者已清理，稳定 ID 仍能解析到唯一文件 |
| 停用但保留过渡入口 | catalog 状态设为 `deprecated`，摘要说明替代能力/迁移安排；核对现有消费者，不再增加新调用 | 总表仍列出该能力与现有引用；状态字段本身不会自动改写路由或清除调用 |
| 正式删除 | 先列出并迁移/移除 WORKFLOW、routes 的入口引用、其他 Skill 的 `invokes` 和当前正文/脚本调用，再移除 catalog 条目及能力包 | 同一任务内同步总表、README、场景和测试；无未登记 Skill、悬空 ID、失效当前链接或调用循环 |
| 合并能力 | 指明原能力→保留能力的对应关系，迁移消费者后按删除规则处理原包 | 不复用旧 ID 表示无关能力，不保留两份互相冲突的活动指令 |

主路由、资料接入和 P01–P10 具有现有结构约束，不能作为普通冗余文件随手删减；确需改变阶段模型时，同时评审流程合同、schema、消费者与测试。历史报告按其记录时间保留，不能为消除旧路径而重写历史证据；`backup/` 只用于恢复，不参与活动 Skill 发现。

## 同步与验收：同一次变更完成

从 `Gitup01` 根目录，使用具备 [QA 依赖](../workflows/cevns-pyeft/qa/requirements.txt)的 Python 执行：

```powershell
# 只读检查：表格是否与 catalog、实际 Skill 文件和流程引用一致
python -B tools/update_skill_library.py --check

# 显式同步：备份旧文件，只替换 skill-library 标记区，保留本页人工规则
python -B tools/update_skill_library.py --write
```

`--write` 将原始字节保存到 `backup/skill-library-<唯一编号>/cevns_pyeft/SKILLS.md`，并在 `backup/BACKUP_MANIFEST.md` 登记；内容相同则不写入、不额外备份。新增、删除、状态/摘要变更或流程引用变化后，表格未同步会使结构检查失败。该工具不会监听文件系统，也不会自动删除 Skill、改写人工规则或刷新保护哈希。

本页和包 README 属于[保护清单](../tools/workflow_validation/config/PROTECTED_FILES.json)。获准修改后，只更新实际变动文档的 SHA256；新增本页这类受保护范围内文件时登记准确路径。先核对差异，再更新对应条目，保留其他代码、数据和冻结参考的基线。

```powershell
python -B tools/update_skill_library.py --check
python -B workflows/cevns-pyeft/qa/validate_skill_pack.py
python -B workflows/cevns-pyeft/skills/engineering/cevns-physics-modularity/scripts/audit_references.py --repo .
python -B workflows/cevns-pyeft/qa/validate_phase_contract.py --check-schemas
python -B -m unittest discover -s tests/workflows -v
python -B tools/validate_docs.py --files cevns_pyeft/SKILLS.md cevns_pyeft/README.md workflows/README.md
```

`validate_skill_pack.py` 已包含本页一致性检查。上面的文档路径按本次实际变动扩展，新增文件和正文命令的说明覆盖仍由维护者核对；机器通过不替代科学审核或真实代理行为测试。

批量删减时按[仓库维护流程](../workflows/cevns-pyeft/definitions/repository-maintenance/WORKFLOW.md)先保存 Git/文件快照基线，按目录核对增删与 README。`readme_maintenance.py sync --readmes ...` 只负责目录清单区，本页 Skill 表由 `update_skill_library.py` 负责，两者的标记区和职责各自明确。Git 可用时复查 `git diff --name-status`、`git diff --check` 和最终差异；Git 不可用时比较保存的快照，不隐式初始化或提交仓库。

全部文件操作遵循[文件与 README 联动规则](../workflows/_shared/policies/file-lifecycle.md)：所属说明、父级导航、注册与真实消费者在同一次任务内维护，任务报告记录文件→README 对应关系和实际检查结果。

[包目录说明](README.md) · [工作流总览](../workflows/README.md) · [项目总览](../README.md)
