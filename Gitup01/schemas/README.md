# 数据契约

`experiment.schema.json` 给出通用实验配置的最小 JSON Schema。

CSV 契约集中在 `csv_contracts.json`。验证脚本主要检查：

- 文件是否存在；
- 列名；
- 分箱递增；
- 丰度与裂变份额和；
- publication 核心表是否仍有空单元格或 `REQUIRES_INPUT`。
