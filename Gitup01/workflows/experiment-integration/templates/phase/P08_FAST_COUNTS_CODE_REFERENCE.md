# P08 Fast 表示：现有 kernel 代码与重建例子

配合 [P08 填写模板](P08_FAST_COUNTS_TEMPLATE.md) 使用。P08 必须以已通过 P07 Machine Gate、且获 Human Slow Freeze 的结果为权威对照。这里的轻量张量示例仅验证**代数接口**；不能证明物理 Fast kernel 已构建或与 Slow 一致。

## 1. 当前 CsI2021 Fast 框架

| 层 | 文件.symbol | 职责与限制 |
| --- | --- | --- |
| 基底 | [`kernels/basis.py`](../../../../src/cevns_pyeft/kernels/basis.py) | 定义当前 Li2026 LEFT 系数基底及顺序 |
| 实验构建入口 | [`fast_kernel_csi2021.py`](../../../../src/cevns_pyeft/experiments/coherent/fast_kernel_csi2021.py) 的 `build_fast_kernel_csi2021` | 向公共 builder 传 CsI2021、SNS、PE bin、Cs/I 和接受率；这些是实验专有值 |
| 公共构建器 | [`kernels/builder.py`](../../../../src/cevns_pyeft/kernels/builder.py) 的 `build_matrixized_kernel` | 构造按目标、源、通道、基底和 bin 分轴的 kernel |
| 重建 | [`kernels/reconstruction.py`](../../../../src/cevns_pyeft/kernels/reconstruction.py) 的 `coefficient_bilinear`、`reconstruct_from_full_kernel_flavor` | 由系数与源密度矩阵形成双线性，再与 kernel 收缩 |
| 缓存检验 | [`kernels/storage.py`](../../../../src/cevns_pyeft/kernels/storage.py) 的 `validate_fastscan_template` | 核对 flavor 版本、轴、basis、dataset、bin 和元数据；旧缓存不应静默加载 |

```text
P07 已批准 Slow
  → 选定 Fast 数学类型及有效域
  → 构建 K[target,source,channel,basis_i,basis_j,bin]
  → B_ij(source)=Tr[rho_source C_i† C_j]
  → counts[target,source,channel,bin]=Σ_ij K_ij × B_ij
  → 逐 bin、逐源、多个参数点与 Slow 比较
```

当前重建器同时支持 5D `(F,H,B,B,M)` 和 6D `(T,F,H,B,B,M)` full kernel。`B` 是系数基底，`F` 源分量，`H` 核/相互作用通道，`M` 分箱。flavor 系数张量为 `(B,3,3)`，源密度矩阵为 `(F,3,3)`。这些轴必须保留，不能只缓存总事例数。

## 2. 可运行的重建代数示例

在仓库根目录、已安装项目或设置 `PYTHONPATH=src` 后执行。**这个 kernel 是人为构造的两箱张量，不含任何 CEvNS 物理**，只用于检查接口与轴。

```python
import numpy as np

from cevns_pyeft.kernels.reconstruction import (
    reconstruct_from_full_kernel_flavor,
)
from cevns_pyeft.sources.state import pure_flavor_density

# F=1 source, H=1 channel, B=1 basis element, M=2 bins
kernel = np.zeros((1, 1, 1, 1, 2), dtype=float)
kernel[0, 0, 0, 0] = [2.0, 3.0]
coefficients = np.eye(3, dtype=complex)[None, :, :]  # (B,3,3)
source_rhos = pure_flavor_density("mu")[None, :, :]   # (F,3,3)

reconstructed = reconstruct_from_full_kernel_flavor(
    kernel, coefficients, source_rhos
)
assert reconstructed.shape == (1, 1, 2)
assert np.allclose(reconstructed.ravel(), [2.0, 3.0])
print("shape =", reconstructed.shape)
print("toy bins =", reconstructed.ravel())
```

本次运行得到 `shape=(1,1,2)` 与 `[2+0j,3+0j]`。这不满足 P08 Gate；真实 Fast 还必须由与 P07 相同的物理输入构建，包含完整 basis 和来源元数据。

## 3. 新实验的复用条件

| 部件 | 可能判断 | 必须先核查 |
| --- | --- | --- |
| `coefficient_bilinear` 与 flavor 重建代数 | 候选 `REUSE` | 基底、Wilson flavor 轴、`rho` 形状和 hermiticity 一致 |
| CsI2021 builder 入口 | 通常 `ADAPTER` | SNS 源分量、Cs/I 靶、PE、接受率均是硬编码/传入的专有配置 |
| `build_matrixized_kernel` | `REUSE/SHARED_EXTENSION/BLOCKED` | 当前 builder 的 dataset/source/target/轴限制能否表达新实验 |
| 已保存缓存 | 仅在元数据完全匹配时 `REUSE` | `flavor_schema_version`、基底顺序、source、detector、曝光、bin 与代码版本 |
| 能量依赖 `rho(Eν)`、未审计的反中微子相互作用 | `BLOCKED` 或扩展 | 固定 `(F,3,3)` 密度矩阵不能代表一般的 `rho(Eν)`；`mub` 标签映射也不替代反中微子物理审计 |

构建成本与评价成本分别记录；每个 Fast 类型单独设置缓存失效规则和 Gate。不能修改 Slow 来迎合 Fast，也不能用全局重标定或总计一致替代逐箱检验。

