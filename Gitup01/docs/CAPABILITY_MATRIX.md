# 实际能力

| ID | Slow与实际组件 | Fast | 统计 |
|---|---|---|---|
| CsI2021 | ExperimentModel；source/targets/interaction/observation/run | interface_kernel_v1；满足系数和态合同的替换可重编 | 原近似Gaussian；counts/PE转换一次 |
| CsI2017 | ExperimentModel＋固定251点确定性映射；源/截面/响应可替换，保留14.6kg与元数据14.57kg差异 | 原legacy系数核；任意新组件明确拒绝，默认物理设置可重建 | 25箱外部表＋显式坐标schema；原近似Gaussian |
| Ar2020 | ExperimentModel＋sigma(observed)专用折叠；实际源/截面/响应 | 原legacy系数核；同上 | 原非对称IRLS；历史单位约定保留 |

全部支持统一load/predict/evaluate、严格selection、资源作用域与深层快照。
实际装配进入物理身份；统计输入独立记录，不因只改观测/误差重建物理核。
所有模块替换仍受本实验的靶材、轴、过程与数值策略能力约束，不承诺任意过程自动获得Fast。
验证结果见 [VALIDATION](VALIDATION.md)。
