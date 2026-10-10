---
name: cevns-validation
description: Phase 10 full capability validation, registry exposure and final scientific-claim review, keeping internal numerical validation separate from external publication/likelihood reproduction.
---

# Phase 10 — Validation / Release

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Step 1 — Gate matrix

读取所有阶段状态，先用中文概述已验证能力和仍受阻的能力，再展示核对表：

```text
阶段 | 自动检查 | 人工确认 | 证据状态 | 可用能力
```

区分：

```text
internal numerical self-consistency
legacy/reference-code regression
publication forward reproduction
official likelihood reproduction
```

前一个 PASS 不推出后一个 PASS。

## Step 2 — Full regressions

运行：

- 当前 dataset focused tests；
- shared theory/nuclear/rates/kernel regressions（若相关）；
- 既有实验 regression，尤其 CORE/SHARED_EXTENSION 时；
- stale metadata/cache checks；
- registry load/discovery tests。

不得修改 reference、容差或物理输入来强迫通过。

## Step 3 — Registry exposure

只暴露 Machine + Human 均通过、且满足必要 evidence 的 callable/capability。metadata discovery 不等于 implemented。

## Step 4 — Final Scientific Claim（硬门）

用中文说明以下最终审核内容；允许与不允许的科学主张必须明确分开：

```text
已验证的能力
仍受阻的可选能力
已知近似
与论文或数据集定义的差异
实际运行的测试和诊断
参考材料的来源
目前允许的科学主张
目前不允许的科学主张
```

选项：

```text
1 批准当前最终状态（回复 APPROVE FINAL STATUS）
2 修改科学主张或修正实现
3 查看完整阶段检查表
4 暂停发布
```

## Gate P10

仅 final approval 后可把对应状态写入 completion report/registry。

最后根据所有 section-approved contract 渲染 canonical：

```text
physics_docs/experiments/<experiment_slug>/<dataset_id>/experiment_physics.tex
```

未实现 capability 仍必须保留 BLOCKED/NOT_IMPLEMENTED，不得美化。
