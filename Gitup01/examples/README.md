# examples：从公共 API 开始运行

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
