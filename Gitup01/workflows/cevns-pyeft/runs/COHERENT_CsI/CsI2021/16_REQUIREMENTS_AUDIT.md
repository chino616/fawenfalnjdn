# 任务逐条验收

验收对象为 261194_CODEX_CSI2021_P04_P10_SKILL_EXECUTION.md 指定的既有 CsI2021 九箱执行审计。
从 P04 开始，P01–P03 继承用户给定输入；未重复 Onboarding。
各项状态的权威值在实际阶段报告的唯一 phase-result 中，下面是证据导航。

| 要求 | 实际处理 / 证据 | 边界 |
|---|---|---|
| 实际仓库、branch、HEAD、初始工作树 | baseline.json；00_EXECUTION_PLAN.md | publication worktree，未提交/推送 |
| Skill 驱动而非只读 README | Master、P04–P10 Skill、合同/模板/代码参考均已读取；七份报告沿现有 handoff | 不把机器检查当用户批准 |
| Phase 0 与 DAG | 00_IMPLEMENTATION_MANIFEST.yaml | P06 独立，P09 使用 Slow 不依赖 P08 |
| 三正式输入权威 | input_revision_2 原件、归档哈希、逐数组清单 | MD 派生，YAML 标量/模型、NPZ 数值 |
| 更新/不一致处理 | input_revision_3、bridge snapshot、concurrent_* 审计 | 不覆盖正式输入以匹配任务旧哈希 |
| 完整理论而非 M+c1 | P04_RESULTS 与 04_REPORT、full22 tests | 旧教学 core 仅在最后作受限比较 |
| 22 个 operator metadata/复 flavor | canonicalize 拒绝测试与全算符 Fast 比较 | 外部算符/反中微子科学审计仍缺失 |
| 14 个核响应重建 | y=0,.1,.5,1 对比、NPZ hashes、I127 残差 | 内部重建一致不等于外部源表认证 |
| P04→P05→P07 typed 对象 | 同一 PreparedExperiment 的 PackedInteraction/ResponseW/dsigma_dT | 不从旧 definition 重抄输入 |
| 动量、质量、单位与支撑 | P05_RESULTS、边界/非法值测试 | qabs² 与 signed q² 明确区分 |
| 探测器三部分责任 | P06_RESULTS、响应图、概率检查 | Gamma 密度归一为一，窗内概率不强归一 |
| 归一化一次 | normalization_and_binding.json；质量/注量倍增检查 | 源已含 POT、yield、geometry；核数一次 |
| 源×核素×bin 分解 | predictions/*.npz、P07 实际网格与真实谱诊断 | 真实谱诊断 small grid 明确标为未收敛 |
| Slow 独立积分及收敛 | 十种 profile、独立 E/T/重建轴、0.01+0.5% 判据 | 收敛状态以 P07_RESULTS 为准，不放宽容差 |
| Slow reference | P07 handoff 的精确参数/代码/输入/网格/hash | 技术候选与人工 Slow 接受分开 |
| Fast 每种能力独立 | P08 full22 工程比较、full/pair/save/load/stale | 正式 Fast 受人工冻结缺失限制；cumulative NOT_RUN |
| P09 近似模型复算 | Slow 预测、一次箱宽转换、独立 2×2、Asimov | 只计算 legacy approximate objective |
| 官方统计不被补造 | P09/P10 explicit BLOCKED | 无官方 covariance、likelihood、CL、区间或限制 |
| 指纹/缓存失效 | 包/实现 freshness、统计物理分离、实际替换测试 | 长积分第一次因上游变化被正确拒收 |
| 外部 cwd、无 legacy fallback | package-only import/open guards、wheel-01/02 | 使用明确版本，不能跨指纹加载候选核 |
| Runtime/catalog/packaging | custom catalog、显式 adapter、wheel 数据文件 | 当前同期 default Loader 迁移单列 |
| removal/recovery/其他实验 | 固定版本真实拆装/重装/回滚；当前 127 回归记录 | 当前三项失败保留，不声称全局发布 PASS |
| 最小改动/备份/回滚 | 15_CHANGE_AND_ROLLBACK.md、change manifest | 不回滚或覆盖其他工作产生的变化 |
| README、导航与真实消费者 | readme_sync_manifest、managed inventory、链接检查 | 原手写说明保留，新增报告为 run artifact 非 Skill |
| 七份报告的标准 schema | validate_phase_contract，实际 artifacts SHA256 | 校验只认证结构/文件内容 |
| 物理/冻结参考保护 | unchanged_physics_proof.json | theory、nuclear、frozen reference 字节未变 |
| 失败/未执行准确分类 | JUnit 原件、test_results_summary、能力矩阵 | 测试组重叠不求和、环境错误不计 PASS |
| 最终 ZIP | manifest、文件 SHA256、ZIP 完整性与解包复现 | 不含整仓库/venv/cache/隔离构建或测试树 |

这些要求的工程产物均可检查。外部来源、人工科学接受和当前兼容失败本身仍是未满足的科学/发布条件；
保留 BLOCKED 是本次审计结论，不写成“P04–P10 所有科学能力全部通过”。
