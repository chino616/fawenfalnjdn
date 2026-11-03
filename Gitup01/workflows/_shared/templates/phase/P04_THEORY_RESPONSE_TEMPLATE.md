# P04｜理论与核响应适用性

配合 [P04 Skill](../../../cevns-pyeft/skills/phases/cevns-theory-response/SKILL.md)、
[执行合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)与
[代码参考](../../references/phase/P04_NUCLEAR_RESPONSE_CODE_REFERENCE.md)使用。
用户提供模型和来源，AI 填写实现与验证；不要求用户设计函数。

## A. 用户材料与科学范围

| 内容 | 定义、单位、版本与来源定位 |
|---|---|
| dataset 或明确的理论变更范围；目标声明 | ____ |
| SM/EFT/比较模型及参数域 | ____ |
| Wilson 基底、单位、复数/flavor、SM 是否包含 | ____ |
| matching/LEC 与采用文献 | ____ |
| 靶核、响应表、基底、b 单位和有效动量域 | ____ |
| 所需核响应通道、LNC/LNV 与干涉约定 | ____ |
| ν/反ν及入射态需求 | ____ |
| 独立参考点、源表证据或缺失项 | ____ |

## B. AI 覆盖与实现判断

| 同位素/算符/通道 | 所需含义 | 实现 symbol、资源与版本 | 覆盖/取零/省略/缺失 | 证据与声明限制 |
|---|---|---|---|---|
| ____ | ____ | ____ | ____ | ____ |

逐函数分类：REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED。
说明内部基底一致性和外部源表审计分别完成到哪里；Helm-only 时明确响应表不适用的原因。
需要改变的物理选择及有效 decision refs：____；受影响实验：____。

## C. 验收与交接

检查：key/通道、单位、基底、复数共轭/flavor 轴、SM 加入、适用的独立 benchmark；
记录命令、数值、差异及来源。ν/反ν标签不能代替相互作用审计。
handoff 字段：theory_scope、coefficient_convention、nuclear_responses、coverage、
runtime_binding、external_evidence_limits。
结果写入 [阶段报告](PHASE_REPORT_TEMPLATE.md)，返回 Master。
新实验按依赖进入 P05；只读理论审核可在本次范围完成后交付，
仅当运动学或截面边界属于审核/变更范围时才安排 P05，不自动扩展任务。
