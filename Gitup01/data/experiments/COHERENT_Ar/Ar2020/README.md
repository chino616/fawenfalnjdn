# Ar2020 input package

The registered Ar2020 runtime reads [experiment.input.yaml](experiment.input.yaml)
and [experiment.resources.npz](experiment.resources.npz). The generated
[experiment.physics.md](experiment.physics.md) explains the same inputs for human
review and is distributed with the dataset; runtime does not read it.

The package preserves the legacy SNS/Ar40 prediction, observed-energy Gaussian
resolution, tabulated efficiency and approximate asymmetric IRLS statistics.
Values are legacy-derived; package status is DRAFT and human physics review is
NOT_REVIEWED. Official likelihood, general antineutrino EFT and scientific release
remain BLOCKED. Dataset identity and related papers are indexed in the
[Ar2020 overview](../../../../docs/experiments/COHERENT/Ar2020/README.md).

The detector and statistics directories retain source-review material. Normal
Package runtime does not read these older files; newly relocated reference tables
are not additional runtime inputs. Recompilation uses the common compiler and saved acquisition IR,
with hashes, units, normalization and generated dependencies checked.

[experiment.physics.md](experiment.physics.md) 使用现有共享 Renderer，
按本 dataset 输入选择物理说明、必要公式和简明资源索引；公共 matching/粒子响应不逐项展开。
现有 YAML/NPZ 和权限保持原样，报告可用既有 CLI 的 `--md-only` 只读输入重渲染；
见[package 编译器入口](../../../../tools/compile_experiment_package.py)。

## 保留文件与官方来源

| 文件 | 来源、列定义和转换 | 当前用途 |
|---|---|---|
| [experiment.input.yaml](experiment.input.yaml) / [experiment.resources.npz](experiment.resources.npz) | 从项目旧十二箱 SNS/Ar40 实现提取的正式模型/参数与 20 个数组，来源仍标为 `legacy` | 默认 Runtime 的机器权威 |
| [experiment.physics.md](experiment.physics.md) | 由上述正式输入生成的物理说明，非原始实验数据 | 人工阅读；本次未重新渲染 |
| [detector/CENNS10AnlAEfficiency.txt](detector/CENNS10AnlAEfficiency.txt) | COHERENT 官方 release 同名文件，80×3：第 1 列 keVee，第 2 列 keVnr，第 3 列无量纲效率；本地逐值一致，数字/指数写法不同 | 官方来源核对表，默认 Runtime 不重读；NPZ 数值对应第 1、3 列 |
| [detector/Ar_eff.txt](detector/Ar_eff.txt) | 80×2，逐值等于官方三列表第 2、3 列：keVnr、无量纲效率；可确认选列关系，历史操作者/时间未知 | 从旧 `data/datafiles/Ar_eff.txt` 原样归位；参考派生表，未绑定 Package |
| [statistics/cevnspdf.txt](statistics/cevnspdf.txt) | COHERENT 官方 release 同名表，960×4：能量中心 keVee、F90 中心（无量纲）、触发时间中心 μs、每箱预期 CEvNS 事件数 | 从旧 `data/datafiles/cevnspdf.txt` 原样归位；初始 central-value SM 信号参考，不是观测或正式 NPZ 统计输入 |
| [statistics/provenance.yaml](statistics/provenance.yaml) | 旧 `slow_counts_ar2020.py` / `cutoff_multi.py` 携带的 `AR_D, AR_B, AR_DMIN, AR_DMAX` 解释 | 保留既有非官方统计说明；不由新归位的 signal PDF 替代 |

官方来源是 [COHERENT Ar 2020 release，DOI 10.5281/zenodo.3903810](https://doi.org/10.5281/zenodo.3903810)，对应[数据说明 2006.12659](https://arxiv.org/abs/2006.12659)。精确位置为 release 的 `CENNS10AnlAEfficiency.txt`、`cevnspdf.txt`，列名/归一化分别见 `CENNS10DataReleaseCompanion.pdf` §2.6、§2.2（坐标格式见 §2.1）；`LArParametersAnlA.yaml` 记有 6.12 GWhr 和初始 CV 信号 128±17。

效率包含 Analysis A 的 F90 选择；官方规定超过最后一个重建能量点保持末点效率。`cevnspdf` 为 12 个能量 ×8 个 F90 ×10 个时间箱，按 6.12 GWhr 的初始 CV SM 预测归一化，第 4 列合计约 128.000005；文件名虽称 PDF，它不是积分为 1 的概率表，也不是实测计数。不用它替代任意 EFT 预测或重复乘归一化。

本地官方表及选列表均没有在本次重新取点、插值、归一化或改写指数记法。两份归位表的 SHA256 与原位置相同；这些数值一致性不证明历史下载/选列操作链的每一步。

## NPZ 的 20 个数组及坐标问题

| 数组组 | 个数、坐标/单位 | 来源与消费者 |
|---|---|---|
| `source_energy_MeV`, `source_fluence_1/2`, `rho_0/1/2` | 6；200 点 MeV，连续注量 `cm^-2 MeV^-1`，味态无量纲 | 原 SNS 代码生成并保存；prompt 参数在 YAML，不读取旧 SNS TXT，也不重复乘 POT/运行时间 |
| `nuclear_Ar40_*` | 7；七响应通道，`(p,n)` 2×2 升幂系数，无量纲 | 与现有 [responses_all.json](../../../responses/README.md) Ar40 条目一致，由 NPZ 构造响应；外部源表仍待核实 |
| `efficiency_energy`, `efficiency_values` | 2；YAML 将能量声明为 PE、效率无量纲 | 数值分别等于官方 TXT 第 1、3 列；供当前表格效率模型，单位冲突如下 |
| `observable_edges` | 1；13 个 edges，按现有声明为 PE | 原十二箱约定，供分箱；不能据官方 keVee 标签直接重标 |
| `statistics_observed/background/lower/upper` | 4；12 箱，counts/bin | 旧 `AR_*` 数组，供现有近似非对称 IRLS/有界两 pull 统计；非官方三维 PDF 的观测 |

20 个数组原始哈希均与 YAML 声明一致。需要单独科学核对的现有冲突是：`efficiency_energy` 的数值来自官方 **keVee** 第一列，而 Package 标签为 **PE**。数值相等不代表单位相同；还需追踪模型重建坐标、光产额及单位转换才能决定修复方式。本次明确记录问题，保持 YAML/NPZ、标签和计算行为不变，未改为 `Ar_eff.txt` 的 keVnr 坐标。

分析所用 ZIP 漏装了本地已存在的正式 YAML/NPZ，本次未重建。统计 provenance 的一手来源、残差/背景语义及官方完整 likelihood 仍未闭合，官方表出处的确认不解除这些限制。

[数据集目录](../../README.md) · [data 总览](../../../README.md)

<!-- latest-analyses:start -->

## 当前最新分析与处理方式

[五条实验最新入口](<../../../../docs/experiments/LATEST_EXPERIMENTS.md>)

| 分析 | 方法/版本 | 输入 | 结果与核对范围 |
|---|---|---|---|
| Ar2020：12箱专用观测宽度Gaussian | [Package v2 / legacy compatibility；处理方式](<../../../../docs/experiments/COHERENT/Ar2020/METHODS.md>) | [当前输入](<experiment.input.yaml>) | [最新核对结果](<../../../../outputs/COHERENT_Ar/Ar2020/sm_legacy_12bin_20261111/SM_RESULT.json>) |

来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。

<!-- latest-analyses:end -->
