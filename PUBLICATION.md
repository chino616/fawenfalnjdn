# Refactor-06 发布记录

日期：2026-11-03。分支：`refactor/06-readme-architecture-20261103`。
基底：已发布 Refactor-04，提交 `daeaf80657ea91672ebed1b53c31e205926c8943`。
本次把整理后的当前版本直接同步到独立分支，不修改 `main`。

## 发布内容及管理边界

用户确认沿用此前发布范围，并上传本次所有 README。`Gitup01/` 共选入 376 个文件：当前源码、配置、格式契约、文档、示例、测试、维护工具、工作流，以及此前已发布且当前仍保留的输入和参考资产。

- 61 份项目内 README 全部纳入，其中 51 份覆盖项目根和第一、第二层目录。
- 106 个运行时 Python 文件与当前本地版本逐字节一致。发布操作没有另行修改物理算法、数值容差或冻结参考。
- 实验注册以 `cevns_pyeft/experiments/manifest.py` 为准，活动实验为 CsI2021、CsI2017、Ar2020。文档采用整理后的 `user-guide/`、`software/`、`physics/`、`experiments/COHERENT/` 结构。
- 六份已发布 COHERENT 效率/观测表迁移至实验族和数据集目录，字节与原 Git 提交一致。五份已发布 spec/provenance YAML 按代码中的有限 `ALIASES` 迁移，正文相同，仅规范路径与换行格式变化。
- 共享核响应表、已有谱表、冻结 NPZ 参考和 COHERENT 审查表按既有发布范围保留。新路径中的这些数值资产均可对应此前已发布内容。
- 两个论文图生成器 `.py` 作为源码纳入。它们当前仍有旧源码定位约定，具体限制见[绘图目录说明](Gitup01/论文图NoteBook/README.md)。
- `outputs/` 仅发布目录 README，不上传计算结果、缓存或日志。论文图目录也只发布说明及上述生成器源码，不上传 Notebook、图表、PDF 或生成数组。
- 本地备份、构建产物、临时文件和发布操作控制记录不上传。仓库根已有 `重构/` 历史文档保持原状。

目录 README 描述完整本地工作目录的职责与管理方式，其中对未发布的 Notebook、图表和历史输出的引用，只有在提供对应本地资产后才可访问。不能由 README 的存在推断这些资产已包含在 GitHub 分支中。

## 运行与检查需要的外部资源

按照既有范围，下列本地文件未上传：

| 文件 | 影响 |
|---|---|
| `Gitup01/data/experiments/COHERENT_CsI/CsI2017/statistics/observation_schema.json` | CsI2017 统计评价需要其中的原始数字化坐标映射；完整资源审计也会检查该文件 |
| `Gitup01/cevns_pyeft/2026-10-22 Test.ipynb` | 不参与正常包导入，但完整本地工作区的保护清单包含该 Notebook |

运行时传入 `ResourceCatalog(完整资源根)`，或给示例脚本传 `--resources`。完整资源根必须包含 `data/` 及资源清单要求的文件，详见[资源管理](Gitup01/docs/software/resource-management.md)。不能用空文件或临时编造的坐标表替代缺失统计合同。

工作流保护清单保留完整本地项目的真实哈希，没有为了让发布副本通过而删减条目。因此直接在本分支运行 `validate_skill_pack.py` 会报告上述两项 missing；两个涉及完整保护清单的 workflow 测试也依赖这些本地资产。补齐匹配哈希的文件后才能进行完整工作区验证。

## 本次实际验证

所有结果来自本地执行；未声称已运行 GitHub CI 或重新完成全量科学回归。

| 检查 | 结果与范围 |
|---|---|
| 发布复制核对 | 376 个选入文件与源文件 SHA256 一致；106 个运行时 `.py` 完整纳入；准备前后 542 个已扫描源文件哈希未变 |
| 文档检查 | 发布副本 `python -B tools/validate_docs.py --scope docs` 通过，27 份文档、124 个本地链接 |
| 测试收集 | 发布副本 `python -B -m pytest --collect-only -q -p no:cacheprovider`，212 tests collected；这不是 212 项测试执行通过 |
| 工作流结构 | 17 Skills、8 workflows、14 routes；发布副本只报告上述两份排除资产缺失，未改保护清单掩盖缺项 |
| README 编写阶段验证 | 完整本地项目 51 目录 README 覆盖、431 个本地链接通过；workflow 静态检查及 16 项 workflow 单元测试通过 |
| 发布代码运行检查 | 确认导入的是发布副本中的 `cevns_pyeft`，资源显式指向完整本地根；三个实验均完成预测和统计评价，与本地 README 验证结果一致 |

发布代码的小网格运行结果如下。CsI2021、Ar2020 使用 `n_er=5, n_enu=12, n_pe_bin=3`；CsI2017 使用 `n_enu=12`，其余取实验定义默认值。计数单位为 `events/bin`，总数为逐箱求和；χ² 是各实验当前绑定的近似统计模型结果。

| 实验 | 箱数 | 计数总和 | χ² |
|---|---:|---:|---:|
| CsI2021 | 9 | 381.8912488750059 | 10.777108968658267 |
| CsI2017 | 25 | 167.55855004906758 | 24.696754086455268 |
| Ar2020 | 12 | 110.45236422054067 | 10.0294026463606 |

这些检查用于确认发布复制和基本调用路径，不能据此宣称积分收敛、完整 Fast/Slow 回归通过或物理审计问题已闭合。当前科学限制见[能力矩阵](Gitup01/docs/user-guide/capability-matrix.md)及[物理文档](Gitup01/docs/physics/README.md)。
