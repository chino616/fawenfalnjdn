# Refactor03 验证

日期：2026-10-29（Asia/Shanghai）。C0–C6 工程调整已完成。本文件记录发布前的本地验收；本次上传范围见 [发布记录](RELEASE_03.md)。

## 最终完整测试

运行于 `F:\Work\.codex_conda_envs\codex-py311\python.exe`，Python 3.11.15、NumPy 2.4.6、SciPy 1.17.1、pytest 9.1.1。
最终运行时、测试和数据停止修改后，在独立新进程执行：

```powershell
python -m pytest -q tests --basetemp=.pytest-tmp/refactor03-final-2 --junitxml=outputs/refactor03/verified_tests.xml
```

结果：**237 passed，0 failed，0 errors，0 skipped**，983.00 秒。
完整输出：日志（本地验收路径：`../outputs/refactor03/verified_tests.log`）、JUnit（本地验收路径：`../outputs/refactor03/verified_tests.xml`）、环境（本地验收路径：`../outputs/refactor03/environment.json`）。
原现场 C0 为 223 passed；本轮新增14项接口、组件和缓存合同检查。
测试输入的内容哈希在结束时再次核对，未在全测中修改源码、测试、配置或数据。

## 独立数值回归

在本轮改动之前独立冻结 C0，在改动后重新计算四实验、两组网格、SM/NP/复多味参数。
共比较 **634 个数组和18项统计结果**；没有重新生成原 tests/reference 或放宽任何容差。

| 数据集 | 数组数 | 最大绝对差 | 最大相对差 |
|---|---:|---:|---:|
| CsI2021 | 168 | 0 | 0 |
| CsI2017 | 174 | 3.552713678800501e-15 | 4.70193535432221e-16 |
| Ar2020 | 150 | 0 | 0 |
| CONUS | 142 | 0 | 0 |

χ²最大绝对差：7.105427357601002e-15。
详见 C0独立比较（本地验收路径：`../outputs/refactor03/c0_comparison.json`）。小网格验证工程等价，不代表科学收敛。

C0冻结文件位于 `outputs/refactor03/c0/numerical/`；只读复算比较脚本保留在项目旁的
`../重构/refactor03_work/verify_c0.py`。本次比较命令（从Gitup01执行）：

```powershell
python ../重构/refactor03_work/verify_c0.py
```

该脚本读取修改前的冻结结果并写出本次比较，不覆盖原参考。

## 发行、示例和保护

- wheel仅含运行时包和dist-info；包内所有Python文件与当前源码、隔离安装后的文件逐字节一致。
- wheel SHA256：`fec496bccc2e5339ea9d111ea96729937d3152f12091fc166090fc860c043e04`。
- 在项目外cwd、Python `-I`、无PYTHONPATH条件下，四实验预测通过，分别返回9/25/12/19箱，CONUS含C2/C3/C5有名探测器。
- 同一隔离安装下，四实验切换、启停selection及带独立解析值的synthetic示例均通过。
- 189份原数据、参考、工作流和物理依据经明确路径映射后重新核对内容哈希，均保持不变。
- 外部归档的ZIP CRC、manifest及每个归档条目SHA256再次验证通过；未读取backup作为物理输入。
- 当前用户文档的相对链接和UTF-8读取检查通过；历史evidence来源路径保持原记录。

构建与基本运行命令（从Gitup01执行；不修改用户Python环境，安装到本地target）：

```powershell
python tools/build_wheel.py
python tools/verify_wheel.py
python examples/experiment_modularization/run_experiments.py --resources .
python examples/experiment_modularization/run_experiments.py --resources . --selection configs/analysis_selection.example.yaml
python examples/experiment_modularization/synthetic_dataset.py
```

本次隔离示例验证的完整 `-I` 子进程命令及项目外cwd记录在examples_check.json；
后面三个普通源码调用用于日常使用，需先安装包。

证据：项目外四实验（本地验收路径：`../outputs/release/outside_cwd.json`）、wheel内容（本地验收路径：`../outputs/release/contents_check.json`）、
示例（本地验收路径：`../outputs/release/examples_check.json`）、保护核对（本地验收路径：`../outputs/refactor03/protected_files_check.json`）、
[文件与恢复清单](CHANGE_MANIFEST.json)、最终回执（本地验收路径：`../outputs/refactor03/final_receipt.json`）。

## 审查问题与边界

I01–I04均已修复并覆盖行为检查：未知/错误作用域资源键拒绝；调用方可变输入被快照；实际装配影响物理身份；统计输入检查坐标、单位、箱宽和归一化。
CsI2017/Ar2020/CONUS的执行路径消费实际源、目标、截面、响应和曝光，公共EFT公式未复制。

任务包的另一审查环境（Python3.12.14/NumPy2.3.5/SciPy1.17.0）曾为221 passed、2 failed：
一项是未随远程交付的CONUS观测，一项是CsI2021约4.25e-16的位级差异。
本现场存在原CONUS观测；核对原CSV与论文/metadata哈希后按原字节迁移，未用synthetic数据补齐。
本次报告只声明上述Python3.11环境的实际结果，没有声称重新运行过该Python3.12环境。

CsI2017和Ar2020的legacy Fast对任意替换组件明确拒绝；CONUS Fast仍为探测器响应矩阵，率按理论点重算。
CONUS默认357kg·day不能套用effective119观测，后者保持原近似Gaussian含义。
没有新增天然Ge、官方on/off likelihood、联合χ²、ROOT时间模板或新的物理过程；未提升任何科学Gate。
CsI2017计数质量14.6kg与源元数据14.57kg、Ar历史轴约定、CONUS候选Ge73及原弱混合角默认值均保留。
论文、Notebook及仍有效的复现/核查工具按研究用途保留；目录清理未据名称或年代删除它们。
