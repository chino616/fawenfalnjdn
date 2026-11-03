# Phase / capability 实际报告

复制此模板到已获授权的记录位置；不要把已填写结果写回通用模板。
P04–P10 按 [执行合同](../../references/phase/PHASE_EXECUTION_CONTRACT.md)填写。
P01–P03 继续使用其原阶段字段；下面的结构化 phase-result 块仅用于 P04–P10。

## 范围、输入与决定
- 对象/dataset、capability_id、当前 revision、原目标：
- 本阶段所需上游合同、版本/指纹与有效批准：
- 来源、抽取/推导/假设、缺失与冲突：
- 已有决定引用；本次新增物理选择及实际用户回复：
- 实施授权和精确文件范围（已有授权直接引用）：

## 实际实现与结果
- 复用/配置/adapter/共享扩展判断：
- 实际文件::symbol、调用链、公式、单位、轴、适用范围：
- 输入与归一化因子的 owner：
- 创建/修改文件及备份：
- 实际数值、图表、差异、精度与限制：

## 验证
- 预定验收条件、实际命令和结果文件：
- 内部一致性/旧程序回归/论文 forward/官方 likelihood 分别达到的程度：
- 未运行项及原因；受影响下游与缓存：

## 结构化交接记录

只保留一个标为 `json phase-result` 的块，按当前阶段替换 phase/capability_id 和 handoff。
空值用于草稿，不可据此声明 PASS。decision_refs 是预先的物理决定，
approval_refs 是用户对当前结果的接受。checks 的 result_ref 指向 artifacts 中的 path。
artifacts 使用项目或隔离工作区根目录下的相对路径及实际 SHA256。

```json phase-result
{
  "schema_version": 1,
  "phase": "P04",
  "capability_id": "replace-with-current-capability",
  "workspace": "canonical",
  "plan_status": "DRAFT",
  "machine_gate": "NOT_RUN",
  "human_gate": "NOT_REVIEWED",
  "scope_ref": "",
  "input_refs": [],
  "input_fingerprint": null,
  "evidence_refs": [],
  "decision_refs": [],
  "approval_refs": [],
  "artifacts": [],
  "checks": [],
  "handoff": {}
}
```

对 PASS 的 checks，填写 name、status、command、result_ref；
artifacts 每项填写 path、sha256、role。具体 handoff 字段见当前阶段模板。
正式结果须保留可回溯的批准；候选 workspace 使用 isolated_candidate，不可人工 APPROVED。
使用 [合同校验器](../../../cevns-pyeft/qa/validate_phase_contract.py)检查结构，必要时核对文件哈希；
校验不能认证科学内容或批准真实性。

## 返回 Master
- 交付能力、允许声明和未满足目标：
- 建议下一动作与实际依赖；需回填字段及 owner：
- 权威记录已写入位置；Master 更新 checkpoint 的条件：
