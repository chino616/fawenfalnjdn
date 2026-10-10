---
name: cevns-fast-counts
description: Phase 8 accelerated representations derived only from approved Slow, with explicit Fast type, cache invalidation semantics and per-bin validation.
---

# Phase 8 — Fast

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Precondition

Slow Gate P07 PASS + Human Slow Freeze APPROVED。

## Step 1 — Fast Type（不可模糊命名）

每个 representation 独立选择并命名：

```text
reconstructed_spectrum_cumulative
detector_response_matrix
eft_quadratic_coefficient_kernel
other_surrogate (必须定义数学意义)
```

对每种加速表示，先说明它加速了什么、适用范围和限制，再展示必要的核对项：

```text
省去的高成本计算
缓存的内容
构建时使用的输入
哪些参数变化会使缓存失效
输出维度、单位和元数据
适用的理论模型范围
构建成本与单次求值成本
作为基准的 Slow 函数
```

缺 EFT basis mapping => EFT kernel `BLOCKED`，不得生成 partial kernel；其他 Fast 可独立继续。

### ⛔ Fast Meaning Decision

```text
1 批准当前加速表示（回复 APPROVE THIS FAST REPRESENTATION）
2 修改表示类型或适用范围
3 查看它与 Slow 结果或系数基的关系
4 暂停这一种加速表示
```

## Step 2 — Build

从 validated Slow 推导，不修改 Slow 迎合 Fast。

cumulative：dense reconstructed spectrum -> cumulative -> edge differences。

EFT kernel：必须有完整 coefficient basis/order，构造全部 linear/quadratic terms，保存 convention/version metadata。

## Step 3 — Validation

必须逐 bin 比：

```text
Slow
Fast
abs difference
relative difference
tolerance
```

在多个 theory/parameter points 测试，不得只比较 total，不得用 global scale 修复。

## Gate P08 + Human Approval

每种 representation 独立 Gate/approval。最终报告必须明确“Fast 加速什么、没有加速什么”。
