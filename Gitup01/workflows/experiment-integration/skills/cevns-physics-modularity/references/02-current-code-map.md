# 02 当前代码地图：具体替换位置与交叉依赖

状态均针对检查日期的活动代码，不包含 backup。`文件.py::符号` 是可由配套脚本核对的源码锚点。
路径相对仓库根目录；函数签名、调用方和当前行号须在实际执行替换时复读。

## 1. 实际参数来源与配置消费

| 物理责任 | CURRENT 锚点 | 实际作用与替换注意 |
| --- | --- | --- |
| C00 参数结构 | `src/cevns_pyeft/experiments/coherent/sns.py::SNSDataset` | 只定义 name、质量、基线、POT、r、能量区间等字段；不计算源谱 |
| S02/T02 具体值 | `src/cevns_pyeft/experiments/coherent/sns.py::SNS_DATASETS` | 三个实验的实际 Python 实例；当前第 33 行。修改这里才会改变 SNS loader 读取的值 |
| C00 spec 发现 | `src/cevns_pyeft/experiments/specs.py::load_experiment_spec` | 读取 spec 为 ExperimentSpec，不能据此认定每个物理函数消费了 spec |
| C00 YAML 解析 | `src/cevns_pyeft/experiments/specs.py::read_simple_yaml` | 仅支持实现中的简化 YAML 子集，不是完整 YAML schema 验证器 |
| T01 靶结构 | `src/cevns_pyeft/experiments/base.py::TargetComponent` | 存 name、response_key、weight；当前 COHERENT 仍有自行写死的 target tuple |
| T02 实验结构 | `src/cevns_pyeft/experiments/base.py::ExperimentConfig` | name、dataset、detector_mass_kg；不能当成已贯通全部调用链的总配置 |
| C00 单位 | `src/cevns_pyeft/foundation/constants.py::to_energy_gev`、`src/cevns_pyeft/foundation/constants.py::from_energy_gev` | 当前 GeV/MeV/keV 边界；其它单位变换在同文件 |
| E08 单位 | `src/cevns_pyeft/foundation/units.py::cm2_per_GeV_to_cm2_per_keV` | 微分截面乘 1e-6；不能反向乘 1e6 |

当前 CsI2021 的 `data/experiments/CsI2021/experiment.yaml` 记录了 source/detector/exposure/binning/callables，
但 slow_counts_csi2021 不调用 spec loader。修改 YAML 只有在新增消费桥接后才会改变这条数值路径。
同理，`data/datafiles/SNSflux_nue.txt`、`SNSflux_numu.txt`、`SNSflux_numub.txt` 的存在不意味着 SNS 解析 loader 正在读表。

## 2. S 源、P 入射态、传播

| ID | CURRENT 锚点 | 内容、单位及依赖 |
| --- | --- | --- |
| S01 | `src/cevns_pyeft/experiments/coherent/sns.py::_michel_nue_spectrum` | νe 谱形，输入 MeV；改变仅属于此源物理 |
| S01 | `src/cevns_pyeft/experiments/coherent/sns.py::_michel_numubar_spectrum` | 反νμ 谱形；与 νe 不同 |
| S02 | `src/cevns_pyeft/experiments/coherent/sns.py::_n_time_integrated_flux_cm2` | r×POT/(4πL²)，L 转 cm，输出 cm^-2 |
| S03/S04 | `src/cevns_pyeft/experiments/coherent/sns.py::loadNeutrinoEmpiricalFluxSNS` | 默认 200 点/线性插值；measured.e/mub 单位 cm^-2 MeV^-1；muLine=(MeV,cm^-2) |
| S04 | `src/cevns_pyeft/experiments/coherent/sns.py::_make_interp` | 域外取零，内部按原 tabulation 插值；不自动重新施加理论端点 |
| S04 | `src/cevns_pyeft/rates/differential.py::emax_muon_dar_mev` | μ 静止衰变端点；不能把它改成反应堆端点，需替换调用方的源范围来源 |
| P01/P02 | `src/cevns_pyeft/experiments/coherent/sns.py::sns_component_state` | mu/e/mub → 纯态 mu/e/mu 与 nu/nu/antinu；固定 SNS 映射 |
| P02 | `src/cevns_pyeft/sources/state.py::NeutrinoState` | 只封装 particle_kind 与 rho，不含 flux 或具体能量值 |
| P02 | `src/cevns_pyeft/sources/state.py::NeutrinoState.density_for_energy_shape` | 常量广播，带能量轴必须 shape 一致；不做插值/能量值校验 |
| P02 | `src/cevns_pyeft/sources/state.py::validate_density_matrices` | 每个 rho 有限、Hermitian、PSD、trace=1，失败报错，不自动归一化 |
| P02 | `src/cevns_pyeft/theory/li2026/flavor.py::FLAVOR_ORDER` | (e,mu,tau)；改变需审计整个 flavor 约定与缓存 |
| P03 | `src/cevns_pyeft/propagation/base.py::PropagationState` | 保存 energy_GeV、rho、particle_kind、basis/unit |
| P03 | `src/cevns_pyeft/propagation/backends/snudd.py::SNuDDSolarDensityBackend.density` | 调用外部 calculator.density，输出传播态；不返回 CEvNS 率 |
| P03 | `src/cevns_pyeft/propagation/density.py::wilson_np_to_vector_nsi` | NP-only C6u1/C6d1 → epsilon，拒绝 sm_plus_np；与检测 SM 合并分开 |

P01 当前限制：particle_kind 尚不切换相互作用核。只改变标签不能建立新的反ν物理能力。
P03 当前不会自动接入 COHERENT 的纯态 SNS 循环；调用后端存在不等于某实验已使用它。

## 3. T 靶核、E 理论与截面

| ID | CURRENT 锚点 | 替换责任和保持的契约 |
| --- | --- | --- |
| T03 | `src/cevns_pyeft/nuclear/response.py::ResponseDB` | 读取 data/responses/responses_all.json，不计算核多体结构 |
| T03 | `src/cevns_pyeft/nuclear/response.py::ResponseDB.get` | 按 key 选择核素；Cs133、I、Ar40 是当前 COHERENT keys |
| T03 | `src/cevns_pyeft/nuclear/response.py::ResponseW.W_np` | 原始 (p,n) 2×2 exp(lambda*y)×poly；别把 np 名称解释为 (n,p) |
| T03 | `src/cevns_pyeft/nuclear/response.py::np_to_iso_matrix` | B^T W B；与 ci isospin 定义成对更改 |
| T03 | `src/cevns_pyeft/foundation/constants.py::y_from_qb` | 振幅路径用的 y=(qb/2)²；response.py 另有同名职责，Fast 还内联一次 |
| E01 | `src/cevns_pyeft/theory/li2026/operators.py::LI2026_OPERATOR_SPECS` | 当前 active 22 个 LEFT 结构、维数和 sector |
| E01 | `src/cevns_pyeft/theory/li2026/operators.py::canonicalize_wilson_coefficients` | 字符串/tuple 键统一、重复项拒绝、矩阵验证 |
| E01 | `src/cevns_pyeft/theory/li2026/operators.py::validate_operator_coefficient` | 形状/有限性/LNV 零对角；不检查完整反对称性 |
| E02 | `src/cevns_pyeft/rates/differential.py::_sm_left_dim6` | SM flavor 单位阵系数、sW²、轴流符号 |
| E02 | `src/cevns_pyeft/rates/differential.py::_build_total_left_hat` | NP+SM 在双线性之前合并；低层 amplitude 不自动加 SM |
| E03 | `src/cevns_pyeft/theory/li2026/lec.py::Li2026LECs` | LEC 和质量值、量纲，default 对象供匹配使用 |
| E03 | `src/cevns_pyeft/theory/li2026/left_to_ci.py::_safe_div_by_q2` | photon pole 边界处理；不是完整红外正则化模型 |
| E03 | `src/cevns_pyeft/theory/li2026/left_to_ci.py::_safe_pion_pole` | pion pole 与 invariant q² |
| E04 | `src/cevns_pyeft/theory/li2026/left_to_ci.py::left_to_ci` | 输出 CiPN.p/n/iso，14 个系数；对核子而非整核做匹配 |
| E05 | `src/cevns_pyeft/theory/kinematics.py::minimum_neutrino_energy_GeV` | 精确 Emin(T) |
| E05 | `src/cevns_pyeft/theory/kinematics.py::two_body_recoil_max_GeV` | 精确 Tmax(E) |
| E05 | `src/cevns_pyeft/theory/kinematics.py::is_two_body_recoil_allowed` | 支撑判断；同模型应复用而非实验各写一个端点 |
| E05 | `src/cevns_pyeft/theory/li2026/left_to_ci.py::_resolve_kinematics` | q0/q2/qabs/qabs2 一致性与兼容参数；不能替代 caller 的物理选择 |
| E06 | `src/cevns_pyeft/theory/li2026/responses.py::_ord` | ci†cj；不是逐元素乘法 |
| E06 | `src/cevns_pyeft/theory/li2026/responses.py::NR_SECTOR` | 核子系数的 LNC/LNV sector |
| E06 | `src/cevns_pyeft/theory/li2026/responses.py::responses_R` | 粒子响应公式，SigmaPDelta=0 |
| E06 | `src/cevns_pyeft/theory/li2026/responses.py::compute_R_matrices` | 返回每通道 (3,3,2,2)，组装 flavor 与核子轴 |
| E07 | `src/cevns_pyeft/theory/li2026/amplitude.py::flavor_kernel_onebody_li2026` | 构造近似 q、匹配、R、W、y 和最终 K；当前 norm caveat 必须保留 |
| E07 | `src/cevns_pyeft/theory/li2026/amplitude.py::_contract_R_W` | einsum 收缩核子轴，保留 flavor 矩阵 |
| E08 | `src/cevns_pyeft/theory/li2026/cross_section.py::amplitude_kernel_to_dsigma_cm2_per_GeV` | 相空间因子和面积换算 |
| E08 | `src/cevns_pyeft/theory/li2026/cross_section.py::dsigma_dER_for_density_li2026_cm2_per_GeV` | core 的直接 density 截面 API；E 用 GeV，输出 cm²/GeV |
| E08 | `src/cevns_pyeft/rates/differential.py::differential_flavor_kernel_nn` | rates 接口：E 用 MeV，T 用 keV，返回 cm²/keV kernel |
| E08 | `src/cevns_pyeft/rates/differential.py::differential_cross_section_nn` | 解析 NeutrinoState、匹配能量 shape、Tr(rho K)、诊断 |
| P02/E08 | `src/cevns_pyeft/theory/li2026/flavor.py::contract_density_kernel_grid` | 逐能量收缩，校验矩阵 Hermitian/PSD 和标量结果 |
| H01 | `src/cevns_pyeft/theory/helm/form_factor.py::helm_form_factor_squared` | Helm F²，独立近似分支 |
| H01 | `src/cevns_pyeft/theory/helm/cross_section.py::dsigma_dER_helm_density_cm2_per_GeV` | Helm+flavor 截面，需检查支持的模型及 kinematics |

### 不应误认为主链的对象

- `src/cevns_pyeft/foundation/constants.py::SMEFT_TO_LEFT_TREE` 和 `src/cevns_pyeft/foundation/constants.py::LEFT_QCD_RUNNING`：公式/分类元数据，未发现可执行 RG/matching 驱动。
- `src/cevns_pyeft/theory/li2026/form_factors.py::build_form_factors`：存在并被兼容重导出，但当前 amplitude→left_to_ci 主链没有调用它；只修改此文件通常不改变 COHERENT 主计算。
- `src/cevns_pyeft/core/engine.py`：兼容重导出入口；实施修改应追到真实 owner，避免制造第二份实现。
- 外部 W 规范未闭合： [核响应审计](../../../../../docs/nuclear_response_convention_audit.md)。

## 4. D 探测器与 I 计数

| ID | CURRENT 锚点 | 当前责任和专有假设 |
| --- | --- | --- |
| D01 | `src/cevns_pyeft/rates/differential.py::eee_quenching_csi` | CsI 经验 quenching，输入 keVnr、输出 keVee |
| D02 | `src/cevns_pyeft/rates/differential.py::p_smearing_csi` | CsI gamma PE 密度；默认函数绑定在 counts 的参数上 |
| D03 | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::CsI2021EfficiencyParams` | CsI2021 效率参数对象，默认实例已绑定 |
| D03 | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::efficiency_csi2021` | ε(PE) sigmoid 及非负截断 |
| D04 | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::DEFAULT_ACCEPTANCE` | e/mu/mub 组件接受率，不是 PE 效率 |
| D05 | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::PE_BINS_9` | 9-bin PE edges；统计 datasets.py 也有一份，需同步 |
| T01/I03 | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::combine_equal_stoichiometry` | 133/260、127/260 权重；输入为每种纯靶按整台质量归一化的 raw |
| I01 | `src/cevns_pyeft/rates/counts.py::_choose_phi_cont` | SNS e/mub 连续谱、mu 返回零；不接受任意分量 |
| I01 | `src/cevns_pyeft/rates/counts.py::_rate_per_kg` | 固定 μ 端点和 muLine，输出每 kg 反冲产额；CsI2017 直接用，Ar2020 间接用 |
| I02/I03 | `src/cevns_pyeft/rates/counts.py::_folded_counts` | 反冲产额×fold 求和×探测器质量；fold 的 dT/效率归属需核对 |
| I01 | `src/cevns_pyeft/rates/counts.py::_er_grid` | T 从 0.1 keV 到 μ 端点推得的 Tmax，返回梯形权重 |
| I01/I02 | `src/cevns_pyeft/rates/counts.py::empirical_dNdPE_response_csi` | 固定 PE，逐 T 计算截面和源积分，乘 smearing 后积分 T；此路径自己写了源选择与端点 |
| I02/I03 | `src/cevns_pyeft/rates/counts.py::bin_events_csi` | PE 谱采样→插值→ε×bin 积分→探测器质量；不含 Cs/I 权重和 a_s |
| I03/I04 | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::slow_counts_csi2021` | 6 次 source×target 分箱→Cs/I 权重→a_s→total→counts/PE |
| I03 | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py::slow_counts_csi2017` | 直接用 _rate_per_kg；PE=1.17T、效率表、14.6 kg 与 Jacobian |
| I02 | `src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py::slow_counts_ar2020` | 自建平均映射/高斯 fold、效率表，再调用 _folded_counts |
| D03 | `src/cevns_pyeft/experiments/base.py::_interp_eff` | 旧效率表装载、排序、去重、边界；规则需按新标定数据复核 |

### CsI2021 的精确调用顺序

```text
registry.get_slow_count_function("CsI2021") → 返回 slow_counts_csi2021
  ResponseDB + loadNeutrinoEmpiricalFluxSNS
  for source in mu,e,mub:
    for target in Cs133,I127:
      bin_events_csi
        PE_grid 上逐点 empirical_dNdPE_response_csi
          T_grid 上逐点 differential_cross_section_nn
            differential_flavor_kernel_nn
              _build_total_left_hat → flavor_kernel_onebody_li2026
                left_to_ci → compute_R_matrices → R/W 收缩
              相空间/单位
            density_for_energy_shape → Tr(rho K)
          E 积分 + prompt 线 → 除单核 kg 质量
          T 积分×smearing → 每 kg PE 谱
        插值→ε→bin 积分→乘 14.57 kg
  Cs/I 质量权重 → a_s → 源分量相加 → 除 bin width
```

上图 density_for_energy_shape 实际在 differential_cross_section_nn 调用 kernel 前解析，Tr 在其后；
箭头表示数据依赖而非改变源码的逐行顺序。CsI2021 **不经过 _rate_per_kg**。

默认 PE_step=3 时谱网格 21 点；n_pe_bin 是每个 bin 的求积点数。
每个 PE 点重复算反冲谱是当前 Slow 的实现特征，不是物理模块必须这样嵌套。

## 5. F Fast 构建、代数重建和缓存

| ID | CURRENT 锚点 | 实际角色 |
| --- | --- | --- |
| F01 | `src/cevns_pyeft/kernels/basis.py::li2026_left_basis` | 22 个 LEFT 结构及顺序；与 operator registry 双处维护 |
| F03/E02 | `src/cevns_pyeft/kernels/basis.py::coeff_tensor_from_triplets` | 构造 (B,3,3) 总系数；在此为 Fast 加入 SM |
| F01 | `src/cevns_pyeft/kernels/builder.py::_build_ci_units` | 对各单位系数模板匹配，使用 DEFAULT_LECS |
| F01 | `src/cevns_pyeft/kernels/builder.py::_amplitude_kernel_by_channel` | **重复实现**粒子响应公式；不是直接调用 responses_R |
| F02/D | `src/cevns_pyeft/kernels/builder.py::_build_target_static` | q、W、T 网格、CsI PE fold；源端点和探测器均内联 |
| F02 | `src/cevns_pyeft/kernels/builder.py::_build_one_target_kernel` | SNS 源和 E 积分→每 kg→fold→质量→a_s，构成已积分 H |
| F02 | `src/cevns_pyeft/kernels/builder.py::_build_one_target_kernel_csi2017_ar` | 另一路 SNS E 积分；由 2017/Ar 专用 fold 调用 |
| F02 | `src/cevns_pyeft/kernels/builder.py::build_matrixized_kernel` | 选靶、保存 full/diag/pair 模板和元数据 |
| F02 | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py::build_fast_kernel_csi2021` | 传 dataset、PE bins、接受率、target_mode='all' |
| F02/D | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2017.py::_csi2017_fold` | CsI2017 PE=1.17T fold 的 Fast 对应实现 |
| F02 | `src/cevns_pyeft/experiments/coherent/fast_kernel_csi2017.py::build_fast_kernel_csi2017` | 两核素构建、14.6 kg、CsI 组合 |
| F02/D | `src/cevns_pyeft/experiments/coherent/fast_kernel_ar2020.py::_ar_fold` | Ar 平均响应、宽度、效率的 Fast 对应实现 |
| F02 | `src/cevns_pyeft/experiments/coherent/fast_kernel_ar2020.py::build_fast_kernel_ar2020` | 单靶 Ar40、24 kg |
| F03 | `src/cevns_pyeft/kernels/reconstruction.py::coefficient_bilinear` | Tr(rho C_I†C_J)，rho 只能单个 (3,3) |
| F03 | `src/cevns_pyeft/kernels/reconstruction.py::reconstruct_from_full_kernel_flavor` | full H 与每源 B_IJ 收缩；保持目标/source/channel/bin |
| F03 | `src/cevns_pyeft/kernels/reconstruction.py::reconstruct_from_pair_templates_flavor` | diag/re/im 模板重建 |
| F03 | `src/cevns_pyeft/kernels/reconstruction.py::source_density_for_fast_flavor` | 固定 SNS/纯味映射，mub→mu；不做反ν振幅变换 |
| F03/I04 | `src/cevns_pyeft/kernels/reconstruction.py::reconstruct_counts_from_kernel` | source keys 固定 mu/e/mub，合并 CsI 或单靶、输出 counts/PE |
| F04 | `src/cevns_pyeft/kernels/builder.py::_kernel_to_diag_pair_templates` | pair_im=-Im(H_ab)；与重建正号成套 |
| F04 | `src/cevns_pyeft/kernels/storage.py::validate_fastscan_template` | schema/flavor/basis/shape/dataset 检查；不是完整物理输入指纹校验 |
| F04 | `src/cevns_pyeft/kernels/storage.py::DATASETS` | 当前存储只列 CsI2021/CsI2017/Ar2020；新 dataset 名字也需处理 |
| F04 | `src/cevns_pyeft/kernels/storage.py::save_fastscan_template` | npz+json 元数据，不自动重新积分 |
| F04 | `src/cevns_pyeft/kernels/storage.py::reconstruct_saved_kernel` | 读取既有 H→合并系数→重建，不重新读取新 flux 计算 H |

只有改 Wilson 数值而 H 的其它构建输入保持不变时，才属于这种 Fast 的通常扫描用途。
固定 rho 改变可以通过低层可传 source_rhos 的 API 重算双线性，但高层 reconstruct_counts_from_kernel 仍使用固定源映射；
能量依赖 rho 或 source IDs 改变需要另一契约。不能概括为“所有 rho 改变都一定重建 H”，也不能说“都只改 B”。

## 6. L 统计、O 路由与结果

| ID | CURRENT 锚点 | 当前责任和耦合 |
| --- | --- | --- |
| I04/L01 | `src/cevns_pyeft/statistics/observables.py::PredictionVector` | 预测值、观测量、bin 和 metadata |
| L01 | `src/cevns_pyeft/statistics/observables.py::convert_prediction_to_dataset_observable` | events/bin 到 counts/PE 等明确变换；要求 edges 一致 |
| L01 | `src/cevns_pyeft/statistics/datasets.py::BinnedDataset` | observed/background/uncertainty/pulls/provenance |
| L01 | `src/cevns_pyeft/statistics/datasets.py::csi2021_dataset` | 硬编码 legacy 9-bin excess/background/uncertainty，不是自动官方 likelihood |
| L01 | `src/cevns_pyeft/statistics/datasets.py::csi2017_dataset` | 读取 COHERENT_data/lower/upper/spectrum 文本 |
| L01 | `src/cevns_pyeft/statistics/datasets.py::ar2020_dataset` | legacy Ar 数值；slow_counts_ar2020 也有重复常数 |
| L02 | `src/cevns_pyeft/statistics/likelihoods.py::chi2_for_dataset` | 按 dataset 名字分发模型，不能仅塞入新名字 |
| L02 | `src/cevns_pyeft/statistics/profiling.py::profile_gaussian_two_pull` | Gaussian 双归一化 pull；使用前确认数据和误差模型 |
| L02 | `src/cevns_pyeft/statistics/profiling.py::profile_ar2020_irls` | Ar 特有不对称误差 profile；不可当通用 Poisson |
| L03 | `src/cevns_pyeft/statistics/scans.py::scan_grid_1d` | 参数网格与统计函数分离 |
| L03 | `src/cevns_pyeft/statistics/confidence.py::extract_intervals` | Δχ² 区间提取；阈值选择仍需独立物理/统计定义 |
| O01 | `src/cevns_pyeft/experiments/registry.py::get_slow_count_function` | 返回现有函数，不通过 YAML 自动生成新实验计数 |
| O01/I04 | `src/cevns_pyeft/statistics/predictors.py::predict_raw_components` | 当前三 dataset 分发，要求 e/mu/mub/total 键，观测量固定 PE |
| E01/L | `src/cevns_pyeft/statistics/parameters.py::vector_nsi_to_np_wilson` | epsilon 到 NP Wilson 的模型转换；不要把统计参数转换与 source 混在一起 |

## 7. 散落假设清单：换模块前必须搜调用方

| 想替换的物理量 | 一起检查的位置 |
| --- | --- |
| 源能量范围 | sns loader 的 tabulation/mask；counts 的 _rate_per_kg/_er_grid/empirical；builder 的 _build_target_static 与两条 E 积分路径；实验专有反冲网格 |
| 源分量 ID/数量 | sns_component_state；counts 的两套源选择；Slow loops；builder.FLAVORS/_choose_phi_cont；reconstruction.source_density_for_fast_flavor/reconstruct_counts_from_kernel；storage source 轴；predictors 固定键 |
| 粒子响应公式 | theory/li2026/responses.py 与 kernels/builder.py 内联副本；另查对照模型 |
| 质量 | SNSDataset；每 kg 的 A*amu；运动学 A*AMU_GEV；CsI2017 14.6 kg；Ar24 kg；Fast 对应路径；spec 重复值 |
| CsI 效率/响应 | slow_counts_csi2021；rates/differential；counts 默认绑定；builder 导入别名/默认函数；已保存 fold/H |
| bins | Slow constants；Fast constructor；storage arrays；statistics/datasets；观测值/背景/协方差；图的宽度约定 |
| LEC | Li2026LECs；left_to_ci/amplitude/cross_section 默认绑定；rates wrapper 是否透传；builder DEFAULT_LECS |
| ρ(E) | NeutrinoState 的 shape；实际积分子网格；线能量取值；传播参数；Fast 固定 rho 契约 |

`rg` 找到定义后再查引用，不能只替换第一个出现的名字。Python 默认函数参数和 `from module import symbol`
可能已经绑定旧对象；运行 Notebook 时应显式构造/传参或在适当范围重新加载，避免依靠 monkeypatch 判断生产路径。
