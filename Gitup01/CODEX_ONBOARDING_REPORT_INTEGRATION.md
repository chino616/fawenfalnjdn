# Codex 任务：简化并统一 Onboarding 与 Physics MD 生成

## 目标

在现有 `Gitup01` 主程序中，按本包的 Skill、模板和报告规范，完成两份 Physics MD 的生成：

- `experiment.physics.summary.md`：精简阅读版；
- `experiment.physics.md`：详细实现版。

详细版必须让实现人员在项目公共模块已经存在的前提下，能够据此编写实验适配部分。

## 1. 合并文件

将 ZIP 内 `Gitup01/` 按相对路径合并到主程序根目录。

Master Skill 和 Onboarding Skill 先比较当前版本，只合并本包的 H0–H3、模板入口和报告规则，保留其他已有流程。

Physics MD 唯一规范文件位于 `workflows/_shared/references/onboarding/experiment-physics-report-contract.md`；不要在 `docs/software/` 另建副本。

## 2. Onboarding

按 H0–H3 组织人类审阅：

- H0：确认实验、dataset、run/data release 和研究目标；
- H1：说明材料是什么、能支持什么、不能证明什么；
- H2：按 Source、Target、Interaction、Nuclear Structure、Detector、Observable、Statistics 整理证据；
- H3：确认实验输入、共享模块选择和统计模型。

P00–P03 使用本包模板。P00 是来源登记，P01 claims 引用 P00 的 `source_id`，P02 记录缺失/冲突，P03 保存确认后的配置和报告元数据。

H3 中分开记录 Interaction（SM/NSI/Full EFT）与 Nuclear Structure（Helm/Nuclear Response）。只选项目已有模块，不虚构 model ID。

## 3. Physics MD 内容

### 详细版必须完整写出的实验专属内容

- Source：各分量谱公式、谱线、归一化、POT/曝光、几何关系、味态、谱表生成、mask、插值、端点；
- Target：核素组成、质量分数、靶质量、质量常数、核数公式；
- Detector：每个实际使用响应函数的完整公式、参数、单位、输入输出、定义域、归一化、边界处理和施加顺序；
- Observable：观测量、完整 bin edges、单位和边界约定；
- Prediction folding：实验输入如何组合成分箱预测，以及实际数值积分设置；
- Statistics：完整统计公式、逐 bin 数据、背景、误差/covariance、nuisance、先验和 profiling。

每条实验专属公式连续编号，紧跟符号表；符号表必须给出单位及精确 Parameter ID / NPZ key。

### 共享模块只登记选择

Interaction、Nuclear Structure、Kinematics、Cross-section 只写本实验选择的 model ID、必要配置和资源引用。

不要复制公共 EFT matching、Particle Response、Nuclear Response、Helm 或公共截面理论公式。

## 4. 使用现有生成入口

只修改现有 Compiler / Renderer，不另建生成器。相关现有位置：

- CLI：`tools/compile_experiment_package.py`
- Compiler / Writer：`cevns_pyeft/experiments/package_compiler.py`，现有 `compile_draft` / `write_package`
- v1/v2 Physics renderer：`cevns_pyeft/experiments/input_package.py` 的 `render_physics`
- v2 委托入口：`cevns_pyeft/experiments/generic_input.py` 的 `render`

现有报告元数据入口：

```text
P03: sections.validation_claim.fields.physics_report.value
IR:  document.extensions["lab.physics_report"]
```

沿用现有 Schema 字段：
- report：`summary`, `calculation_steps`, `models`
- model：`group`, `content_class`, `title`, `explanation`, `equations`
- equation：`id`, `title`, `latex`, `symbols`
- symbol：`symbol`, `definition`, `unit`, `parameter_ref`

分类规则：
- `experiment_specific`：输出完整公式、参数和实验数据；
- `shared_framework`：只输出本实验选择的模块 ID/配置；
- `implementation_detail`：不输出。

当前 `--md-only` 只重渲染 `experiment.physics.md`。请沿用同一命令，使其只读现有 YAML/NPZ，从同一份 `lab.physics_report` 一次生成两份 MD；除这两份 MD 外，不写其他文件：

```text
experiment.physics.summary.md
experiment.physics.md
```

精简版只输出概要并链接详细版；详细版按报告规范完整展开。保留原有 CLI 参数和 Writer，不新建第二套 Renderer 或写入程序。

命令仍为：

```powershell
python -B tools/compile_experiment_package.py --output <dataset_dir> --md-only --overwrite
```

## 5. 修改边界

- 不处理 P04 及之后；
- 不修改 Runtime 物理算法；
- 不重新提取或改写现有实验 YAML/NPZ 数值；
- 不修改实验 manifest；
- 不改变现有 CLI 的其他用途；
- 文件写入沿用项目当前 Writer，不修改写入层；
- 不做全仓库重构。

完成后对 CsI2021 执行上述命令，交付两份 MD 和简短修改文件清单。

## 活动树接口核实

models 沿用当前 Schema 的 ID→模型记录映射；model ID 是键，不另加 id 字段。符号引用增加对精确 NPZ key 的校验。空模板不填空 summary/calculation_steps。本次只扩展既有输出文件映射，不改 Writer 的备份、ACL、替换或恢复原语。
