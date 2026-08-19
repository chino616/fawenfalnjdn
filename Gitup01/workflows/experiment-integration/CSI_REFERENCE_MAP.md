# CsI 逐模块参考地图

本文件只说明“新实验的某个模块应该参考 CsI 的哪一小部分”。  
路径变更时，以当前仓库的 import graph 和测试为准。

| 新实验模块 | 优先读取的 CsI/通用文件 | 只检查什么 | 不得复制什么 |
|---|---|---|---|
| Dataset/registry | `src/cevns_pyeft/experiments/base.py`；`src/cevns_pyeft/experiments/registry.py`；`data/experiments/*/experiment.yaml`；`schemas/experiment.schema.json` | spec 加载、dataset ID、callable 注册、返回 shape 元数据 | CsI 数据集 ID 和参数 |
| Source | `src/cevns_pyeft/experiments/coherent/` 中被 `slow_counts_csi2017.py`、`slow_counts_csi2021.py` 导入的 SNS source helper | component API、flavor 标签、归一化和时间基准 | SNS prompt/delayed 谱 |
| Target | `slow_counts_csi2017.py`、`slow_counts_csi2021.py` 中 Cs/I 分量；`src/cevns_pyeft/nuclear/response.py` | 核数、同位素/化学计量、Response key、component axes | Cs/I 的丰度和摩尔质量 |
| Theory/Response | `src/cevns_pyeft/theory/li2026/`；`src/cevns_pyeft/nuclear/response.py` | Wilson basis、Response contraction、现有理论覆盖 | 在实验模块重写振幅 |
| Kinematics/cross section | `src/cevns_pyeft/rates/differential.py` | 能量单位、运动学 mask、`dσ/dT` 输出单位 | CsI 的积分上下限或近似 |
| Detector response | `slow_counts_csi2017.py`、`slow_counts_csi2021.py` 及其导入的 detector helper；`src/cevns_pyeft/rates/counts.py` | true recoil 到观测量、response folding、efficiency domain、binning | CsI quenching、PE 展宽、时间结构 |
| Slow counts | `slow_counts_csi2017.py`、`slow_counts_csi2021.py`、`slow_counts_ar2020.py` | public API、分量保存、积分顺序、返回 shape、reference test | 整个 CsI slow 文件 |
| Fast | `fast_kernel_csi2017.py`、`fast_kernel_csi2021.py`、`fast_kernel_ar2020.py`；`kernels/basis.py`、`builder.py`、`reconstruction.py`、`storage.py` | 实验 wrapper 与通用 kernel 的边界、存储格式、逐 bin 重构 | CsI 预计算数组或参数 |
| Statistics | 先检查当前仓库是否存在通用统计层和该 CsI 数据集的数据定义 | data mode、covariance、nuisance 和 test statistic | 假定所有实验使用 CsI likelihood |
| Validation | CsI Slow/Fast check notebooks、`tests/reference_fast_split/`、拆分前后 reference tests | 逐 bin 对比、返回 shape、容差和 provenance | 更新 reference 掩盖差异 |

## 参考顺序

每个 Skill 应按以下顺序阅读：

1. 当前模块的用户物理片段；
2. 上表对应的 CsI 文件；
3. 当前模块已有通用实现；
4. 当前模块测试；
5. 再决定 `REUSE / CONFIG_ONLY / ADAPTER / EXTENSION`。

不得先复制 CsI，再尝试修改成新实验。
