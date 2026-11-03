# 当前项目布局

Status: CURRENT
Scope: 当前运行程序、资源、工具和文档的职责。

| 位置 | 作用 |
|---|---|
| cevns_pyeft/ | 唯一活动运行时源码；保留导入包名 |
| data/ | 外置实验输入、观测schema与溯源 |
| configs/ | 本次分析选择；不执行Python |
| examples/ | 可运行用户例子及明确标记的synthetic扩展 |
| tests/ | 行为/单元/集成检查；helpers保存等值提取的测试参数 |
| docs/ | 当前说明与仍有效物理依据 |
| tools/ | 构建、资源管理、文档检查与脚手架工具 |
| workflows/_shared/ | [共同输入规范](../../workflows/_shared/INPUT_STANDARD.md)、实验输入与工作记录格式、模板及审核规则 |
| workflows/ | 接入流程和科学决策；不进入runtime或wheel |
| outputs/ | 本地结果、诊断和核缓存；不作为隐式实验输入 |

原 `src/cevns_pyeft/` 对应当前 `cevns_pyeft/`。冻结参考、evidence ledger 中的旧路径仍是历史来源，未改写。
没有第二份活动src包。打包只发现 `cevns_pyeft*`；项目外Python -I验证可避免flat布局掩盖发行错误。

`论文图NoteBook/` 保存论文绘图与研究材料；`tests/reference/` 保存冻结参考。它们与运行时源码、生成产物各有用途。

文档分为 user-guide、physics、software、experiments 四类；实验资料集中在 COHERENT 下，主导航为 [docs/README](../README.md)。
