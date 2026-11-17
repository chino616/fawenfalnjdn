# 当前五条实验对应的文件夹构造

2026-11-15 补充公共绘图主题：见[绘图文件架构](../../plotting/README.md)与[v4 主题入口](../../plotting/paper_theme/README.md)。下树中新增 `plotting/` 管理跨实验视觉资源，数值主线的历史基线仍按下述日期解释。

下树为2026-11-11集中整理的五条SM/前向主线基线；[2026-11-13非8B状态更新](CURRENT_REPRODUCTION_STATUS.md)说明CsI-time、CsI2017、Ar与CONUS+的实际完成范围。8B由独立对话按continuous_acceptance完善，其后续版本见[太阳导航](PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md)。每个METHODS.md说明对应处理方式，完整源码与历史材料不在此树重复展开。

```text
Gitup01/
├─ plotting/
│  ├─ README.md                       公共绘图职责和文件架构
│  └─ paper_theme/
│     ├─ README.md                    v4 来源、文件用途和调用方法
│     ├─ PAPER_THEME_GUIDE.md          全文通用绘图规范
│     ├─ PAPER_THEME.json              唯一活动主题参数
│     ├─ theme_styles.py               多系列线/柱样式接口
│     ├─ plot_template.py              字体、坐标轴、固定画布及导出示例
│     ├─ MIGRATION.md                  旧入口移除与接入验证记录
│     └─ previews/                     12色、多图型、多系列的PDF/SVG/PNG
├─ docs/experiments/
│  ├─ LATEST_EXPERIMENTS.md             最新实验总入口
│  ├─ latest_analysis_index.json        同一入口的机器索引
│  ├─ LATEST_FOLDER_LAYOUT.md           本文件
│  ├─ PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/
│  │  ├─ SOLAR_B8_SINGLEBIN_ONBOARDING.v3.2.1.md
│  │  ├─ PandaX4T.singlebin.physics.v3.2.1.md
│  │  ├─ XENONnT.singlebin.physics.v3.2.1.md
│  │  └─ METHODS.md
│  ├─ COHERENT/
│  │  ├─ CsI2021/time_resolved/          时间分析：onboarding、SM/NSI报告、METHODS
│  │  ├─ CsI2017/                       25箱说明与METHODS
│  │  └─ Ar2020/                        12箱说明与METHODS
│  └─ CONUS_Plus/datasets/conusplus_kkl_run1/
│     ├─ experiment.physics.md          当前v3 onboarding
│     ├─ experiment.physics.summary.md
│     ├─ METHODS.md                     SM和NSI的处理区别
│     └─ benchmarks/
│        ├─ sm_response_20261106/SM_BENCHMARK.md
│        └─ nsi_response_20261106/NSI_BENCHMARK.md
├─ data/
│  ├─ experiments/
│  │  ├─ COHERENT_CsI/CsI2017/          YAML、NPZ、Physics MD；确定性25箱
│  │  ├─ COHERENT_CsI/CsI2021/time_resolved/
│  │  │  ├─ analysis_inputs.npz         当前99箱、时间边缘和分析数组
│  │  │  ├─ nuclear_response_CsI.npz    核表切片，仅供来源核对
│  │  │  └─ README.md
│  │  ├─ COHERENT_Ar/Ar2020/            YAML、NPZ、Physics MD；专用12箱折叠
│  │  └─ CONUS_Plus/conusplus_kkl_run1/ Flux、Ge库存、观测及来源映射
│  ├─ benchmarks/
│  │  ├─ solar_b8_singlebin_2601_19883/ 三样本独立card、接受度、拟合信号
│  │  ├─ COHERENT_CsI/CsI2021_time/nsi_20261108/points.json
│  │  └─ CONUS_Plus/conusplus_kkl_run1/
│  │     ├─ sm_response_20261106/        SM论文图线基准
│  │     └─ nsi_response_20261106/       NSI区间/轮廓基准与统计准备
│  └─ responses/responses_all.json      共用原核响应
├─ examples/
│  ├─ COHERENT_CsI/
│  │  ├─ time_resolved_common/          本地时间模块、纯NSI映射、ORIGIN.json
│  │  ├─ time_resolved_sm/              SM前向、验证、绘图
│  │  └─ time_resolved_nsi/             24点NSI前向、验证、绘图
│  └─ CONUS_Plus/conusplus_kkl_run1/
│     ├─ run_benchmark.py               --method sm 或 --method nsi
│     ├─ conusplus_paths.py             本地路径、输入指纹、新输出保护
│     ├─ LOCAL_INPUTS.json
│     ├─ sm_response/                  唯一SM装配及计算/核对/报告
│     └─ nsi_response/                 复用SM装配的NSI映射、核、拟合与报告
├─ tools/
│  ├─ latest_experiments.py             生成/检查最新入口、METHODS及README导航
│  └─ run_solar_b8_singlebin_benchmark.py
├─ outputs/
│  ├─ solar_b8_singlebin/20261111_response_run2/
│  ├─ csi2021_time_sm_20261107/
│  ├─ csi2021_time_nsi_20261108/
│  ├─ csi2021_time_sm_data_comparison_20261109/
│  ├─ COHERENT_CsI/CsI2017/sm_legacy_25bin_20261111/SM_RESULT.json
│  ├─ COHERENT_Ar/Ar2020/sm_legacy_12bin_20261111/SM_RESULT.json
│  ├─ CONUS_Plus/conusplus_kkl_run1/
│  │  ├─ sm_response_20261106/           最新SM数值、图、收敛证据
│  │  ├─ nsi_response_20261106/          最新NSI数值、图、核与验证
│  │  └─ provenance/response_20261106_source.zip
│  └─ latest_layout_20261111/           本次迁移、回滚映射和实际验证
├─ workflows/cevns-pyeft/runs/
│  ├─ COHERENT_CsI/CsI2021/time_resolved/来源、证据、合同及原数组证据
│  └─ CONUS_Plus/conusplus_kkl_run1/
│     ├─ P00/P01/P02/P03等来源与合同
│     └─ benchmarks/
│        ├─ sm_response_20261106/       SM原执行/阶段记录
│        └─ nsi_response_20261106/      NSI原执行/阶段记录
└─ cevns_pyeft/                         共用引擎；现有dataset注册保持原状
```

CsI2017与Ar2020的当前数值是已执行的指定回归网格核对，不被目录名称提升为默认网格收敛结论。CONUS+与CsI-time的原科学来源/审核限制继续保留。

[返回最新入口](LATEST_EXPERIMENTS.md) · [本次整理与验证](../../outputs/latest_layout_20261111/README.md)
