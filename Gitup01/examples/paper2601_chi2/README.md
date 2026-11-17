# 2601.19883v2 卡方复算

[最新Fig.4并排重绘与局部放大（2026-11-12）](../../outputs/paper2601_fig4_redraw_20261112/README.md)：论文原始区域与修正计算分开显示，区分Ar非对称/均误差及旧最小值；太阳仅画论文参考。

**最新联合复核：[各组联合结果与论文偏差](../../outputs/paper2601_joint_audit_20261111/README.md)。已修复原二维搜索漏掉远处极小值的缺陷；Ar非对称、原先均误差和共享通量敏感性分别保存。太阳NSI联合带此前未计算，不能由SM卡方范围代替。**

[Fast专项审计](../../outputs/paper2601_fast_audit_20261111/README.md)逐层对照原生Slow、原生Fast、能量插值和扫描多项式，包含新极小值的大耦合点；独立于最小值搜索修复。

使用当前本地输入计算论文 Eqs.(86)、(88)、(90) 的 SM 点、ee 矢量 NSI 的一维 Δχ² 和二维 90% 区域。**这是一组独立 benchmark，不注册新 dataset，也不修改已有物理输入或生产统计。**

[修复后同均误差模型的数值与图](../../outputs/paper2601_chi2_corrected_20261111/README.md) · [旧结果（联合极小值已失效）](../../outputs/paper2601_chi2_20261111/README.md) · [最新五条实验](../../docs/experiments/LATEST_EXPERIMENTS.md) · [上级](../README.md)

| 文件 | 责任 |
|---|---|
| [plot_fig4_comparison.py](plot_fig4_comparison.py) | 只读已有801×801表面与论文矢量轮廓，输出并排Fig.4和局部差异PNG/SVG；校验轴、最小值、置信阈值与截面交点，不重算物理或拟合。 |
| [audit_fast_predictions.py](audit_fast_predictions.py) | 相同网格下原生Slow/原生四算符Fast、能量插值/full-pair/逐源核素重建、最终网格保存核和扫描多项式、缓存失效与大耦合抵消点审计。 |
| [audit_joint_analysis.py](audit_joint_analysis.py) | 核对所有联合结果：21箱同时四pull最小二乘、当前Ar非对称有界profile、相关通量敏感性、原图截面边界、太阳三pull与缺失味态；输出独立目录，不覆盖旧数值。 |
| [run_benchmark.py](run_benchmark.py) | 复用公共 Runtime、4算符核和 Gaussian profile；保存独立积分细化、原生 Slow 对照、SM 卡方、NSI 扫描、方法差异、输入/代码哈希及中文报告。拒绝覆盖已有计算结果。 |
| [extract_paper_reference.py](extract_paper_reference.py) | 只读 PDF p22/23 的矢量图形，按实际刻度校准图3条高和图4轮廓；需要 pdfplumber，不把图形坐标当作者原始卡方网格。 |

## 运行

只重画Fig.4时运行：

```powershell
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B 'F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/paper2601_chi2/plot_fig4_comparison.py' --output '<新图目录>'
```

脚本自动保存绘图计划，列出源文件与哈希；`--refresh-render`只更新该目录中已知图形/图形元数据文件，用于版式校验，不修改数值输入。

最新联合复核直接读取前一轮已通过forward核验的模板和来源；统计、极小值、截面和图重新计算：

```powershell
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B 'F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/paper2601_chi2/audit_joint_analysis.py' --output '<新联合复核输出目录>'
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B 'F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/paper2601_chi2/audit_fast_predictions.py' --output '<新Fast审计输出目录>'
```

下面两步保留原先的均误差对照复算，并非将该近似提升为论文联合结果：

从任意工作目录执行绝对脚本路径；资源根由脚本位置确定。统计计算需要 numpy/scipy/matplotlib；PDF 提取需要 pdfplumber/numpy。两步使用同一个新输出目录，先提取到其 `paper_reference` 子目录，再计算：

```powershell
& 'C:/Users/Ultimator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/paper2601_chi2/extract_paper_reference.py' --output '<新输出目录>/paper_reference'
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B 'F:/Work/2026-07-15 CEvNSpyEFT-Local/261103Gitup1-CONUS-6/Gitup01/examples/paper2601_chi2/run_benchmark.py' --output '<新输出目录>'
```

默认读取已明确采用的最新 CONUS 19箱 quadratic templates、太阳单bin SM、CsI2017 SM，以及活动 CsI2021/Ar2020 YAML+NPZ。CsI2021/Ar 的二维模板在本次输出内重新计算；不覆盖旧缓存。CONUS 模板另与最新本地重建核对。

## 方法边界

- 论文 CsI 是一维 CsI2021 Gaussian、两个 pull .125/.35；CsI2017 .28 单 pull 和99箱时间分析单独列出，不能替代它。
- Ar 主对照固定采用原上下误差均值和论文 .12/.146 pull；保留旧非对称 IRLS、有界优化的不同结果。效率坐标单位冲突保留记录。
- 太阳主对照按论文百分比计算误差；当前取整误差另列。XENONnT 缺接受度尾段，三样本联合主结果是界，不是完整点值。
- solar ee NSI 所需的振荡平均味态数值输入当前未提供；不沿用仅对 SM 适用的 flavor-universal 代表态。
- 图3只转换已验证的 C61u/d，区分 Wilson 系数正负号分支；其余算符保留未执行原因。
- 旧 CONUS `diag_ud` 模板的轴为 `(d,u)`，本例从来源代码读取该声明后，将六行系数改排为 `(u,d)`，对应2601图4；另用已核对的1σ端点检查轴身份，保留原始数组不变。
- Δχ² 阈值遵循论文约定；不据此宣称已校准频率覆盖率或复现官方 likelihood。

二维优化器已修复：由总事件二次型条件化坐标，按pull与残差界构造覆盖所有可优于SM点的有限域，再进行多种子与确定性多起点核验。原先“扩大原坐标box后两次找到同一局部值即停止”的做法会漏掉约(10.4,-9.3)的联合极小值，已经移除。[数值回归](../../tests/test_paper2601_joint_minimum.py)有独立已知零卡方的远分支模型。

`--reuse-forward <此前输出目录>` 只在该运行保留实际执行源码、文件哈希及已通过收敛的 forward 时可用。程序逐项核对活动输入/Runtime、实验身份及 forward 函数 AST，再复制原 forward；受影响的统计与扫描全部重算。本次修正CONUS轴时的复用证据保存在结果目录的 `REUSED_FORWARD.json`。
