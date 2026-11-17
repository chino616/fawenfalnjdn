# 太阳⁸B SNuDD外部传播 onboarding v3.4（新版本／主线接入核对版）

**2026-11-12。SNuDD已经安装到独立环境，外部ρ已接入标准PreparedExperiment → predict/compile/evaluate，并完成实际三样本点基准。** 此版与本地B16-MSW v3.3并列，保留原SM、多bin与V/B−L。科学结果接受NOT_REVIEWED；不是完整三味演化，也没有把本次适配器验收称为新Fig.4精确复现。

[实际来源/参数卡](<../../../../extensions/solar_rho_snudd/snudd.input.json>) · [实际结果与验收](<../../../../outputs/external/solar_rho_snudd/20261112_run1/README.md>) · [安装/接口入口](<../../../../extensions/solar_rho_snudd/README.md>) · [已修订原方案](<../../../../../重构/2026-11-12_EXTERNAL_SNUDD_ADAPTER_ONBOARDING.md>)

<a id="toc"></a>

## 目录

- [版本、范围与实际安装](#status)
- [Source：绝对通量与外部传播数据](#source)
- [传播：实际参数、近似及NSI映射](#oscillation)
- [文件契约、能量网格与缓存](#protocol)
- [Target与原子核Response](#target)
- [Detector与Observable](#detector)
- [Prediction与Statistics：怎样真正进入Runtime](#prediction)
- [实际基准、差异及验收](#results)
- [程序对应与复算](#code)
- [能力边界和来源缺口](#limits)
- [标准文献与固定上游原件](#references)

<a id="status"></a>

## 版本、范围与实际安装

| 对象 | 实际位置/数值 | 核验范围 |
|---|---|---|
| 官方源码 | [.externals/SNuDD](<../../../../.externals/SNuDD/README.md>)；commit `11622ded104994959a649d85e263c2d9f933ea74` | 先固定commit再安装；checkout跟踪文件逐项hash；未改上游源码 |
| 独立Python | [.venvs/snudd](<../../../../.venvs/snudd/pyvenv.cfg>)；Python3.11.15 | 外部子进程独立依赖；主项目依赖列表未改 |
| 实际依赖 | snudd=1.0.0; numpy=2.4.6; scipy=1.17.1; pandas=3.1.1; packaging=26.3 | [完整锁定列表](<../../../../extensions/solar_rho_snudd/requirements.lock.txt>)；pip check通过；上游漏声明packaging，独立补齐 |
| 主进程隔离 | False | 运行真实基准后sys.modules未包含snudd；原cevns_pyeft/*.py保持原字节 |
| 接入范围 | ee-only实数uV/dV；日间太阳传播；单bin三样本 | 独立scoped Catalog及分析指纹；原默认实验列表和入口不变 |


第一次安装使用既有清华镜像未取得构建依赖，改用官方PyPI成功；随后import检查发现packaging遗漏并补齐。[主安装报告](<../../../../outputs/external/solar_rho_snudd/20261112_run1/INSTALL_REPORT.json>)、[补依赖报告](<../../../../outputs/external/solar_rho_snudd/20261112_run1/INSTALL_PACKAGING_REPORT.json>)保留实际轮子下载URL和hash。[software] AMARAL D W P, CERDEÑO D, CHEEK A, COSTA V, FOLDENAUER P. SNuDD: Solar Neutrinos for Direct Detection[EB/OL]. arXiv:2607.22817v1, 2026. SolarDensityMatrixCalculator.density_mass/density; ProbabilityCalculator._cos_matter_average; direct adopted software, effective two-flavor and mass-decohered flavor reconstruction。

[返回目录](#toc)

<a id="source"></a>

## Source：绝对通量与外部传播数据

通量仍为所有活跃味合计的地球处⁸B通量：$d\phi_{\rm total}/dE=\Phi_{8B}f_{8B}(E)$。SNuDD只提供无量纲传播态，不提供本次计算的源强、散射截面、核模型或探测器效率。

| 输入 | 实际数值/shape与单位 | 本地文件、直接来源和核验范围 |
|---|---|---|
| 总通量 | 固定5.46×10⁶ cm⁻²s⁻¹ | [只读基础卡](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/analysis.input.json>)；Li et al.,2409.04703v2 p5 Eq.(29)；沿用v3.3项目选择 |
| 中微子能谱 | 829×2；0–16.56MeV；f单位MeV⁻¹；原网格积分0.999986544 | [原Bahcall表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/b8_source.txt>)；Bahcall et al.,PRC54(1996)411，DOI10.1103/PhysRevC.54.411；官网829行前两列，保留舍入和线性插值 |
| 电子/中子密度 | 解析拟合；ne/N_A、nn/N_A单位mol/cm³；系数见下式 | [实际solar_profiles.py](<../../../../.externals/SNuDD/snudd/nsi/solar_profiles.py>)；[density]。直接采用软件拟合，未认证与原论文每个拟合数字等价 |
| ⁸B产生位置 | [96, 2]；x=0–0.17；max=18.3642858；原表积分=0.999368247 | [实际96×2原表](<../../../../.externals/SNuDD/snudd/data/flux_distributions/8B_dist.txt>)；表头标注[production]；未标为B16发布表 |
| 实际产生区求积 | 0–0.35Rsun，1000等距点；原表线性插值、域外0；按dr归一，不乘r² | [_cos_matter_average](<../../../../.externals/SNuDD/snudd/nsi/nsi_probabilities.py>)；直接软件约定 |
| 诊断数组 | [1000, 4]；首行0, 107.151931, 52.480746, 0 | [x/ne/nn/产生区诊断](<../../../../outputs/external/solar_rho_snudd/20261112_run1/source_evidence/snudd_profile_diagnostic.txt>)；由实际SNuDD函数求值，并非新输入表 |


实际采用的密度函数（[density]直接源码；x=r/Rsun）：

$$
\log_{10}(n_e/N_A)=2.36-4.52x-0.33\exp[-(x/0.075)^{1.1}],\qquad
\log_{10}(n_n/N_A)=1.72-4.80x.
$$

原v3.3的PEANUTS＋Magnus/B16四列表不参与SNuDD传播。本轮替换同时改变太阳密度/产生区方案；新旧Pee差异不应全部归于求解算法精度。全部直接软件文件、版本和哈希由参数卡登记；原论文与软件转录的独立认证保持单列，不用软件hash冒充原文认证。


[density] BAHCALL J N, SERENELLI A M, BASU S. 10,000 Standard Solar Models: a Monte Carlo Simulation[J]. Astrophysical Journal Supplement, 2006,165:400-431. DOI:10.1086/504043. arXiv:astro-ph/0511337. log10_electron_density, log10_neutron_electron_density; e1..e5,n1,n2; adopted software fits, not B16 arrays。

[production] LOPES I, TURCK-CHIÈZE S. Solar neutrino physics oscillations: Sensitivity to the electronic density in the Sun’s core[J]. Astrophysical Journal,2013,765:14. DOI:10.1088/0004-637X/765/1/14. arXiv:1302.2791. raw two-column file header identifies1302.2791; flux_dists.interpolate_dist linear, outside0; native distribution normalized in dr over0-.35 by propagation code。

[返回目录](#toc)

<a id="oscillation"></a>

## 传播：实际参数、近似及NSI映射

| 参数 | 实际采用值 | 来源/选择 |
|---|---|---|
| θ12 | 0.583638rad | 沿用v3.3 PEANUTS项目输入，显式传入，不用SNuDD默认33.68deg |
| θ13 | 0.149575rad | 沿用v3.3 PEANUTS项目输入，显式传入 |
| Δm²21 | 7.42e-05eV² | 沿用v3.3的7.42e−5；传给SNuDD换为GeV² |
| θ23 / δCP / Δm²31 | 43.3deg / 212deg / 0.002513eV² | [remaining_oscillation]固定软件默认；当前ee-only散射下μτ分配不影响事例数，Δ31用于近似有效性诊断 |
| 传播近似 | 两味有效绝热太阳模型，质量相位平均后UρmassU†重建味矩阵；日间，无地球再生 | [software]SolarDensityMatrixCalculator；不是完整三味太阳数值演化 |


NSI从项目的实数eu、ed映射到SNuDD因子化参数：$\epsilon_p=2eu+ed$、$\epsilon_n=eu+2ed$，$s=\sqrt{\epsilon_p^2+\epsilon_n^2}/\sqrt5$，$\eta=\operatorname{atan2}(\epsilon_n,\epsilon_p)$，$\varphi=0$，$\epsilon_{\rm matrix}=\operatorname{diag}(s,0,0)$。零点定义η=0。GeneralNSI中的ξp、ξn与矩阵相乘后分别恢复上述质子/中子耦合；ξe=0。只传NP epsilon，SNuDD自行包含标准物质势，不能把SM+NP总Wilson系数再当作NP输入。

输出完整rho在味基底(e,mu,tau)保存，包含实际非对角元。当前散射核为diag(σe,σSM,σSM)，因此只用rho_ee与对角等价投影不会改变本子空间事件数；这项等价不推广到非对角/复数NSI。


[nsi_mapping] SNuDD Collaboration. GeneralNSI model source[CP/OL]. Fixed Git commit 11622ded104994959a649d85e263c2d9f933ea74, accessed2026-11-12. GeneralNSI.xi_p/xi_n/xi_u/xi_d/xi_e; model eps_matrix multiplies each xi, phi=0。

[software] AMARAL D W P, CERDEÑO D, CHEEK A, COSTA V, FOLDENAUER P. SNuDD: Solar Neutrinos for Direct Detection[EB/OL]. arXiv:2607.22817v1, 2026. SolarDensityMatrixCalculator.density_mass/density; ProbabilityCalculator._cos_matter_average; direct adopted software, effective two-flavor and mass-decohered flavor reconstruction。

[remaining_oscillation] ESTEBAN I, GONZALEZ-GARCIA M C, MALTONI M, et al. NuFit-6.0: Updated global analysis of three-flavor neutrino oscillations[J]. JHEP,2024,12:216. DOI:10.1007/JHEP12(2024)216. arXiv:2410.05380. osc_params_best; explicit theta23=43.3deg,delta=212deg,dm31=2.513e-3eV² retained; theta12/13/dm21 overridden from v3.3 project card。

[返回目录](#toc)

<a id="protocol"></a>

## 文件契约、能量网格与缓存

| 字段/处理 | 实际约定 | 验证 |
|---|---|---|
| E_MeV | 正、有限、严格递增；正式union=1450点；Slow=1306，Fast=144 | [完整实际网格](<../../../../outputs/external/solar_rho_snudd/20261112_run1/ENERGY_CONTRACT.json>)；不同网格可另导出，已知并集精确取子集 |
| rho_flavour | (N_E,3,3)，complex128，单位1，味顺序e/mu/tau | 每点Hermitian、trace=1、PSD、finite；完整原矩阵留在rho.npz |
| pee | (N_E,)，float64，等于Re(rho[:,0,0]) | 读取时逐值核对；不静默重归一/裁剪/插值 |
| manifest.json | commit、依赖版本、实际振荡卡、NSI映射、能量hash、数组文件hash和物理性/绝热诊断 | cache key包含card内容hash、两耦合IEEE精确表示、能量bytes/shape、source8B、粒子/基底/日间模式 |
| 缓存 | 每个NSI点及能量网格独立目录；允许一次外部进程批量导出多点 | 原NPZ摘要验证、错误epsilon/网格/损坏拒绝；首次读取核验完整内容 |
| 可用性 | 无缓存时需独立环境和固定原件；已有有效包可直接读取 | 缺环境/导出错误会明确失败，不回退到SM或本地MSW |


[文件合同与校验](<../../../../extensions/solar_rho_snudd/protocol.py>) · [精确坐标状态提供器](<../../../../extensions/solar_rho_snudd/state.py>)。正式运行保存19份完整ρ包；深层hash目录由输出README统一说明，避免逐包产生新文档。

[返回目录](#toc)

<a id="target"></a>

## Target与原子核Response

| 输入 | 实际值/数组 | 来源与核验范围 |
|---|---|---|
| 天然Xe | 9×3：A=124–136；首行[124.0, 123.905892, 0.000952]；末行[136.0, 135.907214484, 0.088573] | [原NIST数丰度/原子质量表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xe_isotopes.txt>)；NIST Atomic Weights and Isotopic Compositions for Xenon；原9行作每吨核数分母 |
| 核响应 | Xe128/129/130/131/132/134/136；原数丰度0.998158；不补124/126、不重归一 | [实际原核表](<../../../../data/responses/responses_all.json>)；用户已选既有本地ResponseDB/Li2026约定，外部作者发布认证未闭合 |
| 核数/核质量 | 每吨核数由9行丰度与原子质量计算；截面核质量沿用A·amu | [build_targets](<../../../../cevns_pyeft/experiments/solar_singlebin.py>)；v3.3同一输入和算法，只读复用 |
| 散射理论 | 原核Response→共享振幅；C61q_NP=−√2G_Fεee_qV | [原ElectronVectorNSI](<../../../../cevns_pyeft/theory/li2026/ee_vector_nsi.py>)；Li et al.,2601.19883v2 p22 Eq.(95)。不调用SNuDD的核截面或Helm |


逐核素M系数shape、b与代表值完整保留在[v3.3 Target原记录](<NSI_EE_VECTOR_ONBOARDING.v3.3.md#target>)；本轮实际编译的三个核折叠数组与旧数组逐位相同，见前向验证。

[返回目录](#toc)

<a id="detector"></a>

## Detector与Observable

| 样本 | 曝光[t·yr] | 积分T[keVnr] | shape | 原表范围/首末ε[1] | 出处 |
|---|---|---|---|---|---|
| PandaX_paired | 1.2 | [1.1, 3.0] | [52, 2] | 1.1–3; ε=0.010829633/0.073827571 | [原表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_paired_total.txt>)；R2 PDF p3 Fig.1 Total paired; official exposure 1.20, not R5 1.25; T bounds R4 Table II |
| PandaX_US2 | 1.04 | [0.3, 3.0] | [99, 2] | 0.3–3; ε=0.0057913047/0.015546901 | [原表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/pandax_us2_total.txt>)；R2 PDF p3 Fig.1 Total US2 and exposure; T bounds R4 Table II; no extra Qy/Ne window |
| XENONnT | 3.51 | [0.5, 3.0] | [40, 3] | 0.43–2.77; ε=0.00011196658/0.12398753 | [原表](<../../../../data/benchmarks/solar_b8_singlebin_2601_19883/xenonnt_combined.txt>)；R3 PDF p4 Fig.1 black combined; exposure R3 3.51; bounds R4 Table II |


PandaX：Bo Z et al.,PRL133(2024)191001，DOI10.1103/PhysRevLett.133.191001，2407.10892v3 p3 Fig.1 Total两线。XENONnT：Aprile E et al.,PRL133(2024)191002，DOI10.1103/PhysRevLett.133.191002，2408.02877v2 p4 Fig.1黑combined。T界沿用Liao J et al.,2502.10702v2 p13 Table II。

每样本一个拟合信号数，输出events/bin；Total含ROI选择，只乘一次，无Qy/Ne再切窗、无ci。XENONnT约2.77–3keV效率仍MISSING；主点明确用末点平坦延伸，zero/unit为0≤ε≤1界。软件接入没有补出该缺失实验尾段。

[返回目录](#toc)

<a id="prediction"></a>

## Prediction与Statistics：怎样真正进入Runtime

扩展Preparation从只读单bin输入构建新模型，把同一ExternalSolarState同时绑定到source.state_provider（Slow）及model.state_model（Fast），再通过原load_experiment生成新的PreparedExperiment。没有修改已装配对象、伪造旧指纹或将rebind_state当作注入函数。

$$
\frac{d\sigma_{\rm eff}}{dT}=\frac{d\sigma_{\rm SM}}{dT}+P_{ee}(E;\epsilon)\left[\frac{d\sigma_e(\epsilon)}{dT}-\frac{d\sigma_{\rm SM}}{dT}\right].
$$

此式乘原总通量与Bahcall谱，再按E、T积分，并乘一次原每吨核数、Total效率和曝光。μτ的SM散射保留。新的kernel沿用energy_resolved_ee_vector_nsi_v1算法，保留E轴、每点读取对应Pee；独立编译和保存，不借用旧物理指纹。

统计沿用Li et al.,2601.19883v2 p20 Eq.(88)：三个拟合信号D=(3.5,75,10.7)events，σ=(1.2985,27.975,3.9483)events，分别由37.1%/37.3%/36.9%推导，三个独立12%pull。数据已是实验拟合信号，不再加背景或当作原始Poisson计数：

$$
\chi^2_{\rm prof}(\epsilon)=\sum_k\frac{[D_k-S_k(\epsilon)]^2}{\sigma_k^2+0.12^2S_k(\epsilon)^2}.
$$


[实际统计数组与逐项来源](<../../../../data/benchmarks/solar_b8_nsi_2601_19883/fitted_yields.json>) · [原联合统计程序](<../../../../cevns_pyeft/statistics/solar_nsi.py>)。本次实际验证点χ²及Runtime绑定；未运行新的全域最小化/完整Fig.4置信区。

[返回目录](#toc)

<a id="results"></a>

## 实际基准、差异及验收

| (eu,ed) | SNuDD三信号[events] | SNuDD rawχ² | 原B16三信号[events] | 原rawχ² |
|---|---|---|---|---|
| [0.0, 0.0] | 2.487829836, 47.043419726, 11.857362687 | 1.612757889 | 2.487829836, 47.043419726, 11.857362687 | 1.612757889 |
| [0.3, -0.1] | 1.743904970, 32.785442798, 8.301369763 | 4.362619681 | 1.743108414, 32.764170689, 8.297232777 | 4.367804426 |
| [-0.4, 0.6] | 1.814622473, 33.990162026, 8.630973377 | 3.99976464 | 1.817848035, 34.070566538, 8.647447384 | 3.980752641 |
| [0.0, 0.178] | 1.729812933, 32.439244812, 8.229771361 | 4.451185912 | 1.729866653, 32.440353713, 8.230034270 | 4.450872058 |
| [-17.263001514819095, 15.676753288438908] | 2.851169093, 57.841056334, 13.823610182 | 1.119850906 | 2.851155002, 57.840470947, 13.823525446 | 1.11985791 |


**SM信号逐位相同**：SM下截面味普适，传播重分味不会改变总信号。NSI下出现差异，传播输入的影响正确进入了散射。统计表和核折叠数组未改变。

![](../../../../outputs/external/solar_rho_snudd/20261112_run1/snudd_vs_local.png)

实线为SNuDD，虚线为本地B16-MSW；振荡θ12/13/Δ21一致，太阳profiles不同。

实际9个Slow/Fast点，另有US2在非零及远处耦合点的1201×216求积加密；容差max(3×10⁻⁴events,0.2%)。本轮测试74项通过；386份保护文件保持原字节。

[逐样本前向验证](<../../../../outputs/external/solar_rho_snudd/20261112_run1/FORWARD_VALIDATION.json>) · [完整实际点结果](<../../../../outputs/external/solar_rho_snudd/20261112_run1/RESULTS.json>) · [安装/测试/文件保护/接入验收](<../../../../outputs/external/solar_rho_snudd/20261112_run1/QA.json>)

绝热性另外以两能级劈裂/(2|dθm/dr|)作有限差分诊断，覆盖输入能量与太阳0–1Rsun的4001点。已保存各包最小γ和|2EV/Δ31|；当前诊断中的最小γ=1077.24429。γ≥100只按上游建议作诊断标签，不证明两味近似在大NSI有效。上游gamma_check在此commit将返回(value,label)的tuple与scalar比较，未调用；本项目未修改上游源码。

[返回目录](#toc)

<a id="code"></a>

## 程序对应与复算

| onboarding责任 | 实际程序位置 | 输入/输出 |
|---|---|---|
| 安装与来源冻结 | [prepare.py](<../../../../extensions/solar_rho_snudd/prepare.py>) / [snudd.input.json](<../../../../extensions/solar_rho_snudd/snudd.input.json>) | 固定checkout+实际安装信息→明确模型卡/依赖锁 |
| 传播 | [export_rho.py](<../../../../extensions/solar_rho_snudd/export_rho.py>) | 唯一import snudd；MeV→GeV、NP-only映射→完整ρ与manifest |
| 状态/网格 | [ExternalSolarState](<../../../../extensions/solar_rho_snudd/state.py>) | 子进程导出、参数/坐标绑定、精确子集→Pee及当前等价态 |
| 实验接入 | [load_snudd / Preparation](<../../../../extensions/solar_rho_snudd/experiment.py>) | 新Definition/scoped Catalog→标准PreparedExperiment |
| 事件数/统计/实际验收 | [run_with_rho.py](<../../../../extensions/solar_rho_snudd/run_with_rho.py>) / [test_solar_snudd.py](<../../../../tests/test_solar_snudd.py>) | 原NSIExecutor、kernel和统计API；与旧分支同条件比较 |


从Gitup01根目录，以主项目解释器运行（外部传播由适配器自动调用独立Python）：

```powershell
python -B tools/run_solar_b8_snudd_benchmark.py --output outputs/external/solar_rho_snudd/repeat_new
python -B -m extensions.solar_rho_snudd.prepare --check
python -B tools/finalize_solar_b8_snudd.py --check
```

最小API：

```python
from extensions.solar_rho_snudd.experiment import load_snudd
from cevns_pyeft.experiments.runtime import compile_experiment, predict_experiment
from cevns_pyeft.theory.li2026.ee_vector_nsi import nsi_point

experiment = load_snudd('PandaX_US2')  # 显式外部传播入口
numerics = {'n_er': 801, 'n_enu': 144}
kernel = compile_experiment(experiment, numerics=numerics)
prediction = predict_experiment(experiment, parameters=nsi_point(.3, -.1),
    backend='fast', kernel=kernel, numerics=numerics)
print(prediction.counts)  # 原Response/效率/曝光；仅Pee来自外部
```

重装命令、固定commit、pip报告和锁定依赖见扩展README。既有load_solar_nsi(...,propagation='nsi_msw')继续原B16模型，不声称原签名新增了snudd选项。本扩展随工作区运行，未作为根发行包强制依赖。


[返回目录](#toc)

<a id="limits"></a>

## 能力边界和来源缺口

| 项目 | 当前状态及影响 |
|---|---|
| 安装＋ρ导出＋主线Runtime | 已经实际完成；通过新身份和新缓存使用；保留全部完整ρ |
| 完整三味太阳演化/地球再生 | 本次未实现；day-only有效两味近似，不因3×3输出而升级声明 |
| SNuDD太阳输入原文等价性 | 直接软件输入与哈希已核；密度拟合/96点产生区相对原论文的认证未独立完成，软件引用与原论文身份分开记录 |
| XENONnT尾段 | 约2.77–3keV接受度仍MISSING，保留假设及界 |
| 核表缺口 | Xe124/126缺失且不重归一，外部作者核表认证未闭合 |
| Fig.4绿色区域 | 旧v3.3已有计算及论文差异；本轮验证的是SNuDD适配和点预测，未生成新的完整置信区域 |
| 科学结果接受 | NOT_REVIEWED；执行授权不冒充物理结果接受 |


移除整个extensions/solar_rho_snudd及其外部checkout/环境后，原主项目不依赖该扩展。根README、.gitignore和正式run记录保留历史入口；移除时按文件生命周期规则同步导航。GPL-3.0上游LICENSE保持原样；本次是本地安装，未作扩展分发。

[返回目录](#toc)

<a id="references"></a>

## 标准文献与固定上游原件

**[software]** AMARAL D W P, CERDEÑO D, CHEEK A, COSTA V, FOLDENAUER P. SNuDD: Solar Neutrinos for Direct Detection[EB/OL]. arXiv:2607.22817v1, 2026.

SolarDensityMatrixCalculator.density_mass/density; ProbabilityCalculator._cos_matter_average; direct adopted software, effective two-flavor and mass-decohered flavor reconstruction。

[https://arxiv.org/abs/2607.22817v1](https://arxiv.org/abs/2607.22817v1) · [直接采用的固定源码/数据](https://github.com/SNuDD/SNuDD/blob/11622ded104994959a649d85e263c2d9f933ea74/snudd/nsi/nsi_probabilities.py)

**[nsi_mapping]** SNuDD Collaboration. GeneralNSI model source[CP/OL]. Fixed Git commit 11622ded104994959a649d85e263c2d9f933ea74, accessed2026-11-12.

GeneralNSI.xi_p/xi_n/xi_u/xi_d/xi_e; model eps_matrix multiplies each xi, phi=0。

[https://github.com/SNuDD/SNuDD/blob/11622ded104994959a649d85e263c2d9f933ea74/snudd/models.py](https://github.com/SNuDD/SNuDD/blob/11622ded104994959a649d85e263c2d9f933ea74/snudd/models.py)

**[density]** BAHCALL J N, SERENELLI A M, BASU S. 10,000 Standard Solar Models: a Monte Carlo Simulation[J]. Astrophysical Journal Supplement, 2006,165:400-431. DOI:10.1086/504043. arXiv:astro-ph/0511337.

log10_electron_density, log10_neutron_electron_density; e1..e5,n1,n2; adopted software fits, not B16 arrays。

[https://arxiv.org/abs/astro-ph/0511337](https://arxiv.org/abs/astro-ph/0511337) · [直接采用的固定源码/数据](https://github.com/SNuDD/SNuDD/blob/11622ded104994959a649d85e263c2d9f933ea74/snudd/nsi/solar_profiles.py)

**[production]** LOPES I, TURCK-CHIÈZE S. Solar neutrino physics oscillations: Sensitivity to the electronic density in the Sun’s core[J]. Astrophysical Journal,2013,765:14. DOI:10.1088/0004-637X/765/1/14. arXiv:1302.2791.

raw two-column file header identifies1302.2791; flux_dists.interpolate_dist linear, outside0; native distribution normalized in dr over0-.35 by propagation code。

[https://arxiv.org/abs/1302.2791v1](https://arxiv.org/abs/1302.2791v1) · [直接采用的固定源码/数据](https://github.com/SNuDD/SNuDD/blob/11622ded104994959a649d85e263c2d9f933ea74/snudd/data/flux_distributions/8B_dist.txt)

**[remaining_oscillation]** ESTEBAN I, GONZALEZ-GARCIA M C, MALTONI M, et al. NuFit-6.0: Updated global analysis of three-flavor neutrino oscillations[J]. JHEP,2024,12:216. DOI:10.1007/JHEP12(2024)216. arXiv:2410.05380.

osc_params_best; explicit theta23=43.3deg,delta=212deg,dm31=2.513e-3eV² retained; theta12/13/dm21 overridden from v3.3 project card。

[https://arxiv.org/abs/2410.05380](https://arxiv.org/abs/2410.05380) · [直接采用的固定源码/数据](https://github.com/SNuDD/SNuDD/blob/11622ded104994959a649d85e263c2d9f933ea74/snudd/nsi/oscillation.py)

复用的源谱、靶、效率、统计完整标准引文与PDF页/式/图定位见[v3.3原始引用与核验范围](<NSI_EE_VECTOR_ONBOARDING.v3.3.md#references>)；这些数值文件本轮保持原字节。

[返回目录](#toc)
