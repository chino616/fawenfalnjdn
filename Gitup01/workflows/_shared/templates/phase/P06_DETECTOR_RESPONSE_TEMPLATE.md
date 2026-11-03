# P06｜探测器观测算子

每台探测器/配置期分别填写。见 [P06 Skill](../../../cevns-pyeft/skills/phases/cevns-detector-response/SKILL.md)、
[执行合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)与
[代码参考](../../references/phase/P06_DETECTOR_RESPONSE_CODE_REFERENCE.md)。

## A. 用户材料

| 内容 | 值、单位与来源定位 |
|---|---|
| dataset、探测器、运行期；P01 观测定义 | ____ |
| 真反冲量与有效域 | ____ |
| 重建量、精确 bin edges、窗口 | ____ |
| yield/quenching、均值映射及版本 | ____ |
| 展宽模型/矩阵/理想映射及依据 | ____ |
| 效率自变量、阈值类型、选择顺序 | ____ |
| 窗外迁移、溢出箱、尾部和插值规则 | ____ |
| official/digitized/approximate 分类及不确定性 | ____ |

## B. AI 输出合同

选择 representation：conditional_density / bin_probability / migration_matrix / deterministic。
- unit：____。bin_probability 必须为 `1`（无量纲）。
- normalization：integral_one / sum_at_most_one / explicit_rule；完整定义域与理由：____。
- axes：每轴名称、单位、顺序、边界：____；外部矩阵转置/权重处理：____。
- response_definition：公式、资源、版本和实际 symbol：____。
- included_selections：已包含的 selection ID 列表：____；没有则为空列表。
- selection_ownership：每个效率/接受率在哪里应用、哪些由 P07 补充：____。
- validity_domain：探测器/运行期、有效域和多维/聚合能力限制：____。

conditional_density 在声明完整域检查归一化；已含效率/窗口的互斥 bin_probability 行和至多为 1。
不得把两者混用。矩阵还须说明元素是密度、概率还是已乘积分权重；禁止重复乘效率。
当前 BinProbabilities.values 的轴是 (n_true, *binning.shape)。

## C. 实现、诊断与交接

实际 ObservationModel / sampled_density 路线和数值策略：____。
复用/扩展判断、近似决定、当前 executor 是否支持目标维度和聚合：____。
验证映射、适用的宽度条件、密度积分/概率行和、效率范围、相邻箱闭合、
窗外迁移、插值边界、广播；保存对应诊断。
用 [阶段报告](PHASE_REPORT_TEMPLATE.md) 的 handoff 保存 B 区字段，返回 Master。
