# Refactor-03 发布记录

编号03；日期2026-10-29。基于Refactor-02的bd54dba，分支为refactor/03-layout-data-interfaces-20261029。

## 交付范围

源码从src/cevns_pyeft平铺为cevns_pyeft，保留包名；四个实验的定义、真实组件、观测合同和资源作用域完成整理。
历史阶段脚本退出活动工具目录，测试参数迁入tests/helpers；历史文档转为当前职责名称。
源/截面/响应的实际替换进入计算和物理身份；资源拼写、浅层可变输入、实际装配身份和统计坐标四类缺口修复。

遵循用户既有范围：仅新增源码、测试、源码示例/工具、配置/契约和重构文档。
data/README.md与data/resource_manifest.json是资源说明与路径/哈希清单，不包含新实验数值表。
父提交已有的data、论文、workflow及历史输出保留；本次不新增本地data表、观测CSV、论文、Notebook、
outputs、backup、历史zip、wheel、生成核或其他计算产物。

## 资源与验证边界

本地完整验收为237 passed、0 failed、0 errors、0 skipped，983.00秒。
另有634数组、18项统计比较；最大相对数组差4.70193535432221e-16；最大χ²绝对差7.105427357601002e-15。
189份受保护文件内容未变，139个历史归档条目按哈希验证；项目外wheel及三个示例通过。

VALIDATION.md与CHANGE_MANIFEST.json记录发布前本地验收状态。其outputs、归档、备份和绝对路径是本地溯源，
对应数值产物未随本次提交上传；“未推送”等历史状态指本地验收时刻。
这些记录不代表源码分支自带全部资源，也不代表GitHub CI已经执行。

完整运行/全测需准备与data/resource_manifest.json相符的外部资源根，包含新统计schema、CONUS原观测及原源表。
本分支继承的旧data只是已有资源子集；有限旧路径映射不能代替缺失的统计schema或观测。
公开API可使用ResourceCatalog指定完整外部根。现有测试默认以项目根为资源根，完整全测前需按清单在该位置准备data。
源文件和测试文件与已验收本地快照逐字节核对；发布目录另做测试收集及四实验外部资源预测检查。

CsI2017/Ar2020的legacy Fast仍限制任意替换组件；CONUS仍使用Ge73候选、响应矩阵Fast和effective119近似Gaussian。
没有科学Gate提升，没有新增ROOT时间模板、天然Ge、官方on/off likelihood、联合χ²或新物理过程。
