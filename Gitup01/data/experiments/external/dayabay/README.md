# Daya Bay 反应堆谱外部数据

本目录中的 `.txt` 文件是从 Daya Bay arXiv ancillary data 下载的原始文件：

- `UnfoldAntineutrinoSpectra.txt`：arXiv:2102.04614；
- `AntineutrinoEnergySpectrum_high.txt`：高能谱 ancillary；
- `WholeAntineutrinoEnergySpectrum.txt`：中央与高能段组合参考谱。

`extract_dayabay_spectra.py` 将其中的谱段解析为便于读取的 CSV。

注意：

1. Daya Bay 的原始裂变份额不是 CONUS+ KKL 的裂变份额；
2. U235、Pu-combo 和 total unfolded spectra 不能直接视为四种独立裂变同位素谱；
3. 这些文件是构建 CONUS+ flux model 的外部输入，不是已经完成的 CONUS+ 最终通量；
4. 在发布或再分发前，请独立核对原始数据许可和引用要求。
