# physics：计算约定、单位与科学审核边界

本目录把现有代码中的物理合同与依据说明连接起来。它不执行计算，也不因为写下公式就改变 runtime。

| 入口 | 对应代码及目前含义 |
|---|---|
| [physical-conventions.md](physical-conventions.md) | 当前物理约定和审核入口索引 |
| [PHYSICS_CORE_STEP1.md](PHYSICS_CORE_STEP1.md) | `core.interaction_point.evaluate_li2026_point` 的无源/无探测器单点合同：GeV/keV 输入、cm²/keV 输出、rho 和质量约定 |
| [interaction-theory/legacy_operator_coverage.md](interaction-theory/legacy_operator_coverage.md) | 旧算符覆盖；MIGRATED_NOT_VALIDATED/DEFERRED 仍是能力边界 |
| [nuclear-responses/nuclear_response_convention_audit.md](nuclear-responses/nuclear_response_convention_audit.md) | `ResponseDB/W_np/W_iso` 的内部约定与未完成的外部源表验证 |
| [physics-audits/antineutrino_sign_helicity_audit.md](physics-audits/antineutrino_sign_helicity_audit.md) | 当前 nu/antinu 共享核行为及尚待逐算符核实的符号/螺旋度问题 |

## 为什么与实现分开

单元测试能检查单位、形状、基变换和回归，却不自动证明核表来源或每个算符的科学约定正确。代码、内部验证、外部证据需要分别指明，才能解释一个 PASS 究竟证明了什么。

## 管理与新增文件

新的理论/算符说明放 `interaction-theory/`，核响应来源与约定放 `nuclear-responses/`，跨模块科学问题放 `physics-audits/`。独立的公共物理合同可在本层建立 Markdown 并加入索引。

写明输入输出单位、轴/味顺序、运动学支撑、归一化、对应函数、来源和检查范围。未解决问题标 REVIEW，保留缺失证据；完成科学修正时同时修改权威代码并补必要回归，不能只改文档状态。引用历史步骤中的“本任务”时，应按原文范围理解，不把它当作每次运行都必须执行的程序步骤。

---

[上一级](../README.md) · [项目总览](../../README.md)
