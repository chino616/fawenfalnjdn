# dataset-layout

## 8.1 PER_EXPERIMENT_DATASET_DIRECTORY

每个正式 dataset 使用“可读实验目录 + 唯一 dataset 子目录”的两级隔离：

```text
<experiment_slug>/<dataset_id>/
```

三个身份字段不得混用：

```yaml
experiment_name: "供文档和用户界面显示的正式实验名称"
experiment_slug: "稳定、可读、文件系统安全的实验目录名"
dataset_id: "程序、registry 和 Physics Gate 使用的唯一数据集标识"
```

`experiment_slug` 应清楚表达实验，例如 `CONUS_Plus`、`COHERENT_CsI`，并只使用
ASCII 字母、数字、下划线或连字符。同一实验的多个 dataset 可以共用
`experiment_slug` 父目录，但每个 `dataset_id` 必须有独立子目录；不得混放 evidence、
decision、数据表、cache、阶段报告或验证结果。

新 dataset 的规范目录为：

```text
docs/experiments/<experiment_slug>/datasets/<dataset_id>/
workflows/cevns-pyeft/runs/<experiment_slug>/<dataset_id>/
physics_docs/experiments/<experiment_slug>/<dataset_id>/
data/experiments/<experiment_slug>/<dataset_id>/
```

通用模板仍只保存在 `workflows/_shared/templates/`，不得写入任何实验
专属值。正式目录只能在 Dataset Identity、`experiment_slug` 和 Scope Gate 获批，且
对应 `[WRITE PLAN]` 获得 `APPROVE WRITE` 后创建。

已有平铺目录属于 legacy compatibility。不得仅因本规则自动移动或重命名；迁移时必须
在 implementation manifest 中登记旧、新路径，并为移动、loader/registry 更新和回归
验证单独取得写入批准。
