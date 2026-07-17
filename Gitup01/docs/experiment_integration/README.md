# CEvNS 实验接入包

本包用于把一个新的 CEvNS 实验以“物理规格驱动”的方式接入 CEvNS-pyEFT。

它包含两类文件：

1. **通用 Skill**：规定任意 CEvNS 实验应如何拆成通量、靶核、曝光、真实核反冲谱、探测器响应、效率、分箱和事例数；
2. **具体实验规格**：给 Codex 一份尽可能接近可执行的 CONUS+/CONUS 物理输入说明。

## 目录

```text
skills/integrate-cevns-experiment/SKILL.md
experiment_specs/EXPERIMENT_SPEC_TEMPLATE.md
experiment_specs/conus_plus_2025_publication.md
experiment_specs/conus_plus_2025_reproduction.md
experiment_specs/conus_legacy_mathematica.md
prompts/CODEX_TASK_CONUS.md

data/external/dayabay/
data/conus_plus_2025/
data/conus_legacy_mathematica/

schemas/
scripts/
```

## 两个 CONUS 配置的区别

### `conus_plus_2025_publication`

这是面向 CONUS+ 首次观测论文的实现规格。包内已冻结公开可核对的内容，例如：

- KKL 反应堆功率与基线；
- 四种裂变同位素平均份额；
- C2、C3、C5 三台探测器；
- 327 kg·day reactor-ON、60 kg·day reactor-OFF；
- 160/170/180 eVee 阈值；
- 160–800 eVee 分析窗口；
- 标准模型总预测与测量总信号基准。

论文已公开 Lindhard 与低能分辨率参数；但逐探测器效率曲线、逐 bin 观测谱和完整背景模型没有公开为机器可读数据。论文明确说明完整数据暂不公开、可合理申请，因此这些内容保留为 `REQUIRES_INPUT`。

### `conus_plus_2025_reproduction`

这是可以直接编程的显式近似：使用 Daya Bay Eq. (8) 构造 KKL 谱形、固定总通量、论文公开的 Lindhard/分辨率参数、等分 detector 曝光和阈值阶跃效率。它用于完成代码链，但不宣称复现官方 likelihood。

### `conus_legacy_mathematica`

这是从用户提供的 Mathematica 参考程序抽取的回归配置，用于验证 Python 移植链：

- 固定探测器位置通量 `1.5e13 cm^-2 s^-1`；
- `Ge73_only`；
- 119 kg·day；
- Lindhard `k=0.162`；
- 分辨率参数 `sigma0=20.38 eV`、`F=0.1096`、`eta=2.96 eV`；
- 160 eVee 阶跃阈值；
- 160–350 eVee、10 eVee 分箱。

它不是 CONUS+ 2025 publication 模式。

## 使用流程

1. 阅读 `skills/integrate-cevns-experiment/SKILL.md`；
2. 选择一个实验规格：
   - 正式 CONUS+：`experiment_specs/conus_plus_2025_publication.md`
   - 可执行 CONUS+ 复现：`experiment_specs/conus_plus_2025_reproduction.md`
   - Mathematica 回归：`experiment_specs/conus_legacy_mathematica.md`
3. 填充 publication 模式中仍标记为 `REQUIRES_INPUT` 的数据文件；
4. 运行：

```bash
python scripts/validate_package.py
```

5. 将 `prompts/CODEX_TASK_CONUS.md` 连同本包路径交给 Codex。

## 重要限制

本包提供的是 forward-prediction 接入框架。没有正式逐 bin 数据、背景模型和协方差时，不应声称已经复现 CONUS+ 官方 likelihood。

## 主要参考

- CONUS Collaboration, *Direct observation of coherent elastic antineutrino–nucleus scattering*, arXiv:2501.05206, Nature 643 (2025).
- Daya Bay Collaboration, unfolded reactor antineutrino spectra, arXiv:2102.04614 ancillary data.
- Daya Bay Collaboration, high-energy reactor antineutrino spectrum, arXiv:2203.06686 ancillary data.
- 用户提供的 Mathematica 参考程序，2026-01-08 版本。
