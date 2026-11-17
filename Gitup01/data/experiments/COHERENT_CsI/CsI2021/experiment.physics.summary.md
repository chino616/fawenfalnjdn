# COHERENT CsI[Na] — CsI2021 — Physics Summary

状态：DRAFT / PARTIAL；人工科学审核 NOT_REVIEWED。

COHERENT CsI[Na] — CsI2021 使用 prompt_numu、delayed_nue、delayed_numubar，靶核素为 Cs133、I127；观测量为 reconstructed PE spectrum，共 9 个 PE 分箱。

[详细实现说明](experiment.physics.md) 包含完整实验公式、符号、参数、分箱、逐 bin 数据和数值约定。

## 关键实验输入

| 输入 | 当前值 | 单位 |
| --- | --- | --- |
| `source.baseline_m` | 19.3 | m |
| `source.total_pot` | 3.198e+23 | POT |
| `source.yield_per_pot` | 0.0848 | neutrinos/species/POT |
| `source.fluence_per_species` | 579361763793233.6 | cm^-2 |
| `source.prompt_energy` | 29.792140909877446 | MeV |
| `source.integration_max` | 52.827952069788324 | MeV |
| `target.detector_mass` | 14.57 | kg |

靶核素：Cs133, I127。核素质量分数、单核质量及核数见详细版 Target。

| 探测器组件 | 本次选择 |
| --- | --- |
| CsI 淬灭映射 | `csi_quenching_legacy_v1` |
| Gamma PE 响应 | `legacy_csi_gamma` |
| PE 选择效率 | `csi2021_logistic_legacy` |
| 分量接受率 | `legacy_component_acceptance` |

## 共享模块选择

| 独立维度 | 已登记 model ID | 绑定状态 |
| --- | --- | --- |
| Interaction / 组合接口 | `li2026_sm_left_v1` | BOUND_AND_TESTED |
| Interaction / 组合接口 | `li2026_matching_v1` | BOUND_AND_TESTED |
| Kinematics / Cross-section | `elastic_kinematics_v1` | BOUND_AND_TESTED |
| Nuclear Structure | `nuclear_np_polynomial_v1` | BOUND_AND_TESTED |
| Interaction / 组合接口 | `li2026_R_W_kernel_v1` | BOUND_AND_TESTED |
| Kinematics / Cross-section | `li2026_dsigma_v1` | BOUND_AND_TESTED |

Interaction 与 Nuclear Structure 分开选择；表中的状态是已有记录，不代表本次重新运行或科学接受。

## Observable / Statistics

观测量：reconstructed PE spectrum；9 箱，范围 0.001–60.001 PE。完整边界见详细版第 6 节。

统计选择：`gaussian_two_pull_legacy_v1`。数据单位：counts/PE。

预测为 events/bin，统计前只除一次 PE 箱宽；保留 observed-like residual 的负值。当前是旧 Gaussian 近似，背景扣除语义尚未确认。

## 主要限制

- official_experiment_sources：缺官方论文、补充材料与 release 的独立核对；旧代码值不能称为官方原值。

- eft_primary_conventions：算符 Lorentz/Lagrangian 定义、尺度及公共 matching 约定尚未逐项对照原始文献。

- nuclear_source_audit：外部核响应源、转换流程和归一化仍待核实；I 的 M_nn(0) 差异保留为未决问题。

- antineutrino_kernel：反中微子标签保留，但当前使用同一味核；一般 EFT 的符号和 helicity 尚未独立验证。

- statistics_semantics：observed 是旧 residual/excess；是否已扣除所列背景尚无原始证据，不消除负值，也不宣称官方 likelihood。

完整限制、来源与能力记录见[详细版第 10 节](experiment.physics.md#section-10)。
