# P05 当前运动学与截面合同

配合 [P05 模板](../../templates/phase/P05_KINEMATICS_CROSS_SECTION_TEMPLATE.md)。

| 可审计锚点 | 实际职责 |
|---|---|
| `cevns_pyeft/theory/kinematics.py::two_body_recoil_max_GeV` | 精确弹性 Tmax |
| `cevns_pyeft/theory/kinematics.py::minimum_neutrino_energy_GeV` | 精确 Emin |
| `cevns_pyeft/contracts/interaction.py::ElasticKinematics` | target 的运动学质量及 MeV/keV 接口 |
| `cevns_pyeft/contracts/interaction.py::DifferentialCrossSection` | 能量坐标、形状、单位、非负总截面 |
| `cevns_pyeft/theory/li2026/adapter.py::Li2026LegacyInteraction.dsigma_dT` | target/state/parameters 到截面结果 |
| `cevns_pyeft/rates/differential.py::differential_cross_section_nn` | 底层 flavor 收缩及 cm²/keV 包装 |

源码：[kinematics](../../../../cevns_pyeft/theory/kinematics.py)、
[interaction contract](../../../../cevns_pyeft/contracts/interaction.py)、
[adapter](../../../../cevns_pyeft/theory/li2026/adapter.py)。

所有量统一为 GeV 时：
Tmax = 2 Eν²/(mA+2Eν)，Emin = (T+sqrt(T²+2mA T))/2。
当前 adapter 要求 target.kinematic_mass_GeV 与响应使用的 A×amu 一致；
支持域精确不代表允许域内所有模型公式相同。
核心截面 cm²/GeV 到 cm²/keV 的 Jacobian 为 10^-6。

理论核心拒绝 Eν≤0、负反冲及非有限输入；合法但超端点返回不支持。
底层 rates 包装可将零能网格节点返回零；当前 DifferentialCrossSection 的正式能量坐标要求正值。
接入时按真实消费者处理这一差别，不能用笼统的“域外全返回零”覆盖非法输入。

## 只读端点示例

从项目根目录运行。核质量只是演示值，不作为某实验的质量来源。

```python
import math
from cevns_pyeft.theory.kinematics import (
    two_body_recoil_max_GeV, minimum_neutrino_energy_GeV,
    is_two_body_recoil_allowed,
)
energy, mass = 0.030, 124.0
endpoint = two_body_recoil_max_GeV(energy, mass)
assert math.isclose(minimum_neutrino_energy_GeV(endpoint, mass), energy, rel_tol=1e-12)
assert is_two_body_recoil_allowed(energy, endpoint, mass)
assert not is_two_body_recoil_allowed(energy, endpoint * 1.01, mass)
print("Tmax [keV]", endpoint * 1e6)
```

Helm 的 mathematica/exact_vector 分支见
[独立 SM 比较实现](../../../../cevns_pyeft/theory/helm/cross_section.py)，须明确选择，
不能叠加到完整核响应或自动扩展到 EFT。
回归依据：[单位合同](../../../../tests/test_li2026_units_contract.py)、
[物理核心边界](../../../../tests/test_physics_core_step1.py)。
