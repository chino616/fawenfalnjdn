# CEvNS-pyEFT：当前骨干版

分支：`refactor/07-gitup01-20261104`；整理日期：2026-11-18。
本分支以远端提交 `be634ff` 为基线，同步 `Gitup01/` 当前可维护骨干，不修改 `main`。

- [项目入口与计算链](Gitup01/README.md)
- [本次精简边界](Gitup01/CURATED_UPLOAD.md)
- [运行时源码](Gitup01/cevns_pyeft/)
- [实验输入与数据](Gitup01/data/)
- [测试与维护工具](Gitup01/tests/)
- [工作流定义、模板与技能](Gitup01/workflows/)
- [本次发布记录](PUBLICATION.md)

`Gitup01/` 是实际 Python 项目根。此次上传保留源码、配置、必要数据、测试、工具、文档源文件、示例、扩展、绘图源码和工作流定义；本地备份、虚拟环境、外部安装、缓存、临时目录、批量运行输出、参考论文 PDF 及生成图表不进入分支。

```powershell
cd Gitup01
python -m pip install -e .
```

部分说明文档会引用本地生成结果或参考资料；这些引用用于记录来源与复现实验，但不表示对应的大体积产物已发布。具体范围和验证结果见[发布记录](PUBLICATION.md)。
