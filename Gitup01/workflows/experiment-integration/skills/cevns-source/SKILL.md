---
name: cevns-source
description: Phase 3 neutrino source implementation and review: support, components, interpolation/matching, absolute normalization, time basis and source-only API.
---

# Phase 3 — Source

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Ownership

只负责 differential flux/fluence 和 source metadata；禁止乘 target nuclei、exposure、detector response、binning。

## Step 1 — Pre-code Physics Contract

用中文说明以下源模型约定；需要用户审核的数值、单位、候选和证据仍须完整展示：

```text
flavor/components
energy support
formula/table source
interpolation
matching boundaries
extrapolation/outside-support behavior
flux or fluence unit
time basis: per second / integrated
absolute normalization
normalization uncertainty
```

### Reactor hard decision

如果是 reactor，明确且互斥地选：

```text
A detector-site absolute flux
B thermal power + fission fractions/energies + baseline
```

不用的 route 只能当 cross-check，不能再乘一次。

### ⛔ Physics Decision

```text
1 批准当前源模型约定（回复 APPROVE SOURCE CONTRACT）
2 修改归一化或能谱路线
3 查看论文表格、公式或数据
4 暂停本阶段
```

## Step 2 — Inspect repository API

读取实际 shared source/rate API、已有 experiment source adapter 和 manifest 指定 reference。记录：file/symbol/signature/input unit/output unit/array behavior。

## Step 3 — Implement smallest layer

按 classification：

```text
REUSE         不新增代码
CONFIG_ONLY   标量/表放 experiment.yaml/CSV
ADAPTER       src/cevns_pyeft/experiments/<family>/source.py
SHARED_EXTENSION / CORE_EXTENSION 需要 Master 额外批准影响范围
```

数值表必须保持论文 normalization convention，记录 interpolation 和边界。

## Step 4 — Tests/diagnostics

至少验证：

```text
energy support
finite/nonnegative where required
integrated normalization
component sum
boundary/matching continuity
interpolation/extrapolation
units
scalar/array behavior
source diagnostic CSV + plot
```

## Machine Gate P03

只有实现与测试通过才 PASS。

## Post-code Review

先说明实现和检查结果，再用中文标题列出公式或数表、代码位置与函数、输入输出
单位、归一化与边界检查，以及必要的图表。只有用户要求完整审计时才展开全部
符号和文件路径；不要逐项打印英文方括号标签。

用户选择 APPROVE/FIX/INSPECT/BLOCK。Machine PASS 不等于 Physics approved。
