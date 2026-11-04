# Skill / 执行合同 / Runtime 问题审计

本次实际读取 Master、P04–P10 Skill、共同执行合同、阶段模板与代码参考；不是只读 README。
主干 DAG 正确：P04→P05；P06 独立依赖观测/靶；P05/P06/源/靶汇入 P07；P08/P09 按所选后端分支；P10 按能力收口。
用户已指定已有 CsI2021 并要求连续执行，因此不重做 intake/onboarding/P01–P03，也不重复请求同一工程授权。

| 归属 | 实际问题及影响 | 本次处理 / 后续最小方案 |
|---|---|---|
| 输入→Runtime 边界 | 初始 Task02 reader 只检查三文件，不绑定实际 typed objects；旧 Loader 成功不证明 package-only | 添加 CsI 局部 allow-list adapter，复用已有 Definition/Model/Source/Interaction/Observation；独立 cwd 阻断旧 definition 与数据回退 |
| 输入版本 | pilot/1 期间上游推进到 input/1，之后绑定/Loader 元数据又更新；MD renderer 两段说明文字改变 | 保存 revision 2/3 原件和哈希；仅精确兼容两种已发布说明文字，模型/参数表差异仍拒绝 |
| 运行一致性 | 长积分结束时 freshness 检查读到上游新 revision，四项计算被正确拒收 | 固定 wheel 01 + revision 2 重跑；没有篡改 identity 或将被拒收计算写为成功 |
| 指纹粒度 | 本次窄 adapter 的 model 投影保守包含模型绑定审计元数据；仅该文字变动也会使物理身份改变 | 作为保守失效记录，不能跨版本自动复用；后续可在有合同测试时把纯审计元数据移出数值投影，不据此修改已有证据 |
| 共享 import | 导入 generic statistics profiler 会拉入旧 dataset；catalog describe 经 detector 默认值拉入核模块 | 两个包的 __init__ 改为延迟导出，失败→修复测试与回归均保留；无物理公式变化 |
| P10 Skill | 持久登记权威旧说法与实现不一致，易把 alias/loader 维护绑上新 scientific gate | 修正为 dataset_registry.json→manifest.py 视图→Catalog；明确既有语义 loader/import/packaging 使用工程 Gate；原科学状态保留 |
| Phase schema | phase-result 可保存规范 handoff，但 scope/fingerprint 与实际 scientific truth 需执行器保证；schema 不能认证批准真实性 | 不扩张 schema、不填假 approval；七份报告逐份结构/文件哈希检查，补齐输入、代码及 reference 依赖 manifest |
| P08 前提 | 正式 Fast 需要当前人工 Slow 冻结，连续工程授权不包含该批准 | full22 工程候选证据单列 PASS，正式 P08 BLOCKED；不要求以此阻断 Slow 统计 |
| 保护 QA | Workflow-only 保护清单与此次获授权的 Runtime 接入/同期迁移不在同一差异范围 | 原样保留保护失败；不改保护哈希“消绿”；结构与科学数值检查分开报告 |
| 测试环境 | tempfile 默认 sandbox Temp 有权限/清理失败，移到 git 仓库内又改变 plain-folder Git 语义 | 使用新建任务临时目录；保留 ENV/cleanup 失败，不能计 PASS；不清理已有 tmp/backup |
| 当前并行迁移 | 旧 external-response API 拒绝、Fast 历史数组不等、卸载依赖回归 | 逐项保存实际失败和版本归属；固定 wheel 的对应保护回归另跑；不覆盖另一任务的大范围实现 |

建议的后续改动只需加强明确的交接：Master 生成 input revision + implementation snapshot，
P07 长计算全程使用固定文件；P10 同时报告该快照和当前工作树，禁止自动升级证据。
输入包本身不要因技术运行通过就把 DRAFT/PARTIAL 或 human NOT_REVIEWED 改为批准。
冻结/approval 的科学决定仍由现有合同负责，无需增加第二套工作流状态机。

## 验证结果的真实范围

| JUnit | 实际通过 | 失败 | 错误 | 状态 |
| --- | --- | --- | --- | --- |
| [baseline_tests.xml](../../../../../outputs/csi2021_package_execution_20261104/baseline_tests.xml) | 28 | 0 | 0 | PASS |
| [adapter_29_green.xml](../../../../../outputs/csi2021_package_execution_20261104/adapter_29_green.xml) | 29 | 0 | 0 | PASS |
| [package_fast_tests.xml](../../../../../outputs/csi2021_package_execution_20261104/package_fast_tests.xml) | 31 | 0 | 0 | PASS |
| [existing_regressions_final.xml](../../../../../outputs/csi2021_package_execution_20261104/existing_regressions_final.xml) | 63 | 0 | 0 | PASS |
| [import_boundary_green.xml](../../../../../outputs/csi2021_package_execution_20261104/import_boundary_green.xml) | 2 | 0 | 0 | PASS |
| [current_adapter_05.xml](../../../../../outputs/csi2021_package_execution_20261104/current_adapter_05.xml) | 62 | 0 | 0 | PASS |
| [regression_matrix_02.xml](../../../../../outputs/csi2021_package_execution_20261104/regression_matrix_02.xml) | 124 | 3 | 0 | FAIL |
| [pinned_regression_01.xml](../../../../../outputs/csi2021_package_execution_20261104/pinned_regression_01.xml) | 7 | 0 | 0 | PASS |
| [workflow_qa_04.xml](../../../../../outputs/csi2021_package_execution_20261104/workflow_qa_04.xml) | 82 | 3 | 0 | FAIL |

各批次有重叠，不能直接相加称为独立测试总数。中间失败 XML 保留供诊断；最终对应成功记录单独引用。
