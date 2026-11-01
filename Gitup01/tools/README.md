# 当前工具

`build_wheel.py`：离线构建wheel并安装到本任务outputs的隔离target，不修改用户Python环境。
`verify_wheel.py`：用Python -I从项目外cwd验证三个 COHERENT 实验和显式外部资源。
执行方式：`python tools/build_wheel.py`，再 `python tools/verify_wheel.py`。

CONUS 科学复现工具已归档到 CONUS-Backup（本地 CONUS-Backup/README.md，未随分支上传）。
一次性阶段报告/冻结脚本已归档；
两个受影响测试已改从tests/helpers/regression_cases.py导入完全相同的points/GRIDS。
