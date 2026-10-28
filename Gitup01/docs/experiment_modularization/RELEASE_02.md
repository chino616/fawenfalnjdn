# 重构-02：独立实验定义与统一运行接口

编号：**Refactor-02 / 重构-02**。日期：2026-10-29（Asia/Shanghai）。
分支：`refactor/02-experiment-modularization-20261029`。
父提交：`d7182a116353faf0ba5ba581338db1d2a4b63074`（上一轮接口重构）。

本次按 M0–M7 方案，将 CsI2021、CsI2017、Ar2020 和既有精确 CONUS+ 候选分别绑定到
权威定义；统一 load_experiment / predict_experiment / evaluate_experiment。
选择配置以 enabled 增减本次数据集，禁用项不解析资源。旧 Fast 请求必须匹配核的实验身份、
分箱和源/目标布局。各实验保留原数值策略与实际 Fast 表示。

本地核验：全套222项通过，最终补测后去重223项通过；634个独立基线数组回归无差异；
wheel隔离安装、项目外cwd四实验调用、参数替换及 synthetic 扩展示例通过。
这不是 GitHub CI 运行结果，也不是新增物理积分收敛或官方似然结论。

CONUS+默认三探测器合计357kg·day仅作forward prediction；19箱数字化Gaussian统计
属于独立effective119 C3类配置，需显式曝光(0,119,0)和观测CSV。缺统计输入不阻断预测。

上传范围沿用用户授权：源码、测试、源码例子/核验工具及重构文档。
保留父提交已有内容，不新增本地实验数据、论文、Notebook、outputs、backup、编译核或wheel。
完整测试需要自行准备外部data；本地报告中的outputs路径仅是证据位置，未上传其内容。
实验选择YAML属于重构配置文档；实际解析JSON与变更清单属于重构溯源文档。
迁移报告的“未推送”描述的是工程实施阶段，本文件记录随后发生的编号发布。

- [使用说明](USAGE.md)
- [参数归属](PARAMETER_OWNERSHIP.md)
- [能力矩阵](CAPABILITY_MATRIX.md)
- [迁移报告](MIGRATION_REPORT.md)
- [启停配置](analysis_selection.example.yaml)
- [实施方案](../../../重构/261028_CODEX_EXPERIMENT_MODULARIZATION_PLAN.md)

Git文本统一保存为LF换行；本地源码、验证报告与报告内哈希保留原Windows快照语义。
发布仅规范化CRLF，不改变代码内容；跨环境物理缓存应按实际依赖重新校验。
