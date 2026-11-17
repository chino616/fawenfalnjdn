# 论文通用主题 v4.0

当前全项目新图的公共主题入口。适用于折线、散点/误差棒、阶梯/直方图、堆叠图、一维扫描、二维等高线、热图和多面板。提供 12 个固定系列身份，超过 12 个系列时结合线型、标记和纹理扩展。

来源为用户指定的 `261103Gitup1-CONUS-6/重构/2026-11-15 CEvNS_PAPER_THEME_v4/CEvNS_theme_v4/`。`PAPER_THEME.json`、`theme_styles.py` 和九个预览文件按原文件导入，参数和颜色未重新设计。规范仅调整仓库内的调用方式及预览路径。原始来源目录保留。

## 文件说明

| 文件/类别 | 用途与消费者 |
|---|---|
| [PAPER_THEME_GUIDE.md](PAPER_THEME_GUIDE.md) | 作图前阅读的通用规范与多系列规则 |
| [PAPER_THEME.json](PAPER_THEME.json) | 参数唯一权威：v4 字体、12 色、柱形填充、线型/标记、画布、轴与导出规格 |
| [theme_styles.py](theme_styles.py) | 原方案 `PaperTheme`；返回可传入 `plot`/`bar` 的样式字典 |
| [plot_template.py](plot_template.py) | 读取公共参数，配置 Matplotlib、创建画布、格式化轴及导出；也可执行合成数据示例 |
| `previews/Palette_v4.*` | 原方案的 12 色及线/柱样式预览，PDF/SVG/PNG |
| `previews/Figure_Theme_Preview.*` | 多种图型组合示例，全部是合成数据 |
| `previews/Extended_12_Series.*` | 多系列编码示例，全部是合成数据 |
| [MIGRATION.md](MIGRATION.md) | 文件迁移、旧方案处置、引用归属和实际验证记录 |

原包中的 v3 参考 JSON、v3/v4 对比图和 `build_theme.py` 留在来源目录。该构建器会重写主题文件并生成旧版对比，因此不作为公共主题的生成入口。

## 后续作图的读取约定

> 读取 `plotting/paper_theme/PAPER_THEME_GUIDE.md` 与 `PAPER_THEME.json`，采用 CEvNS-pyEFT v4.0。复用 `theme_styles.py` 和 `plot_template.py`；为同一对象登记稳定的系列 index，并在所有图中保持一致。

不要按每幅图的绘制顺序重新分配身份。`PaperTheme.line_style(index)` 给曲线使用，`bar_style(index)` 给柱形使用；连续热图采用 JSON 指定的连续色图。

## Python 调用

在仓库根目录运行，或把仓库根加入 Python 模块搜索路径：

```python
from plotting.paper_theme.plot_template import (
    load_theme, configure, new_figure, style_axis, export,
)

theme = load_theme()  # 从模块位置读取同目录 JSON，不依赖当前工作目录
configure(theme)
fig, (ax,) = new_figure("single_column", theme)
ax.plot(x, y, markevery=10, **theme.line_style(0, label="Model A"))
ax.set(xlabel="Energy [keV]", ylabel="Rate [a.u.]")
ax.set_title("(a) Spectrum", loc="left")
style_axis(ax, theme)
ax.legend(frameon=False)
export(fig, "new_output/Figure_Spectrum", theme)
```

依赖 Python、NumPy 和 Matplotlib；不依赖 CEvNS 运行时。直接验证模板：

```powershell
python -B plotting/paper_theme/plot_template.py --output-dir outputs/paper_theme_demo_NEW
```

该命令使用合成曲线和分箱数据，输出 `Theme_Template.pdf/.svg/.png`。使用新目录；遇到同名图件即拒绝覆盖。正式研究图应另外保存绘图数组、英文图注、主题版本及 SHA256。

## 当前与历史入口

公共主题只在此维护。`论文图NoteBook/generate_csi2021_flavor_components.py` 已切换为默认读取此 JSON，并采用 v4 填充色；新运行输出到新的 v4 图目录。编号 9–13 等已发布图集的样式、图件和科学数据保留历史身份；其旧生成器用于原样复现，不自动变成 v4 图。以后重画这些图时按本公共入口接入。

[色板 PNG](previews/Palette_v4.png) · [多图型 PNG](previews/Figure_Theme_Preview.png) · [12 系列 PNG](previews/Extended_12_Series.png) · [文件架构](../README.md) · [论文图目录](../../论文图NoteBook/README.md)
