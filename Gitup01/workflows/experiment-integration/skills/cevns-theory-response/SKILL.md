---
name: cevns-theory-response
description: Phase 4 shared EFT/matching/nuclear-response routing review. Prevents experiment-specific duplication and validates Response keys/channels/coefficient conventions.
---

# Phase 4 — Theory / Nuclear Response

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Ownership

确认项目共享理论链能否覆盖该 dataset：

```text
Wilson coefficients
-> nucleon matching
-> particle/nuclear responses
-> amplitude contraction
-> shared differential-cross-section API
```

实验模块不得无理由复制第二套理论公式。

## Step 1 — Mandatory review

展示实际代码调用链和文件/symbol，并列出：

```text
coefficient basis + order
flavor routing
complex coefficient support
nuclear Response key(s)
response channels implemented/omitted
SM comparison model (e.g. Helm) validity domain
```

Hard rules：

- full nuclear response 后不得再额外乘 Helm；
- Helm/SM-only comparison 不得悄悄接受一般 EFT；
- `CORE_EXTENSION` 会影响其他实验，必须单独 Physics Decision。

### ⛔ Decision

```text
1 批准复用现有理论计算路线（回复 APPROVE SHARED THEORY ROUTE）
2 修改靶核或系数的调用路线
3 查看核响应或匹配代码
4 暂停本阶段
```

## Step 2 — Technical validation

运行 shared theory regressions、Response key/channel tests、complex coefficient tests、SM benchmark；仅在必要时实现最薄 adapter。

## Gate P04

PASS 后进行 post-code review，用户批准后才进入 kinematics/cross section。
