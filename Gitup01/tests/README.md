# tests：用可核对的行为保护计算与接口

[pyproject.toml](../pyproject.toml) 将本目录设为 pytest 测试入口，并将项目根加入导入路径。测试既覆盖物理合同，也覆盖实验装配、资源管理和旧数值兼容。

| 测试组 | 实际检查对象 |
|---|---|
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

---

[上一级](../README.md)
