# 实验计算路线逐步核查

2026-11-13。按实际Python文件和函数/类核对P01-P10的职责。阶段有代码不等于当前输入可执行，更不等于正式科学Gate通过。

P01数据身份/观测 → P02靶与曝光 → P03源/味态 → P04理论/核表 → P05运动学/截面 → P06探测器 → P07 Slow → P08 Fast → P09统计 → P10验证。公共模块可跨实验复用，不要求复制十套实验专用代码。

| 实验/路线 | 当前真实状态 |
|---|---|
| CsI2017_25PE | PACKAGE_READ_BLOCKED; SM_SNAPSHOT_ONLY |
| CsI2021_9PE_energy_only | SAVED_VERIFIED_KERNEL_USABLE; NATIVE_PACKAGE_READ_BLOCKED |
| Ar2020_12bin | SAVED_VERIFIED_KERNEL_USABLE; NATIVE_PACKAGE_READ_BLOCKED |
| CsI2021_time_9x11 | FORWARD_DONE; P09_MISSING |
| CONUS_Plus_conusplus_kkl_run1 | LOCAL_FORWARD_AND_GAUSSIAN_NSI_BENCHMARK_DONE |
| SolarB8_three_singlebins_continuous_acceptance | SM_AND_EE_NSI_INFERENCE_DONE_WITH_DECLARED_APPROXIMATIONS |
| SolarB8_multibin_separate_branch | SM_FORWARD_DONE; NOT_REUSED_FOR_SINGLEBIN_SCANS |

## CsI2017_25PE

P06 deterministic PE=1.17T, fixed 251-node PE grid; P09 28% one-pull Gaussian. No saved parameter-resolved kernel available. Core/package exist but reads fail; schema provenance remains partial.

入口：[cevns_pyeft/experiments/coherent/slow_counts_csi2017.py::slow_counts_csi2017](<../../cevns_pyeft/experiments/coherent/slow_counts_csi2017.py>)。

输入：`data/experiments/COHERENT_CsI/CsI2017/experiment.input.yaml + experiment.resources.npz`；已有证据：`outputs/COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json`。

| 步骤 | 负责内容与计算 | 输入 → 输出 | 实际Python文件与函数 | 核对结果 |
|---|---|---|---|---|
| P01 | Dataset/observable<br>读取并绑定身份、单位和bin边界 | dataset配置、数值资源与observable定义 → definition/model与25 PE箱 | [cevns_pyeft/experiments/package_loader.py::read_package](<../../cevns_pyeft/experiments/package_loader.py>)（L14）<br>[cevns_pyeft/experiments/package_loader.py::definition_from_package](<../../cevns_pyeft/experiments/package_loader.py>)（L207） | EXISTS |
| P02 | Target/exposure<br>计算核数并保存曝光归属，避免重复归一 | 同位素组成、核质量、质量/曝光定义 → TargetInventory与run/exposure | [cevns_pyeft/experiments/package_profiles.py::assemble](<../../cevns_pyeft/experiments/package_profiles.py>)（L85） | EXISTS |
| P03 | Source/state<br>建立相同能量轴上的源分量及入射态 | 源能谱/谱线、源强、几何、ν/反ν与味态 → flux/fluence components与rho(E) | [cevns_pyeft/experiments/package_components.py::ArraySource](<../../cevns_pyeft/experiments/package_components.py>)（L38） | EXISTS |
| P04 | Theory/nuclear response<br>response_from_arrays→ArrayInteraction；不重新从ResponseDB读取外部核表 | 正式NPZ内的各核响应系数、常量快照 → package-backed核响应和相互作用 | [cevns_pyeft/experiments/package_components.py::ArrayInteraction](<../../cevns_pyeft/experiments/package_components.py>)（L164）<br>[cevns_pyeft/experiments/package_components.py::response_from_arrays](<../../cevns_pyeft/experiments/package_components.py>)（L103） | EXISTS |
| P05 | Kinematics/cross section<br>ArrayInteraction.dsigma_dT→differential_cross_section_nn；保留全核通道和味迹 | Eν/反冲网格、核质量、入射态和interaction → dσ/dT [cm²/keV] | [cevns_pyeft/theory/kinematics.py::is_two_body_recoil_allowed](<../../cevns_pyeft/theory/kinematics.py>)（L40）<br>[cevns_pyeft/experiments/package_components.py::ArrayInteraction.dsigma_dT](<../../cevns_pyeft/experiments/package_components.py>)（L214）<br>[cevns_pyeft/rates/differential.py::differential_cross_section_nn](<../../cevns_pyeft/rates/differential.py>)（L360） | EXISTS |
| P06 | Detector/selection<br>确定性PE映射与插值梯形分箱，无额外Gaussian | PE=1.17T、效率和251节点PE网格 → 25箱效率折叠信号 | [cevns_pyeft/experiments/package_profiles.py::ArrayEfficiency](<../../cevns_pyeft/experiments/package_profiles.py>)（L11）<br>[cevns_pyeft/detectors/coherent.py::DeterministicPEObservation](<../../cevns_pyeft/detectors/coherent.py>)（L24）<br>[cevns_pyeft/rates/legacy_observables.py::fold_weights](<../../cevns_pyeft/rates/legacy_observables.py>)（L36） | EXISTS |
| P07 | Slow counts<br>直接积分能量与反冲，按源/核素分别求和 | 源、靶、dσ/dT、响应和积分网格 → SM/参数点预测 [events/bin]：25 PE箱 | [cevns_pyeft/experiments/package_profiles.py::ProfileExecutor](<../../cevns_pyeft/experiments/package_profiles.py>)（L174）<br>[cevns_pyeft/rates/legacy_observables.py::predict_legacy_observable](<../../cevns_pyeft/rates/legacy_observables.py>)（L50）<br>[cevns_pyeft/rates/recoil.py::integrate_recoil_yield](<../../cevns_pyeft/rates/recoil.py>)（L16） | EXISTS |
| P08 | Fast representation<br>编译或回放明确参数域内的响应表示 | 已核查前向模型、网格、系数基和缓存身份 → 参数点快速预测及源码/输入指纹 | [cevns_pyeft/experiments/package_profiles.py::compile_profile](<../../cevns_pyeft/experiments/package_profiles.py>)（L254）<br>[cevns_pyeft/experiments/package_profiles.py::predict_profile_kernel](<../../cevns_pyeft/experiments/package_profiles.py>)（L298） | EXISTS |
| P09 | Statistics/inference<br>正式路线28%一pull Gaussian；本次仅重核冻结SM χ²，参数核缺失 | 与预测同语义的观测、误差、背景、nuisance → SM checkpoint；本次弱角/NSI扫描NOT_RUN | [cevns_pyeft/experiments/package_profiles.py::evaluate_statistics](<../../cevns_pyeft/experiments/package_profiles.py>)（L240） | EXISTS |
| P10 | Validation/report<br>核对回归、独立积分/核表示、来源和结果适用范围 | 当前模型、数值输出、原文/旧结果与验收范围 → 验证JSON、表格、图件与未完成能力记录；当前正式YAML/NPZ读失败单独记录 | [examples/experiment_modularization/run_experiments.py::<module>](<../../examples/experiment_modularization/run_experiments.py>)（L1） | EXISTS |

## CsI2021_9PE_energy_only

Separate from 99-bin time route. Saved final 512/1920/256 grid; Gaussian signal/background pulls .125/.35. New scans explicitly replay frozen kernel, not a new public-loader run.

入口：[cevns_pyeft/experiments/runtime.py::predict_experiment](<../../cevns_pyeft/experiments/runtime.py>)。

输入：`data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml + experiment.resources.npz`；已有证据：`outputs/paper2601_chi2_corrected_20261111/CsI2021_FORWARD.json`。

| 步骤 | 负责内容与计算 | 输入 → 输出 | 实际Python文件与函数 | 核对结果 |
|---|---|---|---|---|
| P01 | Dataset/observable<br>读取并绑定身份、单位和bin边界 | dataset配置、数值资源与observable定义 → definition/model与9 PE箱 | [cevns_pyeft/experiments/package_loader.py::read_package](<../../cevns_pyeft/experiments/package_loader.py>)（L14）<br>[cevns_pyeft/experiments/package_loader.py::definition_from_package](<../../cevns_pyeft/experiments/package_loader.py>)（L207） | EXISTS |
| P02 | Target/exposure<br>计算核数并保存曝光归属，避免重复归一 | 同位素组成、核质量、质量/曝光定义 → TargetInventory与run/exposure | [cevns_pyeft/experiments/package_loader.py::_assemble](<../../cevns_pyeft/experiments/package_loader.py>)（L97） | EXISTS |
| P03 | Source/state<br>建立相同能量轴上的源分量及入射态 | 源能谱/谱线、源强、几何、ν/反ν与味态 → flux/fluence components与rho(E) | [cevns_pyeft/experiments/package_components.py::ArraySource](<../../cevns_pyeft/experiments/package_components.py>)（L38） | EXISTS |
| P04 | Theory/nuclear response<br>response_from_arrays→ArrayInteraction；不重新从ResponseDB读取外部核表 | 正式NPZ内的各核响应系数、常量快照 → package-backed核响应和相互作用 | [cevns_pyeft/experiments/package_components.py::ArrayInteraction](<../../cevns_pyeft/experiments/package_components.py>)（L164）<br>[cevns_pyeft/experiments/package_components.py::response_from_arrays](<../../cevns_pyeft/experiments/package_components.py>)（L103） | EXISTS |
| P05 | Kinematics/cross section<br>ArrayInteraction.dsigma_dT→differential_cross_section_nn；保留全核通道和味迹 | Eν/反冲网格、核质量、入射态和interaction → dσ/dT [cm²/keV] | [cevns_pyeft/theory/kinematics.py::is_two_body_recoil_allowed](<../../cevns_pyeft/theory/kinematics.py>)（L40）<br>[cevns_pyeft/experiments/package_components.py::ArrayInteraction.dsigma_dT](<../../cevns_pyeft/experiments/package_components.py>)（L214）<br>[cevns_pyeft/rates/differential.py::differential_cross_section_nn](<../../cevns_pyeft/rates/differential.py>)（L360） | EXISTS |
| P06 | Detector/selection<br>淬灭→Gamma PE迁移→效率与分量接受度→9箱 | 真实反冲、响应/效率数值与观测分箱 → 观测箱折叠权重/接受度 | [cevns_pyeft/detectors/csi2021.py::CsI2021Observation](<../../cevns_pyeft/detectors/csi2021.py>)（L109）<br>[cevns_pyeft/detectors/csi2021.py::CsIGammaResponse](<../../cevns_pyeft/detectors/csi2021.py>)（L87） | EXISTS |
| P07 | Slow counts<br>直接积分能量与反冲，按源/核素分别求和 | 源、靶、dσ/dT、响应和积分网格 → SM/参数点预测 [events/bin]：9 PE箱 | [cevns_pyeft/core/predict.py::predict](<../../cevns_pyeft/core/predict.py>)（L59）<br>[cevns_pyeft/rates/recoil.py::integrate_recoil_yield](<../../cevns_pyeft/rates/recoil.py>)（L16）<br>[cevns_pyeft/rates/folding.py::legacy_density_fold](<../../cevns_pyeft/rates/folding.py>)（L45） | EXISTS |
| P08 | Fast representation<br>编译或回放明确参数域内的响应表示 | 已核查前向模型、网格、系数基和缓存身份 → 参数点快速预测及源码/输入指纹 | [cevns_pyeft/kernels/compiler.py::compile_fast](<../../cevns_pyeft/kernels/compiler.py>)（L200）<br>[cevns_pyeft/kernels/compiler.py::reconstruct_channels](<../../cevns_pyeft/kernels/compiler.py>)（L119） | EXISTS |
| P09 | Statistics/inference<br>九箱Gaussian .125/.35独立信号/背景pull；本次回放已保存核 | 与预测同语义的观测、误差、背景、nuisance → χ²、Δχ²、最佳值和分离阈值区间 | [cevns_pyeft/experiments/package_loader.py::evaluate_package_statistics](<../../cevns_pyeft/experiments/package_loader.py>)（L240） | EXISTS |
| P10 | Validation/report<br>核对回归、独立积分/核表示、来源和结果适用范围 | 当前模型、数值输出、原文/旧结果与验收范围 → 验证JSON、表格、图件与未完成能力记录；当前正式YAML/NPZ读失败单独记录 | [examples/experiment_modularization/run_experiments.py::<module>](<../../examples/experiment_modularization/run_experiments.py>)（L1） | EXISTS |

## Ar2020_12bin

P06 observed-coordinate-width Gaussian, declared PE versus official keVee conflict. Saved 321/1920/64 grid. Mean-error benchmark and legacy asymmetric model are distinct; full asymmetric inputs cannot be reopened now.

入口：[cevns_pyeft/experiments/coherent/slow_counts_ar2020.py::slow_counts_ar2020](<../../cevns_pyeft/experiments/coherent/slow_counts_ar2020.py>)。

输入：`data/experiments/COHERENT_Ar/Ar2020/experiment.input.yaml + experiment.resources.npz`；已有证据：`outputs/paper2601_chi2_corrected_20261111/Ar2020_FORWARD.json`。

| 步骤 | 负责内容与计算 | 输入 → 输出 | 实际Python文件与函数 | 核对结果 |
|---|---|---|---|---|
| P01 | Dataset/observable<br>读取并绑定身份、单位和bin边界 | dataset配置、数值资源与observable定义 → definition/model与12个legacy观测箱 | [cevns_pyeft/experiments/package_loader.py::read_package](<../../cevns_pyeft/experiments/package_loader.py>)（L14）<br>[cevns_pyeft/experiments/package_loader.py::definition_from_package](<../../cevns_pyeft/experiments/package_loader.py>)（L207） | EXISTS |
| P02 | Target/exposure<br>计算核数并保存曝光归属，避免重复归一 | 同位素组成、核质量、质量/曝光定义 → TargetInventory与run/exposure | [cevns_pyeft/experiments/package_profiles.py::assemble](<../../cevns_pyeft/experiments/package_profiles.py>)（L85） | EXISTS |
| P03 | Source/state<br>建立相同能量轴上的源分量及入射态 | 源能谱/谱线、源强、几何、ν/反ν与味态 → flux/fluence components与rho(E) | [cevns_pyeft/experiments/package_components.py::ArraySource](<../../cevns_pyeft/experiments/package_components.py>)（L38） | EXISTS |
| P04 | Theory/nuclear response<br>response_from_arrays→ArrayInteraction；不重新从ResponseDB读取外部核表 | 正式NPZ内的各核响应系数、常量快照 → package-backed核响应和相互作用 | [cevns_pyeft/experiments/package_components.py::ArrayInteraction](<../../cevns_pyeft/experiments/package_components.py>)（L164）<br>[cevns_pyeft/experiments/package_components.py::response_from_arrays](<../../cevns_pyeft/experiments/package_components.py>)（L103） | EXISTS |
| P05 | Kinematics/cross section<br>ArrayInteraction.dsigma_dT→differential_cross_section_nn；保留全核通道和味迹 | Eν/反冲网格、核质量、入射态和interaction → dσ/dT [cm²/keV] | [cevns_pyeft/theory/kinematics.py::is_two_body_recoil_allowed](<../../cevns_pyeft/theory/kinematics.py>)（L40）<br>[cevns_pyeft/experiments/package_components.py::ArrayInteraction.dsigma_dT](<../../cevns_pyeft/experiments/package_components.py>)（L214）<br>[cevns_pyeft/rates/differential.py::differential_cross_section_nn](<../../cevns_pyeft/rates/differential.py>)（L360） | EXISTS |
| P06 | Detector/selection<br>observed_gaussian_fold在每个观测箱内积分；PE/keVee冲突仍保留 | 均值响应、σ随观测坐标变化的Gaussian与效率 → 12箱折叠矩阵 | [cevns_pyeft/experiments/package_profiles.py::ArrayEfficiency](<../../cevns_pyeft/experiments/package_profiles.py>)（L11）<br>[cevns_pyeft/detectors/coherent.py::ObservedGaussianObservation](<../../cevns_pyeft/detectors/coherent.py>)（L35）<br>[cevns_pyeft/rates/legacy_observables.py::observed_gaussian_fold](<../../cevns_pyeft/rates/legacy_observables.py>)（L23） | EXISTS |
| P07 | Slow counts<br>直接积分能量与反冲，按源/核素分别求和 | 源、靶、dσ/dT、响应和积分网格 → SM/参数点预测 [events/bin]：12个legacy观测箱 | [cevns_pyeft/experiments/package_profiles.py::ProfileExecutor](<../../cevns_pyeft/experiments/package_profiles.py>)（L174）<br>[cevns_pyeft/rates/legacy_observables.py::predict_legacy_observable](<../../cevns_pyeft/rates/legacy_observables.py>)（L50）<br>[cevns_pyeft/rates/recoil.py::integrate_recoil_yield](<../../cevns_pyeft/rates/recoil.py>)（L16） | EXISTS |
| P08 | Fast representation<br>编译或回放明确参数域内的响应表示 | 已核查前向模型、网格、系数基和缓存身份 → 参数点快速预测及源码/输入指纹 | [cevns_pyeft/experiments/package_profiles.py::compile_profile](<../../cevns_pyeft/experiments/package_profiles.py>)（L254）<br>[cevns_pyeft/experiments/package_profiles.py::predict_profile_kernel](<../../cevns_pyeft/experiments/package_profiles.py>)（L298） | EXISTS |
| P09 | Statistics/inference<br>正式路线为非对称IRLS；本次单列均误差Gaussian .12/.146两pull | 与预测同语义的观测、误差、背景、nuisance → 均误差SM/NSI一维结果；未冒称非对称模型重跑 | [cevns_pyeft/experiments/package_profiles.py::evaluate_statistics](<../../cevns_pyeft/experiments/package_profiles.py>)（L240） | EXISTS |
| P10 | Validation/report<br>核对回归、独立积分/核表示、来源和结果适用范围 | 当前模型、数值输出、原文/旧结果与验收范围 → 验证JSON、表格、图件与未完成能力记录；当前正式YAML/NPZ读失败单独记录 | [examples/experiment_modularization/run_experiments.py::<module>](<../../examples/experiment_modularization/run_experiments.py>)（L1） | EXISTS |

## CsI2021_time_9x11

99-bin signal and 24 NSI forward points exist. Missing accepted raw/on-off likelihood and absolute BRN/NIN normalization. Cannot replace with 9-bin Gaussian or invent sqrt(C) full errors.

入口：[examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py::main](<../../examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py>)。

输入：`data/experiments/COHERENT_CsI/CsI2021/time_resolved/analysis_inputs.npz`；已有证据：`outputs/csi2021_time_sm_20261107/VALIDATION_RESULTS.json`。

| 步骤 | 负责内容与计算 | 输入 → 输出 | 实际Python文件与函数 | 核对结果 |
|---|---|---|---|---|
| P01 | Dataset/observable<br>读取并绑定身份、单位和bin边界 | dataset配置、数值资源与observable定义 → definition/model与9 PE×11时间箱 | [examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py::inputs](<../../examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py>)（L52）<br>[examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py::analysis_input_file](<../../examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py>)（L75） | EXISTS |
| P02 | Target/exposure<br>计算核数并保存曝光归属，避免重复归一 | 同位素组成、核质量、质量/曝光定义 → TargetInventory与run/exposure | [cevns_pyeft/targets/materials.py::csi_target_inventory](<../../cevns_pyeft/targets/materials.py>)（L37） | EXISTS |
| P03 | Source/state<br>建立相同能量轴上的源分量及入射态 | 源能谱/谱线、源强、几何、ν/反ν与味态 → flux/fluence components与rho(E) | [examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py::build_model](<../../examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py>)（L175）<br>[examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py::time_source](<../../examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py>)（L87） | EXISTS |
| P04 | Theory/nuclear response<br>匹配粒子响应并绑定核响应 | SM/NSI LEFT系数、核响应数值与约定 → interaction及各核响应通道 | [cevns_pyeft/theory/li2026/adapter.py::Li2026LegacyInteraction](<../../cevns_pyeft/theory/li2026/adapter.py>)（L19）<br>[cevns_pyeft/nuclear/response.py::ResponseDB](<../../cevns_pyeft/nuclear/response.py>)（L97） | EXISTS |
| P05 | Kinematics/cross section<br>施加精确两体运动学并计算每核微分截面 | Eν/反冲网格、核质量、入射态和interaction → dσ/dT [cm²/keV] | [cevns_pyeft/theory/kinematics.py::is_two_body_recoil_allowed](<../../cevns_pyeft/theory/kinematics.py>)（L40）<br>[cevns_pyeft/theory/li2026/adapter.py::dsigma_dT](<../../cevns_pyeft/theory/li2026/adapter.py>)（L78） | EXISTS |
| P06 | Detector/selection<br>Gamma PE响应×经积分的源分量时间权重/时间接受度 | 真实反冲、响应/效率数值与观测分箱 → 观测箱折叠权重/接受度 | [cevns_pyeft/detectors/csi2021.py::CsI2021Observation](<../../cevns_pyeft/detectors/csi2021.py>)（L109）<br>[examples/COHERENT_CsI/time_resolved_common/time_acceptance.py::build_time_weights](<../../examples/COHERENT_CsI/time_resolved_common/time_acceptance.py>)（L108） | EXISTS |
| P07 | Slow counts<br>直接积分能量与反冲，按源/核素分别求和 | 源、靶、dσ/dT、响应和积分网格 → 99箱SM信号、PE/时间投影及24个NSI前向点 | [examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py::calculate](<../../examples/COHERENT_CsI/time_resolved_sm/run_benchmark.py>)（L215）<br>[cevns_pyeft/core/predict.py::predict](<../../cevns_pyeft/core/predict.py>)（L59） | EXISTS |
| P08 | Fast representation<br>cached_evaluate缓存已算前向点；不等于已认证任意耦合99箱Fast核 | 明确EFT点与物理输入指纹 → 已存参数点和缓存身份 | [examples/COHERENT_CsI/time_resolved_nsi/run_benchmark.py::cached_evaluate](<../../examples/COHERENT_CsI/time_resolved_nsi/run_benchmark.py>)（L134） | EXISTS |
| P09 | Statistics/inference<br>未实现本轮可执行的原生P09；不替换为九箱Gaussian | C/AC原始数组与背景候选；BRN/NIN绝对归一和统计合同不全 → MISSING / NOT_RUN |  | MISSING |
| P10 | Validation/report<br>核对回归、独立积分/核表示、来源和结果适用范围 | 当前模型、数值输出、原文/旧结果与验收范围 → 验证JSON、表格、图件与未完成能力记录 | [examples/COHERENT_CsI/time_resolved_sm/validate_benchmark.py::main](<../../examples/COHERENT_CsI/time_resolved_sm/validate_benchmark.py>)（L85） | EXISTS |

## CONUS_Plus_conusplus_kkl_run1

19x10 eVee; natural Ge, selected flux, Nuclear Response, Lindhard+Gaussian; independent effective 1 kg119 day normalization. One .169 Gaussian pull. External KN/author spectrum not exactly equivalent.

入口：[examples/CONUS_Plus/conusplus_kkl_run1/run_benchmark.py::main](<../../examples/CONUS_Plus/conusplus_kkl_run1/run_benchmark.py>)。

输入：`data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json`；已有证据：`outputs/CONUS_Plus/conusplus_kkl_run1/nsi_response_20261106/validation.json`。

| 步骤 | 负责内容与计算 | 输入 → 输出 | 实际Python文件与函数 | 核对结果 |
|---|---|---|---|---|
| P01 | Dataset/observable<br>读取并绑定身份、单位和bin边界 | dataset配置、数值资源与observable定义 → definition/model与19个10 eVee箱 | [examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py::build_model](<../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py>)（L106） | EXISTS |
| P02 | Target/exposure<br>按所选1 kg×119 day口径建立核数和活时间 | 天然Ge组成及当前有效归一化定义 → Ge各核素TargetInventory和run | [examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py::build_model](<../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py>)（L106） | EXISTS |
| P03 | Source/state<br>选定反应堆谱插值→反νe纯态；几何/源强依所选谱口径施加一次 | 源能谱/谱线、源强、几何、ν/反ν与味态 → flux/fluence components与rho(E) | [examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py::build_model](<../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py>)（L106）<br>[examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py::reactor_state](<../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py>)（L101）<br>[cevns_pyeft/experiments/package_components.py::ArrayContinuum](<../../cevns_pyeft/experiments/package_components.py>)（L16） | EXISTS |
| P04 | Theory/nuclear response<br>匹配粒子响应并绑定核响应 | SM/NSI LEFT系数、核响应数值与约定 → interaction及各核响应通道 | [cevns_pyeft/theory/li2026/adapter.py::Li2026LegacyInteraction](<../../cevns_pyeft/theory/li2026/adapter.py>)（L19）<br>[cevns_pyeft/nuclear/response.py::ResponseDB](<../../cevns_pyeft/nuclear/response.py>)（L97） | EXISTS |
| P05 | Kinematics/cross section<br>施加精确两体运动学并计算每核微分截面 | Eν/反冲网格、核质量、入射态和interaction → dσ/dT [cm²/keV] | [cevns_pyeft/theory/li2026/adapter.py::dsigma_dT](<../../cevns_pyeft/theory/li2026/adapter.py>)（L78）<br>[cevns_pyeft/theory/kinematics.py::is_two_body_recoil_allowed](<../../cevns_pyeft/theory/kinematics.py>)（L40） | EXISTS |
| P06 | Detector/selection<br>Ge Lindhard淬灭→Gaussian能量分辨率→效率→eVee分箱 | 真实反冲、响应/效率数值与观测分箱 → 观测箱折叠权重/接受度 | [examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py::GeLindhardGaussian](<../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py>)（L68） | EXISTS |
| P07 | Slow counts<br>直接积分能量与反冲，按源/核素分别求和 | 源、靶、dσ/dT、响应和积分网格 → SM/参数点预测 [events/bin]：19个10 eVee箱 | [cevns_pyeft/core/predict.py::predict](<../../cevns_pyeft/core/predict.py>)（L59）<br>[examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py::main](<../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/calculate_sm.py>)（L143） | EXISTS |
| P08 | Fast representation<br>编译或回放明确参数域内的响应表示 | 已核查前向模型、网格、系数基和缓存身份 → 参数点快速预测及源码/输入指纹 | [cevns_pyeft/kernels/compiler.py::compile_fast](<../../cevns_pyeft/kernels/compiler.py>)（L200）<br>[examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py::build_polynomials](<../../examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py>)（L54） | EXISTS |
| P09 | Statistics/inference<br>有符号excess与对称平均误差Gaussian，16.9%信号pull；非raw Poisson | 与预测同语义的观测、误差、背景、nuisance → χ²、Δχ²、最佳值和分离阈值区间 | [examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py::profile](<../../examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py>)（L129）<br>[examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py::fit_one_dimension](<../../examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py>)（L135） | EXISTS |
| P10 | Validation/report<br>核对回归、独立积分/核表示、来源和结果适用范围 | 当前模型、数值输出、原文/旧结果与验收范围 → 验证JSON、表格、图件与未完成能力记录 | [examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py::validate_predictions](<../../examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/benchmark_nsi.py>)（L70）<br>[examples/CONUS_Plus/conusplus_kkl_run1/sm_response/validate_results.py::main](<../../examples/CONUS_Plus/conusplus_kkl_run1/sm_response/validate_results.py>)（L109） | EXISTS |

## SolarB8_three_singlebins_continuous_acceptance

Samples PandaX paired/US2/XENONnT. Continuous Total efficiency, explicit X-tail flat sensitivity, seven Xe isotopes, SNuDD effective two-flavor propagation recomputed at ee points, independent .12 pulls. Explicit full-rho trace v3.5 pending, not required to relabel old results.

入口：[extensions/solar_rho_snudd/experiment.py::load_snudd](<../../extensions/solar_rho_snudd/experiment.py>)。

输入：`data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json + solar_b8_nsi_2601_19883/nsi.input.json`；已有证据：`outputs/external/solar_rho_snudd/20261112_fig4_run2/NSI_RESULTS.json`。

| 步骤 | 负责内容与计算 | 输入 → 输出 | 实际Python文件与函数 | 核对结果 |
|---|---|---|---|---|
| P01 | Dataset/observable<br>读取并绑定身份、单位和bin边界 | dataset配置、数值资源与observable定义 → definition/model与paired/US2/XENONnT三个独立信号总数 | [cevns_pyeft/experiments/solar_singlebin.py::read_card](<../../cevns_pyeft/experiments/solar_singlebin.py>)（L39）<br>[cevns_pyeft/experiments/solar_singlebin.py::load_singlebin](<../../cevns_pyeft/experiments/solar_singlebin.py>)（L230） | EXISTS |
| P02 | Target/exposure<br>保留九行天然Xe丰度分母，取七个有核表的同位素，不重新归一丰度 | 同位素组成、核质量、质量/曝光定义 → TargetInventory与run/exposure | [cevns_pyeft/experiments/solar_singlebin.py::build_targets](<../../cevns_pyeft/experiments/solar_singlebin.py>)（L65） | EXISTS |
| P03 | Source/state<br>SNuDD v3.4.1有效两味绝热传播；ee NSI每点更新Pee(E)，保留显式近似 | 源能谱/谱线、源强、几何、ν/反ν与味态 → flux/fluence components与rho(E) | [cevns_pyeft/experiments/solar_singlebin.py::SourceSpectrum](<../../cevns_pyeft/experiments/solar_singlebin.py>)（L47）<br>[extensions/solar_rho_snudd/state.py::ExternalSolarState](<../../extensions/solar_rho_snudd/state.py>)（L19）<br>[extensions/solar_rho_snudd/scan.py::ScanSource](<../../extensions/solar_rho_snudd/scan.py>)（L29） | EXISTS |
| P04 | Theory/nuclear response<br>匹配粒子响应并绑定核响应 | SM/NSI LEFT系数、核响应数值与约定 → interaction及各核响应通道 | [cevns_pyeft/theory/li2026/ee_vector_nsi.py::ElectronVectorNSI](<../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>)（L48）<br>[cevns_pyeft/nuclear/response.py::ResponseDB](<../../cevns_pyeft/nuclear/response.py>)（L97） | EXISTS |
| P05 | Kinematics/cross section<br>施加精确两体运动学并计算每核微分截面 | Eν/反冲网格、核质量、入射态和interaction → dσ/dT [cm²/keV] | [cevns_pyeft/theory/li2026/ee_vector_nsi.py::spectral_coefficients](<../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>)（L79）<br>[cevns_pyeft/theory/kinematics.py::is_two_body_recoil_allowed](<../../cevns_pyeft/theory/kinematics.py>)（L40） | EXISTS |
| P06 | Detector/selection<br>continuous_acceptance积分；XENON缺尾段显式flat_sensitivity | 三样本Total效率曲线及反冲窗口 → 三个总信号接受度；不与多bin响应混用 | [cevns_pyeft/experiments/solar_singlebin.py::TotalAcceptance](<../../cevns_pyeft/experiments/solar_singlebin.py>)（L88） | EXISTS |
| P07 | Slow counts<br>直接积分能量与反冲，按源/核素分别求和 | 源、靶、dσ/dT、响应和积分网格 → SM/参数点预测 [events/bin]：paired/US2/XENONnT三个独立信号总数 | [cevns_pyeft/experiments/solar_nsi.py::NSIExecutor](<../../cevns_pyeft/experiments/solar_nsi.py>)（L101） | EXISTS |
| P08 | Fast representation<br>能量分辨核系数与每点传播相乘；弱角作用所有味，不把NSI当固定Pee二次式 | 已核查前向模型、网格、系数基和缓存身份 → 参数点快速预测及源码/输入指纹 | [cevns_pyeft/kernels/solar_nsi.py::SolarNSIKernel](<../../cevns_pyeft/kernels/solar_nsi.py>)（L32）<br>[cevns_pyeft/kernels/solar_nsi.py::compile_kernel](<../../cevns_pyeft/kernels/solar_nsi.py>)（L97） | EXISTS |
| P09 | Statistics/inference<br>拟合信号总数Gaussian；弱角/NSI独立12% pull；fB data-only和pull control分开 | 与预测同语义的观测、误差、背景、nuisance → χ²、Δχ²、最佳值和分离阈值区间 | [cevns_pyeft/statistics/solar_nsi.py::SolarNSIJoint](<../../cevns_pyeft/statistics/solar_nsi.py>)（L16） | EXISTS |
| P10 | Validation/report<br>核对回归、独立积分/核表示、来源和结果适用范围 | 当前模型、数值输出、原文/旧结果与验收范围 → 验证JSON、表格、图件与未完成能力记录 | [tools/run_solar_b8_snudd_inference.py::direct_validation](<../../tools/run_solar_b8_snudd_inference.py>)（L53） | EXISTS |

## SolarB8_multibin_separate_branch

Kept as distinct legacy multibin response. Current task requests mainline singlebin fit; no mixing Qy/Ne/cS2 observations or author fit-background histograms into that likelihood.

入口：[cevns_pyeft/experiments/solar_nuclear.py::with_solar_nuclear_response](<../../cevns_pyeft/experiments/solar_nuclear.py>)。

输入：`data/experiments/PandaX4T/PandaX4T_2024_US2 + XENONnT/XENONnT_2024_SolarB8`；已有证据：`outputs/solar_b8_sm/20261110_nuclear_response_run2/RUN_SUMMARY.json`。

| 步骤 | 负责内容与计算 | 输入 → 输出 | 实际Python文件与函数 | 核对结果 |
|---|---|---|---|---|
| P01 | Dataset/observable<br>读取并绑定身份、单位和bin边界 | dataset配置、数值资源与observable定义 → definition/model与各自Ne/cS2或真实反冲多bin | [cevns_pyeft/experiments/solar_b8.py::definition_from_solar](<../../cevns_pyeft/experiments/solar_b8.py>)（L214） | EXISTS |
| P02 | Target/exposure<br>SolarPreparation原核数→NuclearPreparation七核素筛选，不重新归一丰度 | 同位素组成、核质量、质量/曝光定义 → TargetInventory与run/exposure | [cevns_pyeft/experiments/solar_b8.py::SolarPreparation](<../../cevns_pyeft/experiments/solar_b8.py>)（L126）<br>[cevns_pyeft/experiments/solar_nuclear.py::NuclearPreparation](<../../cevns_pyeft/experiments/solar_nuclear.py>)（L167） | EXISTS |
| P03 | Source/state<br>建立相同能量轴上的源分量及入射态 | 源能谱/谱线、源强、几何、ν/反ν与味态 → flux/fluence components与rho(E) | [cevns_pyeft/experiments/solar_b8.py::SolarSpectrum](<../../cevns_pyeft/experiments/solar_b8.py>)（L25） | EXISTS |
| P04 | Theory/nuclear response<br>SolarNuclearSM沿用ResponseDB与共享振幅；保持完整SM核通道 | SM/NSI LEFT系数、核响应数值与约定 → interaction及各核响应通道 | [cevns_pyeft/experiments/solar_nuclear.py::SolarNuclearSM](<../../cevns_pyeft/experiments/solar_nuclear.py>)（L42）<br>[cevns_pyeft/nuclear/response.py::ResponseDB](<../../cevns_pyeft/nuclear/response.py>)（L97） | EXISTS |
| P05 | Kinematics/cross section<br>SolarNuclearSM.channel_dsigma计算共享振幅的精确能量二次式并施加两体端点 | Eν/反冲网格、核质量、入射态和interaction → dσ/dT [cm²/keV] | [cevns_pyeft/experiments/solar_nuclear.py::channel_dsigma](<../../cevns_pyeft/experiments/solar_nuclear.py>)（L104）<br>[cevns_pyeft/theory/kinematics.py::is_two_body_recoil_allowed](<../../cevns_pyeft/theory/kinematics.py>)（L40） | EXISTS |
| P06 | Detector/selection<br>XENON响应基底/Ne或cS2映射，或PandaX真实反冲接受度；不同输出分别保存 | 真实反冲、响应/效率数值与观测分箱 → 观测箱折叠权重/接受度 | [cevns_pyeft/experiments/solar_b8.py::XenonBasisObservation](<../../cevns_pyeft/experiments/solar_b8.py>)（L40）<br>[cevns_pyeft/experiments/solar_b8.py::RecoilAcceptanceObservation](<../../cevns_pyeft/experiments/solar_b8.py>)（L71） | EXISTS |
| P07 | Slow counts<br>直接积分能量与反冲，按源/核素分别求和 | 源、靶、dσ/dT、响应和积分网格 → SM/参数点预测 [events/bin]：各自Ne/cS2或真实反冲多bin | [cevns_pyeft/experiments/solar_b8.py::SolarExecutor](<../../cevns_pyeft/experiments/solar_b8.py>)（L166） | EXISTS |
| P08 | Fast representation<br>未登记独立Fast能力；SM能量二次式属于截面内部计算 | 此分支当前仅直接Slow合同 → NOT_IMPLEMENTED_FOR_THIS_BRANCH |  | MISSING |
| P09 | Statistics/inference<br>仅保留前向结果，不替换三单bin观测 | 此分支的谱与响应；未闭合本轮拟合背景合同 → NOT_RUN_FOR_THIS_TASK |  | MISSING |
| P10 | Validation/report<br>核对回归、独立积分/核表示、来源和结果适用范围 | 当前模型、数值输出、原文/旧结果与验收范围 → 验证JSON、表格、图件与未完成能力记录 | [tools/run_solar_b8_nuclear_benchmark.py::main](<../../tools/run_solar_b8_nuclear_benchmark.py>)（L180） | EXISTS |

## 共享理论内部链（P04–P05）

LEFT系数 → left_to_ci核子系数 → compute_R_matrices粒子响应 → flavor_kernel_onebody_li2026收缩R与W → differential_cross_section_nn按入射态取迹。正式package从NPZ构建核响应，外部ResponseDB路线则由各自显式资源装配；不能仅凭同名类判定两者读取同一文件。

- [cevns_pyeft/theory/li2026/left_to_ci.py::left_to_ci](<../../cevns_pyeft/theory/li2026/left_to_ci.py>)（L107）
- [cevns_pyeft/theory/li2026/responses.py::compute_R_matrices](<../../cevns_pyeft/theory/li2026/responses.py>)（L177）
- [cevns_pyeft/theory/li2026/amplitude.py::flavor_kernel_onebody_li2026](<../../cevns_pyeft/theory/li2026/amplitude.py>)（L85）
- [cevns_pyeft/rates/differential.py::differential_cross_section_nn](<../../cevns_pyeft/rates/differential.py>)（L360）

## 本次一维分析实际调用链

以上是各实验原前向/统计路线。下面列本轮66条扫描的实际编排；冻结核回放不冒称正式loader或原生Slow本轮重跑。

| 环节 | 当前Python | 完成内容 |
|---|---|---|
| 参数→系数 | [examples/one_d_benchmark/prediction_routes.py::coefficients](<../../examples/one_d_benchmark/prediction_routes.py>)（L39） | 弱角写入所有味的SM LEFT系数；单个实NSI经共享映射写入Wilson系数 |
| 参数→信号 | [examples/one_d_benchmark/prediction_routes.py::FrozenBilinearRoute](<../../examples/one_d_benchmark/prediction_routes.py>)（L92）<br>[examples/one_d_benchmark/prediction_routes.py::SolarRoute](<../../examples/one_d_benchmark/prediction_routes.py>)（L120） | 地面固定核全通道收缩；太阳按能量保留核并在每点重算传播 |
| 信号→χ² | [examples/one_d_benchmark/prediction_routes.py::GaussianChannel.profile](<../../examples/one_d_benchmark/prediction_routes.py>)（L54）<br>[examples/one_d_benchmark/prediction_routes.py::SolarRoute.profile](<../../examples/one_d_benchmark/prediction_routes.py>)（L189） | 按声明误差/背景profile nuisance；太阳独立pull或data-only由明确模式选择 |
| χ²→最小值/区间 | [examples/one_d_benchmark/inference.py::scan](<../../examples/one_d_benchmark/inference.py>)（L27）<br>[examples/one_d_benchmark/run_analysis.py::main](<../../examples/one_d_benchmark/run_analysis.py>)（L112） | 构造单实验/联合目标、有根据的搜索域、连续1D最小化、所有阈值根与分离区间 |
| 独立核对/出版图 | [examples/one_d_benchmark/validate_results.py::main](<../../examples/one_d_benchmark/validate_results.py>)（L22）<br>[examples/one_d_benchmark/publish.py::main](<../../examples/one_d_benchmark/publish.py>)（L44） | 解析通量、native截面、full/pair和阈值根核对；只读数值制表/出图 |

## 本次需要保留的缺口

1. CsI-time P09缺明确raw/on-off统计模型、背景绝对归一和必要不确定度；不把99箱硬套九箱Gaussian。
2. CsI2017正式YAML/NPZ被OS拒绝读取，且没有可用的已验收参数核；本次只回读SM点，不生成弱角/NSI伪扫描。
3. CsI2021/Ar的正式Package也有相同OS读取问题，本次可回放此前验证的固定核及保存的Gaussian输入；这不是本次原生loader重跑通过。
4. Ar非对称统计是另一条已存模型；本次可完整重算的是保存了全部数值输入的均误差benchmark，不能将两者混称。
5. 太阳新完整ρ/显式trace v3.5尚待实现；当前ee对角子空间采用既有经过核对的等价Pee表达，并逐点重算传播。
6. 多bin太阳仍是另一条分析；不把拟合背景、Ne/cS2输入带入本次三单bin推断。

[机器索引与源码哈希](../../outputs/one_d_benchmark_20261113_run1/ROUTE_AUDIT.json) · [逐步骤CSV](../../outputs/one_d_benchmark_20261113_run1/ROUTE_STEPS.csv)


[一维计算完整结果](../../outputs/one_d_benchmark_20261113_run1/RESULTS.md) · [实验总目录](README.md)
