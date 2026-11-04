# Task 02 — Canonical Experiment Input Package Schema

日期：2026-11-04。工程任务完成；科学输入继续为 DRAFT/PARTIAL。

## 基线、授权和实际目录

分支：`refactor/07-gitup01-20261104`。实际 HEAD：
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。
项目根为当前 07 worktree 的 `Gitup01/`，不是同级无有效 Git 身份的目录。

开始时保留了 Task 01 的三份 README 修改、未跟踪报告/工具，以及被忽略的三文件。
没有 stash/reset/clean、切换分支、提交或推送。用户后来明确要求各任务总结后连续执行，
该指示覆盖任务包中每项停止等待的默认约定；完成 Task 02 后继续 Task 03。

任务依据为所提供目录中的 CODEX_TASK_RULES.md、TASK_SEQUENCE.md 和
CODEX_02_CANONICAL_INPUT_SCHEMA.md。审计使用当前真实三文件、Task 01 报告和 builder，
以及 specs.py、registry/manifest、资源审计工具、JSON Schema、pyproject、共同输入规范，
并追踪 execution、SNS 源、target inventory、differential、matching、LEC、amplitude、
recoil/folding 和 statistics binding/profiler 的真实消费者。未将备份用作物理证据。

## 已交付内容

- [正式 JSON Schema](../cevns_pyeft/experiments/input_package.schema.json)
- [只读校验与 MD 渲染](../cevns_pyeft/experiments/input_package.py)
- [命令行验证入口](../tools/validate_experiment_input.py)
- [显式 Pilot 迁移适配](../tools/csi2021_input_contract.py)
- [更新后的三文件](../data/experiments/COHERENT_CsI/CsI2021/README.md)
- [合同说明](software/experiment-input-package.md)
- [正向和负向测试](../tests/test_input_package_schema.py)

schema_version 已从 `cevns-experiment-input-pilot/1` 升级为
`cevns-experiment-input/1`。engine_compatibility 独立声明 API/组件合同版本；
没有把 Schema PASS 写成模型绑定、参数消费、端到端运行或人工科学批准。

## 全部参数的角色审计

| 角色 | 数量 | 结果 |
|---|---:|---|
| direct_input | 65 | 有 model/slot/单位和代码消费者证据；作用范围明确。 |
| derived | 12 | 只读缓存，有有序输入、受控推导 ID、依赖指纹和重新计算校验。 |
| runtime_control | 12 | 反冲/能量/PE 采样与源表插值设置，区分运行期与资源生成消费。 |
| reference_only | 11 | run_mass_metadata，以及 Cs/I 的 Z/N/J/T 和单同位素分数描述；无数值消费者。 |
| unused_snapshot | 5 | lecs.Sigma_ud、L9、L10、m_u、m_d；从 active model parameter_refs 排除。 |
| materialized_derived_resource | 3 个数组 | 源能量网格和两条已归一化连续谱，不属于标量角色计数。 |

全部 105 个标量的值和 adopted_value 保持不变；完整角色、消费者阶段、物理含义、单位、
来源和 fingerprint_scope 直接渲染在 Physics MD。未只凭参数名把整组 LEC 认定为使用中。
旧缓存可能因整体代码/元数据哈希变化而失效，这与 canonical 数值消费影响分别记录。

## 归一化和派生权威方案

连续谱 NPZ 是当前运行的物化探测器注量，已包含 POT、每 POT 产额与几何稀释；
运行期数组为权威，额外因子列表为空，重复归一化会被机器拒绝。
原始 POT/yield/baseline 和源表生成设置作为生成依赖保留，改变后使数组 stale。
prompt 线的 F 由同一组输入只读推导，不与连续谱互相额外乘入。

靶质量分数、单核 kg/GeV 质量、核数、源注量和端点不再是可独立编辑的真相。
派生缓存必须与显式上游计算一致，且指纹保留输入顺序：Cs/I 质量分数分子不同，
即使输入集合相同也不能共用一个指纹。没有把 kg、核数或曝光重复乘入。

源能量网格、两个连续谱记录参数/模型 revision/坐标数组的生成 fingerprint。
每个数组仍有 key、shape、dtype、单位、轴/坐标、归一化、用途与 SHA256。
NPZ 字节与 Task 01 完全相同：
`25043e6f510f0ae643a532c53cec2c4b0dad1f2af7172247add5fdc99adc827a`。

## 格式和校验覆盖

正式 `.yaml` 使用已声明的严格 JSON-compatible YAML 1.2：拒绝重复 key、普通 YAML
简写、注释、自定义 tag/object、NaN/Infinity 及溢出非有限值。没有引入 PyYAML。
复用已有 workflow QA 使用的 jsonschema/Draft202012Validator，并在
`pyproject.toml` 的可选 `validation` 依赖中声明 `jsonschema>=4.18`。
旧 Runtime 正常导入不要求该可选依赖。

校验覆盖：严格/闭合字段、受控扩展 namespace、已声明模型 ID、模型/参数/资源依赖环、
真实消费者反向引用、单位/slot、布尔/数值与积分节点类型、只读派生值、物化指纹、
数组双向 key/shape/dtype/轴/哈希、重复归一化、能力 blocker、人工状态和历史 spec 权威。
安全 NPZ 读取拒绝 object/pickle、重复 ZIP 成员、路径/key 不匹配及超出所列 QA 大小限制。

数学表达和 matching/particle_response 符号展开均为 audit_only。
`x-model-contracts` 只有受控 slot/单位元数据，没有 callable；当前 17 模型的 binding
仍是 NOT_IMPLEMENTED。Schema 校验和简单派生核验没有实现 Task 03 的 Physics Model Registry，
也没有实现 Task 04 的 Loader 或第二套 Runtime。

Physics MD 改为同源确定性渲染，覆盖全部模型解释、公式、变量单位、参数角色/来源、
消费者、数组和未决问题；额外手写参数或数值漂移会被拒绝。

## 能力和历史 spec 冲突

分别记录 legacy prediction、package-backed prediction、Fast、legacy approximate
statistics、official likelihood、general antineutrino EFT 和 scientific release。
旧预测/近似统计保留已有内部回归证据；package Runtime 全部 NOT_RUN；
Fast 仅记录旧接口存在，不标为 package-supported；官方 likelihood 和科学发布保持 BLOCKED。

旧 experiment.yaml 保留且标记为 legacy_compatibility，并保存 historical_spec_status。
其历史 fast_validated、phase flags 和失效 run/reference 路径没有被提升成当前批准。
旧 statistics blocked 指权威来源不足，不等于当前没有可运行的近似 Gaussian。
新机器规格以 experiment.input.yaml 为准；实际计算在 Task 05 前仍以原 Python definition 为准。

## 实际验证

执行环境：`F:/Work/.codex_conda_envs/codex-py311/python.exe`，依赖沿用已安装环境。

| 命令/检查 | 实际结果 |
|---|---|
| validate_experiment_input.py --check-schema | PASS，Draft 2020-12 meta-schema。 |
| validate_experiment_input.py 当前 CsI2021 目录 | PASS，17 models / 105 parameters / 23 arrays。 |
| build_csi2021_onboarding_pilot.py --check | PASS，当前源码提取→显式迁移→正式合同→三文件一致。 |
| pytest test_input_package_schema.py + test_experiment_specs.py | 46 passed；涵盖格式、未知字段/模型、环、消费者、重复归一化、stale、单位、派生值、官方来源、能力/人工状态、NPZ、MD、只读性和旧说明兼容。 |
| pytest test_refactor_csi2021_regression.py -k 'small or same_prediction' | 12 passed，16 deselected；旧九箱小网格与近似统计冻结回归。 |
| validate_resource_manifest.py --root . --dataset CsI2021 | PASS；旧绑定核响应与原登记 SHA256 一致。 |
| 对 Task 01 恢复点比较 | 全部 105 个 value 完全相同；NPZ 原始字节完全相同。 |

测试开发阶段修正过一处新测试语法及一处负向错误消息期望；最终测试真实执行通过，
没有放宽验证器或科学容差。默认大网格收敛、全量 Fast、隔离安装、package-only 运行和
官方物理复现未执行，本报告不记 PASS。文档/保护检查结果在交接前完成并追加。

## 变更清单和恢复

| 操作 | 内容/归属 | 影响 |
|---|---|---|
| 新增 | input_package.py/schema、validate_experiment_input.py、csi2021_input_contract.py、schema 测试 | 只读合同及显式迁移工具，不改变旧执行路径。 |
| 修改 | CsI2021 YAML/Physics MD、旧 experiment.yaml、builder | 角色/权威/指纹/渲染合同及兼容说明；数值和 NPZ 不变。 |
| 修改 | pyproject 可选 validation 依赖和 schema package data | 让声明的 schema 真正随验证模块可用，不切换实验数据分发。 |
| 新增/修改 | 本报告、合同说明、进度索引及各 owning README/共同规范入口 | 路径和真实消费者导航同步。 |
| 精确更新 | PROTECTED_FILES.json 中本次修改的五个既有保护项 | 仅 CsI2021 README/spec、experiments README、pyproject、旧 schema 目录 README；其他科学文件/冻结数组哈希不变。 |

15 个被修改文件的起始版本保存在 `backup/task02-canonical-input-20261104/` 对应原路径，
复制前后 SHA256 逐项完全相同；清单登记于 backup/BACKUP_MANIFEST.md。
恢复点含 Task 01 的用户当前状态，不覆盖旧 Task 01 备份；恢复副本只用于恢复，非科学来源。
NPZ、物理核心、Prediction/Statistics 合同、现有 Loader/Catalog/registry/resource manifest、
其他实验及冻结 reference 均未改变。

## 下一任务交接

Task 03 输入：v1 Schema、17 个受控模型合同、明确的 scalar/resource consumer slots、
DRAFT/PARTIAL 的 CsI2021 fixture 和现有 Runtime。需建立真实受控实现绑定与每模型测试，
分别记录 binding、parameter consumed、Runtime 和科学状态；不得 eval 数学审计字符串。
在 Task 03 改变元数据状态前必须保留这些独立状态，不能把本报告的 Schema PASS 推广成 Runtime PASS。

[合同说明](software/experiment-input-package.md) · [续跑进度](ONBOARDING_TASKS_02_10_PROGRESS.md)

## 最终交接检查

受影响的 11 个 Markdown 文件共 151 个本地链接检查通过。保护清单除五个既有条目更新外，
还显式登记了 input_package.py、schema JSON 和三份正式输入文件这五个获准新增文件。
其余原有保护项哈希保持不变。

全局 Skill-pack 检查的结构/fixtures 通过，但整体检查仍 FAIL：另一路工作出现的
coherent/csi2021_package.py 和 csi2021_package_contract.json 被报告为保护区未登记新增。
配套 tests/test_csi2021_input_package.py 也不属于本任务实现。用户要求三者保留原样；
本任务不修改、不登记它们，也不将该全局检查记为 PASS。

普通 git diff --check 对保护清单的 CRLF 行结束符报告空白问题；显式允许 cr-at-eol 后检查通过。
这属于现有行结束符格式，没有改变物理值、回归参考或容差。Task 02 完成；后续任务的
绑定与运行证据单独记录，不能反向更改本任务当时的 NOT_RUN 事实。
