# 新 CEvNS 实验完整 Workflow

## 1. 输入

Codex 的输入为：

```text
physics_docs/experiments/<dataset_id>/experiment_physics.tex
论文、补充材料和机器数据
可选的旧程序、notebook 或 reference arrays
当前 Gitup01 仓库
```

物理文档应采用以下逻辑片段：

```text
实验目标
数据集
探测器与靶材
中微子源
振幅与 Response
运动学与截面
探测器响应
Slow 事例数
Fast 事例数
统计分析
计算目标
```

PDF 中给出的通用物理计算链是：

```text
Flux
→ target inventory
→ dσ/dT
→ true recoil spectrum
→ detector response
→ binned counts
→ statistics
```

Workflow 的输入加载顺序是：

```text
target inventory
→ Flux / source
→ dσ/dT
→ true recoil spectrum
→ detector response
→ binned counts
→ statistics
```

这里的顺序是工程上的阶段顺序，不表示 target 在物理上依赖 source。

项目代码的理论链继续复用：

```text
LEFT coefficients
→ nucleon coefficients
→ particle/nuclear responses
→ |M|²
→ dσ/dT
```

新实验不得在实验模块中复制这条理论链。

---

## 2. CsI 的使用方式

CsI2017/CsI2021 是已验证的参考实现，但只允许逐模块参考。

允许参考：

- public API；
- import 关系；
- 数据到配置的组织方式；
- source/target/detector 分量如何保留；
- Slow 返回数组的 shape；
- Fast kernel 如何调用通用 `kernels/`；
- reference arrays 和逐 bin 测试方式。

禁止复制：

- SNS 谱到非 SNS 实验；
- Cs/I 靶材到其他靶；
- CsI quenching、PE 映射或时间结构；
- CsI efficiency；
- CsI 的统计数据定义；
- CsI 的数值参数。

每个 Skill 只读取 `CSI_REFERENCE_MAP.md` 中该模块列出的参考文件。

---

## 3. 固定阶段

| Phase | 调用 Skill | 读取模板 | 主要产物 | Gate |
|---|---|---|---|---|
| 0 | `$cevns-experiment-intake` | `00_IMPLEMENTATION_MANIFEST.md` | 数据集拆分、输入清单、模块分类、文件计划 | I |
| 1 | `$cevns-dataset` | `01_DATASET.md` | `experiment.yaml` 骨架、dataset identity、bin axes | D0 |
| 2 | `$cevns-target` | `02_DETECTOR_TARGET.md` | detector inventory、target inventory、Response keys 的文本核对报告；不写 target 代码 | T0 |
| 3 | `$cevns-source` | `03_SOURCE.md` | source 数据和 source adapter | S0 |
| 4 | `$cevns-theory-response` | `04_THEORY_RESPONSE.md` | 理论覆盖报告或最薄 adapter | T1 |
| 5 | `$cevns-kinematics-cross-section` | `05_KINEMATICS_CROSS_SECTION.md` | 运动学和截面接口验证 | X |
| 6 | `$cevns-detector-response` | `06_DETECTOR_RESPONSE.md` | quenching/yield、resolution、efficiency、migration | R |
| 7 | `$cevns-slow-counts` | `07_SLOW_COUNTS.md` | `slow_counts_<dataset>.py` 和 Slow reference | L |
| 8 | `$cevns-fast-counts` | `08_FAST_COUNTS.md` | Fast representation、逐 bin Slow/Fast 比较 | F |
| 9 | `$cevns-statistics` | `09_STATISTICS.md` | 数据读取、χ²/likelihood、nuisance profile | Q |
| 10 | `$cevns-validation-registry` | `10_VALIDATION_REGISTRY.md` | registry、全量测试、完成报告 | V |

每个阶段完成后必须停止并输出：

```text
完成的文件
运行的测试
数值结果
尚未解决的问题
下一个 Skill
```

自动连续执行时，也必须保留每个 Gate 的报告，不能跳过。

---

## 4. 模块分类

每个模块只能选择一个状态：

| 状态 | 含义 | 处理 |
|---|---|---|
| `REUSE` | 当前通用模块直接覆盖 | 不新增物理实现 |
| `CONFIG_ONLY` | 只需 YAML/CSV/NPZ | 不新增 Python |
| `ADAPTER` | 核心可复用，接口不同 | 增加最薄实验 adapter |
| `SHARED_EXTENSION` | 同一实验族可共享 | 增加 family-level 模块 |
| `CORE_EXTENSION` | 通用 theory/rates/kernels 不覆盖 | 单独修改核心并运行全局回归 |
| `BLOCKED` | 关键输入缺失 | 停止 |

不得因为物理文档有一个小节，就自动创建一个同名 Python 文件。

---

## 5. 通用落盘规则

```text
物理标量
→ data/experiments/<dataset_id>/experiment.yaml

数值表
→ data/experiments/<dataset_id>/*.csv

大数组、迁移矩阵、EFT templates
→ data/experiments/<dataset_id>/*.npz

必须新增的实验物理函数
→ src/cevns_pyeft/experiments/<family>/*.py

Slow
→ src/cevns_pyeft/experiments/<family>/slow_counts_<dataset>.py

Fast
→ src/cevns_pyeft/experiments/<family>/fast_kernel_<dataset>.py
  或 fast_<method>_<dataset>.py

统计
→ 优先复用通用统计函数；
  无法配置时才创建 statistics_<dataset>.py

验证基准
→ tests/reference_<dataset>/
  或 data/experiments/<dataset_id>/reference_values.*
```

---

## 6. 每个阶段的文件边界

### Phase 0

只允许创建：

```text
runs/<dataset_id>/00_IMPLEMENTATION_MANIFEST.md
runs/<dataset_id>/00_INPUT_INVENTORY.md
```

不得修改生产代码。

### Phase 1

只允许创建或修改 dataset 数据、配置和 dataset 验证测试。
不得提前写 target、source、Slow、Fast 或 Statistics。

### Phase 2

只允许创建或修改 `runs/<dataset_id>/02_DETECTOR_TARGET.md`。
这是 target 文本核对阶段，不创建 target 代码、target CSV、target 测试，
也不修改 `experiment.yaml`。

### Phase 3-6

只允许修改当前模块的数据、配置、adapter 和测试。
不得提前写 Slow、Fast 或 Statistics。

### Phase 7

只实现 Slow。  
不得创建预计算 kernel 代替物理积分。

### Phase 8

只从已验证 Slow 推导 Fast。  
不得修改 Slow 使其迁就 Fast。

### Phase 9

只按数据定义实现统计。  
不得把 background-subtracted excess 当 Poisson 原始计数。

### Phase 10

只做 registry、回归测试和报告。  
不得修改物理实现强制通过 benchmark。

---

## 7. 必须保留的验证层级

```text
INPUT_PARSED
DATASET_VALIDATED
TARGET_VALIDATED
SOURCE_VALIDATED
THEORY_VALIDATED
CROSS_SECTION_VALIDATED
DETECTOR_RESPONSE_VALIDATED
SLOW_VALIDATED
FAST_VALIDATED
STATISTICS_VALIDATED
FULLY_INTEGRATED
```

未通过前一级，不能声明后一级。

---

## 8. Codex 的起始指令

```text
读取 EXPERIMENT_WORKFLOW.md。
读取指定实验物理文档。
调用 $cevns-experiment-intake。
只生成 Phase 0 的两个报告，不写生产代码。
```
