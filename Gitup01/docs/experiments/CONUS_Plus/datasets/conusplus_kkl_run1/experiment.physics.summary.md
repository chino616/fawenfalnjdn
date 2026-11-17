# CONUS+ onboarding v3 精简版（2026-11-06）

<!-- report-navigation:start -->
[详细物理说明](experiment.physics.md) · [用户资料](EXPERIMENT_USER_INPUT.md) · [来源登记 P00](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P00_SOURCE_REGISTER.yaml) · [证据台账 P01](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P01_EVIDENCE_LEDGER.yaml) · [缺失与冲突 P02](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P02_MISSING_AND_CONFLICTS.md) · [配置草稿 P03](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P03_PHYSICS_CONTRACT.yaml) · [Benchmark 登记](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/benchmark/BENCHMARK_REGISTER.md) · [资料目录](README.md)
<!-- report-navigation:end -->

主文件已整合本轮数据来源和引用，版本状态为 PARTIAL。采用天然 Ge 五同位素、Nuclear Response、参考 PDF 的 Flux 和用户选定的零端点。

## 已有资料

Mueller 24 系数已核原表，32 个低能点已核用户 PDF 表 2，天然锗质量/丰度和物理常数已核 NIST/CODATA，19 个观测点已核指定图 1。[详细版参数与公式](experiment.physics.md)

## 当前缺口

| 事项 | 已有依据 | 仍需补充/核验 | 影响与下一步 |
| --- | --- | --- | --- |
| 低能 32 点原始出处 | 用户 PDF 表 2 和本轮 Flux 文献图 | Kopeikin 原文图/表或作者数值文件 | 全谱归一化的原始来源限制，继续向上游核对 |
| Ge Response 数值链 | 本地 JSON、五个 Ge key、读取器与指纹 | 原始核计算论文/数据包/生成脚本及归一化转换 | Response 可信预测前处理 |
| 统计误差约定 | 原图上下误差及算术平均候选列 | 拟合前确认对称化办法，或取得作者数表 | 进入统计实现时确认 |
| 实现核验 | 源谱、靶核数、响应公式与单位已有 | 反中微子接口、Response 归一化、预测单位映射和积分收敛 | Phase 0 中分配实现与验证步骤 |

## 下一步

可据详细版进行 Phase 0 路线与输入审阅。数据的原始出处补充、Response 接口核验和拟合前误差约定分别列在 P02。[待补事项](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/P02_MISSING_AND_CONFLICTS.md)
