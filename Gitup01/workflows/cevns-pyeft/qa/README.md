# Workflow QA

工作流 QA 与物理运行包隔离。工具分别验证以下内容：
- validate_skill_pack.py：catalog、路由、phase 映射、引用、过期路径、[Skill 总表](../../../cevns_pyeft/SKILLS.md)一致性和受保护文件指纹；只需标准库。
- audit_references.py：工程模块化文档及共享 phase 参考中的源码 AST 锚点和本地链接；
  检查范围包括 P04–P10，但不能证明调用顺序或物理公式正确。
- [validate_phase_contract.py](validate_phase_contract.py)：JSON Schema 2020-12、
  P04–P10 阶段报告的条件字段、状态组合、可选的产物哈希与 P08 引用的 Slow 冻结。
- tests/workflows：通过合成记录和临时文件检验正常/拒绝行为，不创建真实 dataset 或批准。
- [validate_docs.py](../../../tools/validate_docs.py)：用 `--files` 检查本次受影响 README 和索引的本地链接；按[联动规则](../../_shared/policies/file-lifecycle.md)核对新增说明归属与删除/移动后的旧引用。它不自动改写文档，也不证明每个新文件都有充分说明。
- [readme_maintenance.py](../../../tools/readme_maintenance.py)：维护计划使用真实 Git 差异或文件快照，自动目录区只由显式 sync 更新；测试覆盖本地临时 Git 仓库、快照、清单同步和人工说明保留。
- [update_skill_library.py](../../../tools/update_skill_library.py)：按 catalog 和 WORKFLOW metadata 检查/同步用户 Skill 表，默认只读，显式 `--write` 才备份并更新表格标记区；增减规则在总表页，工具不更新保护基线。

## 环境与命令

阶段合同检查需要 [requirements.txt](requirements.txt) 中的 jsonschema；
它只属于 QA 环境，不加入 cevns_pyeft 的运行依赖。若当前环境缺少它：
```powershell
python -m pip install -r workflows/cevns-pyeft/qa/requirements.txt
```

从项目根目录执行：
```powershell
python -B workflows/cevns-pyeft/qa/validate_skill_pack.py --repo .
python -B workflows/cevns-pyeft/skills/engineering/cevns-physics-modularity/scripts/audit_references.py --repo .
python -B workflows/cevns-pyeft/qa/validate_phase_contract.py --check-schemas
python -B workflows/cevns-pyeft/qa/validate_phase_contract.py workflows/_shared/templates/phase/PHASE_REPORT_TEMPLATE.md
python -B workflows/cevns-pyeft/qa/validate_phase_contract.py workflows/_shared/templates/onboarding/PHYSICS_CONTRACT_TEMPLATE.yaml --kind physics
python -B -m unittest discover -s tests/workflows -v
```

实际阶段报告以唯一 `json phase-result` 块保存机器记录；也可显式提供单独 JSON 记录。
验证实际产物时给 `--artifact-root`，指向原项目或隔离候选根目录。
artifact 路径必须在该根内；不接受绝对路径、越界、backup 或内容哈希变化。
正式 P08 的 Slow 引用还要匹配 P07 PASS、canonical 接受及冻结引用。
这些检查不验证输入总指纹的生成过程、不认证用户回复，也不自动检查公式或科学证据。

新 Physics Contract 用 v4，DRAFT 允许空字段；APPROVED section 必须有非空 fields、
decision_refs 和 evidence_refs。v1–v3 JSON 实例只检查历史结构兼容，不自动升级批准。
原历史 YAML/run 文件不被扫描或改写；需要新记录时由 Master 显式补充并核对版本。

## 场景与实际试用分开

[router cases](../router/scenarios/router-cases.yaml)、
[onboarding](scenarios/onboarding-cases.yaml)、
[Phase 0](scenarios/phase0-cases.yaml)、
[handoffs](scenarios/handoff-cases.yaml)、
[P04–P10 realistic cases](scenarios/phase-cases.yaml)
是输入和预期，不是已发生的行为结果。

独立试用保存原始请求、实际回答、审查结论和未解决项，分开记录。
标明静态结构检查、合成合同测试、真实代码示例执行、独立 agent 试用和人工接受各自覆盖；
只有用户实际审查后才能写 human acceptance，不能把自动审查改名为人工批准。

17 个 Skill 保持 repository-local。catalog 可发现不代表全局安装；
workflow QA 通过不意味着实验接入完成或科学主张获准。
