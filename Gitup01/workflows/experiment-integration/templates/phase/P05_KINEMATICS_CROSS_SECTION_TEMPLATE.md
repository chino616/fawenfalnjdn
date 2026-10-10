# P05｜Kinematics / Cross Section：可填写模板

对应 [cevns-kinematics-cross-section Skill](../../skills/cevns-kinematics-cross-section/SKILL.md)。用户提供散射模型、变量和论文公式位置；AI 核对现有微分截面。此阶段不处理通量、曝光或探测器折叠。真实函数、核心公式、可运行调用和 Helm 分支选择见 [P05 运动学与截面代码参考](P05_KINEMATICS_CROSS_SECTION_CODE_REFERENCE.md)。

## A. 用户填写：截面定义

| 字段 | 请填写；数值需带单位与来源 |
| --- | --- |
| dataset_id；散射过程 | ____；□ 弹性 □ 其他（写公式/来源）____ |
| 入射能量 `Eν` | 单位 ____；输入范围 ____；能量约定（总能/动能）____ |
| 真反冲量 `T` | 物理意义 ____；单位 ____；分析范围 ____ |
| 核质量 | 同位素逐项来源 ____；单位 ____；质量数近似/精确质量 ____ |
| 运动学边界 | `Eν_min(T)` 公式/出处 ____；`T_max(Eν)` 公式/出处 ____；近似适用域 ____ |
| `dσ/dT` | 论文公式/项目模型 ____；输出单位 ____；核 Response/form factor 与 P04 的关系 ____ |
| flavor/ν反ν | 入射状态与末态求和约定 ____；需要区分 ν/反ν 的项 ____ |
| 域外行为 | 不满足阈值、超端点、负能量时应返回零/错误：____ |
| 可复算点 | 同位素 ____；`Eν` ____；`T` ____；期望 `T_max/Eν_min/dσ/dT` ____；来源 ____ |

## B. AI 核对：函数接口和单位桥

| 职责 | 实际文件.symbol / 是否复用 | 输入→输出；轴/单位；边界行为 |
| --- | --- | --- |
| `Eν_min(T,target)` | ____ | ____ |
| `T_max(Eν,target)` | ____ | ____ |
| `dσ/dT(Eν,T,target,coeffs,state)` | ____ | ____ |
| 实验薄适配层（若需） | ____ | 只桥接靶/源参数及单位：____ |

复用分类：____；如果共享函数需要改动，影响的既有实验和回归：____。写明 `MeV↔GeV`、`keV↔GeV`、面积单位的转换 owner：____。

## C. 完成检查

- [ ] `T=0`/小反冲、端点、`Eν_min(T_max)` 逆关系和支撑域外行为已核查。
- [ ] 至少一个端点可由手算或独立公式复算；SM 非负性在适用域内检查。
- [ ] full response 与比较模型的适用域不混用；EFT 参数点和 flavor 约定已核对。
- Machine Gate P05：`NOT_RUN / PASS / BLOCKED`；端点数值、测试结果：____。
- Human Gate：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；物理约定决定：____。

**CsI2021 结构参考**：`rates.differential.differential_cross_section_nn` 与 `differential_flavor_kernel_nn` 是候选共享入口。只借用函数职责和单位检查方式，不复制 CsI/SNS 的能量网格或靶参数。

