# tests/helpers：测试输入的共同来源

[regression_cases.py](regression_cases.py) 提供 `points()` 和 `GRIDS`，被 [冻结计数回归](../test_refactor_csi2021_regression.py)等测试导入。`points()` 构造 SM、NP、SM+NP、复数和多味 Wilson 点；`GRIDS` 保存 small/medium/default 的数值网格。

## 为什么不与参考数组混在一起

这里描述“给程序什么输入”，`tests/reference/` 保存“修改前程序得到什么输出”。测试同时读取两者进行比较。如果随意改变已有点的含义，原参考数组就不再对应同一物理输入。

## 管理与新增文件

多个测试共享的新输入构造器可在这里增加 `<主题>_cases.py`，由测试显式导入；局部 fixture 留在使用它的测试文件。构造器应确定性、无隐式读写、无全局状态污染。

新增测试点使用新的明确名称，并说明系数单位、SM 开关、味矩阵和网格；不要重定义旧名称来让回归通过。helper 本身不自动成为 pytest 测试，也不生成冻结参考。检查使用者仍覆盖原有点和网格，避免仅修改输入导致比较对象悄然变化。

---

[上一级](../README.md) · [项目总览](../../README.md)
