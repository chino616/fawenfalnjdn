# targets：从材料组成算真实核数

[materials.py](materials.py) 将探测器质量和核素组成转换成 `TargetInventory`，实验装配后交给 `core.predict`。每核反冲产额最终乘这里确定的 `number_of_nuclei`。

| 入口 | 计算规则 |
|---|---|
| `inventory_from_mass_fractions` | 各核素核数 = 总质量 × 该核素质量分数 ÷ 单核质量 |
| `inventory_from_number_fractions` | 用核数分数计算平均单核质量，再分配各核素核数 |
| `csi_target_inventory` | 使用 [recipes.py](recipes.py) 中共享 CsI 配方；Cs133/I127 质量分数为 133/260、127/260 |

质量分数和核数分数不能互换。按当前 CsI 配方两种核素核数相等；CsI2017 的有效计数质量 14.6 kg 与源元数据 14.57 kg 的历史区别仍由该实验 definition 保留。

## 为什么独立

核响应描述单核散射，源描述到达探测器的粒子数；都不应拥有整台探测器的质量。材料库存集中计算核数，才能在计数时只施加一次质量/组成归一化。

## 管理与新增文件

多个实验可复用的材料配方放 `recipes.py`，新的组成转换算法放 `materials.py` 或独立模块；单实验的总质量与运行选择放其 definition。新核素还要有相应核响应/interaction 支持，仅增加配方不保证可以预测。

由实验 `prepare` 调用库存构造器，或在已支持核素范围内用 `components={"targets": ...}` 替换。检查分数非负且和为一、核数单位、总质量缩放和每核产额不变，参考 [test_interface_contracts.py](../../tests/test_interface_contracts.py) 与 [test_component_replacement.py](../../tests/test_component_replacement.py)。

## 化学计量组合的共享归属

`materials.combine_equal_stoichiometry`保存原有Cs:I=1:1的质量加权组合，供多个实验与kernel共同调用。旧CsI2021入口保留同名兼容转发，公共算法不再依赖这个dataset必须安装；数值公式保持原样。

---

[上一级](../README.md) · [项目总览](../../README.md)
