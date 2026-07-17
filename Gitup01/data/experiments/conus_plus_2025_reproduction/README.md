# CONUS+ 2025 可执行复现配置

此目录提供一个**明确标注为近似**的可执行 forward-model 配置，目的是让 Codex 可以先完成程序，而不是声称复现官方 likelihood。

## 通量构造

1. 1.925–7.675 MeV：使用 Daya Bay unfolded `Total`、`U235`、`Pu combo`，按 Daya Bay 论文 Eq. (8) 调整到 KKL 裂变份额；
2. `U238` 使用 Mueller 指数多项式，`Pu241` 使用 Huber 指数多项式；
3. 7.75–10.75 MeV：使用 Daya Bay 高能总谱，并把 7.675 MeV 处的 KKL/Daya Bay 比值作为常数修正；
4. 低于 1.8 MeV：此复现配置设为零。CONUS+ 当前阈值主要对应大于约 5 MeV 的反中微子，因此这用于程序开发，但不是论文的 Estienne 低能扩展；
5. 归一化采用固定探测器位置总通量 `1.5e13 cm^-2 s^-1`，`normalized_shape_per_mev` 在所给能区积分为 1。

## 探测器近似

- 三台 detector 的 327 kg·day 曝光平均分配为 109 kg·day；
- efficiency 采用各自阈值上的阶跃函数；
- 使用论文公开的 Lindhard、Fano 和低能 FWHM；
- 不包含正式非线性校正、逐能量 trigger efficiency、背景或 likelihood。

输出必须标记：

```yaml
implementation_mode: reproduction_approximation
publication_likelihood_reproduced: false
```
