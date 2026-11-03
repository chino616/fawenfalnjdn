# tests/workflows：工作流管理规则的结构测试

[test_workflow_structure.py](test_workflow_structure.py) 通过 `importlib` 直接加载 [validate_skill_pack.py](../../workflows/cevns-pyeft/qa/validate_skill_pack.py)，使用 `unittest` 验证 catalog、路由、workflow 引用、phase 映射、循环、链接及保护清单。

测试会构造重复 ID、越界路径、未知路由和缺失配置等反例；还验证机器配置确实从 `tools/workflow_validation/config/` 读取，缺失时不回退到旧 docs 副本。

## 运行与职责边界

从项目根目录运行：

```powershell
python -B -m unittest discover -s tests/workflows -v
```

这些检查不导入物理预测代码，不能证明新实验模型或自然语言协作行为正确。把它们与数值回归分开，可以分别定位流程结构问题与物理实现问题。

## 管理与新增文件

新的结构不变量追加到当前 `TestCase`，独立验证器可建立新的 `test_<主题>.py`。反例用内存深拷贝、mock 或临时目录，不修改正式 catalog/routes/数据。路由场景数据放 `workflows/cevns-pyeft/router/scenarios/`，阶段/交接场景放其 `qa/scenarios/`。

保护文件的合法文档增补需按 [校验配置管理](../../tools/workflow_validation/README.md) 登记；不要删测试或放宽物理文件保护来消除错误。测试报告注明它是结构验证，与用户实际审核和物理结论分开。

---

[上一级](../README.md) · [项目总览](../../README.md)
