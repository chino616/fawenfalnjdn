# write-authorization

本政策的准确写入口令约束正式实验接入、实验续作和 mock physics artifacts。
已明确授权的纯 workflow 结构维护或普通 runtime 工程动作按其工作流范围执行，
不要求把用户同一工程请求再转述为物理写入口令；这不授予新物理选择或实验激活。

## 4. confirm_mode

`confirm_mode=minimal` 可以自动通过：

- 重复的执行确认；
- 非物理参数的默认值（前提是 Skill 明确指定）。

它不能自动通过任何原项目文件写入，包括 mkdir、`.onboarding_tmp` mock 文件、
state/ledger/report 文件、正式 run 文件、data/src/tests/registry 修改。
独立目录的写入由 `workflows/_shared/policies/automation.md` 的单次启用授权控制，与
`confirm_mode=minimal` 无关。

它绝不能自动通过：

- dataset identity；
- scientific claim；
- target/isotope interpretation；
- source normalization route；
- detector response approximation；
- statistical data semantics；
- Slow authoritative freeze；
- Fast mathematical meaning；
- final scientific claim。


## 4.1 Write Approval Gate

原项目的任何文件写入均执行本节；隔离候选目录的写入仅在
`workflows/_shared/policies/automation.md` 的带 `plan_id` 启用授权后进行。两者的授权范围不能混用。
写入前按 [交互规范](interaction.md)说清目的、用户可见的变化、影响范围和完成后的停止点。
用户已审核过的科学细节不机械重述。

用户可见的 `[WRITE PLAN]` 按“文件的用途”组织，不把 `Scope`、`Reason`、
`Create`、`Modify`、`Delete` 等内部字段名或一串裸路径当作说明：

1. **会改什么**：按用户能识别的对象分组，说明每组文件具体新增/修改/删除的
   内容及其用途；说清正式配置或代码是否影响运行结果，审核记录会记录哪项
   已发生的决定，进度会指向哪项下一工作。不能只说“更新报告、状态和进度”。
   相同信息只说一次。
2. **影响与恢复**：用中文写明只影响哪个实验和 dataset、是否改变正式配置或
   计算代码、若出错如何恢复。无删除也要明确说明。
3. **准确路径供核对**：在批准请求之前列出每条路径及其新增/修改/删除动作，
   让路径与上述用途一一对应，不让用户从文件名猜测用途。
   可先写共同目录前缀，再列该目录下的文件名；前缀与文件名组合后必须唯一
   确定完整路径。路径放在对应用途组后或单独的路径核对区，不替代用途说明。
4. **单一用户动作**：普通原项目写入请准确回复 `APPROVE WRITE`；隔离候选的
   最终导入按 `workflows/_shared/policies/automation.md` 展示科学结论和路径后，请准确回复
   `批准导入 <promotion_id>`。两种回复只覆盖各自展示的范围；也可提出修改或
   回复 `BLOCK`。等待该回复时不附通用主线菜单。

`Scope` 等内部枚举仍按规范写入 Authorization Log；面向用户说明其实际
边界即可。文件扩展名、阶段编号和 revision 仅在区分路径或当前决定确实需要时
解释。不要在开头和文件分组中重复同一变更，也不要把备份隔离等内部规则展开
为与当前授权无关的长说明。

只有用户明确回复 `APPROVE WRITE` 或有效的 `批准导入 <promotion_id>` 后，
才能执行列出的原项目写入。用户批准只覆盖计划中的准确路径和动作；新增路径
或动作必须重新请求批准。隔离目录的启用口令不授权写入原项目。

原项目默认状态为 `read_only`。读取文件、列目录、运行非写入校验、展示候选菜单
不需要 Write Approval Gate；隔离自动运行中的技术写入不改变这一默认状态。


## 12. WRITE_AUTHORIZATION_LOG

Write Approval 与 Physics Decision 分开编号。普通原项目写入只有用户在完整
`[WRITE PLAN]` 后精确回复 `APPROVE WRITE` 才产生 `Wxxxx`。隔离候选导入只有用户
审核完整导入计划后精确回复 `批准导入 <promotion_id>` 才产生对应的 `Wxxxx` 和
独立的 Physics Decision。启用自动模式只授权指定隔离目录；候选计划、模糊同意或
其他问题的回答不产生原项目写入授权。

每条授权至少记录：

```yaml
authorization_id: W0001
status: ACTIVE|EXHAUSTED|REVOKED|SUPERSEDED
approved_at: ISO-8601
approval_message_ref: <当前对话中的原始批准引用>
approval_kind: manual_write|promotion
promotion_id: null
scope: skill_debug|physics_onboarding|existing_dataset
plan_ref: <WRITE PLAN 引用或完整摘要>
allowed_actions: [create, modify, delete]
create_paths: []
modify_paths: []
delete_paths: []
production_paths_affected: false
recovery_plan: ...
supersedes: []
superseded_by: null
```

日志追加写，不覆盖历史授权。`authorization_refs` 只是索引；每次写入仍须核对原批准
的路径、动作和有效范围。临时目录授权不覆盖正式 run；某次创建授权不自动覆盖以后
新增路径。若 `[WRITE PLAN]` 明确批准在列出的状态变化事件持续修改同一个进度文件，
该授权可覆盖这些精确事件；任何路径或动作扩展必须申请新的 `Wxxxx`。

日志文件本身也受 Write Approval Gate 约束。首次日志尚未获准创建时，当前对话中的
原始 `[WRITE PLAN]` 与 `APPROVE WRITE`，或完整导入计划与准确的
`批准导入 <promotion_id>`，是对应写入的权威；日志创建后可按原始批准补录。
