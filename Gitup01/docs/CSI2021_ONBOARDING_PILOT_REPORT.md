# CsI2021 Onboarding 三文件试点审计报告

日期：2026-11-04。任务范围：旧九箱 CsI2021；正式输入包 DRAFT / PARTIAL。

分支 `refactor/07-gitup01-20261104`，起始 HEAD `520e1d0a33913a6793b326ed493f5b66e0004a0a`；初始 `git status --short --branch` 干净。

实际执行目录为已验证的 07 分支 worktree：`261103Gitup1-CONUS-6/.github-publish/gitup01-20261104/Gitup01/`。用户最初给出的同级 Gitup01 目录无有效 Git 身份，未向其写入；本次结果在 07 worktree。

## 1. 三份正式输入的位置

- [experiment.input.yaml](../data/experiments/COHERENT_CsI/CsI2021/experiment.input.yaml)
- [experiment.resources.npz](../data/experiments/COHERENT_CsI/CsI2021/experiment.resources.npz)
- [experiment.physics.md](../data/experiments/COHERENT_CsI/CsI2021/experiment.physics.md)

本报告与生成工具仅为审计/提取辅助，不是正式输入的必要组成部分。现有 experiment.yaml 和 Python definition 作为提取依据继续保留。

## 2. YAML 物理模块和 NPZ 内容

YAML 复用现有 dataset_name/source_type/target_mode 与共同输入证据字段；扩展 package、capabilities、source、target、interaction、detector、observable、prediction、statistics、parameters、models、resources 和 provenance。

计数：17 个模型、105 个显式标量参数、23 个 NPZ 数组。

NPZ：Cs133/I127 实际七类响应系数（两个核素共十四个数组）、SNS 能量/两条连续谱表、两种固定味态、PE 边界、observed/background/uncertainty。Gamma 与效率为解析模型；未加入无消费者的表、协方差或 ROOTTime 资源。

完整 key 为：`nuclear_Cs133_M`、`nuclear_Cs133_SigmaPP`、`nuclear_Cs133_SigmaP`、`nuclear_Cs133_PhiPP`、`nuclear_Cs133_PhiPT`、`nuclear_Cs133_Delta`、`nuclear_Cs133_MPhiPP`，以及对应的七个 `nuclear_I127_*`；另有 `source_energy_MeV`、`source_fluence_e`、`source_fluence_mub`、`state_rho_e`、`state_rho_mu`、`observable_pe_edges`、`statistics_observed`、`statistics_background`、`statistics_uncertainty`。各 key 的 shape/dtype/轴/单位与解释完整列于 Physics MD 第 7 节。

NPZ SHA256：`25043e6f510f0ae643a532c53cec2c4b0dad1f2af7172247add5fdc99adc827a`。

## 3. Physics MD 与机器输入的关系

Physics MD 从同一 YAML 结构及 NPZ 内容渲染每个模型、变量、单位、参数表、来源、数学展开、分箱、全部数组清单与问题清单。精确重新渲染检查阻止任意额外参数、公式或数组说明漂移。YAML 是标量/模型权威，NPZ 是数组权威；辅助脚本只在提取/审核时需要。

## 4. 官方资料、legacy 来源、缺失与冲突

官方实验一手资料：本次没有取得可独立核对的原文/官方数据文件；官方来源条目为空。标量/统计数据来自当前 definition 和共享 legacy 参数；源表由当前 SNS 实现提取；核响应从当前 JSON 逐项无损恢复；计算量标 PROJECT_DERIVED。SOURCE_EXTRACTED 只表示读取到项目源码，不表示官方确认。

| 问题 | 状态 | 能力影响 |
| --- | --- | --- |
| official_experiment_sources | MISSING | 未获得旧九箱实验的官方论文/补充材料版本、数据表及逐参数原值；不能比较官方值与采用值是否舍入或冲突。 |
| eft_primary_conventions | MISSING | 已恢复 22 内部算符 key、单位、味轴、扇区与完整 matching；一手理论文献的逐算符 Lorentz/Lagrangian 定义及重整化尺度未独立核对，阻断官方 EFT 算符物理解读声明。 |
| nuclear_source_audit | MISSING | 聚合 JSON 可读且打包无损，但外部源表、转换流程、所有通道符号/归一化未独立确认；I 的 M_nn(0) 存在已记录残差。 |
| antineutrino_kernel | MISSING | antinu 标签已保存，当前与相同 rho 的 nu 共用截面核。一般 EFT 的反中微子符号/螺旋度尚未逐算符审查。 |
| statistics_semantics | CONFLICT | 旧 spec/README 写统计阻断；当前 definition/runtime 实际提供 legacy Gaussian。observed 称 residual/background-subtracted，而公式又加 BRN+NIN，具体已扣背景组成缺原始证据；两者保留，不把代码可运行等同物理确认。 |
| legacy_status_and_reference | CONFLICT | 旧 spec 标 fast_validated，旧 README 停在 DATASET_VALIDATED，所引 CsI2021 run/reference 路径不存在。当前 tests/reference/interface_refactor_v1 与 interface_kernel_v1 确实存在，属于内部冻结兼容基线。 |
| source_endpoint | MISSING | 旧节点掩码上限与 DAR 积分上限不同；谱被裁剪、线性插值且不重归一化，保留实际行为；不能宣称精确物理 Michel 端点归一化。 |
| detector_validity | MISSING | Gamma/quenching/efficiency 原始校准适用区间、CsI[Na] 掺杂影响、硬件阈值和分量接受率的确切时间选择未登记；仅声明当前代码和实际采样范围。 |
| pilot_runtime | MISSING | 当前 Loader 不读取 experiment.input.yaml/NPZ；未实现或执行只用两个机器文件的独立 Runtime 加载。 |

## 5. 完整性及验收状态

| 验收组 | 实际结论 |
| --- | --- |
| A 物理内容 | 已整理真实调用链、源/靶/理论/探测器/坐标/数值/统计及公式解释；每参数有来源与 DRAFT 状态。官方有效域/语义仍 PARTIAL。 |
| B 数值资源 | 当前九箱链可获得且必需的数值数组已打包，唯一 key、单位/shape/dtype/轴与 SHA256 齐全；无 object、绝对运行路径或外部数值依赖。 |
| C 一致性 | 脚本逐模型/参数/资源核对，MD 精确重渲染，NPZ 安全回读与哈希检查，负向破坏拒绝检查。 |
| D 科学状态 | 官方材料 MISSING，代码恢复与推导已区分；未批准未确认物理，未宣称 standalone Runtime 或官方 likelihood。 |

提取与三文件架构试点已完成；科学完整性为 PARTIAL。旧引擎可运行的近似能力与官方科学确认分开；本包只凭机器文件运行尚未实现/未验证。

## 6. 本次自动检查

三文件一致性：PASS；错误：[]。

| 负向破坏案例 | 正确拒绝 |
| --- | --- |
| scalar/MD drift | True |
| missing model units | True |
| undeclared NPZ key | True |
| declared NPZ key missing | True |
| wrong shape | True |
| wrong dtype | True |
| missing parameter provenance | True |
| false official provenance | True |
| bad archive SHA256 | True |
| extra MD parameter | True |

检查范围是本试点声明结构与当前实现的相符性；没有实现或声称通用模型编译器、科学来源认证、官方数据复现和数值收敛。

## 7. 后续 Runtime 可复用与需扩展的能力

可复用 ExperimentDefinition/ExperimentCatalog、ResourceCatalog 的显式根与指纹、prepare/executor、ExperimentModel、TheoryPoint、POTExposure、TargetInventory、SourceModel/DetectorFluence、InteractionModel、ObservationModel、Prediction、compile_fast 和统计 profiler。

后续需建立：版本化 package schema 与严格字段/单位/坐标验证；受约束 model_id 到经过测试实现的绑定；NPZ 原子/安全读取和哈希/形状验证；ResponseW 从声明数组构造的适配；参数驱动的源/靶/探测器/统计装配；生命周期 owned_files 登记与模型版本兼容；隔离环境仅凭两机器文件的加载测试。不得 eval 模型字符串。

现有 parser 只支持浅层 experiment.yaml，不适合深层 pilot；此次用标准库 JSON 读取 YAML 1.2 JSON 子集，并调用现有 required-field validator，未改生产 Loader 或公共 schema。

## 8. 文件与 README 联动、恢复及授权

| 新增/修改内容 | 说明归属 | 实际运行绑定 |
| --- | --- | --- |
| 三份正式输入 | data/experiments/COHERENT_CsI/CsI2021/README.md | 只由 pilot 工具提取/检查，现有 Loader 未绑定 |
| 本审计报告 | docs/README.md | 任务审计入口 |
| tools/build_csi2021_onboarding_pilot.py | tools/README.md | --write 创建；默认/--check 只读；拒绝覆盖 |

用户在精确 WRITE PLAN 后回复 APPROVE WRITE。修改前 README 保存在 backup 对应原相对路径并由 backup/BACKUP_MANIFEST.md 登记；备份只用于恢复。没有删除原文件、提交或推送。未修改 registry/resource manifest、公共理论、核响应核心、Prediction/Statistics 接口、其他实验或冻结基线。

新三文件尚未进入 dataset registry owned_files，因此当前 datasets export 不会自动把它们纳入既有安装包；这是 Task 01 的未接入边界，需后续正式 Runtime/生命周期任务处理。

## 9. 复核命令

```powershell
python -B tools/build_csi2021_onboarding_pilot.py --check
python -B tools/validate_resource_manifest.py --root . --dataset CsI2021
python -B tools/validate_docs.py --files data/experiments/COHERENT_CsI/CsI2021/README.md data/experiments/COHERENT_CsI/CsI2021/experiment.physics.md docs/README.md docs/CSI2021_ONBOARDING_PILOT_REPORT.md tools/README.md
```

上述命令中的 `python` 必须使用已安装项目依赖的解释器；本次实际使用 `F:/Work/.codex_conda_envs/codex-py311/python.exe`。系统默认 Python 3.12 缺少 SciPy，首次生成在写任何正式文件之前退出；没有安装依赖或修改系统环境。正式包记录 Python 3.11.15、NumPy 2.4.6、SciPy 1.17.1 以及实际公共常数值，便于复核环境差异。

## 10. 实际执行结果

| 检查 | 实际结果和证明范围 |
| --- | --- |
| `build_csi2021_onboarding_pilot.py --check` | PASS；17 模型、105 标量、23 数组；磁盘 YAML 与当前源码重新提取一致，MD 精确重渲染一致，NPZ key/shape/dtype/值/哈希、安全回读一致。 |
| 内存负向一致性检查 | 10/10 正确拒绝，覆盖标量漂移、缺模型变量、NPZ key 双向缺失、shape/dtype 错误、缺 provenance、伪官方来源、错误 SHA256 和额外 MD 参数。 |
| `validate_resource_manifest.py --root . --dataset CsI2021` | PASS，旧运行时已绑定核响应的实际 SHA256 与登记一致；这不意味着新三文件已注册到 Runtime。 |
| `validate_docs.py --files ...` | 5 份受影响 Markdown、48 个本地链接，0 失效；锚点和远程 HTTP 内容不在此检查覆盖范围。 |
| `validate_docs.py --scope docs` | 28 份文档、133 个本地链接，0 失效。 |
| `pytest tests/test_refactor_csi2021_regression.py -k 'small or same_prediction'` | 12 passed、16 deselected；当前小网格 SM/BSM/complex/multiflavor 与冻结 source/isotope/bin 结果及旧统计 χ² 保持一致。不是全量收敛或默认大网格验收。 |
| `pytest tests/test_nuclear_response_convention.py tests/test_interface_contracts.py` | 首次 15 passed、1 setup error：pytest 系统临时目录权限不允许创建/枚举目录，测试体未执行。提升执行环境后同一系统临时目录仍返回 WinError 5；保留失败记录。 |
| 对上述未执行的导入合同测试单独重跑 | 改用项目内新建的 `.pytest-tmp/csi2021-pilot-20261104-import01`，1 passed。首次指定 basetemp 时其父目录尚不存在，返回 WinError 3；创建父目录后通过，未删除任何已有目录。核响应/接口这组共 16 个测试均已实际通过。 |
| NPZ 核响应数值重建 | 两核素 × 七通道 × 四个 y 点（0、0.1、0.5、1），56 次比较，通过；与当前 `ResponseDB.W_np` 最大绝对差为 0。这仅验证打包/多项式约定未漂移，不认证外部源表。 |
| Gamma 密度积分 | 在 1、5、10、30 keVnr 上以现有实现对 PE 正半轴积分，结果分别约为 0.9999999999999729、1.0000000000000102、0.9999999999999992、0.9999999999999951。shape-rate 解释与单位核对通过；不证明官方校准有效域。 |
| 生成器覆盖保护 | 已有全部输出时再次调用 `--write`，正确返回 FileExistsError 并拒绝覆盖；前后四份输出哈希未变。 |
| 只读性和派生说明 | `--check` 前后输出哈希不变；`--render-md` stdout 与磁盘 Physics MD 逐字相同。 |
| 相对资源路径 | 递归检查正式 YAML 的所有字符串，没有 Windows 绝对路径；NPZ 由相邻文件名引用。 |

三组现有 pytest 运行合计实际通过 28 个测试（12 + 15 + 成功补跑 1），同时如实保留临时目录设置失败的记录。未以“收集成功”代替测试执行。

本次小网格为 `n_er=5,n_enu=12,n_pe_bin=3,pe_step=3.0`，通过当前实际 Loader/Runtime 计算得到信号总数 `381.8912488750059 events`，近似 `chi2=10.777108968658267`，`alpha=-0.16573830000469747`、`beta=-0.024404353064389497`。该计算读取现有 Python definition 和原资源；没有把它描述为新机器文件的独立加载测试。

```powershell
$pilotPython = 'F:/Work/.codex_conda_envs/codex-py311/python.exe'
& $pilotPython -B tools/build_csi2021_onboarding_pilot.py --check
& $pilotPython -B -m pytest -q -p no:cacheprovider tests/test_refactor_csi2021_regression.py -k 'small or same_prediction'
& $pilotPython -B -m pytest -q -p no:cacheprovider tests/test_nuclear_response_convention.py tests/test_interface_contracts.py
# 系统临时目录失败项的成功重跑（只选择未存在的基目录，避免 pytest 清理用户目录）
& $pilotPython -B -m pytest -q -p no:cacheprovider tests/test_interface_contracts.py::test_neutral_import_does_not_eagerly_load_experiments_and_engine_still_works --basetemp .pytest-tmp/csi2021-pilot-20261104-import01
```

全量 tests、完整 Fast/Slow 参数域、默认大网格收敛、官方数值复现、官方 likelihood、wheel 和两文件独立 Runtime 加载均未执行，不记录 PASS。

## 11. Task 01 逐项验收

| 任务项 | 状态 | 核对依据或限制 |
| --- | --- | --- |
| A 真实预测/统计执行链 | 已完成 | 当前 07 分支实际 loader、definition、executor、rates 与统计绑定；已调用现有入口。 |
| A 源模型 | 已完成（legacy） | SNS 三分量、Michel/线谱公式、插值/掩码/积分域、POT/几何和时间积分约定全部显式。官方独立确认缺失。 |
| A 靶材和曝光 | 已完成（legacy） | Cs133/I127、化学计量、核数、kg/GeV 质量常数和质量使用位置显式；没有猜造活时间或 kg day。 |
| A 理论和核响应 | 已完成提取，科学审查部分完成 | 22 算符、matching 数学规格、公共 LEC/常数、R/W 收缩、截面和七类核响应；外部源表和反中微子审计未闭合。 |
| A 探测器响应 | 已完成（legacy） | 四次 quenching、shape-rate Gamma、logistic 效率、分量接受率、归一化及边界行为。官方有效域缺失。 |
| A 九箱坐标 | 已完成 | 十条精确 PE edges、bin 顺序、端点与 counts/bin-width 语义。 |
| A 数值积分 | 已完成 | 真实 E/T/PE 网格、运动学节点筛选、梯形积分、先积分再裁剪/插值的次序；未伪称 quad 是当前默认路径。 |
| A 统计定义 | 已完成提取，语义部分完成 | 原 observed/background/sigma、双 pull 公式和一次箱宽转换齐全；官方数据语义/协方差/likelihood 仍缺失。 |
| A 每公式有物理解释 | 已完成 | 17 个 model 的解释、变量/单位、输入/输出、边界、依赖、来源和数学审计表。 |
| A 每参数有来源/状态 | 已完成 | 105 项有采用值、当前代码/资源原值或显式推导、单位、定位和 DRAFT/未人工确认状态。 |
| B 所有可获得且被消费的数组 | 已完成 | 23 数组；没有将未使用核素/通道或其他实验资源打包。 |
| B 稳定 key | 已完成 | NPZ/YAML key 双向一一对应。 |
| B 单位/shape/dtype/轴 | 已完成 | YAML 和 MD 逐项声明，实际回读一致。 |
| B allow_pickle=False | 已完成 | 所有 NPY 成员均为非 object 数组并安全回读。 |
| B SHA256 | 已完成 | NPZ 整体 SHA256 及各数组 C-order 原始字节 SHA256 记录在 YAML。 |
| B 无绝对运行路径或外部隐式数组 | 已完成 | NPZ 相邻相对引用；来源文件相对路径仅为审计定位；必要数值已纳入三文件。通用引擎仍须提供算法实现。 |
| B 无 ROOTTime 混入 | 已完成 | 资源由当前旧九箱实际消费者提取。 |
| C 参数、模型、数组均有说明 | 已完成 | 精确重渲染、逐项元数据与引用检查。 |
| C YAML 资源真实存在且数值一致 | 已完成 | 安全回读、全 key、shape/dtype、数值及哈希检查。 |
| C MD 数值与数组信息一致 | 已完成 | 由 YAML/NPZ 同源渲染且字面一致；额外手写参数被拒绝。 |
| C 缺失/冲突可见 | 已完成 | 九项问题及能力影响在 YAML/MD/报告保留。 |
| D 官方与 legacy 区分 | 已完成 | 官方一手材料列表为空，全部代码恢复明确标记；PROJECT_DERIVED 单独标记。 |
| D 未冒充人工/官方确认 | 已完成 | human_confirmed=false，decision_status=DRAFT。 |
| D 未猜造缺失信息 | 已完成 | 官方原值、完整 covariance、有效域、时间选择保持缺失；无零占位。 |
| D 提取和执行区分 | 已完成 | 三文件结构检查、现有引擎计算、冻结回归各有实际命令与范围；未执行能力明确列出。 |
| D 独立 Runtime 声明 | 未实现/未验证（本任务排除） | 不声称当前程序能只凭两个机器文件运行。 |

## 12. Git、历史治理与恢复边界

新建的三个正式数据文件被当前仓库 `.gitignore` 的 `Gitup01/data/**` 忽略；本次没有改 ignore、stage 或 commit。它们真实存在并通过独立回读，不能仅从 `git status` 的未跟踪列表推断不存在。审计报告和生成工具为未跟踪文件，三个 README 为修改文件。

本次精确授权范围不包含 `tools/workflow_validation/config/PROTECTED_FILES.json`。其中 CsI2021 README 的历史保护哈希仍为修改前值；未修改该保护清单，也未运行/宣称 Skill-pack 保护校验通过。后续若需要全量治理验收，应在维护范围中单独登记该 README 的实际变更；不能为消除误报重算其他科学文件或冻结数组的哈希。

恢复副本正文已核对一致；部分备份的末尾空行和换行编码已规范化，不宣称三个备份全部字节相同。验证用临时目录保留在 `.pytest-tmp/`，不属于输入包。当前普通同级 `261103Gitup1-CONUS-6/Gitup01/` 没有被同步写入；需要读取结果时使用本报告第 1 节对应的 07 worktree 路径。

最终 `git diff --name-only` 仅列三份已授权 README；`git diff --check` 无空白错误。Runtime、核响应 JSON、数据集 registry/resource manifest 和 tests/reference 冻结基线均没有工作区差异。

## 13. 最终正式交付物 SHA256

| 文件 | SHA256 |
| --- | --- |
| experiment.input.yaml | 8c3b9e789a05c0b6bee78a89670aca08c98701a92146bc479119d694cb5f89d4 |
| experiment.resources.npz | 25043e6f510f0ae643a532c53cec2c4b0dad1f2af7172247add5fdc99adc827a |
| experiment.physics.md | 41ced17db401ac0a49a5a8ca7082eff3fe432271276821f52ae0f875f7160533 |
