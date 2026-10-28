# 四实验模块化迁移报告

完成核验日期：2026-10-29（Asia/Shanghai，按客户端日期）。
目标项目：`F:\Work\2026-07-15 CEvNSpyEFT-Local\261028Gitup1-CONUS-3\Gitup01`。
方案：`../重构/261028_CODEX_EXPERIMENT_MODULARIZATION_PLAN.md`。
这是工程模块化与数值复现记录，未新增科学结论或提升正式 Physics Gate。

## 版本和环境

目标项目无 `.git`，本轮在原项目原地编辑，未新建项目副本或工作树，未提交/推送。
审查提交为 d7182a116353faf0ba5ba581338db1d2a4b63074。
M0 与该提交比较：93个runtime源码文件字节相同；5个缺失项只是本地egg-info构建元数据。
实际旧基线以M0代码/资源SHA256为准，不把远程提交替代现场状态。

执行环境：Python 3.11.15、NumPy 2.4.6、SciPy 1.17.1、pytest 9.1.1。
解释器：`F:\Work\.codex_conda_envs\codex-py311\python.exe`。
未安装/升级用户环境依赖，wheel使用本地隔离target。

## M0–M7结果

| 工作包 | 结果 |
|---|---|
| M0 | 四实验改造前Slow、既有Fast、raw诊断和资源/代码哈希单独冻结；SM/合法NP/复系数多味点；每项两组有效数值设置 |
| M1 | 旧Fast统计先检查请求ID、核ID、metadata/array分箱、源与目标布局；未知ID和未消费kwargs拒绝 |
| M2 | 不可变ExperimentDefinition、PreparedExperiment、ExperimentPrediction；惰性catalog；显式ResourceCatalog |
| M3 | CsI2021运行/质量/材料/响应/效率/接受率/分箱/近似统计集中，旧工厂与兼容出口派生 |
| M4 | CsI2017与Ar2020实际计算与旧Fast消费显式设定，保留各自算法、质量/响应/网格约定 |
| M5 | 精确CONUS+候选ID，显式源表/通量、Ge73核数、MassTimeExposure、响应、分箱；有名探测器；原响应矩阵表示 |
| M6 | 严格选择配置/别名/数值键，禁用项无资源读取；资源实例隔离；synthetic数据集经公开注册和公共算法与解析结果核对 |
| M7 | 原测试与新增行为验收，wheel外部cwd四实验调用，用户例子、参数归属、能力/限制、变更和恢复清单 |

四实验均达到定义集中、统一加载、实际输入消费、原有预测能力接入与启停验证。
CsI2017/Ar2020的Fast保留legacy_compat，不宣称升级成CsI2021编译器。
CONUS+的Fast只加速响应折叠，不宣称完整EFT系数核已构建。

## 数值与测试

M0原测试：187 passed，446.44 s；原有精确相等断言与容差未改变。
最终全套：**222 passed**，0 failures、0 errors。
最后新增的确切源表路径用例计入补测；按各用例最近结果去重，共 **223个用例通过**。
最后资源路径增强另有 `conus_resources_final.xml`（22 passed）及
`final_physical_checks.xml`（4 passed）定向核验；这些数量有重叠，不能相加作为总用例数。
完整各轮结果见 `outputs/experiment_modularization/test_summary.json`。

独立旧基线634个数值数组（原Slow/legacy Fast核及诊断逐项对比）：

| 实验 | 数组数 | 最大绝对差 | 最大相对差 |
|---|---|---|---|
| CsI2021 | 168 | 0 | 0 |
| CsI2017 | 174 | 0 | 0 |
| Ar2020 | 150 | 0 | 0 |
| CONUS | 142 | 0 | 0 |

统一入口Slow/统计与旧基线核对；CONUS+还核对逐探测器/分量/能区/箱与合计。
公共Fast另有18组对比：
CsI2021相对原Slow最大绝对差1.137e-13 events、相对差1.256e-15；
CsI2017相对旧Fast最大绝对差7.106e-15、相对差4.951e-16；
Ar2020相对旧Fast最大绝对差1.421e-14、相对差4.461e-16。
使用rtol=1e-10、atol_events=1e-12；核阵列不套用事件数atol。
最后一次完整基线重跑的前三个实验均完成比较；到CONUS阶段时，运行期间更新的资源路径接口
与进程已导入旧模块混用而报TypeError。未改变任何数值判据；全新进程执行
`verify_modularization_baseline.py --only-conus`，142个数组及其统一Slow/Fast结果核验通过，
独立写入conus_final_baseline_comparison.json。
初轮新增验收的两项失败（旧核metadata/array分箱不一致未拒绝、CONUS观测路径缺失）
已分别补齐校验和显式外部资源指定，最终均通过。
旧CsI2021 Fast转换常数与新接口原有差异仍分别保护，未混称同一算法。

审查者Python3.12环境中报告的约4.25e-16位级差异，在当前环境原测试中未复现；
本次没有放宽其assert_array_equal。
24个原测试/参考文件与审查提交校验未变；37个M0登记的数据资源未变。

## 必须保留的边界

1. CsI2017 Slow固定251个PE点，历史n_er/n_pe_bin/pe_step无效；新入口明确拒绝。
   其Fast n_er有效，保留自身分箱选点规则，因此不能把粗网格Slow/Fast差异说成接口误差。
2. Ar2020保留sigma依赖观测值、原效率列和历史观测单位；本轮不重新解释其物理单位。
3. CONUS+默认C2/C3/C5各119kg·day，合计357kg·day，是forward prediction。
   现有19点digitized统计属于独立effective119 C3类配置，不能用于默认合计或复制给三个探测器。
   评价需显式设曝光(0,119,0)并提供正确观测资源；只使用一次combined_prediction。
4. 默认data路径缺CONUS观测CSV。既有文件位于
   `outputs/conus-plus-completion-20261012/statistics/approximate_paper_benchmark/observations_digitized_approx.csv`；
   通过ResourceCatalog overrides显式指定，不自动扫描workflow或把历史输出当新输入。
5. M0当时未绑定CONUS统计，找到资源后进行了补充旧代码比较：先验证原统计代码与M0哈希一致，
   再在改造前冻结的C3计数上执行原代码；2网格×3点的6次chi²差值均为0。
   这是可审计的补充核验，不冒称变更前已捕获该统计运行。
6. 数值小网格用于工程回归，不建立物理积分收敛或官方likelihood结论。
7. 不实现联合chi²、ROOT时间模板、新真实实验、天然Ge替换或其他未授权物理假设。
8. 相同箱数不等于相同观测。单位、箱边界、探测器身份或分析版本变化会检查统计映射。

## 发行与使用

wheel SHA256：`88c58e71d57101d0b3f2132e3f2cea8b233562642cd26d4d1b63879d33721300`。
`release/outside_cwd.json`证实隔离安装的wheel从项目外cwd用显式外部资源计算四实验。
安装路径在本任务outputs中，未改用户Python环境。外置数据不打入wheel。
单实验/切换/启停/参数替换与synthetic例子均已实际运行，日志在release目录。
说明入口：USAGE.md、PARAMETER_OWNERSHIP.md、CAPABILITY_MATRIX.md、
analysis_selection.example.yaml、resolved_experiments.json、SKILL_OPERATION_GUIDE.md。

## 变更与恢复

精确清单见FILE_CHANGES.md、CHANGE_MANIFEST.json；所有原有修改文件有按M0哈希绑定的备份路径。
无删除、无数据搬迁、无原参考更新。backup只用于恢复，不作为物理或回归输入。
恢复时按manifest复制相应文件，核对SHA256，再执行原测试；不要混用中间修订。
本轮完成本地工程任务，未改变已有GitHub分支内容，未修改workflow正式Gate或已安装Skill。
