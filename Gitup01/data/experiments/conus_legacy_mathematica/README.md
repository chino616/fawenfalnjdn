# CONUS Legacy Mathematica 数据

本目录保存用户提供的 Mathematica 参考计算所使用的实验层参数。

它只用于回归测试，不是 CONUS+ 2025 publication 数据。

已冻结：

- 固定总通量；
- 裂变份额；
- Ge73-only；
- 119 kg·day；
- Lindhard 与 Gaussian 参数；
- 阶跃 efficiency；
- 分箱。

未包含：

- Mathematica 外部 Mueller/Kopeikin 函数的全部系数；
- 固定 Wilson 点的逐 bin Mathematica 导出 reference。

因此在补齐这两项前，只能验证 detector response 和接口，不可声称完整数值逐 bin 等价。
