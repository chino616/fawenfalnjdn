# data/responses：共享旧格式核响应表

<!-- solar-nuclear-v31:start -->

## 太阳⁸B SM的显式复用

D0004选择本JSON及现有reader约定。[v3.1](../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md)记录七个Xe核素、全部通道和实际核系数；缺Xe124/Xe126，不重归一、不用KN补齐。外部原始作者/转换认证仍待核。

<!-- solar-nuclear-v31:end -->

[responses_all.json](responses_all.json) 保留给显式 [ResponseDB](../../cevns_pyeft/nuclear/response.py) 调用、兼容入口、历史构建与核响应对照。当前 CsI2017、CsI2021、Ar2020 的默认 Package 均从各自 NPZ 构造 `ArrayResponseW`，不重新读取这份外部 JSON；具体装配见 [package_components.py](../../cevns_pyeft/experiments/package_components.py)。

## 文件内容与约定

| 项目 | 当前文件内容 |
|---|---|
| 核素键（20 个） | `F, Na, Si28, Si29, Si30, Ar40, Ge70, Ge72, Ge73, Ge74, Ge76, I, Cs133, Xe128, Xe129, Xe130, Xe131, Xe132, Xe134, Xe136`；`I` 对应 Package 的 `I127` |
| 响应通道（8 个） | `M, SigmaPP, SigmaP, PhiPP, PhiPT, Delta, MPhiPP, SigmaPDelta` |
| 存储 | 每核素有 `basic`、`exp_factor`、`responses`；响应为升幂多项式系数列表或由列表构成的 2×2 矩阵 |
| 基底与矩阵顺序 | 元数据声明 `np`，行列均按 `(p,n)`；`iso` 结果由读取代码变换 |
| 求值 | `W_ab(y) = exp(exp_factor*y) * sum_k(coeff_abk*y**k)`；`y=(q*b/2)**2` 无量纲，调用方需保证 `q` 与 `b` 的单位互逆 |
| 单位与归一化 | Package 声明系数及 W 无量纲；外部源表的绝对归一化、通道符号与完整转换链仍待独立核实 |

核表不含材料质量分数、源谱、曝光或探测器效率。三个 Package 使用其中七个通道，合计 35 份核素/通道系数数组；2026-11-06 核对均与当前 JSON 对应条目一致（空通道按读取器约定比较）。这证明当前本地转换的一致性，不证明外部核物理来源已经确认。

## 来源与转换边界

当前可确认的直接来源是项目既有聚合 JSON。内部格式标识为 `Mu2eNRET_ResponseW_v1`；它不是论文引用。原始作者数据包、源表下载位置、生成脚本版本、具体论文表号以及所有通道的转换/归一化流程尚未完整取得，来源未知部分保持未知，不把格式名当成来源证明。

CsI2021时间分析的用户已明确选择直接调用本目录原JSON。[该分析的r2来源记录](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/README.md)展示Cs133/I全部八通道的16个实际数组、矩阵基底、系数阶数、指数因子和原读取器约定。复用权威仍是本文件，查看用NPZ与当前系数逐值一致。外部作者生成链只限制外部来源认证，不作为该已选本地复用的前置条件。

本轮取得了作者Elastic的Cs133/I127密度矩阵和Mu2e_NRET固定提交代码，[原始下载和SHA](../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/sources/upstream_nuclear/README.md)可查。它们目前是候选上游，与当前JSON逐通道的生成对应尚未证明，来源状态继续保留未核实。

正式 [CsI2021 YAML](../experiments/COHERENT_CsI/CsI2021/experiment.input.yaml) 的 `provenance.sources.nuclear_audit` 保留历史审计路径，但对应审计文件未随当前本地源码提供，不能当作已经可查阅的一手来源。YAML/NPZ 中的来源声明仍指向历史实现或本地 JSON；本次没有改写 JSON、重算系数、改基底或更新冻结参考。

## 维护

不要删除仍供兼容代码及显式 `ResponseDB` 测试使用的旧表。新增共享表时，在本目录说明具体版本、核素、通道、单位、原始位置和转换，再由消费者显式选择；不会自动扫描拼接。维护已有清单的真实路径/哈希，核对受影响消费者。正式 Package 保存的系数不因外部 JSON 变化自动更新，不应为了匹配期望事件数调整系数。

---

[上一级](../README.md) · [项目总览](../../README.md)
