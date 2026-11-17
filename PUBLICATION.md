# Refactor-07 骨干版发布记录

日期：2026-11-18。分支：`refactor/07-gitup01-20261104`。
基线：远端提交 `be634ff0a9f9523e4c3ce3f57f741660df4ffb3d`。

本次从当前本地 `Gitup01/` 同步可维护代码骨干，并主动分离运行环境、缓存、历史备份和批量生成物。没有修改 `main`，也没有覆盖本地备份。

## 纳入范围

- `cevns_pyeft/` 运行时源码与包内资源；
- `configs/`、`data/` 中可发布的配置、实验输入与必要数值资源；
- `docs/` 的文字文档、索引和书目数据；
- `examples/`、`extensions/`、`tests/`、`tools/`；
- `plotting/` 的主题配置与绘图源码；
- `workflows/` 的定义、规则、模板、技能、脚本与文字化运行记录；
- `论文图NoteBook/` 顶层说明和生成器源码；
- 项目根配置、依赖清单和维护说明。

## 分离范围

- `backup/`、`.venvs/`、`.externals/`、`.pytest_cache/`、`.pytest-tmp/`、`tmp/`；
- `outputs/` 下的计算结果、缓存、日志和图表，仅保留目录说明；
- `docs/references/` 中的论文 PDF，保留引用索引与文字说明；
- `plotting/paper_theme/previews/` 中的预览图；
- `data/` 中由输入审计生成的诊断图片（原始数值输入仍保留）；
- `论文图NoteBook/` 中的 Notebook、生成图片、PDF、CSV、NPZ 和结果目录；
- 工作流中的下载缓存、ROOT/NPZ、归档、图片、HTML 快照和日志等运行产物；
- Python 字节码、构建目录与打包产物。

## 受保护输入

当前本地目录中的以下 6 个文件受 Windows ACL 保护，发布过程无法直接读取。为避免删除核心实验输入，本分支继续保留基线 `be634ff` 中已发布的对应版本：

- Ar2020、CsI2017、CsI2021 各自的 `experiment.input.yaml`；
- Ar2020、CsI2017、CsI2021 各自的 `experiment.resources.npz`。

没有用空文件、推测值或其他实验资源替代它们。

## 验证

- 排除路径审计通过：未追踪备份、环境、缓存、批量输出、参考 PDF、绘图预览或工作流二进制产物。
- 敏感信息特征扫描未发现候选文件；没有已追踪文件达到 10 MiB，更没有超过 GitHub 100 MiB 单文件限制。
- 345 个 Python 文件完成 AST 语法解析，0 个失败；`import cevns_pyeft` 从本发布副本加载成功。
- `tools/update_skill_library.py --check` 通过。
- 文档检查读取 102 份 Markdown、3339 个本地链接，报告 1179 个当前链接缺失；主要来自本次明确分离的 PDF、输出、图集和二进制工作流附件，因此没有伪造占位文件消除错误。
- Skill 包检查识别 17 个 Skills、9 个 workflows、15 条 routes，但旧保护清单对当前完整源码报告 394 项差异（312 项保护指纹、81 项链接、1 项路径）。没有为追求通过而覆盖科学保护指纹。
- 当前系统 Python 未安装 `pytest`，本地隔离环境也未包含 `pytest`，因此未声称测试收集或测试执行通过。

上述失败项是本次“骨干版”与完整本地证据库之间的公开边界，不应解读为全量科学回归已经通过。
