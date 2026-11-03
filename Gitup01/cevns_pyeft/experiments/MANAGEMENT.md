# Dataset 完整管理链

从 [DATASETS.md](DATASETS.md) 查看全部实验、dataset ID、安装/活动状态、版本、代码和数据归属。唯一登记数据保存在 [dataset_registry.json](dataset_registry.json)，[manifest.py](manifest.py)提供兼容 Python 视图，[catalog.py](catalog.py)继续负责运行时身份解析。

## 从哪里执行

在包含 `cevns_pyeft/` 和 `data/` 的管理根目录，使用具备项目依赖的 Python：

```powershell
python -m cevns_pyeft.cli datasets list
python -m cevns_pyeft.cli datasets show CsI2021
python -m cevns_pyeft.cli datasets audit
```

安装项目后也可以用 `cevns-pyeft datasets ...`。管理其他检出/解压目录时，把全局参数放在子命令前：

```powershell
python -m cevns_pyeft.cli datasets --root F:/path/to/managed-root list
```

本工具管理这个明确根目录内的 dataset 文件，不调用 pip 卸载整个 CEvNS-pyEFT，也不搜索其他工程或备份。wheel 包含 registry 资源，实验 data 仍按现有规则外置提供；需要实际拆装时使用可写的管理根目录，不对另一位置的外部 data 隐式操作。

## 一键导出、卸载与重装

```powershell
# 导出当前已安装实验的独占代码、data 和声明
python -m cevns_pyeft.cli datasets export CsI2021 --output outputs/dataset-management/packages/CsI2021.zip

# 默认只展示计划：列出将增、删、改的准确文件与前后哈希
python -m cevns_pyeft.cli datasets uninstall CsI2021

# 明确执行；自动备份，并生成可以重装的包
python -m cevns_pyeft.cli datasets uninstall CsI2021 --apply

# 安装后默认 archived，仍会在隔离子进程验证该 definition 的 Slow 合同
python -m cevns_pyeft.cli datasets install outputs/dataset-management/packages/CsI2021.zip --apply

# 需要安装并启用时显式加 --activate
python -m cevns_pyeft.cli datasets install outputs/dataset-management/packages/CsI2021.zip --activate --apply
```

两条 install 命令是不同使用选择，不能对已经安装的同一 ID 连续安装。共享依赖的 API/内容不兼容、包损坏、文件归属冲突、目标文件已存在时会拒绝；不覆盖用户文件。包内所有 payload 都校验哈希，禁止路径越界、重复成员和 symlink。

卸载只删除 `owned_files` 中明确列出的普通文件，并清理实际变空的所属目录。共享核响应、物理库、用户额外存放的文件和历史证据会保留；不会递归删除一个实验文件夹来猜测归属。卸载保留未安装的身份记录：`installed=false, status=archived`，因此能够区分“从来没有这个 ID”与“已卸载”。

导出包包含版本、核心 API 要求、独占文件哈希、共享依赖哈希和该实验的资源登记。SHA256验证完整性，不作为来源签名或物理审核。引入新科学含义的实验仍按 onboarding 和科学审核接入，管理命令不替代这些决定。导出/安装不会自动将上一次运行的 selection 配置设为 enabled。

## 保存计划再执行

```powershell
python -m cevns_pyeft.cli datasets uninstall CsI2021 --plan outputs/dataset-management/plans/uninstall-csi.json
python -m cevns_pyeft.cli datasets apply outputs/dataset-management/plans/uninstall-csi.json
```

保存的计划包含根目录、对象、包哈希、依赖/文件前置条件和准确变更。执行时从当前唯一登记重新生成计划，逐项一致才执行；计划过期或被编辑时要求重建。保存计划本身只创建用户显式指定的计划文件；不添加 `--plan` 的只读查询不会创建事务/备份。

## 归档、启用与本次运行开关

```powershell
python -m cevns_pyeft.cli datasets archive CsI2021 --apply
python -m cevns_pyeft.cli datasets activate CsI2021 --apply
```

`archive` 保留文件并阻止默认 Catalog 加载；`activate` 要求文件已安装，并在验证成功后保留活动状态。归档/卸载会把根 `configs/*.yaml` 中该 ID 的 `enabled: true` 改为 false；启用/重装不会覆盖用户后续的运行选择。只有要更改本次计算组合时才修改 selection 的 enabled，详情见 [configs](../../configs/README.md)。

活动资源清单仅保留 active dataset；归档/卸载时移除该项资源登记，启用/重装时根据同一 registry 中保存的资源声明恢复。共享文件本身不随活动资源条目移除。

## 事务、验证、回滚与中断恢复

每个执行操作按同一顺序完成：

1. 核对最新计划、文件归属、包版本、依赖和反向的顶层代码导入，取得根目录操作锁。
2. 在新进程计算当前活动实验的小网格 Slow/统计基线，并检查兼容导入。
3. 保存所有将改写/删除文件的原始字节，记录备份和 PREPARED 日志；卸载同时生成重装 ZIP。
4. 按准确文件执行原子替换或单文件移除，同步 registry、活动资源、selection、用户清单、受影响文档链接及准确的保护哈希。
5. 再次做依赖/资源审计和新进程检查；比较不受影响实验的预测、轴、单位和 χ²。安装的候选即使保持 archived，也通过单独的验证 Catalog 检查，不改变其正式状态。
6. 全部通过才记为 COMMITTED；失败则恢复旧字节。恢复遇到用户后续编辑或备份损坏时报告 RECOVERY_REQUIRED，并保留证据，不能覆盖这些变化。

基线使用小网格验证接口和剩余实验等价，不宣称物理收敛。共享物理代码重构仍须通过项目完整数值回归；管理操作没有修改模型公式或冻结参考的权限。

执行结果给出 transaction_id、journal 路径和自动重装包路径：

```powershell
python -m cevns_pyeft.cli datasets history
python -m cevns_pyeft.cli datasets rollback <transaction_id>
python -m cevns_pyeft.cli datasets recover <transaction_id>
```

事务记录位于 `outputs/dataset-management/transactions/<transaction_id>/`，原文件备份位于 `backup/dataset-management/<transaction_id>/`，每次备份追加到 `backup/BACKUP_MANIFEST.md`。只在明确管理/恢复该事务时读取相关备份，不把备份作为实验输入。

`rollback` 在所有目标和依赖前置条件仍匹配时恢复操作前的字节，并验证恢复结果；有连续操作时按相反顺序回滚。回滚验证失败也会恢复回滚前的状态并报告失败。`recover` 面向中断的 PREPARED/ROLLING_BACK 事务：先确认原进程已经退出，才处理遗留锁和恢复；不会打断存活进程，也不会把已经完成的 COMMITTED 事务当作未完成而撤销。尚未开始写入的 PREPARING 事务可标为 ABORTED_NO_WRITES。

完成管理后重新启动或重新导入正在使用旧 Catalog/缓存的长驻进程。命令的新进程验证不等于自动替换其他 Python 进程里已有的模型对象。

## README 与文件归属维护

[DATASETS.md](DATASETS.md)在事务内由 registry 生成，未安装文件显示为普通路径。其他当前 Markdown 对将删除文件的链接会暂时显示“该 dataset 未安装”，原始链接保存在明确的 `dataset-link` 标记中；重装时恢复。人工正文、代码块与历史结果不整篇覆盖。

新增 dataset 包需声明唯一 ID/别名、definition、package_version、capabilities、owned_files、shared_dependencies、requires_datasets、资源和验证要求。需要固定其他 dataset 的版本时，另用 `required_dataset_versions` 映射声明精确版本。独占路径不能覆盖核心管理文件、其他包的文件或共享依赖。新增/改名/删除能力同时维护其目录 README、上级索引、真实消费者和检查，遵循[文件联动规则](../../workflows/_shared/policies/file-lifecycle.md)。

共享算法不属于某个 dataset 的卸载单元：例如 Cs:I 化学计量组合在 `targets/materials.py`，可复用的 CsI 响应和 SNS 默认组件参数分别在 `detectors/legacy_parameters.py`、`sources/legacy_parameters.py`。专用 definition/Slow/Fast 包通过延迟入口消费这些公共能力，避免卸载一个数据集破坏其他数据集的导入。

未请求的用户文件、裸文本中的示例、历史报告和动态反射代码不能靠链接扫描自动判定语义；清单与审计明确报告覆盖范围，剩余实验由真实新进程检查验证。

[注册与安装清单](DATASETS.md) · [代码目录](README.md) · [项目总览](../../README.md)
