# 模块化与接口审阅

范围更新：2026-10-28，按用户要求聚焦程序模块化、物理交接与接口；不安排外部时间数据接入。

## 实际组合边界

Source/Run → DetectorFluence；TargetInventory → 真实核数；Interaction → cm²/keV；Observation → 概率与选择；Prediction → 带轴 events/bin。合同检查单位、实际坐标、shape、有限值及归一化责任，执行器不按实验名字选公式。

## R5 接口审阅

1. 从实际实例导出 ModuleDescriptor、依赖图、能力和内容指纹。
2. 替换 source 或 efficiency 的一个插槽，通过同一 predict 入口验证结果及实例隔离。
3. 参数确实被消费；未知配置和未支持能力应给出明确错误。
4. 保留旧 import、默认物理约定、输出键和历史 raw 含义。
5. 核对 Fast/Slow 使用同一模型；扫描参数与预积分依赖分离。
6. 用内容指纹拒用过时模板，不把同一路径或相同 shape 当作物理兼容。

## R6 交付

运行共享数据集回归、wheel 构建与项目外 import/资源读取；发布实际能力、示例、差异和恢复记录。保留模型适用域及统计近似的限制，不将接口验证当作外部物理审核。
