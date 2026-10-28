# 源码基线与架构证据

状态：CURRENT（下列提交内的事实）。设计方案另见02–12。

## 1. 核对范围

仓库：chino616/fawenfalnjdn；目录：Gitup01；分支：conus-v2-current-snapshot-20261011。
固定提交：`e04ab7a9270380d6fd0191735c489e5b7c5fe2e4`。
本次重构文档生成前后，目标仓库没有本任务产生的代码修改。
所有源码链接固定到该提交；未来执行时必须复读当前版本，不依赖行号稳定。

主要读取：源→状态→截面→计数→Fast→统计→注册与配置，以及适用仓库工作流规则。
用户提供的五份参考Markdown仅作辅助；其中建议接口没有被当作当前API。
未将backup作为活动源码或参考来源，未把隔离候选结果当作已进入此提交的正式能力。

## 2. 已核实的主要结论

1. 理论、核响应、入射态存在实际分层和校验，是值得复用的基础。
2. CsI2021计数入口没有source/interaction/observation对象的完整替换参数。
3. 下层counts仍依赖SNS能区、分量字段和muLine结构；只换源文件不足以接入新源。
4. 探测器质量来自源对象，材料权重和选择接受率在另外的环节施加。
5. 每个PE节点调用的旧函数重复计算与PE无关的反冲谱；可在保持离散语义后提取复用。
6. Fast独立构造部分理论响应且再次选择实验输入，当前存储校验不覆盖全部物理内容。
7. 统计对象支持一维分箱信息，直接把二维数组传给旧9箱观测会不匹配。
8. 配置发现、Slow支持、Fast支持和统计支持是不同能力。

## 3. 已做的小规模运行检查

此前在同一会话、该提交上运行CsI2021粗网格（n_er=3、n_enu=6、n_pe_bin=3、pe_step=3.0）：
输出total shape为(9,)，数值有限，mu/e/mub之和等于total。
将(9,11)数组交给旧9箱PredictionVector得到 `prediction/bin mismatch: prediction=99, bins=9`。
注册发现包含CONUS+的spec，但共用get_slow_count_function没有其入口。
这些仅证明接口结构和调用行为，不证明积分收敛或实验复现精度。
曾尝试运行pytest，当前环境返回 `No module named pytest`，因此全套测试未重跑。

## 4. 源码符号锚点

以下路径和顶层符号由打包检查实际解析确认。

| 证据 | 文件与符号 | 对本方案的意义 |
|---|---|---|
| [S01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/coherent/sns.py#L23) | `src/cevns_pyeft/experiments/coherent/sns.py::SNSDataset` | 源配置中包含质量；需在新源输出中分离 |
| [S02](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/coherent/sns.py#L55) | `src/cevns_pyeft/experiments/coherent/sns.py::loadNeutrinoEmpiricalFluxSNS` | 时间积分SNS源、固定组件及单能线结构 |
| [S03](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/coherent/sns.py#L123) | `src/cevns_pyeft/experiments/coherent/sns.py::sns_component_state` | 源分量与入射态、粒子标签的现有映射 |
| [C01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py#L61) | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::slow_counts_csi2021` | 入口内固定源/靶/分箱/效率/接受率 |
| [C02](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py#L57) | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py::combine_equal_stoichiometry` | CsI材料组合权重 |
| [C03](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/rates/counts.py#L146) | `src/cevns_pyeft/rates/counts.py::empirical_dNdPE_response_csi` | 源积分、展宽和非负截断的旧顺序 |
| [C04](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/rates/counts.py#L203) | `src/cevns_pyeft/rates/counts.py::bin_events_csi` | 质量来自flux对象；PE插值后逐箱积分 |
| [C05](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/rates/counts.py#L64) | `src/cevns_pyeft/rates/counts.py::_rate_per_kg` | 共享函数含SNS端点与muLine假设 |
| [C06](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/rates/counts.py#L135) | `src/cevns_pyeft/rates/counts.py::_er_grid` | 反冲网格上限含muon-DAR假设 |
| [T01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/base.py#L11) | `src/cevns_pyeft/experiments/base.py::TargetComponent` | 旧weight未形成完整的核数合同 |
| [X01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/rates/differential.py#L356) | `src/cevns_pyeft/rates/differential.py::differential_cross_section_nn` | 现有MeV/keV截面及入射态收缩入口 |
| [X02](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/rates/differential.py#L148) | `src/cevns_pyeft/rates/differential.py::p_smearing_csi` | 实验专用响应放在rates/differential |
| [X03](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/theory/li2026/cross_section.py#L48) | `src/cevns_pyeft/theory/li2026/cross_section.py::dsigma_dER_flavor_kernel_li2026_cm2_per_GeV` | 可复用的理论内核边界 |
| [P01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/sources/state.py#L108) | `src/cevns_pyeft/sources/state.py::NeutrinoState` | 已有状态校验，但主要携带shape而非实际能量 |
| [P02](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/propagation/base.py#L21) | `src/cevns_pyeft/propagation/base.py::PropagationState` | 已有实际能量索引的传播态 |
| [K01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/kernels/builder.py#L252) | `src/cevns_pyeft/kernels/builder.py::_amplitude_kernel_by_channel` | 独立的Fast通道响应表达式 |
| [K02](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/kernels/builder.py#L307) | `src/cevns_pyeft/kernels/builder.py::_build_one_target_kernel` | Fast内执行源和探测器归一化 |
| [K03](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/kernels/builder.py#L429) | `src/cevns_pyeft/kernels/builder.py::build_matrixized_kernel` | 构建metadata与固定实验布局 |
| [K04](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/kernels/reconstruction.py#L160) | `src/cevns_pyeft/kernels/reconstruction.py::reconstruct_counts_from_kernel` | 源标签与材料布局仍有固定分支 |
| [K05](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/kernels/storage.py#L68) | `src/cevns_pyeft/kernels/storage.py::validate_fastscan_template` | 已有schema/shape校验，非完整物理指纹 |
| [L01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/statistics/observables.py#L49) | `src/cevns_pyeft/statistics/observables.py::prediction_vector` | 一维观测和数量匹配检查 |
| [L02](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/statistics/predictors.py#L77) | `src/cevns_pyeft/statistics/predictors.py::predict_raw_components` | 统计桥固定实验路由与源分量 |
| [L03](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/statistics/datasets.py#L92) | `src/cevns_pyeft/statistics/datasets.py::csi2021_dataset` | 现有近似统计数据与标签 |
| [R01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/registry.py#L35) | `src/cevns_pyeft/experiments/registry.py::get_slow_count_function` | 注册发现与实际Slow支持不同 |
| [R02](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/specs.py#L88) | `src/cevns_pyeft/experiments/specs.py::read_simple_yaml` | 简单YAML解析不是完整配置装配 |
| [G01](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py#L25) | `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py::slow_counts_csi2017` | 保护其现有14.6质量数值与PE转换 |
| [G02](https://github.com/chino616/fawenfalnjdn/blob/e04ab7a9270380d6fd0191735c489e5b7c5fe2e4/Gitup01/src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py#L25) | `src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py::slow_counts_ar2020` | 保护Ar共享rates与既有响应 |

## 5. 当前测试入口

以下文件存在并已检查其职责；“存在”不代表本轮已运行通过。

- `test_conus_plus_paper_config_guard.py`
- `test_conus_plus_source.py`
- `test_experiment_specs.py`
- `test_legacy_coherent_scalar_regression.py`
- `test_li2026_amplitude_flavor.py`
- `test_li2026_units_contract.py`
- `test_nuclear_response_convention.py`
- `test_rates_differential_flavor.py`
- `test_source_state_p2.py`

其中test_legacy_coherent_scalar_regression的计数级用例覆盖CsI2017/CsI2021；共享修改还需明确补足或运行Ar的实际计数回归。
test_experiment_specs主要验证配置发现/读取，不证明配置中的全部物理字段已被数值入口消费。

## 6. 内容指纹

用于执行前确认是否仍对应本文证据。文件改变时重新核对受影响接口，不强制将用户代码回退到旧提交。

| 相对Gitup01路径 | SHA256 |
|---|---|
| `AGENTS.md` | `2ca31e59f1961b838b40e80ca1d0e4b3ff92f0b0e1c61f2b0808aa49b6703a9d` |
| `data/experiments/CsI2021/experiment.yaml` | `3f494f4319aa8f0c189b1875b42b1cd5ad3c65d5bc5944cd71a3b83ff0a05622` |
| `data/responses/responses_all.json` | `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74` |
| `pyproject.toml` | `15b629c7f66d42b3c67edc80ecc7e989924e813d9c00efadf93662516f0f6897` |
| `src/cevns_pyeft/experiments/base.py` | `5e4b6689fcb858b88e0036ce24ee53992760cb70174221a250007c2c1433cef4` |
| `src/cevns_pyeft/experiments/coherent/slow_counts_ar2020.py` | `cea4d5a54bf39469df159ad36e914ec726e8eb8b1dea4a79ea6cb66bc2581067` |
| `src/cevns_pyeft/experiments/coherent/slow_counts_csi2017.py` | `17c2911cb604d207c29b1621cee6eb5e1fb7fcae109cf2d65e731b7242b57d9f` |
| `src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py` | `73d793e61dfa190af26ca01b1381ba4b019da07b0b95f25a5a09a99f595773c9` |
| `src/cevns_pyeft/experiments/coherent/sns.py` | `9ea97baf50e46a158680b556f9fe514502fd8ca7386d8e9ea36ed07681e7a764` |
| `src/cevns_pyeft/experiments/registry.py` | `50b0ea299899cb38a8910d631f174180c97a9dd00de65c0946b50bd711d5b318` |
| `src/cevns_pyeft/experiments/specs.py` | `5b0633166370d9ec45d06bc2f9e069a319ebca5a04c6b51c78cf070621dcdac7` |
| `src/cevns_pyeft/kernels/builder.py` | `d05411d08999f137725a80f164660837a086b07ab33d7d1916a59dce37aa14c0` |
| `src/cevns_pyeft/kernels/reconstruction.py` | `1d3ef686e45cae01f4a481532d7a025358400496e445b9707093a66400cca1ad` |
| `src/cevns_pyeft/kernels/storage.py` | `86ab01e539701fe496ad937c6f53e4fd5285ba229e93424d778e6ad7c8ccbbaf` |
| `src/cevns_pyeft/propagation/base.py` | `f1e531e91d96ffbc1ae46f855897a5c3793fa280f904d0e61c08e8b4b46eab0a` |
| `src/cevns_pyeft/rates/counts.py` | `776630b714f3cc0b03fab897a4b4a34d25812744728654f38c4ab8ad2ea17733` |
| `src/cevns_pyeft/rates/differential.py` | `d7e7c42c6eb92202e52524447328521c71c3a1050b4e93b6acc5adf9a16a85ce` |
| `src/cevns_pyeft/sources/state.py` | `39ae30776f58bb19c15e842317940cb3aece2040eabb19046d01842e55815100` |
| `src/cevns_pyeft/statistics/datasets.py` | `20d1ff2f0811144844b8cf7883020907a5f2969be949f101253444237694b455` |
| `src/cevns_pyeft/statistics/observables.py` | `562a18e77e4b0f75666847d220f785e6c54b99df436f014e203f76ef05109941` |
| `src/cevns_pyeft/statistics/predictors.py` | `78a50e586342d82c38d797aa306c714a9dc91b5dac64ec9bb3693575b7b90ba3` |
| `src/cevns_pyeft/theory/li2026/cross_section.py` | `adc13f3e1acc9b88b85fc033a6117cc2f99a77d1bc88e66368e416e4f5304393` |
| `tests/test_conus_plus_paper_config_guard.py` | `1b6321072f0bd0d4b743ed0d9c19cf13f8a0769587b419196cd2bd7e569bbcd9` |
| `tests/test_conus_plus_source.py` | `e1636777bbf15cb989a52590c0d9c805fa85e7cd372653e969a3403b357b8dec` |
| `tests/test_experiment_specs.py` | `0cee22e047549e7a758cf7b7b17460e3338e098f68829893b4dc33257dc95d56` |
| `tests/test_legacy_coherent_scalar_regression.py` | `0772afb1cd7d0a7d1fb2791104aa8aa6029c05253e874f036c843f831fed32e6` |
| `tests/test_li2026_amplitude_flavor.py` | `774fff2266bca6d1fe74211e63686d8adb37e4e7ea2231b8997b5be6ec581af0` |
| `tests/test_li2026_units_contract.py` | `99250f87fd1826c942e6843f55d46c03f71e4b499ebad99fc3fea6ec2cf14e67` |
| `tests/test_nuclear_response_convention.py` | `08292127e16a2df037ca7672d534193a2720aa756eae90b8309667d3d788620c` |
| `tests/test_rates_differential_flavor.py` | `27ae7e88d506af48175e88e90562a6c2437f1f8feef660bd531cefff34be08bf` |
| `tests/test_source_state_p2.py` | `e2f1c39cd64cf9208ae9548de26be85c850ca085450005050e67ab05b82f1bca` |
| `workflows/experiment-integration/AGENTS.md` | `342f9501c6e4fa82f6e5d66359ec1614dac9821cf4ad99bbb9d62f8b85887697` |
| `workflows/experiment-integration/_shared.md` | `61f759b82d3ae7f1ad7bb689d6d2b941d602832f1f0d4d18ff7a1acf5d188049` |
| `workflows/experiment-integration/skills/cevns-experiment/SKILL.md` | `881ea7a67e2e70570a989efb97988d1148246bdfcb8b7cc35a48a9a7553823a6` |
