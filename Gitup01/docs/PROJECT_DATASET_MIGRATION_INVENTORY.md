# Active Dataset Migration Inventory

2026-11-04；实际branch refactor/07-gitup01-20261104，HEAD
520e1d0a33913a6793b326ed493f5b66e0004a0a。当前唯一registry/catalog核实的active且installed ID如下；
三个均有Slow/Fast/legacy统计能力，不以README或实验名推断其他数据集。

| Dataset | 组件/迁移前资源 | 三文件目标 | 批次与边界 |
|---|---|---|---|
| CsI2021 | Task05已package-backed；SNS/CsI/Gamma/九PE箱；17模型105标量23数组 | COHERENT_CsI/CsI2021/ | 既有fixture保留；Task06独立通过，科学DRAFT/PARTIAL。 |
| Ar2020 | SNS/Ar40/观测值相关sigma Gaussian；原响应JSON+效率表；12箱；asymmetric IRLS | COHERENT_Ar/Ar2020/ | 首批已完成，v2/7模型80参数20数组；保留原折叠与统计语义。 |
| CsI2017 | SNS/Cs133/I127/确定性PE映射；原响应JSON+效率/统计表；25箱；one-pull Gaussian | COHERENT_CsI/CsI2017/ | 第二批已完成，v2/7模型82参数28数组；保留固定251节点与原精确分箱。 |

未发现其他active manifest ID。CONUS、ROOTTime、time-resolved、9×11 demo、历史与backup不纳入迁移。
没有扫描backup为实验材料；恢复点只用于回滚。各批先从当前实现形成explicit legacy-derived IR，
使用同一compiler生成三文件，再接通现有Runtime并逐项验证。新科学含义、人工决定和RELEASED不自动产生。
三个默认 definition 现均为 package 薄适配；旧表不再作为默认数值来源。
全部三文件、Runtime、外部cwd、安装/export与隔离运行已通过；科学审核继续单列受限。

[进度](ONBOARDING_TASKS_02_10_PROGRESS.md) · [项目迁移报告](PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md)
