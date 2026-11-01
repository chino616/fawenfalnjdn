# 项目级操作说明

这是项目文档，未安装或覆盖任何 SKILL.md。
工程 M0–M7 不替代 `workflows/experiment-integration` 的 Physics Gate。

1. 从 catalog 识别准确 dataset_id 与 analysis_revision。实际变更真实实验时仍从项目 Master Skill 进入。
2. 使用 load_experiment(...,resources=...) 查看 describe，确认实际源、曝光、材料、观测轴、统计状态和资源哈希。
3. 区分实验设定与理论参数、数值参数。前者修改本实验不可变 definition 实例；后两者使用 TheoryPoint / numerics。
4. 修改前备份相关已有文件并登记 BACKUP_MANIFEST；不从 backup 发现或推导科学输入。
5. 检查能力矩阵，选用该实验已有策略；不以窄Gaussian代替CsI2017映射，不扩大统计适用性。
6. 修改源、质量、响应、阈值或分箱后检查物理核失效；只改统计输入时重评统计，不要求重编物理核。
7. 对所有受影响实验执行独立冻结基线与行为测试，报告实际误差、环境、失败和适用限制。
8. 添加新实验时只新增自己的 definition、必要组件、资源与catalog项。先用测试专用 synthetic 定义验证扩展合同；它不是新的真实实验身份。

用户已经授权的工程动作不重复申请；本工程记录不冒充正式 Human Physics Gate。
