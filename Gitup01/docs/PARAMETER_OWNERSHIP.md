# 实验参数归属（工程迁移）

权威定义位于 `cevns_pyeft/experiments/*/*_definition.py` 和
`conus_plus/definition.py`。旧常量是定义的派生兼容出口。资源内容本身仍由原文件拥有。
数据只按明确映射迁移，原字节不变；不改理论公式、原参考或科学Gate。实际组件替换覆盖定义默认值，并进入装配身份。

用户切换已有实验时，给 `load_experiment(dataset_id)` 传入对应ID。四个实验的默认设定分别从以下文件进入：

| 实验ID | 默认设定的权威入口 | 外置数据目录 |
|---|---|---|
| CsI2021 | [csi2021_definition.py](../cevns_pyeft/experiments/coherent/csi2021_definition.py) | COHERENT_CsI/CsI2021（外部资源：`../data/experiments/COHERENT_CsI/CsI2021/`） |
| CsI2017 | [csi2017_definition.py](../cevns_pyeft/experiments/coherent/csi2017_definition.py) | COHERENT_CsI/CsI2017（外部资源：`../data/experiments/COHERENT_CsI/CsI2017/`） |
| Ar2020 | [ar2020_definition.py](../cevns_pyeft/experiments/coherent/ar2020_definition.py) | COHERENT_Ar/Ar2020（外部资源：`../data/experiments/COHERENT_Ar/Ar2020/`） |
| conus_plus_2025_c2c3c5_ge73_pyeft | [conus_plus/definition.py](../cevns_pyeft/experiments/conus_plus/definition.py) | [CONUS_Plus/Ge73候选](../data/experiments/CONUS_Plus/conus_plus_2025_c2c3c5_ge73_pyeft/) |

definition拥有本实验的默认源/运行期、靶材、响应、曝光、分箱、统计和数值配置，并绑定所需资源。
算法实现由公共模块及明确的专用执行器拥有；谱表、效率表和外部观测由data文件拥有。
这些文件通过资源ID和组件接口连接。修改单个实例时用 `dataclasses.replace` 或 `components` 覆盖，
不修改其他实验的定义或全局常量；具体方法见 [使用与替换](USAGE.md)。

| 量 / 语义及单位 | 权威来源 | 实际消费者 / 兼容出口 | 失效范围 |
|---|---|---|---|
| SNS L[m], POT, 每 POT 产额、源质量元数据、谱支撑/插值节点 | 各 COHERENT definition 的 run | SNS source / SNS_DATASETS | 源积分与物理核 |
| CsI2021 实际质量 14.57 kg、Cs133:I127 133:127 | csi2021_definition physical | make_csi2021_model / inventory | 计数与核 |
| CsI2017 有效质量 14.6 kg（源元数据14.57不同） | csi2017_definition physical | 参数化 deterministic executor / Slow及Fast | 计数与核 |
| Ar2020 24 kg、Ar40 | ar2020_definition physical | 参数化 Gaussian executor / Slow及Fast | 计数与核 |
| CsI淬灭四项式、gamma a/b、logistic效率、味接受率 | csi2021_definition physical | CsIGammaResponse / CsI2021Efficiency / observation | 折叠与核 |
| CsI2017 PE/keV=1.17、Jacobian、阈值4.9、效率列0/1及low | csi2017_definition physical + COHERENT_eff.txt | deterministic folding / legacy常量 | 折叠与核 |
| Ar均值(0.246+0.00078T)T、sigma依赖观测x、效率列0/2 | ar2020_definition physical + CENNS10AnlAEfficiency.txt | Gaussian folding / Slow及Fast | 折叠与核 |
| 各实验轴/单位/分箱 | 各 definition observation | Prediction及统计转换 / bins常量 | 折叠、核、统计身份 |
| COHERENT观测/背景/误差、nuisance | 各 definition statistics；CsI2017 text资源 | 绑定统计loader / datasets兼容出口 | 仅统计，不重建物理核 |
| CONUS源总通量[cm^-2 s^-1]、支撑、拼接、状态 | conus_plus definition physical | 显式 Reactor source 实例 / source常量 | 率积分；响应矩阵不含源 |
| Kopeikin节点、Mueller系数及裂变份额 | 原 source/*.csv 内容 | content-keyed源表实例 | 源率积分 |
| CONUS Ge73核数/kg、86400秒/day | conus_plus definition physical | rate[kg^-1 day^-1 keV^-1] executor | 率与计数 |
| C2/C3/C5各119 kg·day | conus_plus definition MassTimeExposure | 每探测器响应折叠 | 响应矩阵与计数 |
| Lindhard、分辨率、阈值[eVee] | conus_plus definition physical | detector_response 显式配置 | 响应矩阵与计数 |
| CONUS统计19箱、sigma_alpha .169 | conus_plus definition statistics + digitized CSV | effective119专用绑定（仅C3=119） | 仅统计；357配置拒绝评价 |
| 数值默认及合法覆盖键 | 各 definition numerical_profiles | runtime校验、专用executor | 数值依赖的核 |
| 复现 sin²θW（COHERENT .2387；CONUS .23857） | 各 definition reproduction default | parameters=None；显式TheoryPoint优先 | 单点预测，不改变参数无关核 |

CsI2017 Slow保留251点；旧n_er/n_pe_bin/pe_step无效，统一入口拒绝这些键。
Ar2020旧pe_step无效，统一入口拒绝。Fast能力按实际表示分别发布，
旧矩阵核不宣称具备新物理指纹。

Refactor03：共享CsI配方归targets/recipes.py；具体运行设定仍各自拥有。
CONUS核数/kg与kg·day由MassTimeModel分别消费；RecoilRate标记events/(kg day keVnr)，不冒充RecoilYield。
坐标与观测schema位于所属data/statistics目录；统计内容/误差只影响评价记录。
纯响应矩阵只依赖实际探测器、曝光、反冲网格和分箱；源强/截面改变且网格未变时无需重建该矩阵。
