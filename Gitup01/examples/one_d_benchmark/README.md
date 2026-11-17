# 实验路线审计与一维 χ² benchmark

本目录只编排既有物理计算、保存核回放、推断与作图，不被 `cevns_pyeft` 导入，不修改正式输入、原结果或工作流 Gate。所交付的科学范围为 **approximate local-model benchmark**，保留当前输入/论文等价性缺口。

[每个实验的70项逐步计算、Python函数及输入输出](../../docs/experiments/COMPUTATION_ROUTES_20261113.md) · [全部数值结果与区间](../../outputs/one_d_benchmark_20261113_run1/RESULTS.md) · [统计定义](../../outputs/one_d_benchmark_20261113_run1/STATISTICS_CONTRACT.md) · [统一版式论文图](<../../论文图NoteBook/10. OneD_Chi2_Benchmarks/README.md>)

## 做了什么、完成了什么

| 实验/分析方式 | 已完成 | 本次一维路线数 | 尚未完成/限制 |
|---|---|---:|---|
| CsI2017，25 PE箱 | 程序路线核对、冻结SM χ²回算 | 0 | 正式YAML/NPZ被OS拒读，无可用参数核 |
| CsI2021，九箱能量谱 | 保存核回放、弱角、12个矢量NSI坐标 | 13 | 含2个τ对角平坦坐标；本次公开loader未跑通 |
| Ar2020，12箱均误差Gaussian | 保存核回放、弱角、12个NSI坐标 | 13 | 含2个平坦坐标；非对称IRLS为另一方法，PE/keVee冲突仍保留 |
| CsI2021，9×11时间分析 | 核对99箱SM及既有24点NSI前向程序 | 0 | P09原生统计、背景绝对归一和所需不确定度未闭合 |
| CONUS+，`conusplus_kkl_run1` | 弱角、ee/eμ/eτ的uV/dV、论文Table II端点对照 | 7 | 当前核表/通量与作者输入未逐项等价 |
| CsI2021九箱＋Ar均误差 | 弱角及12个NSI坐标，独立nuisance联合 | 13 | 含2个平坦坐标；不重复叠加CsI时间样本或CsI2017 |
| 太阳三单bin，continuous_acceptance | paired、US2、XENONnT及joint各做弱角、两种fB、ee-uV/dV | 20 | 有效两味SNuDD v3.4.1；XENON尾段flat_sensitivity；v3.5完整ρ/trace未在本轮实现 |
| 太阳多bin | 保留并核对独立SM前向路线 | 0 | 未混入三单bin拟合 |

合计66条一维路线：60条有识别度，6条τ对角对无入射τ的SNS源完全平坦，允许集为全实轴。参数定义、先验、边界与未执行能力见统计定义和结果报告。GF、其他振荡参数、复NSI相位及同时多参数profile不在本轮扫描范围。

## 文件与职责

| Python文件 | 输入 → 计算 → 输出 |
|---|---|
| [route_audit.py](route_audit.py) | 实际源码、workflow职责、选定输入路径 → AST文件/符号/行号及哈希核对 → `ROUTE_AUDIT.json`、70行`ROUTE_STEPS.csv` |
| [prediction_routes.py](prediction_routes.py) | 已验证地面核/统计数组、太阳能量分辨核与SNuDD源 → LEFT映射、全通道收缩、逐点传播、Gaussian nuisance profile → 参数点信号与χ² |
| [inference.py](inference.py) | 单参数目标函数及有根据的搜索域 → 连续极小化、独立网格核对、阈值求根 → 所有简并极小值和分离区间 |
| [run_analysis.py](run_analysis.py) | 既有模型 → 装配单实验/联合目标、回归与66条扫描 → 不覆盖的`RESULTS.json`、扫描NPZ、验证与来源清单 |
| [validate_results.py](validate_results.py) | 已完成结果和原始理论API → 解析自由通量、full/pair、新弱角逐能量原始截面及阈值根回代 → 独立验收JSON、文献比较 |
| [publish.py](publish.py) | 上述数值及原统一版式 → 只读绘图/制表 → 七图PDF/SVG/PNG、合集、图注、参考文献、66份逐点CSV和阅读报告 |

P01–P10对应数据身份、靶、源、理论、截面、探测器、Slow、Fast、统计和验证；复用公共模块符合workflow，不要求复制十份实验专用程序。源码存在、数值验证与科学接受分别记录。正式路线和本次冻结核回放也分别标注。

## 可复现命令

从项目根执行，建议使用已核查的科学Python：`F:/Work/.codex_conda_envs/codex-py311/python.exe`。本轮结果目录已经存在；新的数值运行必须换一个目录名，禁止覆盖既有结果。

```powershell
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B examples/one_d_benchmark/run_analysis.py --output outputs/one_d_benchmark_NEW_RUN
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B examples/one_d_benchmark/validate_results.py --output outputs/one_d_benchmark_NEW_RUN
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B examples/one_d_benchmark/publish.py --results outputs/one_d_benchmark_NEW_RUN --figures '论文图NoteBook/OneD_Chi2_NEW_RUN'
```

仅刷新源码路线表时使用 `run_analysis.py --audit-only --output <结果目录>`；它不重算或改写数值扫描。`publish.py --refresh-draft`仅用于同一任务尚未交付的图层修订。PDF另需逐页渲染和视觉核对；新输出须保留各自来源清单和未执行范围。

本次运行的实际数值验证、文件归属/备份、链接和图件检查保存在[结果目录](../../outputs/one_d_benchmark_20261113_run1/README.md)。复用上一套[统一样式](<../../论文图NoteBook/9. SM_uniform_style/STYLE_GUIDE.md>)；统计图的实验配色扩展另见[本图集STYLE.json](<../../论文图NoteBook/10. OneD_Chi2_Benchmarks/STYLE.json>)。

[返回examples](../README.md)
