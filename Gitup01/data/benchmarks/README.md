# benchmarks

<!-- solar-singlebin-v321:start -->

## 太阳⁸B单 bin：2601.19883v2

[单bin v3.2.1：输入、来源、代码与SM结果](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/README.md>) · [多bin v3.1（保留）](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_ONBOARDING.v3.1.md>)。

单bin采用2601.19883v2 Eqs.(87),(88)：paired/US2/XENONnT三个信号总数；[独立数据](<solar_b8_singlebin_2601_19883/README.md>)、[独立入口](<../../tools/run_solar_b8_singlebin_benchmark.py>)、[独立结果](<../../outputs/solar_b8_singlebin/20261111_response_run2/README.md>)。多bin继续原Qy平均映射/响应基底及Ne/cS2分箱。只共享底层物理，不交叉数据、统计和缓存。旧文档中的“当前v3.1”仅指多bin分支。

<!-- solar-singlebin-v321:end -->

<!-- solar-vector-20261108:start -->

## Solar B8 vector benchmark

[solar_b8_vector_v1/](solar_b8_vector_v1/README.md)保存V/B−L显式项目测试点及固定正式输入包哈希。它是benchmark配置，不是新测量数组或实验注册。

<!-- solar-vector-20261108:end -->

<!-- pandax-simplified-20261110:start -->

## PandaX US2：简化方法参数卡

[pandax_us2_simplified_v1/](pandax_us2_simplified_v1/README.md)固定R01无分辨率平均映射、R02 nominal Qy与Total(US2)及现有包哈希。直接预测和条件有效校准分开；这是项目benchmark配置，不是新实验或作者发布数据。

<!-- pandax-simplified-20261110:end -->

## 当前选定分析的专属基准

- [太阳⁸B单bin](solar_b8_singlebin_2601_19883/README.md)：独立总接受度与拟合信号。
- [CsI-time NSI坐标](COHERENT_CsI/CsI2021_time/nsi_20261108/README.md)：最新24点，不读取旧拟合输出。
- [CONUS+ SM/NSI](CONUS_Plus/conusplus_kkl_run1/README.md)：两种处理各自的论文基准与统计准备。

<!-- solar-nsi-v33:start -->

## 太阳⁸B NSI：v3.3（2026-11-12）

solar_b8_nsi_2601_19883是ee-only接触NSI输入，与太阳SM、轻媒介子和多bin资料分开。

[完整新onboarding：实际输入、标准引文、物理与程序](<../../docs/experiments/PandaX4T_XENONnT_SolarB8/singlebin_2601_19883/NSI_EE_VECTOR_ONBOARDING.v3.3.md>) · [独立NSI数据](<solar_b8_nsi_2601_19883/README.md>) · [实际结果与核对](<../../outputs/solar_b8_nsi/20261112_fig4_run2/README.md>)

<!-- solar-nsi-v33:end -->
