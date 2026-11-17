# 取得的原始材料

全部来源身份、直接路径、原始网址与指纹由 [P00](../P00_SOURCE_REGISTER.yaml) 唯一登记。此处展示实际取得情况。

| 材料 | 实际文件与核验范围 |
|---|---|
| COHERENT原始数据 | [official/](official/README.md) 包含官方ROOT、C/AC事件、BRN/NIN四表、效率与淬灭系数和Supplement。原始下载位置为2110.07730v2 ancillary，当前拷贝与既有官方下载指纹一致 |
| NIST物理常数 | [CODATA2022原始ASCII表](NIST_CODATA2022_allascii.txt)，muon/electron质量、原子质量单位能量和G_F的具体行值在P01登记 |
| pion质量 | [PDG2024原始listing](PDG2024_pi_charged.pdf)，p1 OUR FIT已视觉核对 |
| 核结构候选上游 | [upstream_nuclear](upstream_nuclear/README.md) 保存作者Elastic密度矩阵与Mu2e_NRET固定提交源码、ZIP和SHA。它们与本地JSON的生成对应尚未证实 |
| 导入及下载记录 | [原始数值拷贝](IMPORT_MANIFEST.json)、[常数原始下载](CONSTANTS_DOWNLOAD.json) |

采用的 RESPONSE 直接数值来源是主项目原 [data/responses/responses_all.json](../../../../../../../data/responses/responses_all.json)，按用户补充直接调用。外部候选材料不替换该文件的来源身份。

测量与校准PDF在主项目唯一文献库保存，P00给出实际路径。主要原始发布入口为 [COHERENT官方数据页](https://sites.duke.edu/coherent/data/)、[2110.07730v2](https://arxiv.org/abs/2110.07730v2)、[2211.11905v2](https://arxiv.org/abs/2211.11905v2)、[2111.02477v2](https://arxiv.org/abs/2111.02477v2)。

[上一级](../README.md)
