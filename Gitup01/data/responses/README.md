# data/responses：共享核响应数值表

[responses_all.json](responses_all.json) 是当前共享核响应输入。三份 COHERENT definition 通过逻辑资源 ID `responses` 指向它，`Li2026LegacyInteraction` 使用 [ResponseDB](../../cevns_pyeft/nuclear/response.py) 加载，再按核素和通道取 W 矩阵。

## 文件怎样被解释

顶层 `nuclei` 保存核素；每个核素含 `basic`、`exp_factor` 和 `responses`。响应条目是多项式系数列表或由这些列表组成的 2×2 矩阵，求值规则为 `exp(exp_factor*y) × poly(y)`。元数据声明 `np` 基，矩阵顺序为 `(p,n)`；内部 `iso` 结果由代码变换得到。

核表只提供单核响应，不含 CsI 材料质量分数、曝光、源谱或探测器效率。多个实验共享同一文件，因此改变表内容会影响所有使用它的物理身份和 Fast 核。

## 管理与新增文件

已有表按来源证据维护，不为匹配期望事件数直接调整系数。新增独立响应表时，在本目录创建清楚标识来源/版本的 JSON，提供核素键、基底、单位、通道和转换来源；通过 definition 的 `responses` 资源或 `ResourceCatalog` 覆盖显式选择。

随后用 `ResponseDB` 检查结构、核素和通道，核对 interaction 的 response key 映射，同步资源清单的哈希并检查已有实验回归。新文件不会被自动扫描或拼接进原表。外部源表和生成过程的审计仍未闭合；内部结构检查不代表外部来源与归一化已确认。

---

[上一级](../README.md) · [项目总览](../../README.md)
