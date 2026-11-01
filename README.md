# CEvNS-pyEFT · CONUS 归档后快照

分支：`refactor/04-conus-archive-20261102`；发布日期：2026-11-02。基于 Refactor-03：`c578dae`。

当前运行时保留 **CsI2021、CsI2017、Ar2020** 三个实验。
CONUS 专属源码、数据、工具、测试和相关接入已经从当前版本移除。
共享 EFT 理论、核响应、积分器和公共合同保持原实现。

- [安装与项目入口](Gitup01/README.md)
- [使用与组件替换](Gitup01/docs/USAGE.md)
- [实际能力](Gitup01/docs/CAPABILITY_MATRIX.md)
- [验证记录与发布边界](Gitup01/docs/VALIDATION.md)
- [资源路径与哈希清单](Gitup01/data/resource_manifest.json)

本地完整测试 **173 passed**；三个实验的计数和 χ² 与 CONUS 归档前一致。
本分支依照既有发布规则上传源码、测试、配置和文档，保留继承的非 CONUS 资产。
完整运行需自行提供与资源清单匹配的外置 data 根。
本地 CONUS-Backup、缓存、计算输出、旧构建产物和新实验数值文件不包含在本次发布中。
混合历史文档和冻结参考记录原有来源，不能当作当前仍支持 CONUS 的声明。
