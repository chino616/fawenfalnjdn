# 物理约定与审计入口

Status: CURRENT
Scope: 对既有接口与科学审计的导航，不新增公式、单位约定或物理结论。

- [单点相互作用合同](PHYSICS_CORE_STEP1.md)：现有无源、无探测器接口，对应 [interaction_point.py](../../cevns_pyeft/core/interaction_point.py) 与 [现有测试](../../tests/test_physics_core_step1.py)。
- [核响应约定审计](nuclear-responses/nuclear_response_convention_audit.md)：REVIEW；内部基变换检查不等于外部核响应源表验证完成。
- [反中微子符号与螺旋度审计](physics-audits/antineutrino_sign_helicity_audit.md)：REVIEW；保留现有共享 nu/antinu 路径的科学限制。
- [旧算符覆盖](interaction-theory/legacy_operator_coverage.md)：REFERENCE；MIGRATED_NOT_VALIDATED 和 DEFERRED 保持原意。

理论与核响应的实现权威仍分别在 [theory](../../cevns_pyeft/theory/) 和 [nuclear](../../cevns_pyeft/nuclear/)。本次仅整理这些说明的地址和交叉引用。
