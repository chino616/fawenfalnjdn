# 公共绘图主题 v4 接入记录

日期：2026-11-15。用户确认的结构是 `Gitup01/plotting/paper_theme/`。本任务导入用户给定 v4，移除之前的全局 v1 入口，并记录文件架构与实际消费者。

## 导入来源与权威关系

直接来源：`../重构/2026-11-15 CEvNS_PAPER_THEME_v4/CEvNS_theme_v4/`（相对于 Gitup01）。原始来源目录保留。

当前唯一的新图参数权威是 [PAPER_THEME.json](PAPER_THEME.json)，`schema=cevns_pyeft_paper_theme/1`、`version=4.0`。JSON、原 `theme_styles.py` 与九个预览文件原样导入；规范仅更新调用示例、预览位置与仓库导航。v3 参考/对比和原 `build_theme.py` 未进入公共目录。

## 文件操作与说明归属

| 操作及原路径 | 新位置或处置 | 所属说明与导航 | 程序绑定/检查 |
|---|---|---|---|
| 来源中的 v4 JSON、规范、样式接口 | `plotting/paper_theme/` | 本目录 README；`plotting/README.md`；根 README | JSON 和样式接口与来源 SHA256 相同；规范只作路径接入 |
| 来源中的三组预览，各 PDF/SVG/PNG | `plotting/paper_theme/previews/` | 本目录 README 的预览类别说明 | 九文件与来源 SHA256 相同 |
| 新增完整配置/示例模板 | `plotting/paper_theme/plot_template.py` | 本目录 README | 默认从模块同目录读 JSON；生成合成数据示例 |
| 删除 `论文图NoteBook/PAPER_THEME_GUIDE.md` | 原活动入口移除 | 论文图目录 README 改指公共 v4 | 删除前恢复副本逐文件 SHA256 核对通过 |
| 删除 `论文图NoteBook/PAPER_THEME.json` | 原活动入口移除 | 论文图目录 README 改指公共 v4 | 旧全局默认路径不再被消费者引用 |
| 修改 `generate_csi2021_flavor_components.py` | 默认主题改为公共 v4；去掉局部旧色板；新输出目录 | 论文图 README、CsI2021 文档、13号历史图 README | 新参数快照；v4 不透明填充与白色分隔；保留数值和误差定义 |
| 更新旧 9号样式说明和 13号图入口 | 明确历史身份，移除通向已删除主题的链接 | 各目录 README / STYLE_GUIDE | 历史图件、参数快照与数据保持对应 |
| 增加新图主题约定 | 根 `AGENTS.md` | 根 README | 后续执行者先读公共主题；不启用实验接入流程 |
| 写入文件架构 | `plotting/README.md`、根 README、`docs/experiments/LATEST_FOLDER_LAYOUT.md` | 各自文档入口 | 主题、具体绘图、运行产物和物理包的职责明确 |
| 新增调用验证产物 | `outputs/paper_theme_v4_integration_20261115/` | 运行 README、outputs README | 模板与 CsI 图件、数据一致性和文档检查 |

旧全局主题和修改前 CsI 生成器的恢复副本保存在 `backup/paper_theme_v4_migration_20261115/`，已退出活动入口。它们可恢复，不参与默认读取或资源发现。

## 当前消费者和历史范围

新图模板及 CsI 味分量生成器已读取公共 v4。既有 SM、一维/二维 benchmark、截断能标等历史发布器仍保留各自当时的数值/排版接口；它们不是公共 v4 的实现，也没有在本任务中批量重画。后续要求更新这些图的风格时，读取公共 v4 接入其绘图层。

历史结果目录中的 `STYLE.json`、主题快照、执行源码及 SHA256 清单按历史版本保留。不能将新主题直接写进旧运行的参数快照，否则会使旧图与来源记录失配。

## 实际验证

- 通用模板已生成 PDF/SVG/PNG；CsI 味分量图已使用公共 v4 在独立目录生成三种格式。
- CsI 生成器的协方差重推、分量求和、9/11 个误差点、文字边界和共享图例检查通过。
- PNG 已目视检查；记录中的额外文件/尺寸/接口核对及文档链接结果见[本轮验证目录](../../outputs/paper_theme_v4_integration_20261115/README.md)。
- 独立核对通过：11 个导入文件 SHA256 一致、12 色/24 种曲线编码、6 个画布布局、格式化不改变坐标范围、同名导出拒绝覆盖；两组 PDF 均为 180 × 85 mm，PNG 均为 300 dpi。
- CsI 两个投影 CSV 和两个输入 NPZ 与历史图目录逐字节相同；只替换绘图主题。
- 仓库文档工具检查本次 12 份活动文档的 228 个本地链接，无失效链接。输出目录由该工具默认排除，另对本轮运行 README 和 outputs 总入口的 55 个链接作定向核对，全部通过。
- 最后一次生成器调用位于 `tmp/paper_theme_v4_final_smoke_20261115/`，其记录的源码 SHA256 与最终脚本一致；CSV 与 PNG 均与本轮展示输出逐字节相同。

[公共主题](README.md) · [绘图文件架构](../README.md)
