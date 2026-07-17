# CONUS+ 2025 可执行复现规格

## 0. 定位

```yaml
spec_status: executable_reproduction_approximation
publication_likelihood_reproduced: false
```

该模式用于让 Codex 直接写出一条完整 forward-prediction 链。它不替代 `conus_plus_2025_publication.md`。

## 1. 通量

读取：

```text
data/conus_plus_2025_reproduction/reactor_spectrum_shape.csv
```

定义：

\[
rac{d\Phi}{dE_
u}=1.5	imes10^{13}\,p(E_
u)
\quad[\mathrm{cm^{-2}s^{-1}MeV^{-1}}],
\]

其中 `normalized_shape_per_mev` 的数值积分为 1。

中央能区按 Daya Bay Eq. (8)：

\[
S_A=S_{m total}+\Delta f_{235}S_{235}+\Delta f_{239}S_{m combo}
+\Delta f_{238}S_{238}+(\Delta f_{241}-0.183\Delta f_{239})S_{241}.
\]

Daya Bay 裂变份额：

```text
0.564, 0.076, 0.304, 0.056
```

KKL 裂变份额：

```text
0.53, 0.08, 0.32, 0.07
```

`U238` Mueller 与 `Pu241` Huber 采用：

\[
S(E)=\exp\left(\sum_{i=0}^{5}a_iE^iight).
\]

```yaml
U238_Mueller: [4.833, -4.616, 1.988, -0.4828, 0.05576, -0.002091]
Pu241_Huber: [2.990, -2.882, 1.278, -0.3343, 0.03905, -0.001754]
```

高能段使用 Daya Bay 高能测量并采用固定的小幅裂变份额修正。低于 1.8 MeV 在本模式设为零。

## 2. 靶核

天然锗五同位素，读取：

```text
data/conus_plus_2025_reproduction/natural_germanium_isotopes.csv
```

## 3. 曝光和 detector

```yaml
C2: {exposure_kg_day: 109, threshold_evee: 180}
C3: {exposure_kg_day: 109, threshold_evee: 160}
C5: {exposure_kg_day: 109, threshold_evee: 170}
```

平均分配曝光是显式近似。

## 4. 响应

```yaml
lindhard_k: 0.162
lindhard_k_sigma: 0.004
fano_factor: 0.11
pair_creation_energy_eV: 2.96
noise_fwhm_evee: {C2: 48, C3: 47, C5: 47}
```

\[
\sigma_{0,d}=rac{\mathrm{FWHM}_d}{2.35},\qquad
\sigma_d(E)=\sqrt{\sigma_{0,d}^2+F\eta E}.
\]

## 5. 效率和分箱

每台 detector 使用阈值阶跃效率；分析边界为 160–800 eVee，步长 10 eVee。

## 6. 验证

```python
assert abs(np.trapz(shape, energy) - 1.0) < 5e-3
assert sum(detector_exposure.values()) == 327
assert counts_components.shape == (3, 5, 4, 64)
assert np.allclose(counts_total, counts_components.sum(axis=(0,1,2)))
```

不得把总事件与 347 的差异通过经验 normalization 消除；差异应作为近似响应和缺失官方 efficiency 的诊断。
