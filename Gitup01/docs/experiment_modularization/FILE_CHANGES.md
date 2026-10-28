# 逐文件变更与恢复

相对路径均以 Gitup01 为根。无删除；现有数据目录和旧参考未移动、未覆盖。

| 动作 | 路径 | 用途 |
|---|---|---|
| modify | `README.md` | 增加统一实验入口和外置资源/能力文档链接 |
| create | `docs/experiment_modularization/CAPABILITY_MATRIX.md` | 参数归属、能力、用法、操作说明或实际解析记录 |
| create | `docs/experiment_modularization/PARAMETER_OWNERSHIP.md` | 参数归属、能力、用法、操作说明或实际解析记录 |
| create | `docs/experiment_modularization/SKILL_OPERATION_GUIDE.md` | 参数归属、能力、用法、操作说明或实际解析记录 |
| create | `docs/experiment_modularization/USAGE.md` | 参数归属、能力、用法、操作说明或实际解析记录 |
| create | `docs/experiment_modularization/analysis_selection.example.yaml` | 参数归属、能力、用法、操作说明或实际解析记录 |
| create | `docs/experiment_modularization/resolved_experiments.json` | 参数归属、能力、用法、操作说明或实际解析记录 |
| create | `examples/experiment_modularization/run_experiments.py` | 可运行的用户示例或synthetic扩展示例 |
| create | `examples/experiment_modularization/synthetic_dataset.py` | 可运行的用户示例或synthetic扩展示例 |
| modify | `src/cevns_pyeft/detectors/csi2021.py` | 参数化CsI响应对象，describe与density读取相同实例参数 |
| modify | `src/cevns_pyeft/experiments/__init__.py` | 惰性兼容导出，保留旧公开导入名 |
| create | `src/cevns_pyeft/experiments/catalog.py` | 四项惰性目录、公开扩展注册、别名与冲突校验 |
| modify | `src/cevns_pyeft/experiments/coherent/__init__.py` | 惰性兼容导出，保留旧公开导入名 |
| create | `src/cevns_pyeft/experiments/coherent/ar2020_definition.py` | Ar2020十二箱分析：源、24kg、sigma(observed)、效率与近似统计权威 |
| create | `src/cevns_pyeft/experiments/coherent/csi2017_definition.py` | CsI2017二十五箱分析：历史质量、映射/Jacobian/效率与统计资源权威 |
| modify | `src/cevns_pyeft/experiments/coherent/csi2021.py` | 旧工厂从CsI2021权威定义组装，保留参数名及有效默认值 |
| create | `src/cevns_pyeft/experiments/coherent/csi2021_definition.py` | CsI2021九箱分析：源、质量、材料、gamma/效率/接受率及统计权威 |
| create | `src/cevns_pyeft/experiments/coherent/execution.py` | 实验专用执行装配及统一结果适配，消费显式物理设定 |
| modify | `src/cevns_pyeft/experiments/coherent/fast_kernel_ar2020.py` | 保留历史Fast表示和默认数组；接受定义提供的显式设定 |
| modify | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2017.py` | 保留历史Fast表示和默认数组；接受定义提供的显式设定 |
| modify | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py` | 保留历史Fast表示和默认数组；接受定义提供的显式设定 |
| modify | `src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py` | 保留历史返回键与算法；使用对应权威定义的实际物理/数值输入 |
| modify | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py` | 保留历史返回键与算法；使用对应权威定义的实际物理/数值输入 |
| modify | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py` | 保留历史返回键与算法；使用对应权威定义的实际物理/数值输入 |
| modify | `src/cevns_pyeft/experiments/coherent/sns.py` | SNS参数化源及从定义派生的旧数据表/兼容类 |
| create | `src/cevns_pyeft/experiments/coherent/statistics_binding.py` | 定义绑定的COHERENT近似统计；counts/PE转换一次 |
| modify | `src/cevns_pyeft/experiments/conus_plus/__init__.py` | 惰性兼容导出，保留旧公开导入名 |
| create | `src/cevns_pyeft/experiments/conus_plus/definition.py` | 定义/资源/观测/统计/曝光的不可变数据结构；CONUS精确ID的权威参数 |
| modify | `src/cevns_pyeft/experiments/conus_plus/detector_response.py` | CONUS响应、阈值从不可变设定实例求值 |
| create | `src/cevns_pyeft/experiments/conus_plus/execution.py` | 实验专用执行装配及统一结果适配，消费显式物理设定 |
| modify | `src/cevns_pyeft/experiments/conus_plus/fast_kernel.py` | CONUS响应矩阵按实际响应、曝光、分箱及支撑验证与持久化 |
| modify | `src/cevns_pyeft/experiments/conus_plus/slow_counts.py` | CONUS源/曝光/核数/响应/分箱/分区显式消费 |
| modify | `src/cevns_pyeft/experiments/conus_plus/source.py` | CONUS通量实例设置；源表缓存以内容哈希区分 |
| modify | `src/cevns_pyeft/experiments/conus_plus/statistics.py` | 现有CONUS nuisance与箱数从定义派生 |
| create | `src/cevns_pyeft/experiments/definition.py` | 定义/资源/观测/统计/曝光的不可变数据结构；CONUS精确ID的权威参数 |
| create | `src/cevns_pyeft/experiments/loader.py` | 外部资源解析、内容/实现指纹、统一PreparedExperiment |
| create | `src/cevns_pyeft/experiments/runtime.py` | 统一预测/评价/编译/启用列表；身份及观测映射检查 |
| create | `src/cevns_pyeft/experiments/selection.py` | 有限选择配置及严格字段/别名/数值检查 |
| modify | `src/cevns_pyeft/kernels/builder.py` | 旧Fast接受显式源通量/每核质量；矩阵公式保留 |
| modify | `src/cevns_pyeft/rates/counts.py` | 每核质量显式输入；默认值与旧计算保持一致 |
| modify | `src/cevns_pyeft/rates/differential.py` | 参数化CsI淬灭/gamma响应，保留旧默认包装和截面公式 |
| modify | `src/cevns_pyeft/sources/sns.py` | SNS参数化源及从定义派生的旧数据表/兼容类 |
| modify | `src/cevns_pyeft/statistics/datasets.py` | 旧统计数据常量与归一化不确定度从权威定义派生 |
| modify | `src/cevns_pyeft/statistics/predictors.py` | 旧Fast先核对请求ID、核ID、数组/metadata分箱与目标/源布局 |
| create | `tests/test_experiment_modularization.py` | 真实行为验收：独立实验、切换、覆写、身份、启停、缓存、资源和synthetic扩展 |
| create | `tools/_modularization_edit.py` | 本次冻结/核验/发行的可复现工具；不作为runtime导入 |
| create | `tools/build_modularization_wheel.py` | 本次冻结/核验/发行的可复现工具；不作为runtime导入 |
| create | `tools/capture_modularization_baseline.py` | 本次冻结/核验/发行的可复现工具；不作为runtime导入 |
| create | `tools/verify_conus_statistics_migration.py` | 本次冻结/核验/发行的可复现工具；不作为runtime导入 |
| create | `tools/verify_modularization_baseline.py` | 本次冻结/核验/发行的可复现工具；不作为runtime导入 |
| create | `tools/verify_modularization_release.py` | 本次冻结/核验/发行的可复现工具；不作为runtime导入 |
| create | `tools/verify_unified_fast.py` | 本次冻结/核验/发行的可复现工具；不作为runtime导入 |

新增 `tools/finalize_modularization_report.py`：根据已完成证据刷新最终报告、实际解析记录、文件哈希与收据。

附加文档：本清单、CHANGE_MANIFEST.json、MIGRATION_REPORT.md。

## 恢复

CHANGE_MANIFEST.json 对每个原有修改文件给出 `recovery_backup`、原SHA256与本次SHA256。
恢复时停止正在运行的程序；按记录把该文件备份复制回同一相对路径，再核对原SHA256。
不要按备份目录名猜测版本；同一文件可能有多次中间修订，以manifest中对应M0哈希的条目为准。
新增文件可按create清单逐项移出；不删除数据或旧参考。若只恢复部分文件，依赖关系可能不一致，
应恢复同一阶段相关文件并执行原有tests。backup只用于恢复，不作为实验输入或回归参考。

原项目无.git，本轮未提交、推送、移动Git分支或覆盖用户其他目录。构建生成的egg-info、
本地wheel和验证输出只位于构建/输出区域，不属于实验物理输入。
