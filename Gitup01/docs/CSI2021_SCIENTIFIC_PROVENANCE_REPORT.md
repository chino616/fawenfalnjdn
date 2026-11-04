# Task 07 — CsI2021 Scientific Provenance Audit

2026-11-04；branch `refactor/07-gitup01-20261104`；HEAD
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。保留工作区修改及三份并行候选，未提交。
读取 Task07/规则/顺序、Pilot/Tasks02–06 报告、真实三文件、核响应/反中微子审计、
消费者和当前冻结参考；来源搜索仅当前 docs/data/代码及下列网页，未搜索 backup。

## 原始来源与版本

- [COHERENT 官方 data 页](https://sites.duke.edu/coherent/data/)：2026-11-04 读取。
  “full CsI … 2021”指向 arXiv:2110.07730 的 ancillary；2018 首次观测、Ar2020、2023 反冲校准
  为不同数据发布，不替代本九箱输入。
- [CsI 实验论文 v2，2022-06-02](https://arxiv.org/html/2110.07730v2)，
  DOI [10.1103/PhysRevLett.129.081801](https://doi.org/10.1103/PhysRevLett.129.081801)：
  Experiment 段给出 19.3 m、约14.6 kg、3.20e23 POT 和0.0848产额；Data analysis 段明确
  PE×时间的二维拟合，含形状 nuisance。不能等同九箱独立误差 Gaussian。
- [v2 ancillary 清单](https://arxiv.org/src/2110.07730v2/anc)：存在 beam-on/AC events、BRN/NIN、
  efficiency/scintillation coefficients、SNS ROOT 和 supplement。只核对下面两份小文本，
  未将二维事件/ROOT 静默重投影为九箱或导入新 dataset。
- [effCoefficients.txt](https://arxiv.org/src/2110.07730v2/anc/effCoefficients.txt)：nominal 行。
  [scintRespCoefficients.txt](https://arxiv.org/src/2110.07730v2/anc/scintRespCoefficients.txt)：nominal 行。
- [Li2026 v2，2026-09-21](https://arxiv.org/html/2601.19883v2)：Sec II Eq(1) 系数维度，
  Eqs(2–12)算符，Table2/App B 的 LEC；[期刊版本](https://doi.org/10.1103/klg7-36x7)。
  v1 与 v2 的部分 LEC 已变化，当前 L1/L2/L5–L8 与 v2 表值一致。
  本次没有完成逐算符全 matching、RG scale pipeline 或 helicity 符号证明。

## 原文与采用值抽查

| 字段 | 原文/定位 | package 采用值与单位 | 结论 |
|---|---|---|---|
| baseline | 实验 Experiment/Introduction | 19.3 m | 一致；未人工批准。 |
| mass | 实验 Experiment：14.6 kg | 14.57 kg | 原文舍入不能证明额外精度；保留 legacy。 |
| POT | 实验 Experiment：3.20e23 | 3.198e23 POT | 舍入兼容，精确版本尚缺。 |
| yield | 实验 Experiment：0.0848 | 0.0848 neutrinos/species/POT | 中心值一致；其不确定度未变成新 nuisance。 |
| q1..q4 | scintResp nominal 行 | .0554628,4.30681,-111.707,840.384；依次1/MeV^-1/MeV^-2/MeV^-3 | 完全一致；MeVnr 输入，转 keVee 的既有换算保留。 |
| efficiency a,b,c | eff nominal 行 | 1.32045,.285979,10.8646；1/PE^-1/PE | 一致。 |
| efficiency d | eff nominal：-.333322 | -.3333，1 | 差2.2e-5，保留 legacy 舍入；不悄悄修正。 |
| L1,L2 | v2 Table2/App B Eq144 | 1.855,-1.017，1 | 一致；v1 的1.355/-1.535不作为当前修正依据。 |
| L5..L8 | v2 Table2/App B Eq151 | .00138,-.00049,-.00676,.00265 GeV | 原文MeV×1e-3一致。 |

全部105个标量、17个模型及23数组的现有来源/采用值/单位/推导/consumer仍在 Physics MD。
另有逐字段 [SCIENTIFIC_REVIEW.json](experiments/COHERENT/CsI2021/SCIENTIFIC_REVIEW.json)：
未取得原文值的字段明确 null，不能将 legacy original_source_value 当成官方 raw value。
来源核对仅是 SOURCE_EXTRACTED，reviewer_decision 始终 NOT_REVIEWED。

## 九项问题与能力结论

| 问题 | 结论 | 依据、剩余缺失及限制 |
|---|---|---|
| S01 official_experiment_sources | LEGACY_ONLY | 已定位官方论文/ancillary，部分字段匹配；原九箱数组的提取/投影/舍入链仍缺，不能称官方完整复现。 |
| S02 eft_primary_conventions | LEGACY_ONLY | 已锁定v2；内部22 key、GeV^(4-d)、final×initial、LNC/LNV合同存在；全 matching/scale审核不完整。 |
| S03 nuclear_source_audit | MISSING | 仅聚合JSON/NPZ与内部多点等价；无独立原表/生成链。7通道、p/n/power和exp_factor按旧实现；I127 M_nn(0) residual未改。 |
| S04 antineutrino_kernel | BLOCKED | particle_kind保留但不进入核分支。一般EFT逐算符 helicity/sign/interference仍缺；共享核只属legacy。 |
| S05 statistics_semantics | CONFLICT | 官方二维profiled likelihood不同于九箱近似；residual/excess是否已扣BRN/NIN未闭合。Gaussian可作兼容，official likelihood阻断。 |
| S06 source_endpoint | LEGACY_ONLY | mask上限56 MeV、tab上限300、积分端点52.827952…；旧final-cell taper未重归一化。不是已证实物理精度。 |
| S07 detector_validity | MISSING | nominal quenching/efficiency部分可核对；Gamma标定、硬件阈值、Na效应、component time selection、完整有效域未逐项闭合。 |
| S08 legacy_status_and_reference | LEGACY_ONLY | 旧fast_validated及缺失run/reference均是历史；当前真实冻结reference为interface_refactor_v1/interface_kernel_v1。未改基线。 |
| S09 pilot_runtime | CONFIRMED（工程） | Task06安装引擎I01–I10和small/default回归通过；不授予科学批准，网格收敛诊断仍受限。 |

Signal、有限范围 Fast 和 legacy approximate statistics 技术能力保留；official likelihood、
general antineutrino EFT、scientific release继续BLOCKED。包仍DRAFT/PARTIAL，人工NOT_REVIEWED。
本任务不改任何参数、数组、公式或科学语义；版本/舍入差异保留并给出以后修正所需证据。

无新科学公式实现，因此不为文档制造数值测试。实际运行：三文件validator、受影响文档链接、
review JSON完整字段及九问题覆盖检查；结果写入进度。下一步通用 compiler，不能把来源可得
或技术PASS解释为自动人工接受。

[进度](ONBOARDING_TASKS_02_10_PROGRESS.md)
