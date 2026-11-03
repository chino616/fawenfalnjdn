# data：运行时显式读取的外置输入

`ResourceCatalog.root` 是包含本目录的根，不是 `data/` 本身。[loader.py](../cevns_pyeft/experiments/loader.py) 遍历实验 definition 的 `resources`，用资源 ID、role 和路径解析文件。物理输入在加载时读取/记录 SHA256；统计资源延迟到评价阶段使用。

| 子目录或文件 | 实际用途 |
|---|---|
| [responses/](responses/README.md) | 共享 `responses_all.json`，三个活动实验均通过 `responses` 资源 ID 使用 |
| [experiments/](experiments/README.md) | 按实验族/dataset 保存效率、观测表、坐标 schema、spec 与来源说明 |
| [datafiles/](datafiles/README.md) | 保留其他谱表与旧资料；当前 COHERENT 主路径并不按名称自动读取它们 |
| [resource_manifest.json](resource_manifest.json) | 供资源审计使用的规范路径、有限旧路径、SHA256、资源归属与坐标合同；不代替 definition 中的绑定 |

## 为什么与 Python 包分开

安装 wheel 后，代码位置和数据位置可以不同；调用方显式指定资源根即可。共享核表保留一份，实验独有数据各自归档，避免不同实验同名 `efficiency` 被混用。outputs 和 workflows 不作为隐式输入。

单实验可覆盖资源 ID；多实验同名且不同路径的资源要用 `(dataset_id, resource_id)` 作用域。旧六份 COHERENT 表与 spec/provenance 的路径只通过 [有限 ALIASES](../cevns_pyeft/foundation/resources.py) 兼容。旧/新文件同时存在且内容冲突会报错。

## 管理与新增文件

1. 确定数据归属、来源、单位、坐标和是否已经包含效率/曝光。真实新数据集按实验接入流程确认范围。
2. 独有输入放 `data/experiments/<实验族>/<dataset_id>/detector/`、`statistics/` 等职责子目录；共享核表放 `responses/`。文件名表达物理量和版本，具体命名由该数据集说明记录。
3. 在 definition 新增/更新 `ResourceRef(id, path, role, semantic)`，让 `prepare` 或统计 loader 实际消费它。资源清单同步登记路径和真实内容哈希，必要时绑定坐标 schema。
4. 从根目录运行 `python tools/validate_resource_manifest.py --root .`，再检查受影响预测、统计或缓存失效。

不手工编辑生成结果当作原始观测，不为通过回归改变数据或冻结参考。CsI2017 的数字化坐标按原 schema 逐行绑定；CsI2021 九箱、Ar2020 十二箱的当前观测仍内联在各自 definition，不能另建 CSV 后假设程序会改用它。

---

[上一级](../README.md)
