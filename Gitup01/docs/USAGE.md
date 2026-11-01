# 使用与替换

资源根是“包含data/的目录”。源码checkout可使用包旁默认资源，安装wheel后应显式传入。
不会搜索cwd或逐层寻找同名文件。

```python
from cevns_pyeft.experiments.loader import load_experiment, ResourceCatalog
from cevns_pyeft.experiments.runtime import predict_experiment, evaluate_experiment
from cevns_pyeft.contracts import TheoryPoint
resources = ResourceCatalog("/external/project-root")
exp = load_experiment("Ar2020", resources=resources)
p = predict_experiment(exp, parameters=TheoryPoint(), numerics={"n_er":5,"n_enu":12,"n_pe_bin":3})
fit = evaluate_experiment(exp, p)
```

小网格仅演示接口，不证明科学收敛。CsI2017 Slow固定251点，只接受n_enu；Ar2020不消费pe_step，新入口拒绝。
显式TheoryPoint不被实验默认弱混合角覆盖。预测以events/bin保存；CsI2021评价只除一次箱宽成为counts/PE。

## 启停与资源覆盖

```python
from cevns_pyeft.experiments.selection import load_selection
from cevns_pyeft.experiments.runtime import predict_selection
results = predict_selection(load_selection("configs/analysis_selection.example.yaml"), resources="/external/project-root")
```

结果按dataset_id分别返回，不自动合并异轴数组或chi²。禁用项只核对声明，不解析文件/编译/评价。
YAML仅允许文档化的block列表、enabled/backend/numerics，不执行import；未知字段/键/重复别名报错。

单实验可用 `ResourceCatalog(root,{"responses":path})`。多实验共享responses可用裸键；
实验专属覆盖写成 `{("CsI2017","efficiency"):path, ("Ar2020","efficiency"):other}`。
同名资源属于不同实验时裸键拒绝；拼写错误、未知作用域和整份选择中未使用的键均拒绝。
数据集作用域大小写规范化；资源ID大小写敏感。共享覆盖先应用，专属覆盖后应用。

## 替换真实物理输入

```python
from dataclasses import replace
from cevns_pyeft.sources.composable import ScaledSource
changed = load_experiment("Ar2020", resources=resources,
    components={"source":ScaledSource(exp.model.source,2)})
```

三个实验公开source/interaction/observation槽位。COHERENT使用ExperimentModel，
还可替换run与已支持核素范围内的targets。CsI2017/Ar2020保持专用折叠策略，
其旧Fast不支持任意新组件时明确拒绝；默认设定改变仍可重建已有Fast。

相互作用复用InteractionModel.dsigma_dT，响应分别消费真实概率/效率；不复制EFT公式。
组件提供稳定describe、资源及实现记录；实际装配改变会改变外层物理身份，原实验不能评价变化后的结果。
调用方list/dict/ndarray会防御性快照；加载后实际依赖变化会要求重新加载。

源码例子：[单实验/切换](../examples/experiment_modularization/run_experiments.py)、
[synthetic扩展](../examples/experiment_modularization/synthetic_dataset.py)。后者只在显式registry注入，不注册为真实实验。
