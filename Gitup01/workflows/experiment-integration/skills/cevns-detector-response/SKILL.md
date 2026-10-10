---
name: cevns-detector-response
description: Phase 6 true-recoil to reconstructed-observable detector response, combining original implementation responsibilities with mandatory physics review.
---

# Phase 6 — Detector Response

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Ownership

```text
true recoil T
-> mean reconstructed observable / quenching / yield
-> resolution or migration R(x|T)
-> efficiency epsilon
-> threshold/window/bin semantics
```

Detector Response 与 nuclear Response 完全不同。

## Step 1 — Pre-code review

逐参数展示 value/unit/source locator/source class，并标 official/digitized/phenomenological approximation。

必须明确：

```text
true recoil variable + unit
reconstructed variable + unit
mean mapping formula
yield/quenching
resolution width/matrix
efficiency function
efficiency acts on T / mean x / reconstructed x
threshold semantics
analysis window/binning
```

Hard safeguards：

- threshold 不自动等于 step efficiency；
- 不得用 analysis-window 内重归一化偷偷吃掉 migration；
- detector-by-detector differences 合并成 effective detector 时必须明确是 approximation。

### ⛔ Decision

```text
1 批准当前探测器响应约定（回复 APPROVE DETECTOR CONTRACT）
2 修改淬火、分辨率或效率定义
3 查看来源材料或诊断图
4 暂停本阶段
```

## Step 2 — Technical implementation

按 manifest 选择 CONFIG_ONLY/ADAPTER 等。可实现：

```python
mean_reconstructed_observable(T, spec)
resolution_width(mean_x, spec)
response_density(x_reco, T, spec)
efficiency(x_or_T, spec)
```

实际命名服从仓库 API。

禁止在这些函数中 load flux、evaluate cross section、apply exposure、integrate final counts。

## Step 3 — Diagnostics/tests

```text
mean mapping physical range/monotonicity if required
resolution width > 0
response nonnegative + full-domain normalization
response mean/width
0 <= efficiency <= 1
efficiency domain
threshold/interpolation boundaries
scalar/array/broadcasting
out-of-range behavior
response grid + mean/resolution/efficiency plots
```

## Gate P06 + Post review

向用户展示 mapping 图、response slices、efficiency、代码 symbol 与 normalization test。用户批准后才进入 Slow。
