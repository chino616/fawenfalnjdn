# 当前结果汇总表

**当前为2026-11-15 run2修订版。** CsI2021的论文SM总率Comparator已补为341±11(theory)±42(experiment)，实验拟合信号306±20单列；[原句、页码、选窗和PDF指纹](<../../论文图NoteBook/8. SM_experiment_benchmarks/CSI2021_COMPARATOR_EVIDENCE.md>)。run1保留为修订前快照，run2对照核验其余科学数值不变。

本目录只读汇总五条实验主线及其补充统计路线的最新已存结果，区分SM前向、SM参数、NSI、χ²、能标主版本、完整22算符控制和三组联合。它不重新拟合、不修改正式输入或Runtime，不提升onboarding Gate或作者似然等价性状态。

[最新阅读入口](../../docs/experiments/RESULTS_TABLES_20261115.md) · [完整表与工作簿](../../outputs/results_summary_20261115_run2/README.md) · [每步Python路线](../../docs/experiments/COMPUTATION_ROUTES_20261113.md)

## 文件和数据流

| 文件 | 职责 |
|---|---|
| [collect_results.py](collect_results.py) | 读取明确指定的66条一维、41面二维、24个时间前向点、224条能标及benchmark；回代已存最佳点的Gaussian分解，独立核对全部c→Λ正逆变换；生成JSON、17类CSV和完整Markdown |
| [build_workbook.mjs](build_workbook.mjs) | 使用bundled `@oai/artifact-tool`生成17工作表Excel；能标以显式公式链接|g|及|c|max，核对全部缓存数值、|g|缩放、公式错误并逐表渲染 |
| [verify_delivery.py](verify_delivery.py) | 用标准库只读核查导出XLSX的值/公式缓存/筛选/冻结窗格及所有CSV；复查来源哈希，生成内部视觉联系表；`--links-only`核查9份指定文档的本地链接，不编写XLSX |
| [revise_csi_comparator.py](revise_csi_comparator.py) | `evidence`核对原始PDF第4页并保存原句/数值/哈希；`table`只重画论文总表；`collection`生成有明确修订文件名的合集并核对其余7页内容流不变；不做物理拟合 |

所有脚本仅由显式CLI调用，不被Runtime、资源注册或工作流导入。Python科学运算沿用已安装的NumPy/SciPy/Numba及主线代码；Excel使用桌面工具定位的bundled Node依赖。Windows沙箱拒绝创建指向WindowsApps的junction，本轮通过`createRequire`从定位后的只读bundled目录解析公开包，未安装或更改依赖。`node_modules`不属于科学产物。

## 重建冻结的2026-11-15快照

从Gitup01根目录运行，`NEW_SUMMARY`必须是新目录，避免覆盖既有数值表。先复制本轮write plan并核对其来源选择；该命令重建相同日期/来源快照，不自动挑选未来结果。

```powershell
$summaryRun = 'outputs/NEW_SUMMARY'
New-Item -ItemType Directory -Path $summaryRun
Copy-Item -LiteralPath 'outputs/results_summary_20261115_run2/WRITE_PLAN.json' -Destination "$summaryRun/WRITE_PLAN.json"
& 'F:/Work/.codex_conda_envs/codex-py311/python.exe' -B examples/results_summary/collect_results.py --output $summaryRun
```

通过桌面`load_workspace_dependencies`取得`node.exe`、`node_modules`和带Pillow的bundled Python路径，分别赋给下列任务变量。生成前按表格技能执行一次artifact operation marker；同一任务的版式修订不重复marker。

```powershell
& $summaryNode examples/results_summary/build_workbook.mjs $summaryRun $summaryBundledModules
& $summaryBundledPython -B examples/results_summary/verify_delivery.py --output $summaryRun
```

数值表生成器拒绝覆盖`TABLES.json`；同一个新汇总中的Excel/内部预览可以在版式验收时重建。发布前逐表查看预览，检查明确允许的README导航、源文件保护及文档链接。`verify_delivery.py`不会自动宣称人工视觉核对通过。

文档验收：仓库`tools/validate_docs.py --files`检查明确选择的非outputs文档；它明确拒绝outputs内文档，因此再用`verify_delivery.py --links-only`检查当前汇总、CsI证据及对应导航共15份指定文档。本地链接数量以run2的qa记录为准。只检查路径存在性，不检查HTTP可用性或Markdown锚点，不遍历历史outputs/backup。

## 科学范围

当前为approximate local-model benchmark。一维SM参数是sin²θW及太阳fB，GF/振荡参数未扫描。CsI-time为前向分析，CsI2017只有冻结SM点。Ar均误差与历史非对称方法不混用。太阳continuous_acceptance/v3.4.1、固定态full22控制及尚未执行的v3.5分别记录。

能标采用`c=s|g|/Λ^(d−4)`、`|g|=1`、GeV；全域下确界、SM分支及系数正负号分别列出，全部分离允许带保留。full22控制的LNV味结构、固定太阳态和dim-8正定性缺口不能由数值验收解除。来源身份、区间端点与所有文献定位在交付中可追查。

[返回examples](../README.md)
