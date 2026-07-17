# `<dataset_name>` CEvNS 实验物理规格模板

## 0. 文档状态

```yaml
spec_status: REQUIRES_INPUT
implementation_mode: publication | legacy | reproduction
```

本文件必须与 `skills/integrate-cevns-experiment/SKILL.md` 一起使用。
任何核心 forward-model 字段仍为 `REQUIRES_INPUT` 时，Codex 不得把实现标为 publication-ready。

## 1. 数据集身份

```yaml
experiment_family: REQUIRES_INPUT
dataset_name: REQUIRES_INPUT
dataset_version: REQUIRES_INPUT
publication: REQUIRES_INPUT
analysis_channel: REQUIRES_INPUT
```

## 2. 中微子源

```yaml
source_type: stopped_pion | reactor | solar | accelerator_continuous | custom_tabulated
flavors: []
production_components: []
time_basis: per_second | integrated
```

给出完整通量定义：

```yaml
flux:
  representation: analytic | tabulated | piecewise
  energy_min_mev: REQUIRES_INPUT
  energy_max_mev: REQUIRES_INPUT
  output_unit: REQUIRES_INPUT
  normalization_mode: REQUIRES_INPUT
  formula_or_file: REQUIRES_INPUT
  interpolation: REQUIRES_INPUT
  extrapolation: REQUIRES_INPUT
```

若为反应堆，必须给出四种裂变份额、每次裂变能量、功率与基线，或给出已经归一化的探测器位置总通量；两种归一化方式不能同时使用。

## 3. 靶材

```yaml
target_material: REQUIRES_INPUT
target_mode: natural_mixture | compound | single_isotope
isotopes:
  - isotope: REQUIRES_INPUT
    response_key: REQUIRES_INPUT
    abundance_or_stoichiometric_count: REQUIRES_INPUT
```

## 4. 曝光

```yaml
exposure:
  mode: mass_and_time | kg_day
  detectors: REQUIRES_INPUT
```

## 5. 真实核反冲谱

声明截面入口、单位、运动学范围和 recoil grid。

## 6. 观测量

```yaml
observable:
  name: REQUIRES_INPUT
  unit: REQUIRES_INPUT
```

## 7. 平均响应

给出 \(\bar x(T)\) 的完整公式、参数和单位。

## 8. 分辨率/涨落

给出 \(R(x\mid T)\) 的完整公式、参数和归一化检查。

## 9. 效率

```yaml
efficiency:
  domain: true_recoil | mean_observable | reconstructed_observable
  files: REQUIRES_INPUT
  interpolation: REQUIRES_INPUT
  outside_range: REQUIRES_INPUT
```

## 10. 分箱

```yaml
binning:
  observable: REQUIRES_INPUT
  unit: REQUIRES_INPUT
  edges_file: REQUIRES_INPUT
```

## 11. 背景和数据

明确 ON/OFF、背景模型、残差谱、协方差和 likelihood 的可用程度。

## 12. 系统误差

逐项写明是归一化、谱形还是 bin migration nuisance。

## 13. 数值设置

```yaml
numerical:
  enu_grid: REQUIRES_INPUT
  recoil_grid: REQUIRES_INPUT
  observable_grid: REQUIRES_INPUT
  integrator: REQUIRES_INPUT
  rtol: REQUIRES_INPUT
  atol: REQUIRES_INPUT
```

## 14. 验证基准

```yaml
validation:
  flux_integral: REQUIRES_INPUT
  sm_total_events: REQUIRES_INPUT
  sm_binned_reference: REQUIRES_INPUT
```

## 15. Codex 文件清单

列出实际应创建的 `.py`、`.yaml`、测试和 notebook 文件。

## 16. 停止条件

列出本实验中任何不得猜测的参数。
