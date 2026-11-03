# experiment_modularization：统一入口与自定义 Catalog 示例

## 两个文件分别做什么

| 文件 | 真实调用和结果 |
|---|---|
| [run_experiments.py](run_experiments.py) | 无 `--selection` 时预测 CsI2021 并评价 χ²，再预测 Ar2020、CsI2017；用 `dataclasses.replace` 将 CsI2021 POT 加倍后再次计算 |
| [synthetic_dataset.py](synthetic_dataset.py) | 自定义源/interaction/observation，创建 `ExperimentDefinition`，注册到 `ExperimentCatalog(builtins=False)`；比较计数和独立解析值 |

从根目录运行：

```powershell
python examples/experiment_modularization/run_experiments.py --resources .
python examples/experiment_modularization/run_experiments.py --resources . --selection configs/analysis_selection.example.yaml
python examples/experiment_modularization/synthetic_dataset.py
```

带 selection 时脚本输出启用实验的计数 JSON，不执行无 selection 分支中的 χ²/POT 示例。synthetic 的三箱计数为 `[4.32, 6.48, 2.16]`（浮点打印可有末位差异），没有真实实验统计意义，且不会进入内置 manifest。

## 为什么用 synthetic

常数谱、常数截面、已知核数和概率允许手算积分，从而检查 custom catalog、组件合同与通用算法之间的连接，不需要猜测真实数据集的新参数。

## 管理与新增文件

扩展统一接口示例可在本目录新增脚本；保持独立入口、明确 `--resources`，在本 README 增加运行命令。新的主题另建 `examples/<主题>/`。演示自定义实验时用私有 Catalog，不改进程全局活动清单。

若新增组件示例，说明装配位置、消费的合同和支持的 backend，并用解析值或已验证的缩放关系检查输出。真实模型实现应放 `cevns_pyeft/`；不能把示例文件中的临时公式作为生产代码的第二个来源。

---

[上一级](../README.md) · [项目总览](../../README.md)
