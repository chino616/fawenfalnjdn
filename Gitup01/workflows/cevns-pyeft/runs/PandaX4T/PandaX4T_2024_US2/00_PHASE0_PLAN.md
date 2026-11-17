# 太阳8B SM前向计算：Phase 0

2026-11-07。用户授权并入主项目并按已有流程计算SM事件谱；结果尚未经用户验收。

| 组件 | 判断 | 实际调用与证据 |
|---|---|---|
| 输入包与运行入口 | REUSE / ADAPTER | v2 Compiler → load_experiment_package → predict_experiment；增加显式solar profile，不复制旧实验参数 |
| Source / Target | CONFIG_ONLY / ADAPTER | Bahcall中心谱、天然Xe九核素、P00/P01；通量×有效秒数×1t核数等价于总质量时间，不声称1t是实测质量 |
| SM / 核运动学 | SHARED_EXTENSION / REUSE | 文献[1]式(1)–(3)树级SM与KN；复用ElasticKinematics、项目常量；不调用Fig.4 EFT系数 |
| Detector | ADAPTER / BLOCKED | XENONnT单能基底在(E,Ly,Qy)插值，边际化三观测轴；PandaX仅真实反冲接受度诊断，电子数谱BLOCKED |
| Slow积分 | REUSE | rates.recoil.integrate_recoil_yield、probability_fold；原样保留每run/核素分量与单位 |
| Fast / Statistics | NOT_REQUESTED | 本轮只做SM前向事件谱与参考谱比较，未请求拟合或扫描 |

## 预定检验

通量/曝光线性缩放、响应概率和≤1、核素/run分量和、分别加密Eν与T。
数值收敛容差逐箱max(2e-4 events, 0.2%)；原模型与公开重铸残差分别报告，不用重标定通过。
外部谱只作对照，不作为重新定义SM输出的输入。保留文献版本、参数点、图、数组和指纹。
加入共享模型后运行现有CsI2017/CsI2021/Ar2020相关回归。

## 授权、范围与恢复

D0001与W0001记录用户原话。只新增solar包、适配器、SM模型、阶段/benchmark记录并维护直接消费者。
旧15份核心onboarding与原数值表保留；已有实验公式、参考数组和容差不改。修改前备份见BACKUP_MANIFEST。
正式科学验收与默认全局激活不由数值PASS替代，结果阶段保留NOT_REVIEWED。
