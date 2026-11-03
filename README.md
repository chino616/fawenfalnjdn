# CEvNS-pyEFT：当前运行时与目录架构

分支：`refactor/06-readme-architecture-20261103`；版本日期：2026-11-03。
本版基于已发布的 Refactor-04（`daeaf806`），同步整理后的源码、文档、测试和工作流。
当前活动实验为 **CsI2021、CsI2017、Ar2020**，由实验 manifest 统一管理。

- [项目入口：安装、实际计算链和新增文件位置](Gitup01/README.md)
- [目录划分与管理方式](Gitup01/docs/software/LAYOUT.md)
- [运行时架构](Gitup01/docs/software/runtime-architecture.md)
- [使用方法](Gitup01/docs/user-guide/USAGE.md)与[能力矩阵](Gitup01/docs/user-guide/capability-matrix.md)
- [数据根、资源身份与哈希](Gitup01/data/README.md)
- [本次发布范围、验证结果和外部资源要求](PUBLICATION.md)

`Gitup01/` 是实际 Python 项目根。根目录及前两层目录共 51 份 README，分别说明真实消费者、职责拆分原因、文件管理方式和新增文件的创建、接入、检查步骤。项目内全部 61 份 README 随本版发布。

## 运行前准备

使用 Python 3.11 或以上版本。数据通过 `ResourceCatalog` 显式读取，资源根必须包含 `data/`。
本分支沿用此前发布范围：保留已发布输入和冻结参考；本地新增数值数据、Notebook、图表与计算输出不随源码上传。因此完整统计与资源审计需要另外提供完整资源根，尤其是 CsI2017 的 `observation_schema.json`。

在仓库根执行以下命令；将示例 `D:\CEvNS-resources` 替换成自己的完整资源根：

```powershell
cd Gitup01
python -m pip install -e .
python examples/experiment_modularization/run_experiments.py --resources 'D:\CEvNS-resources'
```

本次用发布副本代码、显式外部资源完成了三个实验的小网格预测和统计评价，结果与完整本地版本一致；发布副本的 docs 链接检查通过，212 项测试可正常收集。完整科学回归、数值收敛和 GitHub CI 不在这些结果的证明范围内，详见[发布记录](PUBLICATION.md)。

`重构/` 保留已有历史设计记录；当前接口与目录以 `Gitup01/` 下的代码和文档为准。
