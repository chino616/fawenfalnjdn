# P01｜Dataset：可填写模板

对应 [cevns-dataset Skill](../../skills/cevns-dataset/SKILL.md)。复制本文件作为本次实验的 P01 工作表。用户可以直接填写，也可以在“资料位置”栏给论文/数据，交由 AI 摘录。每个关键值写 **值、单位、来源定位（页/表/文件列）**；找不到填“缺失”，不用填“不适用”，有冲突保留两种说法。填写不等于 Physics Gate 批准。

## A. 用户填写：数据集边界

| 必要信息 | 请填写；可用资料定位代替数值 |
| --- | --- |
| `experiment_name`、`experiment_slug`、唯一 `dataset_id`；论文或资料版本 | ____；____；____ |
| 本次目标 | □ 官方复现 □ 近似 forward model □ 旧程序回归 □ 新预测；具体可验证的输出：____ |
| site、运行期、探测器列表 | 包含：____；排除：____；各探测器配置版本：____ |
| 一个 dataset 还是需要拆分 | 不同运行期、源、靶、响应或统计定义的差异：____ |
| 真实物理量与最终观测量 | 真实量/单位：____；重建量/单位：____；仅真实谱时说明：____ |
| 输出量 | □ 率 □ 逐箱期望事件数 □ 非分箱事件；单位：____；保留的轴及顺序：____ |
| 分箱 | 边界数组/文件：____；单位：____；左/右端点规则：____；箱数：____ |
| 阈值和分析窗口 | 阈值定义：____；窗口：____；是否与 bin 范围相同：____ |
| 观测数据的主要语义 | □ raw_counts □ signal_plus_background □ on_off □ background_subtracted_excess □ unbinned_events □ 尚未知；证据：____ |
| 静态靶和曝光元数据 | 材料：____；探测器质量或曝光：____；这里只登记，P02 核对归一化 |
| 输入文件 | 相对仓库路径、版本、列名、单位、数据点数：____；外部文件取得方式：____ |

若有多台探测器或多个运行期，请复制一份“探测器/运行期”记录：`ID ____；观测量 ____；bin ____；输出轴 ____；数据语义 ____；资料定位 ____`。

## B. AI 核对：配置与代码契约（用户可核对）

| 检查项 | 本次填写 |
| --- | --- |
| 已批准的 `dataset_id` / scientific claim / decision ID | ____ / ____ / ____ |
| `contract 字段 → experiment.yaml key` 逐项映射 | ____；未被 schema 表达的字段：____ |
| 候选函数 | `experiments.specs.load_experiment_spec(name_or_path) → ExperimentSpec`；实际文件/签名/错误行为：____ |
| 输出契约 | 轴顺序：____；shape：____；dtype：____；unit：____；各探测器组合规则：____ |
| 复用判断 | □ REUSE □ CONFIG_ONLY □ ADAPTER □ SHARED_EXTENSION □ CORE_EXTENSION □ BLOCKED；逐项理由及受影响实验：____ |
| 计划文件 | `data/experiments/<experiment_slug>/<dataset_id>/experiment.yaml`、`README.md`、`runs/<experiment_slug>/<dataset_id>/01_DATASET.md`；增改列表：____ |
| 缺失回填 | 字段：____；取得途径：____；最迟 P__ 需要；阻断能力：____ |

## C. 完成检查

- [ ] `experiment_name` 清楚、`experiment_slug` 可读且文件系统安全、`dataset_id` 唯一；源文件路径可从仓库定位；schema 和 loader 均接受配置。
- [ ] bin edges 严格递增，`len(edges)-1` 与输出箱数一致；所有输出轴、单位和数据模式已明确。
- [ ] 配置中的 pending callable 与实际实现状态一致；未实现能力未写成已完成。
- Machine Gate P01：`NOT_RUN / PASS / BLOCKED`；命令及结果：____。
- Human Gate：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；批准的合同或待修改项：____。

**CsI2021 结构参考**：`data/experiments/CsI2021/experiment.yaml` 使用显式 PE bin、`[source_component, pe_bin]` 输出和 `experiments.specs.load_experiment_spec`。这些数值、数据语义和状态不得作为新实验默认值；配置列出的 reference 路径须单独检查实际存在性。

