# Codex 任务卡、替换卡与审核模板

状态：TEMPLATE。复制到实际授权的记录位置后填写；尖括号字段是待填项，不是默认物理输入。
本包只提供模板，不自动创建或批准项目 workflow 状态。

## 1. 阶段任务卡

```yaml
task_id: <唯一标识>
work_package: <R0..R6>
repository_commit: <实际提交>
dataset: CsI2021
task_kind: <refactor_preserve_behavior|capability_extension|physics_change>
objective: <具体可验证目标>
authorization_basis: <实际用户请求及适用规则，不虚构批准>
read_first:
  - <实际合同文档>
inputs:
  - <资源路径、版本、内容哈希及语义>
create_paths: []
modify_paths: []
delete_paths: []
must_preserve:
  - <API 或旧物理/数值行为>
checks_required:
  - <真实可运行入口>
blocked_inputs: []
completion_evidence: []
```

任务必须具体到实际文件。不能只写“重构所有接口”“完成模块化”，也不能先填 PASS 再实现。

## 2. 模块替换卡

```yaml
replacement_id: <唯一标识>
slot: <source|targets|interaction|observation.efficiency|其他明确插槽>
classification: <见12的分类>
old:
  model_id: <旧实现>
  model_revision: <旧版本>
  contract_id: <合同>
  fingerprint: <实际值>
new:
  model_id: <新实现>
  contract_id: <目标合同>
physical_change: <明确写出；若只改接口则写无>
unit_and_axis_conversion: <无或具体转换>
normalization_ownership_change: <无或具体变化>
additional_slots_required: []
allowed_paths: []
recompute:
  - <从依赖图得到的对象>
reuse:
  - <经依赖检查可以保留的对象>
module_checks: []
pipeline_checks: []
shared_regressions: []
```

## 3. 阶段报告

```markdown
# <阶段名称> 实施结果

## 完成的行为
<从用户入口出发说明新行为，列实际调用路径。>

## 文件变化
| 文件 | 动作 | 原因 | 是否改变物理结果 |
|---|---|---|---|

## 物理交接
| 边界 | 输入量/单位/轴 | 输出量/单位/轴 | 已含因子 |
|---|---|---|---|

## 实际验证
| 检查 | 命令或入口 | 状态 | 最差误差/证据 | 适用范围 |
|---|---|---|---|---|

## 尚未完成
<缺资料、未支持能力、未运行检查及其影响。>

## 下一步与恢复
<下一项实际动作、版本和输入条件、恢复办法。>
```

不能只汇报测试个数。关键回归需列最差 bin、参数点和相对/绝对误差。

## 4. 可恢复执行记录

```yaml
record_schema: refactor_checkpoint_v1
task_id: <实际值>
work_package: <R编号>
step: <具体函数/检查/输入待办>
revision: <整数>
base_commit: <基线>
current_commit: <当前版本或未提交状态说明>
changed_file_fingerprints: {}
input_fingerprints: {}
completed_checks: []
pending_checks: []
blockers: []
next_action: <单一明确动作>
```

本工程记录不是现有 Master 的 MIGRATION_PROGRESS，也不替代其 Gate/授权日志。
恢复时核对真实代码和输入；记录与当前版本不一致则重新验证受影响项目。

## 5. 接口审核问题

- 这个输入是 flux、fluence、概率、截面还是事件数？
- 单位是否在签名/类型和校验中固定？
- 实际坐标是否与数组值同行，还是只有 shape？
- 质量、曝光、接受率和求积权重各由谁施加？
- 使用者是否仍根据 SNS/CsI 的名字决定算法？
- 新实现能否与旧实现同时存在？
- 配置的每个公开字段是否真正被消费？
- 不支持的输入是否在计算前被拒绝？
- 结果能否追溯到当前组件和数据内容？

## 6. 建议给 Codex 的分阶段任务

### R1–R3 实施任务示例

```text
根据本包已核对的源码和R0基线，实施R1–R3。
保持CsI2021现有9箱、物理参数和legacy数值约定。
实现源/靶核/截面/观测/预测合同，建立显式组装与通用Slow主链。
保留旧入口和历史raw输出语义，保护CsI2017/Ar2020。
不要在这次接口迁移中改核响应规范、反中微子处理、源尾部或统计定义。
逐阶段完成实际检查并报告；只有真实资料或适用授权缺口阻断时才停止对应分支。
```

### 兼容源替换任务示例

```text
读取目标模型的source合同和实际ModuleDescriptor。
先判断所给新源是否是兼容替换，以及run/selection是否同步需要更改。
新增源实现并通过真实predict入口接入；保留旧模型实例。
执行合同、归一化、能量态对齐和相关回归，重建含源的Fast核或报告不支持。
不把新源硬命名为mu/e/mub来绕过旧接口。
```

### 接口审阅任务示例

```text
根据09核对实际模块合同和依赖图，选择一个 source 或 efficiency 实例替换。
验证单位、坐标、归一化一次、双实例隔离，以及含依赖的 Fast 模板失效。
保留原模型，使用同一 predict 入口；报告实际能力和可审阅差异。
```

这些任务文本需与用户实际提供的范围和材料结合；不填入不存在的文件或批准记录。
