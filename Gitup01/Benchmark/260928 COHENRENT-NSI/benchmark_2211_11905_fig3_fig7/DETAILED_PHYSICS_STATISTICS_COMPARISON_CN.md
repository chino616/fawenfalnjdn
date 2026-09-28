# arXiv:2211.11905v2 Fig. 3–7：CEvNS-pyEFT Flavor 数值复现的物理、统计与绘图对照规范

> **文档定位**：这是一个交给本地编程代理/研究者执行的 benchmark specification，而不是已完成复现的报告。每一步都要说明「论文计算什么」「本程序计算什么」「共同可比对象是什么」「什么差异不应被掩盖」。
>
> **资料状态（2026-09-28）**：已核对 De Romeri et al., *Physics implications of a combined analysis of COHERENT CsI and LAr data*, JHEP 04 (2023) 035 的公开正文及 Fig. 3–7 图注；本会话可读取先前上传的 `coherent_flavor_highres_grid101_lowres_summary.pdf` 和此前绘图工具包。用户 Windows 上 `F:/.../2211.11905v2.pdf` 与指定分支 `Gitup01` 的完整源码没有挂载到当前工作环境，**故下面对“本程序当前已有”仅限已经提供的旧汇总证明的内容，其余标为“待源码审计/待移植”，不可伪称已验证该分支的具体函数**。执行前应以用户的 *v2 PDF* 核验页码与方程编号；这里按可访问的 JHEP 正文编号引用。论文正式版和本地 v2 的排版页码不得无检查地互换。

**论文**：https://arxiv.org/abs/2211.11905 ，指定版本 https://arxiv.org/pdf/2211.11905v2 ；公开全文交叉核对 https://www.researchgate.net/publication/369914924_Physics_implications_of_a_combined_analysis_of_COHERENT_CsI_and_LAr_data ；DOI https://doi.org/10.1007/JHEP04(2023)035 。

**待对接的代码分支**：https://github.com/chino616/fawenfalnjdn/tree/flavor-v7-statistic-chi2-20260924/Gitup01 。上述 GitHub 链接指定比较对象，但仅有链接并不能证明 API、数据、likelihood 或 NGI 算子已实现。

---

## 0. 这个对比究竟在比较什么（必须写在最终图注/结果报告开头）

一个二维 NSI benchmark 不是简单地比较两个图像；被比较的对象是**在相同物理假设和实验输入下，每一个新物理参数点对应的 profile-likelihood test statistic**：

\[
 (\epsilon_x,\epsilon_y)
 \longrightarrow \frac{d\sigma_{\nu_\alpha N}}{dT}
 \longrightarrow S_{ij}(\epsilon_x,\epsilon_y)
 \longrightarrow \min_{\eta_D}\chi_D^2(\epsilon_x,\epsilon_y,\eta_D)
 \longrightarrow \Delta\chi_D^2
 \longrightarrow \{\Delta\chi_D^2\le 4.605\}.
\]

论文及本程序的真正共同输出应是同一组 `CsI2021 / LAr2020 / CsI2021+LAr2020` 的每点 **predicted signal+background、profiled χ²、Δχ² 和 90% CL contour**。其中“理论核/fast kernel 数值一致”仅证明积分路径相互一致，**不等于**与论文数据似然一致；“原图 vs 复现图”是最终展示而非核心数值判据。

必须把以下三种比较分别标在图上：

| 层级 | 共同可比物 | 论文一侧 | 我们一侧 | 可以得出的结论 |
|---|---|---|---|---|
| A 物理模型 | 给定同一靶核、味和耦合的 \(d\sigma/dT\) | Eqs. (2.1)–(2.3)、(2.5)–(2.6)、Fig. 7 的 (2.7)–(2.11) | Flavor/Wilson 矩阵 + 核响应/EFT 截面；**逐函数待审计** | 验证 convention 和散射振幅/干涉结构 |
| B 实验预测 | 指定 bins 的 \(S_{ij}\) 和 SM baseline | Eqs. (3.1)–(3.8) 的 SNS 通量、Cs/I/Ar、QF、分辨率、效率、时间分布 | 现有 detector models / fast kernels；旧 PDF 证明 fast-vs-slow 接近，但**不能证明使用论文相同响应** | 验证事件数预测；量化响应差异 |
| C 统计推断 | nuisance-profiled raw \(\chi^2\)、\(\Delta\chi^2\)、contour | CsI: Eq. (3.9)+(3.11)，LAr: Eq. (3.12)–(3.13) | 分支 statistical likelihood，**须逐项审计**；旧 PDF 明标 `legacy approximate statistics` | 验证正式 Fig. 3–7，若不一致先定位 likelihood 而非改动物理核 |

**最终不可混淆的两个结果系列**：`paper-matched`（方程、实验输入、nuisance 尽可能与论文逐项匹配）与 `native-program`（保留 CEvNS-pyEFT 本身物理/统计默认）。两者都可以画；只有前者可称“论文数值复现”。若相同的物理但不同的统计实现，标签必须是“physics-equivalent / likelihood-different comparison”。

---

## 1. 必须先冻结的理论和实验定义

### 1.1 论文 SM CEνNS 截面：什么被计算

论文 §2.1 Eq. (2.1)–(2.3) 采用的（无轻子末态探测）SM 核反冲公式为

\[
\frac{d\sigma_{\rm SM}}{dT}
=\frac{G_F^2 M_N}{\pi}\,[Q_V^{\rm SM}]^2
 F_W^2(q^2)\left(1-\frac{M_NT}{2E_\nu^2}\right),
\quad Q_V^{\rm SM}=g_V^p Z+g_V^n N,
\]

\[
g_V^p=\tfrac12-2\sin^2\theta_W,\quad g_V^n=-\tfrac12,\quad q^2\simeq2M_NT.
\]

论文使用 \(\sin^2\theta_W=0.23857\) 和 Klein–Nystrand (KN) 参数化：

\[
F_W(q^2)=\frac{3j_1(qR_A)}{qR_A}\frac{1}{1+q^2 a_k^2},\quad
R_A=1.23A^{1/3}\,{\rm fm},\quad a_k=0.7\,{\rm fm}.
\]

该论文把 \(F_p\simeq F_n\equiv F_W\) 作为近似；在扫描 Fig. 3–7 时应先使用**同一 KN 定义和单位转换**，再额外给出 CEvNS-pyEFT 自有 form-factor 选择造成的理论差异。绝不能把 Helm 与 KN 的差异归因于 flavor 实现。注意同名 \(R_A\) 不等于可以直接当作 Helm 半径或另一个库的 neutron RMS 参数。

### 1.2 论文 vector NSI 与 CEvNS-pyEFT Flavor/Wilson 的共同物理量

论文 §2.2 Eq. (2.5)：

\[
{\cal L}_{\rm NSI}^{\rm NC}
=-2\sqrt2G_F\sum_{q=u,d}\sum_{\alpha\beta}\sum_{X=L,R}
\epsilon_{\alpha\beta}^{qX}
(\bar\nu_\alpha\gamma_\mu P_L\nu_\beta)
(\bar q\gamma^\mu P_Xq),\qquad
\epsilon^{qV}=\epsilon^{qL}+\epsilon^{qR}.
\]

对一个入射 flavor \(\alpha\)，末态 flavor 不被测量，物理上需相加末态振幅的模平方：

\[
Q^{\alpha\beta}_N(q)=Q_V^{\rm SM}\delta_{\alpha\beta}
+(2Z+N)\epsilon^{uV}_{\alpha\beta}
+(Z+2N)\epsilon^{dV}_{\alpha\beta},\quad
\mathcal Q^2_{\alpha}=\sum_{\beta=e,\mu,\tau}|Q_N^{\beta\alpha}|^2.
\]

对于本 benchmark 的实数 Hermitian NSI，指标转置约定不影响结果；若将来检验复相位必须明确 \(Q_{\beta\alpha}\)、密度矩阵和反中微子共轭约定。对角项与 SM 干涉，非对角项不与 SM 干涉。切勿把带有相位的 flavor matrix 先求元素和再平方，也切勿让不同**不相干源 flavor**的通量相互振幅干涉。

**我们程序的拟对接方式**：将 \(\epsilon^{uV},\epsilon^{dV}\) 转换成 detector NP-only Wilson 矩阵，按源 flavor 分别计算三种 SNS 事件预测，再相加。此方式在旧的扫描 PDF 中已有描述；但分支真实转换系数/程序 API 尚待源码审计。若 detector 使用质子/中子系数：

\[
\epsilon^{pV}=2\epsilon^{uV}+\epsilon^{dV},\qquad
\epsilon^{nV}=\epsilon^{uV}+2\epsilon^{dV}.
\]

**不能未经检查就将论文 \(\epsilon\) 直接复制到 `c_p/c_n` 或 `c_iso`**。核验 Lagrangian 中 \(P_{L,R}\)、\((1-\gamma_5)\)、\(G_F/\sqrt2\)、SM/NP 拆分是否存在 2、4、\(\sqrt2\) 或符号差。对一个核种、一个源味、一个非零 \(\epsilon\) 逐点比较振幅和截面：\(\epsilon=0,\pm10^{-3},\pm10^{-2}\)，再检验全扫描。

如本程序按密度矩阵计算，定义一个源态 \(\rho_\alpha=|\alpha\rangle\langle\alpha|\)，并对末态迹化：

\[
\mathcal Q^2_\alpha={\rm Tr}\bigl[Q_N\rho_\alpha Q_N^\dagger\bigr].
\]

这与论文纯 flavor 源的末态求和等价；**本次不是**在比较太阳/长基线传播、MSW、振荡相位或源端新物理。SNS prompt \(\nu_\mu\)、delayed \(\bar\nu_\mu,\nu_e\) 是分别加权的 source channels，不能把本框架可能支持的通用 \(\rho\) 功能自动视为论文模型的一部分。

### 1.3 纵横坐标互换的实质影响

旧结果 PDF 采用横轴 \(\epsilon^{uV}\)、纵轴 \(\epsilon^{dV}\)；论文 Fig. 3 **横轴 \(\epsilon^{dV}\)、纵轴 \(\epsilon^{uV}\)**。不可直接叠加旧 PNG。核电荷不变近似下，相消条件：

\[
(2Z+N)\epsilon^{uV}+(Z+2N)\epsilon^{dV}=0.
\]

旧坐标的带斜率是 \(d\epsilon^{dV}/d\epsilon^{uV}=-(2Z+N)/(Z+2N)\)；论文坐标的带斜率应为 \(d\epsilon^{uV}/d\epsilon^{dV}=-(Z+2N)/(2Z+N)\)。这两个值互为倒数，**图的倾斜不同并不必然代表物理错误**。Cs 和 I 要分别计算，然后按靶原子事件数相加，而非用“平均 CsI 核”替代两个同位素；LAr 的 \(Z,N\) 则另有一组相消方向。

### 1.4 Fig. 7 NGI 不是 Fig. 3–6 的 NSI 参数重命名

论文 §2.3 Eq. (2.7)–(2.11) 给出 nucleon/nucleus 级的 scalar / vector / tensor 通道；其 Eq. (2.8) 为（符号和归一化按原文）：

\[
\frac{d\sigma_{\rm NGI}}{dT}=\frac{G_F^2 M_N}{4\pi}F_W^2(q^2)
\left[ C_S^2\frac{M_NT}{2E_\nu^2}
+(C_V+2Q_V^{\rm SM})^2\left(1-\frac{M_NT}{2E_\nu^2}-\frac{T}{E_\nu}\right)
+8 C_T^2\left(1-\frac{M_NT}{4E_\nu^2}-\frac{T}{E_\nu}\right)
\pm 2C_SC_T\frac{T}{E_\nu}\right].
\]

干涉号：**反中微子 `+`、中微子 `−`**。这意味着将所有 SNS 三种通量先加为“统一通量”再计算同一个 S–T 截面会出错。论文 nucleus 级的系数（Eqs. (2.9)–(2.11)）为：

\[
C_V=Z(2C_V^u+C_V^d)+N(C_V^u+2C_V^d),
\]
\[
C_S=Z\sum_{q=u,d}C_S^q\frac{m_p}{m_q}f_q^p+N\sum_{q=u,d}C_S^q\frac{m_n}{m_q}f_q^n,
\]
\[
C_T=Z\sum_{q=u,d}C_T^q\delta_q^p+N\sum_{q=u,d}C_T^q\delta_q^n,
\quad C_X^q=g_{\nu X}g_{qX}.
\]

论文给定 \(f_u^p=0.0208,f_u^n=0.0189,f_d^p=0.0411,f_d^n=0.0451\)，\(\delta_u^p=\delta_d^n=0.54\)，\(\delta_d^p=\delta_u^n=-0.23\)。Fig. 7 **假设 \(C_X^u=C_X^d=C_X^q\)**，一次只开 1 或 2 个 Lorentz 通道，其他设零。必须审计本项目的 scalar/tensor Wilson 与核矩阵元定义、核质量与夸克质量取值、sigma 张量 convention；如果没有这些实现，状态标为 **NGI not implemented**，不允许用 vector kernel 替代。

论文 NGI vector 的 SM 结构是 \((C_V+2Q_{\rm SM})^2\)；NSI 表述是 \((Q_{\rm SM}+\Delta Q)^2\)。仅在相关动量学近似和相同矢量约定下，振幅对齐条件是 \(C_V=2\Delta Q\)，即论文 universal vector 参数的数值一般**不可直接等同**于 \(\epsilon^{uV}=\epsilon^{dV}\)；还须注意 Eq. (2.8) 中的次阶 \(T/E_\nu\) 项。

---

## 2. 从截面到实验 bin：必须真正比对的物理积分

### 2.1 论文 CsI 事件率的计算链（§3.1, Eqs. (3.1)–(3.6)）

论文是将**真核反冲 \(T'\)** 的散射率卷积到**观测 photoelectrons/时间 \((i,j)\)**，分别计算 Cs 与 I：

\[
S^{A}_{i\alpha}=N_{\rm target}\int_{\mathrm{obs}\,i}dT\,\mathcal A_E(T)
\int dT'\,P(T,T')\int_{E_\nu^{\min}(T')}^{E_\nu^{\max}}dE_\nu
\,\Phi_\alpha(E_\nu)\frac{d\sigma_{\alpha A}(E_\nu,T')}{dT'},
\]
\[
S^{\rm CsI}_{ij}=\sum_{A=\rm Cs,I}\sum_{\alpha=\nu_\mu,\bar\nu_\mu,\nu_e}
S^{A}_{i\alpha}\int_{t_j}^{t_{j+1}}dt\,f_\alpha(t;\alpha_6)\mathcal A_T(t).
\]

- 论文的 SNS 三部分：prompt monoenergetic \(\nu_\mu\)（\(\pi^+\) DAR），delayed Michel \(\bar\nu_\mu\)、\(\nu_e\)；Eq. (3.2)。CsI: \(m_{\rm det}=14.6\,\mathrm{kg}\)、\(L=19.3\,\mathrm m\)、\(r=0.0848\) neutrinos/flavor/POT、\(N_{\rm POT}=3.198\times10^{23}\)。
- Eq. (3.3) 能量效率：\(\mathcal A_E=a/[1+e^{-b(x-c)}]+d\)，\(x=\mathrm{PE}+\alpha_7\)，\(a=1.32045,b=0.285979,c=10.8646,d=-0.333322\)。**需对照实际 PDF 的括号与 efficiency 数据文件**。
- Quenching/light yield：\(\mathrm{PE}=13.35\,\mathrm{PE/keV_{ee}}\times E_{er}\)；\(E_{er}(T')\) 论文采用四阶多项式参数，并用 Gamma resolution，Eq. (3.4)。多项式输入单位需依原始 COHERENT 数据 release/论文，而非凭系数猜 keV/MeV。
- 论文 Eq. (3.5) 把三个 channel 的时间分布分别积分，包含 \(\pm250\,\mathrm{ns}\) timing shift nuisance \(\alpha_6\)；Eq. (3.6) 的 time-dependent efficiency 在 \(t_0=0.52\,\mu s\) 前为 1，之后指数下降，\(k=0.0494/\mu s\)。
- 论文使用 **9 个 PE bins × 11 个 time bins**；最后做 Cs + I 的事件数相加。**不能用核平均后再做 response，不能把 recoiled-energy bin 和 PE bin 当作同一数轴**。

**本程序的可比对象**：不应只提供 total events；请输出 `S_Cs[flavor, PE_bin, time_bin]`、`S_I[...]`、`S_CsI_sum` 及用于 likelihood 的 signal array。对于现有 fast kernel，另输出与 slow authoritative integrator 在**同一参数点、同一物理参数/response**下的逐 bin 相对误差。旧 PDF 已记录 CsI2021 fast-vs-slow 的数值吻合，但其统计输入被标为 legacy approximate，不能代替上述论文实验模型比对。

### 2.2 论文 LAr 事件率（§3.2）

同样从 Eq. (3.1) 的核反冲积分出发，但必须使用另一套实验响应：\(m_{\rm det}=24\,\mathrm{kg},L=27.5\,\mathrm m,r=0.09,N_{\rm POT}=1.38\times10^{23}\)，QF 关系 \(QF(T')=0.246+7.8\times10^{-4}T'(\mathrm{keV_{nr}})\)，论文采用 Gaussian energy smearing、公开 data-release 的 energy efficiency、**无额外 time efficiency**；共 **12 energy × 10 time bins**。ES 信号没有纳入 LAr 的 CEνNS 约束。

不要把 CsI 的 timing nuisance、PE Gamma response 或效率函数复制给 LAr。比较 LAr 时需保留 `prompt BRN / delayed BRN / SSB` 背景的不同模板。

### 2.3 优先制作 SM baseline 对照（每个实验一张诊断页）

在扫任何新物理参数前，固定 \(\epsilon=C^q_X=0\)，使用**论文参数设定**，输出：每靶核每源味积分前 \(dR/dT\)；真反冲谱；quenching 后谱；smearing/efficiency 后谱；各时间 slice；二维 signal；各背景二维模板；预设 nuisance=0 时总预测。论文附录 A / Fig. 17–18 为 CsI detector-response 和时间分箱谱的额外核查对象，但不能从印刷图像取得未经数字化的精确 bin 真值。

基于可获得的 release/reference，逐 bin 验证：bin 边界、归一化、数组轴顺序 `[time,energy]` 还是 `[energy,time]`、单位 cm²/GeV/keV、同位素 target 个数、time window normalization 以及所有 flux channels 积分。形状一致但总量整体有常数差，优先查 \(N_{POT}\)、距离平方、原子个数、GF 和单位变换；prompt vs delayed 不符优先查 flavor/时间谱绑定；低 recoil 不符优先查 QF、threshold、efficiency 与 smearing。

---

## 3. 统计层：这里不是“看起来都是 χ²”就可以比较

### 3.1 论文的 CsI：Poisson 2D likelihood，不是泛用一维 Gaussian χ²

论文 §3.3 Eq. (3.9)，在 \(9\times11\) bins 上采用 Poisson deviance（写成常见的等价形式）：

\[
\chi^2_{\rm CsI}(\theta,\boldsymbol\alpha)=2\sum_{ij}
\left[\mu_{ij}(\theta,\boldsymbol\alpha)-n_{ij}
+n_{ij}\ln\frac{n_{ij}}{\mu_{ij}(\theta,\boldsymbol\alpha)}\right]
+\sum_{k\in K}\left(\frac{\alpha_k}{\sigma_k}\right)^2.
\]

针对 **Fig. 3–7 所采用的 CEνNS-only** 情况，论文 Eq. (3.11) 的 \(\mu_{ij}\) 是

\[
\mu_{ij}^{\rm CsI}=(1+\alpha_0)S_{ij}^{\rm CE\nu NS}(\alpha_4,\alpha_6,\alpha_7)
+(1+\alpha_1)B_{ij}^{\rm BRN}(\alpha_6)
+(1+\alpha_2)B_{ij}^{\rm NIN}(\alpha_6)
+(1+\alpha_3)B_{ij}^{\rm SSB}.
\]

高优先级核对：\(\sigma_0=11.45\%\)（CEνNS-only 情况，把 flux/efficiency/QF 等归一化合并），\(\sigma_1=25\%\) BRN，\(\sigma_2=35\%\) NIN，\(\sigma_3=2.1\%\) SSB，\(\sigma_4=5\%\) 的核半径；\(\alpha_6\) timing shift 和 \(\alpha_7\) efficiency shape 不应未经论文核对便当成普通同方差 Gaussian normalization。论文 Eq. (3.10) **CEνNS+ES** 是另一条统计分支，额外涉及 \(\alpha_5\)（QF），**不可与本次 NSI/NGI 图的 Eq. (3.11) 混用**。

实际实现要处理 \(n_{ij}=0\) 的极限 \(n\log(n/\mu)\to0\)，且 \(\mu_{ij}>0\)。输出每个 nuisance 的 best fit、boundary hit、优化器收敛、penalty 分项；不可只保存总 χ²。

### 3.2 论文的 LAr：12×10 Gaussian + 明确 shape template nuisance

论文 Eq. (3.12)–(3.13) 是带 \(1/\sigma_{ij}^2\) 的 binned Gaussian：

\[
\chi^2_{\rm LAr}=\sum_{ij}\frac{[\mu_{ij}^{\rm LAr}(\theta,\boldsymbol\beta)-n_{ij}]^2}{\sigma_{ij}^2}
+\sum_{k\in\{0,3,4,8\}}\left(\frac{\beta_k}{\sigma_k}\right)^2
+\sum_{k\in\{1,2,5,6,7\}}\beta_k^2,
\quad \sigma_{ij}^2=n_{ij}+B_{ij}^{\rm SSB}/5.
\]

\(\mu_{ij}\) 是 CEνNS、SSB、prompt BRN、delayed BRN 的带 nuisance 加权之和；CEνNS 的 \(\beta_1,\beta_2\) 改变 F90/trigger-time shape，prompt BRN 的 \(\beta_5,\beta_6,\beta_7\) 改变 energy/trigger-time/width shape。不能把它们一律当作常数归一化。论文标准化 \(\sigma_0,\sigma_3,\sigma_4,\sigma_8=(0.13,0.0079,0.32,1.0)\)。模板相对变化按 Eq. (3.13) 从 data release 的 ±1σ 模板和 central value 构造；需要明确零 central bin 的除法保护/重构规则。

**本程序的对照要求**：统计实现出一份 `likelihood_equivalence.md`，逐项列出实际源码函数、数据文件、nuisance 个数/范围/prior、Poisson 或 Gaussian、shape template 来源、能量时间 bins。如果仍是旧 PDF 的 approximate stats，图像标题必须标为 `non-equivalent likelihood`，不得声称复现论文的 90% CL 区域。

### 3.3 联合 χ² 与 profile 的精确定义（也纠正早先 README 中一句过强的警告）

记实验 \(D\in\{\rm CsI2021,LAr2020\}\)，二维物理参数 \(\theta=(x,y)\)。假定两实验 nuisance 独立：

\[
\widetilde\chi_D^2(\theta)=\min_{\eta_D}\chi_D^2(\theta,\eta_D),\quad
\widetilde\chi_{\rm joint}^2(\theta)=\widetilde\chi_{\rm CsI}^2(\theta)+\widetilde\chi_{\rm LAr}^2(\theta),
\]
\[
\Delta\chi_D^2(\theta)=\widetilde\chi_D^2(\theta)-\min_{\theta\in\Omega}\widetilde\chi_D^2(\theta),\quad
\Delta\chi_{\rm joint}^2(\theta)=\widetilde\chi_{\rm joint}^2(\theta)-\min_{\theta\in\Omega}\widetilde\chi_{\rm joint}^2(\theta).
\]

**细节**：最稳妥的是保存并相加 raw profiled χ²；但数学上若两个 Δχ² 使用完全相同网格和各自一致的 min 定义，那么**将两张单实验 Δχ² 逐点相加后再次减去总和的最小值，得到的 joint Δχ² 是等价的**。真正错误的是把单实验 Δχ² 直接相加后**不重新归零**、将不同参数网格/不同 statistic 混加、或者将 CsI2017 与覆盖它的更新 CsI2021 当成独立实验重复计数。为溯源与最佳点诊断，仍规定保存 raw profile 和每实验 minima。

Fig. 3–6 / Fig. 7 下排的二维 **90% C.L., 2 d.o.f.** 阈值采用 \(\Delta\chi^2=4.605170...\)。这应对齐论文的绘图约定，不等于已有 Feldman–Cousins 覆盖率验证。Fig. 7 **上排是一维单耦合扫描曲线**，其 χ² reference min 和横轴必须与下排二维独立；不可随意把二维曲面 \(y=0\) 的切片标作“一维 profile of same two-operator model”。如论文说明“single NGI”，应让另两个 NGI 耦合保持零，并只 profile 实验 nuisance。

**禁止把 CsI2017 再与 CsI2021 累加作为正式 joint**。旧 PDF 的三个数据集相加可留作程序组合单元测试；论文 benchmark 的联合值只能是 CsI2021 + LAr2020。

---

## 4. Fig. 3–7 每一张图：论文在算什么、程序应算什么、检查什么

**全图统一**：Fig. 3–6 每一二维扫描只打开图示两个**实数** NSI 参数，其他 NSI 设 0；默认无 SNS 传播新物理、无源端新物理。左列绘 CsI（magenta）和 LAr（orange）各自的允许区，右列绘 CsI+LAr（blue）。论文轴名称中的 \(uV/dV\) 是 quark **vector** NSI，不是程序任意的 “u/d Wilson” 默认值。扫描域见本项目 `manifest.json`，但它只是绘图模板，必须再对照原始 v2 PDF 图框。

### Fig. 3：同一 flavor 的 u/d 两参数——检验核电荷线性组合与两支解

- 上排：横轴 \(\epsilon_{ee}^{dV}\)、纵轴 \(\epsilon_{ee}^{uV}\)。仅 electron-flavor diagonal NP；\(\nu_e\) 信号改变，\(\nu_\mu/\bar\nu_\mu\) 的 CEνNS 核振幅保持 SM。
- 下排：横轴 \(\epsilon_{\mu\mu}^{dV}\)、纵轴 \(\epsilon_{\mu\mu}^{uV}\)。仅 muon-flavor diagonal NP；prompt \(\nu_\mu\) 与 delayed \(\bar\nu_\mu\) 贡献改变，\(\nu_e\) 为 SM。
- 论文 §4.2 的描述：单独 CsI/LAr 的 electron plane 可出现一条带，联合可分辨出靠近 SM 与 \(Q_{\rm NSI}\simeq -Q_{\rm SM}\) 的两支；muon plane 中单数据也可能显示两支。具体结构依 2-dof 图阈值/数据；不能强制程序“输出两条”，须扫描完整参数域并在论文条件下核对。
- 此图首先对比 \(Q_N^{\alpha\alpha}\) 的线性加权、两靶核斜率、单源味比例、两支 \(Q\mapsto -Q\) 的平方简并，然后才对比 contour 带宽。

### Fig. 4：electron 与 muon diagonal 同时变化——检验 flavor source bookkeeping

- 上排 \((\epsilon_{ee}^{uV},\epsilon_{\mu\mu}^{uV})\)，下排 \((\epsilon_{ee}^{dV},\epsilon_{\mu\mu}^{dV})\)；**同一 quark type，两种不同初始 flavor** 同时开启，其他系数归零。
- 公式检验：总体 event rate 是 \(\nu_e\)、\(\nu_\mu\)、\(\bar\nu_\mu\) 各自按通量和时间核相加，而不是把 \(\epsilon_{ee}\) 与 \(\epsilon_{\mu\mu}\) 在一个振幅里相加。prompt/delayed 的时间区分对此图特别重要。
- 若图像结果近似只沿单轴变化，先检查 source-flavor injection 是否有一种味被误置为零；如正确的全事件数但等高线不同，查 time response / nuisance。

### Fig. 5：diagonal + tau-changing——检验无 tau 入射通量时的末态求和

- 上排 \((\epsilon_{ee}^{dV},\epsilon_{e\tau}^{dV})\)，下排 \((\epsilon_{\mu\mu}^{dV},\epsilon_{\mu\tau}^{dV})\)。所有 u NSI 和其他 d NSI =0。非对角元素设 Hermitian companion \(\epsilon_{\tau e}=\epsilon_{e\tau}^*\)、\(\epsilon_{\tau\mu}=\epsilon_{\mu\tau}^*\)。
- **虽然 SNS 没有入射 \(\nu_\tau\)，\(\nu_e\to\nu_\tau\)、\(\nu_\mu\to\nu_\tau\) 的不可见末态贡献仍存在**，不应因输入 flux 的 tau row 为零就将 off-diagonal detection term 删除。
- 固定 diagonal 值时，\(\epsilon_{e\tau}\to-\epsilon_{e\tau}\) 或 \(\epsilon_{\mu\tau}\to-\epsilon_{\mu\tau}\) 应保持率/χ² 不变（实系数、未检测末态、无其他 flavor coherence/干涉前提）；这是最直接的矩阵索引回归测试。

### Fig. 6：diagonal + e–mu changing——检验源味双向与复共轭/索引

- 上排 \((\epsilon_{ee}^{dV},\epsilon_{e\mu}^{dV})\)，下排 \((\epsilon_{\mu\mu}^{dV},\epsilon_{e\mu}^{dV})\)，其他 NSI =0。
- \(\epsilon_{e\mu}\) 能使 \(\nu_e\to\nu_\mu\) 与 \(\nu_\mu\to\nu_e\) 的末态 CEνNS 同时改变相应 source channels；**不是入射 νe 和入射 νμ 的振幅相加**。应保存按 source 拆分的 NSI–SM ratio，并检验 \(\epsilon_{e\mu}\to-\epsilon_{e\mu}\) 的偶对称。
- 对角的允许区位置可能随 off-diagonal 强度变化：这是对角与非对角事件贡献共同满足总观测量的简并，不能误绘成 SM 与 eμ 振幅线性干涉。

### Fig. 7：NGI scalar/vector/tensor——检验 Lorentz 通道及真正的干涉项

- 上排：三个独立一维 \(\Delta\chi^2(C_S^q)\)、\(\Delta\chi^2(C_V^q)\)、\(\Delta\chi^2(C_T^q)\)，其余 NGI=0。论文的 x 轴是 **quark-level product coupling** \(C_X^q=g_{\nu X}g_{qX}\)，不是 nucleus-level \(C_X\)。
- 下排三平面：\((C_S^q,C_T^q)\)，\((C_V^q,C_S^q)\)，\((C_V^q,C_T^q)\)（按论文图实际横/纵轴核对）；一次打开两个，第三个归零；uniform \(u=d\) 假设。
- 检查：SM–vector 线性干涉与第二个 vector minimum；纯 S/T 的非负平方项；**S–T 的 \(\pm2C_SC_T T/E_\nu\)** 在三种入射 flux 中的中微子/反中微子符号；Cs/I/Ar 的 scalar/tensor hadronic matrix elements；只凭一个 vector-NSI fast kernel **无法**复现 scalar/tensor。
- 论文上排 vector 的另一极小值在约 \(C_V^q\sim0.18\) 附近（只作核对数量级，不当作硬编码真值）。若 kernel 显示只有原点一个 minimum，先查 nucleus-level/vector normalization、扫描域和 quadratic/linear interference。

**与旧 15 图文件的对应关系**：它包含 Fig. 3 的两组相关参数平面，但旧图横纵互换；它的 \((\epsilon_{e\mu}^{uV},\epsilon_{e\mu}^{dV})\) 既不是论文 Fig. 5 也不是 Fig. 6；旧图没有 Fig. 4 的跨味 diagonal 平面，也没有 Fig. 5 的 \(e\tau/\mu\tau\) 和 Fig. 7 NGI。旧图所有统计均自称 `legacy approximate statistics`；不得用那些 PNG 贴到“Reproduction”栏冒充同一物理/统计任务。

---

## 5. 代码审计/移植清单：用证据写“我们这边采用了什么”

请在**指定 branch 的实际源码**逐项填写以下表格。没有读到源文件或无法运行，不允许填“已实现”。建议每一行附 `path:line`、输入和输出维数、基准参数 hash 和测试命令。

| 任务 | 论文定义 | 本程序应核查的真实实现证据 | 本会话可确认状态 |
|---|---|---|---|
| Wilson → vector NSI | Eq. (2.5),(2.6)；u,d 两个 Hermitian flavor 矩阵 | `epsilon_to_np_only_Wilson` 等真实函数名/系数变换、SM baseline 插入位置 | **旧 PDF 只叙述映射；分支函数待审计** |
| 物理核/核响应 | Eqs. (2.1)–(2.3); Cs,I,Ar individually | differential rate、form factor、fast/slow 参数表及基准比较 | **旧 PDF 有 fast/slow 一致检查，不代表论文 KN 匹配** |
| SNS flux / density | Eq. (3.2)，3 个 source channels 和时间分布 | νμ / anti-νμ / νe flavor indices、anti-ν convention、时间积分 | 待审计 |
| Detector response | §§3.1–3.2；9×11 / 12×10 | QF/PE/efficiency/smearing/timing 各数据文件 | 待审计 |
| CsI likelihood | Eqs. (3.9),(3.11)；Poisson, 5 类 prior + shape shift | observed/background/template/bin order/nuisance/objective | **旧 PDF 自称 approximate；新 branch 待审计** |
| Ar likelihood | Eqs. (3.12),(3.13)；Gaussian + shape templates | β0…β8 / template ±1σ / statistical variance | 待审计 |
| Joint profiler | 两实验同点同物理参数求和，nuisance 各自 profile | raw χ²、各自 minima、joint min、优化器收敛/边界 | 待审计；**不能加 CsI2017** |
| Fig. 7 NGI | Eqs. (2.7)–(2.11)，u=d coupling，S,V,T 干涉 | scalar/tensor operators、hadronic coefficients、ν/anti-ν sign | **不由旧 vector-NSI 结果证明；待审计/待新增** |
| 论文原图提取 | 确实从用户 v2 PDF 的图版区域提取 | PDF sha256、Fig caption text、crop bbox、每图人工审视 | 当前本地 v2 PDF 未挂载 |

**建议的实现约束**：在新的 benchmark adapter 中调用本项目现有事件率接口；不要为复现另写一份独立“看起来相同”的 CEνNS physics。若必须增加论文特有 KN/response/likelihood，写可配置的 `paper_2211_11905` backend，并保留 native backend 与同样的 Wilson/flavor 核接口，这样才能做归因实验：

1. `paper_physics + paper_response + paper_likelihood`：文献复现基准。
2. `native_physics + paper_response + paper_likelihood`：只隔离核响应/截面实现差异。
3. `paper_physics + native_response + paper_likelihood`：只隔离 detector 模型差异。
4. `paper_physics + paper_response + native_likelihood`：只隔离统计实现差异。

没有这些受控组，最终两个 contour 的差不能被归因于 Flavor、form factor 或统计中任何单一因素。

---

## 6. 对照图、原始数值及定量差异必须怎样交付

### 6.1 产出结构（每一个 panel 而不是只给总图）

```text
Benchmark/2211.11905v2_Fig3-Fig7/
  source/2211.11905v2.pdf                 # 用户提供原件；保留 hash，不做无授权替换
  provenance/paper_sha256.json
  provenance/code_commit_and_env.json
  configuration/paper_physics.yaml
  configuration/paper_response_csi.yaml
  configuration/paper_response_lar.yaml
  configuration/paper_likelihood.yaml
  audit/branch_function_mapping.md
  audit/likelihood_equivalence.md
  sm_checks/CS_SM_binwise.csv, I_SM_binwise.csv, Ar_SM_binwise.csv
  sm_checks/SM_spectra_and_timing.png
  raw/fig3_top.npz ... fig6_bottom.npz
  raw/fig7_profile_scalar.npz ... fig7_plane_vector_tensor.npz
  figures/paper/Fig03_original.png ... Fig07_original.png
  figures/reproduced/Fig03_reproduction.png ... Fig07_reproduction.png
  figures/comparison/Fig03_comparison.png ... Fig07_comparison.png
  figures/panels/Fig03_top_left_original.png ...
  figures/panels/Fig03_top_left_reproduced.png ...
  diagnostics/Fig03_top_delta_chi2_surface.png ...
  diagnostics/bestfits_and_truncation.csv
  diagnostics/parameter_scan_comparison.csv
  report/DIFFERENCE_REPORT.md
```

**三份图的意义**：`original` 必须忠实提取论文原图（有 v2 SHA256 和 crop bbox）；`reproduction` 必须从本程序产生的真实 raw event/χ² 数据独立绘出；`comparison` 是前两者同轴并排或轮廓叠加，注明论文曲线是手工数字化还是原始图像，绝不把截图像素当作数值表。需要再提供 `native-program` 独立图，但它不能替代 `paper-matched reproduction`。

### 6.2 数值文件要求

每二维 plane：`x`, `y`, `chi2_csi_raw`, `chi2_lar_raw`, `chi2_joint_raw`（各矩阵 `[len(y),len(x)]`）、`delta_*`（可衍生）、`nuisance_bestfit_*`, `optimizer_status`, `boundary_truncated`, `physics_mode`, `response_mode`, `likelihood_mode`。如沿用此前绘图工具包的字段名，则兼容另存 `chi2_csi/chi2_lar/chi2_joint`，明确它们是 raw profiled χ²，而非数据测量值；每一个 NPZ 需记录参数列表与被固定为 0 的全部其他参数。

Fig. 7 每条一维曲线需保留 `x`, `chi2_csi_raw`, `chi2_lar_raw`, `chi2_joint_raw` 和其归零曲线；不要套用二维 \(\Delta\chi^2=4.605\) 来解释上排曲线的横轴范围。

### 6.3 差异度量（不要只说“肉眼差不多”）

- **物理核差异**：同一 \((E_\nu,T,A,\alpha,\theta)\) 的 \(\delta_{d\sigma}=[\sigma_{our}-\sigma_{paper-formula}]/\max(|\sigma_{paper-formula}|,\varepsilon_{\rm floor})\)，零点单独报告绝对误差。
- **bin 事件数差异**：按 Cs/I/Ar 与 νμ、anti-νμ、νe 分开报告 max absolute bin diff、aggregate diff、RMS relative diff；需确保逐项使用同一 exposure/response。
- **χ² 诊断**：SM \(\chi^2\)、最优点位置和数值、joint 最优点、各 nuisance pulls；在手选 anchor points 上报告 Δχ² 值。对照原图没有开放数字化数据时，不能声称“论文 χ² 差值精确为 x”。
- **等高线**：比较连通分支数量、是否穿过 SM、是否触框、带斜率、两支间距、允许区面积；若从论文图数字化出原始边界，再报告 Hausdorff distance / area overlap，附数字化像素分辨率与读轴误差。
- **统计兼容性**：同一 threshold/dof/min 定义，否则面积、宽度的差异不具有同义性。输出 `MATCH / PHYSICS_ONLY_MATCH / STATISTICS_DIFFER / NGI_MISSING / NOT_COMPARABLE` 等**技术状态**及原因，而非在未测量时打“通过”。

### 6.4 裁剪/绘图器现有问题（执行前要修）

此前工具包的 `plot_benchmark.py` 使用 `page.search_for('FIG. 3:')` / `('Fig. 3:')`，而可访问的 JHEP 文字图注写作 `Figure 3.`。这会导致即使本地 PDF 正确也找不到图号。需要兼容 `Figure {n}.`, `Fig. {n}.`, `FIG. {n}:` 等，**再人工核对实际 PDF 版面**；此外从页面顶部一直裁到 caption 的方式可能把前一段正文/另一张图包含进去，应使用 figure region bbox 而非盲裁整个上半页。此前 `manifest.json` 的 page index 只是模板，必须以 v2 原件的实际 page captions 校正。

**禁止只把原图按页面宽度整体缩放，再把本程序重绘放在旁边就直接测像素差**；它们的字体、裁边、线宽都不同。要量化物理约束差别，先对齐轴坐标，再对 contour 做数字化。

---

## 7. 分阶段实施和退出条件

| Stage | 操作 | 需要留下的证据 | 放行条件 |
|---|---|---|---|
| 0 | 获取本地 v2 PDF、指定 Gitup01 源码/数据，记录版本/hash | `code_commit_and_env.json`, `paper_sha256.json`, audit 表 | 文件和 branch 确认；不得把旧 PDF 混作原件 |
| 1 | Paper vs Wilson/Flavor formula（一个核、一个 source、少数 anchor points） | `physics_kernel_unit_tests.csv` | epsilon→NP-only factor、SM、off-diagonal evenness、u/d 准确 |
| 2 | SM CsI/Ar 预测与论文响应链一致 | `sm_checks/` 和差异归因 | Cs/I/Ar 各自能谱/时间谱、单位、曝光确认 |
| 3 | 两实验独立 likelihood 对齐 | `likelihood_equivalence.md`, nuisance pulls | bins/observable、background、prior、形状 nuisance 匹配 |
| 4 | Fig. 3–6 八张二维 surface/contour | 每 plane raw NPZ + original/reproduction/comparison | 扫描涵盖完整 minima 和各支；90% contour 不被图框误截 |
| 5 | Fig. 7 三一维+三二维 NGI | NGI 物理单测与 raw NPZ | S/T 核矩阵元、ν/anti 的 S–T sign、V–SM 干涉均验证 |
| 6 | 输出 independent + overlay + difference report | 成果文件、hash、caption、实际偏差表 | 每一结论注明 `paper-matched` 或 `native-program` |

最关键的异常处理顺序：

1. SM 总量不符：先查 exposure、靶个数、flux / units；**不要**通过拟合 NP epsilon 去补。
2. SM 真反冲符合、observed PE/time 不符：查 quenching/efficiency/smearing/time-shape；**不要**修改核弱电荷。
3. 各 bin 符合、χ² 不符：查 observed data、background、statistic、nuisance 和数值优化器。
4. χ² 局部符合、contour 不符：查物理参数 convention、全局/局部 minima、grid 截断、插值和自由度。
5. Fig. 5/6 的正负不对称：先检查是否遗漏 Hermitian companion / 误加 flavor 振幅。
6. Fig. 7 的 S–T 形状不符：查 neutrino vs antineutrino interference sign；如尚未实现 NGI 则直接标未实现，不准用 NSI 假造。

---

## 8. 最终报告中可以直接采用的“比较定义”文字

> 我们以 De Romeri et al. (arXiv:2211.11905v2) 的 Fig. 3–7 为 benchmark，在相同的 CsI2021 与 LAr2020 目标数据、SNS flux、form factor、探测器响应和统计约定下，逐点扫描论文指定的两个非零 NSI 或 NGI 耦合。对于 Fig. 3–6，我们将论文 quark-level vector NSI \(\epsilon_{\alpha\beta}^{qV}\) 映射到 CEvNS-pyEFT 的 flavor-dependent detector Wilson matrices，采用不可分辨末态 flavor 的振幅模平方求和，得到每个实验 energy–time bin 的信号事件预测，之后分别进行 nuisance profiling 并构造 CsI、LAr 和联合的二维 \(\Delta\chi^2\)。对于 Fig. 7，我们独立实现/验证论文 scalar、vector、tensor 核电荷及中微子–反中微子相反符号的 S–T 干涉，不把其参数等同于 NSI epsilon。最终分别比较物理截面、探测器级事件数、profiled statistic 和 90% CL contours；若使用本程序的本征 form factor 或近似 likelihood，则另列为 model-systematic comparison，而非视为论文的完全统计复现。

### 最终绘图应使用的图注

- `Paper original — De Romeri et al., arXiv:2211.11905v2, Fig. N (exact supplied PDF; SHA256: …)`
- `Paper-matched reproduction — CEvNS-pyEFT Flavor; CsI2021 / LAr2020; theory+response+likelihood settings matched; commit …`（仅全部核对以后才能使用）
- `Native CEvNS-pyEFT comparison — same couplings/data, different: [list exact model/likelihood differences]`
- `Difference / contour overlay — transformed to identical parameter axes; paper boundary source: [digitized/manual/reference data]; 2D 90% CL, Δχ²=4.605`。

**必须留空而不能推测的字段**：branch 真实代码路径及 commit、已经实现的 NGI 项、是否完全复现论文的 α/β nuisance、官方数据 release 文件 hash、v2 PDF 页码/crop bbox、论文数字化 contour 的点坐标、实际的数值偏差和测试通过/失败结果。填齐以前，这份文档是实施规范，而不是结果声明。
