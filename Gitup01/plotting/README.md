# 公共绘图资源与文件架构

本目录管理跨实验、跨图型共用的绘图主题。当前唯一的新图主题是 [paper_theme/](paper_theme/README.md) 中的 **CEvNS-pyEFT v4.0**，直接采用用户提供的方案。后续绘图先读[主题规范](paper_theme/PAPER_THEME_GUIDE.md)，再读取[参数 JSON](paper_theme/PAPER_THEME.json)。

## 在项目中的位置

```text
Gitup01/
├─ plotting/                         跨实验共用的视觉规范和调用入口
│  ├─ README.md                      本文件：职责、文件架构与导航
│  └─ paper_theme/
│     ├─ README.md                   版本、来源、文件说明与调用方式
│     ├─ PAPER_THEME_GUIDE.md         v4 通用绘图规范
│     ├─ PAPER_THEME.json             唯一权威主题参数
│     ├─ theme_styles.py              原方案的多系列线/柱样式接口
│     ├─ plot_template.py             完整主题配置、轴格式化、导出及最小示例
│     ├─ MIGRATION.md                 旧入口移除、引用更新与验证记录
│     └─ previews/
│        ├─ Palette_v4.pdf/.svg/.png
│        ├─ Figure_Theme_Preview.pdf/.svg/.png
│        └─ Extended_12_Series.pdf/.svg/.png
├─ 论文图NoteBook/
│  ├─ generate_*.py                   具体研究图生成器
│  └─ <图集或新运行>/                 图件、数值、图注、主题快照和来源记录
├─ examples/                         具体分析和历史图集的运行/发布脚本
├─ outputs/                          数值运行结果或独立绘图验证输出
├─ cevns_pyeft/                      物理、预测、探测器及统计实现
├─ README.md                         项目导航与目录职责
└─ AGENTS.md                         后续执行者使用公共主题的约定
```

## 为什么独立放置

主题由多个实验和图型共享，需要稳定路径，不随编号图集、论文案例或运行日期变化。`plotting/` 保存视觉规则，`论文图NoteBook/` 保存具体研究作图，`outputs/` 保存运行产物。主题由绘图消费者显式读取，物理计算包不导入本目录。

`paper_theme` 使用稳定目录名，版本由 JSON 的 `version` 和来源记录标识。不要为每个实验复制一套可修改的公共主题。各运行可保存采用参数的只读快照用于复现，快照不成为新主题入口。

## 后续新增文件

| 内容 | 归属 |
|---|---|
| 全文共用的字体、色板、线宽、图例与导出参数 | `paper_theme/PAPER_THEME.json`，同步其规范 |
| 主题接口或通用最小示例 | `paper_theme/`，由该目录 README 说明 |
| 某个实验或物理量的具体绘图代码 | `论文图NoteBook/` 或对应 `examples/` 分析目录 |
| 正式图件、绘图数组、图注与输入/主题快照 | 新的图集或运行目录，由该目录 README 说明 |

旧图集中的 `STYLE.json`、旧模块与色板只说明历史输出。新图采用公共 v4，历史原样复现显式选择对应历史生成器和快照。当前接入状态见[迁移记录](paper_theme/MIGRATION.md)。

[项目总览](../README.md) · [论文图与生成器](../论文图NoteBook/README.md)
