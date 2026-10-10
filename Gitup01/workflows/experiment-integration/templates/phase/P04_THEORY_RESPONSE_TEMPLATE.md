# P04｜Theory / Nuclear Response：可填写模板

对应 [cevns-theory-response Skill](../../skills/cevns-theory-response/SKILL.md)。本阶段决定**共享理论链**是否覆盖新实验。用户说明需要的物理模型或给出处；AI 核对代码。核 Response 与探测器 Response 是不同对象。真实函数、精简核心代码和可运行调用见 [P04 核响应代码参考](P04_NUCLEAR_RESPONSE_CODE_REFERENCE.md)。

## A. 用户填写：模型范围

| 必要信息 | 请填写；值/定义 + 来源定位 |
| --- | --- |
| dataset_id；要计算的模型 | □ SM □ EFT □ 指定比较模型；目标参数域和科学声明：____ |
| Wilson 系数 | 基底名称与版本 ____；系数顺序 ____；单位 ____；实数/复数 ____；SM 项是否包含：____ |
| flavor 结构 | 入射与末态 flavor 约定 ____；ν/反ν 适用性 ____；纯态或密度矩阵：____ |
| nucleon matching | 使用的约定/参数/文献定位：____；如沿用项目共享实现，请写“按项目共享实现” |
| 靶核 Response | 每个同位素的文件、key、版本、有效动量域：____ |
| 需要的通道 | 保留 ____；明确省略 ____；省略理由和影响：____ |
| SM 对照模型 | □ 完整 nuclear response □ Helm/其他仅作比较 □ 无；适用参数域：____ |
| 参考点 | 能量、靶、系数和可对照的截面/响应值：____；无外部点填“缺失” |

## B. AI 核对：共享链与复用

| 步骤 | 当前文件.symbol | 输入→输出、单位/轴 | 是否覆盖本实验/证据 |
| --- | --- | --- | --- |
| Wilson → nucleon matching | ____ | ____ | ____ |
| nucleon → particle/nuclear response | ____ | ____ | ____ |
| ResponseDB key 与通道 | ____ | ____ | ____ |
| flavor/复数收缩 → differential API | ____ | ____ | ____ |

逐函数分类：`REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED`；不适用原因或扩展对 CsI2017、CsI2021、Ar2020 的影响：____。完整核 Response 后不能再乘 Helm；仅 SM 有效的比较模型不得悄悄接受一般 EFT。

## C. 物理决定与 Gate

- 待批准的共享路线、系数约定和 Response key：____；冲突候选：____；decision ID：____。
- [ ] 共享理论回归、Response key/通道、复数系数、flavor 轴和 SM benchmark 已检查。
- [ ] ν/反ν kernel 适用性有证据；若未审计，明确限制可宣称的能力。
- Machine Gate P04：`NOT_RUN / PASS / BLOCKED`；检查命令及结果：____。
- Human Gate：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；受影响的共享代码：____。

**CsI2021 结构参考**：`rates.differential.differential_flavor_kernel_nn` 提供共享 flavor kernel 的候选入口；`ResponseDB.get` 选择核响应。新实验要核对基底、通道、单位和反中微子适用域，不能因为函数已存在就直接判定 `REUSE`。

