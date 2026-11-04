# Onboarding IR 与现有 Compiler / Renderer

人类报告内容的唯一规范是
[Experiment Physics Report Contract](../../workflows/_shared/references/onboarding/experiment-physics-report-contract.md)。
本页只说明真实代码入口、输入映射、输出和兼容行为。

## 什么生成什么

| 环节 | 实际入口 | 输入 → 输出 |
|---|---|---|
| 材料与审阅 | [Master](../../workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md)、[Onboarding](../../workflows/cevns-pyeft/skills/onboarding/cevns-onboarding/SKILL.md) | H0–H3 审阅材料、证据与配置；P00–P03 记录身份、claim、问题与合同 |
| IR 整理 | 现有研究人员/AI 整理步骤；[synthetic fixture](../../tests/helpers/onboarding_drafts.py) 是可编译示例 | 已整理的来源/合同和显式数组 → `cevns-onboarding-draft/1` |
| 历史采集适配器 | [pilot](../../tools/build_csi2021_onboarding_pilot.py)、[migration](../../tools/migrate_legacy_input_packages.py) | 迁移前资料 → acquisition IR；本次不运行重提取 |
| CLI | [compile_experiment_package.py](../../tools/compile_experiment_package.py) | 显式 draft / NPZ 或现有 package → 对应输出 |
| Compiler | [package_compiler.py](../../cevns_pyeft/experiments/package_compiler.py)：`compile_draft` | 校验、受控派生和确定性 NPZ → 两个机器文件与两份 MD |
| Renderer | [input_package.py](../../cevns_pyeft/experiments/input_package.py)：`render_physics`；[generic_input.render](../../cevns_pyeft/experiments/generic_input.py) 委托它 | 同一只读文档/数组/报告元数据 → 详细版或精简版 |
| Writer | 原有 `write_package` | 将编译输出映射交给原有备份、同目录替换、ACL 检查和失败恢复逻辑 |

当前没有自动读取 P00–P05 的通用 Builder；材料/P03 到 IR 仍需显式整理。
P00/P02 现在分别有 SOURCE_REGISTER_TEMPLATE.yaml 和 MISSING_AND_CONFLICTS_TEMPLATE.md，
它们是 Workflow 模板，不是 Python 转换器。P04/P05 与后续阶段未改。

## 生成命令

在项目根目录沿用已有命令：

```powershell
python -B tools/compile_experiment_package.py --draft draft.json --arrays declared.npz --output package
python -B tools/compile_experiment_package.py --draft draft.json --arrays declared.npz --output package --check
```

完整编译输出固定为：

- `experiment.input.yaml`：标量、模型、来源、资源声明和能力状态；
- `experiment.resources.npz`：数值数组；
- `experiment.physics.md`：详细实现版；
- `experiment.physics.summary.md`：精简阅读版，链接详细版。

旧 YAML 的三文件 `formal_files` 声明作为兼容数据保留，本次不回写。
摘要是新派生阅读文件，不成为 Runtime 输入，不修改 dataset/resource manifest。

默认 create-only，显式 `--overwrite` 复用原 Writer 的备份与覆盖；
`--check` 只读比较全部本次预期输出。已有 `--report <path>` 仍是可选参数，
默认不生成额外 JSON 报告。

## 现有包只重渲染两份 MD

```powershell
python -B tools/compile_experiment_package.py --output data/experiments/COHERENT_CsI/CsI2021 --md-only --overwrite
python -B tools/compile_experiment_package.py --output data/experiments/COHERENT_CsI/CsI2021 --md-only --check
```

`--md-only` 只读目标目录内的 YAML/NPZ，严格验证后一次提交两份 MD 给同一 Writer。
不与 `--draft/--arrays` 混用，不写 YAML/NPZ、manifest 或其他报告。
既有恢复备份仍由原 Writer 存入 `backup/package_compiler/` 并登记备份清单。

API 不增加新生成器：`render_physics(data, arrays)` 返回详细版，
`render_physics(data, arrays, summary=True)` 返回精简版。
`generic_input.render` 支持相同可选参数并委托同一函数。
`write_package(None, None, directory, md_only=True, overwrite=True)` 更新两份 MD。

`validate_package` 总是核对详细版；存在摘要时也核对摘要。
旧格式包缺少摘要仍可读取；新编译与 `--md-only --check` 均要求两份派生 MD，
摘要被修改时不会静默通过。

## P03 与报告元数据的真实映射

保留 P03 v4 和原 sections：

```text
sections.validation_claim.fields.physics_report.value
    → document.extensions["lab.physics_report"]
```

`models` 是以精确 model ID 为键的映射，值含
`group/content_class/title/explanation/equations`；不添加 id 字段，不改成列表。
report 的 `summary/calculation_steps` 有内容时才填，空模板只留 `models: {}`。

符号 `parameter_ref` 精确解析为一个 YAML Parameter ID 或 NPZ key；
验证存在性、唯一性和单位。数学常量/推导中间量使用 null。
未知字段、未知模型/参数/资源、重复公式 ID、重复符号及单位不符都拒绝，
不按名称相似度匹配。

既有三包的 YAML 没有报告 namespace 时，沿用已登记 binding 的显式只读报告视图；
新 P03/IR 元数据优先。两份报告从相同输入生成，不回写旧包配置。
未分类模型显示 H3_UNCLASSIFIED_MODEL，不自动展开公式。

## 写入与验证

本次只扩展现有输出文件映射，Writer 的备份、flush/fsync、同目录临时文件、
内容回读、继承 ACL、替换与恢复原语保持原样。
`CEVNS_TARGET_WINDOWS_PRINCIPAL`、WRITE_OK、ACL_INHERITANCE_OK、
TARGET_USER_READ_OK/PENDING 的区别不变；沙箱读取不代表目标用户实读。

相关测试位于 [test_package_compiler.py](../../tests/test_package_compiler.py)：
两份同源报告、实验内容完整性、共享模块不展开、精确 NPZ 引用、只读 check、
重复覆盖、权限和写入失败恢复；现有 schema 测试继续检查机器合同。
Markdown 只使用当前数学语法；语法解析与实际窗口预览的验收分别说明。

修改归属：Renderer/Schema → experiments README；Compiler → tools README；
H0–H3、六个模板及 P03 Schema → workflows/_shared 与 cevns-pyeft README；
测试 → tests README；两份 CsI2021 报告 → dataset README；
示例 → examples README。材料目录只读，不把模板或示例当成 Runtime 输入。

[v1 输入 Schema](../../cevns_pyeft/experiments/input_package.schema.json) · [v2 输入 Schema](../../cevns_pyeft/experiments/generic_input.schema.json) · [共享报告规范](../../workflows/_shared/references/onboarding/experiment-physics-report-contract.md)
