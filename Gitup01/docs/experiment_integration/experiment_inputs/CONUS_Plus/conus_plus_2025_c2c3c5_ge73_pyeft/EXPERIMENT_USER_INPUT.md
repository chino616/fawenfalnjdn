# CONUS+ C2/C3/C5 Ge73 CEvNS-pyEFT：用户输入表

```yaml
experiment_name: "CONUS+"
experiment_slug: CONUS_Plus
dataset_id: conus_plus_2025_c2c3c5_ge73_pyeft
scope_gate: APPROVED
```

本文件由通用模板
`workflows/experiment-integration/templates/onboarding/EXPERIMENT_USER_INPUT_TEMPLATE.md`
复制并预填。它是资料接收和核对记录，不是运行时 `experiment.yaml`。

状态说明：`SOURCE_EXTRACTED` 为材料摘录，`USER_CONFIRMED` 为用户已选择，
`PROJECT_DERIVED` 为项目推导，`REFERENCE_ONLY` 只用于比较，`MISSING` 为待补。

## 1. 实验身份、资料与目标

| 项目 | 已填写内容 |
| --- | --- |
| 实验名称、运行期和唯一数据集名称 | CONUS+ 首次测量配置；`conus_plus_2025_c2c3c5_ge73_pyeft`；`USER_CONFIRMED` |
| 本表覆盖的探测器或运行配置 | C2、C3、C5；C4 因不稳定排除；阈值分别为 180、160、170 eVee；`USER_CONFIRMED` / arXiv:2501.17843v2 Sec. III |
| 主要论文、补充材料、官方数据文件 | `docs/CONUS_docs/2501.17843v2.pdf`；`docs/CONUS_docs/2026_07_16_CEvNSpyEFT - CONUS.pdf`。官方实验论文 arXiv:2501.05206 及机器可读数据未提供，记为 `MISSING` |
| 可选的旧程序或参考数组 | 未提供；`MISSING`。备份区内容受 `BACKUP_QUARANTINE`，不作为输入 |
| 本次科学目标 | 先完成 C2/C3/C5 的 CEvNS-only 真实反冲谱、重建谱和逐箱 authoritative Slow，再处理可实现的 Fast；主线冻结后新增论文 response/statistics benchmark |
| 结果性质 | `hybrid_approximate_signal_forward_model`：实际 detector scope + Ge73-only + 项目统一核 Response + 理想阶跃效率；`USER_CONFIRMED` |

## 2. 输出量与数据轴

| 项目 | 已填写内容 |
| --- | --- |
| 真实核反冲量和单位 | 核反冲能量 `T`，`keVnr`；`SOURCE_EXTRACTED` |
| 最终观测量和单位 | 重建电离能 `E_reco`，`eVee`；`SOURCE_EXTRACTED` |
| 希望保留的分量轴 | `detector × isotope × reactor_component × reconstructed_bin`；预期细分 shape `3 × 1 × 4 × 19`，另给各级 total；`PROJECT_DERIVED` |
| 输出是计数还是率 | Slow/Fast 正式输出为 `expected_events/bin`；诊断谱可另存率，但不得混用 |
| 精确 bin edges | 160–350 eVee、10 eVee 步长，共 19 个相邻半开区间；最终上边界 350 eVee；`SOURCE_EXTRACTED`，Phase 1 再冻结 edge convention |

## 3. 中微子源

| 项目 | 已填写内容 |
| --- | --- |
| 入射粒子、flavor 或 flavor 状态 | reactor electron antineutrino，`antinue`；CEvNS only；`USER_CONFIRMED` |
| 需要分别输出的源分量 | U235、U238、Pu239、Pu241 及 total |
| 能谱公式或数值表 | Eν < 2 MeV 使用32点 Kopeikin 表线性插值；2–10 MeV 使用 Mueller 指数多项式；节点和系数已在 Phase 3 保存为独立 CSV |
| 能量范围及单位 | 0–10 MeV；0–0.01 MeV 使用前两节点线性外推并截断负值；Mueller 拟合依据范围为2–8 MeV，8–10 MeV 当前继续同一多项式但明确作为模型延拓；支持区外取零 |
| 谱值单位与时间基准 | 最终 differential detector-site flux：`cm^-2 s^-1 MeV^-1`，per second |
| 数值表处理规则 | 各同位素以 `S_r^Mueller(2)/rho_Kopeikin(2)` 独立匹配，使四分量和总谱在2 MeV连续；全能区积分归一化到固定总通量；`USER_CONFIRMED` |

**绝对归一化：**

- [x] **A. 探测器位置绝对总通量。** `1.5e13 cm^-2 s^-1`；不含运行时间。
- [ ] **B. 热功率、基线和裂变能推导。** 不作为本数据集归一化路径。

裂变份额：U235=0.56、U238=0.07、Pu239=0.31、Pu241=0.06；Phase 3 验证和为1。

Phase 3 复算得到 `rho_Mueller(2)=1.2580795232698319`、总匹配因子
`0.9677534794383323`、非负低端方案的 `N_rho=6.461355163040058`。论文给出的
4.6% 通量归一化不确定度保存为 metadata；当前 signal-only forward model 不采样该
nuisance，若以后请求 statistics 再由 Phase 9 接管。

## 4. 靶材、曝光、截面与运动学

| 项目 | 已填写内容 |
| --- | --- |
| 靶材料和同位素组成 | Ge73-only，number fraction=1.0；这是用户选择的 hybrid approximation，不是实际天然锗组成 |
| 靶核质量或摩尔质量来源 | `A=73, Z=32, N=41`；Phase 2 已批准项目约定 `m=73×1.6605390666e-27 kg`，即 `8.249507893261811e24 nuclei/kg`；`USER_CONFIRMED` / `PROJECT_DERIVED` |
| 每台探测器曝光 | 本轮正式计算采用 C2=C3=C5=119 kg day，合计357 kg day；实际资料值111.15/103.40/111.86 kg day及其326.41总和保留为参考元数据，不参与本轮主计算；`USER_CONFIRMED` |
| 散射模型和参数点 | CEvNS-pyEFT Wilson basis；SM 低能弱混合角 `sin^2(theta_W)=0.23857`；完整 Wilson basis/order 待 Phase 4/8 核验 |
| 核 form factor/Response 的要求 | 使用项目统一 Ge73 nuclear Response；不得替换为论文的天然锗 Klein–Nystrand 模型 |
| 运动学和截面约定 | CEvNS elastic scattering；基准材料给出重核近似 `E_nu,min=sqrt(m_A T/2)`；最终项目截面接口、精确单位与边界在 Phase 5 冻结 |

所选119 kg day曝光已为 `mass × live time`，Slow 中只能乘一次；源通量仍为 per second，因此时间换算由 Slow normalization ledger 明确所有权。不得从实际曝光下的最终计数按比例缩放得到119 kg day结果。

## 5. 探测器响应

| 项目 | 已填写内容 |
| --- | --- |
| 平均映射 | Lindhard：`epsilon=11.5 Z^(-7/3) T`，`g=3 epsilon^0.15+0.7 epsilon^0.6+epsilon`，`Q=k g/(1+k g)`，`Eee=1000 Q T`；`k=0.162` |
| 分辨率或迁移核 | Gaussian；`sigma(Eee)=sqrt(sigma0^2+F*eta*Eee)`；`sigma0=20.38 eVee`、`F=0.1096`、`eta=2.96 eV` |
| 响应核归一化范围 | `MISSING`：全实轴、非负物理域或数值截断域尚未冻结，Phase 6 必须决定并验证 |
| 效率/接受率 | 重建能量上的精确阶跃函数；阈值以下0，阈值及以上1；`USER_CONFIRMED` |
| 阈值、窗口和差异 | C2=180、C3=160、C5=170 eVee；公共分析网格160–350 eVee，再按 detector mask |

## 6. 逐箱输出检查

| 项目 | 已填写内容 |
| --- | --- |
| 分箱观测量和单位 | `E_reco`，eVee |
| bin edges 规则 | `160 + 10*i` eVee，`i=0..19`；Phase 1 生成机器可读边界表 |
| 分量输出含义 | detector=C2/C3/C5；isotope=Ge73；source=U235/U238/Pu239/Pu241；bin=19个重建能量箱 |
| 计数归一化 | `expected_events/bin`，已乘各 detector exposure；禁止再次乘 mass 或 live time |

## 7. 统计分析

当前先完成 signal forward model 主线；其后按已请求的论文 benchmark 顺序处理 Fig.1、弱混合角、一维/二维 vector NSI 和 CEvNS-only 磁矩曲线。

材料中存在19-bin background-subtracted excess 和 `sigma_alpha=0.169` 的简化 χ²，
但 Fig. 1 单位与迁移笔记中的“counts”语义尚未完全一致，且没有官方机器可读表。
这些内容在 Phase 9 Data Semantics Gate 前仍为 `REFERENCE_ONLY`。缺少官方表时可采用明确标记的 PDF 数字化 excess 与误差条，并保留负 excess；不得称为官方 likelihood。

## 8. 外部数值基准

| 项目 | 已填写内容 |
| --- | --- |
| 参考结果 | 论文 SM 预测 C2=90、C3=143、C5=113、total=346 |
| 输入点 | 天然锗、论文 Klein–Nystrand form factor、论文 detector model；不是本数据集的 Ge73-only/项目 Response 输入 |
| 单位、轴和归一化 | detector total expected events；已乘论文 detector exposure |
| 来源类型 | arXiv:2501.17843v2 Sec. III；`REFERENCE_ONLY` |

禁止用经验 normalization 强迫 Ge73-only 结果匹配 90/143/113/346。本数据集的正式
Slow reference 必须由已批准的 Ge73-only 链生成。

## 9. 补充项与 Fast

- Fast 目标：`reconstructed_spectrum_cumulative` 和 `eft_quadratic_coefficient_kernel` 候选。
- Fast 必须从 Human-approved Slow 派生。
- 完整 Wilson coefficient basis/order、20组模板的全部映射和有效参数域目前 `MISSING`；EFT Fast 在补齐前保持 `BLOCKED`。
- 通量、k、阈值、active mass 等不确定度如以后进入 statistics，再按 Phase 9 补充。

## 10. 缺失与冲突

| 字段 | 缺失或冲突 | 已查来源 | 影响 |
| --- | --- | --- | --- |
| 官方实验材料 | arXiv:2501.05206 PDF、补充材料和机器可读数据未提供 | 两份本地 PDF | publication/official likelihood claim |
| Ge73 Response key | `Ge73` 已由 `ResponseDB` 实际加载；8个项目响应通道可读取 | `data/responses/responses_all.json`、Phase 2 检查 | 已解决；外部源表审计仍归 Phase 4 |
| 实际曝光与本轮计算曝光 | 实际值111.15/103.40/111.86仅保留为资料；本轮计算明确覆盖为三台各119 | 用户明确要求；2501.17843v2 Sec. III | P02记录与P07绝对计数 |
| Mueller高能范围 | 系数拟合依据范围为2–8 MeV；当前8–10 MeV为继续多项式的模型延拓 | Mueller原文与Helm审计 | P03适用范围说明、P07逐bin敏感性、论文尾部比较 |
| 响应积分域 | Gaussian full-domain/truncation 规则未冻结 | 两份 PDF | Detector、Slow |
| 完整 Wilson basis | 只看到部分模板说明，缺完整20组映射 | 2026迁移笔记 | EFT Fast |
| Ge73-only 外部基准 | 90/143/113/346属于天然锗论文模型 | 2501.17843v2 | 外部数值验证 |
| 统计数据语义 | Fig. 1 单位与迁移表的 counts 说法需核对 | 两份 PDF | Statistics only |
| 字面低端线性外推 | 在0–0.006538 MeV产生负值；已批准改为非负截断，归一化相对变化7.16e-5 | 迁移笔记表2与Phase 3复算 | Source 已解决 |

## 渐进式细节计划

按 `PROGRESSIVE_DETAIL_LOOP`，整体方案先进入 Master Scope Gate；Phase 1–10 到达各自
字段时再定向抽取和保存详细 CSV/YAML/NPZ。当前文件不要求提前生成所有数值表。
