# 外部资源与格式约定

Status: CURRENT
Scope: 显式资源根、资源归属和机器格式说明。

ResourceCatalog.root 指向包含 data 的目录。数据与运行包分离；安装 wheel 后由调用者显式提供资源根，不扫描当前工作目录或 outputs 寻找输入。
[资源清单](../../data/resource_manifest.json)记录逻辑资源、规范路径和哈希；[资源审计工具](../../tools/validate_resource_manifest.py)检查现有清单。

共享核响应位于 data/responses，实验效率、观测和溯源位于所属 data/experiments。覆盖共享资源可使用裸资源 ID；同名实验专属资源使用 (dataset_id, resource_id) 作用域。有限旧路径兼容由 [resources.py](../../cevns_pyeft/foundation/resources.py)实现。

[根 schemas](../../schemas/README.md)描述实验配置和数据表格式；[工作流 schemas](../../workflows/_shared/schemas/)描述证据与授权记录。现有实验说明加载器使用 Python 检查，不能把 JSON schema 文件的存在解释为所有规则已自动执行。

当前内置实验资源属于 CsI2017、CsI2021、Ar2020；具体来源与用途见 [data/README](../../data/README.md)。
