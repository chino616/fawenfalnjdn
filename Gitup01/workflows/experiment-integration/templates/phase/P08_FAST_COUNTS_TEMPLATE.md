# P08｜Fast representation（可选）：可填写模板

对应 [cevns-fast-counts Skill](../../skills/cevns-fast-counts/SKILL.md)。没有 P07 Machine PASS 与 Human Slow Freeze 时，不填写实施结果，只记录“前置条件阻断”。**每种 Fast 表示单独复制一份**，不可把不同加速对象合并成一个含糊的“Fast”。builder、flavor 重建和缓存条件见 [P08 Fast 代码参考](P08_FAST_COUNTS_CODE_REFERENCE.md)。

## A. 用户填写：需要加速什么

| 字段 | 请填写 |
| --- | --- |
| dataset_id；P07 已批准的 Slow 版本与路径 | ____；____ |
| 加速场景 | 扫描哪些参数 ____；预计调用次数 ____；慢操作瓶颈 ____ |
| 选择表示 | □ reconstructed_spectrum_cumulative □ detector_response_matrix □ eft_quadratic_coefficient_kernel □ other_surrogate（数学定义）____ |
| 参数有效域 | 系数/靶/源/探测器/能量范围 ____；是否包含复系数与 flavor 混合 ____ |
| 精度要求 | 逐 bin 绝对容差 ____；相对容差 ____；接近零的 bin 如何判断 ____ |
| 性能目标 | 构建时间预算 ____；单次评价时间目标 ____；缓存存储限制 ____ |
| 需要保留的分量 | 源、flavor、同位素、探测器和 bin 轴 ____ |

## B. AI 填写：数学与缓存契约

| 必须记录 | 本次填写 |
| --- | --- |
| Fast 具体避免的运算 | ____ |
| 构建输入与权威 Slow callable | 输入、版本、参数点、文件.symbol：____ |
| 缓存对象 | 数学定义 ____；轴次序/shape ____；单位 ____；元数据版本 ____ |
| 重建函数 | `fast_counts(parameters, cache) → counts[axes]`；文件.symbol/输入输出：____ |
| 缓存失效条件 | 源谱、flavor 状态、靶/Response、探测器、曝光、bin、理论基底、代码版本变化时：____ |
| EFT kernel 专项 | 完整 coefficient basis/order、linear/quadratic terms、复数约定、`ρ(Eν)` 是否可缓存：____ |
| 复用分类 | `REUSE / CONFIG_ONLY / ADAPTER / SHARED_EXTENSION / CORE_EXTENSION / BLOCKED`；依据和影响：____ |

缺 EFT basis mapping 时，只阻断 EFT kernel，不自动阻断其他 Fast 类型；不能生成 partial kernel 冒充完整表示。Fast 不能修改 Slow 物理输入或用全局比例重标定来通过比较。

## C. 逐箱对照与 Gate

| 参数点/分量/bin | Slow | Fast | 绝对差 | 相对差 | 容差 | PASS? |
| --- | --- | --- | --- | --- | --- | --- |
| ____ | ____ | ____ | ____ | ____ | ____ | ____ |

- [ ] 至少覆盖基准、非零参数、边界和适用时复系数/flavor 混合点；逐 bin 而非仅总数比较。
- [ ] 记录构建成本、评价成本、缓存失效测试和存储/加载一致性。
- Machine Gate P08（**本表示**）：`NOT_RUN / PASS / BLOCKED`；诊断路径：____。
- Human Gate（**本表示**）：`NOT_REVIEWED / APPROVED / REVISE / BLOCKED`；允许宣称的加速范围：____。

**CsI2021 结构参考**：`fast_kernel_csi2021.build_fast_kernel_csi2021` 与 `kernels.reconstruction.reconstruct_from_full_kernel_flavor` 展示 EFT kernel 的构建/重建职责。当前 builder 存在 SNS 分量、CsI/PE 和 dataset 约束；ν/反ν kernel 适用性审计也不能省略。

