# 外置实验资源

ResourceCatalog.root 是包含data/的根；安装包不含这些文件。无cwd搜索，无隐式outputs或workflow输入。

| 家族 / dataset_id | 内容 |
|---|---|
| COHERENT_CsI/CsI2017 | detector效率表、statistics四份原表及显式坐标schema |
| COHERENT_CsI/CsI2021 | 原spec/provenance；当前九箱观测内联定义保持唯一来源 |
| COHERENT_Ar/Ar2020 | detector效率表、原provenance；十二箱观测内联定义 |

共享核响应保持responses/responses_all.json，不复制到每实验。datafiles中其他尚未迁移资源保留，
不根据文件名推断其科学用途或删除。data与包内experiments通过逻辑资源ID/合同相连，不合并目录。

旧六份COHERENT表及旧spec/provenance路径由foundation/resources.py的有限ALIASES兼容。
规范与旧路径同时存在且字节内容冲突会报错；不使用symlink，不维护两份可独立修改的权威表。
规范迁移的旧/新路径、哈希和所有者见 [资源清单](resource_manifest.json)。

CsI2017坐标是各role原数字化x，按显式schema逐行绑定25个原箱；不是重插值后的新观测。
单位、顺序、重复坐标、箱宽、分析/profile身份均检查。真实资源缺失时明确报缺失，不用synthetic观测替代。
