# tests：用可核对的行为保护计算与接口

[test_paper2601_joint_minimum.py](test_paper2601_joint_minimum.py)使用具有四个远处精确零卡方解的非负计数模型，回归二维狭长谷漏搜缺陷，并验证不能证明有限搜索域时明确拒绝；不依赖论文图形或修改物理参考值。

<!-- solar-singlebin-v321:start -->

## 太阳⁸B：单 bin独立能力

[test_solar_singlebin.py](test_solar_singlebin.py)验证统计解析式与独立优化器、源/核数、核表截面委托、独立PDF效率、双向文件读取隔离、跨方案统计拒绝、未知尾段严格处理和显式敏感性模式。新18项与原43项核Response/COHERENT回归的实际记录在[本轮QA](../outputs/solar_b8_singlebin/20261111_validation/README.md)。

<!-- solar-singlebin-v321:end -->

<!-- solar-nuclear-v31:start -->

## Solar核Response合同

[test_solar_nuclear_response.py](test_solar_nuclear_response.py)验证真实表读取、p/n绝对收缩、共享逐能量API一致性、SM二次重组、同质量/原核数、端点与非法替代拒绝。

<!-- solar-nuclear-v31:end -->

[test_dataset_package_distribution.py](test_dataset_package_distribution.py)检查三文件所有权/哈希、
export完整性和精确ignore；事务卸载/重装/回滚沿用test_dataset_management。

[test_package_compiler.py](test_package_compiler.py)与[synthetic drafts](helpers/onboarding_drafts.py)
检查跨实验确定性编译、tabulated模型、缺失/冲突保留与写入安全。

[pyproject.toml](../pyproject.toml) 将本目录设为 pytest 测试入口，并将项目根加入导入路径。测试既覆盖物理合同，也覆盖实验装配、资源管理和旧数值兼容。

| 测试组 | 实际检查对象 |
|---|---|
| `test_input_package_schema.py` | 三文件正式格式、参数角色/单位/消费者、重复归一化、派生值、失效指纹、资源与 MD 的成功及负向拒绝；不装配新 Runtime |
| `test_physics_model_registry.py` | 17 个模型真实消费者、受控公式/参数/单位、核响应 NPZ 适配、反中微子标签和探测器中间量扰动 |
| `test_experiment_package_loader.py` | 两文件装配、冻结基线、统计/物理指纹分离、缺省 SM 选择及安全拒绝 |
| `test_package_runtime_migration.py` | 默认 CsI2021 两文件入口、禁止外部响应读取、显式探测器无旧默认值依赖，以及全算符小网格 Slow/Fast/旧格式一致性 |
| `test_li2026_*`、`test_rates_differential_flavor.py`、`test_nuclear_response_convention.py` | 单位、味矩阵、响应收缩、运动学和已知核响应约定 |
| `test_interface_contracts.py`、`test_component_replacement.py`、`test_source_state_p2.py` | 源/态、曝光、材料、响应、替换组件实际被消费 |
| `test_refactor_csi2021_regression.py`、`test_legacy_coherent_scalar_regression.py` | 三实验旧返回语义、分量计数与冻结参考 |
| `test_fast_model_contract.py` | Fast–Slow、算符覆盖、缓存保存加载和失效 |
| `test_experiment_modularization.py`、`test_refactor03_contracts.py`、`test_runtime_migration_contracts.py` | Catalog、selection、资源作用域、身份与迁移工具 |
| `test_experiment_archive_isolation.py`、`test_manifest_and_migration_tools.py`、`test_experiment_specs.py` | 生命周期、活动清单、外置说明与审计 |
| [workflows/](workflows/README.md) | 工作流结构和管理配置，不执行科学预测 |

[helpers/](helpers/README.md) 保存共用输入；[reference/](reference/README.md) 保存修改前数值基线。把二者分开，能区分“如何构造测试点”和“必须保持的输出证据”。

## 运行与管理

从项目根目录运行：

```powershell
python -m pytest -q tests --basetemp=.pytest-tmp/local
python -m pytest -q tests/test_interface_contracts.py
```

每次完整运行可选择独立的 basetemp，pytest 会管理其中的临时文件。报告应记录实际环境、命令、范围和结果；旧 `outputs/` 报告不能证明当前副本已通过。

## 新增测试放哪里

与现有职责相同的回归追加到对应测试文件；新独立行为使用 `tests/test_<主题>.py` 和 `test_*` 函数，便于 pytest 发现。临时资源用 `tmp_path`，可复用输入放 helpers；测试输出不写回原始 `data/` 或冻结 reference。

优先验证可独立判定的量，如解析积分、源缩放、单位、分量闭合、过期缓存拒绝，而非只复述实现。共享物理或内核改动需覆盖 CsI2017、CsI2021、Ar2020；不通过改基线或放宽容差来掩盖变化。小型文档改动以链接、路径和示例检查为主。

## Dataset 完整生命周期测试

[test_dataset_management.py](test_dataset_management.py)在临时管理根检验唯一路径/归属、版本和包哈希、只读计划、陈旧计划、依赖和顶层导入阻断、共享文件保留、README恢复、活动资源、备份损坏和事务回滚。合成单元测试只替换昂贵数值子进程；真实集成测试逐个卸载/重装/反向回滚三个内置dataset，并在新进程比较其余实验的Slow预测与统计。所有拆装发生于隔离副本。

---

[上一级](../README.md)

## 独立截断能标Part

[test_cutoff_scales.py](test_cutoff_scales.py)包含15项解析测试：d=5–8单位/耦合缩放、两岛完整允许集、严格SM分支、无灵敏度、触边拒绝、Gaussian有理式与独立增广最小二乘、事件率必要上界。它只检验[独立分析](../examples/cutoff_scales/README.md)的算法；原生Slow、网格细化和未解决PSD点另见该Part的数值报告，不作为已经闭合的物理验收。

[test_cutoff_joint.py](test_cutoff_joint.py)新增2项：不同扫描尺度转换到共同物理c、总χ²重求极小值和总level搜索域，以及6通道43观测/8个pull的独立块最小二乘。两文件共17项通过；实际24条联合168个验收点另存[联合结果](../outputs/cutoff_scales/20261114_three_group_joint_run1/README.md)。


## CsI2021 三文件审计合同

[test_csi2021_input_package.py](test_csi2021_input_package.py) 检查包/MD/哈希、单位轴、安全读取、外部 cwd 无旧数据回退及物理/统计身份分离；[test_csi2021_package_fast.py](test_csi2021_package_fast.py) 检查完整 22 算符复味矩阵重建与真实依赖失效。数值收敛由 [P07 实际报告](../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md) 提供，接口小网格测试不代替收敛。
# Project package migration acceptance

[test_project_package_migration.py](test_project_package_migration.py) verifies
Ar2020/CsI2017 source and isotope components against frozen arrays, saved Fast
identity, two-file prediction/statistics, parameter consumption, stale source
materialization, strict assembly/units/models and statistical-only cache reuse.
Original reference values and regression tolerances remain unchanged.
Distribution and real uninstall/reinstall tests cover all three active datasets.

`test_package_compiler.py` 还覆盖三实验报告内容选择、q²/q₂ 的显式参数引用、
连续公式编号/内部链接、严格报告元数据、MD-only 和同目录写入/重复覆盖/失败恢复。
Windows fixture 只在一个任务测试根内恢复测试目录继承，不修改正式数据目录或 YAML/NPZ ACL。

ReadyToMerge 报告回归仍在 `test_package_compiler.py`：
检查完整 Source/Target/Detector/folding/statistics、逐箱原始数据、两视图同源、
共享模块仅登记选择、精确 NPZ 引用与摘要失配拒绝。沿用原 Writer 测试，不跑无关物理重提取。

<!-- solar-b8-sm-20261107:start -->

## Solar B8 SM profile

[test_solar_b8_sm_contract.py](test_solar_b8_sm_contract.py)核对零反冲弱荷/单位、运动学端点、味普适性、天然组分、概率归一化、通量线性和PandaX缺失响应不能被提升。

<!-- solar-b8-sm-20261107:end -->

<!-- solar-vector-20261108:start -->

## Solar B8 vector benchmark

[test_solar_b8_vector_contract.py](test_solar_b8_vector_contract.py)验证g=0、g⁴纯NP标度、重质量退耦、干涉符号与抵消、弱荷零点、味普适性、运动学端点和组件物理指纹。

<!-- solar-vector-20261108:end -->

<!-- pandax-simplified-20261110:start -->

## PandaX US2：简化映射合同

[test_solar_mean_map.py](test_solar_mean_map.py)独立核对解析变量变换、非单调/域外输入拒绝、通量线性、全T域分区、分量闭合及原包/简化分支身份隔离；配合既有[test_solar_b8_sm_contract.py](test_solar_b8_sm_contract.py)共10项通过。

<!-- pandax-simplified-20261110:end -->

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

test_solar_nsi.py核验原生径向/本征向量传播、共享截面API、状态参数绑定、Slow/Fast/统计与缓存拒绝。

[完整新onboarding：实际输入、标准引文、物理与程序](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<../data/benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->

<!-- solar-snudd-v34:start -->

## 太阳传播可选扩展：SNuDD v3.4

[已安装并接入主线的新onboarding](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_EXTERNAL_ONBOARDING.v3.4.md>) · [独立安装/API](<../extensions/solar_rho_snudd/README.md>) · [三样本实际对照](<../outputs/external/solar_rho_snudd/20261112_run1/README.md>)。只更换传播源，旧B16-MSW/SM/多bin入口保留；不改变全局默认注册。

<!-- solar-snudd-v34:end -->

<!-- solar-snudd-v341:start -->

## 太阳完整统计：SNuDD v3.4.1

[三样本全流程、联合区域和论文比较](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际结果、图与验收](<../outputs/external/solar_rho_snudd/20261112_fig4_run2/README.md>)。已计算601×601面与各方案联合最小值；2601 Fig.4绿色精确复现未成立，旧结果保留。

[完整推断测试](<test_solar_snudd_inference.py>)核对完整矩阵、Runtime/联合统计、独立pull、各方案最小值、601²面和实际边界。

<!-- solar-snudd-v341:end -->
