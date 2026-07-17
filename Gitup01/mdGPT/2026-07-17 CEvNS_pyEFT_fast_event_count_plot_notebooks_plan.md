# CEvNS-pyEFT 三个实验 Fast 事例数绘图 Notebook 方案

## 1. 目标

在 Fast Kernel 拆分已经完成的基础上，由 Codex 新建三个 Jupyter Notebook，复现三个实验的分箱事例数图：

```text
CsI2017
CsI2021
Ar2020
```

本任务只新增 `.ipynb` 文件，不修改物理公式、kernel、实验响应、slow 计算或统计代码。

Notebook 必须直接调用当前项目已经拆分完成的公开接口：

```text
fast kernel
→ coefficient vector
→ fast reconstruction
→ flavor/bin counts
→ plot
```

并使用对应 slow 结果做数值核对。

---

# 2. 新建文件

```text
src/cevns_pyeft/experiments/coherent/
├── fast_counts_csi2017_plot.ipynb
├── fast_counts_csi2021_plot.ipynb
└── fast_counts_ar2020_plot.ipynb
```

不要修改或替代已有：

```text
*_check.ipynb
```

检查 notebook 用于单元验证；本方案中的 notebook 专门用于完整事例数图展示。

---

# 3. 强制限制

Codex 必须遵守：

1. 只新增三个 notebook；
2. 不在 notebook 中复制任何物理公式；
3. 不重新实现 kernel reconstruction；
4. 不重新实现 detector response；
5. 不硬编码新的 Wilson coefficients；
6. 使用项目现有默认或 SM coefficient 构造接口；
7. 使用现有实验 bin、效率、曝光和 detector response；
8. 不修改 `core/engine.py`；
9. 不修改 `kernels/`；
10. 不修改 `rates/`；
11. 不修改 `slow_counts_*.py`；
12. 不修改 `fast_kernel_*.py`；
13. 不生成新的 `.py` 绘图模块；
14. 不提交额外 PNG/PDF 文件，图只在 notebook 内联显示；
15. 不使用 `core.engine` 作为新调用入口。

正确调用应来自：

```text
kernels/reconstruction.py
experiments/coherent/fast_kernel_*.py
experiments/coherent/slow_counts_*.py
```

---

# 4. 备份要求

三个 notebook 均为新建文件，因此不需要备份。

如果 Codex 发现必须修改任何已有文件，必须先停止并说明原因。

只有在确认修改确实必要后，才允许按照既有规则备份：

```text
backup/YYYYMMDD_HHMMSS__原路径__文件名
```

并登记到：

```text
backup/BACKUP_MANIFEST.md
```

原则上本任务不应修改任何已有文件。

---

# 5. Notebook 统一结构

每个 notebook 最多使用 4 个代码单元。

## 单元 1：导入和固定配置

只做：

- 导入 NumPy；
- 导入 Matplotlib；
- 导入对应 fast reconstruction 接口；
- 导入对应 slow counts 接口；
- 构造项目当前默认/SM coefficient；
- 指定已有 reference kernel 或调用当前 fast builder。

不得在该单元定义物理 helper。

## 单元 2：计算 Fast 与 Slow counts

输出至少包括：

```text
prompt νμ
delayed νe
delayed anti-νμ
total
```

要求：

- fast 和 slow 使用完全相同的 coefficient；
- fast 和 slow 使用相同实验配置；
- 保留逐 flavor、逐 bin 数组；
- 计算前后不手动重新归一化。

## 单元 3：严格数值检查

至少执行：

```python
np.testing.assert_allclose(fast_total, slow_total, rtol=..., atol=...)
```

并检查：

```text
bin 数一致
shape 一致
dtype 合理
所有 counts 有限
总 counts 有限
```

容差必须使用项目当前 fast-vs-slow 已有容差。

不得为了通过检查而自行放宽容差。

## 单元 4：绘图

每个 notebook 只生成一张图、一个坐标轴。

不得使用多 panel 或复杂排版。

---

# 6. 统一绘图内容

每张图至少包含：

```text
prompt νμ
delayed νe
delayed anti-νμ
Fast total
Slow total
```

推荐表达：

- 三个 flavor 分量使用 step 或 bar；
- Fast total 使用清晰实线；
- Slow total 使用点或虚线；
- fast 与 slow 应在视觉上重合；
- 不手动指定颜色；
- 不使用 seaborn；
- 不使用子图；
- 不添加无关装饰。

如果项目中已有 observed counts 和 background，并且它们与当前 bin 定义完全一致，可以额外加入：

```text
observed data
background
```

否则不得补写或猜测数据。

---

# 7. 坐标轴要求

## 7.1 CsI2017

文件：

```text
fast_counts_csi2017_plot.ipynb
```

横轴：

```text
CsI2017 PE bin
```

或使用当前代码中实际定义的 PE bin center。

纵轴：

```text
Expected events / bin
```

图中必须体现：

```text
CsI2017 实际采用的 1.17 PE/keV 线性映射
```

但 notebook 不重新实现该映射，只调用：

```text
slow_counts_csi2017.py
fast_kernel_csi2017.py
```

中的现有实现。

标题建议：

```text
COHERENT CsI2017 expected event counts
```

---

## 7.2 CsI2021

文件：

```text
fast_counts_csi2021_plot.ipynb
```

横轴：

```text
CsI2021 PE bin
```

或使用当前代码中的 PE bin center。

纵轴：

```text
Expected events / bin
```

必须使用已有完整链：

```text
quenching
→ PE smearing
→ logistic efficiency
→ PE-bin counts
```

不得使用 CsI2017 的 1.17 PE/keV 映射。

标题建议：

```text
COHERENT CsI2021 expected event counts
```

---

## 7.3 Ar2020

文件：

```text
fast_counts_ar2020_plot.ipynb
```

横轴必须使用当前 Ar2020 代码中实际定义的 reconstructed observable 或 bin center。

不得自行猜测单位或改名。

纵轴：

```text
Expected events / bin
```

必须使用已有完整链：

```text
reconstructed observable mapping
→ Gaussian smearing
→ efficiency
→ bin counts
```

标题建议：

```text
COHERENT Ar2020 expected event counts
```

---

# 8. 数据来源

优先使用已经生成并验证的 reference kernel。

推荐顺序：

```text
1. 加载项目已有 reference kernel
2. 使用 kernels/reconstruction.py 重建
3. 使用 slow_counts_*.py 计算 slow reference
4. 对比后绘图
```

只有在 reference kernel 不存在时，才允许在 notebook 中调用小网格 fast builder。

不要在绘图 notebook 中重新生成完整大 kernel，避免运行时间过长。

不得修改：

```text
data/kernels/reference/
```

---

# 9. Fast 数组处理要求

Notebook 应保留 kernel 原有轴契约，不得猜测 axis。

应使用项目已有 reconstruction helper 完成：

```text
target sum
flavor separation
response-channel sum
bin output
```

不得在 notebook 中手动书写新的 `einsum`、矩阵收缩或 axis permutation。

如果 reconstruction API 返回：

```text
flavor × bin
```

则直接用于绘图。

如果只返回 total，需要调用项目已经存在的 flavor-resolved reconstruction 接口；不得自行重构 kernel。

---

# 10. Slow 数组处理要求

三个 slow 文件必须分别提供完整实验入口：

```text
slow_counts_csi2017
slow_counts_csi2021
slow_counts_ar2020
```

Notebook 只调用这些公开入口。

不得从 notebook 内部重新组合：

- flux；
- target mass；
- efficiency；
- smearing；
- bin integration。

---

# 11. Notebook 最终输出

每个 notebook 最后必须输出一行摘要：

```python
print({
    "experiment": "...",
    "bins": int(...),
    "fast_total": float(...),
    "slow_total": float(...),
    "max_abs_diff": float(...),
    "status": "PASS",
})
```

并显示一张完整事例数图。

Notebook 必须在：

```text
Kernel → Restart & Run All
```

后无错误运行。

---

# 12. 三个 Notebook 的最低检查项

## 12.1 CsI2017

检查：

- 25 个 PE bins，或以当前代码实际 bins 为准；
- 三个 flavor 分量；
- fast total；
- slow total；
- 逐 bin 差异；
- 总 counts；
- 无 NaN/Inf。

## 12.2 CsI2021

检查：

- 9 个 observable bins，或以当前代码实际 bins 为准；
- 三个 flavor 分量；
- fast total；
- slow total；
- 逐 bin 差异；
- 总 counts；
- 无 NaN/Inf。

## 12.3 Ar2020

检查：

- 12 个 observable bins，或以当前代码实际 bins 为准；
- 三个 flavor 分量；
- fast total；
- slow total；
- 逐 bin 差异；
- 总 counts；
- 无 NaN/Inf。

---

# 13. 验收标准

三个 notebook 全部满足：

- 可独立 Run All；
- 不调用 `core.engine`；
- 不复制物理计算；
- fast 和 slow 使用同一 coefficient 点；
- fast 与 slow 逐 bin 在既有容差内一致；
- 总 counts 在既有容差内一致；
- 三个 flavor 分量均被展示；
- 横轴使用实验真实 observable；
- 只生成一张图；
- 图只保存在 notebook 输出中；
- 未修改任何已有 `.py` 文件；
- 未修改 reference kernel；
- 未引入新的物理参数。

---

# 14. 停止条件

出现以下情况立即停止：

- fast 和 slow bin 数不同；
- axis 含义无法从 metadata 或公开 API 确认；
- 必须手动猜测 flavor axis；
- 必须修改 kernel 才能绘图；
- 必须修改 slow counts 才能绘图；
- 必须调用 `core.engine`；
- fast 和 slow 差异超过项目既有容差；
- reference kernel 与当前 basis、channel 或 bin metadata 不一致；
- 实验 observable 单位不明确。

停止后只输出差异和缺失信息，不要自行修复物理代码。

---

# 15. 给 Codex 的最终指令

1. 新建三个 notebook：
   - `fast_counts_csi2017_plot.ipynb`
   - `fast_counts_csi2021_plot.ipynb`
   - `fast_counts_ar2020_plot.ipynb`
2. 每个 notebook 使用现有 fast kernel reconstruction 和对应 slow counts。
3. 每个 notebook 最多 4 个代码单元。
4. 每个 notebook 只生成一张分箱事例数图。
5. 图中展示三个 flavor 分量、Fast total 和 Slow total。
6. 优先加载已有 reference kernel，不重新生成完整 kernel。
7. 不在 notebook 中复制 physics、smearing、matching 或 reconstruction 公式。
8. 不调用 `core.engine`。
9. 不修改任何已有 `.py` 文件。
10. 不生成额外 PNG/PDF，只保留 notebook 内联图。
11. 使用项目已有 fast-vs-slow 容差。
12. Run All 后必须输出 PASS 摘要。
13. 如果必须修改已有文件，先停止并报告，不要直接修改。
