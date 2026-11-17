# XENONnT 2024 Solar 8B — Onboarding 用户资料 v2.0（新版本）

**版本日期：2026-11-06；用户指定：Response 方法、补充数据、严格标准文献引用；旧版保持原位。**

[详细物理说明 v2](<experiment.physics.v2.md>) · [精简版 v2](<experiment.physics.summary.v2.md>) · [标准参考文献 v2](<../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md>) · [旧用户资料](<../../../../../../../.experiment-auto-runs/cevns-threephase-20261105-high01/snapshot/docs/experiments/XENONnT/datasets/XENONnT_SolarB8/EXPERIMENT_USER_INPUT.md>)

<a id="toc"></a>

- [实验身份与目标](#identity)
- [输入与出处](#inputs)
- [采用的方法](#method)
- [缺失与执行状态](#status)

<a id="identity"></a>

## 实验身份与目标

身份为 `XENONnT_2024_SolarB8`，文献 [[3]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-3) 的早期太阳 8B；以 [[1]](../../../PandaX4T_XENONnT_SolarB8/SOLAR_B8_RESPONSE_REFERENCES.v2.md#ref-1) 作物理结果比较。新版独立保存，既有旧版的更广范围不自动继承。数据身份与后续资源发布/响应校准版本分开标注。

[返回目录](#toc)

<a id="inputs"></a>

## 输入与出处

已收集：官网源谱形、NIST 组成、既有 Qy 与逐箱 D/B、更新版完整 Response/B 网格及各 run 4D D。数值、单位、定位和文件哈希见 [详细版第 9 节](<experiment.physics.v2.md>)；每条来源使用标准编号书目，具体版本保留，不将最后发表版本默认当作当年分析输入。

[返回目录](#toc)

<a id="method"></a>

## 采用的方法

完整概率 response 已由本轮用户明确指定。按 run 与天然同位素分别做真实反冲到观测箱的卷积，禁止把 Qy 均值变换当作完整 Response；不新增 c_i，不重复效率，不将 fitted B 当成独立 prefit 模板。

Interaction、Nuclear structure、Kinematics、Cross-section 与 Detector 的选择独立；现有模块是否支持所选实验的适配仍需验证，未虚构已注册 ID。详细版的式 (1)–(6) 为实验侧数学合同，共享理论不在此复制推导。

[返回目录](#toc)

<a id="status"></a>

## 缺失与执行状态

XENONnT：完整后续 Response 和 B 已能回读，2024 原版响应/后续校准追溯适用性尚未证明；run 曝光、响应支撑外贡献、nuisance prior/covariance 和官方推断校准仍需对应版本证据。

无需用户重复提供已经提取的数字或再次确认 Response/c_i 选择。这里的缺口是后续查证和实现的依赖条件，不是要求用户猜值。当前可审阅 v2 文档与数据；正式适配、拟合或科学复现尚未完成。共有 8 份旧 onboarding 文件的指纹在本次记录中固定，未修改旧版。

[返回目录](#toc)
