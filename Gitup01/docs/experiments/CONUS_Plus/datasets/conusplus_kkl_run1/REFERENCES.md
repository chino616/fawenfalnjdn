# CONUS+ onboarding v3 标准参考文献与核验范围

## 文献与文件入口

<a id="ref-1"></a>

[1] V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, "Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering," Phys. Rev. D **111**, 075025 (2025).

v3; Sec. III, Eqs. (26)-(33), Fig. 1; Eq. (34), Table II。核验范围为 `primary_read`。

[本地原文或直接材料](../../../../references/CONUS/2501.17843v3.pdf) · [DOI](https://doi.org/10.1103/PhysRevD.111.075025) · [官方入口](https://arxiv.org/abs/2501.17843v3)

SHA256 `b20923363badde299106a6df83f0dff5308fd69d652b59b9967d32b764057c90`。

<a id="ref-2"></a>

[2] Th. A. Mueller et al., "Improved predictions of reactor antineutrino spectra," Phys. Rev. C **83**, 054615 (2011).

Eq. (12), Table VI, PDF p. 13; nominal coefficient arrays verified 24/24。核验范围为 `primary_read`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/1101.2663v3.pdf) · [DOI](https://doi.org/10.1103/PhysRevC.83.054615) · [官方入口](https://arxiv.org/abs/1101.2663v3)

SHA256 `1421b06de707afa7d5bd6ec2a61b31a011bc069a6d7358e477a7a49695afa429`。

<a id="ref-3"></a>

[3] V. I. Kopeikin, "Flux and spectrum of reactor antineutrinos," Phys. At. Nucl. **75**, 143-152 (2012).

Publisher title/author/volume/pages/DOI verified; subscription full text and exact 32-node source table not acquired。核验范围为 `metadata_only_not_numeric_table_verified`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/kopeikin_2012_publisher.html) · [DOI](https://doi.org/10.1134/S1063778812020123) · [官方入口](https://link.springer.com/article/10.1134/S1063778812020123)

SHA256 `a512f096496f388b81046dae0652aa2e399bc28a9c76297a346ce08ae74ac447`。

<a id="ref-4"></a>

[4] 作者未署名，"CEνNS-pyEFT 逐文件物理编程笔记：从 LEFT Wilson 系数到 COHERENT 分箱事件数"，第1章 "CONUS+ 的 73Ge 现象学分析"，未发表项目笔记（2026），用户提供，访问日期2026-11-06。

filename 2026_07_16_CEvNSpyEFT - CONUS.pdf; Flux Sec. 1.4.1; PDF pp. 4-6, printed pp. 3-5; Tables 1/2。核验范围为 `user_document_read_not_peer_reviewed`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/user_reference_CONUS.pdf)

SHA256 `2f0d7901c92858b2bb2319cfced1986b3d42dba2d441fc51b4d0b715280685d8`。

<a id="ref-5"></a>

[5] NIST Physical Measurement Laboratory, "Atomic weights and isotopic compositions for germanium," online data table, accessed 2026-11-06.

Ge70, Ge72, Ge73, Ge74, Ge76 rows; relative atomic masses and number abundances。核验范围为 `primary_read`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/nist_ge_isotopic_masses.html) · [官方入口](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Ge)

SHA256 `3dd6571ed66ea7046a444e3eb02c5dfe30ee559054a9c2a877ff4ca054a221c5`。

<a id="ref-6"></a>

[6] NIST Physical Measurement Laboratory, "Fundamental physical constants: 2022 CODATA adjustment, complete listing," online data table, accessed 2026-11-06.

atomic mass constant; atomic mass/electron rest energies; Avogadro constant; Fermi coupling constant。核验范围为 `primary_read`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/nist_codata2022_allascii.txt) · [官方入口](https://physics.nist.gov/cuu/Constants/Table/allascii.txt)

SHA256 `77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67`。

<a id="ref-7"></a>

[7] CEvNS-pyEFT project, "responses_all.json: shared nuclear response tables," local numerical/software asset, format Mu2eNRET_ResponseW_v1, snapshot accessed 2026-11-06. 原始核计算表的逐项来源对应尚未闭合。

nuclei.Ge70/Ge72/Ge73/Ge74/Ge76; np basis; ResponseDB.W_np; exact whole-file SHA256 recorded。核验范围为 `local_asset_verified_external_nuclear_table_provenance_pending`。

[本地原文或直接材料](../../../../../data/responses/responses_all.json)

SHA256 `cef361cd91a1efa3fe2b509ba0dd478f8b8fc9c13511f6d8637aad6c9bcf3d74`。

<a id="ref-8"></a>

[8] G. Li, C.-Q. Song, F.-J. Tang, and J.-H. Yu, "Comprehensive effective field theory framework for coherent elastic neutrino-nucleus scattering," arXiv:2601.19883v2 (2026).

Shared theory/matching/particle-response/nuclear-response framework; not proof of the provenance of every coefficient in S0007。核验范围为 `primary_read`。

[本地原文或直接材料](../../../../references/General_CEvNS/2601.19883v2.pdf) · [官方入口](https://arxiv.org/abs/2601.19883v2)

SHA256 `e72ae8b8d7642027b9723ce9758b2477d7322c802b53cef67f561191289d90cd`。

<a id="ref-9"></a>

[9] J. J. Choi et al. (NEON Collaboration), "Exploring coherent elastic neutrino-nucleus scattering using reactor electron antineutrinos in the NEON experiment," Eur. Phys. J. C **83**, 226 (2023).

Fig. 23 caption, U235/Pu239/U238/Pu241 order。核验范围为 `primary_read`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/neon_2023_publisher.html) · [DOI](https://doi.org/10.1140/epjc/s10052-023-11352-x) · [官方入口](https://link.springer.com/article/10.1140/epjc/s10052-023-11352-x)

SHA256 `4b0893c25b159ee2ebf1d628ce61814148f33540464e19d5c74f0e8d5b1ff65f`。

<a id="ref-10"></a>

[10] N. Ackermann et al. (CONUS Collaboration), "Direct observation of coherent elastic antineutrino-nucleus scattering," Nature **643**, 1229-1233 (2025).

arXiv:2501.05206v3, PDF p. 6, reactor flux paragraph。核验范围为 `primary_read`。

[本地原文或直接材料](../../../../references/CONUS/2501.05206v3.pdf) · [DOI](https://doi.org/10.1038/s41586-025-09322-2) · [官方入口](https://arxiv.org/abs/2501.05206v3)

SHA256 `81a612c6c6d31cd37d3a056e9e44fbc5cd061bc9e8399e3636308ef06c4bfc2d`。

<a id="ref-11"></a>

[11] CEvNS-pyEFT project, CONUS+ Fig. 1 vector-digitized data and provenance, release 2026-11-06, derived numerical asset from Ref. [1].

19 signed excess values and upper/lower endpoints; source is [1], not Table 3 of the user note。核验范围为 `figure_digitization_checked_not_author_raw_release`。

[本地原文或直接材料](../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/statistics/conusplus_2501_17843v3_fig1_digitized.csv)

SHA256 `ee4d11af7e543b2d9c895c5e0165d557b68869a1d6dc1b733360e0c41ec4ce60`。

<a id="ref-12"></a>

[12] CEvNS-pyEFT project, Model bindings, package statistics dispatch and nuclear response reader, local software snapshot, 2026-11-06.

model_bindings.json model keys, package_profiles.py::definition_from_generic/evaluate_statistics, profiling.py::profile_gaussian_one_pull。核验范围为 `local_code_identity_checked`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/project_implementation_manifest.json)

SHA256 `b4d300674f2b2f09befe6da527d687bac37bafefe6479c9966a681dc0ccc7886`。

<a id="ref-13"></a>

[13] Bureau international des poids et mesures, The International System of Units (SI), 9th ed. (2019), version 4.01 (June 2026), DOI 10.59161/AUEZ1291.

Chapter 4, Table 8, day row, PDF p. 142 / printed p. 140. SI prefixes in Chapter 3.。核验范围为 `primary_numeric_definition_checked`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/bipm_si_brochure_9_v4_01.pdf) · [DOI](https://doi.org/10.59161/AUEZ1291) · [官方入口](https://www.bipm.org/documents/20126/41483022/SI-Brochure-9.pdf)

SHA256 `1122cf38e25b23d780a30607c68f7350b2b6d1f9970a89947aaa87a45ecbb20a`。

<a id="ref-14"></a>

[14] User and CEvNS-pyEFT project, CONUS+ configuration decisions recorded in the onboarding conversation, 2026-11-06, local project record.

user_decisions entries D_V2_001, D_V2_002, D_V2_003 and D_V3_001。核验范围为 `user_decision_transcription`。

[本地原文或直接材料](../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/input_choices.json)

SHA256 `475d1c0dd96680c2139813997437b7c593ec2b543b382b3e13c5cf29317ed7db`。

<a id="ref-15"></a>

[15] CEvNS-pyEFT project, CONUS+ source and natural-Ge input generation, build_inputs.py, version v3_20261106_provenance (2026), local reproducible calculation.

build, verify_transcription and plot_flux functions。核验范围为 `local_algorithm_and_rebuild_checked`。

[本地原文或直接材料](../../../../../data/experiments/CONUS_Plus/conusplus_kkl_run1/build_inputs.py)

SHA256 `ca6f9f10ba53f41bcedde5186bd07a1739d9fff09e1ee9c59d49db330c456ad9`。

<a id="ref-16"></a>

[16] User-provided Flux reference figure identifying Kopeikin (2012) and Mueller et al. (2011), received 2026-11-06, unpublished reference image.

Two bibliography bullets and the low/high-energy split。核验范围为 `bibliographic_identification_only`。

[本地原文或直接材料](../../../../../workflows/cevns-pyeft/runs/CONUS_Plus/conusplus_kkl_run1/sources/user_flux_reference_slide.png)

SHA256 `b4be4061eaeb56ef6d95aa25b62d52e4a7867284d5223791b61bcf3d91652dca`。

## 来源与数据的对应

具体数据定位和上游核验范围见详细版逐字段来源索引及 P01。低能表直接来自用户 PDF，截图支持书目对应。Response 的数值直接来自本地 JSON。
