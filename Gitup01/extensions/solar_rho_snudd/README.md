# SNuDD：可移除的外部太阳传播源

[新v3.4物理/数值/来源读本](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_EXTERNAL_ONBOARDING.v3.4.md>) · [已经执行的主线基准](<../../outputs/external/solar_rho_snudd/20261112_run1/README.md>) · [实际来源/版本/参数卡](<snudd.input.json>)

只有export_rho.py在独立解释器内import snudd；其他文件由主项目解释器使用，不把SNuDD加入根依赖。完整ρ文件经验证后进入显式load_snudd→标准Runtime。旧入口不受影响。

| 文件 | 职责 |
|---|---|
| [export_rho.py](<export_rho.py>) | NP-only参数映射、独立太阳传播、完整ρ和诊断 |
| [protocol.py](<protocol.py>) | 可版本化文件身份、物理性/内容/坐标核验 |
| [state.py](<state.py>) | 子进程与精确子网格状态提供器 |
| [experiment.py](<experiment.py>) | 新Definition/scoped Catalog/PreparedExperiment；源与Fast状态双绑定 |
| [run_with_rho.py](<run_with_rho.py>) | 实际三样本Slow/Fast/统计与旧源对照 |
| [prepare.py](<prepare.py>) | 来源卡与锁定依赖生成/检查 |
| [snudd.input.json](<snudd.input.json>) | 实际输入、标准文献、固定commit和哈希 |
| [requirements.lock.txt](<requirements.lock.txt>) | 实际独立环境版本 |


## 安装（当前已经完成）

从Gitup01根目录；选择已有Python3.11解释器。先固定commit，再安装。

```powershell
git clone --no-checkout https://github.com/SNuDD/SNuDD.git .externals/SNuDD
git -C .externals/SNuDD checkout --detach 11622ded104994959a649d85e263c2d9f933ea74
python -m venv .venvs/snudd
.venvs/snudd/Scripts/python.exe -m pip install --index-url https://pypi.org/simple -e .externals/SNuDD packaging==26.3
.venvs/snudd/Scripts/python.exe -m pip check
```

精确重装应按requirements.lock.txt中固定的NumPy/SciPy/Pandas等版本安装，保留安装报告中的轮子hash。上游packaging依赖漏声明，已明确补齐。使用主项目Python运行tools/run_solar_b8_snudd_benchmark.py，工作进程会自动使用.venvs/snudd。

原cevns_pyeft/物理源码和data/只读；此扩展不进入根发行包的强制依赖。删除/移走扩展、独立环境与checkout后，原程序仍可运行；移除时同步主线导航。上游GPL-3.0 LICENSE保留在.externals/SNuDD。

<!-- solar-snudd-v341:start -->

## 太阳完整统计：SNuDD v3.4.1

[三样本全流程、联合区域和论文比较](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_BENCHMARK.v3.4.1.md>) · [实际结果、图与验收](<../../outputs/external/solar_rho_snudd/20261112_fig4_run2/README.md>)。已计算601×601面与各方案联合最小值；2601 Fig.4绿色精确复现未成立，旧结果保留。

[scan_source.py](<scan_source.py>)导出原1000节点数值输入；[scan.py](<scan.py>)计算相同ee-only代数求积，完整ρ逐点验证；不新增SNuDD导入或概率插值。

<!-- solar-snudd-v341:end -->

<!-- solar-full-rho-trace-onboarding-v35:start -->

## 当前太阳onboarding：完整ρ与Tr(ρK) v3.5

[微分/总截面、事例数积分与三样本差别](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_ONBOARDING.v3.5.md>) · [明确合同与待改程序](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/SNUDD_FULL_TRACE_CONTRACT.v3.5.json>)。按用户要求先更新文档；旧投影程序尚未改成新版trace，旧结果保留。

<!-- solar-full-rho-trace-onboarding-v35:end -->
