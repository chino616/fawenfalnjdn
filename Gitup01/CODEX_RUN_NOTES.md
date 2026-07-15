# Codex 运行注意事项

本文档用于让新的 Codex 窗口在本目录下直接运行程序。

目标项目目录：

```powershell
F:\Work\2026-07-15 CEvNSpyEFT-Local\2026-07-15 First
```

必须使用的 Python：

```powershell
F:\Work\.codex_conda_envs\codex-py311\python.exe
```

不要优先使用项目自带的 `venvCEvNSpyEFT` 或 `.venv`。本项目在 Codex 中统一使用上面的 conda Python。

## 1. 进入项目目录

```powershell
Set-Location -LiteralPath "F:\Work\2026-07-15 CEvNSpyEFT-Local\2026-07-15 First"
```

## 2. 检查 Python

```powershell
Test-Path -LiteralPath "F:\Work\.codex_conda_envs\codex-py311\python.exe"
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" --version
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "import sys; print(sys.executable)"
```

期望结果：

```text
True
Python 3.11.x
F:\Work\.codex_conda_envs\codex-py311\python.exe
```

## 3. 快速检查项目是否可导入

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -m py_compile src/cevns_pyeft/core/engine.py src/cevns_pyeft/statistics/cutoff_single.py src/cevns_pyeft/statistics/cutoff_multi.py src/cevns_pyeft/statistics/chi2_2d.py src/cevns_pyeft/eft/uv_dim6.py
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "from cevns_pyeft.core import engine; print(len(engine.li2026_left_basis_current()))"
```

第二条命令期望输出：

```text
22
```

## 4. 推荐启动方式

本目录已经提供 Codex 专用启动脚本：

```text
run_streamlit_codex_conda.ps1
```

因为 Windows PowerShell 可能禁止直接执行 `.ps1`，请用 `ExecutionPolicy Bypass`：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run_streamlit_codex_conda.ps1
```

启动成功时会看到类似输出：

```text
You can now view your Streamlit app in your browser.
URL: http://127.0.0.1:8610
Uvicorn server started on 127.0.0.1:8610
```

浏览器打开：

```text
http://127.0.0.1:8610
```

## 5. 后台运行注意事项

在 Codex 沙箱中，直接后台启动的子进程可能会在命令结束后被清理。若需要让 Streamlit 在本轮命令结束后继续运行，应请求在沙箱外启动。

后台启动命令建议使用相对脚本路径，避免项目路径中的空格导致引用问题：

```powershell
$project = "F:\Work\2026-07-15 CEvNSpyEFT-Local\2026-07-15 First"
$process = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ".\run_streamlit_codex_conda.ps1") -WorkingDirectory $project -WindowStyle Hidden -PassThru
$process.Id
```

后台启动后验证：

```powershell
Get-NetTCPConnection -LocalPort 8610 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
try { (Invoke-WebRequest -Uri "http://127.0.0.1:8610" -UseBasicParsing -TimeoutSec 8).StatusCode } catch { $_.Exception.Message }
```

期望 HTTP 检查输出：

```text
200
```

## 6. 常见问题

### 无法直接运行 ps1

错误类似：

```text
因为在此系统上禁止运行脚本
```

使用：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run_streamlit_codex_conda.ps1
```

### 端口 8610 被占用

检查：

```powershell
Get-NetTCPConnection -LocalPort 8610 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
```

如果已有旧 Streamlit 进程在运行，可以直接打开：

```text
http://127.0.0.1:8610
```

如果需要重启，先确认 `OwningProcess` 对应的是本项目的 Streamlit，再停止对应进程。

### pip show 输出乱码或 GBK 编码错误

这通常只是 Windows 终端编码问题，不代表依赖不可用。优先用导入检查：

```powershell
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -c "import streamlit, numpy, pandas, scipy, matplotlib, PIL; print('imports ok')"
```

### 不要随意安装或升级包

除非用户明确确认，否则不要运行：

```powershell
pip install ...
pip uninstall ...
conda install ...
conda update ...
```

如确实缺包，先说明要安装的包、原因、目标环境和完整命令，再等待用户确认。

## 7. 本次已验证结果

2026-07-15 已验证：

```text
Python: F:\Work\.codex_conda_envs\codex-py311\python.exe
Python version: 3.11.15
Import check: 22
Streamlit URL: http://127.0.0.1:8610
HTTP check: 200
```

## 8. pytest 安装与测试

pytest 已安装到 Codex 专用 conda 环境：

```text
F:\Work\.codex_conda_envs\codex-py311
```

安装命令：

```powershell
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -m pip install --force-reinstall --ignore-installed pytest
```

说明：

- 不要直接依赖 `pytest.exe`，因为 `F:\Work\.codex_conda_envs\codex-py311\Scripts` 不一定在 PATH 中。
- 推荐始终使用 `python -m pytest`。
- 如果 pip 把依赖误判为用户目录已满足，可能出现 `ModuleNotFoundError`；此时使用上面的 `--force-reinstall --ignore-installed` 命令。

验证 pytest：

```powershell
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -m pytest --version
```

运行项目测试：

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
& "F:\Work\.codex_conda_envs\codex-py311\python.exe" -m pytest -q
```

2026-07-15 已验证：

```text
pytest 9.1.1
14 passed
```

## 9. Phase 1 Split Validation Notebooks

The updated split plan adds compact `*_check.ipynb` notebooks next to migrated modules.

Notebook execution packages were installed into the project-local virtual environment only:

```text
F:\Work\2026-07-15 CEvNSpyEFT-Local\2026-07-15 First\.venv
```

They were not installed into the shared Codex conda environment.

Run all split notebooks from the repository root:

```powershell
Get-ChildItem -Path .\src\cevns_pyeft -Recurse -Filter *_check.ipynb | ForEach-Object {
    & ".\.venv\Scripts\python.exe" -m nbconvert --execute --to notebook --inplace $_.FullName
}
```

2026-07-15 verified result:

```text
15 split notebooks executed successfully
```
