# P04/P05/P07/P10：原子核Response SM

D0004/W0004选择本地七核素核表；不改共享公式、旧数据或参考数组。

| 核对 | 实际记录 |
|---|---|
| 逐核素/通道与归一化 | [全部系数、M(0)、hash与外部来源边界](<../../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/NUCLEAR_INPUT_AUDIT.json>) |
| 振幅/截面 | [原逐能量共享API对照、绝对M收缩、端点与拒绝行为](<../../../../../../tests/test_solar_nuclear_response.py>) |
| 事例数和收敛 | [实际数值/独立T与E加密/通道闭合](<../../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/PandaX4T_2024_US2/RESULT.json>) |
| 当前说明 | [同节输入、标准引用、全部缺口](<../../../../../../docs/experiments/PandaX4T/datasets/PandaX4T_2024_US2/experiment.physics.v3.1.md>) |
| 检查结果 | [测试与文件保护](<../../../../../../outputs/solar_b8_sm/20261110_nuclear_response_run2/VALIDATION.json>) |
| 科学接受 | NOT_REVIEWED；不把局部机器PASS提升为完整天然Xe/原生统计/论文等价 |
