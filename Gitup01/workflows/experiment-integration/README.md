# experiment-integration：保留的历史实验接入记录

当前工作流权威入口已经迁到 [workflows/README.md](../README.md)。本目录只保存旧的运行证据、进度和授权，不包含活动 router、政策或 Skill 定义。

## 现有记录怎样使用

[runs/Solar_B8/](runs/Solar_B8/) 保留两个独立 dataset 的输入清单、implementation manifest、进度、来源登记、证据、物理合同及授权日志：2024 paper-approx 与 2026 public-template。记录中的旧资料路径按当时来源解释；当前 `docs/experiments/` 已整理为 COHERENT 文档，恢复前需核对旧资料的实际位置。

这些记录说明当时读过什么、缺少什么、允许做什么；不是活动实验注册。恢复工作时由 Master 核对唯一当前索引、revision、来源和有效授权，不能因旧文件存在直接继续写 runtime。

## 为什么独立保留，怎样新增

旧路径和原始记录字节与证据/授权指纹相联系，因此不应为了新目录说明而改写它们。新的工作流规则放 `workflows/cevns-pyeft/` 或 `_shared/`，不要在这里增加新的 SKILL/route 副本。

新的 dataset 运行记录应由当前 Master 按已批准的目录身份创建；明确续接这里的旧 dataset 时，先完成索引和授权核对，再按有效写入范围更新。不要把旧记录复制成“新获批”运行，也不要用这里的状态反推当前 Catalog 已启用该实验。

---

[上一级](../README.md) · [项目总览](../../README.md)
