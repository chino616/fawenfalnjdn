---
name: cevns-dataset
description: Phase 1 dataset contract and runtime-spec implementation with mandatory human approval of dataset identity, reconstructed observable, binning and statistical data semantics.
---

# Phase 1 — Dataset

用户可见回复执行 `../../_shared.md` 第 1 节：先回答本轮问题；仅在相关时说明实际结果、影响、停下原因和下一步。下方字段用于核对，不是回复模板。
隔离自动运行执行 `../../AUTO_RUN_PROTOCOL.md`：本阶段产物只是候选；下方人工批准要求约束正式导入，不得在候选目录内写成正式 Human Gate。

## Physics ownership

本阶段只冻结并落盘：dataset identity、run/detector scope、observable、binning、output shape/unit、data mode、静态 exposure/target metadata。

不实现 source/detector/Slow/Fast/statistics。

## Read

```text
_shared.md
P01_EVIDENCE_LEDGER.yaml
P03_PHYSICS_CONTRACT.yaml
00_IMPLEMENTATION_MANIFEST.yaml
schemas/experiment.schema.json
src/cevns_pyeft/experiments/base.py
src/cevns_pyeft/experiments/specs.py
data/experiments/*/*/experiment.yaml
legacy data/experiments/*/experiment.yaml
```

## Step 1 — Pre-code Dataset Contract（不可自动批准）

用中文说明以下合同字段及其证据或用户决定；具体数值、单位和未决项仍须完整展示：

```text
dataset_id
publication/reproduction/phenomenology/legacy mode
site/run period
detectors included/excluded
observable + unit
analysis window
exact bin edges / edge rule
output axes + shape + unit
data mode:
  raw_counts | signal_plus_background | on_off |
  background_subtracted_excess | unbinned_events | not_yet_known
exposure semantics
```

每行附 evidence claim 或 user decision。

选项：

```text
1 批准当前数据集约定（回复 APPROVE DATASET CONTRACT）
2 修改约定或拆分数据集
3 查看证据
4 暂停本阶段
```

## Step 2 — Technical implementation

将批准字段映射到现有 schema，创建最小：

```text
data/experiments/<experiment_slug>/<dataset_id>/experiment.yaml
data/experiments/<experiment_slug>/<dataset_id>/README.md
runs/<experiment_slug>/<dataset_id>/01_DATASET.md
```

目录身份执行 `_shared.md` 的 `PER_EXPERIMENT_DATASET_DIRECTORY`。配置内的
`dataset_id` 仍是唯一机器标识，不能用 `experiment_slug` 代替。若现有 loader 只支持
平铺路径，应将递归发现或显式路径映射列为已批准的最小实现；不得建立第二套数据副本
来掩盖 loader 不兼容。

不得引入未批准字段。schema 无法表达时 BLOCK 或提出显式 schema extension，不得静默改 schema。

## Step 3 — Machine Gate P01

验证：unique ID、schema、loader、repository-relative paths、bin edges、bin count/shape、data mode、pending callables。

## Step 4 — Post-code Review

先说明实现了什么、自动检查是否通过，以及本次希望用户审核什么。随后按需列出：

- 实际创建或修改的文件；
- 已批准字段与 `experiment.yaml` 配置项的对应关系；
- 观测量、输出和曝光的单位；
- schema 与 loader 的检查结果。

使用中文标题，不打印 `[CODE]`、`[MAPPING]`、`[UNITS]`、`[TEST]` 标签。

### ⛔ Human Gate Dataset

先用一段话说明 P01 自动检查的结果、用户本次审核的具体内容，以及批准后是否
还需单独授权写入记录。不要只展示 Gate 名称或下面的英文口令。

```text
1 批准当前实现（回复 APPROVE IMPLEMENTATION）
2 指出需要修正的字段映射
3 查看配置或改动明细
4 暂停本阶段
```

只有 `P01=PASS` 且用户 APPROVED，Master 才可进入 Target。
