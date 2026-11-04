# 复现命令与版本边界

实际解释器：`F:/Work/.codex_conda_envs/codex-py311/python.exe`；Python 3.11.15、
NumPy 2.4.6、SciPy 1.17.1、Matplotlib 3.11.0、pytest 9.1.1、jsonschema 4.26.0。
没有安装依赖或修改全局环境。原始版本与环境记录见
[baseline](../../../../../outputs/csi2021_package_execution_20261104/baseline.json)。

长计算固定在 revision-2 输入与 wheel-01 实现，结果的 fingerprint 包含代码/模型/数值配置。
当前源码另有窄适配器修复与同期通用 Loader 迁移，不能直接用当前代码重载旧指纹核。

## 在当前工作区复核已保存数值

从 publication worktree 的 Gitup01 根目录运行：

```powershell
$python = 'F:/Work/.codex_conda_envs/codex-py311/python.exe'
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
& $python -X utf8 -B tools/run_csi2021_package_phases.py `
  --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel `
  --package outputs/csi2021_package_execution_20261104/input_revision_2 `
  --phases P04 P05 P06 P07 P09
```

这会检查并复用同身份、NPZ 校验和一致的逐网格预测；P07 再计算同网格 legacy 对照。
使用新的 `--output` 目录会重新计算全部十种 profile，较密网格需数分钟以上。
单独运行一个 profile 使用 `--profile fine_energy`、`fine_recoil`、`fine_observed` 或 `finer`。
不能改数值/代码后沿用旧 identity，不能用 small 网格作为科学冻结。

P08 工程候选在原 wheel-01 外部 case 中保存。现有候选的复核：

```powershell
& $python -X utf8 -B tools/run_csi2021_package_phases.py `
  --implementation-root outputs/csi2021_package_execution_20261104/wheel_validation_01/installed_wheel `
  --package outputs/csi2021_package_execution_20261104/input_revision_2 `
  --phases P08
```

P08 脚本如实输出正式 BLOCKED，工程等价状态在 JSON 内单列；它不产生人工接受。
生成报告使用 `outputs/csi2021_package_execution_20261104/build_execution_reports.py`，
不会重做物理计算或填入批准。

## 从最终 ZIP 在新目录复现

先解压到新目录。ZIP 不是直接覆盖当前工作树的安装包，review source/registry/pyproject
快照含同期变更，先看清单与差异。两个 wheel 是完整但版本不同的引擎分发；只将 wheel-01
用于本次数值 reference，wheel-02 证明更新后适配器可独立装载当前包。

最终 ZIP 不重复携带 installed_wheel、隔离 build/lifecycle/tests 副本。使用本机已有依赖，
将 wheel-01 安装到解压目录中的独立 target（不修改全局环境）：

```powershell
$python = 'F:/Work/.codex_conda_envs/codex-py311/python.exe'
$root = (Resolve-Path './Gitup01').Path
$evidence = Join-Path $root 'outputs/csi2021_package_execution_20261104'
$wheel = (Get-ChildItem -LiteralPath (Join-Path $evidence 'wheel_validation_01/wheels') -Filter '*.whl').FullName
$target = Join-Path (Get-Location) 'engine01'
$taskTemp = Join-Path (Get-Location) 'install_temp01'
New-Item -ItemType Directory -Path $taskTemp | Out-Null
$env:TEMP = $taskTemp
$env:TMP = $taskTemp
$env:PYTHONUTF8 = '1'
& $python -B -m pip install --no-index --no-deps --no-cache-dir --target $target $wheel
& $python -X utf8 -I -B (Join-Path $root 'tools/run_csi2021_package_phases.py') `
  --implementation-root $target `
  --package (Join-Path $evidence 'input_revision_2') `
  --output $evidence --phases P07 P09
```

此命令可从仓库外 cwd 运行。比较专用的 `data/responses/responses_all.json` 在 ZIP 中单独注明角色；
package-only 正式输入只有三文件，它不回退到这份 JSON。复算 P08 时，候选 NPZ 已按原路径保留。
如果本机依赖版本不同，应创建自己的结果目录，记录环境与差异，不覆盖本次证据。

## 测试、Schema 与发布检查

当前工作树测试（适配器数值是 small-grid 合同，不代替 P07 收敛）：

```powershell
& $python -X utf8 -B -m pytest -q -p no:cacheprovider `
  --basetemp outputs/csi2021_recheck_new_tmp `
  tests/test_csi2021_input_package.py tests/test_csi2021_package_fast.py
& $python -B workflows/cevns-pyeft/qa/validate_phase_contract.py `
  workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/07_SLOW_COUNTS_REPORT.md `
  --artifact-root .
& $python -B tools/verify_csi2021_package_release.py --mode wheel `
  --output outputs/csi2021_recheck_new_wheel
```

发布工具要求一个尚不存在的输出目录；lifecycle 模式只操作其隔离 managed_copy。
不要删除已有 tmp、backup 或 reference。原始完整测试结果、失败和清理错误全部保留；
重跑选择新目录，测试通过与环境错误分别计数。

全局 Skill QA 的保护哈希属于先前 workflow-only 范围，当前 Runtime 接入/同期迁移使其失败。
本任务没有通过重写保护基线消除该失败。结构审计和完整保护检查的实际状态见
[workflow_structure_audit.json](../../../../../outputs/csi2021_package_execution_20261104/workflow_structure_audit.json)。
