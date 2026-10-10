---
name: cevns-kinematics-cross-section
description: Phase 5 elastic kinematics and differential-cross-section routing with explicit units, support, endpoint tests and model validity.
---

# Phase 5 — Kinematics / Cross Section

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Ownership

```text
E_nu_min(T)
T_max(E_nu)
physical support
dsigma/dT routing
unit conversion
comparison model validity
```

不做 source normalization、exposure 或 detector folding。

## Step 1 — Pre-code review

展示实际公式/公共 API，并固定：

```text
E_nu unit
T unit
target mass convention
dsigma/dT output unit
support condition
full_response vs comparison model
```

如果存在多个 kinematic conventions/approximations，列出选项。

### ⛔ Physics Decision

```text
1 批准当前运动学与截面路线（回复 APPROVE KINEMATICS/CROSS-SECTION ROUTE）
2 修改模型或单位约定
3 查看共用截面代码
4 暂停本阶段
```

## Step 2 — Implement/route

优先复用 shared differential cross-section。实验 adapter 只负责 target/source-compatible wrapper、kinematic bounds 和单位桥接。

## Tests

```text
T=0 / small recoil behavior
endpoint Tmax
inverse relation Enu_min
below/above support -> zero/error per contract
unit conversion
finite/nonnegative SM where appropriate
full_response with EFT coefficients
SM-only comparison rejects unsupported EFT
```

## Gate P05 + Post review

展示至少一个可复算 endpoint 数值和代码 symbol，Machine PASS 后再让用户 APPROVE。
