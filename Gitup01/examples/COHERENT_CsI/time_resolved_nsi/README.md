# CsI2021 时间分辨 NSI 前向事例数

按用户选择计算24个实对称u/d矢量NSI点与SM的未拟合信号。直接复用主项目SM/RESPONSE、四算符核编译器，以及用户指定旧目录的ε→Wilson映射与时间权重。原package、核表、参考和统计不修改；此处工程核不构成正式P08冻结。

[主报告](../../../docs/experiments/COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md) · [运行结果和来源](../../../outputs/csi2021_time_nsi_20261108/README.md) · [主线记录](../../../workflows/cevns-pyeft/runs/COHERENT_CsI/CsI2021/time_resolved/nsi_benchmark_20261108/README.md) · [上一级](../README.md)

| 文件 | 实际职责 |
|---|---|
| [prepare_benchmark.py](prepare_benchmark.py) | 新运行前固定原package和SM helper指纹；比较原生与checked同网格的全24点，保存独立等价记录 |
| [run_benchmark.py](run_benchmark.py) | 从r2读取同一输入、校验来源，调用原项目核编译和旧时间权重，保存全部矩阵、通道、核素和源分量 |
| [validate_benchmark.py](validate_benchmark.py) | 原生Slow逐点对照、SM恢复、味流/符号、整体与独立T/Eν/PE加密，阈值0.005 events/bin |
| [summarize_benchmark.py](summarize_benchmark.py) | 生成24点与逐箱CSV、配置/数据字典、三份同源报告、资源审计；先备份再同步四个父README |
| [plot_benchmark.py](plot_benchmark.py) | 只读通过检查的NPZ，输出投影、11个时间窗和味分量变化PNG/SVG；只画信号 |
| [validate_documents.mjs](validate_documents.mjs) | 独立Markdown/KaTeX/Edge环境检查链接、图片、真实目录跳转/返回、公式与720px阅读布局 |
| [finalize_benchmark.py](finalize_benchmark.py) | 回读CSV/NPZ和来源指纹，生成环境、代码快照、文件归属与交付清单；不修改原Runtime或数据 |

需要numpy、scipy、uproot、PyYAML；绘图另需matplotlib。默认读取项目内time_resolved_common及data/benchmarks的最新24点坐标，不需要旧项目副本。从本项目根执行，`$run`必须为新目录：

```powershell
$entry='examples/COHERENT_CsI/time_resolved_nsi'
python -B "$entry/prepare_benchmark.py" --run-dir $run --stage prepare
python -B "$entry/run_benchmark.py" --output-dir "$run/pilot" --n-er 16 --n-enu 40 --n-pe-bin 12 --pe-step 2
python -B "$entry/run_benchmark.py" --output-dir "$run/pilot_checked" --n-er 16 --n-enu 40 --n-pe-bin 12 --pe-step 2 --checked-coefficient-energy
python -B "$entry/run_benchmark.py" --output-dir "$run/grid_256_480" --n-er 256 --n-enu 480 --n-pe-bin 128 --pe-step .125
python -B "$entry/run_benchmark.py" --output-dir "$run/grid_256_480_checked" --n-er 256 --n-enu 480 --n-pe-bin 128 --pe-step .125 --checked-coefficient-energy
python -B "$entry/prepare_benchmark.py" --run-dir $run --stage equivalence
python -B "$entry/validate_benchmark.py" --run-dir $run --stage native
python -B "$entry/run_benchmark.py" --output-dir "$run/grid_512_960" --n-er 512 --n-enu 960 --n-pe-bin 256 --pe-step .0625 --checked-coefficient-energy
python -B "$entry/run_benchmark.py" --output-dir "$run/grid_1024_1920" --n-er 1024 --n-enu 1920 --n-pe-bin 512 --pe-step .03125 --checked-coefficient-energy
python -B "$entry/validate_benchmark.py" --run-dir $run --stage precision --finest grid_1024_1920
python -B -m pytest -q tests/test_component_replacement.py tests/test_rates_differential_flavor.py tests/test_nuclear_response_convention.py --junitxml="$run/runtime-tests.xml"
python -B "$entry/summarize_benchmark.py" --run-dir $run
python -B "$entry/plot_benchmark.py" --run-dir $run
```

本次512/960的独立Eν检查曾超门限，最终采用1024/1920。重跑到新目录时不要求复制该失败实验；可另执行512的precision stage留存诊断。汇总脚本若找到该组轴检查则保留失败记录。汇总会生成主文档并更新父README，重复生成前须先保存旧版并选新备份标识。单纯数值重跑不必执行汇总步骤。

NSI定义依据为[2211.11905v2](https://arxiv.org/abs/2211.11905v2) PDF第5页Sec.2.2式(5)–(6)；本轮点含旧诊断坐标和明确设计的测试刺激，均不冒充论文最佳拟合。背景归一、论文Helm/辐射修正等价和正式统计仍保留原缺口，详见报告。

<!-- latest-analyses:start -->

## 当前最新分析与处理方式

[五条实验最新入口](<../../../docs/experiments/LATEST_EXPERIMENTS.md>)

| 分析 | 方法/版本 | 输入 | 结果与核对范围 |
|---|---|---|---|
| CsI-time：9PE×11时间箱 | [r2 / SM 20261107；NSI 20261108；处理方式](<../../../docs/experiments/COHERENT/CsI2021/time_resolved/METHODS.md>) | [当前输入](<../../../data/experiments/COHERENT_CsI/CsI2021/time_resolved/analysis_inputs.npz>) | [SM报告](<../../../docs/experiments/COHERENT/CsI2021/time_resolved/SM_BENCHMARK.md>) / [NSI报告](<../../../docs/experiments/COHERENT/CsI2021/time_resolved/NSI_BENCHMARK.md>) / [观测叠加](<../../../outputs/csi2021_time_sm_data_comparison_20261109/README.md>) |

来源/审核状态、计算完成状态与默认Runtime注册分别记录；链接不授予新的科学批准。

<!-- latest-analyses:end -->
