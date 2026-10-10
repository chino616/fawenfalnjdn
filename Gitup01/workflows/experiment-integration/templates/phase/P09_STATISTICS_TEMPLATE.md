# P09｜Statistics（按目标可选）：可填写模板

对应 [cevns-statistics Skill](../../skills/cevns-statistics/SKILL.md)。若只迁移 forward prediction 且未请求统计，本阶段计划填 `NOT_REQUESTED`，不要构造伪 likelihood。若请求官方 likelihood，用户应提供其所需数据和定义或给出可核查的材料位置。旧 CsI2021 观测量转换和 χ² 的边界见 [P09 统计代码参考](P09_STATISTICS_CODE_REFERENCE.md)。

## A. 用户填写：观测数据语义

**只选择一个主要模式**：□ `raw_counts` □ `signal_plus_background` □ `on_off` □ `background_subtracted_excess` □ `unbinned_events`。论文/数据列对此模式的明确定义和来源定位：____。不能凭计数是否为整数推断模式。

| 字段 | 请填写；值 + 单位 + 来源定位 |
| --- | --- |
| dataset_id；希望得到的统计结果 | χ² / likelihood / best fit / 区间 / significance：____ |
| 观测数据文件 | 版本/路径/列名/探测器/运行期：____；bin 或事件轴：____ |
| 信号预测映射 | P07/P08 的哪一输出 ____；bin 重排、单位变换或曝光匹配 ____ |
| 背景 | 模板/控制区/ON-OFF 比例/不确定度：____；是否已从 observed 扣除 ____ |
| 协方差或逐箱误差 | 文件及轴/单位 ____；对称/非对称 ____；相关性 ____ |
| nuisance 参数 | 名称、作用于信号/背景/效率的公式、范围、先验、相关性：____ |
| 统计定义 | Poisson/Gaussian/其他公式及出处 ____；是否包含常数项 ____ |
| 推断规则 | profiling/marginalization ____；test statistic ____；置信区间阈值或 toys ____ |
| 外部基准 | 已发表最佳拟合/区间/显著性及对应数据版本 ____ |
| 声明等级 | □ 旧程序统计回归 □ 数字化/简化近似 □ 官方 likelihood 复现；证据：____ |

背景扣除后的 excess 可以为负，不能直接代入 raw Poisson。只有总事例数或显著性不足以构建官方 likelihood；缺协方差/相关性时保留 `BLOCKED`，不得猜。

## B. AI 核对：统计接口

| 职责 | 候选文件.symbol | 输入→输出、shape/unit | 复用判断 |
| --- | --- | --- | --- |
| `dataset → observed/background/covariance` | ____ | ____ | ____ |
| `prediction → approved observable` | ____ | ____ | ____ |
| `expected → logL/χ² → profile` | ____ | ____ | ____ |
| confidence construction | ____ | ____ | ____ |

分类为 `REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED`；旧实验的 pull 公式不能只改 dataset 名称就复用。记录统计数据文件的 provenance：____。

## C. 验证与 Gate

- [ ] 观测模式、bin 对齐、背景定义、单位和 covariance shape 已核对。
- [ ] toy 数据、nuisance 极值/边界、profile、发表基准差异和数据来源均记录。
- Machine Gate P09：`NOT_RUN / PASS / BLOCKED`；公式、代码、结果：____。
- Human Gate：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；允许的统计声明：____。

**CsI2021 结构参考**：`statistics.datasets.csi2021_dataset` 返回 `BinnedDataset`，`statistics.likelihoods.chi2_csi2021` 调用 Gaussian 双 pull profiling。这是当前旧程序统计定义的参考，不自动证明官方 likelihood 复现；其数据 provenance 必须逐项核查。

