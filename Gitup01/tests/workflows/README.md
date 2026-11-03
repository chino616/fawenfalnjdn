# tests/workflows：结构与阶段交接测试

[test_workflow_structure.py](test_workflow_structure.py) 验证 catalog、路由、引用、
phase 映射、调用循环和保护清单。
[test_phase_contracts.py](test_phase_contracts.py) 验证阶段记录与产物交接：
响应密度/概率区分、选择不重复、Fast 状态限制、Slow 冻结引用、
统计所需 covariance、excess/Poisson 拒绝、可选能力与部分交付、候选不自批、
记录哈希变化与路径越界。另检验共享阶段参考的未知源码 symbol 能被审计发现。

[test_document_lifecycle.py](test_document_lifecycle.py) 检验删除文件后链接失效、重命名后 README 同步、指定文档的检查范围、越界路径拒绝，以及扫描前排除 backup/outputs/缓存；验证检查器不会自动改写 README。

[test_readme_maintenance.py](test_readme_maintenance.py) 在临时 Git 仓库或文件快照中检验 staged/unstaged/未跟踪变更、改名/删除与子目录范围；另检验目录清单同步、备份、幂等、人工说明保留和标记错误时不写文件。测试提交只属于临时合成仓库，不操作实际项目的 Git 历史。

[test_skill_library.py](test_skill_library.py) 检验 Skill 登记增减、状态/摘要与流程引用变化后的表格过期检测，以及未登记/缺失文件、无效 metadata、路径越界、备份、人工规则保留和幂等；结构检查同时要求用户总表为当前版本。

所有批准、输入和结果都为合成测试值；文件副作用仅位于临时目录。
不导入物理预测包，不创建正式 dataset，不改变真实阶段状态。

## 运行

使用装有 [QA 依赖](../../workflows/cevns-pyeft/qa/requirements.txt) 的 Python：
```powershell
python -B -m unittest discover -s tests/workflows -v
```

新的不变量应测试可观察行为和反例，而不是匹配 Skill 文案。
自然语言场景输入与预期在 workflows/cevns-pyeft/qa/scenarios；
其结构通过不代表实际 agent 行为已经测试。相关边界见 [QA 说明](../../workflows/cevns-pyeft/qa/README.md)。

保护文件的管理仍按 [校验配置说明](../../tools/workflow_validation/README.md)；
不能通过改写冻结数组、放宽容差或删除检查使测试通过。

[上一级](../README.md) · [项目总览](../../README.md)
