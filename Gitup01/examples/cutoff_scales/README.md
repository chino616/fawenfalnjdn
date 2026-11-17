# 截断能标：独立统计 Part

当前阶段：**已实现、计算并出图（2026-11-14）**。本目录属于 Gitup01 主线的独立分析；没有新的runtime导出或dataset注册，原一维、二维与实验原生统计路线保留各自身份。

[本轮配色、论文逐算符差异与三组联合合同](COMPARISON_JOINT_20261114.md) · [66＋10行论文比较](../../outputs/cutoff_scales/20261114_paper_comparison_run1/README.md) · [24条三组联合结果](../../outputs/cutoff_scales/20261114_three_group_joint_run1/README.md)。新联合包括2条太阳逐点传播的dim-6矢量主路线与22条固定SM太阳态控制路线；6份底层数据各计一次，43个观测、8个独立pull。跨实验相关系统误差未认证，full22和dim-8科学接受边界保持原样。

[实施与物理合同](IMPLEMENTATION_20261114.md) · [dim-6结果：24条](../../outputs/cutoff_scales/20261114_dim6_run1/RESULTS.md) · [full22控制结果：176条](../../outputs/cutoff_scales/20261114_full22_control_run1/RESULTS.md) · [独立图集](<../../论文图NoteBook/12. Cutoff_Scale_Benchmarks/README.md>)

dim-6主版本有22个有限名义下限和2个Ar零响应，太阳逐点更新SNuDD v3.4.1。完整22算符控制版有167个有限名义数值和9个Ar零响应；太阳固定SM传播，LNV采用明确的e↔μ过渡，dim-8正定性检查尚未闭合，其控制柱高不能作为已接受物理排除。

[完整计算与实施方案](PLAN_20261114.md) · [实际输入审计](../../outputs/cutoff_scales/20261114_preflight_run1/README.md) · [原主线状态快照](../../docs/experiments/MAINLINE_STATUS_20261114.md)

## 文件与运行

| 文件 | 职责 |
|---|---|
| [PLAN_20261114.md](PLAN_20261114.md) | LEFT 系数/能标定义、完整允许集、味结构、实验范围、能力缺口、隔离目录、柱状图和验收方案 |
| [inspect_sources.py](inspect_sources.py) | 显式只读回读已有主线输入，记录实际数组/单位/哈希、原生文件可读性、22算符×10路线能力表和受保护源码基线；不扫描或修复正式数据 |
| [common.py](common.py)、[inference.py](inference.py) | Part/schema、有限JSON、新运行保护；Gaussian profile、有符号推断、解析根、完整c/Λ区间及严格SM分支 |
| [model_adapters.py](model_adapters.py)、[run_analysis.py](run_analysis.py) | 显式采用旧核和统计输入，24条dim-6路线，太阳逐点传播与独立统计/核检查 |
| [forward22.py](forward22.py)、[build_forward_models.py](build_forward_models.py) | 从可读资源重建分析模型，新22算符核、基线/加密积分与原四算符投影检查 |
| [validate_forward.py](validate_forward.py) | 原生Slow和Xe逐算符原生振幅检查；保留PSD拒绝点 |
| [record_inputs.py](record_inputs.py) | 按实际读取的模型和资源生成/核对具体输入及哈希交接记录 |
| [run_full22.py](run_full22.py) | 完整176条控制路线、90/95%、分支及两网格能标变化 |
| [report_results.py](report_results.py)、[publish.py](publish.py) | 只读生成可读表、旧epsilon轴交叉检查、文献范围与180mm/STIX图件 |
| [run_joint.py](run_joint.py) | 同一物理c处求和绝对profile χ²、联合最小值、共同搜索域、八pull独立验收；2条主路线与22条控制路线 |
| [compare_paper.py](compare_paper.py) | 读取Fig.3图形参考，输出逐算符比值/差异、可比性标志及联合相对最强单组表 |
| [publish_comparison.py](publish_comparison.py) | 直接调用9. SM_uniform_style；旧两套各5张重画、新增9张论文对比/联合图；不改数值 |
| [verify_delivery.py](verify_delivery.py) | 用带PDF依赖的Python渲染三套合集、核对数值表/样式/来源与旧文件保护 |

在本项目根目录，使用装有 NumPy 的项目科学 Python：

```powershell
python -B examples/cutoff_scales/inspect_sources.py --output outputs/cutoff_scales/NEW_PREFLIGHT_RUN
```

`--output` 必须是本 Gitup01 的 `outputs/cutoff_scales/` 下尚不存在的运行目录；拒绝覆盖和写入其他分析目录。新回读生成 `SOURCE_AUDIT.json`、`CAPABILITIES.csv`、`README.md`。输出仅描述可用性，不能作为限值表引用。当前完成的方案验收另见已存回读目录。

## 内容边界

本Part不被 `cevns_pyeft` 导入，也不导入另一套checkout的engine或cutoff模块。计算复用本主线理论与统计API，新核、新扫描、新图件分层保存。正式输入、dataset registry、onboarding Gate和已有SM/NSI结果的语义保持原样。

只有完成独立验证后，才考虑将稳定的通用能标/区间转换函数并入 `cevns_pyeft/statistics/`；实验装配、参考图几何和绘图继续留在分析层。原方案的能力表是实施前快照；当前已实现范围及尚未闭合的物理条件以本入口和实施合同为准。

## 计算与绘图命令

使用装有NumPy/SciPy/Matplotlib/Numba的项目科学Python。已存运行拒绝覆盖，NEW需换成新名字：

```powershell
python -B examples/cutoff_scales/run_analysis.py --output outputs/cutoff_scales/NEW_DIM6
python -B examples/cutoff_scales/report_results.py --results outputs/cutoff_scales/NEW_DIM6
python -B examples/cutoff_scales/publish.py --results outputs/cutoff_scales/NEW_DIM6 --output '论文图NoteBook/12. Cutoff_Scale_Benchmarks/NEW_DIM6'
python -B examples/cutoff_scales/run_full22.py --forward outputs/cutoff_scales/20261114_full22_forward_run1 --output outputs/cutoff_scales/NEW_CONTROL
python -B examples/cutoff_scales/report_results.py --results outputs/cutoff_scales/NEW_CONTROL
python -B examples/cutoff_scales/publish.py --results outputs/cutoff_scales/NEW_CONTROL --output '论文图NoteBook/12. Cutoff_Scale_Benchmarks/NEW_CONTROL'
python -B -m pytest -q tests/test_cutoff_scales.py -p no:cacheprovider
```

新建前向可运行`build_forward_models.py --output outputs/cutoff_scales/NEW_FORWARD`，随后`validate_forward.py --output outputs/cutoff_scales/NEW_FORWARD`和`record_inputs.py --forward outputs/cutoff_scales/NEW_FORWARD`。输入交接格式见[本轮具体输入](../../outputs/cutoff_scales/20261114_full22_forward_run1/INPUTS_AND_IDENTITIES.json)，`record_inputs.py --check`只读核对，不能复制旧哈希冒充新来源。`--resume --solar-only/--ground-only`只恢复本Part自己的模型构建目录。

15项[解析算法测试](../../tests/test_cutoff_scales.py)通过。原生Slow有11个通过点与1个保留的CONUS dim-8 PSD拒绝点，另有44个Xe原生味振幅检查；详见[前向验证](../../outputs/cutoff_scales/20261114_full22_forward_run1/README.md)。一般LEFT太阳自洽传播、CsI-time P09、CsI2017参数前向和作者等价性仍未闭合。

## 本轮联合与新配色重跑

```powershell
python -B examples/cutoff_scales/run_joint.py --output outputs/cutoff_scales/NEW_JOINT
python -B examples/cutoff_scales/compare_paper.py --joint outputs/cutoff_scales/NEW_JOINT --output outputs/cutoff_scales/NEW_COMPARISON
python -B examples/cutoff_scales/publish_comparison.py --comparison outputs/cutoff_scales/NEW_COMPARISON --output '论文图NoteBook/12. Cutoff_Scale_Benchmarks/NEW_COMPARISON'
python -B examples/cutoff_scales/publish_comparison.py --replot dim6 --output '论文图NoteBook/12. Cutoff_Scale_Benchmarks/NEW_DIM6_STYLE'
python -B examples/cutoff_scales/publish_comparison.py --replot full22 --output '论文图NoteBook/12. Cutoff_Scale_Benchmarks/NEW_FULL22_STYLE'
python -B -m pytest -q tests/test_cutoff_scales.py tests/test_cutoff_joint.py -p no:cacheprovider
```

新publisher以`--replot`显式读取当前已冻结的两套旧数值；新计算结果需经其`--comparison`流程发布。没有隐式挑选最新目录。17项算法测试与168个实际联合八pull验收点均已通过；19张新图和3套合集及来源/旧文件哈希验收见[本轮交付记录](../../outputs/cutoff_scales/20261114_comparison_joint_baseline/README.md)。

[返回 examples](../README.md) · [统计公共模块](../../cevns_pyeft/statistics/README.md)
