# Missing and Blocking Matrix — conus_plus_2025_c2c3c5_ge73_pyeft

```yaml
experiment_name: "CONUS+"
experiment_slug: CONUS_Plus
dataset_id: conus_plus_2025_c2c3c5_ge73_pyeft
scope_gate: APPROVED
```

本表按 `PROGRESSIVE_DETAIL_LOOP` 管理。未到对应 Phase 的细节不要求现在补齐；到达
`needed_by_phase` 时再从已登记材料定向提取，仍缺失时才询问补充材料。

| 字段 | 状态 | needed_by_phase | blocks dataset | blocks Slow | blocks Fast | blocks statistics | 解决方式 |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| Ge73 actual Response key | RESOLVED_BY_PROJECT_AND_USER | 2 | no | no | no | no | `ResponseDB` 已加载 key `Ge73`；A=73、Z=32、N=41；外部源表审计仍归 Phase 4 |
| Exact bin edge convention | RESOLVED_BY_USER | 1 | no | no | no | no | 20条边界、19个 `[low, high)` bins、窗口 `[160,350)` 已由 Phase 1 冻结 |
| Mueller coefficients and 32 Kopeikin nodes in machine-readable form | RESOLVED_BY_SOURCE_AND_USER | 3 | no | no | no | no | 已逐值保存为两份 CSV，并通过节点数、顺序和系数检查 |
| Source interpolation/matching implementation | RESOLVED_BY_USER_AND_PROJECT | 3 | no | no | no | no | 非负低端外推、逐同位素2 MeV连续拼接和绝对归一化检查通过 |
| Mueller 8–10 MeV high-energy continuation | CONTROL_REQUIRED | 3/7/10 | no | no for baseline Slow | no | no | 主线保留同一Mueller多项式延拓；P07逐bin分离`E_nu>8 MeV`并运行替代延拓敏感性；不得调尾部强迫复现论文 |
| Complete CEvNS-pyEFT Wilson basis/order | MISSING | 4/8 | no | no for SM Slow | yes for EFT kernel | no | Phase 4 映射理论基底，Phase 8 构建 kernel |
| Kinematics/cross-section API and units | DRAFT | 5 | no | yes | yes | no | Phase 5 检查项目实际 callable |
| Gaussian normalization domain/truncation | MISSING | 6 | no | yes | yes | no | Phase 6 Physics Decision + normalization test |
| Ge73-only external binned benchmark | MISSING | 7/10 | no | no for internal Slow | no | no | 内部 Slow 可验证；不得宣称外部逐箱复现 |
| Official machine-readable excess data | MISSING | 9 | no | no | no | yes | 仅请求 statistics 时补充官方数据或批准数字化近似 |
| Fig. 1 unit versus project “counts” wording | CONFLICT | 9 | no | no | no | yes | Phase 9 Data Semantics Gate |
| Natural-Ge 90/143/113/346 versus Ge73 target | RESOLVED_AS_REFERENCE_ONLY | 10 | no | no | no | no | 只做诊断，不做 pass/fail 或 rescaling |
| Selected 357 calculation exposure versus 326.41 raw observed sum and 327 rounded publication value | RESOLVED_BY_USER | 2 | no | no | no | no | 主线计算采用C2/C3/C5各119；实际值111.15/103.40/111.86及327只保留为资料，不参与本轮主计算 |
| S001 sin²θW=0.2312 Fast constant versus selected 0.23857 | RESOLVED_BY_USER | 4/8 | no | no after implementation | yes until regenerated | no | 全链采用0.23857并重建模板 |

## Current capability impact

- Dataset Identity 和 Scientific Claim 已批准。
- Phase 1 已完成；Phase 2/3 的重新定基机器检查通过，等待用户审核新的曝光与高能延拓说明。
- Slow 尚不能实现，仍须完成 P02/P03 复核以及 Theory、Kinematics、Detector Gate。
- Cumulative Fast 可在 Slow freeze 后评估。
- EFT kernel 因完整 Wilson basis 缺失而 `BLOCKED`。
- Statistics benchmark 已请求，但只在 authoritative Slow 冻结后开始；当前统计缺失不阻断 signal forward model。
