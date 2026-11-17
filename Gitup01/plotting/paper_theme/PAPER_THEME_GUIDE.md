# CEvNS-pyEFT 论文图主题 v4.0 — 清晰增强、12 色扩展

> 本文档和同目录 `PAPER_THEME.json` 共同定义**内容无关**的论文图主题。JSON 是绘图参数的机器可读权威。v4 在 v3 基础上**适度加深主体颜色、保持柱状填充明亮、提供 12 个固定系列身份及超过 12 个系列时的编码策略**。示例图全部是合成数据，不是实验预测或统计结果。

## 1. 保留不变的绘图契约

- 原有 `schema`、`colors.blue/vermillion/green/magenta/amber/sky/purple`、`colors.series_order`、`default_roles`、`bar_style` 等键保持可读取。新增键不会使只依赖旧字段的绘图代码失效。
- 字体 STIXGeneral、数学字体 stix；86/180 mm 画布；9/9.5/10 pt 字号层级、线宽、刻度、图例、PDF/SVG/PNG 导出规范全部保留。
- 不能为了配色改变物理输入、数据、归一化、分箱、置信区间、残差定义、坐标范围。不能把误差或负贡献隐藏。
- **映射由物理对象身份决定**：同一数据集/模型/耦合项在频谱、残差、扫描和二维约束中保持同一系列身份。不能按绘图调用顺序重新配色。

## 2. v4 色板：线条稍深、柱形中浅，保留 v3 的清爽感

| 顺序 | 键名 | 名称 | 曲线/轮廓 | 柱状填充 |
|---:|---|---|---|---|
| 1 | `blue` | Ocean blue | `#2879B8` | `#82B7DC` |
| 2 | `vermillion` | Coral | `#D66B50` | `#EDA996` |
| 3 | `green` | Teal | `#218D7B` | `#7FC5B4` |
| 4 | `magenta` | Rose | `#BB6293` | `#D9AAC5` |
| 5 | `amber` | Ochre | `#BB9432` | `#E5C679` |
| 6 | `sky` | Iris | `#8271BC` | `#B2D9E5` |
| 7 | `purple` | Aqua | `#3D9FB5` | `#BFB3DE` |
| 8 | `burgundy` | Wine red | `#A94C55` | `#D8A5AE` |
| 9 | `olive` | Olive | `#718C4E` | `#BCCE9C` |
| 10 | `rust` | Copper | `#B57737` | `#DFB38A` |
| 11 | `slate` | Slate | `#596E96` | `#AAB9CF` |
| 12 | `forest` | Fern | `#568B60` | `#9AC8A7` |

前三色维持蓝 → 珊瑚 → 青绿的语义。第四至第十二色允许不同数据集/模型的扩展；它们不预先绑定任何特定物理可观测量。对高密度图，12 色是可用资源，**不是一幅图必须一次用完**。

- 主要线条相较 v3 更深，边界和误差棒也略增强；保留白色背景、很浅的网格。
- 柱状图采用与曲线同色相、**更浅但不发白**的不透明色块；相邻堆叠块用 0.55 pt 白色细线。总量轮廓用 `ink`，不使用纯黑粗边。
- `ink=#344B61` 为数据/总量/文字，`frame=#768CA1` 为坐标框，`grid=#E6EDF3` 为辅助网格，禁止将参考线冒充数据。

## 3. 多颜色兼容：12 色 + 线型/标记/纹理可扩展至 24+ 系列

### 3.1 稳定系列身份

按照**全项目预先约定的物理对象顺序**分配一个固定的整数 `series_index`，例如一个数据集的 index=2。全论文中永远不重排其颜色、标记及柱状填充。`PAPER_THEME.json` 的 `series_palette` 将每一个 index 关联到 color、bar_fill、linestyle、marker、hatch。`colors.series_order` 按相同顺序提供与旧接口兼容的颜色数组。

### 3.2 不同系列数量下的用法

| 系列数 | 使用方式 |
|---|---|
| 1–3 | 采用前三色，线型及符号复编码 |
| 4–6 | 按固定身份扩展 4–6 色，简单图中可共存 |
| 7–12 | 可以用十二色，但**必须**用不同线型及点形；柱状超过 6 分量建议加纹理或分面；长图例外置/分组 |
| 13–24 | 复用 1–12 色，但用不同线型/点形，并在柱图上加纹理；同一面板尽量不画全部系列，优先拆分图组 |
| 更多 | 仍可确定性地编码，但不承诺凭肉眼能分辨每条曲线；应分面、分组、直接标注或交互筛选 |

**重要限制：** 没有 12 种颜色能保证在所有色觉条件、低分辨率或灰度打印中两两充分可辨。因此色板兼容多系列，但不等于 12 条挤在一起也能单凭颜色区分。尤其是蓝/石板蓝、珊瑚/铜棕、青绿/蕨绿等相近色，必须加线型、标记或分面。

### 3.3 在程序中调用

提供 `theme_styles.py`：

```python
from plotting.paper_theme.plot_template import load_theme
style = load_theme()
ax.plot(x, y, **style.line_style(7, label="Model H"))
ax.bar(bin_centers, yields, **style.bar_style(7, label="Component H"))
# 13th series (index=12) gets the first hue but a different linestyle and marker
ax.plot(x, y13, **style.line_style(12, label="Model M"))
```

调用者负责先给对象登记稳定 index，函数自身不推断物理身份，也不改变任何数据数组。`line_style` 的字典可直接用于 `plot`；`bar_style` 的字典可直接用于 `bar`。超过 12 的系列会在更高的编码轮次中改变线型/标记/纹理。`use_hatch=True` 可对柱图启用纹理，适用于灰度输出。

## 4. 论文作图规则

1. 折线、扫描：颜色 + 线型 + 点形，点过密时只画部分 marker；一维扫描保留准确的阈值定义。
2. 观测数据：`ink` 圆点和误差棒，模型线单独用彩色，不能把仿真数据当作实测值。
3. 分箱谱：如实使用 step/stairs；堆叠不改变分量求和、负贡献或统计意义。
4. 二维置信区间：颜色区分数据集，线型区分置信水平；填充 alpha 使用原有 `fills.contour_alpha`。
5. 柱状图：优先 `bar_style.fill_by_series`。默认白色细分隔边，若灰度打印启用 `hatch`，且图例必须同步呈现纹理。
6. 热图与连续量：沿用 viridis/RdBu_r/magma；**不使用离散 12 色板去替代连续色条**。
7. 超过 6 项时重构图例；超过 8 条重叠曲线时建议分组/分面，决不以缩小字号掩盖密度。

## 5. 用于验收的示例

- [previews/Palette_v4.png](previews/Palette_v4.png)（另有 PDF/SVG）：12 色及对应柱色/线型/标记。
- [previews/Figure_Theme_Preview.png](previews/Figure_Theme_Preview.png)（另有 PDF/SVG）：曲线、误差棒、柱状分量、扫描、二维置信区间的统一视觉效果。
- [previews/Extended_12_Series.png](previews/Extended_12_Series.png)（另有 PDF/SVG）：12 条线/多组柱的极限案例，提示必要时使用分面和纹理。

以上图中的数值都是人为构造的样例，仅用于验收配色效果。更换主题必须保持实际输入数组、统计含义和坐标定义不变。

## 6. 仓库内的公共入口

本规范位于 `plotting/paper_theme/`，具体调用与文件归属见 [README.md](README.md)，文件架构见[上级说明](../README.md)。完整字体/坐标轴配置和固定尺寸导出使用 [plot_template.py](plot_template.py)；`theme_styles.py` 专门处理系列身份。v3 对比文件与原始主题构建器保留在用户提供的来源目录，不参与当前主题读取。
