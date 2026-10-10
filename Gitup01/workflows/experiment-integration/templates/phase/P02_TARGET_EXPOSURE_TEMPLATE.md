# P02｜Target / Exposure：可填写模板

对应 [cevns-target Skill](../../skills/cevns-target/SKILL.md)。按**每种同位素、每台探测器、每个运行期**分别填；用户可给表格/论文位置由 AI 摘录。每个数值写单位和来源。此阶段通常核对配置与核响应，不自动新增 target Python。

## A. 用户填写：靶和曝光

| 必要信息 | 请填写；未知填“缺失” |
| --- | --- |
| experiment_slug；dataset_id；探测器/运行期 ID | ____；____；____ |
| 靶材料 | 元素/化合物：____；天然/富集/单同位素：____；化学计量：____ |
| 同位素明细 | 每行：`核素 ____；Z ____；A 或质量 ____；丰度 ____；number_fraction/mass_fraction ____；来源 ____` |
| 摩尔质量与常数来源 | 取值/单位/版本：____；不同核素是否按精确质量或 A 近似：____ |
| 核 Response 资料 | 文件/版本：____；每个同位素的 key：____；缺项及处理：____ |
| 有效质量 | 每台探测器质量、单位、fiducial/active 定义、来源：____ |
| 活时间或曝光 | 活时间 ____（s/day）；或已给曝光 ____（kg·day）；两者关系及定义：____ |
| 运行分段 | 如质量、活时间或组分随运行期改变，逐段填写：____ |
| 源时间基准（从 P03 回填） | □ 每秒通量 □ 已积分注量 □ 尚未知；当前 P02 对时间因子的约定：____ |

**互斥归一化选择**：用于每秒通量时，□ `mass_kg × live_time` 或 □ 已给 `exposure_kg_day`；选择：____。若源已给时间积分注量，计算只再乘靶质量，记录活时间已包含于源，不能再次乘。若论文只给 kg·day 而不能拆出质量，应在 P03/P07 前解决注量的适配问题。

## B. AI 核对：逐靶计算及复用

| 核素/探测器 | fraction 类型和换算 | nuclei/kg 推导与单位 | Response key 是否存在 | 来源 |
| --- | --- | --- | --- | --- |
| ____ | ____ | ____ | ____ | ____ |

| 代码契约 | 本次填写 |
| --- | --- |
| 候选共用入口 | `nuclear.response.ResponseDB.get(key) → ResponseW`；实际 key、通道和单位：____ |
| 组合接口 | `per_isotope_rate × isotope_count → detector_rate`；化合物/丰度权重施加位置：____ |
| 逐函数分类 | `REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED`；理由：____ |
| 归一化 owner 台账 | 源：____；核数/kg：____；质量：____；时间：____；是否已包含于另一因子：____ |
| 产物 | `runs/<experiment_slug>/<dataset_id>/02_DETECTOR_TARGET.md`；必要的配置补充：____ |

## C. 完成检查

- [ ] 同位素清单完整；fraction 类型明确，合计及单位转换可复算。
- [ ] 每个核素的 Response key 存在或明确标记阻断；没有用相近核素静默替代。
- [ ] 靶核数/kg 可独立复算；源、质量和时间各只归一化一次。
- Machine Gate P02：`NOT_RUN / PASS / BLOCKED`；复算和检查结果：____。
- Human Gate：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；物理选择：____。

**CsI2021 结构参考**：`ResponseDB.get` 选择 Cs133 与 I 的响应；`slow_counts_csi2021.combine_equal_stoichiometry` 体现 Cs/I 等化学计量。新靶必须重新推导组成权重，不能复制该组合公式或质量数值。

