# Phase0 CONUS+ SM 输入交接

隔离候选，结果人工审核状态为NOT_REVIEWED。

<a id="report-toc"></a>

## 目录

- [输入、来源与实际核对](#section-1)

<a id="section-1"></a>

## 输入、来源与实际核对

| 阶段 | 本次工作 | 实际结果 |
| --- | --- | --- |
| Phase 0 | 恢复 conusplus_kkl_run1，选择原有 Slow executor | 已保存实施计划与输入指纹 |
| P01 | 19 箱、eVee、signed excess 数据语义 | 按原图取点表读入 |
| P02 | 天然 Ge 五同位素、核数和曝光 | 核数与质量归一化检查通过 |
| P03 | 已准备的非负反应堆谱 | 生成脚本 --check 与注量积分检查通过 |
| P04–P05 | 原有 Li2026LegacyInteraction、五个 Response key | SM 适用约定、基底、单位和运动学检查通过 |
| P06 | Lindhard + Gaussian 箱概率 adapter | CDF 与独立箱内积分一致，窗外损失保留 |
| P07 | 项目 core.predict，backend=slow | 最终网格及独立加密结果见数值节 |
| P10 | 图线对照、来源和能力检查 | 已产出本报告与阶段交接，科学来源状态 PARTIAL |
| P08、P09 | 本次未请求 | NOT_RUN / NOT_REVIEWED |

实际调用为 `ExperimentModel → core.predict.predict → rates.recoil.integrate_recoil_yield → Li2026LegacyInteraction → rates.folding.probability_fold`。源表、核表和共享包来自独立 snapshot。

本次新增的探测器 adapter 只返回无量纲箱概率。真实反冲直接以 keV 积分，Lindhard 映射进入箱概率，因此折叠时不再另乘 dT/dEee。

归一化路径为探测器处每秒通量 × 119×86400 秒 → 每核反冲产额 → 1 kg 中各同位素核数 → 重建箱概率。图中纵值由 Nᵦ / 1 kg × 10 eVee / ΔEᵦ 得到，本次 ΔEᵦ=10 eVee，因此数值等于逐箱事件数。

[阶段报告目录](../phase_reports/README.md) · [实施计划](../EXECUTION_PLAN.json) · [输入与代码快照](../INPUT_SNAPSHOT.json)

[返回目录](#report-toc)
