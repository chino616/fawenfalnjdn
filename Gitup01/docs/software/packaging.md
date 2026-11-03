# 打包与安装边界

Status: CURRENT
Scope: 当前打包配置和工具用途；本次文档任务没有重建安装包或运行物理回归。

[pyproject.toml](../../pyproject.toml) 使用 setuptools，只发现 cevns_pyeft 包。当前版本保持 0.1.0a1。外部 data、docs、workflows 和论文材料不随运行 wheel 自动提供。

在项目根执行 `python -m pip install -e .` 可作开发安装；运行依赖见 [requirements.txt](../../requirements.txt)。
[build_wheel.py](../../tools/build_wheel.py)离线构建 wheel 并安装到 outputs/release 的隔离目录；[verify_wheel.py](../../tools/verify_wheel.py)使用显式外部资源和项目外 Python -I 进行检查。
build、egg-info、wheel 和隔离安装副本是可重建产物，当前已清理并由 gitignore 排除。现存发行日志仅是历史记录，不能据此声称当前文件刚通过安装验证。

构建与安装工具的使用入口见 [tools/README](../../tools/README.md)。
