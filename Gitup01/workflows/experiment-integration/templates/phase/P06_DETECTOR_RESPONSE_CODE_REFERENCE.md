# P06 探测器响应：现有代码与可运行例子

配合 [P06 填写模板](P06_DETECTOR_RESPONSE_TEMPLATE.md) 使用。本例展示当前 CsI2021 的 **真实反冲能 → PE 迁移 → PE 效率**。核响应 `ResponseW` 属 P04；这里的 response 是探测器条件概率。CsI2021 的参数和 PE 语义不能作为其他探测器的默认值。

## 1. 职责与调用框架

| 职责 | 当前文件.symbol | 输入 → 输出 | 迁移时的复用判断 |
| --- | --- | --- | --- |
| 真反冲到电子等效能 | [`rates/differential.py`](../../../../src/cevns_pyeft/rates/differential.py) 的 `eee_quenching_csi` | `E_R[keV] → Eee[keVee]` | CsI 专有曲线；新靶一般写适配器或配置数据 |
| PE 迁移核 | 同文件的 `p_smearing_csi` | `PE,E_R[keV] → p(PE|E_R) [PE⁻¹]` | CsI Gamma 模型；须检查是否适用于新探测器 |
| PE 效率 | [`slow_counts_csi2021.py`](../../../../src/cevns_pyeft/experiments/coherent/slow_counts_csi2021.py) 的 `efficiency_csi2021` | `PE → [0,1]` | CsI2021 解析参数；不可复制为通用值 |
| bin 积分位置 | [`rates/counts.py`](../../../../src/cevns_pyeft/rates/counts.py) 的 `bin_events_csi` | 重建谱 × `efficiency(PE)` → `events/bin` | 这里只借用折叠顺序；完整函数还含 CsI/SNS 细节 |

```mermaid
flowchart LR
  T["真实核反冲 E_R [keV]"] --> Q["eee_quenching_csi<br/>Eee [keVee]"]
  Q --> R["p_smearing_csi<br/>p(PE|E_R)"]
  R --> E["efficiency_csi2021(PE)"]
  E --> B["在 PE bin 内积分"]
```

`bin_events_csi` 中先构造 `dN/dPE`，随后在每个 PE bin 的子网格上乘 `efficiency(pe_sub)` 并积分。对全 PE 域归一化的迁移核不应在分析窗口内重新归一化；窗口外迁移按当前配置排除。P06 只定义响应，通量、截面、靶质量和最终计数归 P07。

## 2. 从实现提炼的核心计算

`eee_quenching_csi` 将 `E_R` 先转为 MeV 数值代入 CsI 多项式，再返回 keVee。`p_smearing_csi` 以 `Eee` 构造 Gamma 密度，`PE≤0` 返回零。对 `Eee>0`，当前参数满足：

```text
a = 0.0749 / Eee
b = 9.56 × Eee
shape k = 1+b
rate λ = a(1+b)
p(PE|E_R) = λ^k / Γ(k) × PE^(k-1) × exp(-λ PE), PE>0
```

这只是当前 CsI 模型的核心结构。效率在 **重建 PE** 上评价，`efficiency_csi2021` 使用独立的解析曲线并在零处截断。新实验必须在 P06 模板明确效率究竟作用于真实反冲、平均响应还是重建量。

## 3. 可运行的当前 API 示例

在仓库根目录且已安装项目或设置 `PYTHONPATH=src` 后执行：

```python
import numpy as np

from cevns_pyeft.rates.differential import (
    eee_quenching_csi,
    p_smearing_csi,
)
from cevns_pyeft.experiments.coherent.slow_counts_csi2021 import (
    efficiency_csi2021,
)

recoil_keV = 10.0
pe = np.linspace(0.0, 200.0, 20_001)
pdf = np.asarray(p_smearing_csi(pe, recoil_keV), dtype=float)
acceptance = np.asarray(
    efficiency_csi2021(np.array([0.0, 10.0, 30.0])), dtype=float
)
area_0_200 = float(np.trapezoid(pdf, pe))

assert pdf.shape == pe.shape and np.min(pdf) >= 0.0
assert 0.99 < area_0_200 < 1.01
assert np.all((0.0 <= acceptance) & (acceptance <= 1.0))
print("Eee [keVee] =", eee_quenching_csi(recoil_keV))
print("response area on PE 0..200 =", area_0_200)
print("efficiency at PE 0,10,30 =", acceptance)
```

本次运行：`Eee=0.88200584 keVee`、有限区间 `PE∈[0,200]` 的响应积分约为 `1`，效率为 `[0, 0.24571554, 0.98162539]`。一次网格积分只证明该示例点近似归一化；P06 Gate 仍需覆盖多个反冲点、完整定义域、边界和探测器差异。

## 4. 新实验的最小实现边界

| 新实验资料 | 决策 | 代码动作 |
| --- | --- | --- |
| 响应与当前模型、变量、单位和参数来源完全一致 | 候选 `REUSE/CONFIG_ONLY` | 核对来源后传配置，复用现有 callable |
| 给了新的效率/展宽表，但能表达同样接口 | `ADAPTER` | 实验层实现 `response_density(x,T)` 与 `efficiency(x_or_T)`，保留通用积分责任 |
| 探测器输出不是 PE，或多探测器响应不同 | `ADAPTER` 或 `SHARED_EXTENSION` | 明确每台探测器的重建轴、迁移核与 bin；不得套用 CsI PE |
| 缺淬火、效率作用域或分辨率，且要求重建谱 | `BLOCKED` | 定向索取校准资料；若选理想近似，须单独批准其科学声明 |

代码验收记录 `R(x|T)` 的归一化域、`x` 单位、效率施加位置、阈值语义和窗外迁移。不能把分析阈值自动实现成阶跃效率，也不能用窗口内重新归一化掩盖损失。

