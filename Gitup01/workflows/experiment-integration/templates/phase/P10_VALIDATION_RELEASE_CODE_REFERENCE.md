# P10 验证与暴露：现有注册接口和证据检查例子

配合 [P10 填写模板](P10_VALIDATION_RELEASE_TEMPLATE.md) 使用。P10 不另写一套物理计算；它核对 P01–P09 的实际代码、Gate 和外部证据，然后决定哪些 capability 可在 registry 与报告中暴露。

## 1. 当前代码与工作流职责

| 职责 | 现有位置 | 不能据此推断 |
| --- | --- | --- |
| 数据集元数据发现 | [`experiments/specs.py`](../../../../src/cevns_pyeft/experiments/specs.py) 的 `load_experiment_spec` | 有 `experiment.yaml` 不代表 Slow/Fast/statistics 已实现 |
| 已注册源/Slow callable | [`experiments/registry.py`](../../../../src/cevns_pyeft/experiments/registry.py) 的 `get_experiment`、`get_slow_count_function` | callable 存在不代表通过最新回归或官方复现 |
| workflow Gate | [Master Skill](../../skills/cevns-experiment/SKILL.md) 与各阶段报告 | Machine PASS 不能替代 Human Physics Approval |
| 核验来源 | 当前实验的测试、诊断、外部 reference 和物理文档 | 配置里写了 reference 路径不等于文件存在或比较通过 |

```text
P01–P09 contract/decision/evidence
  → 逐层重跑目标实验与共享回归
  → 核对 reference 的来源、参数点、单位和差异
  → Gate 矩阵和可暴露 capability
  → registry 与最终科学声明
```

验证结论要分成四层：**内部数值一致性、旧程序回归、发表 forward model 复现、官方 likelihood 复现**。前一层成立不推出后一层成立；未请求的 P08/P09 在计划里保留 `NOT_REQUESTED`，不能写成 Machine PASS。

## 2. 可运行的只读接口检查

在仓库根目录、已安装项目或设置 `PYTHONPATH=src` 后执行。它只检查当前 CsI2021 的 registry、spec 和一个 reference 路径，**不是 P10 全量验证**。

```python
from pathlib import Path

from cevns_pyeft.experiments.registry import (
    get_experiment_spec,
    get_slow_count_function,
    list_experiments,
)

names = list_experiments()
spec = get_experiment_spec("CsI2021")
slow = get_slow_count_function("CsI2021")
reference = Path("tests/reference_CsI2021/slow_reference.npy")

assert "CsI2021" in names and callable(slow)
print("dataset_id =", spec.data["dataset_id"])
print("slow callable =", slow.__name__)
print("reference exists =", reference.is_file())
```

本次运行显示 `dataset_id=CsI2021`、Slow callable 已注册，而该 `slow_reference.npy` **不在活动目录**。配置所列路径不是已通过的 reference 回归。新实验应逐项核查自己的 reference 路径、版本及比较命令。

## 3. P10 应填的核验矩阵

| 能力 | 需要的实际证据 | 暴露规则 |
| --- | --- | --- |
| Dataset metadata | schema/loader、bin 和数据语义 | 可发现不等于可计算 |
| Source/Target/Theory/Detector | 对应 P02–P06 Machine + Human Gate | 缺任一关键物理定义则限制下游声明 |
| Slow | P07 直接积分、收敛、逐 bin、归一化与 Human Freeze | 只注册已验证的 callable |
| Fast | 每种表示独立的 P08 逐 bin Slow 对照及缓存元数据 | 未请求或阻断时不宣称 Fast |
| Statistics | P09 数据语义、背景、协方差/nuisance、发表基准 | 旧 χ² 不标为官方 likelihood |
| 最终声明 | 内部/旧程序/论文/官方四层分别给参考与差异 | 只有最终 Human Gate 批准后发布对应措辞 |

若修改共享 theory、rates 或 kernel，既有 CsI2017、CsI2021、Ar2020 的相关回归也须复查。Fast 缓存元数据陈旧时应失效或重建；不得修改 reference、放宽容差或改变物理输入来强行通过。

## 4. 复用与新增边界

`list_experiments` 和 `get_experiment_spec` 可复用作**发现**；`get_slow_count_function` 仅对显式注册的 Slow 生效。新实验在 P10 前应完成真正的计算和 Gate，再决定是否添加 registry 项；只加 `experiment.yaml` 不等于完成迁移。最终物理文档路径和科学声明按 P10 模板填写，并保留未实现能力的 `BLOCKED/NOT_IMPLEMENTED` 状态。

