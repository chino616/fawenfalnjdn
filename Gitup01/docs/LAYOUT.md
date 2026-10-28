# 当前布局与恢复

| 位置 | 作用 |
|---|---|
| cevns_pyeft/ | 唯一活动运行时源码；保留导入包名 |
| data/ | 外置实验输入、观测schema与溯源 |
| configs/ | 本次分析选择；不执行Python |
| examples/ | 可运行用户例子及明确标记的synthetic扩展 |
| tests/ | 行为/单元/集成检查；helpers保存等值提取的测试参数 |
| docs/ | 当前说明与仍有效物理依据 |
| tools/ | 当前发行和已有CONUS复现/核查工具 |
| schemas/ | 现有契约 |
| workflows/ | 接入流程和科学决策；不进入runtime或wheel |
| outputs/ | 本地结果、诊断和核缓存；不作为隐式实验输入 |

原 `src/cevns_pyeft/` 对应当前 `cevns_pyeft/`。冻结参考、evidence ledger 中的旧路径仍是历史来源，未改写。
没有第二份活动src包。打包只发现 `cevns_pyeft*`；项目外Python -I验证可避免flat布局掩盖发行错误。

阶段性报告、旧状态页、一次性脚本与旧构建目录逐项归档到项目外
`../archives/refactor03_history_20261029.zip`。归档内 REF03_ARCHIVE_MANIFEST.json
给出每个原相对路径的SHA256。先CRC/逐项解压字节核对，才移出原文件。
恢复时先核对zip哈希及条目哈希，再将所需条目解压回其记录位置；保留现有修改，按阶段manifest恢复依赖。
不得把备份或归档重新当作实验数据源。无Git现场仍可从归档、逐文件backup与变更记录恢复。
机器可读的变更/路径映射见 [变更清单](CHANGE_MANIFEST.json)。

`论文图NoteBook/` 和旧科学审查资产仍有研究/绘图用途，保留其内容，不按名称或年代删除。
现行Master工作流、论文依据、原始data、tests/reference均保留；数据迁移只改变明确记录的路径。
tools/conus依赖历史复现输入/输出，见 [工具说明](../tools/README.md)；它们不是新的运行时默认入口。
