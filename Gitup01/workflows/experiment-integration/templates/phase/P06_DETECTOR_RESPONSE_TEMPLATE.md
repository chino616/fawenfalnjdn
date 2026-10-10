# P06｜Detector Response：可填写模板

对应 [cevns-detector-response Skill](../../skills/cevns-detector-response/SKILL.md)。**每台探测器、每个配置期**各填一份；若声称共用响应，给出共用的证据。用户可填写公式/参数，或给论文、校准曲线和文件位置由 AI 摘录。实际调用链和可运行示例见 [P06 探测器响应代码参考](P06_DETECTOR_RESPONSE_CODE_REFERENCE.md)。

## A. 用户填写：从真反冲到观测量

| 字段 | 请填写；值 + 单位 + 来源定位 |
| --- | --- |
| dataset_id、探测器 ID、配置期 | ____；____；____ |
| 真反冲 `T` | 物理量和单位 ____；可用范围 ____ |
| 重建量 `x` | 名称/单位 ____；PE、电子等效能或其他 ____ |
| 平均映射 `mean_x(T)` | 公式/曲线/表格 ____；参数及单位 ____；校准版本 ____ |
| quenching / yield | 定义 ____；参数/数据文件 ____；是否已包含在平均映射里 ____ |
| 分辨率或迁移核 `R(x|T)` | □ 概率密度 □ 响应矩阵 □ 理想无展宽；公式/矩阵文件及轴 ____ |
| 响应归一化域 | 对 `x` 的完整积分范围 ____；物理边界/截断规则 ____；窗外迁移如何处理 ____ |
| 效率/接受率 `ε` | 公式/文件 ____；作用于 □ `T` □ `mean_x` □ 重建 `x`；作用前后的顺序 ____ |
| 阈值 | 触发/重建/分析阈值是哪一种 ____；数值/单位 ____；是否另有平滑效率 ____ |
| 分箱与窗口 | 精确边界文件/规则 ____；单位 ____；各探测器差异 ____ |
| 数据来源类别 | 每个参数标 □ 官方 □ 数字化 □ 近似；数字化误差或近似适用域 ____ |

没有展宽、quenching 或效率时，明确填“理想模型＝……，依据……”；不能留空或把缺失值填 0。若把多探测器合成一台有效探测器，写出权重、近似及对目标声明的影响：____。

## B. AI 核对：最薄响应接口

| 职责 | 输入→输出、单位和 shape | 文件.symbol / 复用判断 |
| --- | --- | --- |
| `mean_reconstructed_observable(T,spec)` | ____ | ____ |
| `resolution_width(mean_x,spec)` 或矩阵选择 | ____ | ____ |
| `response_density(x,T,spec)` / `R[reco,true]` | ____；全域归一化：____ | ____ |
| `efficiency(x_or_T,spec)` | ____；作用位置：____ | ____ |

分类用 `REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED`，逐函数说明原因：____。本层只描述探测器，不读取通量、不算截面、不乘曝光、不积分最终事例数。

## C. 检查与 Gate

- [ ] 平均映射在适用域物理可行；宽度为正；响应非负、按完整域归一化。
- [ ] 效率在 [0,1]；其自变量、阈值与插值边界已核查；窗外迁移没有被隐式重归一化。
- [ ] 标量、数组与广播行为一致；保存映射图、响应切片、效率图和参数来源表。
- Machine Gate P06：`NOT_RUN / PASS / BLOCKED`；诊断与测试路径：____。
- Human Gate：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；响应近似决定：____。

**CsI2021 结构参考**：`rates.differential.eee_quenching_csi`、`p_smearing_csi` 与 `slow_counts_csi2021.efficiency_csi2021` 分担映射、迁移和效率。它们的 PE 语义与参数属于 CsI2021；新探测器只可参考职责拆分。

