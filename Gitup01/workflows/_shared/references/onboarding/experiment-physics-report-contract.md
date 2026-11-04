# Experiment Physics MD 生成规范

## 1. 每个 dataset 生成两份文件

| 文件 | 用途 |
|---|---|
| `experiment.physics.summary.md` | 精简阅读版，快速说明实验、输入、模块选择、观测量、统计模型和主要限制 |
| `experiment.physics.md` | 详细实现版，供研究人员审阅，并使实现人员能够据此编写实验适配 |

两份文件由同一份实验输入生成。精简版不替代详细版。

## 2. 实验专属内容：必须写完整

以下内容不能只列参数或模块 ID。

### Source
写出源分量、谱公式、谱线、归一化、POT/曝光、几何关系、味态/粒子标签，以及谱表节点、mask、插值、端点和归一化约定。说明每个公式的性质：理论衰变谱、衰变运动学、几何关系、实验归一化输入或数值处理。

### Target
写出靶材和核素组成、质量分数、靶质量、质量常数、核数计算公式及数值。

### Detector
每个实际使用的响应都必须给出完整数学定义、参数和单位、输入输出、定义域、边界/裁剪、归一化和施加顺序。只列 `Gamma`、`quenching` 或参数值不合格。

### Observable
写出观测量、坐标、完整 bin edges、单位和边界约定。

### Prediction folding
说明 Source、Target、公共截面输出、Detector 和分箱如何组成实验预测；给出实验侧积分关系、单位和数值积分设置。不重复推导公共截面。

### Statistics
完整写出实验采用的 likelihood / χ² / deviance、逐 bin observed/background、误差或 covariance、nuisance、先验、相关性、profiling/marginalization 和 test statistic。数据语义不清时明确标记，不能猜测。

## 3. 共享物理模块：只记录选择

以下内容属于项目共享模块，实验报告只记录实际选择的 model ID、必要配置和资源引用：

- Interaction theory：SM / NSI / Full EFT；
- Nuclear structure：Helm / Nuclear Response；
- Kinematics；
- Cross-section。

**Interaction 与 Nuclear structure 是两个独立选择维度。** 不要把它们合并成一个 Response 模块，也不要在每个实验报告中重写 EFT matching、Particle Response、Nuclear Response、Helm 或公共截面的理论公式。

只选择项目中实际存在的模块；组合是否可用由项目现有接口决定。

## 4. 精简版内容

精简版只保留：
- 实验身份和数据范围；
- 关键 Source / Target / Detector 输入；
- 模块选择；
- Observable / Binning；
- Statistics 模型和主要限制；
- 指向详细版的链接。

不重复完整公式、逐 bin 数据和所有参数表。

## 5. 详细版内容顺序

```text
# <Experiment> — <Dataset>
## 目录
## 1. 实验范围
## 2. Source
## 3. Target
## 4. 本实验选择的共享模块
## 5. Detector
## 6. Observable
## 7. Prediction folding
## 8. Statistics
## 9. 数值资源
## 10. 来源、限制与状态
```

每条独立公式按正文顺序连续编号。公式后紧跟符号表，至少列出：符号、物理定义、单位、精确 Parameter ID 或 NPZ resource key；也可在符号表中引用文末唯一的参数索引。数学常量/中间变量没有 Parameter ID 时明确标为 derived/constant。参数值在对应模块表中列一次，不要在多个章节重复抄录。

## 6. Markdown 约定

- UTF-8，无 BOM。
- 行内公式 `$...$`，独立公式 `$$...$$`。
- 不用 SVG，不把公式放进普通代码块。
- 公式编号按正文顺序。
- 保留正常 Markdown 表格和目录链接。


## 7. 现有报告元数据入口

沿用现有 P03 v4，不增加新的顶层 section。报告元数据写在：

```yaml
sections:
  validation_claim:
    fields:
      physics_report:
        value:
          models: {}
```

现有整理步骤将其映射到：

```python
document.extensions["lab.physics_report"]
```

结构只使用现有报告 Schema 接受的字段：

- report：`summary`, `calculation_steps`, `models`
- model（以稳定 model ID 为键的映射；不在值中再写 id）：`group`, `content_class`, `title`, `explanation`, `equations`
- equation：`id`, `title`, `latex`, `symbols`
- symbol：`symbol`, `definition`, `unit`, `parameter_ref`

`content_class`：
- `experiment_specific`：Source、Target、Detector、Observable、Prediction folding、Statistics；完整输出。
- `shared_framework`：Interaction、Nuclear Structure、Kinematics、Cross-section；只输出所选 model ID/必要配置。
- `implementation_detail`：不进入实验正文。

符号的 `parameter_ref` 必须精确对应 YAML Parameter ID 或 NPZ key；数学常量和推导中间量使用 `null`，不得用模糊字符串匹配。


## 8. Onboarding 完成条件

P03 可以保存尚未完成的候选，但只有本次 requested capability 所需的实验专属内容齐备，才可 handoff 给 Physical Implementation。未请求的能力可以保持 DRAFT/MISSING；阻断当前目标的缺失必须明确保留，不能把 PARTIAL 写成 READY。

## 9. 当前活动接口的兼容约定

`models` 是以 model ID 为键的映射，不是列表。空白模板仅保留 `models: {}`；summary 和 calculation_steps 在 H3 有内容后再填，不能用空字符串/空列表冒充完成。

`group` 沿用现有枚举：source、target、theory、nuclear、kinematics、detector、prediction、statistics。theory 表示 Interaction，nuclear 表示独立的 Nuclear Structure；四个公共模块的必要选择记录在详细版第 4 节。

公式符号的 `parameter_ref` 可以精确指向参数 ID 或 NPZ key，单位由对应声明校验；数学常量/中间量为 null。旧包没有 lab.physics_report 时，沿用已注册合同的显式只读报告视图，两份报告使用同一输入；不回写旧 YAML。
