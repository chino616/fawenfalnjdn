# 实际数值数据与来源映射

| 文件 | 具体数据与直接来源 |
|---|---|
| [nuclear_response_CsI.npz](nuclear_response_CsI.npz) | 原共享JSON的Cs133/I八通道，合计16个2×2×K系数数组，逐值提取供阅读和一致性核验。实际调用仍使用原JSON，来源P00的S_LOCAL_W |
| [nuclear_response_inventory.json](nuclear_response_inventory.json) | 各数组的原始JSON key、shape、升幂范围、轴顺序、指数因子、前三项系数和核素元数据 |
| [analysis_inputs.npz](analysis_inputs.npz) | PE/time边界、C/AC/SS 9×11矩阵、四味ROOT时间/能量边缘和完整轴边界 |
| [ROOT_inventory.json](ROOT_inventory.json) | 官方ROOT各TH2F对象、完整轴域、实际代表箱、权重总和及0–6μs分数 |
| [observed_99bins.csv](observed_99bins.csv) | 官方C/AC逐事件文件的项目重分箱，以及AC指数时间模型推导的SS。轴为PE/time，单位events/bin |

逐数组到来源、单位、变换和核验范围由 [P01](../P01_EVIDENCE_LEDGER.yaml) 管理。原始文件在 [sources](../sources/README.md)。本轮仅从原始文件读取/提取，核响应系数的数值由原共享JSON拥有，提取文件保持完全一致。

计数重分箱规则为用户指定PE边界和2211 Fig.18时间边界，左闭右开。来源证据C_PE/C_TIME/C_ENDPOINT_RULE和直方图算法在 [prepare_records.py](../prepare_records.py)，完整C/AC矩阵也展示在详细Physics文档中。

[上一级](../README.md)
