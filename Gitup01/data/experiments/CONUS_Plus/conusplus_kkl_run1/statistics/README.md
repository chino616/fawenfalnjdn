# CONUS+ 图 1 数字化观测

直接来源为 arXiv:2501.17843v3 PDF 第 10 页图 1。19 个中心和上下误差由 PDF 向量提取，原图单位为 counts kg^-1 (10 eVee)^-1。

| 文件 | 用途 |
|---|---|
| [CSV](conusplus_2501_17843v3_fig1_digitized.csv) | 有符号中心值、上下误差、候选均值及箱边界 |
| [来源与坐标记录](conusplus_2501_17843v3_fig1_digitized.provenance.json) | 原图位置、坐标标定、单位和每点向量路径 |
| [叠加核对图](conusplus_2501_17843v3_fig1_digitized.overlay.png) | CSV 与原图的叠加 |
| [取点脚本](digitize_fig1.py) | --check 只读重提取与指纹核对 |

上下误差均保留。算术平均列是候选统计约定，拟合前按 P02 审阅。

[数据集来源映射](../PROVENANCE_MAP.json) · [数据集入口](../README.md)
