# examples：从公共 API 开始运行

[最新结果表生成与验收（2026-11-15）](results_summary/README.md)：SM、16条SM参数、50条NSI一维、41二维、340条χ²、224条能标与128项benchmark汇总为17表Excel/CSV和Markdown；只读回代/变换核对，主版、控制与无灵敏度明确分列。

[截断能标独立统计Part（2026-11-14）](cutoff_scales/README.md)：24条dim-6与176条完整22控制路线分别保存；新增2条逐点太阳传播矢量＋22条固定态三组联合、66＋10行论文数值比较和统一视觉角色图。太阳传播、LNV过渡味和dim-8正定性限制不混用。

[各实验二维SM/NSI benchmark（2026-11-13）](two_d_benchmark/README.md)：41个参数/实验/方法平面、完整域与论文窗口、二维最小值、全部轮廓、原文benchmark和独立Runtime/Slow核对。三条τ对角面平坦；单太阳信号数的连续简并与物理边界明确记录。

[各实验计算路线与一维SM/NSI χ²（2026-11-13）](one_d_benchmark/README.md)：逐步定位70项Python职责，完成66条声明的参数路线、区间和统一论文图；保留CsI-time统计与CsI2017输入缺口，Ar均误差和非对称方法分开。

[2601联合结果复核入口](paper2601_chi2/README.md)：直接比较所有实验组与图4，区分当前Ar非对称、此前平均误差和相关通量敏感性，记录太阳NSI尚未计算的条件。

[2601.19883v2 卡方复算](paper2601_chi2/README.md)：当前输入的SM点、不同统计处理、ee矢量NSI扫描和原图轮廓对照；独立benchmark，不修改生产实验定义。

[CONUS+最新SM/NSI本地运行入口](<CONUS_Plus/conusplus_kkl_run1/README.md>)。本入口仅列当前选定分析；不同方法的输入、代码、结果和审核范围分别说明。

本目录给用户提供可读、可执行的入口。当前示例集中在 [experiment_modularization](experiment_modularization/README.md)，分别演示真实三实验运行和 synthetic 自定义实验。

## 实际运行方式

从项目根目录，用安装了本项目的 Python 执行：

```powershell
python examples/experiment_modularization/run_experiments.py --resources .
python examples/experiment_modularization/synthetic_dataset.py
```

前者通过 `load_experiment/predict_experiment/evaluate_experiment` 运行已有模型；后者用常数源、截面和箱概率构造可独立核算的结果。示例代码消费 runtime，不作为 runtime 的导入依赖。

## 为什么独立

示例展示“用户怎样组合接口”，物理公式仍从包中调用。演示网格可以较小，真实科学分析仍需按任务验证收敛；因此不能把示例输出直接当成论文结果或测试冻结值。

## 管理与新增文件

新示例放 `examples/<主题>/`，入口可命名为 `run_<任务>.py`，相邻 README 写明资源根、依赖、命令、预期输出形状和计算范围。用显式参数接受外部数据，不把作者机器路径写死。

新功能示例应调用已存在或本次实现的公共接口；真实数据仍由 `data/` 提供，运行产物用显式输出目录。验证脚本能从文档声明的位置启动；需要长期保证的行为另放 `tests/`，不要把示例本身当作完整回归套件。

---

[上一级](../README.md)

[COHERENT CsI 示例](COHERENT_CsI/README.md)提供 CsI2021 精简/详细 Physics MD 的可读示例。
示例不参与 Runtime 或材料发现；实际权威输入仍在 data/experiments/COHERENT_CsI/CsI2021。

[CsI2021时间分辨SM计算](COHERENT_CsI/time_resolved_sm/README.md)显式读取已整理的时间分析来源，复用主项目Slow和旧时间权重；输出逐箱数据、积分验收和PNG/SVG图表，不注册新的生产数据集。
