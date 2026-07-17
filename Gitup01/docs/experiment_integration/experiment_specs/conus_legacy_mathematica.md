# CONUS Mathematica 参考程序：Legacy 回归规格

## 0. 身份

```yaml
spec_status: executable_legacy_reference
implementation_mode: legacy_mathematica
dataset_name: conus_legacy_mathematica_2026_01_08
not_publication_model: true
```

本规格只用于把用户提供的 Mathematica 计算链迁移到 Python，并检查：

```text
isotope
→ reactor flux
→ dR/dT
→ Lindhard yield
→ Gaussian resolution
→ threshold efficiency
→ reconstructed bins
```

它不得被注册为 CONUS+ 2025 publication 默认配置。

## 1. 参考程序中的计算链

```text
CreateIsotopeModel
→ CreateReactorFluxMuellerKopeikin
→ CreateSofT
→ BuildSinterp
→ CreateGeDetectorResponse
→ Make_dNdEreco
→ MakeFastIntegralModel
→ binCounts
```

## 2. 通量

```yaml
flavor: nuebar
time_basis: per_second
normalization_mode: fixed_detector_site_total_flux
total_flux_cm2_s: 1.5e13
energy_min_mev: 0.001
energy_max_mev: 10.0
```

裂变份额：

```yaml
fission_fractions:
  U235: 0.56
  U238: 0.07
  Pu239: 0.31
  Pu241: 0.06
```

能谱模型名称：

```yaml
spectrum_model: Mueller_Kopeikin_legacy
```

该名称只表示复现原程序所调用的参考实现。若原 Mathematica 外部函数/系数未完整提供，Python 版本必须要求单独的谱表或同一公式实现，不能自行替换为 CONUS+ 2025 Daya Bay publication 谱。

原程序存在需要保留在诊断中的可疑变量传递：名为 `fluxPowerGW` 的值被传入 `EnuMaxMeV` 位置。Python 迁移不得照抄错误命名；应将最终使用的能量上限显式固定为 10 MeV，并记录行为差异。

## 3. 靶核

```yaml
target_mode: Ge73_only
isotope: Ge73
atomic_number: 32
mass_number: 73
response_key: Ge73
```

这是 legacy 近似，不是天然锗 publication 模型。

## 4. 曝光

```yaml
exposure_mode: kg_day
exposure_kg_day: 119.0
```

## 5. Lindhard 响应

```yaml
lindhard_k: 0.162
```

\[
\epsilon_L=11.5Z^{-7/3}T,
\qquad
g(\epsilon_L)=3\epsilon_L^{0.15}+0.7\epsilon_L^{0.6}+\epsilon_L,
\]

\[
Q(T)=\frac{k g(\epsilon_L)}{1+k g(\epsilon_L)},
\qquad
\bar E_{\rm ee}(T)=1000Q(T)T.
\]

## 6. 分辨率

```yaml
sigma0_eV: 20.38
fano_factor: 0.1096
pair_creation_energy_eV: 2.96
```

\[
\sigma(E)=\sqrt{\sigma_0^2+F\eta E}.
\]

## 7. 效率

```yaml
efficiency_model: reconstructed_energy_step
threshold_evee: 160.0
below_threshold: 0.0
at_or_above_threshold: 1.0
```

## 8. 分箱

```yaml
bin_min_evee: 160.0
bin_max_evee: 350.0
bin_width_evee: 10.0
```

边界表：

```text
data/conus_legacy_mathematica/bin_edges_evee.csv
```

## 9. 数值参考设置

```yaml
enu_grid_points: 600
recoil_min_kevnr: 0.0001
recoil_max_kevnr: 3.0
recoil_grid_points: 700
reconstructed_min_evee: 0.0
reconstructed_max_evee: 2000.0
reconstructed_grid_points: 801
```

## 10. 输出

```text
isotope × reactor_component × bin
```

虽然只有一个 Ge 同位素，仍保留 isotope 轴。

## 11. 验证

必须与 Mathematica 固定输入输出比较：

```text
mean ionization energy at selected recoil points
resolution width at selected Eee points
reconstructed spectrum at selected points
each bin count
total count
```

若未从 Mathematica 导出固定 reference，则只能完成接口和内部恒等检查，不能宣称逐 bin 数值一致。

## 12. 数据文件

```text
data/conus_legacy_mathematica/experiment.yaml
data/conus_legacy_mathematica/fission_fractions.csv
data/conus_legacy_mathematica/bin_edges_evee.csv
data/conus_legacy_mathematica/efficiency_threshold.csv
```
