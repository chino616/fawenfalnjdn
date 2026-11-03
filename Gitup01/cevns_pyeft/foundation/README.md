# foundation：常量、单位与资源定位

这里放多条计算路径共用的底层定义。物理模块从 [constants.py](constants.py) 取得常量；截面接口经 [units.py](units.py) 完成单位换算；资源加载由 [paths.py](paths.py) 和 [resources.py](resources.py) 提供路径规则。

## 实际运行中的规则

`ResourceCatalog.path_for` 调用 `resolve_resource(root, path)`。根目录必须包含 `data/`；没有传根目录时，`resource_root()` 只取源码包旁的位置，不搜索当前工作目录。安装 wheel 后应显式传入外部资源根。

`resources.py::ALIASES` 仅兼容明确列出的旧 COHERENT 表/spec 路径。规范路径与旧路径同时存在且字节不一致会报错；绝对路径覆盖可以指向资源根之外。它不会根据文件名猜测数据用途。

## 为什么独立

同一个 GeV→keV 换算或数据路径兼容规则应被所有消费者一致采用。例如截面由 cm²/GeV 变为 cm²/keV 的单位边界在这里复用，实验专属的曝光、分箱和效率不属于共享常量。

## 管理与新增文件

共享常量或单位换算写入对应文件，并注明单位、约定和来源；新的独立基础功能才另建模块，由消费者显式导入。修改共享常量会影响已有实验，需检查单位测试和三个实验回归。

新增数据首先在实验 definition 中声明 `ResourceRef`；只有确实需要兼容旧地址时才向 `ALIASES` 增加一条有限映射，并同步资源清单的 `legacy_paths`。检查规范/旧路径冲突及显式外部根，见 [test_refactor03_contracts.py](../../tests/test_refactor03_contracts.py)。不要把某次机器的绝对工作路径写成新默认值。

---

[上一级](../README.md) · [项目总览](../../README.md)
