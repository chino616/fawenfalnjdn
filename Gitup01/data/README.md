# data：正式输入与来源核对资料

[当前五条实验输入与方法](<../docs/experiments/LATEST_EXPERIMENTS.md>)。本入口仅列当前选定分析；不同方法的输入、代码、结果和审核范围分别说明。

<!-- solar-singlebin-v321:start -->

## 太阳⁸B：独立的单 bin输入

[单bin v3.2.1：输入、来源、代码与SM结果](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md>) · [多bin v3.1（保留）](<../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>)。

单bin采用2601.19883v2 Eqs.(87),(88)：paired/US2/XENONnT三个信号总数；[独立数据](<benchmarks/solar_b8_singlebin_2601_19883/README.md>)、[独立入口](<../tools/run_solar_b8_singlebin_benchmark.py>)、[独立结果](<../outputs/solar_b8_singlebin/20261111_response_run2/README.md>)。多bin继续原Qy平均映射/响应基底及Ne/cS2分箱。只共享底层物理，不交叉数据、统计和缓存。旧文档中的“当前v3.1”仅指多bin分支。

<!-- solar-singlebin-v321:end -->

<!-- solar-nuclear-v31:start -->

## 当前太阳⁸B SM：v3.1 原子核Response

[当前新版本与两实验实际计算](<../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>)。核表→振幅→截面→事例数；旧KN文档/计算保留。

<!-- solar-nuclear-v31:end -->

<!-- solar-onboarding-v3:start -->

## 历史v3.0太阳⁸B onboarding：v3.0完整整合版（2026-11-09）

[单文件阅读PandaX与XENONnT：全部输入、来源、SM/V/B−L结果及交接](<../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.0.md>)。本版合并v2.0–v2.3的有效内容；旧版本保留。

<!-- solar-onboarding-v3:end -->

本目录按四类职责存放：实验数据在 `experiments/`，共享核响应在 `responses/`，显式计算参数卡在 `benchmarks/`，旧混合资料留在 `datafiles/`。文件存在不等于当前计算会读取它。

| 子目录或文件 | 内容与实际用途 |
|---|---|
| [experiments/](experiments/README.md) | 按实验族和 Dataset 保存正式 YAML/NPZ，以及核对它们所需的探测器表、统计来源和说明 |
| [responses/](responses/README.md) | 共享旧格式 `responses_all.json`；供显式 `ResponseDB`、兼容调用和核响应对照使用 |
| [benchmarks/](benchmarks/README.md) | SM简化方法、V/B−L固定点等显式计算配置；记录采用的实验包、输入哈希、处理选择和来源，不作为新实验注册 |
| [datafiles/](datafiles/README.md) | 六份 SNS/CHOOZ 历史辅助文件；不再接收新数据。两份 Ar2020 表已归位，七份太阳 8B 表维持此前归档 |
| [resource_manifest.json](resource_manifest.json) | 资源路径、作用域、有限别名和 SHA256 清单；不是科学来源文献表，也不代替实际资源绑定 |

## 当前三个 Dataset 如何读取数据

CsI2017、CsI2021、Ar2020 的注册 definition 经 [package loader](../cevns_pyeft/experiments/package_loader.py) 声明 `package_input` 和 `package_arrays`，分别读取各自的 `experiment.input.yaml`、`experiment.resources.npz`。YAML 拥有参数、模型、单位、来源引用和数组声明，NPZ 拥有数值数组；`experiment.physics.md` 及已有精简版是阅读材料，Runtime 不读取它们。

[Package 装配](../cevns_pyeft/experiments/package_profiles.py) 从 NPZ 构造源谱、核响应和统计输入。[response_from_arrays](../cevns_pyeft/experiments/package_components.py) 构造 `ArrayResponseW`，不重新读取外部 `responses_all.json`。旧 `experiment.yaml`、独立效率 TXT 和统计表保留用于历史追溯或显式兼容读取，不再是这三个默认 Package 的第二份权威输入。不能把旧表改动等同于当前计算已同步。

SNS 连续谱数组来自原有代码生成的注量表，不来自 `datafiles/SNSflux_*.txt`；Package 已包含运行期积分注量。连续谱的单位是 `cm^-2 MeV^-1`，谱线权重是 `cm^-2`，不应再重复乘 POT 或运行时间。具体归一化、采样、端点和插值约定以各自 YAML 为准；历史实现一致不等于已完成一手物理核验。

本地三个正式 YAML/NPZ 均存在，共 71 个数组；2026-11-06 已核对数组原始哈希与 YAML 声明一致。分析所用 `2026-11-05_Gitup01.zip` 漏装了这六个正式文件，不能据该 ZIP 判定本地也缺失，更不能用旧 TXT 重建覆盖。CsI2017 的 `statistics/observation_schema.json` 本地确实缺失，仍在历史归属/来源声明中出现；当前 Package 不读取它，兼容分发问题见 [Dataset 说明](experiments/COHERENT_CsI/CsI2017/README.md)。

## 存放规则与来源说明

| 归属 | 放置位置 |
|---|---|
| 实验专属正式输入与说明 | `experiments/<实验族>/<dataset_id>/` |
| 独立探测器效率或响应表 | 该 Dataset 已有的 `detector/` |
| 观测、背景、协方差或统计参考表 | 该 Dataset 已有的 `statistics/` |
| 多个理论计算共享的核响应 | `responses/` |
| 尚未整理的历史混合文件 | 现有 `datafiles/`，不再新增 |

只在有实际文件时保留职责子目录；不增加 `raw/processed/external/archive/generated` 层级或另一套数据管理系统。论文 PDF、生成脚本、拟合输出、日志和缓存不放入本目录。

正式参数和数组的来源写在现有 `experiment.input.yaml`；独立文件在所属 README 回答：来自哪里、原文件/图表位置、列含义和单位、经历何种转换、当前谁读取。未知项直接写未知。三个已有 `statistics/provenance.yaml` 保留历史说明，不另建逐文件 sidecar。文件格式标识、相同文件名和曲线相似都不能替代来源证据。

## 资源根与维护

2026-11-06 补充的太阳 8B 文献摘录分别位于 [PandaX-4T US2](experiments/PandaX4T/PandaX4T_2024_US2/README.md) 和 [XENONnT 2024](experiments/XENONnT/XENONnT_2024_SolarB8/README.md)：包括 Qy、观测和背景的数值表、来源及版本差异。这两处是计算准备资料，尚未注册或绑定 Runtime；不改变上文三个正式 Package 的读取链，也不恢复旧 `datafiles/` 归档表。

`ResourceCatalog.root` 是包含 `data/` 的项目或资源根，不是 `data/` 本身；wheel 代码与资源可以分开部署。资源仅由实际 definition/调用显式选择，不自动扫描启用。单实验覆盖用资源 ID，多实验同名资源用 `(dataset_id, resource_id)` 作用域；[有限别名](../cevns_pyeft/foundation/resources.py)只兼容既有路径，不替代新文件的来源核对。

新增正式输入先确认归属、单位、坐标、归一化和是否已含响应/曝光，再更新真实消费者及已有清单。仅供核对的历史表不因此新增 Runtime 绑定。现有资源检查入口为 `python -B tools/validate_resource_manifest.py --root .`；不为通过检查而修改数据、参考数组或无关哈希。新实验接入仍通过[现有工作流入口](../workflows/cevns-pyeft/skills/router/cevns-experiment/SKILL.md)确认范围。

---

[上一级](../README.md)

<!-- solar-onboarding-history:start -->

## 历史记录（v3.0时期）

[2026-11-07 SM执行记录](<../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_SM_BENCHMARK_20261107.md>) · [2026-11-08 V/B−L执行记录](<../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_VECTOR_BENCHMARK_20261108.md>)。旧实验报告与数值保留，各版本链接集中在dataset版本导航；当前SM以页首v3.1为准，旧矢量结果仍按历史版本解释。

<!-- solar-onboarding-history:end -->

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

新增solar_b8_nsi_2601_19883来源卡、太阳径向输入和精确百分比误差；旧SM/多bin数据保留。

[完整新onboarding：实际输入、标准引文、物理与程序](<../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<benchmarks/solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->
