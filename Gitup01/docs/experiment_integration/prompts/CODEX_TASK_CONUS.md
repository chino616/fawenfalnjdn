# Codex 任务：按实验规格接入 CONUS

你需要在 CEvNS-pyEFT 仓库中接入 CONUS 实验。

## 必读文件

按顺序读取：

```text
skills/integrate-cevns-experiment/SKILL.md
experiment_specs/conus_plus_2025_publication.md
experiment_specs/conus_plus_2025_reproduction.md
experiment_specs/conus_legacy_mathematica.md
```

## 执行模式

先实现两个可执行模式：

```text
conus_legacy_mathematica
conus_plus_2025_reproduction
```

前者验证 Mathematica 迁移，后者验证天然 Ge、多 detector 和 Daya Bay Eq. (8) 通量链。

随后检查：

```bash
python scripts/validate_package.py
```

若 publication 核心输入仍有 `REQUIRES_INPUT` 或空数据单元：

- 可以创建 publication 模式的 dataclass、数据加载器和测试骨架；
- publication 构造器必须抛出清晰异常；
- 不得猜测缺失数据；
- 不得用 legacy 参数静默替代。

## 物理依赖方向

```text
existing theory dσ/dT
→ reactor flux integration
→ isotope-resolved recoil spectra
→ Lindhard mapping
→ Gaussian detector response
→ reconstructed-energy efficiency
→ bin integration
```

实验模块不得复制 LEFT matching、核响应、振幅或截面。

## 必须保留的输出轴

Legacy：

```text
isotope × production_component × bin
```

Publication：

```text
detector × isotope × production_component × bin
```

## 应创建的主要文件

```text
src/cevns_pyeft/experiments/fluxes/reactor.py
src/cevns_pyeft/experiments/targets/germanium.py
src/cevns_pyeft/experiments/detector/ge_ionization.py
src/cevns_pyeft/experiments/detector/ge_resolution.py
src/cevns_pyeft/experiments/detector/efficiency.py
src/cevns_pyeft/experiments/datasets/conus_legacy_mathematica.py
src/cevns_pyeft/experiments/datasets/conus_plus_2025.py
src/cevns_pyeft/experiments/datasets/slow_counts_conus_legacy.py
src/cevns_pyeft/experiments/datasets/slow_counts_conus_plus_2025.py
```

若项目已有等价公共组件，应复用，不能再建第二套。

## 测试顺序

1. 通量形状、单位与归一化；
2. Ge 靶核核数；
3. Lindhard 映射；
4. Gaussian 核全域归一化；
5. efficiency 作用域；
6. bin edges；
7. 分量求和；
8. legacy Mathematica reference；
9. publication 输入完整性；
10. slow-vs-fast。

## 禁止

- 不得把 `Ge73_only` 用于 publication 默认；
- 不得把 legacy `k=0.162` 用于 publication 默认；
- 不得把阶跃 efficiency 称为 CONUS+ 官方效率；
- 不得同时用固定总通量和热功率几何归一化；
- 不得伪造逐 bin 数据、背景或 covariance；
- 不得通过经验 normalization 强制总事例数等于 347。
