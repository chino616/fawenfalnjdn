# Validation 与 Registry 片段

## Registry

优先由：

```text
data/experiments/<dataset_id>/experiment.yaml
```

自动发现。

只有 registry 无法加载新的 callable 类型时才修改：

```text
src/cevns_pyeft/experiments/registry.py
```

## 回归范围

```text
new dataset tests
existing CsI2017 tests
existing CsI2021 tests
existing Ar2020 tests
theory/response tests
Fast kernel tests
```

## Reference 规则

- reference 必须有来源和生成命令；
- 不允许仅因测试失败而更新 reference；
- Slow reference 与 Fast reference 分开；
- benchmark 与论文、旧程序或内部 reference 的等级必须标明。

## 完成状态

```text
DATASET_VALIDATED
TARGET_VALIDATED
SOURCE_VALIDATED
THEORY_VALIDATED
DETECTOR_RESPONSE_VALIDATED
SLOW_VALIDATED
FAST_VALIDATED
STATISTICS_VALIDATED
FULLY_INTEGRATED
```

## Gate V

```text
PASS / BLOCKED
```
