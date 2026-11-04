# nuclear：读取并计算核响应 W

[response.py](response.py) 是核响应表的实际消费者：`ResponseDB(path)` 读取 JSON 的 `nuclei`，`get(name)` 返回 `ResponseW`，`W_np(channel, y)` 按 `exp(exp_factor*y) × poly(y)` 求值。Li2026 的振幅计算调用这些矩阵，与粒子响应 R 收缩。

从项目根目录可检查输入和求值入口：

```python
from cevns_pyeft.nuclear.response import ResponseDB
db = ResponseDB("data/responses/responses_all.json")
print(db.nuclei())
print(db.get("Cs133").W_np("M", 0.0))
```

`W_iso` 从表中的 `(p,n)` 矩阵按固定基变换推导。`ResponseW` 保存核素基本量和响应多项式，不持有探测器质量、通量或曝光。

## 为什么代码与数据分开

本目录拥有“怎样读取和求值”，[data/responses](../../data/responses/README.md) 拥有表的实际数值。多个实验可以共享同一份响应数据，而加载器和缓存能够追踪输入内容变化。

## 管理与新增文件

新读取器或核响应表示可在这里建模块，提供清晰的核素、通道、基底和单位接口，并让 interaction 显式选择它。新增核素或修正响应系数应在有来源依据的响应数据中处理，配合资源哈希、靶核映射及相应测试，不能仅添加一个未被读取的 JSON。

基底/归一化改动需检查 [test_nuclear_response_convention.py](../../tests/test_nuclear_response_convention.py) 和既有事件数回归。内部基变换测试不等于外部源表验证；外部源表的来源与归一化问题仍待核实。

---

[上一级](../README.md) · [项目总览](../../README.md)
