# P10｜Validation / Release：可填写模板

对应 [cevns-validation Skill](../../skills/cevns-validation/SKILL.md)。用户明确希望最终宣称什么；AI 根据证据与 Gate 限定实际可宣称的能力。P08/P09 可未请求，但必须在矩阵中保留状态。registry、spec 与 reference 检查示例见 [P10 验证与暴露代码参考](P10_VALIDATION_RELEASE_CODE_REFERENCE.md)。

## A. 用户填写：最终交付目标

| 字段 | 请填写；可给外部资料定位 |
| --- | --- |
| experiment_name、experiment_slug、dataset_id、配置版本、希望交付的接口 | ____；____；____ |
| 目标科学声明 | □ 内部数值一致性 □ 旧程序回归 □ 论文 forward prediction 复现 □ 官方 likelihood 复现；具体图/表/参数点：____ |
| 外部基准 | 论文图表/官方数据/参考数组路径与版本：____；参考条件：____ |
| 容差 | 数值/单位/依据：____；数字化图表误差与数值积分误差分别：____ |
| 预期已知近似 | 源、靶、响应、统计或有效探测器近似：____；适用范围：____ |
| 交付形式 | callable、配置、逐箱表、图、报告、physics document：____ |

## B. AI 填写：能力与 Gate 矩阵

| 阶段/能力 | Machine Gate | Human Gate | 证据状态 | 可暴露的接口/限制 |
| --- | --- | --- | --- | --- |
| P01 Dataset | ____ | ____ | ____ | ____ |
| P02 Target | ____ | ____ | ____ | ____ |
| P03 Source | ____ | ____ | ____ | ____ |
| P04 Theory | ____ | ____ | ____ | ____ |
| P05 Cross section | ____ | ____ | ____ | ____ |
| P06 Detector | ____ | ____ | ____ | ____ |
| P07 Slow | ____ | ____ | ____ | ____ |
| P08 Fast（可选） | ____ / NOT_REQUESTED | ____ | ____ | ____ |
| P09 Statistics（可选） | ____ / NOT_REQUESTED | ____ | ____ | ____ |

`NOT_REQUESTED` 只用于阶段计划，不是假装 Machine Gate `PASS`。注册只暴露满足必要证据且 Machine/Human Gate 均通过的 callable；metadata discovery 不代表计算已实现。

## C. AI 填写：复现与回归

| 验证层级 | 参考、条件和来源 | 运行命令 / 输出 | 差异与结论 |
| --- | --- | --- | --- |
| 内部数值一致性与收敛 | ____ | ____ | ____ |
| 旧程序/reference-code 回归 | ____ | ____ | ____ |
| 论文 forward prediction | ____ | ____ | ____ |
| 官方 likelihood | ____ | ____ | ____ |
| 既有 CsI2017/CsI2021/Ar2020 回归（相关时） | ____ | ____ | ____ |
| cache metadata、registry load/discovery | ____ | ____ | ____ |

## D. 最终声明与释放决定

- 已验证能力：____；阻断能力：____；已知近似：____；论文/数据集不一致处：____。
- **允许写入报告的声明**：____。**禁止写入报告的声明**：____。
- 代码/registry 变更及回滚位置：____；canonical `physics_docs/experiments/<experiment_slug>/<dataset_id>/experiment_physics.tex` 生成状态：____。
- Machine Gate P10：`NOT_RUN / PASS / BLOCKED`；完整回归命令及结果：____。
- Final Human Gate：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；最终批准的精确措辞：____。

**CsI2021 结构参考**：`experiments.registry` 展示能力注册模式。`experiment.yaml` 中列出的 `tests/reference_CsI2021/*`、`runs/CsI2021/00_*` 若在活动目录不存在，应记 `MISSING`；不能以配置路径或内部一致性代替外部回归。

