# workflow_validation：工作流检查使用的机器配置

可执行检查器位于 [workflows/cevns-pyeft/qa/validate_skill_pack.py](../../workflows/cevns-pyeft/qa/validate_skill_pack.py)；本目录保存它读取的配置，避免把程序依赖混入历史审计文档。

| 文件 | 检查器怎样使用 |
|---|---|
| [config/PROTECTED_FILES.json](config/PROTECTED_FILES.json) | `protected_errors` 逐项核对 SHA256，并枚举 `cevns_pyeft/data/configs/examples` 与 `workflows/_shared/schemas/experiment-input`，报告未登记新增项 |
| [config/HISTORICAL_PATH_EXCEPTIONS.json](config/HISTORICAL_PATH_EXCEPTIONS.json) | 识别允许保留的历史定位符，不把它们误认成新的活动路径 |
| [config/README.md](config/README.md) | 配置格式、来源及消费者说明 |

## 为什么 README 也需要管理

当前保护逻辑按文件枚举，而非只检查 `.py` 或数据后缀。因此在上述受保护目录增加 README、修改已有 README 也会触发保护差异。这是管理清单的一致性检查，不是物理数值测试。

## 新增和变更规则

配置使用 JSON，由维护任务显式修改。对已经授权、经审阅的纯文档变化，只登记对应 README 的真实 SHA256 和新路径；保留代码、数据、schema 内容、冻结参考等其他项的既有哈希，不把失败批量“更新为当前值”。

新历史路径例外需说明它属于哪份原始证据及为何不能改写；不要用例外掩盖活动文档断链。新增配置文件还必须更新检查器中的明确读取逻辑和配置缺失测试，单独创建 JSON 不会被自动消费。

从项目根目录检查：`python -B workflows/cevns-pyeft/qa/validate_skill_pack.py` 和 `python -B -m unittest discover -s tests/workflows -v`。相关测试会确保配置缺失时报错，而非回退旧目录。

---

[上一级](../README.md) · [项目总览](../../README.md)
