# 当前工具

`build_wheel.py`：离线构建wheel并安装到本任务outputs的隔离target，不修改用户Python环境。
`verify_wheel.py`：用Python -I从项目外cwd验证四实验和显式外部资源。
执行方式：`python tools/build_wheel.py`，再 `python tools/verify_wheel.py`。

`conus/` 与 `experiment_integration/conus_paper_config_guard.py` 是既有科学复现/配置核查工具，保留。
CONUS论文/历史diagnostics/benchmark必须具备后再执行；这些工具读取或生成outputs的历史交付结构，
不自动授予科学状态，也不是新的默认资源loader。一次性阶段报告/冻结脚本已归档；
两个受影响测试已改从tests/helpers/regression_cases.py导入完全相同的points/GRIDS。
