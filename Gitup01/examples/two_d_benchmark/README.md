# 二维 SM/NSI benchmark 程序

沿用[一维分析的模型和统计](../one_d_benchmark/README.md)，同时改变两个物理参数，profile相同nuisance。当前任务不修改Runtime、data、正式Gate或旧结果。各实验独立保存，Ar均误差与非对称统计、太阳data-only与既有pull控制严格分开。

本轮目标是41个明确平面：33个基础平面包括SNS三组各6个NSI uV/dV味坐标、CONUS+三个、太阳三个样本与joint各一个，以及太阳弱角/通量的4×2个SM平面；另有四组地面分析各两个ee-dV与eμ/eτ-dV混合平面，对应CONUS论文Fig.4下方benchmark。SNS的三个τ对角平面完全平坦，不能给有限限值；单个太阳拟合总数在两个参数下有连续简并最佳点。

| 文件 | 职责 |
|---|---|
| [models.py](models.py) | 核对既有来源哈希，从冻结核构造全二维多项式；太阳NSI逐点传播，SM弱角作用所有味；计算率上界和完整域 |
| [plane_inference.py](plane_inference.py) | 条件化搜索、独立网格与连续极小化、物理边界、阈值等高线和端点精化 |
| [run_analysis.py](run_analysis.py) | 逐实验扫描、共享计算太阳传播、混合耦合holdout、保存面/轮廓/最佳点及来源 |
| [extend_mixed.py](extend_mixed.py) | 补充八个已发表混合味坐标平面；保留基础33平面RESULTS.json，写出41平面BENCHMARK_RESULTS.json索引 |
| [validate_results.py](validate_results.py) | 新点full/pair与独立最小二乘、1D坐标轴切片、轮廓回代、论文换轴/内洞/IoU、隔离SNuDD→Runtime与新最佳点Slow |
| [publish.py](publish.py) | 只读41平面数值，生成逐实验两面板、12张汇总图、全部表格/图注/参考文献与导航 |

二维名义阈值为2.30、4.61、5.99；它们与上一轮一维阈值及最小值分开。未做coverage toys，不把退化/边界情形的阈值称为已认证覆盖率。当前科学范围仍为approximate local-model benchmark。

```powershell
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B examples/two_d_benchmark/run_analysis.py --output outputs/two_d_benchmark_NEW_RUN --grid-size 601
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B examples/two_d_benchmark/extend_mixed.py --output outputs/two_d_benchmark_NEW_RUN
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B examples/two_d_benchmark/validate_results.py --output outputs/two_d_benchmark_NEW_RUN
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B examples/two_d_benchmark/publish.py --results outputs/two_d_benchmark_NEW_RUN --figures '论文图NoteBook/TwoD_Chi2_NEW_RUN'
```

已完成的RESULTS.json禁止覆盖，重算必须用新目录。本轮结果归[二维运行目录](../../outputs/two_d_benchmark_20261113_run1/README.md)，论文图归[二维图集](<../../论文图NoteBook/11. TwoD_Chi2_Benchmarks/README.md>)。

[上一级](../README.md)
