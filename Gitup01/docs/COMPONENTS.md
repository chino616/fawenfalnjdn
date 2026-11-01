# CsI2021 组合式接口

当前实现覆盖组合式一维 Slow/Fast、组件替换、内容缓存及发行验证。保留现有 CsI2021 9 个 PE 箱的物理约定与离散算法；源、运行期、靶核、相互作用与观测由实例组装。三实验能力见 [能力矩阵](CAPABILITY_MATRIX.md)，实际验收见 [验证记录](VALIDATION.md)，Fast 接口见 [Fast 与缓存](FAST_AND_CACHE.md)。

```python
from dataclasses import replace
from cevns_pyeft.contracts import TheoryPoint, IntegrationSettings
from cevns_pyeft.core.predict import predict
from cevns_pyeft.experiments.coherent.csi2021 import make_csi2021_model
from cevns_pyeft.sources.composable import ScaledSource
from cevns_pyeft.detectors.csi2021 import ConstantEfficiency

# 路径由调用方明确提供，可使用项目外绝对路径。
model = make_csi2021_model("data/responses/responses_all.json")
point = TheoryPoint(include_sm=True, sin2thetaW=0.2387)
numerics = IntegrationSettings.legacy_csi2021_v1()
result = predict(model, parameters=point, numerics=numerics)

# 实际材料贡献；源名不是味索引。两个核素之和已包含真实核数和选择。
prompt_cs = result.components[("prompt_numu", "Cs133")]
assert result.counts.shape == (9,)

twice_source = replace(model, source=ScaledSource(model.source, 2))
twice_result = predict(twice_source, parameters=point, numerics=numerics)
zero_efficiency = replace(model, observation=replace(model.observation, efficiency=ConstantEfficiency(0)))
zero_result = predict(zero_efficiency, parameters=point, numerics=numerics)
```

源输出 `DetectorFluence` 的连续谱单位固定为 `cm^-2 MeV^-1`，谱线权重为 `cm^-2`。源对象不包含探测器质量。`POTExposure`、`LiveTimeExposure`、`IntegratedRunReference` 分别对应每 POT 输入、每秒通量和已积分注量，混用会报错。连续谱、每条谱线均在实际能量网格查询本次 `StateParameters` 对应的密度矩阵。

`TargetInventory` 使用真实核数；CsI 默认质量分数为 133/260、127/260，保留 A×amu 质量近似。`Li2026LegacyInteraction` 包装既有 MeV/keV 截面，不改理论公式。`legacy_shared_kernel` 仍表示既有反中微子处理，不能据此宣称一般 antinu 振幅已实现。

`IntegrationSettings.legacy_csi2021_v1` 保留旧流程：反冲谱 → PE 节点求积 → 非负截断 → PE 线性插值 → 效率 → 箱内积分 → 分量选择。`bin_probability_v1` 是独立的概率折叠策略，概率矩阵无量纲，反冲求积权重不混入其中；它不承诺有限网格上等于旧策略。新核心不选择具体实验，不导入实验模块。

旧入口 `slow_counts_csi2021(...)` 的签名和五个返回键保持兼容。旧 `target_flavor_counts_per_bin` 仍指每个核素按整台质量计算、尚未施加材料质量分数及分量接受率的历史 raw；新 `Prediction.components` 是实际最终材料贡献，两者不可互换。

```python
from cevns_pyeft.statistics.adapters import to_statistical_vector
from cevns_pyeft.statistics.datasets import csi2021_dataset
from cevns_pyeft.statistics.likelihoods import chi2_csi2021

vector = to_statistical_vector(result, target_observable=csi2021_dataset().observable)
profile = chi2_csi2021(vector)
```

统计桥从 events/bin 显式转换到旧数据的 counts/PE，只除一次箱宽，拒绝错误轴或边界。既有统计仍是 legacy approximate statistics。

替换组件应实现对应 `contracts/` Protocol，提供 `describe()` 返回版本为 1 的 `ModuleDescriptor`，通过 `dataclasses.replace` 组装；不修改全局 loader。自定义 callable 源的描述由其提供者负责准确声明资源和参数。`model.describe()` 导出实际参数、靶核清单、依赖图及指纹；实际装配与执行描述进入外层身份；Fast仍按其实际表示检查完整物理依赖或兼容绑定。

运行验证（PowerShell，在 Gitup01 中）：

```powershell
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' -m pytest -q tests --basetemp=.pytest-tmp/review-run
& 'F:\Work\.codex_conda_envs\codex-py311\python.exe' tools/verify_wheel.py
```

`--basetemp` 应选择本次运行专用的临时目录，pytest 会管理其中的测试文件。冻结参考由修改前代码生成，保持不变；旧冻结脚本已归档，测试参数等值提取到tests/helpers/regression_cases.py。

组合式 Fast 使用 `compile_fast(model, numerics=...)`；能力检查要求明确的系数表示及固定、参数无关的入射态。`predict(..., backend="fast", compiled=kernel)` 复用同一物理模型；不支持的能力及过时模板明确报错。`backend="auto"` 在没有给出编译核时使用 Slow 并记录原因。旧 Fast API 保留其既有数值约定。本轮只安排模块化、接口、Fast 缓存和发行验证。
