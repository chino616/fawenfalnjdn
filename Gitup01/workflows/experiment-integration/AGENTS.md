# CEvNS Experiment Integration — Agent Router

本目录只有一个 workflow 总入口：

```text
skills/cevns-experiment/SKILL.md
```

当用户要求新增/迁移/继续 CEvNS 实验、从论文接入实验、实现 Slow/Fast/statistics，或测试实验集成 Skill 时：

1. 先读取 `_shared.md`；
2. 再读取 `skills/cevns-experiment/SKILL.md`；
3. 由 Master Skill 决定下一阶段；
4. 不允许从 AGENTS.md 自行推断 dataset 或跳入某个 Phase；
5. 不允许绕过 Master Skill 直接把本地文献、占位目录或旧代码解释成用户批准的 physics scope。
6. 不允许在用户批准 `[WRITE PLAN]` 前创建 `.onboarding_tmp`、mock 文件、正式 run、data、src、tests 或 registry 修改。隔离自动候选只能按 `AUTO_RUN_PROTOCOL.md` 的带 `plan_id` 启用授权写到原项目之外；导入原项目仍需审核并准确批准。
7. 必须执行 `_shared.md` 的 `BACKUP_QUARANTINE`：`backup/**` 不参与材料扫描、候选计数、证据抽取、dataset 判定、迁移输入、repository map 或验证；只有显式的备份写入、恢复或审计请求可以访问它。

子 Skill 只负责自己的物理阶段；workflow 顺序只由 `cevns-experiment` 决定。
用户要求进入低自动或高自动时，Master 先读取 `AUTO_RUN_PROTOCOL.md` 并展示警告与
计划；“切换模式”请求本身不授权写入，也不使正式 Human Gate 自动通过。
