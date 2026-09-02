# CEvNS-pyEFT Flavor 重构当前完成情况

更新日期：2026-09-02（Asia/Shanghai）

## 1. 结论摘要

当前正确工作树为：

```text
F:\Work\2026-07-15 CEvNSpyEFT-Local\260820Gitup1-Flavor\git-worktree-f0\Gitup01
```

当前 Git 状态：

```text
branch: flavor-refactor-source-state-v4
HEAD:   bb8d2aa
```

总体结论：

```text
核心重构 P0-P2                    已实现并通过当前聚焦测试
CsI workflow Phase 0-6           已完成，Gate R = PASS
CsI workflow Phase 7 Slow        只完成 source-state 接线，Gate L 未通过
CsI workflow Phase 8 Fast        未开始
CsI workflow Phase 9 Statistics  BLOCKED
CsI workflow Phase 10 Validation 未开始
SNuDD 通用能力                    当前核心 rho(E_nu) 已具备
SNuDD adapter                     旧非 Git 副本有可运行原型，正确工作树尚未接入
```

因此，当前项目不能声明为 `FULLY_INTEGRATED`，也不能声明 SNuDD 已经合入当前分支。

## 2. 原始参考文档是否包含 SNuDD

答案是：**包含，但它被安排为后期 propagation backend，而不是 P0-P2 或 CsI Slow 之前必须合入的特殊接口。**

### 2.1 问题处理优先级提示词

原始文件：

```text
F:\Work\2026-07-15 CEvNSpyEFT-Local\260820Gitup1-Flavor\CEvNS-pyEFT Flavor 重构：问题处理优先级提示词.md
```

该文档在 P0 明确要求先构造 Flavor kernel，再执行：

```text
Tr[rho(E_nu) K(E_nu, E_R)]
```

并在第 208 行明确规定，不得把太阳传播、SNuDD 或 source-specific 逻辑写入 amplitude/response 层。

该文档的 P2 要求核心支持：

```text
constant rho:          (3,3)
energy-dependent rho: Enu.shape + (3,3)
```

其目的之一是在未来直接连接：

```text
SNuDD
solar MSW
vacuum propagation
arbitrary coherent source
```

所以 P2 的交付物是 **SNuDD-ready 的 rho(E_nu) 核心合同**，不是必须在 P2 内完成 SNuDD adapter。

### 2.2 完整 Flavor 重构实施规范

原始文件：

```text
F:\Work\2026-07-15 CEvNSpyEFT-Local\260820Gitup1-Flavor\CEvNS_pyeFT_full_flavor_refactor_implementation_spec.md
```

该规范明确把 SNuDD 列入总范围，并规定：

```text
SNuDD 只在最后作为 propagation backend 接入。
```

规范的总体边界是：

```text
SNuDD -> rho_solar(E_nu)
CEvNS-pyEFT -> Flavor detection kernel K(E_nu, E_R)
observable -> Tr[rho_solar(E_nu) K(E_nu, E_R)]
```

SNuDD 不得进入：

- LEFT/nucleon matching；
- nuclear response；
- CEvNS amplitude；
- detector smearing；
- statistics。

规范第 48 节给出了 `SNuDD adapter` 的最终合同，而且明确写明：

```text
只有 Slow/reference flavor core 通过全部测试后，才写 SNuDD adapter。
```

建议目录为：

```text
src/cevns_pyeft/propagation/
    base.py
    density.py
    backends/
        snudd.py
```

规范还要求：

- public energy boundary 必须明确单位；
- SNuDD density 输入使用 GeV；
- SNuDD 输出为 `(N_E,3,3)`；
- Flavor 顺序为 `(e,mu,tau)`；
- 每个能量点检查 Hermitian、`Tr(rho)=1` 和 PSD；
- propagation matching 只能使用 NP part，不能再次加入 SNuDD 已包含的 SM matter potential；
- detection 与 propagation 应来自同一个 canonical Wilson tensor；
- solar Fast 必须处理能量依赖 `rho(E_nu)`，不能把它错误地拆成常量 Flavor factor。

### 2.3 当前实验工作流

`workflows/experiment-integration/EXPERIMENT_WORKFLOW.md` 的固定 Phase 0-10 **没有单独命名一个 SNuDD Phase**。

其含义是：

- Phase 3 Source 是通用 source adapter 阶段；
- Phase 7 必须先完成并验证 Slow；
- Phase 8 只能从已验证 Slow 推导 Fast；
- SNuDD 应在需要 solar propagation 的数据集或独立 propagation backend 工作中接入；
- CsI2017/CsI2021 是 SNS stopped-pion source，不需要 SNuDD solar propagation。

因此，原始 Flavor 总规范包含 SNuDD；后来的通用实验工作流没有把 SNuDD 固定成每个实验都必须执行的阶段。这两者并不矛盾。

## 3. 正确工作树中的 SNuDD 状态

当前正确工作树中没有以下文件或模块：

```text
src/cevns_pyeft/integrations/snudd.py
src/cevns_pyeft/propagation/backends/snudd.py
tests/test_snudd_rho_integration.py
```

当前正确分支也没有生产代码直接 import `snudd`。

所以准确状态是：

```text
SNuDD adapter merged into current branch: NO
SNuDD used by CsI Slow chain:             NO
SNuDD is a required runtime dependency:   NO
Current core accepts SNuDD-style rho(E):  YES
```

## 4. 旧非 Git 副本中的 SNuDD 原型

旧副本位置：

```text
F:\Work\2026-07-15 CEvNSpyEFT-Local\260820Gitup1-Flavor\Gitup01
```

该目录不是当前允许继续修改和提交的工作树，但其中确实存在：

```text
src/cevns_pyeft/integrations/snudd.py
src/cevns_pyeft/integrations/__init__.py
tests/test_snudd_rho_integration.py
docs/SNUDD_RHO_INTEGRATION.md
tools/plot_snudd_rho_cross_section.py
```

旧原型实现了：

- `SnuddDensityProvider.from_checkout(...)`；
- solar 与可选 Earth propagation；
- MeV public input 到 SNuDD GeV input 的一次转换；
- `(e,mu,tau)` Flavor 顺序检查；
- `rho(E_nu)` shape/Hermitian/trace/PSD 检查；
- `Tr(rho K)` 的复数 contraction；
- 直接返回 `rho`、Flavor kernel 和 `dσ/dE_R`；
- SNuDD 作为可选依赖，不在模块 import 时强制加载。

2026-09-02 的只读验证结果：

```text
旧原型 adapter tests: 9 passed
```

本机真实 SNuDD checkout：

```text
F:\Work\SNuDD-main\SNuDD-main
```

实际通过旧 adapter 调用 SNuDD `8B` density 的结果：

```text
E_nu = [5, 6] MeV
rho.shape = (2,3,3)
Tr(rho) = 1（数值虚部约 1e-17 或更小）
minimum eigenvalue = 0.02215484143300197
```

这证明旧原型能够连接真实 SNuDD，但不能证明它已经合入当前分支。

## 5. 当前 `rho` 处理已经完成的部分

### 5.1 Canonical source state

当前实现：

```text
src/cevns_pyeft/sources/state.py
```

包含：

- `ParticleKind = Literal["nu", "antinu"]`；
- immutable `NeutrinoState`；
- 常量 `(3,3)` density matrix；
- `Enu.shape + (3,3)` 能量依赖 density grid；
- constant density 对能量网格广播；
- raw `rho` 必须同时给出 `particle_kind`；
- `NeutrinoState` 与额外 particle label 矛盾时拒绝；
- density matrix 设置为只读，避免积分过程中被修改。

### 5.2 Density matrix validation

当前逐矩阵检查：

- shape 末两维必须为 `(3,3)`；
- real/imag 均为 finite；
- Hermitian；
- `Tr(rho)=1` 且 trace 虚部受控；
- positive semidefinite；
- energy shape 必须与 `Enu` 一致。

### 5.3 Flavor contraction

当前统一 convention：

```text
C[final flavor, initial flavor]
K = C-dagger C
dσ = Tr(rho K)
```

`src/cevns_pyeft/rates/differential.py` 已支持：

```text
rho = NeutrinoState
```

或：

```text
rho = raw constant/energy-dependent density array
particle_kind = explicit label
```

对于 grid，当前实现逐能量验证 kernel，并使用：

```python
np.einsum("...ab,...ba->...", rho, kernel)
```

即明确计算 `Tr(rho K)`，而不是错误的逐元素同指标乘积。

### 5.4 当前 rho 测试

2026-09-02 当前正确工作树验证：

```text
tests/test_source_state_p2.py: 7 passed
```

覆盖：

- SNS 三个 component 的 flavor 与 particle identity；
- constant rho 广播；
- energy-dependent rho grid；
- 逐能量 `Tr(rho K)`；
- SNuDD-style synthetic rho grid；
- SM Flavor universality；
- shape/Hermitian/trace/PSD 错误；
- raw rho 缺少 particle label；
- `nu/antinu` label 矛盾。

注意：测试名中的 `SNuDD-style` 表示输入 shape 和数学合同与 SNuDD 输出兼容，并不 import 或执行 SNuDD。

## 6. CsI 中 rho 的当前数据流

CsI2017/CsI2021 使用 stopped-pion SNS source，而不是 solar propagation。

当前 source mapping：

| SNS component | `particle_kind` | density matrix |
|---|---|---|
| prompt `nu_mu` | `nu` | `rho_mu = |mu><mu|` |
| delayed `nu_e` | `nu` | `rho_e = |e><e|` |
| delayed `antinu_mu` | `antinu` | `rho_mu = |mu><mu|` |

实现入口：

```text
src/cevns_pyeft/experiments/coherent/sns.py::sns_component_state
```

Phase 7 已经把 state 接入：

```text
slow_counts_csi2017.py -> sns_component_state(flv) -> counts.py
slow_counts_csi2021.py -> sns_component_state(flavor) -> counts.py
counts.py -> differential_cross_section_nn(..., rho=source_state)
```

已保留：

- prompt monoenergetic line `29.65 MeV`；
- CsI2017 legacy Slow multiplier `14.6 kg`；
- CsI2021 detector mass `14.57 kg`；
- 三个 source component 分开映射，不把 `all` 当成一种 Flavor state。

但是 Gate L 尚未通过，因此该接线还不能称为已验证 Slow 实现。

## 7. `particle_kind` 的当前限制

当前 `nu/antinu` 已被严格保存为 metadata，但 P2 明确没有改变 antineutrino interaction kernel 的符号或 helicity convention。

当前源码注释也规定：

```text
P2 records the particle label without changing the existing antineutrino
interaction convention; sign/helicity changes require a separate audit.
```

因此：

- `rho_nu_mu` 与 `rho_antinu_mu` 在纯 Flavor 空间可以相同；
- 两者依靠 `particle_kind` 区分；
- 反中微子 vector/axial、parity-odd、LNC/LNV 符号尚需独立物理审计；
- 不得把 `particle_kind` 已存在误解为 antineutrino 物理已经完全验证。

## 8. 项目阶段完成情况

### 8.1 核心优先级

| Priority | 状态 | 结果 |
|---|---|---|
| P0 | PASS | 单位、精确运动学、Wilson strict contract、SM identity、complex coherence |
| P1 | PASS | scale-aware Hermitian/PSD/positivity 与 Cs/I kernel 测试 |
| P2 | PASS | `NeutrinoState`、constant/energy-dependent rho、particle metadata |
| P3 | PARTIAL | CsI Slow source-state 接线已写，Gate L 未验证 |
| P4 | NOT STARTED | Flavor Fast contract 和 Slow/Fast 对比未实现 |
| P5 | NOT STARTED | 完整物理回归与正式 SNuDD backend 尚未完成 |
| P6 | NOT STARTED | `pyc`/generated artifacts 等代码卫生尚未单独处理 |

### 8.2 CsI workflow

| Phase | Gate | CsI2017 | CsI2021 |
|---:|---|---|---|
| 0 Input/Manifest | I | PASS | PASS |
| 1 Dataset | D0 | PASS | PASS |
| 2 Detector/Target | T0 | PASS | PASS |
| 3 Source | S0 | PASS | PASS |
| 4 Theory/Response | T1 | PASS | PASS |
| 5 Kinematics/Cross section | X | PASS | PASS |
| 6 Detector response | R | PASS | PASS |
| 7 Slow counts | L | NOT PASSED | NOT PASSED |
| 8 Fast counts | F | NOT STARTED | NOT STARTED |
| 9 Statistics | Q | BLOCKED | BLOCKED |
| 10 Registry/validation | V | NOT STARTED | NOT STARTED |

当前两个 dataset YAML 仍正确标记：

```text
slow_validated: false
fast_validated: false
statistics_validated: false
```

## 9. 尚未完成的关键工作

### 9.1 CsI Gate L

必须先完成：

- CsI2017/CsI2021 frozen Slow 小网格；
- prompt/delayed component 逐分量结果；
- direct `Tr(rho K)` 独立 reference loop；
- 旧 scalar benchmark 回归；
- shape、单位和逐 bin 数值报告；
- `07_SLOW_COUNTS.md`；
- YAML 更新为 `slow_validated: true`；
- Gate L PASS。

### 9.2 正式 SNuDD backend

如果按原始规范顺序执行，应在 Slow/reference core 全部通过后：

1. 从旧副本提取设计，不直接复制；
2. 将重复的 density validation/contraction 改为复用当前 `sources/state.py` 和 `rates/differential.py`；
3. 按规范放入独立 propagation backend，而不是 amplitude/response；
4. adapter 输出 canonical `NeutrinoState("nu", rho(E_nu))` 或等价严格接口；
5. 明确 MeV/GeV public boundary；
6. 添加 mocked provider tests 与真实 checkout optional test；
7. 增加 SNuDD SM rho(E) Flavor-universality regression；
8. 实现 NP-only Wilson -> propagation NSI matching 前，完成符号与单位审计；
9. 不把 SNuDD 特殊逻辑写入 CsI Slow 或通用 amplitude；
10. solar Fast 另建 energy-resolved Gate。

### 9.3 Fast、Statistics 和最终验证

- Phase 8 Flavor Fast 尚未开始；
- Phase 9 缺少 authoritative statistics provenance；
- Phase 10 registry/full regression 尚未开始；
- 现有旧 Fast arrays 不能静默当成 Flavor-compatible kernel；
- reference arrays 和 tolerance 不得为了通过而修改。

## 10. 推荐继续顺序

```text
保持当前 P0-P2 实现
    -> 完成 CsI Phase 7 / Gate L
    -> 完成 Phase 8 Flavor Fast / Gate F
    -> 独立实现正式 propagation backend / SNuDD adapter
    -> solar rho(E_nu) Slow regression
    -> energy-resolved solar Fast
    -> Statistics / Registry / full regression
    -> 单独代码卫生
    -> 明确选择文件 commit/push
```

如果近期目标仍然是 CsI，应先完成 Gate L；SNuDD 不属于 CsI SNS 物理链，不应为了“看起来已接入”而混进 CsI Phase 7 提交。

## 11. Git 与提交状态

当前 `bb8d2aa` 是 Helm 阶段提交。P0-P2、CsI workflow 报告、Phase 7 局部接线以及本状态文档都仍是本地工作树内容。

当前禁止：

- `git add .`；
- force-push；
- 覆盖旧分支；
- 从旧非 Git 副本整体复制；
- 把 `pyc` 混入源码提交；
- 在 Gate L 前宣称 Slow、Fast 或 SNuDD 已完成。
