---
name: cevns-target
description: Phase 2 target/isotope/exposure physics review. Freezes target inventory, Response keys and normalization ownership before source/cross-section/counting work.
---

# Phase 2 — Target / Exposure

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Physics ownership

```text
material/isotope composition
fraction convention
molar mass
nuclei_per_kg
nuclear Response key(s)
active mass / live time / exposure semantics
normalization ownership
```

本阶段通常是**物理核对阶段**，不因为 target 有小节就自动创建 target.py。

## Precondition

Dataset human gate APPROVED + P01 PASS。

## Step 1 — Mandatory review

用中文说明以下靶核与曝光核对项；需要用户决定的数值、单位和证据仍须完整展示：

```text
material
isotope list
abundance: number_fraction or mass_fraction
A/Z/N or molar mass source
nuclei_per_kg derivation
Response key for each isotope
active detector mass
live time
exposure
whether exposure already = mass × live time
seconds/day owner
```

### Hard normalization rule

同一 normalization 只能选一种：

```text
mass_kg + live_time
OR
exposure_kg_day
```

如果 sources 允许 natural isotope 与 single-isotope 两种解释，必须列两个候选，不得自行选择。

### ⛔ Physics Decision

```text
1 批准当前靶核与曝光解释（回复 APPROVE TARGET / EXPOSURE）
2 选择其他同位素或曝光解释
3 查看核响应数据或计算过程
4 暂停本阶段
```

## Step 2 — Technical verification

检查实际 response database/key、fraction sum、molar mass 和 nuclei/kg 计算；确认后续 Slow 不会再次乘相同 exposure 因子。

创建：

```text
runs/<experiment_slug>/<dataset_id>/02_DETECTOR_TARGET.md
```

除非 Master 已批准 `CONFIG_ONLY` 的静态字段补充，否则本阶段不写新的 target Python。

## Gate P02

PASS 条件：composition 完整、Response keys 存在/明确、exposure ownership 唯一、nuclei/kg 可复算。

Post review 后要求用户再次确认实现/报告与已批准 contract 一致。
