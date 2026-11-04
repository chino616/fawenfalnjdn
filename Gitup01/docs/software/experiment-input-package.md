# Experiment Input Package v1：格式、角色和校验合同

Status: CURRENT。Schema/语义验证、受控模型绑定、两文件 Loader 与默认 CsI2021 运行入口已实现。
数值范围与限制见[迁移报告](../CSI2021_PACKAGE_RUNTIME_MIGRATION_REPORT.md)；科学状态仍 DRAFT/PARTIAL。
Ar2020/CsI2017 使用同一 compiler 的 v2 输入和显式可执行 profile，见
[通用合同](onboarding-package-compiler.md)及[项目迁移](../PROJECT_WIDE_PACKAGE_MIGRATION_REPORT.md)。

正式文件固定为 `experiment.input.yaml`、`experiment.resources.npz`、
`experiment.physics.md`。YAML 管直接标量和模型规格，NPZ 管数组，MD 是机器输入的派生解释。

## 实际入口和解析格式

- [正式 JSON Schema](../../cevns_pyeft/experiments/input_package.schema.json)：
  Draft 2020-12，版本 `cevns-experiment-input/1`。
- [只读校验与渲染实现](../../cevns_pyeft/experiments/input_package.py)：
  不导入物理模块，不装配实验，不读取 workflow 文件。
- [命令行校验](../../tools/validate_experiment_input.py)：从明确 package 目录检查三文件。
- [CsI2021 Pilot 迁移适配](../../tools/csi2021_input_contract.py)：
  仅把 pilot/1 的真实数据注解成正式合同，不是通用 Onboarding 编译器。

`.yaml` 的正式编码为 **UTF-8、JSON-compatible YAML 1.2 子集**：必须使用严格 JSON
语法，拒绝注释、重复 key、NaN/Infinity、数值溢出、普通 YAML 简写和自定义 tag/object。
采用标准库解析，不依赖 PyYAML。结构验证沿用工作流 QA 已使用的 `jsonschema`；
从 Task 05 起为核心依赖，因为默认 package-backed Runtime 必须校验输入；`.[validation]` 保留兼容。

```powershell
python -B tools/validate_experiment_input.py --check-schema
python -B tools/validate_experiment_input.py data/experiments/COHERENT_CsI/CsI2021
```

命令只读且失败返回非零退出码。`schema_version` 与 `engine_compatibility` 独立；
引擎 API/组件合同版本符合声明不表示绑定、运行或科学验证已经执行。

## 参数角色和消费者

| role | 权威及消费规则 |
|---|---|
| direct_input | 直接输入；必须绑定已声明 model/slot/单位，附当前代码消费者证据。 |
| derived | 只读派生缓存；有有序 input_refs、受控 formula_id、依赖指纹及重算校验，不可独立编辑。 |
| materialized_derived_resource | 只用于数组；保存参数/模型/资源生成依赖和指纹。 |
| reference_only | 审计元数据，无计算消费者，不参与 canonical 数值指纹。 |
| unused_snapshot | 公共版本保留但当前没有数值消费者的快照，不得列为 active model 输入。 |
| runtime_control | 实际积分/采样/插值设置，显式单位、消费阶段与指纹范围。 |

`consumers` 包含 model_id、slot、runtime/resource_generation/derivation 阶段及代码证据。
模型的 `parameter_refs` 必须与反向消费者一一对应。旧程序经过整体代码或模型元数据
哈希产生的缓存失效，与 canonical 数值消费的作用范围分别记录。
静态 package_consumption_status 继续不承担执行证据；实际读取、模型调用和端到端证据由
BindingSession/测试产物分别记录。声明技术证据不授予人工科学批准。

CsI2021 的 105 项全部保留：65 direct_input、12 derived、12 runtime_control、
11 reference_only、5 unused_snapshot。五个未使用 LEC 为 Sigma_ud、L9、L10、m_u、m_d。
run_mass_metadata 是参考元数据；核素 Z/N/J/T 及单同位素分数是描述，当前数值链使用
已打包响应矩阵、A 和 b，而非再次消费这些描述量。

## 物化连续谱与只读靶推导

SNS NPZ 连续谱保留原数值，已经含 POT、yield 和几何稀释。
`normalization.runtime_authority=array`，运行期额外因子列表为空；重复施加任一已包含
因子会被拒绝。POT/yield/baseline 是生成输入，同时用于只读推导 prompt 线的 F。
两个分量的归一化来自同一组参数，不得对已归一化 continuum 再乘 F。

物化资源的 fingerprint 覆盖生成参数数值/单位、模型 revision、坐标资源哈希；修改
任一相关输入而未重新生成资源会触发 stale。派生量的 fingerprint 还保留输入顺序，
例如 Cs/I 的质量分数分子不同，不能因依赖集合相同而共用一个指纹。

质量分数、kg/GeV 单核质量、核数和源端点均通过声明输入重算校验。
校验器只支持明列的简单审计推导运算，不执行输入中的数学字符串。
这不是新的物理算法或 Runtime 数值路径。

## 模型、单位、坐标与扩展

数学文本及 symbolic_equations 一律 `audit_only`。可绑定规格由稳定 model_id、
revision、结构化 variable_units、输出单位、域/边界合同、归一化和参数/数组引用表达。
首批合同登记当前审计的 17 个模型。Schema 的 `x-model-contracts` 仅声明 slot 单位，
没有 module/callable，不授予任何模型运行能力；Task 03 再提供受控实现绑定。

未知关键字段默认拒绝。审计性扩展仅允许 `extensions` 的点分 namespace key，
如 `lab.review_note`；扩展不能注册执行代码或绕过必填合同。
新增物理模型要显式扩展受控合同和测试，不能通过字符串指定任意 Python 导入。

NPZ 每个数组必须有唯一稳定 key、数值 dtype、shape、单位、顺序轴、坐标引用、
归一化和内容哈希。实际回读以 allow_pickle=False 进行，检查 ZIP 成员双向对应、
重复成员、大小、dtype/shape、数值有限性、坐标单调性、标签长度与坐标单位。
128 MiB 压缩文件/512 MiB 解压内容的限制是当前 QA 读取器的内存边界；不是物理有效域。

## 能力、历史文件和 Physics MD

分别记录 legacy prediction、package-backed prediction、Fast、legacy approximate
statistics、official likelihood、general antineutrino EFT 和 scientific release。
旧回归证据、package Runtime 验证、科学验证和 human approval 是不同字段。
当前 official likelihood 保持 BLOCKED；绑定、Runtime、安装、旧回归及科学接受
分别按各任务报告的实际证据记录，不能由 Schema PASS 推断。

旧 `experiment.yaml` 继续供兼容 spec API 读取，状态为 legacy_compatibility。
新包 YAML/NPZ 是默认数值权威，Python definition 只做身份兼容适配。
旧 fast_validated/阶段标志保留为历史记录，不能升级成 package-only Fast PASS；
旧统计 provenance blocked 不等于没有可运行的近似 Gaussian。

Physics MD 必须由 YAML+NPZ 同源渲染，覆盖模型、公式、变量/单位、全部参数的意义和
角色、消费者、全部数组、来源、缺失及能力边界。任何数值修改后必须重渲染；
额外手写参数或数值漂移会使精确一致性检查失败。

Pilot 迁移由显式适配执行，原三文件及生成器在任务备份中保持字节级恢复点。
Task02 的历史范围没有改 NPZ 字节、105 项数值、理论/统计公式、Runtime 或其他数据集；
后续 Runtime 与全项目工程迁移的实际范围以对应新报告为准。

[软件说明](README.md) · [Task 02 报告](../EXPERIMENT_INPUT_SCHEMA_REPORT.md)
