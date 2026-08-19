# Statistics 片段

## 从用户文档和数据确定 data mode

只能选择一个主模式：

```text
raw_counts
signal_plus_background
on_off
background_subtracted_excess
unbinned_events
```

## CsI 局部参考

先检查当前仓库是否存在可复用统计层。  
CsI 只可参考相同 data mode 的数据 shape 和 nuisance 处理，不可整块复制 likelihood。

## 数据

```text
observed data
background
covariance
nuisance priors
correlations
test statistic
confidence construction
```

## 文件决策

优先使用 YAML + 通用统计函数。  
只有现有函数无法表达时才创建：

```text
statistics_<dataset>.py
```

## 强制检查

- excess 不重复扣背景；
- ON/OFF 不简化为统一比例，除非输入明确；
- Poisson 输入必须是非负原始计数；
- covariance shape；
- analytic profile 与数值最小化；
- benchmark statistic。

## Gate Q

```text
PASS / BLOCKED
```
