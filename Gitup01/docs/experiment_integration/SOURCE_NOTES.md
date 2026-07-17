# 来源与可信度说明

## CONUS+ publication

包内冻结的公开总量来自 CONUS+ 首次观测论文：

- KKL 3.6 GW；
- 约 20.7 m 基线；
- 平均裂变份额 0.53/0.08/0.32/0.07；
- C2/C3/C5 阈值 180/160/170 eVee；
- reactor-ON 327 kg·day、OFF 60 kg·day；
- 三台探测器总有效质量 2.83±0.02 kg；
- SM 预测 347±59、拟合信号 395±106、显著性 3.7σ。

## Daya Bay 数据

原始 ancillary 文件逐字复制到 `data/external/dayabay/`，解析 CSV 只提取文件开头的谱段，不修改数值。

## 天然锗丰度

`natural_germanium_isotopes.csv` 使用常见天然丰度值作为项目默认初值，并明确标记 `project_default_requires_source_freeze`。正式分析前必须由项目确定采用的权威来源和版本。

## 探测器响应

首次观测论文明确给出 Lindhard `k=0.162±0.004`、C2 `48±1 eVee` FWHM、C3/C5 `47±1 eVee` FWHM、Fano `0.11` 和电子-空穴对产生能 `2.96 eV`。

## Mathematica legacy

Legacy 参数来自用户提供的 2026-01-08 Mathematica 参考程序。它们只服务于迁移回归。

## 数据公开状态

Nature 论文声明完整数据目前不公开，可向 CONUS 合作组合理申请。因此包内不伪造逐 bin 数据、背景和 trigger-efficiency 参数。
