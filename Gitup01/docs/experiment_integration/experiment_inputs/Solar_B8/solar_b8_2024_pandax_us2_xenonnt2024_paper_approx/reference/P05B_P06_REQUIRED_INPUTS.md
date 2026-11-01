# CEνNS-pyEFT 太阳 B8 迁移：P05-B / P06 缺失输入交付单

版本：2026-10-13。目标仓库分支：`conus-v2-current-snapshot-20261011/Gitup01`。运行标识：`ha-xenonnt-b8-snudd-20261012-01`。

## 0. 当前可核实状态及边界

来自用户提供的 `MIGRATION_PROGRESS.md`：P03(SNuDD) / P04(Xe) / P05(kinematics) 仅 `CANDIDATE_PASS`；P05-B `NOT_VERIFIED`；P06 `BLOCKED`；正式源码和原始 SNuDD 尚未修改。本数据包未读取本地 Windows F: 盘，未运行 SM 事件数，也未取得 2024 efficiency 曲线。禁止将下列已刊参考值标成计算产物。

**已获得：** 2025 现象学论文的 Eq.(31) 参数、PandaX US2 和 XENONnT 2024 曝光与阈值、Table III / IV 24 个 Λ_NS​​I 数值，以及 2026 Zenodo release 的固定 DOI/MD5/下载 URL。

**仍缺：** 2024 两实验的匹配 NR signal efficiency 数组、原文核响应数值或严格同等约定、PEANUTS exposure-averaged probabilities、Fig.4–6 等高线定量表。2026 官方 ZIP 有公开来源，但尚未在本机下载并审计。不能以 2026 detector response 证明已复现 2024 结果。

## 1. 确认的 2025 现象学论文数值

来源：Li, Song, Tang, Yu, *Phys. Rev. D* **111**, 035002 (2025), [arXiv:2409.04703v2](https://arxiv.org/html/2409.04703v2), §§III, IV.2, Appendix B.

- 公共太阳总通量：`5.46e6 cm^-2 s^-1`，相对先验 12%。注意真正微分能谱还需匹配能谱形状。
- 论文核响应：`131Xe`，但 target-number 正规化使用 `131.29 g/mol`（原文约定，不自动用 131 同位素摩尔质量替换）。
- PandaX-4T US2：`exposure=1.04 tonne·year`，`threshold=0.33 keVnr`，`N_meas=69.1`，`N_SM=44.9`，`sigma_stat=0.37*69.1`，`sigma_alpha=0.245`；signal efficiency 来自 PandaX 2024 Fig.1。
- XENONnT 2024：`exposure=3.51 tonne·year`，`threshold=0.5 keVnr`，`N_meas=10.7`，`N_SM=11.15`，`sigma_stat=3.95`，`sigma_alpha=0.13`。
- Paper Eq.(31)：`chi2=[N_meas-(1+alpha)*N_pred]^2/sigma_stat^2+(alpha/sigma_alpha)^2`。
- 闭式检验：`alpha_star=N_pred*(N_meas-N_pred)*sigma_alpha^2/(sigma_stat^2+N_pred^2*sigma_alpha^2)`；`chi2_profile=(N_meas-N_pred)^2/(sigma_stat^2+N_pred^2*sigma_alpha^2)`。
- 90% CL：论文对一维扫描使用 `DeltaChi2=2.71`；二维使用 `4.61`。必须对每个扫描按论文定义扣除全局最小值。
- `P05B_REFERENCE_VALUES.yaml` 收录 Table III/IV（12+12 数值，单位 GeV）。这是 Λ_NS​​I 的下界，不是 Wilson 系数本身。
- 论文 PandaX Table II 将 paired 曝光列为 1.25 t·yr，而 2024 实验原文摘要为 1.20 t·yr。P05-B US2 基准两者均不使用，固定 1.04 t·yr；不可静默合并。

## 2. P05-B 真正缺失的 2024 原始资料与交付格式

| 必需输入 | 官方/原文来源 | 建议目标产物 | 核验方法 |
|---|---|---|---|
| PandaX US2 NR efficiency | [PandaX 2024](https://arxiv.org/abs/2407.10892), Fig. 1 | `p05b/pandax_us2_efficiency.csv`，列 `E_nr_keV,efficiency` | 单位、阈值、图像数值化误差和每点来源 |
| XENONnT 2024 NR efficiency | [XENONnT 2024](https://arxiv.org/abs/2408.02877) 及配套 detector model | `p05b/xenonnt_2024_efficiency.csv` | 2024 分析专属、效率定义和版本匹配 |
| 131Xe 响应输入及规范 | [Li et al. 2025](https://arxiv.org/html/2409.04703v2) §III | `p05b/xe131_response_reference.*`+来源 | spin、W_M/W_Sigma、系数约定和归一化对照 |
| PEANUTS averaged probability | [Li et al. 2025](https://arxiv.org/html/2409.04703v2) Fig.2/3；[PEANUTS](https://github.com/michelelucente/PEANUTS) | `p05b/peanuts_probability_reference.csv` | E_ν [MeV]、Pee/Peμ/Peτ、日夜/地理时间权重、NSI 点 |
| Fig.4–6 contours | [Li et al. 2025](https://arxiv.org/html/2409.04703v2) Fig.4–6 | `p05b/fig4_ref.csv` 等 | 参数轴、轮廓连续分支、提取误差、CL 设置 |

重要：SNuDD 包含预定义的 XENONnT / PandaX-4T efficiency，但**不能在未比对分析年份及曲线定义时自动判定其为 2024 论文一致的输入**。可以用作候选 cross-check，必须保留 provenance 和 `UNVERIFIED` 标识。

如果 Fig.4–6 只有图片，允许透明数值化并保存人工检查记录、像素到坐标映射、图源、重复 digitization 偏差；不得宣称获得了作者原始数据。

### 2.1 P05-B 验收顺序

1. 先审计 2024 两条 efficiency 曲线是否为 nuclear-recoil selection efficiency，是否包含触发、ROI、重建和曝光，排除 double-count。
2. 用已完成的 SNuDD+Xe+运动学前向计算重新计算 `44.9` 和 `11.15`；分别报告 `N_raw`、`N_after_efficiency`、`N_after_exposure` 及积分误差；禁止乘“经验校正因子”。
3. 将论文 Eq.(31) 已实现的单参数 profile 连到真正预测 `N_pred(C)`；不得以常数参考事件数代替前向物理。
4. 检查一维 Wilson 符号、规范、扫描边界、Λ 与系数的映射，复现 Table III/IV。
5. 检查 MSW 传播是否与论文 §IV.2/Appendix B 的 PEANUTS 设定一致，复现 Fig.4–6；SM-only 物理对传播差异可能不敏感，但 flavor-dependent NSI 可能敏感。
6. 生成 `LEGACY_B8_REPRODUCTION_REPORT.md`，每项附命令、提交哈希、参考数据、差异、容差、图片和 `PASS/FAIL/NOT_VERIFIED`。

## 3. P06: 2026 官方 SR0+SR1+SR2 归档

- [Zenodo record 20576156](https://zenodo.org/records/20576156)，DOI `10.5281/zenodo.20576156`。
- [XENONnT GitHub tag `sr0_sr1_sr2`](https://github.com/XENONnT/cevns_data_release/tree/sr0_sr1_sr2)。
- 原始归档：`XENONnT/cevns_data_release-sr0_sr1_sr2.zip`，官方 MD5：`e0d740c3347fe13061e9cff576775632`。
- 运行 `FETCH_XENONNT_2026.ps1` 下载、核对 MD5、记录 SHA256、解压到原先外部路径；**本数据包不含 ZIP，未能代替官方归档**。
- README 指定观测四维：cS2、S2_pre/Δt_pre 的 quantile、S1 BDT、S2 BDT；四维 binning 在 `binning/`；`data/` 观测 CSV；`templates/sr*/mono/` mono NR 模板；`templates/sr*/ac|er|rg/` 背景；`plot.ipynb` 为读取示例。Mono NR 模板**无量纲 detector efficiency**，其他背景模板为 `/t/y`；官方 README 使用 `inference_interface.template_to_multihist`。
- 必须审计 exposure 属于哪个 SR、grid Energy/单位、axis ordering、HDF5 key、nuisance 模板节点、不可观测 bin、mask、插值/截断、前向 recoil rate 的单位。源项每次只能乘一次曝光。
- 仍需正式的 nuisance priors/correlations、拟合行为和 published benchmark 验证；仅能读取全部模板时不等于 official-likelihood reproduction。

## 4. 给本地 Codex 的指令

> 在当前隔离运行 `ha-xenonnt-b8-snudd-20261012-01` 中执行下一阶段，不修改正式源项目和原始 SNuDD。首先审计并固定 `P05B_REFERENCE_VALUES.yaml` 对应的文献参数；从已经存在的本地代码和数据中逐文件搜寻 PandaX 2024 US2 和 XENONnT 2024 efficiency 输入，以及 PEANUTS 曝光平均概率和 Xe131 响应，不得因为在 2026 release 中找到相似模板就替代 2024 输入。仅在有论文一致的独立 detector-input 证据后计算 44.9 / 11.15。其次独立执行 `FETCH_XENONNT_2026.ps1`，生成 P06 release 物理语义审计。分别输出 P05-B 和 P06 独立报告，无法取得的数据明确标成 BLOCKED，禁止经验归一化、伪造响应、伪造 nuisance。 

## 5. 来源和版本

- [现象学论文 2409.04703v2](https://arxiv.org/html/2409.04703v2)
- [PandaX 2024 原实验论文](https://arxiv.org/abs/2407.10892)
- [XENONnT 2024 原实验论文](https://arxiv.org/abs/2408.02877)
- [SNuDD README](https://github.com/SNuDD/SNuDD)
- [2026 XENONnT 官方 Zenodo](https://zenodo.org/records/20576156)
- [2026 XENONnT GitHub 公开 release](https://github.com/XENONnT/cevns_data_release/tree/sr0_sr1_sr2)

该资料包不构成任何已完成的论文计算或数据复现。`P05B_REFERENCE_VALUES.yaml` 所有参考数值均为 paper published values；本轮未访问本地 F 盘，也未重新运行旧程序。
