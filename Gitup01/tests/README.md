# tests：用可核对的行为保护计算与接口

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


## CsI2021 三文件审计合同

[test_csi2021_input_package.py](test_csi2021_input_package.py) 检查包/MD/哈希、单位轴、安全读取、外部 cwd 无旧数据回退及物理/统计身份分离；[test_csi2021_package_fast.py](test_csi2021_package_fast.py) 检查完整 22 算符复味矩阵重建与真实依赖失效。数值收敛由 [P07 实际报告](../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md) 提供，接口小网格测试不代替收敛。
# Project package migration acceptance

[test_project_package_migration.py](test_project_package_migration.py) verifies
Ar2020/CsI2017 source and isotope components against frozen arrays, saved Fast
identity, two-file prediction/statistics, parameter consumption, stale source
materialization, strict assembly/units/models and statistical-only cache reuse.
Original reference values and regression tolerances remain unchanged.
Distribution and real uninstall/reinstall tests cover all three active datasets.
