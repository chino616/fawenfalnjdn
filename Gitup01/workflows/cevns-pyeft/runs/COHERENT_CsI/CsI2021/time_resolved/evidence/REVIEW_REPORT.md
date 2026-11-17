# CsI2021 时间分辨 onboarding r2 验收记录

2026-11-06，Asia/Shanghai。逐数据溯源重写、用户补充回填、同源生成及范围内文档验收已完成。科学状态仍为 **r2 DRAFT/PARTIAL**，严格论文benchmark保持BLOCKED。

| 核对项 | 实际结果与证据 |
|---|---|
| 来源与证据 | [7组检查通过](PROVENANCE_CHECKS.json)：28份直接来源文件指纹符合登记，74项采用字段均映射到证据；不据此自动认证全部外部引文 |
| 原始RESPONSE调用 | 真实ResponseDB读取原[data/responses/responses_all.json](../../../../../../../data/responses/responses_all.json)，Cs133/I的16个通道数组与提取NPZ完全一致；y=0、0.1、0.5处计算一致。原JSON未修改 |
| 生成一致性 | `export_physics_docs.py --check`及来源检查通过；详细版、精简版、用户资料和P02均来自同一P00/P01/P03。生成器及输出指纹见[交付清单](ARTIFACT_MANIFEST.json) |
| 编码、链接与目录 | [独立渲染检查](READABILITY_CHECKS.json)覆盖23份受影响文档；四份派生MD为UTF-8无BOM/LF。详细版10章、用户资料7章的目录和返回共17组实际点击通过；链接与锚点逐项计数保存在JSON |
| 公式与目视核对 | 详细版9个真实display-math节点、连续编号1–9、无KaTeX错误。已目视检查目录、核响应及观测表、九条公式、用户资料和窄视口来源栏；样例见[公式2](readability/detailed_formula_2.png)、[公式8](readability/detailed_formula_8.png)、[Detector来源栏](readability/detailed_detector_narrow_sources.png) |
| 窄视口 | 三份报告在720px视口无整页横向溢出；宽表可横向滚动。完整预览与截图归属[readability目录](readability/README.md) |
| 全局工作流 | [77项测试中75项通过、2项失败](workflow-tests-localtemp.log)，无环境错误；工作区TEMP/TMP消除了首次运行的Windows短路径问题 |

公式预览现从rehype-katex实际使用的KaTeX包解析CSS，避免pnpm顶层别名指向不同版本；检查器额外验证编号右对齐。此项只修正验证环境。渲染范围是独立CommonMark/GFM、KaTeX与headless Edge，未认证Codex内部渲染器，也未在本轮重新检查外部网址在线可达性。

两项全局失败分别为`test_complete_pack`与`test_protected_fingerprints`。完整[全局条目](GLOBAL_WORKFLOW_ISSUES.json)记录了该次捕获的196项，其中137项为其他文件的保护指纹差异；链接项主要涉及缺失的历史输出。当前CsI时间目录匹配到的一项来自原样保存的[作者README](../sources/upstream_nuclear/Mu2e_NRET/v2/README.md)：其中`git@github.com:Berkeley-Electroweak-Physics/Elastic.git`被全局检查器当成本地路径。它是SSH仓库地址，原始材料保持未改。本轮选定23份文档的本地链接检查通过。未刷新无关保护指纹以消除全局失败。

| 文件范围 | 所属README及实际消费者 |
|---|---|
| AGENTS、共享溯源/输出规范、来源及证据模板、onboarding Skill | [共享入口](../../../../../../_shared/README.md)与[主项目规则](../../../../../../../AGENTS.md)；同节数值、直接来源、原文核验及适用性规则由相应合同统一拥有 |
| P00–P03、决定、提取/导出/验收脚本 | [本分析入口](../README.md)；记录→生成器→三份阅读文件，检查器回读同一数据链 |
| 核响应切片、ROOT边缘、C/AC/SS、99箱CSV | [data说明](../data/README.md)；提取NPZ供审阅，实际核响应仍调用原JSON |
| 官方附件、常数表和候选作者材料 | [sources说明](../sources/README.md)及其子目录README；主PDF由文献库统一保存，P00登记原始URL、版本和指纹 |
| 详细版、精简版及用户资料 | [阅读目录](../../../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/README.md)与CsI2021父目录导航 |
| 旧诊断、原文定位、检查日志和预览 | [evidence说明](README.md)及legacy_resolution/readability的README；原配置诊断与本稿新参数保持区分 |
| 原候选、r1、r2阅读性修正前快照 | [修订归档](../revisions/README.md)；修改前另外保存backup清单，未初始化Git |

来源身份以[P00](../P00_SOURCE_REGISTER.yaml)为准；逐数据核验以[P01](../P01_EVIDENCE_LEDGER.yaml)为准；当前缺口与交接以[P02](../P02_MISSING_AND_CONFLICTS.md)、[P03](../P03_PHYSICS_CONTRACT.yaml)为准。用户明确选择原表复用后，外部作者生成链待核仅影响作者来源认证，不阻断本次原表调用。

下一轮可复用原RESPONSE并核对nominal Detector输入。逐箱预测还须使用统一的质量、官方效率、源和时间归一化配置；BRN/NIN绝对归一、PE边界的重建标记及论文半径nuisance等价问题继续限制相应benchmark主张。旧数值诊断不能作为新配置已运行的结果。本轮未改生产Runtime、原始核表、参考数组或数值容差。

[来源、记录与生成入口](../README.md) · [阅读文件](../../../../../../../docs/experiments/COHERENT/CsI2021/time_resolved/README.md)
