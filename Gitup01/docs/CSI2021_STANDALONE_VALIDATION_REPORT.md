# Task 06 — Two-file Standalone Validation

2026-11-04；branch `refactor/07-gitup01-20261104`；HEAD
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。保留所有既有修改，未提交 Git。
读取任务规则/顺序、Task06、实际 Loader/Runtime、wheel 工具及冻结 reference metadata。

新增 [validate_package_standalone.py](../tools/validate_package_standalone.py)。离线 build/install wheel
至临时 target，再仅从临时引擎移除全部旧 *_definition.py、legacy_parameters.py 和候选 adapter。
原工作区不删除任何文件。独立进程使用 python -I -B，import guard 禁止旧参数导入，
文件 audit hook 禁止原源码树、外部 responses JSON、旧 spec 和 Physics MD。
正式依赖沿用解释器已安装版本；没有声称第二台实体机器或全新操作系统。

外部运行根：`F:/Work/2026-07-15 CEvNSpyEFT-Local/standalone-onboarding-20261104-run01/`。
保留 build/install/worker.log、results.json、package_predictions.npz 和全部篡改错误；
项目内副本：`outputs/onboarding/task06/standalone_results.json`。

| 检查 | 实际结果 |
|---|---|
| I01 | PASS；仅 YAML/NPZ 加载、Schema、绑定、资源校验。 |
| I02 | PASS；外部 cwd 与安装引擎，源码树不在 sys.path。 |
| I03 | PASS；旧定义/legacy 参数从临时安装移除，import guard 生效。 |
| I04 | PASS；无源码树或未声明实验资源；模型只读两文件。 |
| I05 | PASS；9×float64、events/bin、6 个 source×isotope 分量、有限非负、分量总和一致。 |
| I06 | PASS；原 approximate Gaussian；official likelihood BLOCKED。 |
| I07 | PASS；仅 gamma_b×0.99，直接响应密度及最终预测均变化。 |
| I08 | PASS；Cs133 M 数组×1.001、更新哈希，输出变化，原包未修改。 |
| I09 | PASS；archive hash/key/shape/dtype/unit/model/dependency/path/role/物化指纹十种篡改逐项拒绝。 |
| I10 | PASS；移动两文件至另一目录，预测数值完全相同；同主机。 |

小网格全算符 Fast 现场编译并与 Slow 相容，不使用外部 kernel/reference。

| 网格 | n_er/n_enu/n_pe_bin/step | events | 预测秒 |
|---|---|---:|---:|
| small | 5/12/4/4 | 379.8315235321747 | 2.082 |
| default | 21/120/8/3 | 332.93383502572743 | 25.770 |
| refined | 41/240/16/1.5 | 329.53506500643806 | 73.236 |

small/default 对冻结内部基线最大绝对差 1.07e-13 / 6.76e-14，原容差 rtol=1e-10、atol=1e-12。
解析 1.643 秒，完整 load/prepare 2.171 秒，small Fast 编译+预测 0.435 秒。
另一相同安装 small 进程以 Windows PSAPI 实测峰值工作集 83,771,392 bytes；非全测试最高内存。
无 NaN/Inf 或非物理负数。

default→refined 最大逐箱绝对差 0.7988 events，相对 refined 最大 15.74%，总量变化约 1.03%。
**默认网格收敛尚未证明**，没有改数值、参考或容差掩盖差异。

实际命令：`python -B tools/validate_package_standalone.py --package data/experiments/COHERENT_CsI/CsI2021 --output <新的外部目录>`。
首次直接 pip build 因 OS TEMP ACL 失败；工具指定工作区 TEMP/TMP 后离线 build/install 成功。
Runtime 不需要原始论文、ROOTTime 或其他实验数据。技术 ready 不改变 DRAFT/PARTIAL、
human NOT_REVIEWED、官方统计/一般反中微子/科学发布 BLOCKED；Task07继续审核来源。

[进度](ONBOARDING_TASKS_02_10_PROGRESS.md)
