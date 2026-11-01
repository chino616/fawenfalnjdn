# CONUS 归档后版本的验证

本地完整资源环境验证日期：2026-11-01（Asia/Shanghai）。发布日期：2026-11-02。
当前内置实验：CsI2021、CsI2017、Ar2020。

- 完整测试：173 passed，0 failed，0 errors，0 skipped，327.465 秒。
- 三实验计数数组与归档前逐值一致，χ² 完全一致。
- wheel 的 104 个 Python 文件与源码、隔离安装逐字节一致；三个实验均通过项目外 cwd、Python -I 预测。
- 实验切换、selection、synthetic 示例通过。
- 发布前核对全部 163 个最终测试输入文件哈希，内容未改变。

环境：Python 3.11.15、NumPy 2.4.6、SciPy 1.17.1、pytest 9.1.1。
这是本地验收结果；GitHub CI 未执行。

CONUS-Backup、测试日志和移动清单保存在本地，未随本分支上传。
本次仍按既有发布规则，仅新增源码、测试、配置/契约、文档和工作流文本；
不新增本地实验数值表、论文、Notebook、数值输出、备份、ZIP、wheel 或核缓存。
父提交中的非 CONUS 数据和历史记录保留；CONUS 专属旧路径从本分支移除。

完整预测及全测需要与 data/resource_manifest.json 匹配的外部 data 根。
发布副本另做 173 项测试收集、源码/测试字节核对和三实验外置资源预测检查。
