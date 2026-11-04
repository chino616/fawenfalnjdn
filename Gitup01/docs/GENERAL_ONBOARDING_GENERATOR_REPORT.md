# Task 08 — General Onboarding Package Generator

2026-11-04；branch `refactor/07-gitup01-20261104`；HEAD
`520e1d0a33913a6793b326ed493f5b66e0004a0a`。既有修改保留，不提交、不覆盖用户三份候选文件。
已读Task08/规则/顺序、Schema/validator、模型绑定、Loader、当前Onboarding/Master/Workflow。

新增 [通用编译器](../cevns_pyeft/experiments/package_compiler.py)、
[v2验证/渲染](../cevns_pyeft/experiments/generic_input.py)、
[v2 Schema](../cevns_pyeft/experiments/generic_input.schema.json)、
[组件合同](../cevns_pyeft/experiments/component_bindings.json)、
[CLI](../tools/compile_experiment_package.py)、[synthetic fixtures](../tests/helpers/onboarding_drafts.py)
及[测试](../tests/test_package_compiler.py)。既有input_package分派v1/v2，pyproject登记JSON资源。
正式v1保留兼容，v2消除原Pilot的固定字段/模型集合/观测布局，不改当前CsI2021数值。

IR `cevns-onboarding-draft/1` 的document是唯一参数数据库；获取方式human/ai/mixed只记录流程。
模型spec保留公式、变量/单位、输入输出合同、依赖和来源；数组显式声明轴、单位、归一化与哈希。
数学文本不执行；新模型只有受控注册后才能绑定，SPECIFICATION_ONLY不获运行能力。
新deterministic-PE/observed-Gaussian profiles实跑前保持BOUND_UNVERIFIED，Task10负责数值验收。

确定性编译：按key排序、ZIP固定时间、保留原shape/dtype/精度、SHA256、strict JSON-compatible YAML、
同源Physics MD；没有CsI路径/参数默认值。105参数和全部公式/数组在v1fixture中仍完整渲染。
编译器不会自动取得任意论文事实；缺失null、冲突、来源状态与能力阻断原样保留。

实际命令：`python -B -m pytest tests/test_package_compiler.py tests/test_input_package_schema.py -q`，
解释器`F:/Work/.codex_conda_envs/codex-py311/python.exe`：**56 passed**。
包括不同dataset/value、tabulated curve、missing/conflict、来源/role/单位/循环/任意公式/
不安全dtype/隐式精度转换拒绝；重复编译字节一致；只读check、create-only和显式覆盖备份。
初次v1 fixture测试发现重新结合派生浮点算式造成指纹变化；保留已通过相同1e-14核验的缓存表示，
仍拒绝真实上游改变的stale物化数组。没有降低验证容差。

Master/Onboarding Skill及Workflow增补资料获取→同一IR→确定性编译→人工审查→独立Machine Gate→
Runtime交接；步骤不堆入Master。文档/owning README/skill library同步与检查结果在本报告追加。
恢复点backup/task08-generator-20261104逐文件字节复制并登记。算法未改，三文件生成本身不授予
人工科学接受、激活或发布。下一步Task09把三文件纳入已有生命周期与分发。

Skill库生成器实际运行结果UNCHANGED。十份文档157个本地链接检查发现4个并行写入的新run
报告引用尚无目标文件；均非本任务新链接。未记文档全局PASS，Task09最终导航核对时再处理。

[合同用法](software/onboarding-package-compiler.md) · [进度](ONBOARDING_TASKS_02_10_PROGRESS.md)
