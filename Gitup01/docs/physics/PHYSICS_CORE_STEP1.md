# 物理抽取第一步：冻结无源、无探测器的相互作用合同

Status: CURRENT
Scope: 既有内容的目录与引用整理；公式、数据、单位和科学结论保持原意。

当前用户任务是整理已有 `cevns_pyeft` 的物理核心，不是接入一个新的实验数据集。因此原有
Master Skill 的 `physics_onboarding → P01` 不是本任务的第一个实现动作。它负责新数据集身份、
材料证据和统计语义；如果直接从它开始写代码，会把现有实验重构误当成新实验接入。

本任务的第一步是一个只针对已有活动代码的 R0 物理基线：

1. 选定一条已经运行的参考链（当前使用 CsI2021 的 Li2026 interaction 路径）。
2. 冻结输入输出单位、flavor 轴、运动学支撑和核质量约定。
3. 把 `source → interaction` 的边界与 `interaction → detector/counts` 的边界分开。
4. 在不复制公式的前提下，用一个小适配器暴露“单个 (E_\nu,T) 点的差分截面”。
5. 用端点、域外零、密度矩阵合法性和质量约定测试这个合同。

## 当前代码的真实 owner

| 物理责任 | 当前实现 | 第一阶段处理 |
|---|---|---|
| 双体运动学 | `cevns_pyeft/theory/kinematics.py` | 复用，不复制公式 |
| Wilson→核子→响应→振幅 | `cevns_pyeft/theory/li2026/` | 复用现有 Li2026 链 |
| 核响应表 | `cevns_pyeft/nuclear/response.py` | 由 `ResponseW` 提供 |
| 差分截面和单位桥 | `cevns_pyeft/rates/differential.py`、`theory/li2026/cross_section.py` | 复用；输出 `cm²/keV` |
| 源/ρ | `cevns_pyeft/sources/state.py` | 只提供密度矩阵，不由核心加载源 |
| 靶质量/核数 | `cevns_pyeft/contracts/target.py`、`targets/materials.py` | 第一阶段只核对质量约定 |
| 探测器、曝光、分箱、统计 | 各自的 `detectors/`、`rates/`、`statistics/` | 明确排除在本步骤之外 |

## 合同

- 入射能：`E_nu_GeV > 0`。
- 真实反冲：公共边界使用 `recoil_keV >= 0`。
- 核响应质量：当前 Li2026 路径固定使用 `m_A = A × AMU_GEV`；传入其它质量必须拒绝。
- 入射态：`rho` 必须是 Hermitian、正半定、trace 为 1 的 `(3,3)` 矩阵。
- 输出：flavor kernel 和 `dσ/dT` 均为 `cm²/keV`，不含通量、核数、质量、时间、效率和分箱。
- 支撑：`T > T_max(Eν)` 返回零，而不是把域外点送入振幅。
- 粒子标签：保留 `nu/antinu` 元数据；当前共享 kernel 仍是 legacy common route，不能宣称独立反中微子符号/螺旋度实现。

核心适配器位于
`cevns_pyeft/core/interaction_point.py`，它只调用现有物理 owner，不复制核响应、匹配或响应多项式。
这一步完成后，下一步才是把源分量和 `rho(E)` 接入同一合同；再之后才进入 detector/Slow。

## 框架路径维护记录

初查发现的旧 src 布局引用在本次 workflow 目录重构中修正。当前静态检查入口是
`workflows/cevns-pyeft/qa/validate_skill_pack.py`，物理模块文档锚点检查入口是
`workflows/cevns-pyeft/skills/engineering/cevns-physics-modularity/scripts/audit_references.py`。
二者只提供结构/引用证据；检查范围见 [工作流 QA 说明](../../workflows/cevns-pyeft/qa/README.md)。
本节仅更新框架路径，上述 R0 物理合同与源码不属于目录重构范围。
