# Codex 完整调整方案：目录简化、历史清理、实验数据与物理接口

日期：2026-10-29（Asia/Shanghai）。

审查项目：CEvNS-pyEFT / Gitup01。  
审查分支：`refactor/02-experiment-modularization-20261029`。  
审查提交：`bd54dba8835ed245374c5a9d1d113ed20917c33b`。  
文档性质：**源码评估 + 可执行工程方案**。不表示下列修复已经全部完成。

用户已明确选择：去掉 `src` 一层，保留 `cevns_pyeft` 包名；清理与当前使用无关的历史内容。
本次审查另在隔离副本做过目录试迁移，用于检查打包与依赖。用户 Windows 项目和 GitHub 分支未被本次审查修改或推送。

## 0. 结论与实施原则

Refactor-02 已经实现了有实际作用的实验管理层：四个实验的默认设定有独立定义，统一加载、预测和启停会消费这些设定，CONUS+ 也已接入。它不是只有目录和空包装。

但目前还不能称为“所有实验的整条物理链都可独立替换”：

- CsI2021 使用组合式 `ExperimentModel`，物理组件边界最成熟。
- CsI2017、Ar2020 仍通过专用执行器调用带 SNS 假设的旧率积分和 Fast 实现。
- CONUS+ 的源、截面与率积分仍存在固定导入和候选模型约束。
- 资源覆盖、不可变快照、实际装配指纹和外部统计坐标存在可复现缺口。

本次调整分为两个相互配合、分别提交的部分：

1. **目录与使用整理**：源码少一层；当前文档可直接找到；历史记录退出主项目；实验输入有明确归属。
2. **接口可靠性与后续组件化**：先修复已复现的合同缺口，再逐实验开放有实际需求的替换能力。

不得以“重建一套十几个新类”代替复用现有合同。不得借整理目录修改物理公式、天然/单核素假设、曝光、数据或原测试容差。

## 1. 独立审查事实

### 1.1 已有能力

| 内容 | 审查结果 |
| --- | --- |
| 四个独立定义 | `coherent/{csi2021,csi2017,ar2020}_definition.py` 和 `conus_plus/definition.py` 已存在 |
| 统一入口 | `load_experiment`、`predict_experiment`、`evaluate_experiment`、`predict_selection` 已实现 |
| 实际参数消费 | 源强、曝光和部分响应参数的覆盖确实改变结果；已有行为测试 |
| 禁用实验 | 不解析其物理资源、不运行预测；选择层校验身份和数值键 |
| CONUS+ | 有名 C2/C3/C5 结果、kg·day 曝光、源表路径覆盖与响应矩阵 Fast |
| 旧 Fast 身份误标 | 请求 ID 与核 ID、分箱、源/目标布局已有检查 |
| 新实验扩展 | synthetic 示例经公开 catalog 注册，并使用公共算法与解析值比较 |

### 1.2 当前测试基线

审查环境：Python 3.12.14、NumPy 2.3.5、SciPy 1.17.0、pytest 9.2.0。

对未经本轮调整的提交执行全部 `tests`：**221 passed，2 failed，0 skipped**，269.68 秒。

| 失败 | 判断与处理 |
| --- | --- |
| `test_conus_bound_benchmark_consumes_one_combined_prediction` | 依赖未上传的 `outputs/conus-plus-completion-20261012/statistics/approximate_paper_benchmark/observations_digitized_approx.csv`。是当前交付的外部资源缺口，不能伪造观测补齐 |
| `test_existing_fast_builders_preserve_pre_refactor_arrays_exactly[CsI2021]` | 最大相对差约 `4.24775396e-16`，与此前审查环境中已记录的问题一致；不能据此宣称本轮改动造成新的物理差异，也不能自行放宽 `assert_array_equal` |

提交内“634 个旧基线数组一致”是原实施报告的结果；对应冻结输出未随此分支提供，本次没有独立重跑这 634 个数组，不将其冒充本次实测。

隔离副本平铺源码、修正资源根并恢复必要测试依赖后，完整测试为 **221 passed，2 failed**，258.85 秒；失败仍为上述两项，没有新增测试失败。flat layout 的 wheel 构建成功，并在项目外 cwd、Python `-I` 下从解包的 wheel 加载四个实验，得到 9/25/12/19 箱结果和正确的探测器标识。

这证明目录方案的可行性，不代表全部文档/data 迁移或 I01–I04 已修复。试迁移还逐文件核对了 data、tests/reference 和 workflows 共 102 份受保护文件，内容未变。首次清理暴露了 freeze_baseline 的测试依赖，已恢复后再完整验证；正式方案按第 3.3 节处理此依赖。

### 1.3 已复现的四项接口缺口

小网格仅用于工程复现，下面的数值不构成科学收敛结果。

| 编号 | 触发方式 | 实际现象 | 要求 |
| --- | --- | --- | --- |
| I01 | `ResourceCatalog(root, overrides={"respones": missing_path})`，故意拼错 responses | 加载成功，仍使用默认核响应文件；覆盖键未被消费也不报错 | 对未消费/未知资源键报错，支持跨数据集资源时明确键的作用域 |
| I02 | 通过 `dataclasses.replace` 给 CONUS `thresholds_evee` 传入 list；加载后修改该 list | C3 小网格计数从约 113.913 变为 1.936，外层物理指纹不变，记录仍显示旧阈值 160 eVee | 深层快照不可变；外部可变对象不能继续控制已加载实例 |
| I03 | 用公开 `prepare` 装配入口把 CsI2021 实际源强加倍，而声明的 physical 字段不变 | 计数严格加倍；实际 model 描述不同，但外层 physics/analysis 指纹相同；原实验可接受该预测进行统计评价 | 指纹必须包含实际装配与执行依赖，不能只哈希声明字段 |
| I04 | 提供 19 行 synthetic 统计 CSV，数值列合法，但能量列在 10165–10345 eVee | 对 160–350 eVee 预测仍返回有限 chi² | 校验外部观测的坐标、单位、顺序和归一化，不只检查向量长度 |

I04 的 CSV 是刻意构造的接口测试夹具，不是 CONUS+ 观测。现有 loader 没有规定/检查坐标字段，正是需要补上的合同。不能把该夹具用于论文统计或冻结真实实验基线。

### 1.4 仍存在的结构耦合

- `rates/counts.py::_rate_per_kg` 固定使用 μ 衰变端点、e/mub/mu 和 muLine；`_folded_counts` 仍从通量字典取得探测器质量。
- `conus_plus/slow_counts.py::true_recoil_rate_components_per_kg_day` 固定调用当前截面函数、源函数与入射态。
- `coherent/execution.py::assemble_csi2021` 内部选择具体源、相互作用和响应。修改它或改写 prepare 可以替换组件，但尚非所有实验都具有同样明确的替换槽位。
- `CsI2017Settings` 从 `csi2021_definition` 取得共用 CsI 材料配方。共用材料应该由中立的材料模块拥有，不应依赖另一份实验定义。
- `implementation_modules` 是手工维护的依赖名单；不同缓存表示的真正依赖不能仅靠一份大名单推断。

这些问题不否定当前默认分析的数值复现，但限制“用户/Skill 可以安全替换任意物理组件”的承诺。

## 2. 为什么移除 src 可行，为什么保留包名

原结构 `Gitup01/src/cevns_pyeft` 中：

- `Gitup01` 是项目根，包含打包配置、数据、测试和文档。
- `src` 是 Python 打包采用的源码容器，不是运行时模块名。
- `cevns_pyeft` 是真正的导入包，现有代码通过 `import cevns_pyeft` 使用它。

按用户选择，采用 flat layout：`Gitup01/cevns_pyeft/`。
该改变不要求改包名，也不要求改所有 `from cevns_pyeft...`。
src layout 有助于避免工作目录中的源码掩盖安装问题；改成 flat layout 后，必须用项目外 cwd 和隔离安装包验证发行，不能只在项目根运行测试。

目标顶层保持简洁：

| 目录/文件 | 职责 |
| --- | --- |
| `cevns_pyeft/` | 可导入的运行时包 |
| `data/` | 外置的源谱、校准、核响应、观测、背景与数据溯源 |
| `configs/` | 本次分析选择、后端和允许的数值覆盖 |
| `examples/` | 可运行的用户示例 |
| `tests/` | 单元/行为/集成验证及受保护参考 |
| `docs/` | 当前使用、架构、物理约定与限制 |
| `tools/` | 当前仍使用的核验、发行、复现工具 |
| `schemas/` | 已有数据/接口契约 |
| `workflows/` | 项目实验接入流程和决策记录；不进入运行时依赖 |
| `outputs/` | 本地计算结果、图、日志和核缓存 |
| `pyproject.toml`、`README.md`、`AGENTS.md` | 安装、入口说明、项目规则 |

这一轮不同时重排 `cevns_pyeft` 内部全部物理模块，也不把包内 experiments 与外置 data 合并成同一个目录。

## 3. 文档与“剪枝”的精确处理

### 3.1 保留并改为当前职责命名

以下路径相对 Gitup01。移动后修复 README、文档内链接和命令示例。

| 现有位置 | 目标位置 |
| --- | --- |
| `docs/experiment_modularization/USAGE.md` | `docs/USAGE.md` |
| `docs/experiment_modularization/PARAMETER_OWNERSHIP.md` | `docs/PARAMETER_OWNERSHIP.md` |
| `docs/experiment_modularization/CAPABILITY_MATRIX.md` | `docs/CAPABILITY_MATRIX.md` |
| `docs/experiment_modularization/SKILL_OPERATION_GUIDE.md` | `docs/SKILL_OPERATION_GUIDE.md` |
| `docs/interface_refactor/README.md` | `docs/COMPONENTS.md` |
| `docs/interface_refactor/FAST_AND_CACHE.md` | `docs/FAST_AND_CACHE.md` |
| `docs/experiment_modularization/analysis_selection.example.yaml` | `configs/analysis_selection.example.yaml` |
| `tools/build_modularization_wheel.py` | 可整理为 `tools/build_wheel.py` |
| `tools/verify_modularization_release.py` | 可整理为 `tools/verify_wheel.py` |

新增简短的 `docs/README.md`、`docs/LAYOUT.md`、`data/README.md`。
README 应以四实验统一入口为主，删除对仓库中不存在的 `README_FINAL.md`、`FINAL_STATUS.md`、`KNOWN_LIMITATIONS.md`、8B 压缩包和 Notebook 的“已保留”断言。若用户现场确实有这些文件，则先盘点再分类，不以远程缺失断言本地不存在。

### 3.2 从主项目移出、按原字节归档

默认归档到 Gitup01 外的独立历史压缩包；不要把原来的杂乱内容原样塞进新的 `docs/archive`。

历史文档候选：

- `docs/interface_refactor/R0_R3_REPORT.md`
- `docs/interface_refactor/R4_R6_REPORT.md`
- `docs/experiment_modularization/MIGRATION_REPORT.md`
- `docs/experiment_modularization/RELEASE_02.md`
- `docs/experiment_modularization/CHANGE_MANIFEST.json`
- `docs/experiment_modularization/FILE_CHANGES.md`
- `docs/experiment_modularization/resolved_experiments.json`（原机器路径快照，不当作运行配置）
- `docs/experiment_integration/VALIDATION_RESULT.txt`
- `docs/experiment_integration/INTEGRATE_CEVNS_EXPERIMENT_SKILL.md`（旧设计文本；确认未被当前入口引用后归档，现行 Master workflow 保留）

一次性/阶段脚本候选：

- `tools/_modularization_edit.py`
- `tools/finalize_modularization_report.py`
- `tools/capture_modularization_baseline.py`
- `tools/verify_modularization_baseline.py`
- `tools/verify_conus_statistics_migration.py`
- `tools/verify_unified_fast.py`
- `tools/refactor/report_r4.py`
- `tools/refactor/write_report.py`
- `tools/refactor/write_review.py`
- `tools/refactor/check_legacy_fast.py`
- `tools/refactor/check_wheel.py`
- `tools/refactor/validate_interface_fast.py`
- `tools/refactor/compare_baseline.py`

阶段输出候选：`outputs/conus-paper-config-guard-20261002/` 下三份已生成结果。保留生成器、测试和物理解释的可追溯关系；先检查当前代码是否读取这些产物。

**这些是逐项审查清单，不是允许按通配符清空目录。** 若仍有实际入口依赖，先迁移依赖或暂留，不按年代删除。

### 3.3 明确禁止误删的内容

1. `tools/refactor/freeze_baseline.py`：两个现有测试从它导入 `points`、`GRIDS`。试清理已证实直接删除会造成两个测试收集错误。
   正确做法是先把这些确定性测试数据定义等值提取到 `tests/helpers/regression_cases.py`，增加必要包文件并更新两个测试导入。保持参数值和参考不变；确认其他调用方后，才归档冻结脚本。也可在轻量阶段先保留它。
2. `tests/reference/**`：原数组、元数据和历史哈希不删除、不重生成，不因目录移动改写历史来源路径。
3. `docs/nuclear_response_convention_audit.md`、`docs/antineutrino_sign_helicity_audit.md`、`docs/legacy_operator_coverage.md`：仍解释现有模型约定，保留。
4. `docs/CONUS_docs/*.pdf` 和 `docs/experiment_integration/experiment_inputs/**`：属于物理依据，已有 evidence ledger 引用原路径。轻量阶段保留；如后续移入 references，必须做独立路径映射，不能冒充不相关文件删除。
5. `workflows/**`：保留规则、模板和已有决策状态；不把清理当作删除科学审批依据的理由，不改正式 Gate。
6. `data/**`：不凭名称猜测无用；尤其不能因某数据尚未注册就删除。
7. `tools/conus/**` 和 `tools/experiment_integration/conus_paper_config_guard.py`：仍具复现/核查用途，保留并说明外部资源要求。
8. `backup/**` 不参与自动扫描和候选判定。本任务未要求备份恢复/审计，不读取其中内容。

归档流程：列精确文件 → 搜索 Python 导入、动态路径、CLI 和文档链接 → 记录 SHA256 → 写归档 → 逐文件解压校验 → 移出主项目 → 修复入口 → 验证。
无 Git 的用户目录也必须能通过归档和 manifest 恢复；不要仅依赖审查者的 Git 历史。

## 4. 实验 data 的最终安排

### 4.1 推荐目录与身份

使用 `data/experiments/<experiment_slug>/<dataset_id>/`。
同家族不同发布、运行分析或定义版本应有明确身份；年份不是运行期的自动替代。

| 已有分析 | 规范目录 |
| --- | --- |
| CsI2017 | `data/experiments/COHERENT_CsI/CsI2017/` |
| CsI2021 | `data/experiments/COHERENT_CsI/CsI2021/` |
| Ar2020 | `data/experiments/COHERENT_Ar/Ar2020/` |
| CONUS+ 候选 | `data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/` |

各目录按实际内容分为 `source/`、`detector/`、`statistics/`，附来源说明/资源清单。没有实际文件就不建空子目录。
共用核响应继续放 `data/responses/responses_all.json`，不要复制到每个实验目录。
共享源表只有在确有多个使用者、且物理版本相同时才提取为公共资源；不能为“统一”复制或合并不同谱表。

`cevns_pyeft/experiments/.../definition.py` 选择实现、参数与资源；`data` 保存表格和来源。
模型/算法在包内，实验输入在包外；两者通过资源 ID 和明确合同关联，不依靠同名文件夹猜测。

### 4.2 当前文件到规范位置的迁移表

| 当前资源 | 目标安排 |
| --- | --- |
| `data/datafiles/COHERENT_eff.txt` | `.../COHERENT_CsI/CsI2017/detector/COHERENT_eff.txt` |
| `data/datafiles/COHERENT_data.txt` | `.../COHERENT_CsI/CsI2017/statistics/COHERENT_data.txt` |
| `data/datafiles/COHERENT_lower.txt` | 同一 CsI2017 statistics 目录 |
| `data/datafiles/COHERENT_upper.txt` | 同一 CsI2017 statistics 目录 |
| `data/datafiles/COHERENT_spectrum.txt` | 同一 CsI2017 statistics 目录；先确认它当前只作兼容/参考还是实际 likelihood 输入，保留原语义 |
| `data/datafiles/CENNS10AnlAEfficiency.txt` | `.../COHERENT_Ar/Ar2020/detector/CENNS10AnlAEfficiency.txt` |
| `data/experiments/CsI2017/*` | 对应 COHERENT_CsI/CsI2017 下的同类 spec/provenance |
| `data/experiments/CsI2021/*` | 对应 COHERENT_CsI/CsI2021 下的同类 spec/provenance |
| `data/experiments/Ar2020/*` | 对应 COHERENT_Ar/Ar2020 下的同类 provenance |
| CONUS+ 当前规范目录 | 保持；按需补明确的统计资源，不迁成另一个短 ID |
| `data/responses/responses_all.json` | 保持共享路径 |
| `data/datafiles` 的其他资源 | 暂留；另行确认所有者和使用情况，不批量删除 |

此表中的 `...` 表示 `data/experiments`，具体执行 manifest 必须展开为完整相对路径。

CsI2021 和 Ar2020 的部分观测数值当前内联在 definition 中。本轮可以继续以该字段为唯一来源。
若决定外置成数据表，应单独迁移：数据文件拥有数组，definition 仅引用资源；不能保留两份独立修改的“默认值”。

### 4.3 路径兼容与配置权威

1. 迁移前核对每份实际数据的内容哈希，不改其单位、列顺序、有效数值或分箱。
2. 每个资源提供逻辑键、所属数据集/共享作用域、规范路径、必要旧路径、单位、坐标合同、来源与版本。
3. 新入口只通过明确资源目录解析。旧入口通过有限的旧→新路径映射保持兼容，不扩大 `_data_path` 的猜测搜索。
4. Windows 环境不把 symlink 作为必要条件。不长期维护两份可分别修改的权威数据副本。
5. 若规范路径与旧路径同时存在且内容冲突，明确报错并列出路径；不能悄悄选择其中一份。
6. 修复旧 spec discover 逻辑中的重复身份风险。不要通过复制两份 `experiment.yaml` 产生重复 dataset。
7. 当前 API 的 `ResourceCatalog.root` 是“包含 data 的资源根”，不是直接的 data 目录。先保持这个合同；若改名为 data_root，需要显式版本/兼容处理，不能静默改变含义。
8. 对多个实验的覆盖使用作用域，例如公共 `responses` 与 `(dataset_id, resource_id)` 专用覆盖。保持旧单实验写法兼容，但对未使用键明确拒绝；跨实验批处理在整份选择中核对键的归属。
9. 有限选择 YAML 仍只负责启停、后端和已支持数值项。它不执行 import，也不成为另一套物理参数权威。

### 4.4 CONUS+ 统计文件的特殊处理

当前默认三探测器各 119 kg·day 合计 357 kg·day，只是此候选的 forward 配置。
已有 19 点数字化 Gaussian benchmark 对应独立 effective119、C3 类配置，不可当作默认合计的观测，也不可给三个探测器重复使用。

为该基准提供明确命名的配置构造器，例如 `make_effective119_benchmark_definition()`，避免让用户手工改多个曝光字段。名称是建议，不能冒充官方新 dataset_id。

若用户现场存在已声明的旧观测 CSV，先验证原来源、列、坐标和归一化，再将其作为明确输入纳入 `statistics/approximate_paper_benchmark/`，记录原路径和哈希。
若文件缺失：预测仍可运行；真实数据集成测试报告明确缺少资源。测试套件区分有独立 synthetic 数据的单元测试与需要真实外部数据的集成测试；不能简单跳过原失败就宣称科学统计已通过。

## 5. 平铺源码的具体修改

执行移动：`src/cevns_pyeft/` → `cevns_pyeft/`，不保留第二份源码，不更改公开包名。

`pyproject.toml` 的目标配置：

```toml
[tool.setuptools]
package-dir = { "" = "." }

[tool.setuptools.packages.find]
where = ["."]
include = ["cevns_pyeft*"]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

逐项更新：

- 测试中定位包的 `src/cevns_pyeft`，以及子进程 `PYTHONPATH=ROOT/src`。
- 保留的工具中的 `sys.path` 设置或改为要求 editable install；不要每份脚本新增一套路径猜测。
- README 的安装、CLI 和源码直接运行说明。
- 当前文档/配置示例的移动后链接。
- AGENTS 的当前运行时路径说明。旧 evidence ledger 和冻结元数据中的历史路径不改写；说明旧 src 路径与新包路径的映射即可。

建议将以下重复的默认资源根计算集中到 `foundation/paths.py`：

| 现有文件 | 当前问题 |
| --- | --- |
| `experiments/loader.py` | 固定 `parents[3]` |
| `experiments/specs.py` | 固定 `parents[3]` |
| `statistics/datasets.py` | 固定 `parents[3]` |
| `statistics/predictors.py` | 固定 `parents[3]` |
| `experiments/coherent/statistics_binding.py` | 固定 `parents[4]` |
| `experiments/conus_plus/source.py` | 固定 `parents[4]` |
| `experiments/conus_plus/slow_counts.py` | 固定 `parents[4]` |

公共帮助函数只处理资源根定位，不读取实验、不选择物理模型。
源码 checkout 可默认指向包旁的项目资源；安装 wheel 后，应显式传外部资源根，缺失时报具体错误。
不能以搜索 cwd、父目录或同名文件来掩盖路径错误。

## 6. 接口修复要求

### 6.1 深层不可变及实际物理身份（I02/I03）

- 对内置设定中的 list、dict、ndarray 做防御性复制和规范化；tuple 字段不能只靠类型注解。
- 需要替换的用户扩展组件提供可序列化的参数/资源/实现描述；运行时快照不得共享调用方可变容器。
- 外层物理指纹必须由实际模型、执行策略和资源建立。`prepare` 改变实际源、响应或截面时，不能仍与原模型具有相同身份。
- 为不返回 ExperimentModel 的 legacy executor 提供等价的实际执行描述，不能只给 CsI2021 修补。
- 分离 dataset/analysis 身份、物理依赖身份和统计输入身份；相同箱数不能代替身份验证。
- 缓存不必依赖 callable 的内存地址或 repr；使用稳定实现标识/版本/内容与实际参数。未声明的扩展能力应拒绝缓存复用。
- 实例加载后如果检测到其真实依赖被修改，应拒绝继续计算或要求重新加载，不能继续附着旧指纹。

验收：外部 list 修改不改变已加载实例；公开装配入口改变实际源后必须改变物理身份；不能把变化后的预测交给原实验对象评价。

### 6.2 资源覆盖严格消费（I01）

校验所有显式覆盖键是否有定义/被所选数据集使用。缺文件应显示 dataset、逻辑资源 ID 和实际路径。
对大小写、别名、数据集作用域进行确定性处理，不默默忽略拼写错误。
禁用实验不读取资源文件，但选择层仍可核对声明是否合法。

### 6.3 外部统计数据的观测合同（I04）

统计 loader 返回含以下信息的对象，而非只有 ndarray：

- dataset/analysis/profile 身份；
- 观测轴及单位；bin edges 或有明确定义的中心/宽度；
- counts、counts/PE、按质量归一的谱等 observable 语义；
- 观测/背景/误差与坐标的对应关系；
- 原始来源、实际内容哈希、必要的转换记录。

验证缺列、错单位、乱序、重复坐标、错误箱宽及同长度错误坐标。
无坐标的历史表须由显式 schema 绑定其确切分箱，不允许靠“刚好 19 行”推断。
重新排序若被支持，必须同步重排所有数据列并记录；否则明确拒绝。
CsI2017 的外部表也需要对应检查，不能只修 CONUS+。

不得借此更改现有近似 likelihood 的科学含义；events/bin 到 counts/PE 只除一次箱宽。

## 7. 物理组件的下一步整理

这部分在目录与输入稳定后实施，单独提交，不与文件移动混在一起。

### 7.1 复用现有接口

保留现有 `InteractionModel.dsigma_dT`、`DifferentialCrossSection`、`ExperimentModel`、`RecoilYield`、`Prediction` 和观测合同。
理论模型规定算符/匹配，`TheoryPoint` 表示本次 Wilson 参数值；参数扫描不等同于更换模块。

至少让每个 executor 明确收到源、靶材/核数、相互作用、响应、曝光及积分策略。
可以保留专用 executor，但不得在内部重新选择与传入定义无关的固定实现。
把共同 CsI 材料配方放入中立材料模块，解除 CsI2017 对 CsI2021 definition 的依赖。

### 7.2 两种归一化路径

按物理语义命名，不按 COHERENT/CONUS 名称命名：

1. **累计注量 + 实际核数**：源为 `cm^-2 MeV^-1`；与截面积分得到每核、运行期的反冲产额密度；最后按核数和响应计数。
2. **每秒通量 + 每 kg 核数 + kg·day**：源为 `cm^-2 s^-1 MeV^-1`；率明确为每 kg 每秒或每天；只转换一次 86400，再乘质量时间积。

当前 `RecoilYield` 不是 rate。需要质量时间路径时增加明确的率对象/归一化记录，不把 per-second flux 塞进 DetectorFluence，也不伪造 mass=1 kg/live_time=119 day。
接口记录源分量、核素、探测器、坐标、单位和已包含的归一化因素。

### 7.3 保留算法差异

- CsI2021：保留已有 gamma/效率/分量接受率与离散顺序。
- CsI2017：保留确定性映射、Jacobian 和历史网格；不要换成窄 Gaussian。
- Ar2020：保留现有 sigma(observed)、效率列和历史轴约定，单位争议另行科学审计。
- CONUS+：保留分段 Gauss、源表拼接、候选 Ge73 约定和有名探测器结果。

积分器控制如何求积，响应模型控制探测概率；二者不能混成一个隐式实验名称分支。
反冲谱在应用依赖 T 的响应前不能先积分成总数。时间选择可能依赖源分量；若能量与时间不可分离，不能只用一个常数接受率替代联合分布。

截面应保留粒子种类、入射态、算符基底/尺度、核响应通道与运动学约定。
一般 EFT 核响应不压缩成单个标量 form factor。注册新过程也不自动获得下游响应/Fast 支持。
本任务不实现 νe、新非弹性过程、天然 Ge 替换、官方 CONUS likelihood 或联合 χ²。

### 7.4 分阶段诊断与缓存

按需公开截面、每核产额/单位质量率、响应权重和最终分箱结果。若保留 raw，写清其尚未乘过哪些因素，不把历史 raw 改名冒充实际材料贡献。

| 改动 | 预期影响 |
| --- | --- |
| 已支持基底内的 Wilson 系数 | 用系数核重构预测；不必重新编译参数无关核 |
| 源谱或核响应 | 重算反冲谱；包含它们的物理核失效 |
| 探测器效率/响应 | 折叠更新；包含折叠的核失效 |
| 曝光 | 依实际表示重缩放或重建；不能复用已含旧曝光的矩阵 |
| 统计观测/误差 | 重评统计；纯物理核不因该变化自动重建 |

CONUS+ 的 detector_response_matrix 与 CsI 系数核不同：源/截面改变时，如果反冲网格等实际依赖未变，响应矩阵可继续使用。不要为统一名字假装两者加速了同一条链。

## 8. Codex 工作包与顺序

| 阶段 | 工作 | 完成标准 |
| --- | --- | --- |
| C0 现场与保护 | 核对 Git/本地差异、规则、当前文件；冻结本轮清单和测试状态 | 不回退用户修改；已知失败与新增失败可区分 |
| C1 源码平铺 | 移动包、打包配置、集中资源根、更新当前工具和测试路径 | 原导入名不变；四实验可运行；项目外 wheel 调用通过 |
| C2 安全剪枝 | 检查依赖、提取测试参数辅助定义、归档阶段文件、整理当前文档 | 无测试收集错误、无当前文档断链；可按哈希恢复 |
| C3 接口保护 | 修复 I01–I04，明确资源作用域与观测合同 | 四项独立复现均被正确处理；现有数值不变 |
| C4 实验数据归属 | 先 CsI2017，再 Ar2020/CsI2021；维护 CONUS 规范目录；资源显式绑定 | 输入内容不变；新旧路径可控；缺数据不伪造成功 |
| C5 物理链补齐 | 复用现有合同，逐个参数化 legacy/CONUS 的真实输入，保留策略 | 可单独替换一个源/截面/响应且产生预期影响，不修改公共实验名分支 |
| C6 发行与文档 | 干净进程全测、独立回归、wheel 和示例、清理清单、能力矩阵 | 实际结果可复现；未完成项明确，结果不依赖审查者的临时目录 |

各阶段使用独立提交或精确变更清单。布局提交不混入公式更改；数据迁移不混入新科学配置。
轻量目录整理可以先独立交付 C0–C2；C3–C5 是随后明确列出的工程完善任务，不能把它们写成目录整理已解决的问题。

## 9. 验收清单

1. `src/cevns_pyeft` 不再存在第二份源码，`import cevns_pyeft` 正常。
2. wheel 只包含目标运行时包，项目外 cwd 的四实验预测通过；数据显式外置。
3. 源码默认入口、旧统计入口和旧 spec loader 能找到预期资源或明确报缺失。
4. 当前 docs 的相对链接/命令有效，不再声称未交付输出已存在。
5. 归档有完整 manifest、SHA256 和恢复方法；两份回归测试不再依赖已移出的脚本。
6. 原参考数组、容差、物理数据和科学约定未被目录整理修改。
7. 四实验同进程 A→B→A 不污染实例；禁用项不读资源。
8. 资源键拼错、作用域错、必需资源缺失明确失败。
9. 加载后修改调用方提供的 list/dict 不改变已加载实例或其记录。
10. 实际装配后的源/截面/响应变化会改变正确的身份，旧结果不能误配给新实验。
11. 19 行但坐标错误的统计输入拒绝；CsI2017 外部表也检查坐标关系。
12. 数据移位后内容哈希一致；规范与旧路径冲突时拒绝，不能悄悄读取另一份。
13. CONUS 质量时间曝光缩放只生效一次；combined 是有名分项在相同箱上的求和。
14. 默认 357 配置不能评价 effective119 观测；明确命名的 benchmark 配置使用一次正确观测。
15. 只改观测/误差不重建无关物理核；改变受依赖的响应/曝光使旧核失效。
16. Wilson 扫描复用受支持的参数无关核；未支持基底/态/过程明确拒绝。
17. 新 synthetic 数据集只增加定义/必要组件和注册，不修改公共积分器的实验名称分支。
18. 最终代码停止修改后，在全新进程完整跑测试。真实外部数据缺失与环境位级差异分别报告，不通过伪造数据、改参考或放宽断言消除。

## 10. 最终交付

- 调整后的源码、安装配置、当前 README 和文档索引。
- `docs/LAYOUT.md`：当前目录及为什么如此安排。
- `data/README.md`：资源所有权、单位/坐标和兼容路径。
- 机器可读的文件变更/归档清单；旧→新路径、内容哈希、恢复办法。
- 受影响物理参数与缓存依赖说明，准确的能力矩阵。
- 所有验证命令、环境、完整测试输出和独立数值比较；科学收敛另行标注。
- 未解决项：缺失真实资源、旧位级测试环境问题、仍为 legacy 的能力等。

不要把历史 reports/outputs 自动加入 wheel，不要扫描 backup 获取验证输入，不自动安装/覆盖个人 Skill。
若现场项目有 Git，采用独立工作分支；若没有，先完成可恢复备份和精确清单。
本方案不要求推送、合并或部署；是否向远程发布以用户当前授权为准。

## 11. 可直接交给 Codex 的指令

```text
请在实际 Gitup01 项目中读取本方案并执行当前授权范围内的工程调整。

当前依据为 refactor/02-experiment-modularization-20261029，审查提交
bd54dba8835ed245374c5a9d1d113ed20917c33b。不要把该提交当作覆盖现场修改的理由。

用户已选择：去掉 src 一层，保留 cevns_pyeft 包名；清理无当前用途的历史处理文件；
实验 data 按实验家族/具体 dataset 组织，维护明确资源引用和旧路径兼容。

先执行 C0，核对当前代码、Git 状态、适用 AGENTS 和已有授权。对当前源码与此方案的
差异做只读比较。已有授权覆盖的工程动作不重复请求确认；不扩大物理科学范围。

按 C1–C6 分阶段工作，布局、清理、输入迁移和物理接口改动分别提交/记录。
不要删掉实际被测试导入的历史脚本：freeze_baseline.py 的 points/GRIDS 必须先提取
或暂留。归档先校验完整性，主项目不保留重复的权威源码或数据副本。

优先修复四个已有复现：未知资源覆盖被忽略、物理设定浅层冻结、实际模型未进入外层
指纹、外部统计数据坐标未校验。复用已有 InteractionModel/ExperimentModel 等合同。
不要为了统一架构复制 EFT 公式或把不同实验算法改成相同。

保留 CsI2017 14.6 kg 计数与 14.57 kg 源元数据差异、Ar2020 历史约定、CONUS Ge73
候选及 effective119/357 配置区分。不要新造观测 CSV、天然 Ge 结果或官方 likelihood。

审查环境原测试是 221 passed / 2 failed，不是全绿。缺失 CONUS CSV 与已有浮点位级
问题分别处理。原测试参考和容差不能为通过测试而更新。

交付实际代码、当前文档、数据路径/归档 manifest、可恢复清单、完整验证和未完成项。
明确说明完成的是哪些工程能力，不以“已模块化”概括尚未实现的组件替换或统计支持。
```

## 12. 源码依据与使用边界

以下链接固定到审查提交；指向原 src 布局，执行平铺后按本方案映射到包根：

- [定义与快照字段](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/src/cevns_pyeft/experiments/definition.py)
- [资源解析和外层指纹](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/src/cevns_pyeft/experiments/loader.py)
- [统一运行与统计校验](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/src/cevns_pyeft/experiments/runtime.py)
- [COHERENT 执行装配](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/src/cevns_pyeft/experiments/coherent/execution.py)
- [CONUS 执行及统计数据读取](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/src/cevns_pyeft/experiments/conus_plus/execution.py)
- [旧率积分中的 SNS 与质量耦合](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/src/cevns_pyeft/rates/counts.py)
- [仍依赖 freeze_baseline 的测试](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/tests/test_fast_model_contract.py)
- [当前数据集行为测试](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/tests/test_experiment_modularization.py)
- [Refactor-02 发布范围说明](https://github.com/chino616/fawenfalnjdn/blob/bd54dba8835ed245374c5a9d1d113ed20917c33b/Gitup01/docs/experiment_modularization/RELEASE_02.md)
- [Python 官方打包指南：src 与 flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

本方案中的新增路径、帮助函数和阶段是实施目标，除明确标为已有的内容外，不宣称已在用户项目完成。
