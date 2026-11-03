# archive-isolation

## 9. BACKUP_QUARANTINE

`backup/**` 是只用于恢复的隔离区，不属于 experiment-integration 的 physics
workspace。Master、onboarding 和所有 Phase 均不得自动扫描或读取其中内容，也不得
把它用于：

```text
material discovery
candidate list / candidate_count
dataset identity / existing_dataset detection
evidence ledger / scientific claim
repository map / migration input
reference arrays / validation baselines
```

只有以下操作可以访问 `backup/**`：

1. 按仓库规则创建或登记备份；
2. 用户明确要求恢复或审计备份。

即使用户明确要求读取备份，读取结果也只具有 recovery/audit 身份，不自动成为
physics evidence、dataset candidate 或迁移输入。若要把恢复内容重新接入实验流程，
必须将其恢复到非 `backup/**` 路径，并重新经过 Master Skill 的 scope、identity、
scientific claim 和 write gates。
