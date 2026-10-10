---
name: cevns-slow-counts
description: Phase 7 authoritative direct event-count calculation with a mandatory normalization ledger, convergence diagnostics and human freeze before any Fast implementation.
---

# Phase 7 — Slow Authoritative Calculation

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Hard precondition

Dataset/Target/Source/Theory/Kinematics/Detector 的需要 Gate 均 PASS + APPROVED。

## Step 1 — Normalization Ledger（必须先展示）

按实际项目 owner 写成：

```text
source differential flux/fluence [unit]
× differential cross section [unit]
× nuclei per kg [unit]
× exposure OR mass×time [unit]
× time conversion if required
= true recoil counts
× detector response density/matrix [unit]
× efficiency [dimensionless]
= reconstructed spectrum
× bin integration
= expected events/bin
```

每个因子列：source file、symbol、input/output unit、是否已经包含在其他 factor 中。

任何重复 normalization 必须在写 Slow 前解决。

### ⛔ Pre-code Decision

```text
1 批准当前归一化计算链（回复 APPROVE NORMALIZATION LEDGER）
2 修正某个因子的归属
3 查看公式或代码中的因子来源
4 暂停本阶段
```

## Step 2 — Direct calculation

Slow 必须直接执行批准的物理积分，不得依赖 EFT kernel、cumulative reconstructed Fast 或 global rescaling。

典型链：

```text
integrate Enu -> dR/dT
fold T -> reconstructed observable
integrate bins -> counts
```

输出 contract 必须与 dataset axes/shape/unit 一致。

## Step 3 — Diagnostics

保存：

```text
bin edges + units
component-resolved counts
total events
true recoil spectrum
reconstructed spectrum
integration grids/tolerances
normalization checkpoints
grid convergence
external/reference comparison (reference-only where appropriate)
```

测试 exposure scaling、support、finite/nonnegative counts、complex EFT points if supported。

## Machine Gate P07

通过 direct calculation、convergence、output contract、diagnostics、reference checks 后 PASS。

## ⛔ Authoritative Slow Freeze

Machine PASS 后必须再次展示关键数值和逐 bin/总计。

```text
1 将当前 Slow 结果定为后续计算的基准（回复 APPROVE SLOW AS AUTHORITATIVE REFERENCE）
2 重新计算或调整积分网格
3 查看归一化与能谱
4 暂停 Fast 阶段
```

只有用户选 1，Fast 才可开始。
