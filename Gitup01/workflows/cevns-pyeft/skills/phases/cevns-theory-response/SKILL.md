---
name: cevns-theory-response
description: Review P04 theory and nuclear-response applicability for a selected CEvNS scope, including operator coverage, flavor conventions and evidence limits.
---

# P04 — 理论与核响应适用性

从 Master 或 theory-extension 工作流进入。先读
[阶段交接合同](../../../../_shared/references/phase/PHASE_EXECUTION_CONTRACT.md)，
使用 [P04 表单](../../../../_shared/templates/phase/P04_THEORY_RESPONSE_TEMPLATE.md)；
核对实现时读 [代码参考](../../../../_shared/references/phase/P04_NUCLEAR_RESPONSE_CODE_REFERENCE.md)。

## 目标与边界

判断共享理论是否覆盖本次目标，交付可供 P05 使用的系数、匹配、核响应和模型适用域。
本阶段拥有理论约定；P05 拥有可调用截面的运动学、单位和输出合同。
源谱/注量、实际核数和探测器响应分别属于 P03、P02、P06，不写入核响应对象。

## 1. 建立覆盖表

依据目标、靶核和入射态需求，逐项列出：
- Wilson 基底/版本、算符顺序、系数单位、SM 加入方式、复系数与 flavor 轴。
- matching/LEC、LNC/LNV 及干涉约定；只审查目标实际用到的项。
- 每个同位素的 response key、文件版本/哈希、来源、p/n 或 isospin 基底、
  质量与振子长度单位、有效动量域。
- 所需通道：已实现、模型中取零、省略、缺失；给出依据和对结果的影响。
- ν/反ν处理的公式证据；保留标签不等于验证了相互作用差异。
- 完整核响应、SM Helm 或其他模型各自允许的参数域。

将程序内部一致性与外部源表核验分开。未闭合的反中微子或核响应审计限制受影响声明；
不能把所有历史回归作废，也不能把它们作为新目标的外部物理证明。

## 2. 作出复用决定

将当前实际调用链与所需物理逐项对照，给出最小复用/扩展方案。
仅在约定需要新增或改变时，向用户展示候选与影响并取得 Physics Decision。
保留 `APPROVE SHARED THEORY ROUTE` 作为该阶段已有确认入口；有效既有决定直接引用。

完整 nuclear response 后不得再乘 Helm；SM-only 模型不得接受一般 EFT。
缺核素/非零通道不得用邻近核素或 Helm 自动代替。
公共理论扩展记录受影响实验与回归范围，不为每个实验复制一套理论。

## 3. 核查或实现并验证

先复用实际实现；只有接口差异时写薄 adapter，物理定义改变时按扩展范围处理。
针对已声明的范围检查：核素/key/通道、基底变换、系数单位、复数共轭与 flavor 轴、
SM 加入和适用的独立 benchmark。SM 比较必须匹配质量、耦合和形状因子约定。
取零通道和有符号干涉项单独记录；不要求每个干涉项非负。

## 4. 交付与返回

阶段报告的 handoff 包含：
`theory_scope`、`coefficient_convention`、`nuclear_responses`、
`coverage`、`runtime_binding`、`external_evidence_limits`。
不适用的响应输入写明模型及原因，不能留空冒充已核验。

技术检查达到本次约定范围后才记 P04 PASS；展示覆盖表、实际 symbol、数值和未闭合项，
取得当前版本所需的结果接受后返回 Master。若任务只要求只读理论审核，交付该范围的
发现与证据缺口即可，不虚构实施或人工批准。只有后续确需运动学/截面审核或实现时，
P05 才消费此合同；P04 不自行启动或批准 P05，也不扩大科学目标。
