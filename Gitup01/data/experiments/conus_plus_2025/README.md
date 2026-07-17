# CONUS+ 2025 数据目录

## 可直接使用的公开配置

- `experiment.yaml`：公开总量与模型状态；
- `natural_germanium_isotopes.csv`：天然锗组成的项目默认表，正式发表前应固定来源版本；
- `detector_config.csv`：C2/C3/C5 阈值及缺失字段；
- `bin_edges_evee.csv`：160–800 eVee、10 eVee 边界；
- `summary_metrics.csv`：公开总事件基准。

## 必须由用户补齐的模板

- `reactor_spectrum_conus_plus_TEMPLATE.csv`；
- `efficiency_C2_TEMPLATE.csv`、`efficiency_C3_TEMPLATE.csv`、`efficiency_C5_TEMPLATE.csv`；
- `resolution_parameters.csv` 已填入论文公开参数；
- `observed_counts_TEMPLATE.csv`；
- `background_TEMPLATE.csv`；
- `covariance_TEMPLATE.csv`。

空白单元格表示缺失数据，不能自动解释为零或一。

## 数据来源状态

```text
publication_summary       论文正文可核对的数值
external_official_input   外部实验官方 ancillary data
publication_value         首次观测论文明确给出的数值
requires_input            必须补齐
project_default           项目采用的常规数值，必须记录来源版本
```
