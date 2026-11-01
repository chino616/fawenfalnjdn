# CEνNS-pyEFT：Solar-8B → XENONnT / PandaX-4T 迁移实施方案（Codex 任务书）

> **目标代码（必须在本地实际检查）：** https://github.com/chino616/fawenfalnjdn/tree/conus-v2-current-snapshot-20261011/Gitup01  
> **传播计算依赖：** https://github.com/SNuDD/SNuDD  
> **理论参考：** arXiv:2601.19883；**近似统计基准：** arXiv:2409.04703。  
> **输入草稿：** 用户提供的 `2026_07_16_CEvNSpyEFT___中文草稿.pdf`，尤其第 1 章“太阳 8B 中微子源、传播与 CEνNS 事件率”。  
> **任务状态：** 设计与实现指令；**不是已经完成的代码迁移**。当前环境无法读取所指定 V2 分支的源码；以下“已知现有路径”参考项目先前公开架构，其存在性、函数名和调用签名必须在本地 checkout 后确认。  
> **核心约束：** **直接调用 SNuDD 获取太阳振荡概率/密度矩阵，不重复开发 MSW 数值传播器**；保留 CEνNS-pyEFT 的 EFT 振幅、核响应、事件率、kernel 和统计框架。

---

## 0. 最重要的边界：B8 是 source，不是第三个探测器

最终分为三层，并保持接口单向依赖：

```text
[CEνNS-pyEFT: LEFT / nuclear responses / flavor EFT amplitudes]
                              |
                     shared scattering layer
                              ^
                              |
[shared solar 8B source] ---> [SNuDD solar/earth rho(E), P_ealpha(E)]
         |                    |
         +---------> [Xe isotopic recoil dR/dT] <---------------+
                            |                                  |
                     +------+-------+                          |
                     |              |                          |
             [XENONnT 2026] [PandaX-4T 2024]                    |
             SR0/SR1/SR2    Paired / US2                        |
                 |             |                               |
              4D likelihood  channel likelihood                |
                     +------+-------+                          |
                            |                                  |
                 [shared-nuisance joint fit] -------------------+
```

- `solar_b8` 提供 **太阳表面/地球探测器处的未振荡谱形、总通量和传播态**，不拥有实验曝光、背景或 χ²。
- `xenon` 提供天然 Xe 同位素、核质量、自旋和核响应；不拥有 XENONnT/PandaX 的 S1/S2 模板。
- `xenonnt` / `pandax4t` 分别持有 **数据版本、效率、响应、背景、观测、nuisance 与 likelihood**。
- 本次只迁移以太阳 **ν** 为入射态的过程；禁止误用 CONUS 的反电子中微子输入。
- `XENONnT 2024` 和 `XENONnT 2026 SR0/SR1/SR2` 可能存在重叠数据，**不得**当作两个独立似然相加。

## 1. 本地 Codex 的强制第一步：核实指定仓库，而不是照搬推测目录

```bash
# 在具备 GitHub 网络访问权限的本地执行

git clone --branch conus-v2-current-snapshot-20261011 --single-branch \
  https://github.com/chino616/fawenfalnjdn.git CEvNS-v2
cd CEvNS-v2/Gitup01

git rev-parse HEAD
git status --short
find src/cevns_pyeft -maxdepth 5 -type f | sort
find data/experiments -maxdepth 4 -type f | sort
find tests schemas tools -maxdepth 4 -type f 2>/dev/null | sort
```

如果仓库已在本地，不要覆盖用户未提交修改。先生成 `docs/migrations/B8_V2_SOURCE_AUDIT.md`，列出：

1. 当前 HEAD SHA、已修改工作树文件、Python 版本和依赖锁文件。
2. `src/cevns_pyeft/theory/li2026/` 中 flavor Wilson 输入、LEFT→核子匹配、振幅计算的实际入口。
3. `src/cevns_pyeft/nuclear/response.py` 的核响应以及是否支持逐同位素调用。
4. `src/cevns_pyeft/rates/differential.py` 和 `rates/counts.py` 的单位、坐标、返回张量轴。
5. `src/cevns_pyeft/experiments/base.py` 和 `registry.py` 的实验协议与 YAML 加载路径。
6. `src/cevns_pyeft/kernels/` 中 quadratic kernel 的 basis、缓存键、计算限制。
7. 当前统计 `chi2/likelihood/scans/confidence` 的真实入口、nuisance profile 函数。
8. 旧 `coherent`、`conus` 的运行命令和 golden/reference tests。

**禁止在确认路径前直接新建重复抽象层。** 以下新文件名是拟议设计；若 V2 已有相同职责，应复用现有模块与 public API。

## 2. 要从用户中文草稿保留的物理契约

该草稿第 1 章已明确三种不同传播模式，保持其物理含义，但对新实现作如下分层：

| 模式 | 数据来源 | 用途 | 实施级别 |
|---|---|---|---|
| `mathematica_probability` | Mathematica / PEANUTS 旧概率表 | 回归测试旧程序的 10 点概率、二次插值、旧计数 | legacy 兼容；不作为主物理后端 |
| `snudd_density_matrix` | **直接调用 SNuDD** | 默认太阳 MSW 密度矩阵与 `P_ee,P_eμ,P_eτ`，可选择地球传播 | **首要实现** |
| `full_wilson_density_matrix` | CEνNS-pyEFT Wilson→传播 NSI 匹配 + 能兼容的 SNuDD传播实现 | 新物理同时改变太阳传播与散射 | 第二阶段；不得将尚未支持的参数空间标记为完成 |

草稿中特别要求记录：`flux source`, `flux normalization`, `oscillation parameters`, `solar model`, `Earth model`, `propagation approximation`, `interpolation rule`, `Wilson normalization`。这些字段必须进入 provenance、缓存键和计算报告。

### 2.1 legacy 数据不能直接升格为现代官方 likelihood

草稿列举 Mathematica 的旧数据：

| 数据集 | legacy 曝光记法 | legacy T 窗口 keVnr | legacy signal |
|---|---:|---:|---:|
| PandaX Paired | 1.25 yr（旧代码记法，**需核实是否真正等于 t·yr**） | 1.1–3.0 | 3.5 ± 1.3 |
| PandaX US2 | 1.04 yr（同上） | 0.3–3.0 | 75 ± 28 |
| XENONnT | 3.51 yr（同上） | 0.5–3.0 | 10.7 ± 3.95 |

上表只用于 `legacy_regression`。**不得未经检查就转写为官方曝光、真正观测计数或 Gaussian likelihood。** 此处保留草稿原记法是为了定位错误，并非对单位的认可。

## 3. 太阳中微子输入：通量和传播必须分离

### 3.1 `SolarB8Flux`

采用

$$
\phi^0_{8B}(E_\nu)=\frac{d\Phi^0_{8B}}{dE_\nu}=\Phi_{8B}^{\mathrm{tot}}f_{8B}(E_\nu),\quad \int f_{8B}(E_\nu)\,dE_\nu=1.
$$

基础单位：`E_nu` 为 `MeV`；`phi` 为 `cm^-2 s^-1 MeV^-1`。严格区分：

- `legacy_5p69e6`：旧 Mathematica 链中出现的 `5.69e6 cm^-2 s^-1`；仅在确认 `8Bflux_nu.txt` 第二列是归一化形状时相乘。
- `snudd_gs98_5p46e6`：草稿记录的 GS98 参考总通量 `5.46e6 cm^-2 s^-1`；需验证选用的 SNuDD 版本/太阳模型。
- `user_supplied_absolute`：直接提供绝对微分通量，不允许重复乘以总通量。

草稿中旧链为：`8Bflux_nu.txt` 先做一次线性插值、`P(E)` 做二次插值、采样 101 个能量点生成 flavor flux 再做二次插值。clean 模式直接计算 `phi(E)*P(E)`；legacy 模式只为复现旧数值顺序才保留多次插值。

**实现时先做数据归一化自检：** 文件积分约为 1 还是约为 `5e6`？不合格则停止而不是静默归一化。峰外通量默认 0，禁止未声明的高阶外推。

### 3.2 用 SNuDD 计算概率及完整密度矩阵：直接复用正式 API

官方仓库 README 已给出调用方式（SNuDD 基础能量单位为 **GeV**）：

```python
import numpy as np
from snudd.models import GeneralNSI
from snudd.nsi.nsi_probabilities import DensityMatrixCalculator

# 仅示意零 NSI 时的配置；传播基准参数、太阳模型、SNuDD 版本须固定。
model = GeneralNSI(np.zeros((3, 3)), np.pi / 4, 0.0)
calc = DensityMatrixCalculator(model)

E_mev = np.geomspace(0.1, 16.0, 200)
E_gev = E_mev * 1.0e-3
rho_solar = calc.density(E_gev, '8B')

# 本地适配器应首先核验 SNuDD 的返回 shape、轴次序和 flavor 约定，
# 再将其标准化为 (..., 3, 3)，不能在未验证返回格式时硬编码轴交换。
```

**需要三个公开接口，但项目内部全部通过统一适配器调用：**

1. `density_matrix(E_mev, ...) -> np.ndarray[complex]`：首选输出，shape `E.shape + (3,3)`，flavor 顺序 `[e,mu,tau]`。
2. `probabilities(E_mev, ...) -> (Pee,Pemu,Petau)`：从同一 `rho` 对角元提取，不另算一套概率；三项之和为 1。
3. `density_matrix(E_mev, earth_mode=...)`：可选地球物质传播。

SNuDD 官方示例的 Earth 调用：

```python
from snudd.geometry import SolarAngles

# 示例是 Gran Sasso 的全年示意；真实运行应使用各 run 的实际时间窗口。
gran_sasso = SolarAngles(latitude=42.47, t0=0, T=365)
cnadirs, weights = gran_sasso.cnadir_hist(bins=30)
rho_with_earth = calc.density_earth(E_gev, cnadirs, weights, nu='8B')
```

- Gran Sasso/锦屏的纬度与时间权重、nadir histogram **必须各自配置**，不可把 Gran Sasso 的 Earth 权重原样用于 PandaX。
- 初版可以先使用 `earth_mode='day_only'` 的太阳传播，输出报告说明未含地球效应；后续切换 `earth_averaged`。
- SNuDD 是外部传播后端：锁定其 commit/tag、依赖、SM mixing 参数，并测试 `rho†=rho`、`Tr rho=1`、`eigvalsh(rho)>=-tol`。
- 不将 SNuDD 的 `Nucleus.spectrum()` 当作替代 CEνNS-pyEFT 的 EFT 反冲结果。可以用它在 SM/支持的 NSI 子空间做**独立交叉验证**。
- SNuDD 仓库采用 GPL-3.0；优先使用外部依赖而非复制实现。若分发集成软件，先明确许可证兼容性与源码分发要求。

### 3.3 **关键限制：SNuDD 的 `GeneralNSI` 不等于一般 LEFT Wilson 系数**

SNuDD 的 `GeneralNSI`（一个 Hermitian flavor 矩阵和角参数）适合其定义的 NSI 模型族。在该因子化参数化下，电子、上夸克、下夸克的 flavor 耦合通常是同一味矩阵的不同实数倍，不覆盖任意独立的三个 `3x3` 矩阵。

完整框架应显式区分两个映射：

$$
\Pi_{\rm prop}: C_{\rm LEFT}\mapsto\{\epsilon^{e,V}_{\alpha\beta},\epsilon^{u,V}_{\alpha\beta},\epsilon^{d,V}_{\alpha\beta}\},
\qquad
\Pi_{\rm det}: C_{\rm LEFT}\mapsto\{\mathcal M_{\beta\alpha}(E_\nu,T)\}.
$$

**落实规则：**

- **SM propagation**：直接调用 SNuDD；所有 EFT 探测 Wilson 都可变化而 `rho_SM` 固定。
- **SNuDD-supported NSI**：将允许的 Wilson 子空间明确投影至 `GeneralNSI`，逐点计算 `rho(C)`；若投影不满足模型条件，主动报错。
- **General independent e/u/d NSI**：不能用 `GeneralNSI` 冒充。评估能否通过 SNuDD 自定义 model/传播 Hamiltonian 接口完成；若需扩展，上游代码修改置于独立适配/extension 并测试，未经验证不得声称完成一般传播 EFT。
- 标量、赝标量、轴矢量、张量及其他探测算符不可无推导地映射为太阳介质矢量势。

## 4. 用 CEνNS-pyEFT 计算 flavor-aware 散射，而不是用 `Pee × σ(νe)`

对固定 `E_nu`, `T`, 核同位素 `a`，振幅具有 `M[beta,alpha]` 味矩阵结构。未测末态 flavor，必须按

$$
\frac{d\sigma_a^{\rm eff}}{dT}
=\operatorname{Tr}_{\mathrm{flavor}}\!\left[
\rho(E_\nu)\,\frac{d\boldsymbol\sigma_a}{dT}
\right],\qquad
\left[\frac{d\boldsymbol\sigma_a}{dT}\right]_{\alpha\gamma}
\propto\sum_{\beta,\mathrm{spins}}\mathcal M_{\beta\alpha}^{*}\mathcal M_{\beta\gamma}.
$$

等价表达：`Tr(M @ rho @ M.conj().T)`，其中振幅的所有核自旋平均、相空间与通量系数必须一致，不能将它直接当作截面而忽略 prefactors。

- **概率简化只在合适极限使用：** 若截面矩阵在初态味空间为对角，`Σ_alpha P_ealpha dσ_alpha/dT` 才成立；如果 flavor-changing 探测导致非对角干涉，一般需要完整 `rho`。
- **SM 极限：** 对 flavor-universal 的主动味中性流 CEνNS，结果正比 `Tr rho=1`，因此总率不依赖普通主动味 MSW 转换；这是硬性单元测试。
- **核响应：** 天然 Xe 逐同位素加权，不能只取 `132Xe` 并将其标称完整天然 Xe；自旋相关响应不能简单全部替换为 Helm。
- **运动学：** 每种核质量按 `Eν,min(T)`、`Tmax(Eν)` 设置积分边界（精确弹性运动学优先）；分别测试 keVnr、MeV、GeV 和 `cm²/keVnr` 转换。

核反冲预测的通用形式为

$$
\frac{dN_{d,a}}{dT}=
\mathcal E_d\frac{N_A\eta_a}{\bar M_{\rm Xe}}
\int_{E_{\nu,\min}(T)}^{E_{\nu,\max}}dE_\nu\;
\phi^0_{8B}(E_\nu)
\frac{d\sigma_a^{\rm eff}(E_\nu,T)}{dT},
$$

其中在具体实现中必须统一靶质量与 molar mass 的单位，并把秒/年换算与 exposure **恰好应用一次**；公式仅作结构表达。

## 5. 推荐新增文件与现有架构映射

路径都以 `Gitup01/` 为根目录；若实际 V2 已有同功能文件，应修改现有文件而不是造第二套。

```text
src/cevns_pyeft/
  sources/solar/
    b8.py                       # B8 normalized spectrum + flux normalization
    snudd_adapter.py            # **直接调用 SNuDD 的唯一入口**
    legacy_probabilities.py     # Mathematica 10-point/PEANUTS regression
    wilson_propagation.py       # C_LEFT -> epsilon^e/u/d; supported-subspace guard
  nuclear/
    targets/xenon.py            # Xe isotopes, abundance, spin, nuclear provenance
    response.py                 # 复用已有 nuclear response 接口
  rates/
    differential.py             # rho-aware EFT recoil spectrum (slow physics baseline)
    counts.py                   # response-folded counts and exposure handling
  experiments/
    base.py                     # 复用/扩展 source-target-response-likelihood 协议
    registry.py                 # 复用实验注册接口
    xenonnt/
      data_loader.py            # SR0/SR1/SR2 CSV/YAML/H5
      response.py               # mono-energy NR 4D response convolution
      likelihood.py             # public-template Poisson profile
    pandax4t/
      data_loader.py
      response.py               # Paired vs US2
      likelihood.py             # paper_approx + matched-data path
  kernels/
    builder.py                  # 保留旧实现，支持 Xe and rho-dependent caching
    reconstruction.py
    storage.py

data/
  solar/b8/
    flux_provenance.yaml
    legacy/                     # 原 Mathematica 表：有文件才纳入
  experiments/
    xenonnt_b8_2026/
      experiment.yaml
      provenance.yaml
      release/                  # 上游数据可为未跟踪/独立下载资源
    pandax4t_b8_2024/
      experiment.yaml
      provenance.yaml
      release/

tests/
  solar/test_snudd_adapter.py
  solar/test_b8_flux.py
  solar/test_legacy_probabilities.py
  nuclear/test_xenon_target.py
  rates/test_solar_flavor_rate.py
  xenonnt/test_4d_response.py
  pandax4t/test_paired_us2.py
  integration/test_joint_b8_likelihood.py
  regression/test_coherent_conus_unchanged.py

docs/migrations/
  B8_V2_SOURCE_AUDIT.md
  B8_SNUDD_INTERFACE.md
  XENONNT_2026_REPRODUCTION.md
  PANDAX_2024_REPRODUCTION.md
  B8_EFT_VALIDATION_REPORT.md
```

对新源采用统一协议，但不可让 `rates/differential.py` 去 import 具体实验。示意的 Python interface（**非 V2 中已存在的真实签名**）：

```python
from typing import Protocol
import numpy as np

class PropagationBackend(Protocol):
    def rho_flavor(self, energy_mev: np.ndarray, *, model=None,
                   earth=None) -> np.ndarray: ...  # (...,3,3)

class SolarSource(Protocol):
    def differential_flux(self, energy_mev: np.ndarray) -> np.ndarray: ...

class NuclearRecoilPredictor(Protocol):
    def recoil_spectrum(self, recoil_kevnr: np.ndarray,
                        *, wilson, source: SolarSource,
                        propagation: PropagationBackend) -> np.ndarray: ...

class DetectorResponse(Protocol):
    def fold_spectrum(self, recoil_kevnr: np.ndarray,
                      rate_dRdT: np.ndarray, *, nuisance=None) -> np.ndarray: ...

class ExperimentLikelihood(Protocol):
    def deviance(self, wilson, *, shared_nuisance=None,
                 local_nuisance=None) -> float: ...
```

### 5.1 SNuDD adapter 的必备保护

- 所有**项目 API 传入 MeV**，adapter 单点 `MeV → GeV`；不要由各 experiment 自己进行转换。
- 在 adapter 中标明密度矩阵的 flavor 顺序、phase convention、shape、是否包含 Earth、太阳 mixing/mass-splitting 版本。
- `rho` 如复数，必须保留复数与 flavor 非对角项；不能仅 `np.real(rho)` 后当成一般传播对象。
- 对象创建成本高时按 `(SNuDD commit, spectrum, oscillation params, NSI params, Earth latitude/time histogram, energy grid)` 缓存。
- 缓存结果不可从一组 `C_prop` 直接用于另一组 `C_prop`。
- 禁止将极小的负本征值直接无报告地投影为正；先判断是否仅是数值误差，定义明确阈值后才能修正。

## 6. 两项实验的具体数据迁移

### 6.1 XENONnT：2026 SR0+SR1+SR2 **优先**

数据地址：

- https://github.com/XENONnT/cevns_data_release
- 固定归档：https://zenodo.org/records/20576156

公开资源包含 `data/*.csv`、`binning/*.yaml`、`templates/sr*/ac/`、`er/`、`rg/`、`mono/` 下的 `.h5` 和示例 `plot.ipynb`。四维观测量为：

1. `cS2`：corrected S2 amplitude；
2. `quantile(S2_pre / Δt_pre)`；
3. `S1 BDT score`；
4. `S2 BDT score`。

在每个 science run 与 detector nuisance 点上计算

$$
S_{r,k}(C,\theta)=\mathcal E_r
\int dT\;\frac{dR(T;C)}{dT}\;
A_{r,k}(T;\theta),
$$

`k` 指全部 4D bins；`A` 用公开的 monoenergetic NR templates 插值构建。**必须核对 released units**：公开 README 说明 mono NR 模板为无量纲效率，其他背景组件以 `/t/y` 表示；不要对 signal 或 background 重复乘以曝光。

实现顺序：

1. 下载固定 release，保存 commit/DOI、checksum、license。
2. 对全部 SR 验证 bins、事件数、模板 sum、背景归一化、NR 单能模板能量轴和 shape。
3. 使用 SM Xe 反冲能谱卷积得到 4D signal。
4. 用背景+信号构造 extended binned Poisson deviance：

   $$
   D=2\sum_{r,k}\biggl[\mu_{rk}-n_{rk}
   +n_{rk}\ln\frac{n_{rk}}{\mu_{rk}}\biggr]+\chi^2_{\rm pulls},
   $$

   `n=0` 项按连续极限取 0；`mu>0` 严格检查。
5. 以官方可公开获取的 nuisance prior/correlation 与优化边界为准；没有完整定义就命名 `public_template_reconstruction`，**禁止宣称完整官方 likelihood**。
6. 最后做 EFT Wilson 扫描，而不是先扫描再补 SM 统计验证。

### 6.2 PandaX-4T：2024 8B Paired 和 US2 分开

参考文章：`PRL 133, 191001 (2024)`；官方页 https://pandax.sjtu.edu.cn/Publications 。

- Paired：S1+S2；阈值约 1.1 keVnr，曝光约 1.20 t·yr，观测 3，背景 `2.8±0.5`，联合拟合 signal 约 3.5。
- US2：ionization-only；阈值约 0.33 keVnr，曝光约 1.04 t·yr，观测 332，背景 `251±32`，联合拟合 signal 约 75。
- 官方联合显著性约 2.64σ；**信号最好拟合值不是 observed-background 的简单相减。**

官方 data release：https://pandax.sjtu.edu.cn/public/data_release 。目前可浏览到其他主题或 run 的文件；**不能把不匹配的暗物质/S2-only release 自动当成 2024 B8 的官方 background / response。** 需按论文 run、cuts、ROI、selection 和 efficiency 分别建立 provenance 清单。

交付分两级：

- `paper_approx`：精确复现所选现象学文献的输入和单箱 χ²；这是先完成的、可验收的基准。
- `public_reinterpretation` 或经核查的 `official_matched`：取得相匹配的 Paired / US2 response、背景和 nuisance 后实现多 channel 联合拟合。若数据不齐，列出缺口，不伪造模板。

## 7. χ² 验收：先 2409.04703 的单箱近似，再官方公开模板

推荐 arXiv:2409.04703，https://arxiv.org/abs/2409.04703 ，作为与现有 COHERENT 统一 EFT 算符框架直接相关的 **现象学统计复现**。

论文采用的基准（仅用于该论文的 paper-matched approximation）：

| 数值 | PandaX US2 | XENONnT 2024 |
|---|---:|---:|
| `N_meas` | 69.1 | 10.7 |
| `N_SM` | 44.9 | 11.15 |
| `sigma_stat` | `0.37 × 69.1` | 3.95 |
| `sigma_alpha` | 0.245 | 0.13 |
| exposure | 1.04 t·yr | 3.51 t·yr |

按论文约定（必须对照实际公式/误差定义）实现类似

$$
\chi^2(C)=\min_{\alpha}
\left[
\frac{(N_{\rm meas}-(1+\alpha)N_{\rm th}(C))^2}{\sigma_{\rm stat}^2}
+\frac{\alpha^2}{\sigma_{\alpha}^2}
\right].
$$

注意 `69.1` 是该文献的近似拟合输入，不是 PandaX 官方报告的 US2 best-fit `75` 的替代记号；不要跨论文混合 `N_meas/N_SM/exposure`。

测试：SM `N_th`、profiled χ²、`Δχ²(C)`、一维置信区间、`ε_ee^{uV}`–`ε_ee^{dV}` 二维区域。二维 `Δχ²` 阈值必须与实际统计自由度、边界及 Wilks 适用条件一致；遇到边界情形可用 toys 校验。

对于 XENONnT 2026 的多维模板，单独记录 `dataset_id`、`likelihood_level='public_template_reconstruction'`。不得把它与 2024 近似数据重复作为独立样本联合。

## 8. EFT 快速 kernel 与传播耦合：两种模式禁止混淆

若传播固定，则探测幅度在一组 Wilson 系数内线性（含 SM 常数项时将其并入增广向量），每个 detector bin 可写为

$$
N_i(C_{\rm det};\rho_{\rm fixed})=
\widetilde C^\dagger K_i[\rho_{\rm fixed}]\widetilde C.
$$

如果同一 Wilson 系数改变太阳传播：

$$
N_i(C)=\widetilde C^\dagger K_i[\rho(C_{\rm prop})]\widetilde C,
$$

**不存在可以跨全部传播 Wilson 参数点原封不动复用的全局常数 kernel。**

必须提供两种可选实现：

1. `slow_reference`：逐参数点从 SNuDD（或明确兼容的扩展）获得 rho，独立积分、逐核同位素与 bin 计算；作为最终正确性基准。
2. `fast_detector_kernel`：仅对已经固定 `rho` 的探测 Wilson 变化建立 quadratic kernel；如扫描传播 NSI，须刷新 `rho` 与依赖该 `rho` 的 kernel，或采用明确验证的条件插值。

缓存 hash 至少包含：`dataset_id`, source/flux version, SNuDD commit, solar model/oscillation params, Earth weighting, `C_prop`/rho digest, isotope response, EFT basis/normalization, detector template version, binning 和 units。对旧 COHERENT / CONUS kernel 必须保证不会碰撞。

## 9. 完整联合拟合：共享 8B 通量 prior 只能一次

同一太阳通量不确定性同时作用于两实验。

$$
\chi^2_{\mathrm{joint}}(C)=\min_{\eta_{8B},\theta_X,\theta_P}
\left[D_X(C,\eta_{8B},\theta_X)+D_P(C,\eta_{8B},\theta_P)
+\frac{\eta_{8B}^2}{\sigma_{8B}^2}
+\chi^2_{\rm other\ shared}\right].
$$

此式假设 `D_X`,`D_P` **不重复含 8B flux prior**。其他共有物理 nuisance（太阳模型、核 form factors）视来源决定是否相关；各实验 detector calibration/background 通常分别建模。对联合约束应报告全局最小值与 profile 曲线，不仅是两个单实验 `Δχ²` 的相加。

## 10. 可执行的测试门槛（全部自动化）

### A. SNuDD / Solar

- [ ] `density(E,'8B')` 返回格式标准化，flavor 顺序明确。
- [ ] `Pee+Pemu+Petau=1`；概率在 `[0,1]` 内（容许有限数值误差）。
- [ ] `rho = rho†`、`Tr rho=1`、`min eig(rho)>=-tol`。
- [ ] day-only 与 Earth-averaged 显式区分；两个地点、两个 run 的 Earth 角分布不能错误复用。
- [ ] SM `Tr[rho × flavor-universal cross section]` 与不加振荡预测一致。
- [ ] 老 Mathematica 十点概率、插值流程只在 legacy_mode 下与原表/代码比较；不要求不同太阳模型的 SNuDD 数值逐点等于 PEANUTS。
- [ ] 8B 通量积分和 `5.46e6` / `5.69e6` 模式正确；总通量恰好乘一次。

### B. EFT 与核响应

- [ ] `rho` 对角且截面对角时，trace 结果退化为 `Σ P_alpha σ_alpha`。
- [ ] flavor-changing complex Wilson benchmark 显示非对角 `rho` 的干涉；交换 flavor 索引能触发回归测试失败。
- [ ] 截面矩阵 Hermitian、物理正定，预测事件数为实且非负。
- [ ] 天然 Xe 的同位素丰度和为 1；分同位素求和与直接总和一致。
- [ ] SM Helm check 与 full EFT response 的一致性仅在其共同适用的响应子空间检查。
- [ ] 真实反冲谱的 `Eν`、`T` 积分收敛；阈值附近细网格稳定。

### C. 探测器与统计

- [ ] XENONnT 各 SR 的 CSV/YAML/H5 可以加载，所有 4D dimensions、单位、bkg template 归一化正确。
- [ ] Paired 与 US2 具有独立的 detector response、exposure、background、bins；不可盲目合并 raw counts。
- [ ] 无正式配套 likelihood 数据时，不生成 `official_matched` 验收状态。
- [ ] paper-approx 的 `N_SM`、profile curve 与引用文章相符。
- [ ] 联合拟合共享 flux prior 一次，profile minimum 正确。
- [ ] 固定传播下 `fast` 与 `slow` **逐 bin** 一致；改变 propagation NSI 后 kernel cache 自动失效。
- [ ] 原 COHERENT / CONUS 所有 golden tests 无回归。

建议的验收状态字段：

```yaml
validation:
  flux_validated: false
  snudd_probability_validated: false
  density_matrix_validated: false
  eft_flavor_matrix_validated: false
  xenon_isotopes_validated: false
  slow_rate_validated: false
  fast_rate_validated: false
  xenonnt_likelihood_validated: false
  pandax_likelihood_validated: false
  joint_fit_validated: false
```

### D. 自动生成的最少结果图

- 8B `dPhi/dE`，以及 `Pee/Pemu/Petau` 随能量变化；完整 rho 的非对角实部/虚部（用于 flavor-changing 检验）。
- 天然 Xe 的 SM 和 EFT `dR/dT`，同位素分量，`rho` 迹算法 vs 概率近似的物理差异。
- 同样的模型与数据输入上 `slow` vs `fast` 的逐 bin ratio/residual。
- XENONnT 2026 4D 模板投影：逐 SR signal/background/data/pulls。
- PandaX Paired 与 US2 的独立预期；区分论文近似与已核实的多 channel 重建。
- 2409.04703 的 `Δχ²` 和二维 EFT/NSI 轮廓；XENONnT 2026 public-template 轮廓。
- 单实验与联合约束 overlay，标注是否采用 `fixed_sm` 或 `propagation_nsi`。

## 11. 执行顺序与必须生成的产物

| Phase | 工作 | 必须交付 | 开始下一阶段的门槛 |
|---|---|---|---|
| **0** | V2 源码审计及 COHERENT/CONUS baseline | `B8_V2_SOURCE_AUDIT.md`, 原测试报告 | 明确实际入口与无回归基线 |
| **1** | SNuDD 适配器、8B 通量和概率/密度矩阵 | `B8_SNUDD_INTERFACE.md`, rho & flux 测试、图 | 所有概率/单位/密度矩阵测试通过 |
| **2** | 天然 Xe + EFT flavor amplitude + Slow rate | SM recoil 图、按同位素报告、flavor 测试 | SM 味普适极限及积分收敛通过 |
| **3** | arXiv:2409.04703 的单箱统计近似 | profile curves、SM benchmark、对照报告 | 不再将理论错差归因于统计 |
| **4** | XENONnT 2026 4D public-template likelihood | 数据 provenance、4D plots、profile 报告 | 支持相应公开参数的可检验重建 |
| **5** | PandaX-4T Paired+US2 数据审计与实现 | matched-data gap list、分通道报告 | 不使用不匹配 release 强行做官方复现 |
| **6** | Kernel、joint fit、论文图和长期测试 | 联合曲线、逐 bin fast/slow、CI tests | 共享 nuisance 与旧实验回归通过 |

各 phase 必须在 README 说明是否仅为 `design`、`paper_approx`、`public_template_reconstruction` 或已核实的 `official_matched`，禁止跳级宣称完成。

## 12. 可直接复制给本地 Codex 的主提示词

```text
你需要在下列现有项目中实施新增实验：
https://github.com/chino616/fawenfalnjdn/tree/conus-v2-current-snapshot-20261011/Gitup01

背景：这是通用 flavor-aware CEνNS EFT 框架；现有 COHERENT 与 CONUS 实现必须保持数值回归一致。
此次增加太阳 8B 源、天然 Xe 核靶，以及 XENONnT2026 和 PandaX-4T2024 两个独立统计后端。

重要决策：太阳概率和密度矩阵不在本项目中重写 MSW 数值传播器。
直接集成 https://github.com/SNuDD/SNuDD 的 DensityMatrixCalculator：
  density(E_GeV, '8B')
  density_earth(E_GeV, cnadirs, weights, nu='8B')
在本项目建立唯一 snudd_adapter，接收 MeV，返回 (...,3,3) flavor 密度矩阵及由对角元素读取的三味概率。
先运行真实 API 的冒烟测试确定 shape、参数签名、基底、单位；不得臆测。

SNuDD GeneralNSI 只在支持的 NSI 子空间使用。完整 LEFT 的独立 epsilon^e/u/d flavor 矩阵需要明确的 propagation projection，并校验是否受 SNuDD 当前 API 支持。其他 EFT 算符先用于 detector scattering。不能将 GeneralNSI 宣称等价于完整 Wilson basis。

必须先按本 MD 的 Phase 0 审计具体 V2 文件，生成真实 file/function/call-site mapping；如果推荐目录与真实源码不同，以真实源码为准，并解释决定。不得复制一个并行的率和统计框架。

Phase 1: 集成 SNuDD、8B flux + legacy probability baseline，完成 unit tests。
Phase 2: 接入天然 Xe 多同位素核响应、按 flavor amplitude 用 Tr(M rho M†) 计算 slow recoil spectrum，完成 SM/flavor-changing tests。
Phase 3: 按 arXiv:2409.04703 复现 PandaX-US2 和 XENONnT2024 的单箱近似及二维图。
Phase 4: 下载并固定 XENONnT cevns_data_release sr0_sr1_sr2；使用四维 mono-NR 模板与公开背景进行拟合；检查 template 单位，明确 public-template vs official likelihood 边界。
Phase 5: 审计 PandaX-4T2024 的 Paired/US2 专用响应和数据来源，不得把其他 run 的 dark matter data 当成官方 8B likelihood。
Phase 6: 在 fixed propagation 下建立快速 EFT kernel，传播随 Wilson 变化时刷新 rho 和 kernel，最后实现带单个 shared B8 flux prior 的 joint likelihood。

每 Phase 报告：具体修改文件、函数/接口、物理公式/约定、用到的数据版本、测试命令与输出、目前缺失或不能完成的点。运行并报告旧 COHERENT/CONUS tests。任何外部数据文件必须记录 hash/DOI/license/单位；不伪造输入；不靠强制重标定总计数掩盖 fast/slow 差异。

验收：概率和 rho 物理正确，SM flavor-universal total rate 不受标准主动味振荡影响；flavor-changing 用完整 rho；天然 Xe 核响应可复现；XENONnT 4D 和 PandaX Paired/US2 区别明确；联合 shared nuisance 只施加一次；所有旧实验无回归。
```

## 13. 主要可核查资料与链接

1. 项目 V2（本地 Code 审计对象）：https://github.com/chino616/fawenfalnjdn/tree/conus-v2-current-snapshot-20261011/Gitup01
2. SNuDD 官方项目（`GeneralNSI`、`DensityMatrixCalculator`、`SolarAngles`、快速入门）：https://github.com/SNuDD/SNuDD ；论文 arXiv:2607.22817：https://arxiv.org/abs/2607.22817
3. CEνNS-pyEFT 原理论：arXiv:2601.19883：https://arxiv.org/abs/2601.19883
4. COHERENT + XENONnT + PandaX NSI 基准：arXiv:2409.04703：https://arxiv.org/abs/2409.04703
5. XENONnT 2026 CEνNS：arXiv:2604.06002：https://arxiv.org/abs/2604.06002
6. XENONnT CEνNS 公开数据：https://github.com/XENONnT/cevns_data_release ；固定归档：https://zenodo.org/records/20576156
7. PandaX-4T 2024 solar 8B PRL 133, 191001：https://doi.org/10.1103/PhysRevLett.133.191001
8. PandaX 实验数据公开目录：https://pandax.sjtu.edu.cn/public/data_release
9. 太阳概率独立交叉验证（可选）：PEANUTS：https://github.com/michelelucente/PEANUTS
10. 本对话上传的中文草稿 PDF：`2026_07_16_CEvNSpyEFT___中文草稿.pdf`（尤其第 1 章 1.1–1.16）。

---

### 验收声明

此 Markdown 是面向当前指定 V2 代码分支和 SNuDD 的可执行迁移设计，不包含已通过的迁移结果。Codex 只有在本地读取 V2 实际源文件、运行测试并记录官方数据 provenance 后，才能将相应状态由 `planned` 改为 `validated`。
