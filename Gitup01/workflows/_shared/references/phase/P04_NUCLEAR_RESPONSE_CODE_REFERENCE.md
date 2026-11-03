# P04 当前理论与核响应入口

配合 [P04 模板](../../templates/phase/P04_THEORY_RESPONSE_TEMPLATE.md)。
以下为当前源码定位；存在 symbol 不证明外部公式或核响应源表已经核验。

| 实际 owner / 可审计锚点 | 职责与边界 |
|---|---|
| `cevns_pyeft/theory/li2026/operators.py::canonicalize_wilson_coefficients` | 规范化算符/flavor 系数；顺序和单位须按目标核对 |
| `cevns_pyeft/theory/li2026/left_to_ci.py::left_to_ci` | LEFT 到核子系数匹配；核对 LEC 和模型约定 |
| `cevns_pyeft/nuclear/response.py::ResponseDB.get` | 显式核素 key 到响应对象 |
| `cevns_pyeft/nuclear/response.py::ResponseW.W_np` | 响应多项式与指数；表的 np 标签对应物理 (p,n) 顺序 |
| `cevns_pyeft/theory/li2026/amplitude.py::flavor_kernel_onebody_li2026` | 粒子/核响应收缩，保留各通道 |
| `cevns_pyeft/theory/li2026/adapter.py::Li2026LegacyInteraction` | 当前 InteractionModel 适配；真实参数、资源哈希与能力说明 |

源码链接：[matching](../../../../cevns_pyeft/theory/li2026/left_to_ci.py)、
[核响应](../../../../cevns_pyeft/nuclear/response.py)、
[interaction adapter](../../../../cevns_pyeft/theory/li2026/adapter.py)。

## 当前限制

- 核素 key 必须显式映射，如 I127 → I；丰度、实际核数不进入 ResponseW。
- 当前振幅实现令 SigmaPDelta 的粒子响应为零；需要非零贡献的目标须重新判断覆盖。
- full nuclear response 后不额外乘 Helm；SM Helm 是独立模型。
- 当前 adapter 描述粒子处理为 legacy_shared_kernel。
  [反中微子审计](../../../../docs/physics/physics-audits/antineutrino_sign_helicity_audit.md)
  与 [外部核响应源表审计](../../../../docs/physics/nuclear-responses/nuclear_response_convention_audit.md)
  仍有未闭合事项。应按目标限定声明，不能把标签/内部回归写成完整外部验证。

## 只读接口示例

从项目根目录、装有项目依赖的 Python 执行；不需要旧 src 布局。
示例只检查当前响应装载和形状，不生成科学基准。

```python
import numpy as np
from cevns_pyeft.nuclear.response import ResponseDB

db = ResponseDB("data/responses/responses_all.json")
assert db.meta["basis"] == "np"
for isotope, key in {"Cs133": "Cs133", "I127": "I"}.items():
    response = db.get(key)
    matrix = np.asarray(response.W_np("M", 0.0))
    assert matrix.shape == (2, 2)
    print(isotope, key, matrix.shape)
```

相关检查见 [核响应约定测试](../../../../tests/test_nuclear_response_convention.py)
和 [flavor 截面测试](../../../../tests/test_rates_differential_flavor.py)。
新实验还需自己的核素、算符覆盖和独立参考，不能继承此示例的物理输入。
