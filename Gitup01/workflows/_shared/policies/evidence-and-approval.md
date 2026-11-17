# evidence-and-approval

## 2. Physics Decision 菜单

正式采纳物理语义的定义、选择、近似或改变时，必须使用显式菜单。
隔离自动运行可以在副本中测试候选，但不能把候选选择写成正式 Physics Decision；
最终导入按 `workflows/_shared/policies/automation.md` 请用户审核实际采用的路线。

```text
需要你决定的物理问题：<标题>

目前已知：...
需要选择：...
不同选择的影响：...

1. 接受 <候选>（需要固定批准口令时同时写明该口令）
2. 选择其他候选或提出修改
3. 查看证据或代码
4. 暂停此决定
```

如果存在 2 个以上互斥物理候选，选项必须把候选逐项列出，不能用“是否接受推断 y/n”隐藏其他候选。


## 3. Machine Gate 与 Human Physics Gate

状态独立记录：

```yaml
machine_gate: PASS|BLOCKED|NOT_RUN
human_gate: APPROVED|REVISE|BLOCKED|NOT_REVIEWED
```

正式阶段只有在二者满足所需条件时才可向后推进。按
`workflows/_shared/policies/automation.md` 在隔离副本中推进的阶段只是候选；候选 Machine PASS
不产生正式 Human approval，也不更新原项目的 Gate。


## 5. Evidence status

仅使用：

```text
SOURCE_EXTRACTED
PROJECT_DERIVED
USER_CONFIRMED
REFERENCE_ONLY
MISSING
CONFLICT
```

发现冲突时保留所有 claim，不覆盖。


### 5.1 逐数据来源与核验范围

执行[Onboarding 数据溯源与补充闭环](../references/onboarding/data-provenance-contract.md)。
`SOURCE_EXTRACTED` 表示从已登记的直接材料提取，不自动表示原始论文数字已核。
二手转录的直接材料、所引上游文献及实际核验范围分开记录；`USER_CONFIRMED` 只证明相应选择确已发生，不能认证外部事实。
派生结果引用完整输入与变换，继承未闭合的来源限制。现有 evidence status 枚举不变。

首次可读输出必须主动披露缺失数据、溯源缺口及影响，提出针对性补充问题；补充后更新证据并重生成。
终稿的每个采用项都要有可审阅的依据，是否满足请求的原文/benchmark 主张另行核验；Machine PASS 不替代这项审阅。

## 6. Decision log

每次 Physics Decision 追加：

```yaml
decision_id: Dxxxx
phase: ...
field: ...
options_shown: [...]
user_choice: ...
evidence_claims: [...]
result: ...
```
