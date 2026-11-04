# 打包与安装边界

Status: CURRENT
Scope: 当前打包配置、正式输入包分发与安装验证入口；实际结果以所链接任务报告为准。

[pyproject.toml](../../pyproject.toml) 使用setuptools，版本0.1.0a1。
[构建hook](../../tools/package_build.py)把registry声明的活动正式三文件打包到wheel的
cevns_pyeft/_data/；[MANIFEST.in](../../MANIFEST.in)确保sdist包含相同data源。
源码/editable读取原data，wheel读取bundled根；中间Onboarding台账、论文和workflow不属于Runtime输入。
实际构建/外部cwd/安装证据见[生命周期报告](../DATASET_PACKAGE_LIFECYCLE_REPORT.md)。
三个活动实验共九份正式文件的 sdist→wheel、安装/外部cwd与两文件隔离验收见
[项目迁移报告](../PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md)，可由
[项目验证工具](../../tools/validate_project_packages.py)在新的输出目录重跑。

在项目根执行 `python -m pip install -e .` 可作开发安装；运行依赖见 [requirements.txt](../../requirements.txt)。
[build_wheel.py](../../tools/build_wheel.py)离线构建 wheel 并安装到 outputs/release 的隔离目录；[verify_wheel.py](../../tools/verify_wheel.py)使用显式外部资源和项目外 Python -I 进行检查。
build、egg-info、wheel 和隔离安装副本是可重建产物，当前已清理并由 gitignore 排除。现存发行日志仅是历史记录，不能据此声称当前文件刚通过安装验证。

构建与安装工具的使用入口见 [tools/README](../../tools/README.md)。
