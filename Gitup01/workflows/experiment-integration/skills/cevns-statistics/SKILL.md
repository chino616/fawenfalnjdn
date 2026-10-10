---
name: cevns-statistics
description: Phase 9 statistical-model contract and implementation with hard data-semantics, background/covariance/nuisance and confidence-construction gates.
---

# Phase 9 — Statistics

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Precondition

所需 forward prediction 已验证。

## Step 1 — Data Semantics（硬门）

只能选择一个 primary mode：

```text
raw_counts
signal_plus_background
on_off
background_subtracted_excess
unbinned_events
```

必须展示支持该解释的 evidence。不能根据数值是否为整数等“猜”。

### ⛔ Decision

```text
1 批准当前观测数据解释（回复 APPROVE DATA MODE）
2 选择其他数据解释
3 查看数据或论文中的定义
4 暂停统计阶段
```

## Step 2 — Full statistical contract

展示/冻结：

```text
observed quantity + unit
bin/observable mapping
background definition
covariance
nuisance parameters + priors + correlations
likelihood/chi2 formula
test statistic
profiling/marginalization
confidence construction/threshold
published best fit/interval/significance benchmark if available
```

Hard rules：

- background-subtracted excess 可有负 bin，不能喂 raw Poisson；
- published total/significance 不足以重建 official likelihood；
- digitized/simplified statistics 明确标 approximate；
- 缺 covariance/correlation 时保持 BLOCKED，不猜。

## Step 3 — Implement/test

优先复用 shared statistics API；仅必要时 adapter。测试 toy values、nuisance profiling、best-fit/benchmark、input shape/unit。

## Gate P09 + Human Approval

报告实际公式、代码 symbol、数据文件和 benchmark 差异。用户批准后才能宣称相应 statistics capability。
