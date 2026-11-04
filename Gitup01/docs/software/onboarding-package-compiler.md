# Onboarding IR and deterministic package compiler

资料获取由研究人员/AI完成，编译器不阅读论文或判断科学真伪。用户填写模板、AI摘录、混合输入
最终形成同一个 `cevns-onboarding-draft/1` 对象：

```json
{
  "ir_version": "cevns-onboarding-draft/1",
  "acquisition": {"mode": "human", "evidence_claims": []},
  "requested_capabilities": ["signal"],
  "document": {"说明": "完整正式机器文档，参数只维护在这里"}
}
```

`document` 包含身份/状态、来源/证据定位、参数角色/单位/consumer、模型公式/变量/输入输出/依赖、
资源轴/shape/dtype/归一化、assembly、能力/阻断和人工状态。获取模式只记录来源方式，不改变编译规则。
可编译的无科学主张示例为 [synthetic fixture](../../tests/helpers/onboarding_drafts.py)；
它的 specification_only profile 不提供 Runtime 执行。

[package_compiler.py](../../cevns_pyeft/experiments/package_compiler.py) 接受该 IR 与显式数组映射：
校验→保留精度→受控派生核验→拒绝stale→固定ZIP顺序/时间→哈希→YAML→Physics MD。
只有输出的 YAML/NPZ 是运行输入；Physics MD 随包交付人工评审，IR和台账不是Runtime依赖。
任一人工科学决定必须回填IR，不直接手改MD数值。

```powershell
python -B tools/compile_experiment_package.py --draft draft.json --arrays declared.npz --output package --report validation.json
python -B tools/compile_experiment_package.py --draft draft.json --arrays declared.npz --output package --check
```

默认create-only；`--overwrite`明确保存三份原文件到compiler-backup目录后写入，`--check`不写入。
项目 canonical `data/experiments/` 下的覆盖恢复点保存在 `backup/package_compiler/` 并登记清单，
不混入活动 data 或 sdist；其他显式输出目录仍在其内保存 compiler-backup。
物化数组上游改变必须先显式重建数组，compiler不会仅刷新fingerprint使旧数组变成有效。
缺失值/冲突保留为DRAFT和capability blocker，不填零、不授予RELEASED或人工批准。

CsI2021 v1为已有详细合同，兼容编译。跨实验使用
[v2 Schema](../../cevns_pyeft/experiments/generic_input.schema.json)：不要求CsI靶、SNS、9箱或固定17模型。
[component_bindings.json](../../cevns_pyeft/experiments/component_bindings.json) 是代码维护的允许合同与公式标识，
无任意import或eval。新增模型先注册并验证；SPECIFICATION_ONLY可供研究，但不能被Runtime执行。
当前新profile在完成实跑前均为BOUND_UNVERIFIED，不因compiler PASS升级。

已迁移的 Ar2020/CsI2017 也使用这个编译器。其 legacy acquisition adapter 只负责从
迁移前实现取得 IR，不把实验值写入通用生成器。可执行 profile 的 nested assembly 字段、
参数/资源引用和单位、模型集合及状态均受闭合合同检查；未知字段不能静默忽略。
正式三文件、旧近似预测/统计、Fast、独立安装与科学限制见
[Task10 报告](../PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md)。

流程顺序：scope→source register→evidence→单位/坐标/归一化→模型→缺失/冲突→三文件草稿→
人工Physics Review→机器验证/科学决定分别登记→Loader。机器正确打包不证明科学结论。

[报告](../GENERAL_ONBOARDING_GENERATOR_REPORT.md) · [输入合同](experiment-input-package.md)
