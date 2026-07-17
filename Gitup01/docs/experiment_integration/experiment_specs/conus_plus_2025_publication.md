# CONUS+ 2025 首次观测：实验物理规格

## 0. 状态与用途

```yaml
spec_status: incomplete_for_exact_publication_reproduction
implementation_mode: publication_forward_model
experiment_family: CONUS+
dataset_name: conus_plus_2025_first_observation
```

本文件已冻结公开论文中可直接核对的物理输入，并为论文未以机器可读表格公开的输入定义严格文件契约。

以下核心数据仍需由用户从官方补充材料、作者数据仓库或经过批准的数字化过程提供：

```text
REQUIRES_INPUT:
- CONUS+ 实际采用的低于 1.8 MeV 反应堆谱数值表及拼接规则；
- 将 Daya Bay 谱转换到 KKL 裂变份额的正式实现细节；
- C2/C3/C5 的逐能量效率曲线；
- 各探测器独立有效曝光；
- 逐 bin ON/OFF 数据、背景模型及协方差；
- publication 标准模型逐 bin reference。
```

因此，本包可直接用于建立程序骨架、legacy 回归和 forward-model 数据契约，但在上述内容补齐前，不应声称精确复现官方 likelihood。

## 1. 主要参考

- CONUS Collaboration, arXiv:2501.05206, Nature 643 (2025).
- Daya Bay unfolded spectrum, arXiv:2102.04614 ancillary file `UnfoldAntineutrinoSpectra.txt`.
- Daya Bay high-energy spectrum, arXiv:2203.06686 ancillary files.
- Estienne et al., Phys. Rev. Lett. 123, 022502 (2019), low-energy summation spectrum reference.

## 2. 运行条件

```yaml
site: Kernkraftwerk Leibstadt
reactor_thermal_power_gw: 3.6
baseline_m: 20.7
nominal_detector_site_flux_cm2_s: 1.5e13
reactor_on_exposure_kg_day: 327
reactor_off_exposure_kg_day: 60
combined_active_mass_kg: 2.83
combined_active_mass_sigma_kg: 0.02
```

`nominal_detector_site_flux_cm2_s` 只能作为通量推导结果的一致性检查；publication 默认归一化模式定义为：

```yaml
flux_normalization_mode: thermal_power_and_geometry
```

不得再把 `1.5e13 cm^-2 s^-1` 乘到已经由热功率和基线得到的谱上。

## 3. 反应堆通量

### 3.1 味道与生产分量

```yaml
flavors:
  - nuebar
production_components:
  - U235
  - U238
  - Pu239
  - Pu241
```

平均裂变份额：

```yaml
fission_fractions:
  U235: 0.53
  U238: 0.08
  Pu239: 0.32
  Pu241: 0.07
```

必须验证总和等于 1。

### 3.2 通量定义

设每个裂变同位素的每次裂变反中微子谱为 \(S_r(E_\nu)\)，每次裂变释放能量为 \(e_r\)。

\[
R_f=
\frac{P_{\rm th}}
{\sum_r f_r e_r},
\]

\[
\frac{d\Phi_r}{dE_\nu}
=
\frac{R_f}{4\pi L^2}
 f_r S_r(E_\nu),
\qquad
\frac{d\Phi}{dE_\nu}=\sum_r\frac{d\Phi_r}{dE_\nu}.
\]

所需单位：

```text
P_th: GW -> MeV/s
L: m -> cm
S_r: antineutrinos / fission / MeV
dPhi/dE: antineutrinos / cm^2 / s / MeV
```

单位常数：

```yaml
unit_conversions:
  gw_to_watt: 1.0e9
  joule_to_mev: 6.241509074e12
  meter_to_cm: 100.0
  day_to_second: 86400.0
```

每次裂变能量采用 Ma et al. (2013) 的常用中心值；若合作组代码采用不同数值，应在 provenance 中覆盖：

```yaml
energy_release_per_fission_mev:
  U235: 202.36
  U238: 205.99
  Pu239: 211.12
  Pu241: 214.26
```

### 3.3 能谱表示

论文采用 Daya Bay 数据驱动反中微子谱，并：

- 在中央测量能区使用 Daya Bay unfolded spectrum；
- 高能区使用 Daya Bay 高能谱测量扩展；
- 低于 IBD 阈值的区域使用 summation-model 模拟扩展。

包内保存以下官方 ancillary 文件：

```text
data/external/dayabay/UnfoldAntineutrinoSpectra.txt
data/external/dayabay/AntineutrinoEnergySpectrum_high.txt
data/external/dayabay/WholeAntineutrinoEnergySpectrum.txt
```

以及解析后的便捷 CSV：

```text
data/external/dayabay/dayabay_u235_unfolded.csv
data/external/dayabay/dayabay_pu_combo_unfolded.csv
data/external/dayabay/dayabay_total_unfolded.csv
data/external/dayabay/dayabay_high_energy.csv
data/external/dayabay/dayabay_whole_reference.csv
```

这些表不是已经完成的 CONUS+ 四同位素谱。最终代码只能读取：

```text
data/conus_plus_2025/reactor_spectrum_conus_plus_TEMPLATE.csv
```

在该模板被替换为经过物理审核的正式表之前，publication 通量构造器必须拒绝运行。

最终表契约：

```text
energy_mev
U235_per_fission_per_mev
U238_per_fission_per_mev
Pu239_per_fission_per_mev
Pu241_per_fission_per_mev
source_status
```

插值和外推：

```yaml
interpolation: linear
below_first_energy: zero
above_last_energy: zero
negative_values: forbidden
duplicate_energies: forbidden
```

## 4. 探测器

Run-1 使用：

```yaml
detectors:
  C2:
    threshold_evee: 180
  C3:
    threshold_evee: 160
  C5:
    threshold_evee: 170
```

分析窗口：

```yaml
analysis_window_evee:
  minimum: 160
  maximum: 800
```

本包提供 10 eVee 边界表：

```text
data/conus_plus_2025/bin_edges_evee.csv
```

若正式分析使用 detector-specific 起始 bin，代码应先在公共 160–800 eVee 网格计算，再按每台探测器阈值 mask；不得把三台 detector 预先合并成一个平均响应。

各 detector 的独立有效质量和曝光：

```yaml
detector_exposures_kg_day:
  C2: REQUIRES_INPUT
  C3: REQUIRES_INPUT
  C5: REQUIRES_INPUT
```

必须满足三者之和与 publication 的有效 reactor-ON exposure 定义一致。

## 5. 天然锗靶

默认模式：

```yaml
target_mode: natural_germanium
```

同位素清单见：

```text
data/conus_plus_2025/natural_germanium_isotopes.csv
```

每个同位素必须独立调用：

```text
Ge70, Ge72, Ge73, Ge74, Ge76
```

核数：

\[
n_a=
\frac{N_A}{M_{\rm mol}^{\rm natGe}}f_a.
\]

`Ge73_only` 只能用于 legacy 回归，不得作为 publication 默认。

## 6. CEvNS 截面和真实反冲谱

只调用项目通用截面接口，输出单位为 `cm^2/keVnr`。

\[
\frac{dR_a}{dT}
=
 n_a
\int_{E_{\nu,\min}(T)}^{E_{\nu,\max}}
 dE_\nu\,
\frac{d\Phi}{dE_\nu}
\frac{d\sigma_a}{dT}.
\]

使用精确运动学：

\[
E_{\nu,\min}(T)=
\frac{T+\sqrt{T^2+2m_aT}}{2}.
\]

建议初始数值网格：

```yaml
numerical_reference:
  enu_min_mev: 0.001
  enu_max_mev: 11.0
  enu_points: 1200
  recoil_min_kevnr: 0.0001
  recoil_max_kevnr: 3.0
  recoil_points: 1200
  reconstructed_min_evee: 0.0
  reconstructed_max_evee: 1000.0
  reconstructed_points: 2001
```

这些是数值起点，不是论文参数；必须执行网格加密收敛检查。

## 7. 核反冲到 eVee

使用 Lindhard 形式：

\[
\epsilon_L=11.5 Z^{-7/3}T,
\]

\[
g(\epsilon_L)=
3\epsilon_L^{0.15}
+0.7\epsilon_L^{0.6}
+\epsilon_L,
\]

\[
Q(T)=\frac{k g(\epsilon_L)}{1+k g(\epsilon_L)},
\]

\[
\bar E_{\rm ee}(T)=1000 Q(T)T\quad[\mathrm{eV_{ee}}],
\]

其中 \(T\) 以 keVnr 输入。

publication 中心值：

```yaml
lindhard_k: 0.162
lindhard_k_sigma: 0.004
```

该数值与 legacy 程序相同，但 publication 模式必须同时保留论文给出的 `±0.004` 不确定性。

## 8. 能量分辨率

使用：

\[
\sigma_d(E)=
\sqrt{\sigma_{0,d}^2+F_d\eta E},
\qquad \eta=2.96\,\mathrm{eV}.
\]

Gaussian 响应：

\[
R_d(E_{\rm reco}\mid T)
=
\frac{1}{\sqrt{2\pi}\sigma_d}
\exp\left[-\frac{(E_{\rm reco}-\bar E_{\rm ee})^2}{2\sigma_d^2}\right].
\]

正式参数文件：

```text
data/conus_plus_2025/resolution_parameters.csv
```

论文给出 C2 为 `48±1 eVee` FWHM，C3/C5 为 `47±1 eVee` FWHM，Fano 因子为 `0.11`，电子-空穴对平均产生能为 `2.96 eV`。

## 9. 效率

效率作用域：

```yaml
efficiency_domain: reconstructed_energy_eVee
```

正式文件：

```text
data/conus_plus_2025/efficiency_C2_TEMPLATE.csv
data/conus_plus_2025/efficiency_C3_TEMPLATE.csv
data/conus_plus_2025/efficiency_C5_TEMPLATE.csv
```

模板中的空值不得解释为零或一。publication 构造器必须在发现空值时停止。

论文只给出定性信息时，不得把阶跃函数称为官方效率。可以另建显式模式：

```yaml
detector_response_mode: threshold_approximation
```

但其输出必须标记为 reproduction approximation。

## 10. 分箱事例数

对 detector \(d\)、Ge 同位素 \(a\)、裂变分量 \(r\)：

\[
N_{dari}
=
\mathcal E_d
\int_{E_i}^{E_{i+1}}dE_{\rm reco}\,
\epsilon_d(E_{\rm reco})
\int dT\,
R_d(E_{\rm reco}\mid T)
\frac{dR_{ar}}{dT}.
\]

输出轴：

```text
detector × isotope × production_component × bin
```

## 11. 数据、背景与 likelihood

模板：

```text
data/conus_plus_2025/observed_counts_TEMPLATE.csv
data/conus_plus_2025/background_TEMPLATE.csv
data/conus_plus_2025/covariance_TEMPLATE.csv
```

这些文件未填充前，只实现 signal forward model，不实现或宣称复现官方 likelihood。论文的数据可用性声明明确说明完整数据目前不公开，可向 CONUS 合作组合理申请。

## 12. 公开总量基准

```yaml
validation_summary:
  sm_expected_events: 347
  sm_expected_events_sigma: 59
  fitted_signal_events: 395
  fitted_signal_events_sigma: 106
  reported_significance_sigma: 3.7
```

该基准用于检查完整 publication forward model。不得通过乘一个经验 normalization factor 强制得到 347。

## 13. 数值与单元测试

至少检查：

```python
assert abs(sum(fission_fractions.values()) - 1.0) < 1e-12
assert abs(sum(ge_abundances.values()) - 1.0) < 1e-6
assert np.all(np.diff(bin_edges_evee) > 0)
assert np.all(response_matrix >= 0)
assert np.allclose(response_integral_over_full_domain, 1.0, rtol=1e-4)
assert np.all(counts_components >= 0)
assert np.allclose(counts_total, counts_components.sum(axis=(0, 1, 2)))
```

完成全部输入后：

```python
assert abs(sm_total_events - 347.0) <= agreed_publication_tolerance
```

## 14. Codex 应创建

```text
src/cevns_pyeft/experiments/datasets/conus_plus_2025.py
src/cevns_pyeft/experiments/datasets/slow_counts_conus_plus_2025.py
src/cevns_pyeft/experiments/fluxes/reactor_conus_plus.py
src/cevns_pyeft/experiments/detector/ge_ionization.py
src/cevns_pyeft/experiments/detector/ge_resolution.py
src/cevns_pyeft/experiments/detector/tabulated_efficiency.py

tests/test_conus_plus_2025_flux.py
tests/test_conus_plus_2025_target.py
tests/test_conus_plus_2025_response.py
tests/test_conus_plus_2025_counts.py

notebooks/slow_counts_conus_plus_2025_check.ipynb
```

若公共组件已存在，必须复用，不能创建实验专属副本。
