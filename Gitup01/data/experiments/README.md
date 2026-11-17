# data/experiments：按实验身份保存输入

<!-- solar-nuclear-v31:start -->

## 当前太阳⁸B SM：v3.1 原子核Response

[当前新版本与两实验实际计算](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>)。核表→振幅→截面→事例数；旧KN文档/计算保留。

<!-- solar-nuclear-v31:end -->

<!-- solar-onboarding-v3:start -->

## 历史v3.0太阳⁸B onboarding：v3.0完整整合版（2026-11-09）

[单文件阅读PandaX与XENONnT：全部输入、来源、SM/V/B−L结果及交接](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>)。本版合并v2.0–v2.3的有效内容；旧版本保留。

<!-- solar-onboarding-v3:end -->

本目录拥有数据与来源说明，[代码目录](../../cevns_pyeft/experiments/README.md)拥有定义和算法。当前三个注册 Dataset 的默认资源都是 `package_input`（YAML）和 `package_arrays`（NPZ）；不会因目录、论文或旧 YAML 存在就自动启用实验。

| Dataset | 正式输入与实际消费者 | 保留的来源核对材料 |
|---|---|---|
| [COHERENT_CsI/CsI2017](COHERENT_CsI/CsI2017/README.md) | `csi2017_definition.py` 委托 Package loader；28 个数组，包括源谱、味态、核响应、效率、PE edges 和统计量 | 旧 `experiment.yaml`、五份 `COHERENT_*.txt`、统计 provenance；历史 `observation_schema.json` 本地缺失，不是当前默认输入 |
| [COHERENT_CsI/CsI2021](COHERENT_CsI/CsI2021/README.md) | `csi2021_definition.py` 委托 Package loader；23 个数组，当前九箱观测/背景/误差来自 NPZ | 旧 `experiment.yaml` 与 `statistics/provenance.yaml`；探测器模型参数来自正式 YAML |
| [COHERENT_Ar/Ar2020](COHERENT_Ar/Ar2020/README.md) | `ar2020_definition.py` 委托 Package loader；20 个数组，效率和十二箱统计量来自 NPZ | 官方效率表、派生 `Ar_eff.txt`、官方初始 SM 信号参考 `cevnspdf.txt` 与统计 provenance |

各目录的 `experiment.input.yaml` 和 `experiment.resources.npz` 是正式机器输入；`experiment.physics.md`、已有 `experiment.physics.summary.md` 是生成说明。上表中的旧表和 provenance 不由当前默认 Package 重新读取，不能据历史路径推断当前消费者。核响应也从 NPZ 装配，不以外部 [responses_all.json](../responses/README.md) 为默认输入。

## 文件职责与来源

太阳8B文献摘录与显式输入包：旧原表用于来源核对，标准Runtime读取正式YAML/NPZ；默认全局活动清单未变。

| 位置 | 实际文件和用途 |
|---|---|
| [PandaX4T/PandaX4T_2024_US2](PandaX4T/PandaX4T_2024_US2/README.md) | 三份 Qy 曲线/带，原实验和 benchmark 各一份 D/B 表；供后续显式核对 |
| [XENONnT/XENONnT_2024_SolarB8](XENONnT/XENONnT_2024_SolarB8/README.md) | 两份 Qy 曲线/带，两份原图 D/B 表，以及官方 SR0/SR1 事件和逐 run 分箱统计；保留坐标冲突 |

YAML 记录参数、模型、数组单位/来源/哈希；NPZ 保存声明数组；Dataset README 列出保留文件的出处、列定义、转换和实际用途。旧 `experiment.yaml` 仅供兼容说明。[specs 接口](../../cevns_pyeft/experiments/specs.py)能够读取它，不使其恢复为正式 Package 权威。

实验独有数据放已有的 `<实验族>/<dataset_id>/`；探测器表放 `detector/`，观测、背景、协方差或统计参考放 `statistics/`，有文件才保留子目录。不创建空目录和新的来源管理层级，不将未知来源文件当作官方实验输入。

## 读取路径与维护

```text
experiment.input.yaml + experiment.resources.npz
  → definition_from_package / ResourceCatalog
  → Package 装配与显式模型消费者
  → 预测或统计评价
```

新输入需要真实消费者与已有资源清单中的适当绑定；仅供复核的旧表无需虚构 Runtime 资源 ID。现有 [resource_manifest.json](../resource_manifest.json) 保持路径/哈希用途。来源、坐标或统计定义未核实的事项写在 Dataset 说明中，不能通过移动文件或检查成功消除。

默认活动的三套COHERENT正式YAML/NPZ齐全，太阳8B另有可显式加载的正式包；分析所用 ZIP 缺少它们，原 ZIP 未由本次整理重写。新实验接入仍通过[现有工作流入口](../../workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md)确认范围。

---

[上一级](../README.md) · [项目总览](../../README.md)

## CONUS+ v3 来源数据

[CONUS_Plus/conusplus_kkl_run1](CONUS_Plus/conusplus_kkl_run1/README.md)保存参考 Flux、天然锗库存、19 点观测与精确来源映射。元数据记录直接转录、项目推导和上游待核项。

<!-- solar-onboarding-history:start -->

## 历史记录（v3.0时期）

[2026-11-07 SM执行记录](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_SM_BENCHMARK_20261107.md>) · [2026-11-08 V/B−L执行记录](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_VECTOR_BENCHMARK_20261108.md>)。旧实验报告与数值保留，各版本链接集中在dataset版本导航；当前SM以页首v3.1为准，旧矢量结果仍按历史版本解释。

<!-- solar-onboarding-history:end -->
