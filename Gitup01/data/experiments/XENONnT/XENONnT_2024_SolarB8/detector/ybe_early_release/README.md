# 早期官方YBe光/电荷产额原始数值

XENON COLLABORATION. XENONnT light-WIMP data release[DS/OL]. GitHub固定提交 `a09cd8fd77570dc2095f65f094fbcc114b634dfc`[2026-11-06]. 关联论文：APRILE E, et al. First Search for Light Dark Matter in the Neutrino Fog with XENONnT[J]. Physical Review Letters, 2025, 134: 111802. DOI: [10.1103/PhysRevLett.134.111802](https://doi.org/10.1103/PhysRevLett.134.111802). arXiv:2409.17868. 发布README指定DOI [10.5281/zenodo.14522706](https://doi.org/10.5281/zenodo.14522706)，本地实际核验GitHub ZIP而非Zenodo附件。

六文件逐字节复制，保留501个能量节点及原map值。coordinate_system为keVnr，Ly map为photon/keVnr，Qy map为electron/keVnr；存储域约0.3–10keV。lower/median/upper对应该发布的t=−1/0/+1曲线，不是逐能量独立误差。reader仅在0.51–5keV构建重铸信号；0.5keV以下不直接采用非零JSON曲线。与2024太阳CEvNS原分析的精确等价性独立待核。

| 原件 | 固定官方来源及定位 | 单位 |
|---|---|---|
| [ly_ybe_model_lower.json](<ly_ybe_model_lower.json>) | [固定发布原件](https://github.com/XENONnT/light_wimp_data_release/blob/a09cd8fd77570dc2095f65f094fbcc114b634dfc/light_wimp_data_release/data/signal/ly_ybe_model_lower.json)；data/signal/ly_ybe_model_lower.json | coordinate_system keVnr; map photon/keVnr |
| [ly_ybe_model_median.json](<ly_ybe_model_median.json>) | [固定发布原件](https://github.com/XENONnT/light_wimp_data_release/blob/a09cd8fd77570dc2095f65f094fbcc114b634dfc/light_wimp_data_release/data/signal/ly_ybe_model_median.json)；data/signal/ly_ybe_model_median.json | coordinate_system keVnr; map photon/keVnr |
| [ly_ybe_model_upper.json](<ly_ybe_model_upper.json>) | [固定发布原件](https://github.com/XENONnT/light_wimp_data_release/blob/a09cd8fd77570dc2095f65f094fbcc114b634dfc/light_wimp_data_release/data/signal/ly_ybe_model_upper.json)；data/signal/ly_ybe_model_upper.json | coordinate_system keVnr; map photon/keVnr |
| [qy_ybe_model_lower.json](<qy_ybe_model_lower.json>) | [固定发布原件](https://github.com/XENONnT/light_wimp_data_release/blob/a09cd8fd77570dc2095f65f094fbcc114b634dfc/light_wimp_data_release/data/signal/qy_ybe_model_lower.json)；data/signal/qy_ybe_model_lower.json | coordinate_system keVnr; map electron/keVnr |
| [qy_ybe_model_median.json](<qy_ybe_model_median.json>) | [固定发布原件](https://github.com/XENONnT/light_wimp_data_release/blob/a09cd8fd77570dc2095f65f094fbcc114b634dfc/light_wimp_data_release/data/signal/qy_ybe_model_median.json)；data/signal/qy_ybe_model_median.json | coordinate_system keVnr; map electron/keVnr |
| [qy_ybe_model_upper.json](<qy_ybe_model_upper.json>) | [固定发布原件](https://github.com/XENONnT/light_wimp_data_release/blob/a09cd8fd77570dc2095f65f094fbcc114b634dfc/light_wimp_data_release/data/signal/qy_ybe_model_upper.json)；data/signal/qy_ybe_model_upper.json | coordinate_system keVnr; map electron/keVnr |

[标准参考文献[17]](<../../../../../../docs/experiments/PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.1.md>) · [逐文件处理与ZIP指纹](<../../../../../../../重构/20261106_Onboarding_provenance_revision/EARLY_RESPONSE_EXTRACTION.json>) · [全部实验数值及来源](<../../README.md>)
