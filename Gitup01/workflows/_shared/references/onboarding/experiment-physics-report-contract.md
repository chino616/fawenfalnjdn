# Experiment Physics MD 生成规范

<a id="report-toc"></a>

## 目录

- [1. 每个 dataset 生成两份文件](#section-1)
- [2. 实验专属内容：必须写完整](#section-2)
- [3. 共享物理模块：只记录选择](#section-3)
- [4. 精简版内容](#section-4)
- [5. 详细版内容顺序](#section-5)
- [6. Markdown 约定](#section-6)
- [7. 现有报告元数据入口](#section-7)
- [8. Onboarding 完成条件](#section-8)
- [9. 当前活动接口的兼容约定](#section-9)
- [10. 强制数据溯源与首次输出复查](#section-10)

<a id="section-1"></a>

## 1. 每个 dataset 生成两份文件

| 文件 | 用途 |
|---|---|
| `experiment.physics.summary.md` | 精简阅读版，快速说明实验、输入、模块选择、观测量、统计模型和主要限制 |
| `experiment.physics.md` | 详细实现版，供研究人员审阅，并使实现人员能够据此编写实验适配 |

两份文件由同一份实验输入生成。精简版不替代详细版。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-2"></a>

## 2. 实验专属内容：必须写完整

以下内容不能只列参数或模块 ID。

### Source
写出源分量、谱公式、谱线、归一化、POT/曝光、几何关系、味态/粒子标签，以及谱表节点、mask、插值、端点和归一化约定。说明每个公式的性质：理论衰变谱、衰变运动学、几何关系、实验归一化输入或数值处理。

### Target
写出靶材和核素组成、质量分数、靶质量、质量常数、核数计算公式及数值。

### Detector
每个实际使用的响应都必须给出完整数学定义、参数和单位、输入输出、定义域、边界/裁剪、归一化和施加顺序。只列 `Gamma`、`quenching` 或参数值不合格。

本章就地列出实际已取得的数据。每个公式符号标记“定义变量 / 有数值输入 / 项目推导 / MISSING”，并附数值、单位、本地文件、具体文献定位与核验范围。响应核缺失时，在该核对应行写 MISSING 并列出依赖它的计算。Qy、增益、涨落、选择、分箱、nuisance 与 covariance 各自登记。

### Observable
写出观测量、坐标、完整 bin edges、单位和边界约定。

### Prediction folding
说明 Source、Target、公共截面输出、Detector 和分箱如何组成实验预测；给出实验侧积分关系、单位和数值积分设置。不重复推导公共截面。

### Statistics
完整写出实验采用的 likelihood / χ² / deviance、逐 bin observed/background、误差或 covariance、nuisance、先验、相关性、profiling/marginalization 和 test statistic。数据语义不清时明确标记，不能猜测。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-3"></a>

## 3. 共享物理模块：只记录选择

以下内容属于项目共享模块，实验报告只记录实际选择的 model ID、必要配置和资源引用：

- Interaction theory：SM / NSI / Full EFT；
- Nuclear structure：Helm / Nuclear Response；
- Kinematics；
- Cross-section。

**Interaction 与 Nuclear structure 是两个独立选择维度。** 不要把它们合并成一个 Response 模块，也不要在每个实验报告中重写 EFT matching、Particle Response、Nuclear Response、Helm 或公共截面的理论公式。

只选择项目中实际存在的模块；组合是否可用由项目现有接口决定。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-4"></a>

## 4. 精简版内容

精简版只保留：
- 实验身份和数据范围；
- 关键 Source / Target / Detector 输入；
- 模块选择；
- Observable / Binning；
- Statistics 模型和主要限制；
- 指向详细版的链接。

不重复完整公式、逐 bin 数据和所有参数表。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-5"></a>

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

每条独立公式按正文顺序连续编号。公式后紧跟符号表，至少列出：符号、物理定义、单位、精确 Parameter ID 或 NPZ resource key；也可在符号表中引用文末唯一的参数索引。每个实际参数的值/单位必须就近附直接出处、原文定位与核验范围，公式本身注明出处或项目推导。数学常量/中间变量没有 Parameter ID 时可以标为 derived/constant，但物理常数仍须来源，中间数值须追到输入与推导。Parameter ID 不能代替来源。参数值在对应模块表中列一次，不要在多个章节重复抄录。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-6"></a>

## 6. Markdown 约定

本节同时约束人工编写和程序导出的报告。不能用编码、Schema 或文件链接检查通过，代替实际阅读与数学渲染验收。排版调整不改变物理数值、证据状态或科学批准。

### 6.1 编码、标题与阅读顺序

- 使用 UTF-8，无 BOM，换行统一为 LF；不得出现替换字符或意外控制字符。
- 每份文档只保留一个一级标题；正文按第 5 节的章节顺序，标题层级不跳级。
- 标题、正文、列表、表格、公式块和导航之间留空行；避免把长报告压成连续段落。
- 精简版与详细版在顶部互链，显示 Experiment/Dataset 身份和当前状态；缺失与限制保留，不为改善版面删除科学说明。

### 6.2 可点击目录与返回导航

- 详细版必须有可点击目录，覆盖全部主要章节；有三个及以上主要章节的用户资料或长说明也提供目录。
- 目录使用真实 Markdown 链接，不能只列普通文字。正文标题变化时同步更新目录。
- 锚点唯一且稳定；可用经过渲染验证的 ASCII 显式锚点，例如 `<a id="section-1"></a>` 与 `[实验范围](#section-1)`，或实际渲染器生成的标题锚点。不得假定任意中文 slug 或 HTML ID 一定可用。
- 目录自身应有锚点（例如 `report-toc`）；长文各主要章节末尾提供 `[返回目录](#report-toc)`。精简版可直接链接详细版对应章节，不强制增加重复的长目录。
- 交付前实际检查点击跳转，确认锚点存在、没有重名，并保留简洁的段落分隔；仅检查链接目标文件存在不够。

### 6.3 文件、来源与配置的导航

- 报告顶部提供有用入口：精简/详细版、用户资料、P00 来源、P01 证据、P02 缺失、P03 配置与 Benchmark 登记；目录主页可补充上级导航。
- 仅为实际存在的文件生成链接。暂缺文件写明缺失，不创建死链接或空白占位链接。
- 文档内部优先使用相对路径和有意义的链接文字；跨平台使用 `/`，路径含空格时使用 Markdown 尖括号目标或正确转义。
- 论文、官方资源与配置入口使用可点击的描述性标签，避免让读者复制长裸路径或裸 URL。链接标签需说明用途，不能把参考材料暗示为已批准输入。
- 同时核对正向导航、返回链接、实际文件目标和 `#anchor`。生成器与生成结果在同一任务更新，避免下次导出恢复旧格式。

### 6.4 数学公式、编号与符号表

- 行内公式使用 `$...$`。独立公式的起止 `$$` 必须各占一行，并与前后正文留空行；不得输出同一行的 `$$公式$$` 作为独立公式。
- 正确的独立公式形状如下；此代码块只展示 Markdown 写法，实际报告中的公式不得放进普通代码块：

````markdown
$$
N_i = \frac{M w_i}{M_i} N_{\mathrm A}. \tag{1}
$$
````

- `\tag{...}` 只出现在已被实际解析为 display math 的公式块中，公式编号按正文顺序连续。不能只为消除解析报错删除编号或修改公式正文。
- 不用 SVG 图片替代公式；保留可检索的 TeX 正文、紧跟的符号/单位/精确参数或资源映射表。
- Markdown 表格中的数学绝对值或条件竖线应使用能被当前解析器正确处理的写法，避免 `|` 被当成列分隔符；多行公式不塞进表格单元格。
- 使用实际 Markdown 数学节点解析与数学渲染器检查；UTF-8 正确不代表 TeX 可以渲染。新增依赖只进入明确的验证环境，不进入物理 Runtime。

### 6.5 表格与交付验收

- 表格用于平行字段或比较；保留单位、来源、状态和缺失语义。避免把整段报告、巨大 JSON 或完整数组挤进一个单元格，可链接 P01/P03 或数值文件。
- 参数和物理公式保持同源；排版修复后检查导出一致性，不能只手改派生 MD。
- 分别记录：编码检查、文件链接检查、锚点/点击检查、数学解析/渲染检查、窄视口下的表格与公式可读性，以及未覆盖的实际渲染器限制。
- 至少目视核对一个代表性的长详细版、目录跳转、返回导航、带编号公式和表格。发现红色公式源码、死目录或遮挡时，修复后再交付。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-7"></a>

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

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-8"></a>

## 8. Onboarding 完成条件

P03 可以保存尚未完成的候选，但只有本次 requested capability 所需的实验专属内容齐备，才可 handoff 给 Physical Implementation。未请求的能力可以保持 DRAFT/MISSING；阻断当前目标的缺失必须明确保留，不能把 PARTIAL 写成 READY。
终稿还必须满足[逐数据溯源验收](data-provenance-contract.md#section-5)；结构完整或有参考文献总表不代表每个数据已有依据。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-9"></a>

## 9. 当前活动接口的兼容约定

`models` 是以 model ID 为键的映射，不是列表。空白模板仅保留 `models: {}`；summary 和 calculation_steps 在 H3 有内容后再填，不能用空字符串/空列表冒充完成。

`group` 沿用现有枚举：source、target、theory、nuclear、kinematics、detector、prediction、statistics。theory 表示 Interaction，nuclear 表示独立的 Nuclear Structure；四个公共模块的必要选择记录在详细版第 4 节。

公式符号的 `parameter_ref` 可以精确指向参数 ID 或 NPZ key，单位由对应声明校验；数学常量/中间量为 null。旧包没有 lab.physics_report 时，沿用已注册合同的显式只读报告视图，两份报告使用同一输入；不回写旧 YAML。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->

<a id="section-10"></a>

## 10. 强制数据溯源与首次输出复查

本规范和所有 exporter 执行[数据溯源与补充闭环](data-provenance-contract.md)。
详细版中每个实际采用的数值/数组/公式/处理规则必须就近显示具体出处或推导/决定，不能仅列字段名或文末书目。
引用采用标准文献格式，并明确直接材料、上游原文和实际数字核验范围；表格/数组按精确行列或 key/slice 覆盖。

每个实验专属章节执行[同节来源和数值展示规则](data-provenance-contract.md#section-4)。该章的标准参考文献须能直接核对表内各项，标量和小型逐箱数据在正文给出，大数组给出完整文件链接、shape、全部轴范围和代表性切片。来源/配置记录、生成器和详细版、精简版、用户资料在同次修订生成。篇末增加下一步输入交接表。

首次输出标为草稿，正文与回复均说明已有数据、缺失数据/溯源和影响，并针对缺口与用户交互；
补充后更新同源记录及生成器，重生成受影响输出，再报告剩余问题。精简版必须保留主要缺口和来源入口。
尚未取得的原文数字、未经确认的二手来源与未审阅的近似不得被格式通过或用户确认配置掩盖。

当前生成器的结构/引用/一致性检查不自动认证上述事实；终稿逐数据验收由执行者与既有人类审阅负责。
旧报告不自动符合本版规则；来源输出不足时保留为候选，不能直接改名为已完成终稿。

共享模块的实际数值资源按[数值资源溯源要求](data-provenance-contract.md#module-numerical-provenance)展示。核响应选择旁必须有实际核素/通道数组、阶数或网格、基底/单位/归一化、代表值和完整文件链接。数值取得、直接材料核验、上游对应、转换等价和适用性分别标注；原文或转换链待核时，该限制必须传递到下游预测与 benchmark。

<!-- report-backlink:start -->
[返回目录](#report-toc)
<!-- report-backlink:end -->
