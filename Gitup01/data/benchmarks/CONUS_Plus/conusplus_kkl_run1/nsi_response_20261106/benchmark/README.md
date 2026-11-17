# NSI 论文直接基准

采用V. De Romeri, D. K. Papoulias, and G. Sanchez Garcia, “Implications of the first CONUS+ measurement of coherent elastic neutrino-nucleus scattering,” Phys. Rev. D111, 075025 (2025), doi:10.1103/PhysRevD.111.075025, arXiv:2501.17843v3。

- [tableII_1sigma.csv](tableII_1sigma.csv) 保存PDF p.13 TableII的六个CONUS+ NSI行，共8个连通区间，标称1σ。
- [fig4_blue_polygons.csv](fig4_blue_polygons.csv) 保存PDF p.14 Fig.4的四个蓝色90%二维区域，共7个多边形、1429个顶点。
- [REFERENCES_PROVENANCE.json](REFERENCES_PROVENANCE.json) 保存PDF SHA256、原文文本行、各轴刻度校准、逐路径身份和核验限制。

取点入口为 [extract_nsi_references.py](<../../../../../../examples/CONUS_Plus/conusplus_kkl_run1/nsi_response/extract_nsi_references.py>)。实际检查了PDF文本、矢量路径和渲染页。数值精度沿用发表表格的舍入与图形分辨率。

[返回data](../README.md)
