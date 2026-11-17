# 太阳⁸B电子味矢量NSI：独立参数与传播输入

[nsi.input.json](nsi.input.json)拥有标准引文、原文公式位置、实际数值/范围、处理选择与哈希。[fitted_yields.json](fitted_yields.json)使用2601 p20 Eq88精确百分比误差及三个独立12% pull。

主传播输入：[GS98派生profile](solar_b16_gs98_profile.txt)；模型敏感性：[AGSS09派生profile](solar_b16_agss09_profile.txt)。列为r/Rsun、ne/N_A、nn/N_A（mol/cm³）、⁸B产生区profile（归一化前）；实际原始分发表保留在同目录，文件名和哈希见card。

电子密度和产生区来自固定PEANUTS版本；质量密度来自固定Magnus分发表（明确是二手转录）。nn由rho_mass*N_A-ne推导，采用每重子1u近似，不冒充原文提供的中子表；原作者结构表官网本轮不可直接取得。

复用旧单bin源谱/天然Xe/效率的固定文件；不改其原卡，不读多bin数据。核响应仍按已选本地表约定。配置生成器：[prepare_solar_b8_nsi.py](../../../tools/prepare_solar_b8_nsi.py)。
